#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Opt-in native startup/render check with private graphics, audio and configuration."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import select
import subprocess
import tempfile
import time


def stop(child):
    if child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def has_late_rendered_frames(samples):
    # An early logo cannot cover a later black/white game window. This remains
    # a render heuristic: inspect captures, and do not call it gameplay proof.
    return len(samples) >= 2 and all(colors > 512 for colors in samples[-2:])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("korrid", type=Path)
    parser.add_argument("data", type=Path)
    parser.add_argument("--game", choices=("jak1", "jak2", "jak3"), required=True)
    parser.add_argument("--seconds", type=int, default=120)
    args = parser.parse_args()
    if not 10 <= args.seconds <= 600:
        parser.error("--seconds must be between 10 and 600")
    data = args.data.resolve(strict=True)
    anchor = data / "out" / args.game / "iso/GAME.CGO"
    original = digest(anchor)
    manifest = json.loads((args.package / "manifest.json").read_text())
    work = Path(tempfile.mkdtemp(prefix="opengoal-owned-check-"))
    print(f"Private test artifacts: {work}", flush=True)
    environment = os.environ.copy()
    environment.update(XDG_CONFIG_HOME=str(work / "config"), XDG_CACHE_HOME=str(work / "cache"),
                       XDG_DATA_HOME=str(work / "data"), XDG_RUNTIME_DIR=str(work),
                       SDL_VIDEODRIVER="x11", SDL_AUDIODRIVER="pulseaudio",
                       LIBGL_ALWAYS_SOFTWARE="1")
    processes = []
    logs = []

    def start(command, log_name, pass_fds=()):
        log = (work / log_name).open("w")
        logs.append(log)
        child = subprocess.Popen(command, env=environment, stdout=log,
                                 stderr=subprocess.STDOUT, pass_fds=pass_fds)
        processes.append(child)
        return child

    try:
        authority = work / "Xauthority"
        cookie = secrets.token_hex(16)
        subprocess.run(["xauth", "-f", str(authority), "add", ":0", ".", cookie], check=True)
        reader, writer = os.pipe()
        xserver = start(["Xvfb", "-displayfd", str(writer), "-screen", "0", "1280x720x24",
                         "-nolisten", "tcp", "-auth", str(authority)], "xvfb.log", (writer,))
        os.close(writer)
        try:
            number = b""
            while b"\n" not in number:
                if not select.select([reader], [], [], 20)[0]:
                    raise TimeoutError("Private Xvfb did not start")
                chunk = os.read(reader, 64)
                if not chunk:
                    raise RuntimeError((work / "xvfb.log").read_text())
                number += chunk
        finally:
            os.close(reader)
        display = ":" + number.decode().strip()
        assert display[1:].isdigit()
        subprocess.run(["xauth", "-f", str(authority), "add", display, ".", cookie], check=True)
        environment.update(DISPLAY=display, XAUTHORITY=str(authority))

        pulse_socket = work / "pulse.sock"
        pulse = start(["pulseaudio", "--daemonize=no", "--exit-idle-time=-1", "--use-pid-file=no",
                       "--disable-shm", "-n",
                       f"--load=module-native-protocol-unix socket={pulse_socket} auth-anonymous=1",
                       "--load=module-null-sink sink_name=opengoal_test"], "pulse.log")
        deadline = time.monotonic() + 20
        while not pulse_socket.exists():
            if pulse.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError((work / "pulse.log").read_text())
            time.sleep(0.1)
        environment["PULSE_SERVER"] = f"unix:{pulse_socket}"
        inputs = {
            "runnerId": f"@simonwjackson:opengoal/{args.game}",
            "program": manifest["files"]["opengoal"],
            "contentPath": str(anchor),
            "accountRoot": str(work / "account"),
            "files": manifest["files"],
        }
        game = start([str(args.korrid), "plugin-launch", str(args.package / "plugin.ts"),
                      json.dumps(inputs)], "game.log")
        color_samples = []
        elapsed = 0
        for second in sorted({10, args.seconds // 2, args.seconds}):
            try:
                code = game.wait(timeout=second - elapsed)
                raise RuntimeError(f"Game exited before the render check: {code}; {work / 'game.log'}")
            except subprocess.TimeoutExpired:
                assert xserver.poll() is None and pulse.poll() is None
                image = work / f"frame-{second}.png"
                subprocess.run(["magick", "import", "-window", "root", str(image)],
                               env=environment, check=True, timeout=20)
                colors = int(subprocess.check_output(["magick", "identify", "-format", "%k", str(image)],
                                                    text=True, timeout=20))
                print(f"{args.game}: {second}s, {colors} colors: {image}", flush=True)
                color_samples.append(colors)
            elapsed = second
        if not has_late_rendered_frames(color_samples):
            raise RuntimeError(f"Late frames are flat; inspect captures and {work / 'game.log'}")
        assert digest(anchor) == original, "Runtime changed its GAME.CGO input"
        print(f"Native startup/render probe passed: {args.game}; inspect captures for game state.", flush=True)
        print("This does not prove controller input, save/load, audible sound or full gameplay.", flush=True)
    finally:
        for child in reversed(processes):
            stop(child)
        for log in logs:
            log.close()


if __name__ == "__main__":
    main()
