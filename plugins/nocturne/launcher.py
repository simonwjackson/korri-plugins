#!@python@/bin/python3
"""Launch the pinned Nocturne build without modifying the owner's game files."""

import argparse
import fcntl
import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile
import tomllib


XEX_SHA256 = "26a58b074c5dd6185b77a8111a0012866d11cba674b4b0810d79dbf07ad68aa6"
RESOURCES = Path("@out@/libexec/nocturnerecomp")
# The SDK applies these environment variables after command-line arguments.
# Keep host-wide overrides from changing this account's storage or update policy.
PRIVATE_ENVIRONMENT = {
    "REX_GAME_DATA_ROOT",
    "REX_USER_DATA_ROOT",
    "REX_MODS_DATA_ROOT",
    "REX_UPDATE_DATA_ROOT",
    "REX_CACHE_ROOT",
    "REX_METADATA_ROOT",
    "REX_LOG_FILE",
    "REX_AUTO_UPDATE_ENABLED",
}


def check_xex(path: Path) -> None:
    with path.open("rb") as source:
        if hashlib.file_digest(source, "sha256").hexdigest() != XEX_SHA256:
            raise ValueError(
                "Unsupported default.xex. Nocturne requires the supported XBLA release."
            )


def validate_settings(directory: Path) -> None:
    # These filenames and cvars come from ReXApp::SetupEnvironment and
    # NocturnerecompApp::user_settings_path. The SDK loads config after CLI.
    expected = {
        "game_data_root": directory / "assets",
        "user_data_root": directory,
        "mods_data_root": directory / "mods",
        "update_data_root": directory / "update",
    }

    def validate(values, prefix=""):
        for key, value in values.items():
            name = f"{prefix}_{key}" if prefix else key
            if isinstance(value, dict):
                validate(value, name)
            elif name in expected:
                if (
                    not isinstance(value, str)
                    or (directory / value).resolve() != expected[name]
                ):
                    raise ValueError(
                        f"Native setting {name} must point to {expected[name]}."
                    )
            elif name in ("cache_root", "log_file", "metadata_root") and value != "":
                root = (
                    directory
                    / {"cache_root": "cache", "log_file": "logs", "metadata_root": ""}[
                        name
                    ]
                )
                if not isinstance(value, str) or not (
                    directory / value
                ).resolve().is_relative_to(root):
                    raise ValueError(f"Native setting {name} must stay inside {root}.")
            elif name == "auto_update_enabled" and value is not False:
                raise ValueError(
                    "Native self-updates must stay disabled. Update the approved plugin instead."
                )

    for name in ("nocturnerecomp.toml", "settings.toml"):
        path = directory / name
        if path.exists():
            with path.open("rb") as source:
                validate(tomllib.load(source))


def launch(xex: Path, directory: Path) -> None:
    xex = xex.resolve(strict=True)
    if xex.name != "default.xex":
        raise ValueError(
            "Select default.xex beside the complete extracted game assets."
        )
    check_xex(xex)
    source = xex.parent
    for name in ("DATA", "MEDIA"):
        if not (source / name).is_dir():
            raise ValueError(
                f"Missing {name}. Keep all extracted assets beside default.xex."
            )
    # Never place runtime state within the source library, or copy state back
    # into itself. Resolve before mkdir so rejected input leaves nothing behind.
    directory = directory.resolve()
    if (
        directory == source
        or directory.is_relative_to(source)
        or source.is_relative_to(directory)
    ):
        raise ValueError(
            "Nocturne account storage must be separate from the game folder."
        )
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("Nocturne is already running for this account.") from None

        validate_settings(directory)
        assets = directory / "assets"
        if not assets.exists():
            # Upstream removes default.xexp for a vanilla build. Give it a
            # private copy, never symlinks into the owner's game directory.
            for path in source.rglob("*"):
                if path.is_symlink():
                    raise ValueError(
                        "Extracted game assets must not contain symbolic links."
                    )
            with tempfile.TemporaryDirectory(
                prefix=".nocturne-", dir=directory
            ) as temp:
                staged = Path(temp) / "assets"
                shutil.copytree(source, staged)
                check_xex(staged / "default.xex")
                staged.rename(assets)
        else:
            if assets.is_symlink():
                raise ValueError(
                    "Nocturne's private assets must not be a symbolic link."
                )
            check_xex(assets / "default.xex")

        # ReXGlue resolves its writable config and logs beside /proc/self/exe.
        # Refresh only the executable from the approved immutable package.
        # Keep all native config, saves, mods and extracted assets untouched.
        with tempfile.TemporaryDirectory(prefix=".nocturne-", dir=directory) as temp:
            staged = Path(temp) / "nocturnerecomp"
            shutil.copyfile(RESOURCES / "nocturnerecomp", staged)
            staged.chmod(0o700)
            staged.replace(directory / "nocturnerecomp")
        for name in (
            "librexruntime.so",
            "librexgpu-xenos.so",
            "libTracyClient.so",
            "shaders",
        ):
            destination = directory / name
            target = RESOURCES / name
            if destination.is_symlink():
                if destination.readlink() == target:
                    continue
                destination.unlink()
            elif destination.exists():
                raise ValueError(
                    f"Refusing to replace unmanaged runtime file: {destination}"
                )
            destination.symlink_to(target)

        os.chdir(directory)
        os.set_inheritable(lock, True)
        env = {
            key: value
            for key, value in os.environ.items()
            if key not in PRIVATE_ENVIRONMENT
        }
        env["LD_LIBRARY_PATH"] = "@runtimeLibraries@:/run/opengl-driver/lib"
        engine = str(directory / "nocturnerecomp")
        # The SDK loads config after CLI and seeds game-specific defaults.
        # validate_settings prevents saved config redirecting the private roots
        # or re-enabling self-update at boot. Relative native defaults resolve
        # inside this account directory, not the owner's library.
        os.execve(
            engine,
            [
                engine,
                f"--game_data_root={assets}",
                f"--user_data_root={directory}",
                f"--mods_data_root={directory / 'mods'}",
                f"--update_data_root={directory / 'update'}",
                "--auto_update_enabled=false",
            ],
            env,
        )
    finally:
        os.close(lock)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "xex", type=Path, help="default.xex beside complete extracted XBLA assets"
    )
    parser.add_argument("directory", type=Path, help="Account-owned Nocturne directory")
    args = parser.parse_args()
    try:
        launch(args.xex, args.directory)
    except (OSError, ValueError) as error:
        print(f"nocturne: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
