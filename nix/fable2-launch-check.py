#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Check the actual packaged launcher with a real extractor and non-retail XISO."""

from contextlib import contextmanager
import ctypes
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import select
import struct
import subprocess
import sys
import tempfile

package = Path(sys.argv[1])
handoff = sys.argv[2]
manifest = json.loads((package / "manifest.json").read_text())
launcher = Path(manifest["files"]["fable_ii"])
module = runpy.run_path(str(launcher), run_name="fable2_launch_check")
extractor = module["EXTRACTOR"]
install = module["install"]
assert (
    module["DISC_SHA256"]
    == "2cdaafead95680e2c6fe8886a89f1ae3d5e41549857c7fc125a12aab1cb99ad9"
)
assert module["DISC_BYTES"] == 7_838_695_424
assert (
    module["XEX_SHA256"]
    == "88c4ef2e18e65409444d1b068eff921d1f7e180a5ae64edc64ba6b0872372662"
)
owned_files = json.loads(Path(module["GAME_FILES"]).read_text())
assert len(owned_files) == 451
assert owned_files["default.xex"] == 21_217_280
assert sum(owned_files.values()) == 6_997_047_778

# Inspect the real engine output and extractor, not their platform metadata.
expected_machine = {"x86_64": 62, "aarch64": 183}[platform.machine()]
engine_root = Path(module["ENGINE"]).parent.parent
native_executables = 0
for path in [*engine_root.rglob("*"), Path(extractor)]:
    if not path.is_file():
        continue
    with path.open("rb") as binary:
        header = binary.read(64)
        if not header.startswith(b"\x7fELF"):
            continue
        assert header[:6] == b"\x7fELF\x02\x01", path
        assert struct.unpack_from("<H", header, 18)[0] == expected_machine, path
        kind = struct.unpack_from("<H", header, 16)[0]
        phoff = struct.unpack_from("<Q", header, 32)[0]
        phsize, phnum = struct.unpack_from("<HH", header, 54)
        executable = kind == 2
        for index in range(phnum):
            binary.seek(phoff + index * phsize)
            executable |= struct.unpack("<I", binary.read(4))[0] == 3  # PT_INTERP
        if path != Path(extractor) and executable:
            native_executables += 1
assert native_executables >= 1, "Engine output has no native executable"

# SDL can silently omit a requested backend when a build dependency is absent.
# Query the installed runtime itself, without starting video or opening a display.
runtime_paths = list(engine_root.rglob("librexruntimerd.so"))
assert len(runtime_paths) == 1, runtime_paths
runtime = ctypes.CDLL(str(runtime_paths[0]))
runtime.SDL_GetNumVideoDrivers.argtypes = []
runtime.SDL_GetNumVideoDrivers.restype = ctypes.c_int
runtime.SDL_GetVideoDriver.argtypes = [ctypes.c_int]
runtime.SDL_GetVideoDriver.restype = ctypes.c_char_p
drivers = [
    runtime.SDL_GetVideoDriver(index).decode()
    for index in range(runtime.SDL_GetNumVideoDrivers())
]
assert "wayland" in drivers, f"Packaged SDL lacks Wayland: {drivers}"


@contextmanager
def cwd(path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def fails(action, message):
    try:
        action()
    except (OSError, ValueError, subprocess.CalledProcessError):
        return
    raise AssertionError(message)


with tempfile.TemporaryDirectory(prefix="fable2-launch-check-") as temporary:
    root = Path(temporary)
    account = root / "account '; $(exit 19) #"
    account.mkdir()
    configuration = account / "fable_ii.toml"
    configuration.write_text("# existing settings\n")
    save = account / "existing-save.bin"
    save.write_bytes(b"existing progress")
    wrong = root / "wrong '; $(exit 19) #.iso"
    wrong.write_bytes(b"not the owned disc")
    wrong.chmod(0o444)
    fifo = root / "pipe.iso"
    os.mkfifo(fifo)
    for content in (wrong, root / "missing.iso", fifo, root):
        result = subprocess.run(
            [launcher, content], cwd=account, capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 1, result
        assert "Fable II launch failed:" in result.stderr, result.stderr
        assert configuration.read_text() == "# existing settings\n"
        assert save.read_bytes() == b"existing progress"
        assert not (account / "assets-extracted").exists()
        assert not list(account.glob(".fable-ii-extract-*"))
    assert wrong.read_bytes() == b"not the owned disc"

    # SDK saves and achievements also live beneath title/XUID directories.
    other = root / "other-account"
    other_save = other / "4D5307F1/00000001/Hero000/mainsave.bin"
    other_save.parent.mkdir(parents=True)
    other_save.write_bytes(b"other account progress")
    linked = account / "B13EBABEBABEBABE"
    linked.symlink_to(other, target_is_directory=True)
    for depth in ("root", "nested"):
        if depth == "nested":
            linked = account / "B13EBABEBABEBABE/4D5307F1/00000001/Hero000"
            linked.parent.mkdir(parents=True)
            linked.symlink_to(other_save.parent, target_is_directory=True)
        rejected = subprocess.run(
            [launcher, wrong], cwd=account, capture_output=True, text=True, timeout=10
        )
        assert rejected.returncode == 1
        assert "symlink" in rejected.stderr, rejected.stderr
        assert other_save.read_bytes() == b"other account progress"
        linked.unlink()

    lock = os.open(account, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = subprocess.run(
            [launcher, wrong], cwd=account, capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 1
        assert "already running for this account" in result.stderr
    finally:
        os.close(lock)

    # Actual extractor creates and later reads a tiny XISO; no retail code.
    fixture = root / "fixture"
    (fixture / "data").mkdir(parents=True)
    fixture_xex = b"XEX2fixture"
    (fixture / "default.xex").write_bytes(fixture_xex)
    (fixture / "data/gold_version.txt").write_bytes(b"fixture edition")
    (fixture / "data/startup.vfsconfig").write_bytes(b"fixture content")
    files = {
        "default.xex": len(fixture_xex),
        "data/gold_version.txt": len(b"fixture edition"),
        "data/startup.vfsconfig": len(b"fixture content"),
    }
    fixture_manifest = root / "game-files.json"
    fixture_manifest.write_text(json.dumps(files))
    iso = root / "fixture '; $(exit 19).iso"
    subprocess.run([extractor, "-c", fixture, iso], check=True, capture_output=True)
    before = hashlib.sha256(iso.read_bytes()).hexdigest()
    parameters = {
        "disc_sha256": before,
        "disc_bytes": iso.stat().st_size,
        "xex_sha256": hashlib.sha256(fixture_xex).hexdigest(),
        "files": files,
    }
    destination = account / "assets-extracted/00007000"
    with cwd(account), iso.open("rb") as source:
        source.read()  # A reused descriptor at EOF must be rewound.
        install(source, destination, extractor, **parameters)
    assert (destination / "default.xex").read_bytes() == fixture_xex
    assert (destination / "data/startup.vfsconfig").read_bytes() == b"fixture content"
    assert hashlib.sha256(iso.read_bytes()).hexdigest() == before
    assert not list(account.glob(".fable-ii-extract-*"))
    inode = (destination / "default.xex").stat().st_ino
    with cwd(account), iso.open("rb") as source:
        install(source, destination, extractor, **parameters)
    assert (destination / "default.xex").stat().st_ino == inode

    # A real child changes the original after hashing, before native extraction.
    # Extraction must still receive the verified private snapshot.
    moving_iso = root / "changing-during-extraction.iso"
    moving_iso.write_bytes(iso.read_bytes())
    changing_account = root / "changing-account"
    changing_account.mkdir()
    snapshot_keys = ("FABLE2_SNAPSHOT_SOURCE", "FABLE2_REAL_EXTRACTOR")
    previous_environment = {key: os.environ.get(key) for key in snapshot_keys}
    try:
        os.environ.update(
            FABLE2_SNAPSHOT_SOURCE=str(moving_iso), FABLE2_REAL_EXTRACTOR=extractor
        )
        with cwd(changing_account), moving_iso.open("rb") as source:
            install(
                source,
                changing_account / "assets-extracted/00007000",
                handoff,
                **parameters,
            )
    finally:
        for key, value in previous_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    assert hashlib.sha256(moving_iso.read_bytes()).hexdigest() != before
    assert (
        changing_account / "assets-extracted/00007000/default.xex"
    ).read_bytes() == fixture_xex
    assert not list(changing_account.glob(".fable-ii-extract-*"))

    changed = root / "changed.iso"
    data = bytearray(iso.read_bytes())
    data[0] ^= 1
    changed.write_bytes(data)
    with cwd(account), changed.open("rb") as source:
        fails(
            lambda: install(source, destination, extractor, **parameters),
            "Same-size altered ISO accepted",
        )
    assert (destination / "default.xex").stat().st_ino == inode

    # Real exec handoff and lock lifetime, using a recording child, not game emulation.
    path_keys = (
        "REX_GAME_DATA_ROOT",
        "REX_USER_DATA_ROOT",
        "REX_UPDATE_DATA_ROOT",
        "REX_CACHE_ROOT",
        "REX_METADATA_ROOT",
        "REX_LOG_FILE",
    )
    inherited = dict(os.environ, REX_VSYNC="false")
    inherited.update({key: "/another-account" for key in path_keys})
    for selected in (account, root / "second-account"):
        selected.mkdir(exist_ok=True)
        child = subprocess.Popen(
            [
                handoff,
                "--fixture",
                launcher,
                iso,
                handoff,
                fixture_manifest,
                parameters["xex_sha256"],
            ],
            cwd=selected,
            env=inherited,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        try:
            ready, _, _ = select.select([child.stdout], [], [], 15)
            assert ready, "No receipt from exec child"
            line = child.stdout.readline()
            assert line, child.stderr.read()
            receipt = json.loads(line)
            assert receipt["args"] == [
                "--game_data_root",
                str(selected / "assets-extracted/00007000"),
                "--user_data_root",
                str(selected),
                "--update_data_root",
                str(selected / "runtime/update-empty"),
                "--cache_root",
                str(selected / "cache"),
            ]
            assert receipt["cwd"] == str(selected)
            assert receipt["env"]["REX_VSYNC"] == "false"
            assert all(receipt["env"][key] is None for key in path_keys)
            assert not any((selected / "runtime/update-empty").iterdir())
            result = subprocess.run(
                [launcher, wrong],
                cwd=selected,
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert result.returncode == 1
            assert "already running for this account" in result.stderr
            child.communicate(b"x", timeout=10)
            assert child.returncode == 0
            descriptor = os.open(selected, os.O_RDONLY | os.O_DIRECTORY)
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            finally:
                os.close(descriptor)
        finally:
            if child.poll() is None:
                child.kill()
                child.communicate()
    assert configuration.read_text() == "# existing settings\n"
    assert save.read_bytes() == b"existing progress"

    # Refuse damaged published trees. Never erase or silently replace user data.
    (destination / "default.xex").write_bytes(b"YEX2fixture")
    with cwd(account), iso.open("rb") as source:
        fails(
            lambda: install(source, destination, extractor, **parameters),
            "Changed XEX accepted",
        )
    assert (destination / "default.xex").read_bytes() == b"YEX2fixture"
    (destination / "default.xex").unlink()
    with cwd(account), iso.open("rb") as source:
        fails(
            lambda: install(source, destination, extractor, **parameters),
            "Incomplete tree accepted",
        )
    assert (destination / "data/startup.vfsconfig").exists()

    fresh = root / "fresh-account"
    fresh.mkdir()
    # A trusted test composition with non-XISO bytes reaches the actual extractor failure.
    with cwd(fresh), wrong.open("rb") as source:
        corrupt = dict(
            parameters,
            disc_bytes=wrong.stat().st_size,
            disc_sha256=hashlib.sha256(wrong.read_bytes()).hexdigest(),
        )
        fails(
            lambda: install(
                source, fresh / "assets-extracted/00007000", extractor, **corrupt
            ),
            "Corrupt XISO accepted",
        )
    assert not list(fresh.iterdir()), "Failed extraction published account state"
    (fresh / "assets-extracted").symlink_to(
        account / "assets-extracted", target_is_directory=True
    )
    with cwd(fresh), iso.open("rb") as source:
        fails(
            lambda: install(
                source, fresh / "assets-extracted/00007000", extractor, **parameters
            ),
            "Cross-account symlink accepted",
        )

print(
    "Fable II packaged launcher: identity, native ELF, real extraction, rejection, exec/lock lifetime and preservation passed"
)
