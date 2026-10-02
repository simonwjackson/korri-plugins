#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Opt-in build-machine test. Retail assets stay in a temporary directory."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import resource
import secrets
import select
import signal
import subprocess
import sys
import tempfile
import time
import zipfile


@contextmanager
def private_display(root):
    # Match nocturne-owned-check.py: xvfb-run can reuse an occupied display on
    # the shared ARM builder. Let Xvfb select its own socket and own its PID.
    authority = root / "Xauthority"
    authority.touch(mode=0o600)
    cookie = secrets.token_hex(16)
    subprocess.run(
        ["xauth", "-f", str(authority), "add", ":0", ".", cookie], check=True
    )
    reader, writer = os.pipe()
    previous = {key: os.environ.get(key) for key in ("DISPLAY", "XAUTHORITY")}
    with (root / "xvfb.log").open("w") as log:
        server = subprocess.Popen(
            [
                "Xvfb",
                "-displayfd",
                str(writer),
                "-screen",
                "0",
                "1280x900x24",
                "-nolisten",
                "tcp",
                "-auth",
                str(authority),
            ],
            pass_fds=(writer,),
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        os.close(writer)
        try:
            try:
                number = b""
                while b"\n" not in number:
                    assert select.select([reader], [], [], 20)[0], "Xvfb did not start"
                    chunk = os.read(reader, 64)
                    assert chunk, (root / "xvfb.log").read_text()
                    number += chunk
            finally:
                os.close(reader)
            display = ":" + number.decode().strip()
            assert display[1:].isdigit(), (root / "xvfb.log").read_text()
            subprocess.run(
                ["xauth", "-f", str(authority), "add", display, ".", cookie], check=True
            )
            os.environ.update(DISPLAY=display, XAUTHORITY=str(authority))
            yield
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            if server.poll() is None:
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()


def wait_for(predicate, game, log, timeout=90):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if game.poll() is not None:
            raise AssertionError(
                f"Game exited {game.returncode}:\n{log.read_text()[-4000:]}"
            )
        value = predicate()
        if value:
            return value
        time.sleep(0.2)
    raise AssertionError(f"Game readiness timed out:\n{log.read_text()[-4000:]}")


def window_for(game):
    result = subprocess.run(
        [
            "xdotool",
            "search",
            "--onlyvisible",
            "--pid",
            str(game.pid),
            "--name",
            "2 Ship",
        ],
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()[0] if result.returncode == 0 else None


def key(value):
    # Hold across slow software-rendered frames on the shared ARM builder.
    subprocess.run(["xdotool", "key", "--delay", "500", value], check=True)
    time.sleep(1)


def run_game(command, env, root, first):
    log = root / ("first.log" if first else "restart.log")
    with log.open("w") as output:
        game = subprocess.Popen(
            command, env=env, stdout=output, stderr=subprocess.STDOUT
        )
        try:
            window = wait_for(lambda: window_for(game), game, log)
            wait_for(
                lambda: "Starting 2 Ship 2 Harkinian version" in log.read_text(),
                game,
                log,
            )
            time.sleep(7)
            assert game.poll() is None, log.read_text()[-4000:]
            subprocess.run(["xdotool", "windowfocus", "--sync", window], check=True)
            if first:
                second = subprocess.run(
                    command, env=env, capture_output=True, text=True, timeout=15
                )
                assert (
                    second.returncode == 1
                    and "already running for this account" in second.stderr
                ), second.stderr
                # z_en_mag.c and z_file_choose_NES.c both accept A to advance.
                # Keep sending A through their transitions, then enter letters.
                # Start must come last: z_file_nameset_NES.c selects END even
                # when the name is empty, so repeated Start/A can trap the test.
                for _ in range(16):
                    assert game.poll() is None, log.read_text()[-4000:]
                    key("x")
                key("space")
                key("x")
                wait_for(
                    lambda: (root / "account/2ship/saves/file1.json").is_file(),
                    game,
                    log,
                    30,
                )
            else:
                key("space")
                key("x")
                key("x")
            game.send_signal(signal.SIGINT if first else signal.SIGTERM)
            try:
                game.wait(timeout=15)
            except subprocess.TimeoutExpired:
                raise AssertionError(
                    "Native shutdown hung after SIGINT/SIGTERM"
                ) from None
            assert game.returncode == 0, (game.returncode, log.read_text()[-4000:])
        finally:
            if game.poll() is None:
                game.kill()
                game.wait()


def stop_at_first_window(command, env, root):
    log = root / "early-stop.log"
    with log.open("w") as output:
        game = subprocess.Popen(
            command, env=env, stdout=output, stderr=subprocess.STDOUT
        )
        try:
            wait_for(lambda: window_for(game), game, log)
            game.terminate()
            game.wait(timeout=15)
            assert game.returncode == 0, (game.returncode, log.read_text()[-4000:])
        finally:
            if game.poll() is None:
                game.kill()
                game.wait()


def main():
    if len(sys.argv) != 4:
        raise SystemExit("Usage: verify-2ship PACKAGE KORRID ROM_PATH")
    package, korrid, path = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3])
    with path.open("rb") as source:
        original = source.read(32 * 1024 * 1024 + 1)
    digest = hashlib.sha256(original).hexdigest()
    if digest == "8dc31559174f958a938ab7eccb25dd310a4167f98cb68a521181f4653b684431":
        normalized = bytearray(original)
        normalized[0::2], normalized[1::2] = original[1::2], original[0::2]
        normalized = bytes(normalized)
    elif digest == "efb1365b3ae362604514c0f9a1a2d11f5dc8688ba5be660a37debf5e3be43f2b":
        normalized = original
    else:
        raise SystemExit("Supply the measured NTSC-U 1.0 bare ROM, not a ZIP")
    manifest = json.loads((package / "manifest.json").read_text())
    with (
        tempfile.TemporaryDirectory(prefix="korri-2ship-owned-rom-") as temporary,
        private_display(Path(temporary)),
    ):
        root = Path(temporary)
        directory = root / "account/2ship"
        env = dict(os.environ, SDL_AUDIODRIVER="dummy", LIBGL_ALWAYS_SOFTWARE="1")
        plan = dict(
            runnerId="@simonwjackson:2ship/2ship",
            program=manifest["files"]["2ship"],
            accountRoot=str(root / "account"),
            files=manifest["files"],
        )
        rom = root / "ROM '; $(exit 19) #.n64"
        rom.write_bytes(original)
        rom.chmod(0o444)
        plan["contentPath"] = str(rom)
        command = [
            korrid,
            "plugin-launch",
            str(package / "plugin.ts"),
            json.dumps(plan),
        ]
        run_game(command, env, root, True)
        archive = directory / "mm.o2r"
        with zipfile.ZipFile(archive) as data:
            assert data.testzip() is None
            assert data.read("version") == bytes.fromhex("015354631c")
            version_records = {
                name: data.read(name) for name in ["version", "portVersion"]
            }
            entries = len(data.namelist())
        initial_archive = archive.stat()
        save_path = directory / "saves/file1.json"
        saved = save_path.read_bytes()
        assert json.loads(saved)["type"] == "2S2H_SAVE"
        assert (directory / "2ship2harkinian.json").is_file()
        assert rom.read_bytes() == original
        print(
            f"First-run extraction ({entries} entries), visible-window startup, keyboard save and SIGINT shutdown passed",
            flush=True,
        )

        normalized_rom = root / "Normalized '; $(exit 19) #.z64"
        normalized_rom.write_bytes(normalized)
        normalized_rom.chmod(0o444)
        plan["contentPath"] = str(normalized_rom)
        command[-1] = json.dumps(plan)
        run_game(command, env, root, False)
        assert archive.stat().st_ino == initial_archive.st_ino
        assert archive.stat().st_mtime_ns == initial_archive.st_mtime_ns
        assert save_path.read_bytes() == saved, "Restart changed the persisted save"
        assert normalized_rom.read_bytes() == normalized
        print(
            "Normalized ROM, archive reuse, save retention and SIGTERM shutdown passed",
            flush=True,
        )

        stop_at_first_window(command, env, root)
        assert save_path.read_bytes() == saved
        print("SIGTERM at the first visible window passed", flush=True)

        # Regression: CRC-valid version records alone are not game assets.
        with zipfile.ZipFile(archive, "w") as incomplete:
            for name, contents in version_records.items():
                incomplete.writestr(name, contents)
        config_before = (directory / "2ship2harkinian.json").read_bytes()
        incomplete_bytes = archive.read_bytes()

        def limit_staging_file():
            resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))

        failed_staging = subprocess.run(
            command,
            env=env,
            capture_output=True,
            text=True,
            preexec_fn=limit_staging_file,
            timeout=30,
        )
        assert (
            failed_staging.returncode == 1
            and "2 Ship launch failed:" in failed_staging.stderr
        ), failed_staging.stderr
        assert archive.read_bytes() == incomplete_bytes
        assert save_path.read_bytes() == saved
        assert (directory / "2ship2harkinian.json").read_bytes() == config_before
        assert not list(directory.glob(".2ship-extract-*"))
        print(
            "Failed staging preserves existing archives, config and saves", flush=True
        )
        with (root / "regeneration.log").open("w") as output:
            result = subprocess.run(
                command,
                env=dict(env, SDL_VIDEODRIVER="korri-nonexistent-driver"),
                stdout=output,
                stderr=subprocess.STDOUT,
                timeout=180,
            )
        assert result.returncode != 0, (
            "The deliberate invalid video driver unexpectedly worked"
        )
        with zipfile.ZipFile(archive) as repaired:
            assert len(repaired.namelist()) == entries and repaired.testzip() is None
        assert save_path.read_bytes() == saved
        assert (directory / "2ship2harkinian.json").read_bytes() == config_before
        assert not list(directory.glob(".2ship-extract-*"))
        print(
            "Incomplete archive regenerated without changing config/saves; temporary extraction files removed",
            flush=True,
        )
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, "Source ROM changed"
    print(
        "Temporary retail assets removed. Physical-device graphics, audio and controllers remain unverified."
    )


if __name__ == "__main__":
    main()
