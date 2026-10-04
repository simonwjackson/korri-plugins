#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p 'python3.withPackages (ps: [ ps.pillow ])' xvfb-run util-linux pulseaudio
"""Compare private original, roundtrip and edited QSTs on an isolated build host.

Network namespaces prevent uploads. Xvfb and a private PulseAudio null sink
avoid real displays and speakers. The software-MIDI directory must come from
the packaged launcher's ALLEGRO setting. No whole-game clearance is implied.
"""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from PIL import Image

spec = importlib.util.spec_from_file_location(
    "midi_proof", Path(__file__).with_name("zquest-midi-proof.py")
)
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)


def replay_text(quest, frames):
    lines = [
        "M version latest",
        f"M qst {quest}",
        f"M frames {frames}",
        "M test_mode false",
        "M sync_rng false",
        "K 0 84 85 82 83 26 24 67 17 23 75 1 19 4 3",
        "R 0 0 1 123",
        "R 0 2 257 456",
    ]
    events = []
    # Block Smasher's A means "die", so this comparison uses only movement.
    for start in range(360, frames - 300, 360):
        direction = "Right" if (start // 360) % 2 else "Left"
        events.extend(
            [
                (start, f"D {start} {direction}"),
                (start + 150, f"U {start + 150} {direction}"),
            ]
        )
    events.append((frames, f"Q {frames} 3"))
    return "\n".join(lines + [text for _, text in sorted(events)]) + "\n"


def run_private_command(command, *, cwd, env, log, timeout=100):
    """Keep timeout cleanup inside this probe's own process group."""
    child = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    try:
        return subprocess.CompletedProcess(command, child.wait(timeout=timeout))
    finally:
        # xvfb-run and the player are descendants, not just the direct child.
        # Also remove any survivors after a nominally successful wrapper exit.
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        child.wait(timeout=5)


def replay_frame(result_path, expected):
    # Fields come from the observed native proof.zplay.result.txt producer.
    fields = {}
    for line in result_path.read_text().splitlines():
        key, separator, value = line.partition(": ")
        if separator:
            fields[key] = value
    if fields.get("success") != "true" or fields.get("stopped") != "true":
        raise RuntimeError(f"Replay did not finish successfully; inspect {result_path}")
    try:
        frame = int(fields.get("frame", ""))
    except ValueError as error:
        raise RuntimeError(
            f"Replay final frame missing or invalid: {result_path}"
        ) from error
    if frame != expected:
        raise RuntimeError(
            f"Replay stopped at {frame}, expected {expected}: {result_path}"
        )
    return frame


def run_case(root, mode, frames, snapshots, name, quest, engine, audio, pulse_socket):
    stage = root / f"{mode}-{name}"
    stage.mkdir(mode=0o700)
    for resource in (engine / "share/zquestclassic").iterdir():
        if resource.suffix != ".cfg":
            (stage / resource.name).symlink_to(
                resource, target_is_directory=resource.is_dir()
            )
    (stage / "zc.cfg").write_text(
        "[zeldadx]\nnosound = 0\nfullscreen = 0\nreplay_upload = 0\n"
        "replay_upload_prompt = 1\nclicktofreeze = 0\n"
    )
    replay = stage / "proof.zplay"
    replay.write_text(replay_text(quest, frames))
    args = [
        "unshare",
        "--user",
        "--map-root-user",
        "--net",
        "xvfb-run",
        "-a",
        "-s",
        "-screen 0 1240x1080x24",
        str(engine / "bin/zplayer"),
        "-replay",
        str(replay),
        "-replay-exit-when-done",
        "-snapshot",
        " ".join(map(str, snapshots)),
    ]
    if mode == "headless":
        args.append("-headless")
    env = dict(
        os.environ,
        ZC_DISABLE_CHDIR="1",
        LIBGL_ALWAYS_SOFTWARE="1",
        PULSE_SERVER=f"unix:{pulse_socket}",
        ALLEGRO=str(audio),
    )
    env.pop("TEST_ZC_API_SERVER", None)
    log_path = stage / "native.log"
    with log_path.open("w") as log:
        completed = run_private_command(args, cwd=stage, env=env, log=log)
    log = log_path.read_text()
    if (
        completed.returncode != 0
        or "rng desync" in log
        or "Time to load qst:" not in log
    ):
        raise RuntimeError(
            f"Native check failed: {mode}/{name}, exit {completed.returncode}; inspect {log_path}"
        )
    if mode == "audio" and "Initializing sound driver... OK" not in log:
        raise RuntimeError(f"Audio initialization not verified; inspect {log_path}")
    final_frame = replay_frame(stage / "proof.zplay.result.txt", frames)
    image_hashes = {}
    for frame in snapshots:
        with Image.open(stage / f"proof.zplay.{frame}.png") as image:
            image_hashes[str(frame)] = hashlib.sha256(
                image.convert("RGB").tobytes()
            ).hexdigest()
    return {
        "variant": name,
        "mode": mode,
        "frames": final_frame,
        "quest": str(quest),
        "quest_sha256": proof.digest(quest.read_bytes()),
        "returncode": completed.returncode,
        "image_pixel_sha256": image_hashes,
        "diagnostics": [
            line
            for line in log.splitlines()
            if any(word in line.lower() for word in ("warning", "error", "invalid"))
        ],
        "log": str(log_path),
    }


def compare(args):
    engine, audio = args.engine.resolve(strict=True), args.audio.resolve(strict=True)
    variants = {
        name: getattr(args, name).resolve(strict=True)
        for name in ("original", "roundtrip", "edited")
    }
    if proof.digest(variants["original"].read_bytes()) != args.expected_sha256:
        raise ValueError("Original quest differs from the supplied receipt")
    if not (engine / "bin/zplayer").is_file() or not (audio / "allegro.cfg").is_file():
        raise ValueError(
            "Packaged player or production software-MIDI configuration missing"
        )
    root = proof.private_output(args.output_dir, variants["original"])
    subprocess.run(
        ["unshare", "--user", "--map-root-user", "--net", "true"], check=True
    )
    root.mkdir(parents=True, mode=0o700)
    source_hashes = {
        name: proof.digest(path.read_bytes()) for name, path in variants.items()
    }
    pulse_socket = root / "pulse.sock"
    with (root / "pulse.log").open("w") as pulse_log:
        pulse = subprocess.Popen(
            [
                "pulseaudio",
                "-n",
                "--daemonize=no",
                "--exit-idle-time=-1",
                "--use-pid-file=no",
                "--load=module-null-sink sink_name=zquest_proof",
                f"--load=module-native-protocol-unix socket={pulse_socket} auth-anonymous=1",
            ],
            stdout=pulse_log,
            stderr=subprocess.STDOUT,
        )
        try:
            for _ in range(100):
                if pulse_socket.exists():
                    break
                if pulse.poll() is not None:
                    raise RuntimeError(
                        f"Private audio server failed; inspect {root / 'pulse.log'}"
                    )
                time.sleep(0.1)
            if not pulse_socket.exists():
                raise RuntimeError("Private audio socket did not appear")
            results = []
            for mode, frames, snapshots in [
                ("headless", 6000, [300, 900, 2400, 5500]),
                ("audio", 600, [300, 500]),
            ]:
                compared = []
                for name, quest in variants.items():
                    result = run_case(
                        root,
                        mode,
                        frames,
                        snapshots,
                        name,
                        quest,
                        engine,
                        audio,
                        pulse_socket,
                    )
                    results.append(result)
                    compared.append(result["image_pixel_sha256"])
                    (root / "native-results.json").write_text(
                        json.dumps(results, indent=2) + "\n"
                    )
                    print(json.dumps(result), flush=True)
                if compared[0] != compared[1] or compared[0] != compared[2]:
                    raise RuntimeError(f"Sampled pixels differ in {mode} mode")
                print(
                    f"PASS {mode}: three variants have identical sampled pixels.",
                    flush=True,
                )
            for name, path in variants.items():
                if proof.digest(path.read_bytes()) != source_hashes[name]:
                    raise RuntimeError(f"Input quest changed during replay: {name}")
            print(
                "PASS: private native editing proof; no complete-game or rights clearance.",
                flush=True,
            )
        finally:
            if pulse.poll() is None:
                pulse.terminate()
                try:
                    pulse.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pulse.kill()
                    pulse.wait()


def stop(signum, _frame):
    # Let SIGTERM unwind the private process-group and audio-server cleanup.
    raise SystemExit(128 + signum)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, stop)
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("engine", "audio", "original", "roundtrip", "edited", "output-dir"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    args = parser.parse_args()
    try:
        compare(args)
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Runtime proof failed: {error}\n")
