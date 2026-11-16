#!/usr/bin/env -S nix shell nixpkgs#python3 --command python3
"""Local only: never copy game bytes into the source tree or Nix store.

Usage: nix/hashlink-fill-owned-check.py /nix/store/.../bin/hl-fill
The optional second argument selects an owned original outside the repository.
"""
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ORIGINAL = "59350cad475a2375b9e39d7cd13fdb6e4ed9a027fd827ae5140f913c1c07ce7e"
PATCHED = "c977689376ffce6d3400e50bb396de57ab8013846beb963e581b983acd6ac5ed"
SOURCE = Path(sys.argv[2]).expanduser() if len(sys.argv) > 2 else Path.home() / "deadcells-rescue/arfix/hlboot.orig.dat"
if not SOURCE.is_file():
    print(f"SKIP: owned fixture absent: {SOURCE}")
    sys.exit(0)
assert len(sys.argv) > 1, "pass the prebuilt hl-fill binary"
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == ORIGINAL
FIX = Path(__file__).resolve().parent.parent / "plugins/hashlink-fill/fixes/deadcells.json"

with tempfile.TemporaryDirectory(prefix="hl-fill-owned-") as temp:
    home = Path(temp) / "steam with spaces '; $() #"
    target = home / "steamapps/common/Dead Cells/hlboot.dat"
    target.parent.mkdir(parents=True)
    shutil.copyfile(SOURCE, target)
    os.chmod(target, 0o750)
    cache = home / ".korri/hashlink-fill"
    command = [sys.argv[1], "prepare", "--fix", str(FIX), "--steam-home", str(home), "--app", "588650", "--cache", str(cache), "--", "/bin/sh", "-c", "exit 23"]

    def run():
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        assert result.returncode == 23, result
        print(result.stderr.strip())
        return result.stderr

    assert "patched " in run()
    patched = target.read_bytes()
    assert hashlib.sha256(patched).hexdigest() == PATCHED
    assert [i for i, (a, b) in enumerate(zip(SOURCE.read_bytes(), patched)) if a != b] == [3088883, 3088928]
    assert (cache / ORIGINAL).read_bytes() == SOURCE.read_bytes()
    assert target.stat().st_mode & 0o777 == 0o750
    before = target.stat()
    assert "already patched" in run()
    assert target.read_bytes() == patched
    assert (target.stat().st_ino, target.stat().st_mtime_ns) == (before.st_ino, before.st_mtime_ns)
    damaged = bytearray(SOURCE.read_bytes())
    damaged[3] = 255  # Unsupported version must fail open, not write.
    target.write_bytes(damaged)
    assert "launching unchanged" in run()
    assert target.read_bytes() == damaged
    assert (cache / ORIGINAL).read_bytes() == SOURCE.read_bytes()
print("PASS: owned v35 hash, exact two offsets, backup, mode, idempotence, corrupted-file refusal and exec exit status")
