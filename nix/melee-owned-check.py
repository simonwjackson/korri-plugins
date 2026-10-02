#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Opt-in owned-disc test through korrid. Run only on a build machine."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import resource
import secrets
import select
import signal
import subprocess
import tempfile
import time

from Xlib import display, protocol


def stop(child):
    if child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()


@contextmanager
def private_display(root):
    # Xvfb isolates the display and keyboard. Vulkan still uses the build
    # machine's hardware driver; the port refuses CPU Vulkan adapters.
    authority = root / "Xauthority"
    authority.touch(mode=0o600)
    cookie = secrets.token_hex(16)
    subprocess.run(
        ["xauth", "-f", str(authority), "add", ":0", ".", cookie], check=True
    )
    reader, writer = os.pipe()
    previous = {key: os.environ.get(key) for key in ("DISPLAY", "XAUTHORITY")}
    with (root / "xvfb.log").open("w") as log:
        server = subprocess.Popen(
            [
                "Xvfb",
                "-displayfd",
                str(writer),
                "-screen",
                "0",
                "1280x960x24",
                "-nolisten",
                "tcp",
                "-auth",
                str(authority),
            ],
            pass_fds=(writer,),
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        os.close(writer)
        try:
            number = b""
            try:
                while b"\n" not in number:
                    assert select.select([reader], [], [], 20)[0], (
                        "Xvfb startup timed out"
                    )
                    chunk = os.read(reader, 64)
                    assert chunk, (root / "xvfb.log").read_text()
                    number += chunk
            finally:
                os.close(reader)
            value = ":" + number.decode().strip()
            assert value[1:].isdigit()
            subprocess.run(
                ["xauth", "-f", str(authority), "add", value, ".", cookie], check=True
            )
            os.environ.update(DISPLAY=value, XAUTHORITY=str(authority))
            yield
        finally:
            stop(server)
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def wait_for(predicate, child, log, seconds=180):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        assert child.poll() is None, (
            f"Native exit {child.returncode}:\n{log.read_text()[-6000:]}"
        )
        result = predicate()
        if result:
            return result
        time.sleep(0.25)
    raise AssertionError(f"Native readiness timed out:\n{log.read_text()[-6000:]}")


def window():
    result = subprocess.run(
        ["xdotool", "search", "--onlyvisible", "--name", "^melee-pc$"],
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()[0] if result.returncode == 0 else None


def press(key):
    # Hold across slow software-rendered frames, without keyboard autorepeat.
    subprocess.run(["xdotool", "keydown", key], check=True)
    time.sleep(0.2)
    subprocess.run(["xdotool", "keyup", key], check=True)
    time.sleep(2)


def close_window(wid):
    # Send the actual native close event, not SIGKILL or XKillClient.
    connection = display.Display()
    try:
        target = connection.create_resource_object("window", int(wid))
        target.send_event(
            protocol.event.ClientMessage(
                window=target,
                client_type=connection.intern_atom("WM_PROTOCOLS"),
                data=(32, [connection.intern_atom("WM_DELETE_WINDOW"), 0, 0, 0, 0]),
            )
        )
        connection.sync()
    finally:
        connection.close()


def interrupted(signum, _frame):
    raise SystemExit(128 + signum)


def main():
    signal.signal(signal.SIGTERM, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("korrid", type=Path)
    parser.add_argument("iso", type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    iso = args.iso.resolve(strict=True)
    expected = "0de05981a34156b9cedcef73c73d4244ac05cf6149ab3c9cfed917698819e464"
    assert digest(iso) == expected, (
        "Supply the measured USA 1.02 raw ISO, not an archive"
    )
    manifest = json.loads((args.package / "manifest.json").read_text())
    os.umask(0o077)
    root = Path(tempfile.mkdtemp(prefix="korri-melee-owned-"))
    print(f"Private test evidence: {root}", flush=True)
    account = root / "Account '; $(exit 19)"
    native = account / "melee-pc"
    disc = root / "Disc '; $(exit 17).iso"
    disc.symlink_to(iso)
    outside = root / "outside-account"
    outside.mkdir()
    marker = outside / "keep"
    marker.write_text("unchanged")
    command = [
        str(args.korrid),
        "plugin-launch",
        str(args.package / "plugin.ts"),
        json.dumps(
            {
                "runnerId": "@simonwjackson:melee-pc/melee-pc",
                "program": manifest["files"]["melee-pc"],
                "contentPath": str(disc),
                "accountRoot": str(account),
                "files": manifest["files"],
            }
        ),
    ]
    with private_display(root):
        environment = dict(
            os.environ,
            SDL_VIDEODRIVER="x11",
            SDL_AUDIODRIVER="dummy",
            HOME=str(outside),
            APPIMAGE=str(marker),
            MELEE_CACHE_DIR=str(outside),
            MELEE_LOG_FILE=str(marker),
            XDG_DATA_HOME=str(outside),
        )
        card_before = None
        for name in ("first", "reload"):
            log = root / f"{name}.log"
            with log.open("w") as output:
                child = subprocess.Popen(
                    command,
                    env=environment,
                    stdout=output,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                )
                try:
                    wid = wait_for(window, child, log)
                    subprocess.run(
                        ["xdotool", "windowfocus", "--sync", wid], check=True
                    )
                    wait_for(
                        lambda: "graphics backend: vulkan" in log.read_text(),
                        child,
                        log,
                    )
                    if name == "first":
                        competing = subprocess.run(
                            command,
                            env=environment,
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )
                        assert (
                            competing.returncode != 0
                            and "already running" in competing.stderr
                        ), competing.stderr
                    # Main menu loads MnMaAll. This is stronger than detecting
                    # a window or shader warm-up, which can precede game boot.
                    for _ in range(100):
                        assert child.poll() is None, log.read_text()[-6000:]
                        if "HIT: MnMaAll." in log.read_text():
                            break
                        press("Return")
                    else:
                        raise AssertionError(
                            f"Did not reach game menu:\n{log.read_text()[-6000:]}"
                        )
                    time.sleep(3)
                    subprocess.run(
                        ["import", "-window", wid, str(root / f"{name}.png")],
                        check=True,
                        timeout=20,
                    )
                    # F1 opens upstream settings; closing it saves native prefs.
                    press("F1")
                    press("F1")
                    cards = list(native.rglob("*.gci"))
                    assert cards, f"No native memory card under {native}"
                    if name == "reload":
                        assert {str(p.relative_to(native)) for p in cards} == set(
                            card_before
                        )
                    close_window(wid)
                    assert child.wait(timeout=30) == 0, log.read_text()[-6000:]
                finally:
                    stop(child)
            text = log.read_text()
            assert "PANIC " not in text and "[FATAL]" not in text, text[-6000:]
            assert "audio: SDL_OpenAudioDeviceStream failed" not in text, text[-6000:]
            assert (native / "launcher.cfg").is_file(), "Native settings were not saved"
            cards = {
                str(p.relative_to(native)): p.stat().st_size
                for p in native.rglob("*.gci")
            }
            assert cards
            settings = native / "launcher.cfg"
            config = settings.read_text()
            if name == "first":
                card_before = cards
                # Native key/value grammar comes from launcher_data.cpp.
                # Verify use of this nondefault preference through presentation,
                # not just that the file still exists on the second launch.
                assert "\nvsync 1\n" in config, config
                settings.write_text(config.replace("\nvsync 1\n", "\nvsync 0\n"))
            else:
                # The game updates card metadata at startup. Byte-identical
                # files are not an invariant; successfully reopening them is.
                assert cards == card_before, "Native card names or sizes changed"
                assert f"Loaded GC Card Image: {native / 'USA/Card A'}" in text
                assert "\nvsync 0\n" in config
                assert any(
                    f"present mode {mode}" in text for mode in ("Mailbox", "Immediate")
                ), text[:6000]
        assert marker.read_text() == "unchanged"
        assert sorted(p.name for p in outside.iterdir()) == ["keep"], (
            "State escaped account root"
        )
    assert digest(iso) == expected, "Original ISO changed"
    print(
        "PASS: production launch, Vulkan menu, keyboard input, account lock, native card reopening and saved VSync preference, clean window close, unchanged ISO",
        flush=True,
    )
    print(
        "Not tested: full matches, gameplay save/load, physical controllers/audio/display, performance, netplay, or device installation",
        flush=True,
    )


if __name__ == "__main__":
    main()
