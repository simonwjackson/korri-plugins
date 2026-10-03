#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Prepare upstream OpenGOAL data on a build machine, never on a target device."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def prepare(tools: Path, game: str, iso: Path, output: Path, instruction_set: str) -> None:
    if not iso.is_file() or iso.suffix.lower() != ".iso":
        raise ValueError("Supply an extracted retail PS2 .iso, not an archive or directory")
    if output.exists() or output.is_symlink():
        raise ValueError("Output already exists; choose a new directory to preserve existing data")
    if not output.parent.is_dir():
        raise ValueError("Output parent directory must already exist")
    with tempfile.TemporaryDirectory(prefix="opengoal-prepare-", dir=output.parent) as scratch:
        scratch_path = Path(scratch)
        data = scratch_path / "data"
        shutil.copytree(tools / "share/opengoal/data", data)
        # Nix sources are read-only. The native extractor/compiler needs a writable copy.
        for directory, _, filenames in os.walk(data):
            Path(directory).chmod(0o700)
            for filename in filenames:
                (Path(directory) / filename).chmod(0o600)
        environment = os.environ.copy()
        environment["XDG_CONFIG_HOME"] = str(scratch_path / "config")
        subprocess.run(
            [
                str(tools / "bin/extractor"),
                "--game", game,
                "--proj-path", str(data),
                "--instruction-set", instruction_set,
                "--extract", "--validate", "--decompile", "--compile",
                str(iso),
            ],
            cwd=data,
            env=environment,
            check=True,
        )
        # These are upstream game.gp outputs, not Korri marker files.
        for filename in ("KERNEL.CGO", "GAME.CGO"):
            if not (data / "out" / game / "iso" / filename).is_file():
                raise ValueError(f"OpenGOAL did not produce {filename}")
        # Reserve the destination without replacing an existing installation.
        output.mkdir(mode=0o700)
        for entry in data.iterdir():
            entry.rename(output / entry.name)
    print(f"Prepared {game} for {instruction_set}: {output}")
    print(f"Library input: {output / 'out' / game / 'iso' / 'GAME.CGO'}")
    print("Transfer the complete prepared directory. No target-side compilation is needed.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tools", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--game", choices=("jak1", "jak2", "jak3"), required=True)
    parser.add_argument("--iso", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--instruction-set", choices=("x86", "arm64"), default="x86",
                        help="Upstream GOAL code target; select arm64 for Linux ARM devices")
    args = parser.parse_args()
    try:
        prepare(args.tools, args.game, args.iso.absolute(), args.output.absolute(), args.instruction_set)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"OpenGOAL preparation failed: {error}\n")


if __name__ == "__main__":
    main()
