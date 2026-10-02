#!@python@
"""Launch the private build with upstream's data layout; never compile on launch."""

import argparse
import fcntl
import hashlib
import os
from pathlib import Path
import re
import sys
import tempfile

ENGINE = Path("@engine@")
RESOURCES = Path("@resources@")
ROM_SHA256 = "b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0"


def resource_link(root: Path, relative: str) -> None:
    destination = root / relative
    target = RESOURCES / relative
    if destination.is_symlink():
        previous = os.readlink(destination)
        if previous == str(target):
            return
        # Replace only links into earlier private ActRaiser packages. Never
        # overwrite user-authored resource directories or unrelated links.
        pattern = r"/nix/store/[a-z0-9]{32}-actraiser-[^/]+/share/ActRaiserRecomp/"
        if not re.fullmatch(pattern + re.escape(relative), previous):
            raise ValueError(
                f"Refusing to replace unrelated resource link: {destination}"
            )
    elif destination.exists():
        raise ValueError(
            f"Preserve or move the existing resource directory: {destination}"
        )
    with tempfile.TemporaryDirectory(dir=destination.parent) as temporary:
        link = Path(temporary) / "resource"
        link.symlink_to(target, target_is_directory=True)
        link.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path, help="Owned, headerless ActRaiser USA ROM")
    args = parser.parse_args()
    rom = args.rom.resolve(strict=True)
    if (
        rom.stat().st_size != 1048576
        or hashlib.sha256(rom.read_bytes()).hexdigest() != ROM_SHA256
    ):
        raise ValueError(
            "Unsupported ROM: supply the headerless ActRaiser USA cartridge, not Arcade"
        )

    # Upstream installer/internal/appdata/path.go defines this Linux layout.
    # Korri supplies AR_USER_DATA_DIR under its accountRoot treaty instead.
    selected = os.environ.get("AR_USER_DATA_DIR")
    if selected:
        root = Path(selected)
    else:
        data = os.environ.get("XDG_DATA_HOME", "")
        base = (
            Path(data)
            if data and Path(data).is_absolute()
            else Path.home() / ".local/share"
        )
        root = base / "ActRaiserRecomp/game"
    if not root.is_absolute():
        raise ValueError("AR_USER_DATA_DIR must be absolute")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    # Linux directory locking needs no extra persistent lock-file schema.
    lock = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as error:
        raise ValueError(
            "ActRaiser is already running in this data directory"
        ) from error
    os.set_inheritable(lock, True)
    for relative in ("game-assets", "game-assets/languages"):
        directory = root / relative
        if directory.is_symlink():
            raise ValueError(f"Data directory must not be a symlink: {directory}")
        directory.mkdir(mode=0o700, exist_ok=True)
    for relative in (
        "defaults",
        "game-assets/fonts",
        "game-assets/languages/native-us",
    ):
        resource_link(root, relative)
    environment = dict(os.environ, AR_USER_DATA_DIR=str(root))
    # SDL loads Vulkan with dlopen; it is not a DT_NEEDED ELF dependency.
    environment.setdefault("SDL_VULKAN_LIBRARY", "@vulkan@")
    os.execve(ENGINE, [str(ENGINE), str(rom)], environment)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"ActRaiser: {error}", file=sys.stderr)
        raise SystemExit(1) from error
