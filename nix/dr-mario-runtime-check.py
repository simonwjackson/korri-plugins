#!/usr/bin/env python3
"""Opt-in owned-ROM checks. No ROM is included in the build or retained by the test."""

import csv
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import statistics
import struct
import subprocess
import sys
import tempfile
import time
import wave
import zipfile


def run(args, **kwargs):
    try:
        return subprocess.run(
            args, check=True, text=True, capture_output=True, timeout=60, **kwargs
        )
    except subprocess.CalledProcessError as error:
        print(error.stdout, error.stderr, file=sys.stderr)
        raise


def wait_for(condition, child, message, seconds=20, interval=0.1):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if condition():
            return
        if child.poll() is not None:
            raise AssertionError(f"Game exited {child.returncode}: {message}")
        time.sleep(interval)
    raise AssertionError(f"Timed out: {message}")


def stop(child):
    if child.poll() is None:
        os.killpg(child.pid, signal.SIGTERM)
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()


def read_rom(path):
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            entries = [
                item
                for item in archive.infolist()
                if item.filename.lower().endswith(".nes")
            ]
            if len(entries) != 1 or entries[0].file_size != 65552:
                raise ValueError(
                    "Supply one supported Europe ROM, not a ROM collection"
                )
            return archive.read(entries[0])
    with path.open("rb") as source:
        return source.read(65553)


def main():
    package, engine, korrid, rom_path = sys.argv[1:]
    package, engine, rom_path = Path(package), Path(engine), Path(rom_path).resolve()
    rom = read_rom(rom_path)
    expected = "83914c08f82fc70779121760a48392af3a5988f015794eb53cbe1aa0a165c821"
    assert hashlib.sha256(rom).hexdigest() == expected, "Unsupported Europe ROM"
    manifest = json.loads((package / "manifest.json").read_text())
    # The raw-engine smoke test must not inherit developer output paths or
    # experimental execution modes from the caller's shell.
    clean_environment = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("NESRECOMP_", "RECOMP_AUDIO_", "LNG_", "NES_NET"))
    }

    with tempfile.TemporaryDirectory(prefix="dr-mario-owned-") as temporary:
        root = Path(temporary)
        content = root.joinpath(
            *(["long-" + "x" * 90] * 6),
            "Dr. Mario %s '; $(exit 19) `exit 20` #.nes",
        )
        content.parent.mkdir(parents=True)
        assert len(os.fsencode(content)) > 512
        content.write_bytes(rom)
        protected = root / "do-not-overwrite.txt"
        protected.write_text("preserve diagnostic sentinel")
        smoke = root / "smoke"
        smoke.mkdir()
        result_path = smoke / "result.json"
        run(
            [
                str(engine / "bin/DrMarioRecomp"),
                str(content),
                "--smoke",
                "600",
                "--smoke-output",
                str(result_path),
            ],
            cwd=smoke,
            env=dict(
                clean_environment, NESRECOMP_COSIM_HASH=str(smoke / "clock.jsonl")
            ),
        )
        report = json.loads(result_path.read_text())
        assert report["frames_run"] == 600, report
        assert report["dispatch_miss_count"] == 0, report
        assert len(set(report["frame_hashes"].values())) > 1, report
        print("Native 600-frame smoke:", json.dumps(report), flush=True)
        # Existing upstream co-sim output exposes actual pre-handler CPU clocks.
        # Ignore startup and check the real PAL budget, not a source-code constant.
        clocks = [
            json.loads(line)["bclk"]
            for line in (smoke / "clock.jsonl").read_text().splitlines()
        ][-200:]
        cycles_per_frame = (clocks[-1] - clocks[0]) / (len(clocks) - 1)
        print(f"CPU cycles per PAL frame: {cycles_per_frame:.3f}", flush=True)
        assert abs(cycles_per_frame - 33247.5) < 0.1, cycles_per_frame

        # Private X server, no access to the user's desktop or real audio device.
        server = subprocess.Popen(
            [
                "Xvfb",
                "-displayfd",
                "1",
                "-screen",
                "0",
                "1024x768x24",
                "-nolisten",
                "tcp",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            start_new_session=True,
        )
        try:
            assert select.select([server.stdout], [], [], 20)[0], "Xvfb did not start"
            display = server.stdout.readline().strip()
            assert display.isdigit(), display
            environment = dict(
                clean_environment,
                DISPLAY=f":{display}",
                SDL_VIDEODRIVER="x11",
                SDL_AUDIODRIVER="dummy",
            )
            # Feed a real dangerous upstream diagnostic to the packaged
            # launcher. It must remove it before native fopen(..., "w").
            environment["NESRECOMP_MAPPER_TRACE"] = str(protected)
            environment["NESRECOMP_FRAME_DUMP"] = str(root / "unexpected-frame-")

            def request(account):
                payload = {
                    "runnerId": "@simonwjackson:dr-mario/dr-mario",
                    "program": manifest["files"]["dr-mario"],
                    "contentPath": str(content),
                    "accountRoot": str(account),
                    "files": manifest["files"],
                }
                return [
                    korrid,
                    "plugin-launch",
                    str(package / "plugin.ts"),
                    json.dumps(payload),
                ]

            def key(name):
                run(["xdotool", "keydown", name], env=environment)
                time.sleep(0.15)
                run(["xdotool", "keyup", name], env=environment)
                time.sleep(0.25)

            def play(account, reload=False, measure_timing=False):
                state = account / "DrMarioRecomp"
                state.mkdir(parents=True, exist_ok=True)
                config = state / "config.ini"
                if not config.exists():
                    # Native fixture config, not a production default or schema.
                    config.write_text(
                        "[Display]\nRenderer=1\nFullscreen=0\n; preserve-test-marker\n"
                    )
                before_config = config.read_bytes()
                logfile = state / "test.log"
                with logfile.open("w") as log:
                    child = subprocess.Popen(
                        request(account),
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        env=environment,
                        start_new_session=True,
                    )
                    try:

                        def focus_window():
                            windows = subprocess.run(
                                [
                                    "xdotool",
                                    "search",
                                    "--onlyvisible",
                                    "--name",
                                    "Dr. Mario",
                                ],
                                env=environment,
                                text=True,
                                capture_output=True,
                                timeout=5,
                            )
                            if windows.returncode != 0:
                                return False
                            # SDL can replace its startup window while selecting
                            # a renderer. A name match alone is not readiness.
                            for window in reversed(windows.stdout.splitlines()):
                                focused = subprocess.run(
                                    ["xdotool", "windowfocus", "--sync", window],
                                    env=environment,
                                    text=True,
                                    capture_output=True,
                                    timeout=5,
                                )
                                if focused.returncode == 0:
                                    return True
                            return False

                        time.sleep(2)
                        wait_for(focus_window, child, "focusable game window")
                        keybinds = state / "keybinds.ini"
                        assert keybinds.is_file(), (
                            "Native keybinds escaped account storage"
                        )
                        before_keys = keybinds.read_bytes()
                        save = state / "savestates/slot01.sav"
                        if reload:
                            saved = save.read_bytes()
                            key("F1")
                            time.sleep(0.5)
                            assert save.read_bytes() == saved
                        else:
                            key("Return")
                            time.sleep(1)
                            key("Return")
                            time.sleep(2)
                            key("shift+F1")
                            wait_for(
                                lambda: save.exists() and save.stat().st_size > 10000,
                                child,
                                "native save state",
                            )
                            assert save.read_bytes()[:5] == b"NSSR\x02"
                            if measure_timing:

                                def sample_frame():
                                    previous = save.stat().st_mtime_ns
                                    size = save.stat().st_size
                                    started = time.monotonic()
                                    run(
                                        [
                                            "xdotool",
                                            "keydown",
                                            "--delay",
                                            "0",
                                            "shift+F1",
                                        ],
                                        env=environment,
                                    )
                                    try:
                                        wait_for(
                                            lambda: (
                                                save.stat().st_mtime_ns != previous
                                                and save.stat().st_size == size
                                            ),
                                            child,
                                            "timed native save",
                                            seconds=5,
                                            interval=0.005,
                                        )
                                        data = save.read_bytes()
                                        ended = time.monotonic()
                                    finally:
                                        run(
                                            ["xdotool", "keyup", "shift+F1"],
                                            env=environment,
                                        )
                                    assert data[:5] == b"NSSR\x02"
                                    # Upstream savestate.c puts uint64_t frame_count
                                    # last in SaveStateData on both target ABIs.
                                    return (
                                        started,
                                        ended,
                                        struct.unpack("<Q", data[-8:])[0],
                                    )

                                samples = [sample_frame()]
                                for _ in range(2):
                                    time.sleep(4)
                                    samples.append(sample_frame())
                                bounds = [
                                    (
                                        (b[2] - a[2] - 1) / (b[1] - a[0]),
                                        (b[2] - a[2] + 1) / (b[0] - a[1]),
                                    )
                                    for a, b in zip(samples, samples[1:])
                                ]
                                print(
                                    "Normal plugin-launch PAL frame-rate bounds:",
                                    bounds,
                                    flush=True,
                                )
                                # Bound keyboard/file-observation latency and one
                                # frame of quantization. Do not assert a guessed
                                # instant within the observed save interval.
                                assert all(hi - lo < 3 for lo, hi in bounds), (
                                    "Timing observation too uncertain"
                                )
                                assert all(
                                    lo <= 51 and hi >= 49 for lo, hi in bounds
                                ), bounds
                            rejected = subprocess.run(
                                request(account),
                                env=environment,
                                capture_output=True,
                                text=True,
                                timeout=15,
                            )
                            assert rejected.returncode != 0
                            assert "already running" in rejected.stderr, rejected.stderr
                            key("F1")
                        key("Escape")
                        assert child.wait(timeout=10) == 0
                        assert (
                            "[SaveState] Loaded from ./savestates/slot01.sav"
                            in logfile.read_text()
                        ), logfile.read_text()
                        assert config.read_bytes() == before_config, (
                            "Existing configuration changed"
                        )
                        assert keybinds.read_bytes() == before_keys, (
                            "Existing keybinds changed"
                        )
                        return save.read_bytes()
                    except Exception:
                        print(logfile.read_text(errors="replace"), file=sys.stderr)
                        raise
                    finally:
                        stop(child)

            first = root / "Player One '; $(exit 21) #"
            saved = play(first, measure_timing=True)
            assert play(first, reload=True) == saved
            # Raw-engine diagnostics are permitted only inside this private test.
            # Production plugin-launch still strips all diagnostic overrides.
            audio = root / "audio"
            audio.mkdir()
            (audio / "config.ini").write_text("[Display]\nRenderer=1\nFullscreen=0\n")
            (audio / "input.txt").write_text(
                "WAIT 60\nHOLD START\nWAIT 2\nRELEASE START\nWAIT 30\nHOLD START\nWAIT 2\nRELEASE START\nWAIT 1000\n"
            )
            # SDL dummy truncates callback waits to whole milliseconds and
            # drifts with scheduler latency. Use the existing OpenGOAL verifier's
            # private PulseAudio null-sink pattern for a real audio clock instead.
            # No physical device, shared server, or production buffer changes.
            pulse_socket = audio / "pulse.sock"
            (audio / "client.conf").write_text("")
            pulse_environment = dict(
                {
                    name: value
                    for name, value in clean_environment.items()
                    if not name.startswith("PULSE_")
                    and name != "SDL_AUDIO_DEVICE_SAMPLE_FRAMES"
                },
                HOME=str(audio),
                XDG_CONFIG_HOME=str(audio / "config"),
                XDG_CACHE_HOME=str(audio / "cache"),
                XDG_DATA_HOME=str(audio / "data"),
                XDG_RUNTIME_DIR=str(audio),
                PULSE_RUNTIME_PATH=str(audio / "pulse-runtime"),
                PULSE_STATE_PATH=str(audio / "pulse-state"),
                PULSE_CLIENTCONFIG=str(audio / "client.conf"),
                PULSE_COOKIE=str(audio / "client.cookie"),
                PULSE_SERVER=f"unix:{pulse_socket}",
                PULSE_SINK="dr_mario_test",
                # The server wrapper creates its own bus. The engine needs
                # only the private Unix audio socket, not the caller's bus.
                DBUS_SESSION_BUS_ADDRESS=f"unix:path={audio / 'no-shared-bus'}",
            )
            with (audio / "pulse.log").open("w") as pulse_log:
                pulse = subprocess.Popen(
                    [
                        "dbus-run-session",
                        "--",
                        "pulseaudio",
                        "--daemonize=no",
                        "--exit-idle-time=-1",
                        "--use-pid-file=no",
                        "--disable-shm",
                        "-n",
                        f"--load=module-native-protocol-unix socket={pulse_socket} auth-anonymous=1",
                        "--load=module-null-sink sink_name=dr_mario_test",
                    ],
                    env=pulse_environment,
                    stdout=pulse_log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                try:
                    wait_for(pulse_socket.exists, pulse, "private audio server")
                    run(
                        [
                            str(engine / "bin/DrMarioRecomp"),
                            str(content),
                            "--script",
                            str(audio / "input.txt"),
                        ],
                        cwd=audio,
                        env=dict(
                            pulse_environment,
                            DISPLAY=environment["DISPLAY"],
                            SDL_VIDEODRIVER="x11",
                            SDL_AUDIODRIVER="pulseaudio",
                            RECOMP_AUDIO_DEBUG=str(audio),
                            RECOMP_AUDIO_DEBUG_DUMP_SECS="12",
                            NESRECOMP_COSIM_HASH=str(audio / "clock.jsonl"),
                        ),
                    )
                except Exception:
                    print((audio / "pulse.log").read_text(), file=sys.stderr)
                    raise
                finally:
                    stop(pulse)
            with (audio / "events.csv").open() as events:
                fills = [
                    (float(row[0]), dict(pair.split("=", 1) for pair in row[2].split()))
                    for row in csv.reader(events)
                    if len(row) > 2 and row[1] == "bfill"
                ]
            # Upstream primes 200 ms, targets 60 ms, and drains at at most
            # 1.5% correction. That cushion alone needs at least about 9.3 seconds.
            # Exclude server startup and this intentional pre-roll drain.
            warm = next(
                i for i, entry in enumerate(fills) if entry[0] - fills[0][0] >= 10000
            )
            growth = {
                key: int(fills[-1][1][key]) - int(fills[warm][1][key])
                for key in ("under", "over", "stretch_f", "stretch_e")
            }
            print(
                "Audio bridge counter growth after 10-second warm-up:",
                growth,
                flush=True,
            )
            assert all(value == 0 for value in growth.values()), growth
            with wave.open(str(audio / "t1_apu.wav")) as pcm:
                assert pcm.getframerate() == 44100 and pcm.getnchannels() == 1
                sample_count = pcm.getnframes()
                pcm_bytes = pcm.readframes(sample_count)
            samples_per_frame = sample_count / len(fills)
            # Fills are recorded once per audio frame. Their timestamps avoid
            # measuring process startup or SDL initialization as game time.
            produced_rate = (
                samples_per_frame
                * (len(fills) - 1)
                * 1000
                / (fills[-1][0] - fills[0][0])
            )
            print(
                f"Audio samples/frame: {samples_per_frame:.3f}; samples/second: {produced_rate:.1f}",
                flush=True,
            )
            expected_samples = int(len(fills) * 44100 * 106392 * 5 / 26601712.5)
            assert abs(sample_count - expected_samples) <= 1, (
                sample_count,
                expected_samples,
            )
            assert 881 <= samples_per_frame <= 882, samples_per_frame
            assert abs(produced_rate - 44100) < 1000, produced_rate
            with wave.open(str(audio / "t3_bridge_out.wav")) as output:
                assert output.getframerate() == 44100 and output.getnchannels() == 1
                # The tap has no first-callback timestamp. Server startup and
                # buffering make its total unsuitable for a wall-rate estimate.
                # Post-warm-up bridge counters above check downstream starvation.
                output_count = output.getnframes()
                output_values = struct.unpack(
                    f"<{output_count}h", output.readframes(output_count)
                )
                assert max(output_values) - min(output_values) > 100, (
                    "Audio bridge produced no output signal"
                )
            values = struct.unpack(f"<{sample_count}h", pcm_bytes)
            assert max(values) - min(values) > 100, "Game produced no audio signal"
            clock_rows = [
                json.loads(line)
                for line in (audio / "clock.jsonl").read_text().splitlines()
            ]
            assert (
                abs(
                    statistics.mean(
                        b["bclk"] - a["bclk"]
                        for a, b in zip(clock_rows[-200:], clock_rows[-199:])
                    )
                    - 33247.5
                )
                < 0.1
            )
            second = root / "Player Two"
            play(second)
            assert (first / "DrMarioRecomp/savestates/slot01.sav").read_bytes() == saved
            assert hashlib.sha256(content.read_bytes()).hexdigest() == expected
            assert hashlib.sha256(read_rom(rom_path)).hexdigest() == expected
            assert protected.read_text() == "preserve diagnostic sentinel"
            assert not list(root.glob("unexpected-frame-*"))
            print(
                "Core launch with long literal path, save/load hotkeys, native save-file loading, account isolation, diagnostic suppression, concurrent refusal and clean exit passed",
                flush=True,
            )
        finally:
            stop(server)


if __name__ == "__main__":
    main()
