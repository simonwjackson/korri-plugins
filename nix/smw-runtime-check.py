#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Opt-in smoke test on a build machine. Retail bytes never enter Nix outputs."""

import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile


def run_game(
    korrid: str, source: Path, launch: dict, env: dict, check_lock: bool
) -> str:
    command = [korrid, "plugin-launch", str(source), json.dumps(launch)]
    game = subprocess.Popen(
        command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        try:
            stdout, stderr = game.communicate(timeout=3)
            raise AssertionError(
                f"Game exited early: {game.returncode}\n{stdout}\n{stderr}"
            )
        except subprocess.TimeoutExpired:
            if check_lock:
                second = subprocess.run(
                    command, env=env, capture_output=True, text=True, timeout=10
                )
                assert second.returncode == 1, second.stderr
                assert "already running for this account" in second.stderr, (
                    second.stderr
                )
            game.send_signal(signal.SIGINT)
            stdout, stderr = game.communicate(timeout=10)
        assert game.returncode == 0, f"{game.returncode}: {stdout}\n{stderr}"
        return stdout
    finally:
        if game.poll() is None:
            game.kill()
            game.communicate()


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: verify-smw PACKAGE KORRID ROM_PATH")
    package, korrid, path = sys.argv[1:]
    original = Path(path).read_bytes()
    digest = hashlib.sha256(original).hexdigest()
    if digest == "d70c9c7716ad12c674fc7dd744736aa48d4d7b4237f58066be620fda26024872":
        normalized = original[512:]
    elif digest == "0838e531fe22c077528febe14cb3ff7c492f1f5fa8de354192bdff7137c27f5b":
        normalized = original
    else:
        raise SystemExit(
            "Supply the measured USA SMW ROM, with or without its copier header"
        )
    manifest = json.loads((Path(package) / "manifest.json").read_text())
    with tempfile.TemporaryDirectory(prefix="korri-smw-owned-rom-") as temporary:
        root = Path(temporary)
        account = root / "account '; $(exit 19) #"
        directory = account / "smw"
        directory.mkdir(parents=True)
        # Headless behavior does not prove physical graphics, audio or controllers.
        env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
        launch = {
            "runnerId": "@simonwjackson:super-mario-world/smw",
            "program": manifest["files"]["smw"],
            "accountRoot": str(account),
            "files": manifest["files"],
        }
        bootstrap_rom = root / "bootstrap.smc"
        bootstrap_rom.write_bytes(original)
        launch["contentPath"] = str(bootstrap_rom)
        # Exercise first-run config creation, then force a real SDL startup failure.
        bootstrap = subprocess.run(
            [
                korrid,
                "plugin-launch",
                str(Path(package) / "plugin.ts"),
                json.dumps(launch),
            ],
            env=dict(env, SDL_VIDEODRIVER="korri-nonexistent-driver"),
            capture_output=True,
            text=True,
            timeout=15,
        )
        assert bootstrap.returncode == 1, bootstrap.stderr
        assert "Failed to init SDL" in bootstrap.stdout, bootstrap.stdout
        initial_config = (directory / "smw.ini").read_text()
        assert "Autosave = 0" in initial_config and "Fullscreen = 0" in initial_config
        assert (directory / "smw_assets.dat").is_file()
        config = "[General]\nAutosave = 1\n[Graphics]\nOutputMethod = SDL-Software\n"
        (directory / "smw.ini").write_text(config)
        print("First-run native config creation passed; existing config is tested next")
        if original == normalized:
            print(
                "Header removal is not exercised: the supplied ROM is already unheadered"
            )
        assets_digest = None
        for index, content in enumerate([original, normalized]):
            rom = root / f"ROM {index} '; $(exit 19) #.smc"
            rom.write_bytes(content)
            rom.chmod(0o444)
            launch["contentPath"] = str(rom)
            stdout = run_game(
                korrid, Path(package) / "plugin.ts", launch, env, index == 0
            )
            if index == 1:
                assert "Failed fopen" not in stdout, stdout
                assert "Loading slot 0: saves/save0.sav" in stdout, stdout
            snapshot = directory / "saves" / "save0.sav"
            assert snapshot.stat().st_size > 0
            assets = (directory / "smw_assets.dat").read_bytes()
            current_digest = hashlib.sha256(assets).hexdigest()
            if assets_digest is not None:
                assert current_digest == assets_digest, (
                    "ROM forms extracted different assets"
                )
            assets_digest = current_digest
            assert (directory / "smw.ini").read_text() == config
            assert rom.read_bytes() == content
            assert not list(directory.glob(".smw-extract-*"))
            print(
                f"ROM form {index}: startup, exit, config preservation and snapshot passed"
            )
    assert Path(path).read_bytes() == original, "Source ROM changed"
    print(
        "Packaged sandboxed launch, concurrent-launch refusal and snapshot reload passed."
    )
    print(
        "Temporary retail assets removed. Physical-device gameplay remains unverified."
    )


if __name__ == "__main__":
    main()
