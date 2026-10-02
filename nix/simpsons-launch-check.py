#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3
"""Exercise the packaged launcher and actual Xbox ISO extractor without retail data."""

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
manifest = json.loads((package / "manifest.json").read_text())
launcher = Path(manifest["files"]["simpsons"])
module = runpy.run_path(str(launcher), run_name="simpsons_launch_check")
extractor = module["EXTRACTOR"]
install = module["install"]
handoff = sys.argv[2]
# Check payload architecture, not only metadata or a wrapper that could invoke
# a foreign executable through the host's binfmt emulation.
expected_machine = {"x86_64": 62, "aarch64": 183}[platform.machine()]
for binary in (Path(module["ENGINE"]).with_name(".simpsons-wrapped"), Path(extractor)):
    with binary.open("rb") as source:
        header = source.read(20)
    assert header[:6] == b"\x7fELF\x02\x01", binary
    assert struct.unpack_from("<H", header, 18)[0] == expected_machine, binary
assert (
    module["DISC_SHA256"]
    == "fd794e7a3025c3fd1340d25301658bac8c829a65d5e5e47d2663b431f869531b"
)

with tempfile.TemporaryDirectory(prefix="simpsons-launch-check-") as temporary:
    root = Path(temporary)
    account = root / "account '; $(exit 19) #"
    account.mkdir()
    config = account / "simpsons.toml"
    config.write_text("# existing settings\n")
    saves = account / "content"
    saves.mkdir()
    (saves / "save.bin").write_bytes(b"existing progress")
    wrong = root / "wrong '; $(exit 19) #.iso"
    wrong.write_bytes(b"not the owned disc")
    wrong.chmod(0o444)
    fifo = root / "pipe.iso"
    os.mkfifo(fifo)
    for content in (wrong, root / "missing.iso", fifo, root):
        rejected = subprocess.run(
            [launcher, content], cwd=account, capture_output=True, text=True, timeout=10
        )
        assert rejected.returncode == 1, rejected
        assert "launch failed:" in rejected.stderr, rejected.stderr
        assert config.read_text() == "# existing settings\n"
        assert (saves / "save.bin").read_bytes() == b"existing progress"
        assert not (account / "gamedata").exists()
    assert wrong.read_bytes() == b"not the owned disc"

    # A held account lock must reject another process before it reads the ISO.
    descriptor = os.open(account, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        rejected = subprocess.run(
            [launcher, wrong], cwd=account, capture_output=True, text=True, timeout=10
        )
        assert rejected.returncode == 1
        assert "already running for this account" in rejected.stderr
    finally:
        os.close(descriptor)

    # Create a real small XISO with the pinned extractor. The fixture contains
    # no game code. Its executable has only the format magic checked on install.
    source = root / "fixture"
    source.mkdir()
    (source / "default.xex").write_bytes(b"XEX2fixture")
    (source / "movies").mkdir()
    (source / "movies" / "sample.bin").write_bytes(b"fixture data")
    iso = root / "fixture.iso"
    subprocess.run([extractor, "-c", source, iso], check=True, capture_output=True)
    before = hashlib.sha256(iso.read_bytes()).hexdigest()
    destination = account / "gamedata"
    with iso.open("rb") as disc:
        # A descriptor previously read to EOF must still work through /proc/fd.
        disc.read()
        install(disc, destination, extractor)
    assert (destination / "default.xex").read_bytes() == b"XEX2fixture"
    assert (destination / "movies" / "sample.bin").read_bytes() == b"fixture data"
    assert hashlib.sha256(iso.read_bytes()).hexdigest() == before
    assert not list(account.glob(".simpsons-extract-*"))
    identity = (destination / "default.xex").stat().st_ino
    with iso.open("rb") as disc:
        install(disc, destination, extractor)
    assert (destination / "default.xex").stat().st_ino == identity

    # Exercise the successful Python -> exec transition with real child
    # processes. This proves launch arguments/environment and descriptor lifetime,
    # not behavior of the game's GPU or save implementation.
    inherited = dict(os.environ, REX_VSYNC="false", DISABLE_LSFG="0")
    path_keys = (
        "REX_GAME_DATA_ROOT",
        "REX_USER_DATA_ROOT",
        "REX_UPDATE_DATA_ROOT",
        "REX_CACHE_PATH",
        "REX_LOG_FILE",
    )
    inherited.update({key: "/another-account" for key in path_keys})
    for selected in (account, root / "second-account"):
        selected.mkdir(exist_ok=True)
        child = subprocess.Popen(
            [handoff, "--fixture", launcher, iso, handoff],
            cwd=selected,
            env=inherited,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        try:
            # The extractor writes progress before the JSON receipt on first run.
            line = b""
            while not line.startswith(b'{"args":'):
                ready, _, _ = select.select([child.stdout], [], [], 15)
                assert ready, "No receipt from exec child"
                line = child.stdout.readline()
                assert line, child.stderr.read()
            receipt = json.loads(line)
            assert receipt["args"] == [
                "--game_data_root",
                str(selected / "gamedata"),
                "--user_data_root",
                str(selected),
            ]
            assert receipt["cwd"] == str(selected)
            assert receipt["env"]["DISABLE_LSFG"] == "1"
            assert receipt["env"]["REX_VSYNC"] == "false"
            assert all(receipt["env"][key] is None for key in path_keys)
            second = subprocess.run(
                [launcher, wrong],
                cwd=selected,
                capture_output=True,
                text=True,
                timeout=10,
            )
            assert second.returncode == 1
            assert "already running for this account" in second.stderr
            child.communicate(b"x", timeout=10)
            assert child.returncode == 0
            lock = os.open(selected, os.O_RDONLY | os.O_DIRECTORY)
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            finally:
                os.close(lock)
        finally:
            if child.poll() is None:
                child.kill()
                child.communicate()
    assert config.read_text() == "# existing settings\n"
    assert (root / "second-account/simpsons.toml").read_bytes() == Path(
        module["CONFIG"]
    ).read_bytes()
    assert (saves / "save.bin").read_bytes() == b"existing progress"

    # Reject incomplete data rather than deleting a previous installation.
    (destination / "default.xex").unlink()
    with iso.open("rb") as disc:
        try:
            install(disc, destination, extractor)
        except ValueError as error:
            assert "Incomplete game data" in str(error)
        else:
            raise AssertionError("Incomplete installation accepted")
    assert (destination / "movies" / "sample.bin").read_bytes() == b"fixture data"

    other = root / "other-account"
    other.mkdir()
    with wrong.open("rb") as disc:
        try:
            install(disc, other / "gamedata", extractor)
        except subprocess.CalledProcessError:
            pass
        else:
            raise AssertionError("Extractor accepted corrupt ISO")
    assert not list(other.iterdir()), "Failed extraction left account state"
    (other / "gamedata").symlink_to(destination, target_is_directory=True)
    with iso.open("rb") as disc:
        try:
            install(disc, other / "gamedata", extractor)
        except ValueError as error:
            assert "another account" in str(error)
        else:
            raise AssertionError("Cross-account symlink accepted")

    # Reach the real native main function with no display. This checks dynamic
    # loading and CPU startup, not graphics or gameplay.
    environment = dict(os.environ, DISPLAY="", WAYLAND_DISPLAY="")
    engine = subprocess.run(
        [module["ENGINE"]],
        cwd=account,
        env=environment,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert engine.returncode == 1, engine
    assert "Failed to initialize GTK+" in engine.stderr, engine.stderr

print(
    "Simpsons rejection, locking, real extraction, preservation and native-loader checks passed"
)
