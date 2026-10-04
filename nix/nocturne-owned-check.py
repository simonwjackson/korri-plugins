#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Opt-in test with owned assets, outside Nix inputs and public CI."""

import argparse
import atexit
import hashlib
import json
import os
from pathlib import Path
import secrets
import select
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("package", type=Path)
parser.add_argument("korrid", type=Path)
parser.add_argument("xex", type=Path)
args = parser.parse_args()
manifest = json.loads((args.package / "manifest.json").read_text())
xex = args.xex.resolve(strict=True)


def hashes(directory):
    result = {}
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            with path.open("rb") as source:
                result[str(path.relative_to(directory))] = hashlib.file_digest(
                    source, "sha256"
                ).hexdigest()
    return result


original = hashes(xex.parent)
work = Path(tempfile.mkdtemp(prefix="nocturne-owned-check-"))
account = work / "Player One '; $(exit 17)"
state = account / "nocturnerecomp"
command = [
    str(args.korrid),
    "plugin-launch",
    str(args.package / "plugin.ts"),
    json.dumps(
        {
            "runnerId": "@simonwjackson:nocturne/nocturne",
            "program": manifest["files"]["nocturne"],
            "contentPath": str(xex),
            "accountRoot": str(account),
            "files": manifest["files"],
        }
    ),
]
print(f"Private test directory: {work}", flush=True)


def stop_process(child):
    if child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()


# Own the X server PID directly. xvfb-run's shell-background PID cleanup
# failed on the ARM builder even after the game assertions passed.
authority = work / "Xauthority"
cookie = secrets.token_hex(16)
subprocess.run(["xauth", "-f", str(authority), "add", ":0", ".", cookie], check=True)
reader, writer = os.pipe()
xlog = (work / "xvfb.log").open("w")
xserver = subprocess.Popen(
    [
        "Xvfb",
        "-displayfd",
        str(writer),
        "-screen",
        "0",
        "1280x900x24",
        "-nolisten",
        "tcp",
        "-auth",
        str(authority),
    ],
    pass_fds=(writer,),
    stdout=xlog,
    stderr=subprocess.STDOUT,
)
atexit.register(stop_process, xserver)
os.close(writer)
try:
    # Xvfb can write the digits and newline separately. Closing after the
    # first read makes its newline write fail and shuts the server down.
    number = b""
    while b"\n" not in number:
        assert select.select([reader], [], [], 20)[0], "Xvfb did not start"
        chunk = os.read(reader, 64)
        assert chunk, (work / "xvfb.log").read_text()
        number += chunk
    display = ":" + number.decode().strip()
finally:
    os.close(reader)
assert display[1:].isdigit(), (work / "xvfb.log").read_text()
subprocess.run(["xauth", "-f", str(authority), "add", display, ".", cookie], check=True)
os.environ.update(DISPLAY=display, XAUTHORITY=str(authority))

# The released SDL excludes its dummy driver. A private PulseAudio null sink
# provides real audio timing without using the player's audio server.
pulse_socket = work / "pulse.sock"
pulse_log = (work / "pulse.log").open("w")
pulse = subprocess.Popen(
    [
        "pulseaudio",
        "--daemonize=no",
        "--exit-idle-time=-1",
        "--use-pid-file=no",
        "--disable-shm",
        "-n",
        f"--load=module-native-protocol-unix socket={pulse_socket} auth-anonymous=1",
        "--load=module-null-sink sink_name=nocturne_test",
    ],
    stdout=pulse_log,
    stderr=subprocess.STDOUT,
)


def stop_audio():
    stop_process(pulse)
    pulse_log.close()


atexit.register(stop_audio)
deadline = time.monotonic() + 20
while not pulse_socket.exists():
    assert pulse.poll() is None, (work / "pulse.log").read_text()
    if time.monotonic() > deadline:
        raise TimeoutError("Private audio server did not start")
    time.sleep(0.1)
outside = work / "outside-account"
outside.mkdir()
marker = outside / "preserve-me"
marker.write_bytes(b"disposable escape-detection marker")
environment = {
    **os.environ,
    "SDL_AUDIODRIVER": "pulseaudio",
    "SDL_VIDEODRIVER": "x11",
    "PULSE_SERVER": f"unix:{pulse_socket}",
    # Prove inherited native overrides cannot escape private account storage.
    "REX_USER_DATA_ROOT": str(work / "wrong-user"),
    "REX_CACHE_ROOT": str(outside),
    "REX_LOG_FILE": str(marker),
    "REX_AUTO_UPDATE_ENABLED": "true",
    # The bundled Scene Expansion mod must not enter research mode.
    "SCENE_PROBE_DIR": str(work / "probe"),
}


def session(name, competing=False):
    output_path = work / f"{name}.log"
    with output_path.open("w") as output:
        child = subprocess.Popen(
            command, env=environment, stdout=output, stderr=subprocess.STDOUT
        )
        try:
            deadline = time.monotonic() + 120
            while True:
                if child.poll() is not None:
                    raise RuntimeError(f"{name} exited: {output_path.read_text()}")
                windows = subprocess.run(
                    ["xdotool", "search", "--onlyvisible", "--name", "NocturneRecomp"],
                    capture_output=True,
                    text=True,
                )
                if windows.returncode == 0:
                    break
                if time.monotonic() > deadline:
                    raise TimeoutError(output_path.read_text())
                time.sleep(0.25)
            screenshot = work / f"{name}.png"
            # Intro transitions legitimately include black frames. Require a
            # nonblank central frame within a bounded interval, not at one
            # timestamp. Exclude the corner settings toast: it is not gameplay.
            deadline = time.monotonic() + 60
            while True:
                assert child.poll() is None, output_path.read_text()
                subprocess.run(
                    ["import", "-window", "root", str(screenshot)],
                    check=True,
                    timeout=20,
                )
                variance = subprocess.check_output(
                    [
                        "magick",
                        str(screenshot),
                        "-gravity",
                        "center",
                        "-crop",
                        "60%x60%+0+0",
                        "+repage",
                        "-format",
                        "%[fx:standard_deviation]",
                        "info:",
                    ],
                    text=True,
                )
                if float(variance) > 0.01:
                    break
                if time.monotonic() > deadline:
                    raise AssertionError(
                        f"No nonblank frame within 60 seconds: {screenshot}"
                    )
                time.sleep(1)
            native_environment = (
                Path(f"/proc/{child.pid}/environ").read_bytes().split(b"\0")
            )
            for key in (
                "REX_USER_DATA_ROOT",
                "REX_CACHE_ROOT",
                "REX_LOG_FILE",
                "REX_AUTO_UPDATE_ENABLED",
                "SCENE_PROBE_DIR",
            ):
                assert not any(
                    item.startswith(key.encode() + b"=") for item in native_environment
                )
            assert not (work / "wrong-user").exists()
            assert not (work / "probe").exists()
            if competing:
                conflict = subprocess.run(
                    command, env=environment, capture_output=True, text=True, timeout=20
                )
                assert conflict.returncode == 1
                assert "already running for this account" in conflict.stderr
            # Request close through the real X11 window, not SIGKILL. No game
            # progress is implied by reaching a visible window and guest boot.
            subprocess.run(
                ["xdotool", "windowquit", windows.stdout.splitlines()[0]], check=True
            )
            try:
                child.wait(timeout=20)
            except subprocess.TimeoutExpired:
                # This is a startup test, not a clean-shutdown assertion.
                print(
                    f"{name}: upstream did not close within 20 seconds; stopping test process",
                    flush=True,
                )
                child.kill()
                child.wait()
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
    assert not list(state.glob(".nocturne-*"))
    print(f"{name}: native window ran, screenshot {work / f'{name}.png'}", flush=True)


session("cold", competing=True)
# The bundled Scene Expansion mod is linked from the package and loads in
# normal mode: expansion installed, no research controls.
mod_link = state / "mods/scene_expansion"
assert mod_link.is_symlink(), mod_link
assert str(mod_link.readlink()).startswith("/nix/store/"), mod_link.readlink()
native_logs = "\n".join(p.read_text() for p in sorted((state / "logs").glob("*.log*")))
assert "Mod code plugin 'scene_expansion' loaded" in native_logs
assert "[scene_expansion] expand install ok" in native_logs
assert "[scene_expansion] scripted pad added" not in native_logs
assert (state / "assets/default.xex").read_bytes() == xex.read_bytes()
cache = hashes(state / "assets")
# The base game can remove default.xexp from its private copy only.
assert cache == {key: value for key, value in original.items() if key != "default.xexp"}
config = state / "nocturnerecomp.toml"
assert config.is_file()
config_before = config.read_bytes()
# Preservation of unrelated existing data is separate from a gameplay save.
sentinel = state / "preservation-test"
sentinel.write_bytes(b"existing player data")
mtime = (state / "assets/default.xex").stat().st_mtime_ns
session("warm")
assert hashes(state / "assets") == cache
assert (state / "assets/default.xex").stat().st_mtime_ns == mtime
assert sentinel.read_bytes() == b"existing player data"
assert config.read_bytes() == config_before
# The SDK loads native config after CLI. A saved override must not redirect
# writes to the original library or turn on an unpinned self-update.
for native_override in [
    f"game_data_root = {json.dumps(str(outside))}\n",
    "auto_update_enabled = true\n",
    f"cache_root = {json.dumps(str(outside))}\n",
    f"log_file = {json.dumps(str(marker))}\n",
]:
    config.write_text(native_override)
    rejected = subprocess.run(
        command, env=environment, capture_output=True, text=True, timeout=20
    )
    assert rejected.returncode == 1, rejected.stdout + rejected.stderr
    assert "must" in rejected.stderr
    assert config.read_text() == native_override
config.write_bytes(config_before)
assert hashes(xex.parent) == original
assert marker.read_bytes() == b"disposable escape-detection marker"
assert list(outside.iterdir()) == [marker]
print(
    "PASS: sandboxed native launch, bundled Scene Expansion mod loaded, private assets, concurrent-launch refusal, cached launch, config/data preservation, original files unchanged"
)
print(
    "LIMIT: screenshots require inspection; no claim of controller/audio, save/load, or full-game acceptance."
)
