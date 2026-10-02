#!@python@/bin/python3
"""Launch a .qst with native state in an account-owned directory."""

import argparse
import fcntl
import hashlib
import os
from pathlib import Path
import stat
import sys
import tempfile

ENGINE = "@engine@/bin/zplayer"
RESOURCES = Path("@engine@/share/zquestclassic")


def prepare_resources(directory: Path) -> None:
    # Upstream looks up these files relative to cwd, alongside writable zc.cfg,
    # saves/, replays/ and logs. Link only immutable shipped resources, not state.
    for resource in RESOURCES.iterdir():
        target = directory / resource.name
        if target.is_symlink():
            previous = Path(os.readlink(target))
            if previous == resource:
                continue
            if not (
                str(previous).startswith("/nix/store/")
                and previous.parent.name == "zquestclassic"
                and previous.name == resource.name
            ):
                raise ValueError(f"Refusing to replace user resource: {target}")
        elif target.exists():
            raise ValueError(f"Refusing to replace user resource: {target}")
        # A changed package must not leave a half-updated resource link.
        with tempfile.TemporaryDirectory(prefix=".zquest-", dir=directory) as temp:
            link = Path(temp) / resource.name
            link.symlink_to(resource, target_is_directory=resource.is_dir())
            link.replace(target)


def launch(quest: Path, directory: Path) -> None:
    quest = quest.resolve(strict=True)
    if quest.suffix.lower() != ".qst":
        raise ValueError("ZQuest Classic requires an unpacked .qst file.")
    # Nonblocking open lets special-file inputs fail instead of hanging on a FIFO.
    descriptor = os.open(quest, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError("The quest must be a regular file.")
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    # User-approved identity: Core discovery/scanner.rs hashes the whole file.
    save_name = f"sha256:{digest}.sav"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory = directory.resolve(strict=True)
    lock = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError(
                "ZQuest Classic is already running for this account."
            ) from None
        prepare_resources(directory)
        os.chdir(directory)
        # The native binary normally switches cwd into its read-only package.
        os.environ["ZC_DISABLE_CHDIR"] = "1"
        # Allegro's native config selects software MIDI. Autodetection crashes
        # upstream when a device has no ALSA sequencer, such as the Mini V2.
        os.environ["ALLEGRO"] = "@audio@"
        os.set_inheritable(lock, True)
        os.execv(ENGINE, [ENGINE, "-standalone", str(quest), save_name])
    finally:
        os.close(lock)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "quest", type=Path, help="Unpacked quest; keep companion music beside it"
    )
    parser.add_argument("directory", type=Path, help="Account-owned ZQuest directory")
    args = parser.parse_args()
    try:
        launch(args.quest, args.directory)
    except (OSError, ValueError) as error:
        print(f"zquest-classic: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
