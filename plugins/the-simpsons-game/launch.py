#!@python@ -I
"""Install an owned disc into the host-selected account cwd, then run the engine."""

import fcntl
import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

ENGINE = "@engine@"
EXTRACTOR = "@extractor@"
DISC_SHA256 = "@discHash@"
CONFIG = "@config@"


def validate_install(directory: Path) -> None:
    # These are upstream launcher/launcher.py's installation requirements.
    executable = directory / "default.xex"
    movies = directory / "movies"
    if directory.is_symlink() or executable.is_symlink() or movies.is_symlink():
        raise ValueError("Installed game data must not redirect into another account")
    if not executable.is_file() or not movies.is_dir():
        raise ValueError(
            f"Incomplete game data at {directory}: need default.xex and movies/. "
            "Move the incomplete directory aside before installing again."
        )
    with executable.open("rb") as source:
        if source.read(4) != b"XEX2":
            raise ValueError("Installed default.xex is not an Xbox 360 executable")


def install(source, directory: Path, extractor: str) -> None:
    if directory.exists() or directory.is_symlink():
        validate_install(directory)
        return
    # No persistent marker or cache schema: publish only a complete native tree.
    with tempfile.TemporaryDirectory(
        prefix=".simpsons-extract-", dir=directory.parent
    ) as temporary:
        staging = Path(temporary) / "gamedata"
        subprocess.run(
            [extractor, "-x", "-d", str(staging), f"/proc/self/fd/{source.fileno()}"],
            pass_fds=(source.fileno(),),
            check=True,
        )
        validate_install(staging)
        staging.rename(directory)


def launch(
    content: Path,
    *,
    engine: str = ENGINE,
    extractor: str = EXTRACTOR,
    disc_sha256: str = DISC_SHA256,
) -> None:
    # Lock the account directory itself; no extra lock-file format is needed.
    lock = os.open(".", os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise ValueError(
            "The Simpsons Game is already running for this account"
        ) from None

    directory = Path.cwd()
    descriptor = os.open(content, os.O_RDONLY | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError("The Simpsons Game needs a regular ISO file")
        # Verify the exact disc before running the native extractor. The digest
        # is derived from plugin.ts at package time, not maintained twice.
        if hashlib.file_digest(source, "sha256").hexdigest() != disc_sha256:
            raise ValueError("Unsupported disc: expected the verified USA Xbox 360 ISO")
        install(source, directory / "gamedata", extractor)

    # Install upstream's release defaults once. Never overwrite saved settings.
    with tempfile.TemporaryDirectory(
        prefix=".simpsons-config-", dir=directory
    ) as temporary:
        configuration = Path(temporary) / "simpsons.toml"
        configuration.write_bytes(Path(CONFIG).read_bytes())
        try:
            os.link(configuration, directory / "simpsons.toml")
        except FileExistsError:
            pass

    os.set_inheritable(lock, True)
    environment = os.environ.copy()
    # ReXGlue applies environment overrides after CLI arguments. Do not inherit
    # another account's paths from the caller's process environment.
    for key in (
        "REX_GAME_DATA_ROOT",
        "REX_USER_DATA_ROOT",
        "REX_UPDATE_DATA_ROOT",
        "REX_CACHE_PATH",
        "REX_LOG_FILE",
    ):
        environment.pop(key, None)
    # Upstream's launcher disables this layer because it can hang its renderer.
    environment["DISABLE_LSFG"] = "1"
    os.execve(
        engine,
        [
            engine,
            "--game_data_root",
            str(directory / "gamedata"),
            "--user_data_root",
            str(directory),
        ],
        environment,
    )


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: simpsons ISO_PATH (run from the account's Simpsons directory)",
            file=sys.stderr,
        )
        return 2
    try:
        launch(Path(sys.argv[1]))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"The Simpsons Game launch failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
