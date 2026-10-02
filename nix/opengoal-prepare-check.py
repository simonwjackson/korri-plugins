#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Check the real preparation CLI without commercial game data."""

from pathlib import Path
import re
import subprocess
import sys
import tempfile

script, tools = sys.argv[1:]
with tempfile.TemporaryDirectory(prefix="opengoal-prepare-check-") as directory:
    root = Path(directory)
    iso = root / "not a valid disc.iso"
    iso.write_bytes(b"Not a PS2 disc image")
    output = root / "prepared"
    command = [sys.executable, script, tools, "--game", "jak2", "--iso", str(iso), "--output", str(output)]

    caller = root / "unrelated caller"
    caller.mkdir()
    rejected = subprocess.run(command, text=True, capture_output=True, cwd=caller)
    assert rejected.returncode != 0, "The real extractor must reject invalid media"
    assert "OpenGOAL preparation failed" in rejected.stderr
    # Upstream creates some relative build directories despite --proj-path.
    # Its actual startup log proves cwd is isolated, even with invalid media.
    assert re.search(r"Working Directory - " + re.escape(str(root)) + r"/opengoal-prepare-[^/\n]+/data", rejected.stdout), rejected.stdout
    assert list(caller.iterdir()) == []
    assert not output.exists(), "Failed preparation must not publish a data tree"
    assert set(root.iterdir()) == {iso, caller}, "Scratch data must be removed"
    assert iso.read_bytes() == b"Not a PS2 disc image"

    output.mkdir()
    sentinel = output / "existing game data"
    sentinel.write_text("preserve this")
    rejected = subprocess.run(command, text=True, capture_output=True)
    assert rejected.returncode != 0
    assert "Output already exists" in rejected.stderr
    assert sentinel.read_text() == "preserve this"

    # Refuse a dangling destination link rather than following it.
    link = root / "linked output"
    link.symlink_to(root / "missing destination", target_is_directory=True)
    rejected = subprocess.run(command[:-1] + [str(link)], text=True, capture_output=True)
    assert rejected.returncode != 0
    assert link.is_symlink()
    assert not (root / "missing destination").exists()

    invalid_game = command.copy()
    invalid_game[invalid_game.index("--game") + 1] = "jakx"
    rejected = subprocess.run(invalid_game, text=True, capture_output=True)
    assert rejected.returncode != 0
    assert "invalid choice" in rejected.stderr

print("OpenGOAL preparation rejects invalid media, existing destinations, links and unsupported games")
