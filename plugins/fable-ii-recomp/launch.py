#!@python@ -I
"""Extract a verified owned ISO into Oery's native layout and launch Fable II."""

import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

ENGINE = "@engine@"
EXTRACTOR = "@extractor@"
DISC_SHA256 = "@discHash@"
XEX_SHA256 = "@xexHash@"
GAME_FILES = "@gameFiles@"
# Measured whole-file size of the ISO admitted by plugin.ts.
DISC_BYTES = 7_838_695_424


def require_directory(path: Path, *, create: bool = False) -> None:
    if path.is_symlink():
        raise ValueError(f"Native directories must not be symlinks: {path}")
    if create:
        path.mkdir(mode=0o700, exist_ok=True)
    if not path.is_dir():
        raise ValueError(f"Expected a native directory: {path}")


def validate_install(directory: Path, files: dict[str, int], xex_sha256: str) -> None:
    # This filename/size map is the existing Oery docs/re/game-files.json format.
    require_directory(directory)
    actual = {}
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Game data must not contain symlinks: {path}")
        mode = path.stat().st_mode
        if stat.S_ISREG(mode):
            actual[str(path.relative_to(directory))] = path.stat().st_size
        elif not stat.S_ISDIR(mode):
            raise ValueError(f"Game data contains a special file: {path}")
    if actual != files:
        raise ValueError(
            f"Incomplete or changed game data at {directory}. "
            "Move that directory aside before installing again; saves will not be deleted."
        )
    with (directory / "default.xex").open("rb") as executable:
        if hashlib.file_digest(executable, "sha256").hexdigest() != xex_sha256:
            raise ValueError(
                "Installed default.xex does not match the compiled GOTY version"
            )


def verify_disc(source, digest: str, size: int, snapshot=None) -> None:
    before = os.fstat(source.fileno())
    if not stat.S_ISREG(before.st_mode) or before.st_size != size:
        raise ValueError("Expected the verified USA/Europe GOTY ISO as a regular file")
    source.seek(0)
    computed = hashlib.sha256()
    remaining = size
    while remaining:
        block = source.read(min(1024 * 1024, remaining))
        if not block:
            raise ValueError("ISO changed or ended while being read")
        computed.update(block)
        if snapshot is not None:
            snapshot.write(block)
        remaining -= len(block)
    after = os.fstat(source.fileno())
    if source.read(1) or (before.st_size, before.st_mtime_ns) != (
        after.st_size,
        after.st_mtime_ns,
    ):
        raise ValueError("ISO changed while being read")
    if computed.hexdigest() != digest:
        raise ValueError("Unsupported ISO: expected the verified USA/Europe GOTY disc")


def install(
    source,
    directory: Path,
    extractor: str,
    *,
    disc_sha256: str,
    disc_bytes: int,
    xex_sha256: str,
    files: dict[str, int],
) -> None:
    if directory.parent.exists() or directory.parent.is_symlink():
        require_directory(directory.parent)
    if directory.exists() or directory.is_symlink():
        verify_disc(source, disc_sha256, disc_bytes)
        validate_install(directory, files, xex_sha256)
        return
    # A private verified snapshot prevents an in-place ISO edit after hashing
    # from changing the bytes supplied to the native extractor. No marker schema.
    with tempfile.TemporaryDirectory(
        prefix=".fable-ii-extract-", dir=Path.cwd()
    ) as temporary:
        temporary = Path(temporary)
        snapshot = temporary / "disc.iso"
        with snapshot.open("xb") as output:
            verify_disc(source, disc_sha256, disc_bytes, output)
        staging = temporary / "00007000"
        subprocess.run(
            [extractor, "-q", "-x", str(snapshot), "-d", str(staging)],
            check=True,
        )
        validate_install(staging, files, xex_sha256)
        require_directory(directory.parent, create=True)
        if directory.exists() or directory.is_symlink():
            raise ValueError(
                "Game installation appeared during extraction; refusing replacement"
            )
        staging.rename(directory)


def reject_linked_account_data(directory: Path) -> None:
    def failed_scan(error: OSError) -> None:
        raise error

    # The SDK owns title/XUID save and achievement paths below user_data_root.
    # Inspect the existing tree rather than maintaining a second path schema.
    for parent, directories, files in os.walk(
        directory, followlinks=False, onerror=failed_scan
    ):
        for name in directories + files:
            path = Path(parent) / name
            if path.is_symlink():
                raise ValueError(f"Account data must not contain symlinks: {path}")


def launch(
    content: Path,
    *,
    engine: str = ENGINE,
    extractor: str = EXTRACTOR,
    disc_sha256: str = DISC_SHA256,
    disc_bytes: int = DISC_BYTES,
    xex_sha256: str = XEX_SHA256,
    game_files: str = GAME_FILES,
) -> None:
    # Core selects/creates this account cwd. Lock the directory, not a new file.
    lock = os.open(".", os.O_RDONLY | os.O_DIRECTORY)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Fable II is already running for this account") from None
        directory = Path.cwd()
        reject_linked_account_data(directory)
        configuration = directory / "fable_ii.toml"
        if configuration.is_symlink() or (
            configuration.exists() and not configuration.is_file()
        ):
            raise ValueError(
                "Native fable_ii.toml must be a regular account-owned file"
            )
        for name in ("assets-extracted", "cache", "logs", "runtime"):
            path = directory / name
            if path.exists() or path.is_symlink():
                require_directory(path)
        with Path(game_files).open() as manifest:
            files = json.load(manifest)
        descriptor = os.open(content, os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(descriptor, "rb") as source:
            install(
                source,
                directory / "assets-extracted/00007000",
                extractor,
                disc_sha256=disc_sha256,
                disc_bytes=disc_bytes,
                xex_sha256=xex_sha256,
                files=files,
            )
        # Oery scripts/run explicitly uses this empty update directory.
        require_directory(directory / "runtime", create=True)
        update = directory / "runtime/update-empty"
        require_directory(update, create=True)
        if any(update.iterdir()):
            raise ValueError(
                "The native runtime/update-empty directory must stay empty"
            )
        environment = os.environ.copy()
        for key in (
            "REX_GAME_DATA_ROOT",
            "REX_USER_DATA_ROOT",
            "REX_UPDATE_DATA_ROOT",
            "REX_CACHE_ROOT",
            "REX_METADATA_ROOT",
            "REX_LOG_FILE",
        ):
            environment.pop(key, None)
        os.set_inheritable(lock, True)
        os.execve(
            engine,
            [
                engine,
                "--game_data_root",
                str(directory / "assets-extracted/00007000"),
                "--user_data_root",
                str(directory),
                "--update_data_root",
                str(update),
                "--cache_root",
                str(directory / "cache"),
            ],
            environment,
        )
    finally:
        os.close(lock)


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: fable_ii ISO_PATH (run from the selected account's Fable II directory)",
            file=sys.stderr,
        )
        return 2
    try:
        launch(Path(sys.argv[1]))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Fable II launch failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
