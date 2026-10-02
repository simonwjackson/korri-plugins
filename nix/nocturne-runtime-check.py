#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Game-data-free tests of the packaged Nocturne launcher and native ELF."""

import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

package = Path(sys.argv[1])
system = sys.argv[2]
manifest = json.loads((package / "manifest.json").read_text())
native = Path(manifest["packages"]["nocturne"])
launcher = Path(manifest["files"]["nocturne"])
engine = native / "libexec/nocturnerecomp/nocturnerecomp"
elf = engine.read_bytes()
assert elf[:6] == b"\x7fELF\x02\x01"
assert (
    struct.unpack_from("<H", elf, 18)[0]
    == {"x86_64-linux": 62, "aarch64-linux": 183}[system]
)
assert not any(
    path.suffix.lower() in {".xex", ".xexp", ".7z"} for path in native.rglob("*")
)


def run(command, directory):
    return subprocess.run(
        command, cwd=directory, capture_output=True, text=True, timeout=30
    )


with tempfile.TemporaryDirectory(prefix="nocturne-check-") as temp:
    work = Path(temp)
    help_result = run([str(launcher), "--help"], work)
    assert help_result.returncode == 0, help_result.stderr
    assert "default.xex" in help_result.stdout
    # Executes the actual architecture's native binary without retail data,
    # graphics, a display server, or a surrogate engine.
    native_start = subprocess.run(
        [str(engine), "--game_data_root=/missing-nocturne-game"],
        cwd=work,
        capture_output=True,
        text=True,
        timeout=30,
        env={**os.environ, "SDL_VIDEODRIVER": "korri-test-unavailable"},
    )
    assert native_start.returncode == 1, native_start.stderr
    assert (
        "SDL_InitSubSystem(SDL_INIT_VIDEO) failed"
        in native_start.stdout + native_start.stderr
    )
    assert (
        "korri-test-unavailable not available"
        in native_start.stdout + native_start.stderr
    )

    state = work / "Player One '; $(touch injected)/nocturnerecomp"
    missing = run(
        [str(launcher), "--", str(work / "missing/default.xex"), str(state)], work
    )
    assert missing.returncode == 1
    assert not state.exists()
    source = work / "Game '; $(touch injected) #"
    source.mkdir()
    xex = source / "default.xex"
    xex.write_bytes(b"not an Xbox executable")
    rejected = run([str(launcher), "--", str(xex), str(state)], work)
    assert rejected.returncode == 1
    assert "Unsupported default.xex" in rejected.stderr
    assert not state.exists()
    assert not (work / "injected").exists()

    # Existing cache/config/save files never authorize a different source XEX.
    state.mkdir(parents=True)
    sentinel = state / "settings.toml"
    sentinel.write_text('user_name = "Existing player"\n')
    (state / "content").mkdir()
    saved = state / "content/existing-save"
    saved.write_bytes(b"existing save")
    rejected = run([str(launcher), "--", str(xex), str(state)], work)
    assert rejected.returncode == 1
    assert sentinel.read_text() == 'user_name = "Existing player"\n'
    assert saved.read_bytes() == b"existing save"
    assert xex.read_bytes() == b"not an Xbox executable"
    assert not list(state.glob(".nocturne-*"))

print(f"Nocturne {system}: native ELF/startup and launcher rejection checks passed")
print(
    "Retail-data extraction, gameplay and save/load require the separate owned-data test."
)
