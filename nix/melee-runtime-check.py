#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""ROM-free checks of the actual packaged Melee launcher and native ELF."""

import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

package = Path(sys.argv[1])
system = sys.argv[2]
manifest = json.loads((package / "manifest.json").read_text())
native = Path(manifest["packages"]["melee-pc"])
launcher = Path(manifest["files"]["melee-pc"])
resources = native / "libexec/melee-pc"
engine = resources / "melee"
elf = engine.read_bytes()
assert elf[:6] == b"\x7fELF\x02\x01"
assert (
    struct.unpack_from("<H", elf, 18)[0]
    == {
        "x86_64-linux": 62,
        "aarch64-linux": 183,
    }[system]
)
assert not any(
    path.suffix.lower() in {".iso", ".gcm", ".ciso", ".rvz", ".7z", ".gci"}
    for path in native.rglob("*")
)
for name in (
    "resources/launcher.rml",
    "resources/port-menu.rml",
    "initial_pipeline_cache.db",
):
    assert (resources / name).is_file(), name
assert not (resources / "Downloads").exists()
assert not (resources / "melee-env.txt").exists()


def run(command, directory):
    return subprocess.run(
        [str(part) for part in command],
        cwd=directory,
        capture_output=True,
        text=True,
        timeout=45,
    )


with tempfile.TemporaryDirectory(prefix="melee-check-") as temp:
    work = Path(temp)
    help_result = run([launcher, "--help"], work)
    assert help_result.returncode == 0, help_result.stderr
    assert "USA 1.02 ISO" in help_result.stdout
    version = run([engine, "--version"], work)
    assert version.returncode == 0, version.stderr
    assert "melee-pc" in version.stdout and "0.2.2-beta" in version.stdout, (
        version.stdout
    )
    missing_native = run([engine, "--dvd", work / "missing.iso"], work)
    assert missing_native.returncode == 2, missing_native.stderr
    assert "cannot open disc" in missing_native.stderr

    account = work / "Player One '; $(touch injected)"
    state = account / "melee-pc"
    missing = run([launcher, "--", work / "missing.iso", account], work)
    assert missing.returncode == 1
    assert not account.exists()
    source = work / "Melee '; $(touch injected) #.iso"
    source.write_bytes(b"not a GameCube disc")
    rejected = run([launcher, "--", source, account], work)
    assert rejected.returncode == 1
    assert "extracted USA 1.02 ISO" in rejected.stderr
    assert not account.exists()
    assert not (work / "injected").exists()
    assert source.read_bytes() == b"not a GameCube disc"

    # Correct size does not admit an unknown disc. Sparse zeros are not game data.
    source.unlink()
    with source.open("wb") as output:
        output.truncate(1_459_978_240)
    rejected = run([launcher, "--", source, account], work)
    assert rejected.returncode == 1
    assert "Unsupported disc" in rejected.stderr
    assert not account.exists()

    state.mkdir(parents=True)
    settings = state / "launcher.cfg"
    settings.write_text("volume=0.5\n")
    card = state / "existing.gci"
    card.write_bytes(b"existing memory card sentinel")
    before = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in state.iterdir()
    }
    rejected = run([launcher, "--", source, account], work)
    assert rejected.returncode == 1
    assert {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in state.iterdir()
    } == before
    assert source.stat().st_size == 1_459_978_240

print(
    f"Melee PC {system}: native ELF/version, input rejection and preservation checks passed"
)
print(
    "Valid launch, account locking, graphics, input and save/load need the owned-disc test."
)
