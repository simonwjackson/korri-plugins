#!@python@/bin/python3
"""Launch Melee PC from the supported owned ISO with account-owned native state."""

import argparse
import fcntl
import hashlib
import os
from pathlib import Path
import sys


ISO_SIZE = 1_459_978_240
ISO_SHA256 = "0de05981a34156b9cedcef73c73d4244ac05cf6149ab3c9cfed917698819e464"
RESOURCES = Path("@out@/libexec/melee-pc")


def check_disc(disc: Path) -> None:
    if not disc.is_file() or disc.stat().st_size != ISO_SIZE:
        raise ValueError(
            "Select the extracted USA 1.02 ISO, not an archive or compressed disc."
        )
    with disc.open("rb") as source:
        if hashlib.file_digest(source, "sha256").hexdigest() != ISO_SHA256:
            raise ValueError(
                "Unsupported disc. Melee PC requires the supported USA 1.02 ISO."
            )


def launch(disc: Path, account_root: Path) -> None:
    disc = disc.resolve(strict=True)
    check_disc(disc)
    account_root = account_root.resolve()
    # SDL_GetPrefPath(NULL, "melee-pc") appends this native name to XDG_DATA_HOME.
    directory = account_root / "melee-pc"
    if directory.is_symlink() or disc.is_relative_to(directory):
        raise ValueError(
            "Melee PC account storage must be separate from the game image."
        )
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Melee PC is already running for this account.") from None

        # Native environment knobs include arbitrary log, recording and cache
        # paths, input FIFOs and test automation. Do not inherit host-wide values.
        env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("MELEE_")
            and key not in {"APPIMAGE", "APPDIR", "USERPROFILE"}
        }
        env.update(
            {
                "XDG_DATA_HOME": str(account_root),
                "XDG_CACHE_HOME": str(directory),
                "MELEE_CACHE_DIR": str(directory),
                "MELEE_LOG_FILE": str(directory / "melee-pc.log"),
                "LD_LIBRARY_PATH": "@runtimeLibraries@:/run/opengl-driver/lib",
                # updater.cpp downloads into HOME/Downloads or cwd and can
                # replace/relaunch only APPIMAGE. Both destinations are immutable;
                # update checks remain available, but managed code cannot change.
                "HOME": str(RESOURCES),
            }
        )
        # main.c also reads melee-env.txt and loose files relative to cwd.
        # Keep these outside writable account state and the source library.
        os.chdir(RESOURCES)
        os.set_inheritable(lock, True)
        engine = str(RESOURCES / "melee")
        os.execve(engine, [engine, "--dvd", str(disc)], env)
    finally:
        os.close(lock)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("disc", type=Path, help="Supported extracted USA 1.02 ISO")
    parser.add_argument(
        "account_root", type=Path, help="Account root supplied by Korri"
    )
    args = parser.parse_args()
    try:
        launch(args.disc, args.account_root)
    except (OSError, ValueError) as error:
        print(f"melee-pc: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
