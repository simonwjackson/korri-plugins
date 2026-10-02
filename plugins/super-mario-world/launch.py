#!@python@ -I
"""Prepare owned ROM assets in the host-selected cwd, then replace this process."""

import fcntl
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def launch(content: Path) -> None:
    # Lock the existing directory, without adding a persistent lock-file format.
    # Keep the lock across exec so two instances cannot overwrite the same saves.
    lock = os.open(".", os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise ValueError("SMW is already running for this account") from None

    with content.open("rb") as source:
        rom = source.read(524801)
    if len(rom) == 524800:
        # Upstream's header test misses this measured 512 KiB ROM + copier header.
        rom = rom[512:]
    if len(rom) != 524288:
        raise ValueError(
            "SMW requires the 512 KiB USA ROM, with an optional 512-byte header"
        )

    # Always regenerate with the pinned extractor. This avoids cache-version
    # metadata and stale assets after an engine update. It does not compile code.
    with tempfile.TemporaryDirectory(prefix=".smw-extract-", dir=".") as temporary:
        work = Path(temporary).resolve()
        (work / "smw.sfc").write_bytes(rom)
        subprocess.run(
            [
                sys.executable,
                "-E",
                "-s",
                "-B",
                "@resources@/assets/restool.py",
                "--rom",
                str(work / "smw.sfc"),
                "--no-include-rom",
            ],
            cwd=work,
            check=True,
        )
        # The extractor verifies upstream's USA SHA-1 before any output is kept.
        # Do not overwrite a user's config, even when another writer creates it.
        config = work / "smw.ini"
        config.write_bytes(Path("@resources@/smw.ini").read_bytes())
        try:
            os.link(config, "smw.ini")
        except FileExistsError:
            pass
        os.replace(work / "smw_assets.dat", "smw_assets.dat")

    os.set_inheritable(lock, True)
    os.execv("@engine@", ["@engine@", "--config", str(Path("smw.ini").resolve())])


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: smw ROM_PATH (run from the account's SMW directory)",
            file=sys.stderr,
        )
        return 2
    try:
        launch(Path(sys.argv[1]))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"SMW launch failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
