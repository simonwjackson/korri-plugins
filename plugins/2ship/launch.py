#!@python@ -I
"""Validate the owned ROM, prepare upstream assets, and start the native game."""

import fcntl
import hashlib
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import zipfile
import zlib


def read_rom(content: Path) -> bytes:
    with content.open("rb") as source:
        rom = source.read(32 * 1024 * 1024 + 1)
    if len(rom) != 32 * 1024 * 1024:
        raise ValueError("2 Ship requires the bare 32 MiB NTSC-U 1.0 ROM, not a ZIP")
    if rom[:4] == bytes.fromhex("37804012"):
        normalized = bytearray(rom)
        normalized[0::2], normalized[1::2] = rom[1::2], rom[0::2]
        rom = bytes(normalized)
    # This is upstream 3.0.1's supportedHashes.json identity, not a filename test.
    if hashlib.sha1(rom).hexdigest() != "d6133ace5afaa0882cf214cf88daba39e266c078":
        raise ValueError(
            "ROM does not match the supported Majora's Mask NTSC-U 1.0 release"
        )
    return rom


def current_archive(path: Path) -> bool:
    # These records are written by OTRExporter/Main.cpp, not a Korri cache schema.
    version = b"\x01" + struct.pack(">HHH", *map(int, "@version@".split(".")))
    try:
        with zipfile.ZipFile(path) as archive:
            return (
                archive.getinfo("portVersion").file_size == len(version)
                and archive.getinfo("version").file_size == 5
                and archive.read("portVersion") == version
                and archive.read("version") == bytes.fromhex("015354631c")
                # Mandatory title, player and message resources from N64_US XMLs.
                # Version records alone do not make a playable game archive.
                and all(
                    archive.getinfo(resource).file_size > 0
                    for resource in (
                        "objects/object_mag/gTitleScreenZeldaLogoTex",
                        "objects/object_link_child/gLinkHumanSkel",
                        "text/message_data_static/message_data_static",
                    )
                )
                and archive.testzip() is None
            )
    except (
        OSError,
        ValueError,
        KeyError,
        RuntimeError,
        NotImplementedError,
        zipfile.BadZipFile,
        zlib.error,
    ):
        return False


def launch(content: Path) -> None:
    # Validate before touching even an existing archive, config, or save.
    rom = read_rom(content)
    lock = os.open(".", os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise ValueError("2 Ship is already running for this account") from None

    archive = Path("mm.o2r")
    if not current_archive(archive):
        with tempfile.TemporaryDirectory(
            prefix=".2ship-extract-", dir="."
        ) as temporary:
            work = Path(temporary).resolve()
            rom_path = work / "rom.z64"
            rom_path.write_bytes(rom)
            (work / "assets").symlink_to("@bundle@/assets", target_is_directory=True)
            # Extract::CallZapd's native invocation, without its interactive dialogs.
            subprocess.run(
                [
                    "@bundle@/assets/extractor/ZAPD.out",
                    "ed",
                    "-i",
                    "assets/xml/N64_US",
                    "-b",
                    str(rom_path),
                    "-fl",
                    "assets/filelists",
                    "-gsf",
                    "0",
                    "-rconf",
                    "assets/Config_N64_US.xml",
                    "-se",
                    "OTR",
                    "--otrfile",
                    "mm.o2r",
                    "--portVer",
                    "@version@",
                    "-o",
                    "placeholder",
                    "-osf",
                    "placeholder",
                ],
                cwd=work,
                check=True,
            )
            if not current_archive(work / "mm.o2r"):
                raise ValueError(
                    "Upstream extraction did not produce a valid current mm.o2r"
                )
            os.replace(work / "mm.o2r", archive)

    # Never rewrite upstream config or saves. Ignore inherited SHIP_HOME so the
    # native process uses the same host-selected directory as its archive/lock.
    os.environ["SHIP_HOME"] = str(Path.cwd())
    os.set_inheritable(lock, True)
    os.execv("@engine@", ["@engine@"])


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: 2ship ROM_PATH (run from the account's 2ship directory)",
            file=sys.stderr,
        )
        return 2
    try:
        launch(Path(sys.argv[1]))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"2 Ship launch failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
