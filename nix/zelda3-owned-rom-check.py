#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3
"""Opt-in headless test on a build machine. Never include a ROM in Nix inputs."""

import argparse
import configparser
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import time


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("package", type=Path)
parser.add_argument("korrid", type=Path)
parser.add_argument("rom", type=Path)
args = parser.parse_args()
package = args.package.resolve(strict=True)
rom = args.rom.resolve(strict=True)
original_hash = hashlib.sha256(rom.read_bytes()).hexdigest()
assert (
    original_hash == "66871d66be19ad2c34c927d6b14cd8eb6fc3181965b6e517cb361f7316009cfb"
)
manifest = json.loads((package / "manifest.json").read_text())
native = Path(manifest["packages"]["zelda3"])
engine = (native / "libexec/zelda3").resolve()
work = Path(tempfile.mkdtemp(prefix="zelda3-owned-check-"))
account = work / "Player One '; $(exit 17)"
state = account / "zelda3"
owned_copy = work / "Owned ROM '; $(exit 19).sfc"
shutil.copyfile(rom, owned_copy)
command = [
    str(args.korrid),
    "plugin-launch",
    str(package / "plugin.ts"),
    json.dumps(
        {
            "runnerId": "@simonwjackson:zelda3/zelda3",
            "program": manifest["files"]["zelda3"],
            "contentPath": str(owned_copy),
            "accountRoot": str(account),
            "files": manifest["files"],
        }
    ),
]
env = dict(
    os.environ,
    SDL_VIDEODRIVER="dummy",
    SDL_AUDIODRIVER="dummy",
    SDL_RENDER_DRIVER="software",
)
print(f"Private test directory, retained for diagnosis: {work}", flush=True)


def session(name, check_lock=False):
    output_path = work / f"{name}.log"
    with output_path.open("w") as output:
        child = subprocess.Popen(
            command, env=env, stdout=output, stderr=subprocess.STDOUT
        )
        try:
            deadline = time.monotonic() + 180
            while True:
                if child.poll() is not None:
                    raise RuntimeError(
                        f"{name} exited before native startup: {output_path.read_text()}"
                    )
                try:
                    if Path(f"/proc/{child.pid}/exe").resolve(strict=True) == engine:
                        break
                except FileNotFoundError:
                    pass
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"{name} did not enter native engine: {output_path.read_text()}"
                    )
                time.sleep(0.1)
            time.sleep(3)
            assert child.poll() is None, output_path.read_text()
            if check_lock:
                competing = subprocess.run(
                    command, env=env, capture_output=True, text=True, timeout=15
                )
                assert competing.returncode == 1, competing.stdout + competing.stderr
                assert "already running for this account" in competing.stderr
            child.send_signal(signal.SIGTERM)
            status = child.wait(timeout=15)
            assert status == 0, f"{name}: exit {status}: {output_path.read_text()}"
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
    assert not list(state.glob(".zelda3-*"))
    print(f"{name}: native engine ran and exited cleanly", flush=True)
    return output_path.read_text()


session("cold", check_lock=True)
assets = state / "zelda3_assets.dat"
assert assets.stat().st_size > 0
cache = (assets.stat().st_mtime_ns, hashlib.sha256(assets.read_bytes()).hexdigest())
config = state / "zelda3.ini"
assert config.read_bytes() == (native / "share/zelda3/zelda3.ini").read_bytes()
seeded_config = configparser.ConfigParser(interpolation=None)
seeded_config.read(config)
assert seeded_config.getint("Graphics", "Fullscreen") == 1
# Test upstream's snapshot writer and reader without changing package defaults
# or using the player's existing saves.
text = config.read_text().replace("Autosave = 0", "Autosave = 1")
text = text.replace("OutputMethod = SDL\n", "OutputMethod = SDL-Software\n")
# Existing user choices must survive subsequent launches, including windowed mode.
text = text.replace("Fullscreen = 1\n", "Fullscreen = 0\n")
config.write_text(text)
session("warm-save")
snapshot = state / "saves/save0.sav"
assert snapshot.stat().st_size > 0
previous_snapshot = snapshot.stat().st_mtime_ns
logs = session("warm-reload")
assert "Loading slot 0" in logs, logs
assert "Saving slot 0" in logs, logs
assert snapshot.stat().st_mtime_ns > previous_snapshot
assert config.read_text() == text
assert cache == (
    assets.stat().st_mtime_ns,
    hashlib.sha256(assets.read_bytes()).hexdigest(),
)
assert hashlib.sha256(rom.read_bytes()).hexdigest() == original_hash
print(f"Assets bytes: {assets.stat().st_size}")
print(f"Assets SHA-256: {cache[1]}")
print(f"Snapshot bytes: {snapshot.stat().st_size}")
print(
    "PASS: sandboxed launch, cold extraction, default config, session lock, cached launch, snapshot save/reload, config preservation, ROM unchanged"
)
print(
    "LIMIT: dummy video/audio; no visual, audible, controller, SRAM gameplay, or device-install acceptance"
)
