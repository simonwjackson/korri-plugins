#!@python@ -I
"""Validate the owned ROM and launch with upstream's account-owned native state."""

import fcntl
import hashlib
import os
from pathlib import Path
import sys
import tempfile


ROM_HASH = "bb2c0dec0a8287ad256929563d0509801c2f239df883c1cf52cab05b23bd77b6"
SWAPPED_HASH = "613778b244784492a881c0d72d6017f82c39026706a406bd7ef95c6f33e53b89"
ROM_SIZE = 4 * 1024 * 1024


def read_rom(path: Path) -> bytes:
    with path.open("rb") as source:
        data = source.read(ROM_SIZE + 1)
    if len(data) != ROM_SIZE:
        raise ValueError("Supply the bare 4 MiB Dr. Mario 64 US ROM, not a ZIP")
    digest = hashlib.sha256(data).hexdigest()
    if digest == SWAPPED_HASH:
        canonical = bytearray(len(data))
        canonical[0::2], canonical[1::2] = data[1::2], data[0::2]
        return bytes(canonical)
    if digest != ROM_HASH:
        raise ValueError("ROM does not match the supported Dr. Mario 64 US release")
    return data


def link_resource(name: str) -> None:
    target = Path("@bundle@") / name
    path = Path(name)
    if not target.exists():
        raise ValueError(f"The native package is missing {name}")
    if path.is_symlink():
        previous = Path(os.readlink(path))
        # Only replace links installed by an earlier version of this package.
        # Preserve unrelated links and real user files, even when they obstruct launch.
        if previous == target:
            return
        if not (
            previous.is_absolute()
            and str(previous).startswith("/nix/store/")
            and previous.parts[-3:] == ("share", "drmario64", name)
        ):
            raise ValueError(f"Refusing to replace unrelated resource link: {name}")
    elif path.exists():
        raise ValueError(f"Refusing to replace existing resource: {name}")
    with tempfile.TemporaryDirectory(prefix=".drmario64-resource-", dir=".") as work:
        link = Path(work) / name
        link.symlink_to(target, target_is_directory=target.is_dir())
        os.replace(link, path)


def launch(content: Path) -> None:
    # Validate before changing ROM imports, resource links, settings or saves.
    canonical = read_rom(content)
    lock = os.open(".", os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise ValueError("Dr. Mario 64 is already running for this account") from None

    # GameEntry::stored_filename() is game_id + '.z64'. Keep the original immutable.
    stored = Path("drmario64.us.z64")
    if stored.is_symlink() or (stored.exists() and not stored.is_file()):
        raise ValueError("Refusing to replace a non-regular native ROM import")
    existing = None
    if stored.exists():
        with stored.open("rb") as source:
            existing = source.read(ROM_SIZE + 1)
    if existing != canonical:
        if stored.resolve() == content.resolve():
            raise ValueError("Keep the original ROM outside the native import path")
        with tempfile.TemporaryDirectory(prefix=".drmario64-import-", dir=".") as work:
            staged = Path(work) / stored.name
            staged.write_bytes(canonical)
            staged.chmod(0o600)
            os.replace(staged, stored)

    for name in ("assets", "icons"):
        link_resource(name)
    # APP_FOLDER_PATH and portable.txt now resolve to the same host-selected cwd.
    # Do not inherit a path that could mix settings/saves between Korri accounts.
    os.environ["APP_FOLDER_PATH"] = str(Path.cwd())
    os.environ["SDL_VULKAN_LIBRARY"] = "@vulkan@"
    os.set_inheritable(lock, True)
    os.execv("@engine@", ["@engine@", "--start"])


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: drmario64 ROM_PATH (run from the account's drmario64.us directory)",
            file=sys.stderr,
        )
        return 2
    try:
        launch(Path(sys.argv[1]))
    except (OSError, ValueError) as error:
        print(f"Dr. Mario 64 launch failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
