#!/usr/bin/env python3
"""Opt-in owned-ROM checks. No ROM is included in the build or retained by the test."""

import hashlib
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import time
import zipfile


def run(args, **kwargs):
    try:
        return subprocess.run(
            args, check=True, text=True, capture_output=True, timeout=60, **kwargs
        )
    except subprocess.CalledProcessError as error:
        print(error.stdout, error.stderr, file=sys.stderr)
        raise


def wait_for(condition, child, message, seconds=20):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if condition():
            return
        if child.poll() is not None:
            raise AssertionError(f"Game exited {child.returncode}: {message}")
        time.sleep(0.1)
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
            env=clean_environment,
        )
        report = json.loads(result_path.read_text())
        assert report["frames_run"] == 600, report
        assert report["dispatch_miss_count"] == 0, report
        assert len(set(report["frame_hashes"].values())) > 1, report
        print("Native 600-frame smoke:", json.dumps(report), flush=True)

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

            def play(account, reload=False):
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
            saved = play(first)
            assert play(first, reload=True) == saved
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
