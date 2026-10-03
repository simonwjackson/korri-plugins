#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Opt-in owned-ROM test on a build machine, with a private software display."""

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


@contextmanager
def private_display(root):
    authority = root / "Xauthority"
    authority.touch(mode=0o600)
    cookie = secrets.token_hex(16)
    subprocess.run(
        ["xauth", "-f", str(authority), "add", ":0", ".", cookie], check=True
    )
    reader, writer = os.pipe()
    with (root / "display.log").open("w") as log:
        server = subprocess.Popen(
            [
                "Xvfb",
                "-displayfd",
                str(writer),
                "-screen",
                "0",
                "1280x960x24",
                "-nolisten",
                "tcp",
                "-noreset",
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
                assert select.select([reader], [], [], 20)[0], "Xvfb did not start"
                number = os.read(reader, 64).decode().strip()
                assert number.isdigit(), (root / "display.log").read_text()
            finally:
                os.close(reader)
            display = ":" + number
            subprocess.run(
                ["xauth", "-f", str(authority), "add", display, ".", cookie], check=True
            )
            yield dict(
                os.environ,
                DISPLAY=display,
                XAUTHORITY=str(authority),
                SDL_VIDEODRIVER="x11",
                SDL_AUDIODRIVER="dummy",
            )
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()


def wait_for(predicate, game, log, timeout=90):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        assert game.poll() is None, (game.returncode, log.read_text()[-6000:])
        found = predicate()
        if found:
            return found
        time.sleep(0.2)
    raise AssertionError(f"Native game readiness timed out: {log.read_text()[-6000:]}")


def window_for(game, env):
    found = subprocess.run(
        ["xdotool", "search", "--onlyvisible", "--pid", str(game.pid)],
        env=env,
        capture_output=True,
        text=True,
    )
    return found.stdout.splitlines()[0] if found.returncode == 0 else None


def verify_refusals(root, package, korrid, plan, env):
    for case in ("rom-link", "resource-link", "resource-directory"):
        account = root / case
        state = account / "drmario64.us"
        (state / "saves").mkdir(parents=True)
        save = state / "saves/drmario64.us.bin"
        save.write_bytes(bytes(range(256)) * 2)
        sentinel = root / f"unrelated-{case}"
        sentinel.write_text("untouched")
        if case == "rom-link":
            # A dangling link must be rejected, not followed or replaced.
            path = state / "drmario64.us.z64"
            path.symlink_to(root / "missing-original.z64")
        elif case == "resource-link":
            path = state / "assets"
            path.symlink_to(sentinel)
        else:
            path = state / "assets"
            path.mkdir()
            (path / "keep").write_text("untouched")
        invalid = dict(plan, accountRoot=str(account))
        failure = subprocess.run(
            [korrid, "plugin-launch", str(package / "plugin.ts"), json.dumps(invalid)],
            env=env,
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert failure.returncode == 1 and "Refusing to replace" in failure.stderr, (
            failure.stderr
        )
        assert save.read_bytes() == bytes(range(256)) * 2
        assert sentinel.read_text() == "untouched"
        if case == "resource-directory":
            assert (path / "keep").read_text() == "untouched"
        else:
            assert path.is_symlink()


def stop_during_startup(command, env, root, artifacts):
    # SDL creates its window before native rendering and the first VI complete.
    # Exercise the normal host command, without a special production test flag.
    for attempt in range(3):
        log = root / f"early-stop-{attempt}.log"
        with log.open("w") as output:
            game = subprocess.Popen(
                command, env=env, stdout=output, stderr=subprocess.STDOUT
            )
            try:
                window = wait_for(lambda: window_for(game, env), game, log)
                if attempt == 2:
                    subprocess.run(
                        ["drmario64-window-close", window], env=env, check=True
                    )
                else:
                    game.send_signal(signal.SIGTERM)
                game.wait(timeout=20)
                assert game.returncode == 0, (game.returncode, log.read_text()[-6000:])
            finally:
                if game.poll() is None:
                    game.kill()
                    game.wait()
                if artifacts:
                    (artifacts / log.name).write_text(log.read_text())


def check_failed_save(command, env, state, root, artifacts):
    log = root / "failed-save.log"
    saves = state / "saves"
    mode = saves.stat().st_mode & 0o777
    with log.open("w") as output:
        game = subprocess.Popen(
            command, env=env, stdout=output, stderr=subprocess.STDOUT
        )
        try:
            wait_for(lambda: window_for(game, env), game, log)
            time.sleep(5)
            assert game.poll() is None, log.read_text()[-6000:]
            saved = (saves / "drmario64.us.bin").read_bytes()
            saves.chmod(0o500)
            game.send_signal(signal.SIGTERM)
            game.wait(timeout=20)
            assert game.returncode == 1, (game.returncode, log.read_text()[-6000:])
            assert "[Shutdown] Final EEPROM flush: failed" in log.read_text()
            assert "[Shutdown] Persistence complete: failed" in log.read_text()
            assert (saves / "drmario64.us.bin").read_bytes() == saved
        finally:
            saves.chmod(mode)
            if game.poll() is None:
                game.kill()
                game.wait()
            if artifacts:
                (artifacts / log.name).write_text(log.read_text())


def main():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if len(sys.argv) not in (4, 5):
        raise SystemExit(
            "Usage: verify-drmario64 PACKAGE KORRID ROM_PATH [ARTIFACT_DIRECTORY]"
        )
    package, korrid, content = (
        Path(sys.argv[1]),
        sys.argv[2],
        Path(sys.argv[3]).resolve(),
    )
    artifacts = Path(sys.argv[4]).resolve() if len(sys.argv) == 5 else None
    if artifacts:
        artifacts.mkdir(parents=True, exist_ok=True)
    with content.open("rb") as source:
        original = source.read(4 * 1024 * 1024 + 1)
    digest = hashlib.sha256(original).hexdigest()
    assert digest in {
        "613778b244784492a881c0d72d6017f82c39026706a406bd7ef95c6f33e53b89",
        "bb2c0dec0a8287ad256929563d0509801c2f239df883c1cf52cab05b23bd77b6",
    }, "Supply the measured US bare ROM, not a ZIP"
    manifest = json.loads((package / "manifest.json").read_text())
    with tempfile.TemporaryDirectory(prefix="korri-drmario64-owned-") as temporary:
        root = Path(temporary)
        # Verify the host passes a path with shell metacharacters literally.
        rom = root / "ROM '; $(exit 19) #.n64"
        rom.write_bytes(original)
        rom.chmod(0o444)
        account = root / "account"
        state = account / "drmario64.us"
        plan = dict(
            runnerId="@simonwjackson:drmario64/drmario64",
            program=manifest["files"]["drmario64"],
            files=manifest["files"],
            contentPath=str(rom),
            accountRoot=str(account),
        )
        command = [
            korrid,
            "plugin-launch",
            str(package / "plugin.ts"),
            json.dumps(plan),
        ]
        with private_display(root) as env:
            home = root / "home"
            home.mkdir()
            env.update(HOME=str(home), XDG_CACHE_HOME=str(root / "cache"))
            verify_refusals(root, package, korrid, plan, env)
            early_plan = dict(plan, accountRoot=str(root / "startup-account"))
            stop_during_startup(
                [
                    korrid,
                    "plugin-launch",
                    str(package / "plugin.ts"),
                    json.dumps(early_plan),
                ],
                env,
                root,
                artifacts,
            )
            original_state = state
            for attempt in range(3):
                if attempt == 1:
                    # config.cpp loads and saves this native setting. Prove a
                    # non-default value survives restart, not merely valid JSON.
                    sound = json.loads((state / "sound.json").read_text())
                    sound["main_volume"] = 47
                    (state / "sound.json").write_text(json.dumps(sound))
                    (state / "assets").unlink()
                    (state / "assets").symlink_to(
                        "/nix/store/00000000000000000000000000000000-drmario64-old/share/drmario64/assets"
                    )
                if attempt == 2:
                    # Seed a second account from a real upstream record, changing
                    # only the documented native sound field. The first stays 47.
                    state = root / "second-account/drmario64.us"
                    state.mkdir(parents=True)
                    sound = json.loads((original_state / "sound.json").read_text())
                    sound["main_volume"] = 13
                    (state / "sound.json").write_text(json.dumps(sound))
                    second_plan = dict(plan, accountRoot=str(state.parent))
                    command = [
                        korrid,
                        "plugin-launch",
                        str(package / "plugin.ts"),
                        json.dumps(second_plan),
                    ]
                log = root / f"game-{attempt}.log"
                with log.open("w") as output:
                    game = subprocess.Popen(
                        command, env=env, stdout=output, stderr=subprocess.STDOUT
                    )
                    try:
                        window = wait_for(lambda: window_for(game, env), game, log)
                        subprocess.run(
                            ["xdotool", "windowfocus", "--sync", window],
                            env=env,
                            check=True,
                        )
                        time.sleep(8)
                        assert game.poll() is None, log.read_text()[-6000:]
                        # pi.cpp creates saves/ only after loading the game ROM.
                        wait_for(lambda: (state / "saves").is_dir(), game, log)
                        imported = state / "drmario64.us.z64"
                        assert (
                            hashlib.sha256(imported.read_bytes()).hexdigest()
                            == "bb2c0dec0a8287ad256929563d0509801c2f239df883c1cf52cab05b23bd77b6"
                        )
                        second = subprocess.run(
                            command, env=env, capture_output=True, text=True, timeout=15
                        )
                        assert (
                            second.returncode == 1
                            and "already running for this account" in second.stderr
                        ), second.stderr
                        # Source input.cpp maps Enter to Start, Space to A.
                        for key in (
                            "Return",
                            "space",
                            "space",
                            "space",
                            "space",
                            "space",
                            "space",
                            "Return",
                        ):
                            subprocess.run(
                                ["xdotool", "key", "--delay", "300", key],
                                env=env,
                                check=True,
                            )
                            time.sleep(2)
                            assert game.poll() is None, log.read_text()[-6000:]
                        if artifacts:
                            subprocess.run(
                                [
                                    "magick",
                                    "import",
                                    "-window",
                                    window,
                                    str(artifacts / f"game-{attempt}.png"),
                                ],
                                env=env,
                                check=True,
                            )
                        if attempt == 1:
                            subprocess.run(
                                ["drmario64-window-close", window], env=env, check=True
                            )
                        else:
                            game.send_signal(signal.SIGTERM)
                        game.wait(timeout=20)
                        assert game.returncode == 0, (
                            game.returncode,
                            log.read_text()[-6000:],
                        )
                    finally:
                        if game.poll() is None:
                            game.kill()
                            game.wait()
                        if artifacts:
                            (artifacts / log.name).write_text(log.read_text())
                assert rom.read_bytes() == original
                assert len((state / "saves/drmario64.us.bin").read_bytes()) == 512
                shutdown = log.read_text()
                ordered = [
                    "[Shutdown] Game parked at IDLE safe point",
                    "[Shutdown] Final EEPROM flush: ok",
                    "[Shutdown] Mod settings flush: ok",
                    "[Shutdown] Native settings flush: ok",
                    "[Shutdown] Persistence complete: ok",
                ]
                positions = [shutdown.index(marker) for marker in ordered]
                assert positions == sorted(positions), shutdown
                assert not list(state.glob(".drmario64-*"))
                assert (state / "assets").is_dir()
                if attempt == 1:
                    assert (
                        json.loads((state / "sound.json").read_text())["main_volume"]
                        == 47
                    )
                if attempt == 2:
                    assert (
                        json.loads((state / "sound.json").read_text())["main_volume"]
                        == 13
                    )
                    assert (
                        json.loads((original_state / "sound.json").read_text())[
                            "main_volume"
                        ]
                        == 47
                    )
            # ROM reuse and native settings must survive a second launch.
            for filename in (
                "general.json",
                "graphics.json",
                "controls.json",
                "sound.json",
            ):
                assert isinstance(json.loads((state / filename).read_text()), dict), (
                    filename
                )
            check_failed_save(command, env, state, root, artifacts)
            assert hashlib.sha256(content.read_bytes()).hexdigest() == digest
    print(
        "Dr. Mario 64 native startup/restart, host launch, input delivery, locking and source preservation passed"
    )
    print(
        "This test uses dummy audio and software video. It does not prove handheld playability or campaign save/reload."
    )


if __name__ == "__main__":
    main()
