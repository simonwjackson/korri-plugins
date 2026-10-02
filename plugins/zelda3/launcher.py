#!@python@/bin/python3
"""Prepare owned ROM assets, then replace this process with the native game."""

import argparse
import fcntl
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


# Upstream README, at the revision pinned in package.nix.
ROM_SHA256 = "66871d66be19ad2c34c927d6b14cd8eb6fc3181965b6e517cb361f7316009cfb"
RESOURCES = Path("@out@/share/zelda3")
ENGINE = "@out@/libexec/zelda3"


def launch(rom: Path, directory: Path) -> None:
    rom = rom.resolve(strict=True)
    with rom.open("rb") as source:
        if hashlib.file_digest(source, "sha256").hexdigest() != ROM_SHA256:
            raise ValueError(
                "Unsupported ROM. Zelda3 requires the unheadered US ROM with "
                f"SHA-256 {ROM_SHA256}."
            )

    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory = directory.resolve(strict=True)
    # Lock the directory itself. Retain the lock across exec to prevent two
    # game processes from overwriting the same upstream save files.
    lock = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Zelda3 is already running for this account.") from None

        assets = directory / "zelda3_assets.dat"
        if not assets.exists():
            # Extraction writes beside restool.py, so it needs a private copy.
            # Publish only the finished file. A failed extraction leaves no cache.
            with tempfile.TemporaryDirectory(prefix=".zelda3-", dir=directory) as temp:
                work = Path(temp)
                shutil.copytree(RESOURCES / "assets", work / "assets")
                shutil.copytree(RESOURCES / "other", work / "other")
                for path in work.rglob("*"):
                    if path.is_dir():
                        path.chmod(0o700)
                shutil.copyfile(rom, work / "zelda3.sfc")
                # Validate the copied bytes too, before extraction, in case the
                # library file changed between the first hash and the copy.
                with (work / "zelda3.sfc").open("rb") as source:
                    if hashlib.file_digest(source, "sha256").hexdigest() != ROM_SHA256:
                        raise ValueError("The ROM changed while preparing Zelda3.")
                subprocess.run(
                    [
                        "@python@/bin/python3",
                        "-s",
                        str(work / "assets/restool.py"),
                        "--extract-from-rom",
                        "--rom",
                        str(work / "zelda3.sfc"),
                    ],
                    check=True,
                )
                (work / "zelda3_assets.dat").replace(assets)

        config = directory / "zelda3.ini"
        if not config.exists():
            # Never replace the player's config. Stage the default before rename.
            with tempfile.TemporaryDirectory(prefix=".zelda3-", dir=directory) as temp:
                staged = Path(temp) / "zelda3.ini"
                shutil.copyfile(RESOURCES / "zelda3.ini", staged)
                staged.replace(config)
        (directory / "saves").mkdir(exist_ok=True)
        os.chdir(directory)
        os.set_inheritable(lock, True)
        # Explicit --config disables upstream's search of parent directories.
        # No ROM argument: that would enable the optional emulation comparison.
        os.execv(ENGINE, [ENGINE, "--config", str(config)])
    finally:
        os.close(lock)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="Supported unheadered US ROM")
    parser.add_argument("directory", type=Path, help="Account-owned Zelda3 directory")
    args = parser.parse_args()
    try:
        launch(args.rom, args.directory)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"zelda3: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
