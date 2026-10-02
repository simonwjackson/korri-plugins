#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3
"""ROM-free checks of the actual packaged launcher and native executable."""

import configparser
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile


package = Path(sys.argv[1])
system = sys.argv[2]
manifest = json.loads((package / "manifest.json").read_text())
native = Path(manifest["packages"]["zelda3"])
launcher = Path(manifest["files"]["zelda3"])
engine = native / "libexec/zelda3"
resources = native / "share/zelda3"

# This is the native configuration consumed by the real engine, not a TS setting.
config = configparser.ConfigParser(interpolation=None)
config.read(resources / "zelda3.ini")
assert config.getint("Graphics", "Fullscreen") == 1, (
    "Fresh installs must request desktop fullscreen"
)
assert config.get("KeyMap", "Fullscreen") == "Alt+Return"

# Inspect the actual ELF, then execute it on the architecture's build machine.
elf = engine.read_bytes()
assert elf[:6] == b"\x7fELF\x02\x01"
assert (
    struct.unpack_from("<H", elf, 18)[0]
    == {
        "x86_64-linux": 62,
        "aarch64-linux": 183,
    }[system]
)
assert (native / "share/licenses/zelda3/LICENSE.txt").is_file()
opus_notice = (native / "share/licenses/zelda3/OPUS-COPYING").read_text()
assert "Skype Limited" in opus_notice
assert "Neither the name of Internet Society" in opus_notice
assert not (resources / "zelda3_assets.dat").exists()
assert not (resources / "saves").exists()
assert not any(
    path.suffix.lower() in {".sfc", ".smc", ".sav"} for path in native.rglob("*")
)


def run(command, cwd):
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=30)


with tempfile.TemporaryDirectory(prefix="zelda3-check-") as temp:
    work = Path(temp)
    missing = run([str(engine), "--config", str(resources / "zelda3.ini")], work)
    assert missing.returncode != 0
    assert "Failed to read zelda3_assets.dat" in missing.stdout + missing.stderr
    (work / "zelda3_assets.dat").write_bytes(b"not valid game assets")
    invalid = run([str(engine), "--config", str(resources / "zelda3.ini")], work)
    assert invalid.returncode != 0
    assert "Invalid assets file" in invalid.stdout + invalid.stderr

    help_result = run([str(launcher), "--help"], work)
    assert help_result.returncode == 0, help_result.stderr
    assert "Account-owned Zelda3 directory" in help_result.stdout
    absent = run([str(launcher)], work)
    assert absent.returncode != 0
    state = work / "Player One/zelda3"
    absent = run([str(launcher), "--", str(work / "missing.sfc"), str(state)], work)
    assert absent.returncode != 0
    assert not state.exists()

    # Never initialize writable state or run extraction for an unsupported ROM.
    rom = work / "Zelda '; $(touch injected) %.smc"
    rom.write_bytes(b"not a ROM")
    rejected = run([str(launcher), "--", str(rom), str(state)], work)
    assert rejected.returncode == 1, rejected.stderr
    assert "Unsupported ROM" in rejected.stderr
    assert not state.exists()
    assert not (work / "injected").exists()

    # A cache must not bypass the whole-file identity check on later launches.
    state.mkdir(parents=True)
    (state / "zelda3_assets.dat").write_bytes(b"existing cache")
    (state / "zelda3.ini").write_text("existing user configuration")
    (state / "saves").mkdir()
    (state / "saves/sram.dat").write_bytes(b"existing save")
    rejected = run([str(launcher), "--", str(rom), str(state)], work)
    assert rejected.returncode == 1
    assert "Unsupported ROM" in rejected.stderr
    assert (state / "zelda3_assets.dat").read_bytes() == b"existing cache"
    assert (state / "zelda3.ini").read_text() == "existing user configuration"
    assert (state / "saves/sram.dat").read_bytes() == b"existing save"
    assert not list(state.glob(".zelda3-*"))

    # Use the launcher's real interpreter and shipped extractor dependencies.
    python = launcher.read_text().splitlines()[0].removeprefix("#!")
    imports = work / "check-imports.py"
    imports.write_text("import PIL.Image\nimport yaml\n")
    dependencies = run([python, "-s", str(imports)], work)
    assert dependencies.returncode == 0, dependencies.stderr
    extraction = run(
        [
            python,
            "-s",
            str(resources / "assets/restool.py"),
            "--extract-from-rom",
            "--rom",
            str(rom),
        ],
        work,
    )
    assert extraction.returncode != 0
    assert "ROM with hash" in extraction.stderr, extraction.stderr

print(f"Zelda3 {system}: native ELF, startup, dependencies and rejection checks passed")
print(
    "No owned ROM supplied: successful extraction, gameplay and saves are not tested here"
)
