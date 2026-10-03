#!@python@ -I
"""Validate the owned Europe ROM, lock account state, and execute the native game."""

import fcntl
import hashlib
import os
from pathlib import Path
import sys


def launch(content: Path) -> None:
    content = content.resolve(strict=True)
    with content.open("rb") as source:
        rom = source.read(65553)
    if len(rom) != 65552 or hashlib.sha256(rom).hexdigest() != (
        "83914c08f82fc70779121760a48392af3a5988f015794eb53cbe1aa0a165c821"
    ):
        raise ValueError("Dr. Mario requires the supported Europe iNES ROM")

    # Lock the directory without adding a persistent lock-file format. The
    # inherited descriptor keeps the lock across exec and releases it on exit.
    lock = os.open(".", os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise ValueError("Dr. Mario is already running for this account") from None
    # Upstream diagnostics can write to arbitrary inherited paths even with
    # its TCP trace server compiled out. Native config files own user settings;
    # developer environment overrides require an explicit raw-engine invocation.
    for key in list(os.environ):
        if key.startswith(("NESRECOMP_", "RECOMP_AUDIO_", "LNG_", "NES_NET")):
            os.environ.pop(key)
    os.set_inheritable(lock, True)
    os.execv("@engine@", ["@engine@", str(content)])


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: dr-mario ROM_PATH (run from the account directory)", file=sys.stderr
        )
        return 2
    try:
        launch(Path(sys.argv[1]))
    except (OSError, ValueError) as error:
        print(f"Dr. Mario launch failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
