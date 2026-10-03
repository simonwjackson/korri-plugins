#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Make a private canonical ROM for requireFile without changing the original."""

import os
from pathlib import Path
import runpy
import sys


def main() -> int:
    if len(sys.argv) != 4:
        print(
            "Usage: prepare-drmario64 ROM_PATH OUTPUT_PATH",
            file=sys.stderr,
        )
        return 2
    source, rom, output = map(Path, sys.argv[1:])
    if output.name != "drmario64.us.z64":
        print(
            "Output must be named drmario64.us.z64 for Nix requireFile", file=sys.stderr
        )
        return 2
    try:
        # Use the launcher's measured identity and byte-order validation unchanged.
        canonical = runpy.run_path(str(source))["read_rom"](rom)
        descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as target:
            target.write(canonical)
        print(f"Prepared {output}. Keep this ROM and compiled outputs private.")
    except (OSError, ValueError) as error:
        print(f"ROM preparation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
