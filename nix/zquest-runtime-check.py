#!/usr/bin/env python3
"""Exercise the packaged player through Core on an isolated Xvfb display."""

import hashlib
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import time

from PIL import Image

package, engine, korrid, system, fixtures = sys.argv[1:]
package, engine = Path(package), Path(engine)
manifest = json.loads((package / "manifest.json").read_text())
launcher = Path(manifest["files"]["zplayer"])
executable = engine / "bin/zplayer"
header = executable.read_bytes()[:20]
assert header[:6] == b"\x7fELF\x02\x01", header
assert (
    struct.unpack_from("<H", header, 18)[0]
    == {
        "x86_64-linux": 62,
        "aarch64-linux": 183,
    }[system]
)
assert not (engine / "bin/zeditor").exists()
assert not (engine / "bin/zscript").exists()
resources = engine / "share/zquestclassic"
assert not (resources / "quests").exists()
for license_name in [
    "stduuid",
    "allegro5",
    "gme",
    "gme-gpl2",
    "poolSTL-Boost",
    "poolSTL-BSD",
    "poolSTL-MIT",
]:
    assert (
        resources / "licenses/pinned-dependencies" / f"{license_name}.txt"
    ).stat().st_size > 100
assert (resources / "licenses/zquest_classic.LICENSE.txt").stat().st_size > 100
subprocess.run([executable, "-version"], check=True, timeout=20)

root = Path(tempfile.mkdtemp(prefix="zquest-runtime-")).resolve()
print(f"ZQuest runtime evidence: {root}", flush=True)


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def command(quest, account):
    request = {
        "runnerId": "@simonwjackson:zquest-classic/zplayer",
        "program": str(launcher),
        "contentPath": str(quest),
        "accountRoot": str(account),
        "files": manifest["files"],
    }
    return [korrid, "plugin-launch", str(package / "plugin.ts"), json.dumps(request)]


def account(name):
    directory = root / name / "zquest-classic"
    directory.mkdir(parents=True)
    # Native test-only settings. Production retains upstream sound defaults and
    # replay-upload consent. No audio hardware or network is used in this check.
    (directory / "zc.cfg").write_text(
        "[zeldadx]\nnosound = 1\nfullscreen = 0\n"
        "replay_upload = 0\nreplay_upload_prompt = 1\n"
        "[korri_test]\nsentinel = keep-me\n"
    )
    return directory.parent


def wait_for(test, child, explanation, timeout=45):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if test():
            return
        if child.poll() is not None:
            raise AssertionError(
                f"Player exited {child.returncode}: {explanation}; logs in {root}"
            )
        time.sleep(0.1)
    raise AssertionError(f"Timed out: {explanation}; logs in {root}")


def key(name):
    subprocess.run(["xdotool", "keydown", name], check=True)
    # The native game samples input per frame. Very short XTest events can vanish.
    time.sleep(0.2)
    subprocess.run(["xdotool", "keyup", name], check=True)
    time.sleep(0.8)


def play(quest, owner, *, save=False, concurrent=False):
    directory = owner / "zquest-classic"
    native_log = directory / "allegro.log"
    native_log.unlink(missing_ok=True)
    save_file = directory / "saves" / f"sha256:{digest(quest)}.sav"
    with (directory / "check-output.log").open("w") as log:
        child = subprocess.Popen(
            command(quest, owner),
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            wait_for(
                lambda: (
                    native_log.exists()
                    and f"[QUEST METADATA]\nPath: {quest}"
                    in native_log.read_text(errors="replace")
                ),
                child,
                "selected quest loaded",
            )
            wait_for(
                lambda: save_file.exists() and save_file.stat().st_size > 100,
                child,
                "native save exists",
            )
            windows = subprocess.check_output(
                ["xdotool", "search", "--onlyvisible", "--name", "."], text=True
            ).splitlines()
            subprocess.run(
                ["xdotool", "windowfocus", "--sync", windows[-1]], check=True
            )
            time.sleep(1)
            if concurrent:
                before = digest(save_file)
                rejected = subprocess.run(
                    command(quest, owner), capture_output=True, text=True, timeout=20
                )
                assert rejected.returncode != 0, rejected.stdout
                assert "already running" in rejected.stderr, rejected.stderr
                assert digest(save_file) == before
            previous_snapshots = set(directory.rglob("zc_screen*.png"))
            key("F12")
            wait_for(
                lambda: bool(
                    set(directory.rglob("zc_screen*.png")) - previous_snapshots
                ),
                child,
                "native screenshot responds to keyboard input",
            )
            snapshot = next(
                iter(set(directory.rglob("zc_screen*.png")) - previous_snapshots)
            )
            with Image.open(snapshot) as image:
                assert image.width >= 256 and image.height >= 168
                colors = image.convert("RGB").getcolors(image.width * image.height)
                assert colors is not None and len(colors) > 8, (
                    "blank or failed rendering"
                )
            if save:
                before = digest(save_file)
                for action in ["F6", "Return", "Down", "Return"]:
                    key(action)
                wait_for(
                    lambda: digest(save_file) != before,
                    child,
                    "in-game save changed persisted native state",
                )
                assert (directory / "saves/backup").is_dir()
            key("F10")
            key("Return")
            assert child.wait(timeout=20) == 0
            assert "sentinel = keep-me" in (directory / "zc.cfg").read_text()
            return save_file
        except Exception:
            if native_log.exists():
                print(native_log.read_text(errors="replace"), flush=True)
            print(
                (directory / "check-output.log").read_text(errors="replace"), flush=True
            )
            raise
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait()


# Use upstream's shipped default quest, not retail data or downloaded fan games.
quest = root / "Quest '; $(exit 19).qst"
shutil.copyfile(resources / "modules/classic/default.qst", quest)
original_hash = digest(quest)
owner = account("Player One '; $(exit 21)")
save = play(quest, owner, save=True, concurrent=True)
saved_hash = digest(save)
assert digest(quest) == original_hash

# Move the input so the old path is absent. The same save must load, not merely
# a new empty slot. The engine patch also updates the path within loaded state.
moved = root / "renamed.QST"
quest.rename(moved)
assert play(moved, owner) == save
assert digest(save) == saved_hash
assert len(list((owner / "zquest-classic/saves").glob("*.sav"))) == 1

# A second account gets a new slot without touching the first account's state.
other_owner = account("Player Two")
other_save = play(moved, other_owner)
assert other_save != save
assert digest(save) == saved_hash

# This LZSS quest remains valid with trailing bytes. Treat the changed whole
# file as a distinct release even though its native quest data is unchanged.
with moved.open("ab") as changed:
    changed.write(b"\x00")
updated_save = play(moved, owner)
assert updated_save != save
assert digest(save) == saved_hash
assert len(list((owner / "zquest-classic/saves").glob("*.sav"))) == 2

# Reject unsupported or missing inputs before creating state.
os.mkfifo(root / "pipe.qst")
for invalid in [root / "missing.qst", root / "archive.zip", root / "pipe.qst"]:
    if invalid.suffix == ".zip":
        invalid.write_bytes(b"not a quest")
    unused = root / "unused-account"
    result = subprocess.run(
        command(invalid, unused), capture_output=True, text=True, timeout=20
    )
    assert result.returncode != 0
    assert not unused.exists()

# User-authored resources must never be overwritten, including foreign links.
protected = account("Protected")
assets = protected / "zquest-classic/assets"
assets.mkdir()
(assets / "user-file").write_text("preserve")
result = subprocess.run(
    command(moved, protected), capture_output=True, text=True, timeout=20
)
assert result.returncode != 0 and "Refusing to replace" in result.stderr
assert (assets / "user-file").read_text() == "preserve"

# Exercise the actual packaged resource setup too: owned links can be repaired,
# foreign links cannot.
loader = importlib.machinery.SourceFileLoader("zquest_launcher", str(launcher))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)
repair = root / "resource-repair"
repair.mkdir()
(repair / "assets").symlink_to("/nix/store/old-zquest/share/zquestclassic/assets")
module.prepare_resources(repair)
assert (repair / "assets").resolve() == resources / "assets"
(repair / "assets").unlink()
(repair / "assets").symlink_to(root)
try:
    module.prepare_resources(repair)
    raise AssertionError("foreign resource link was replaced")
except ValueError:
    pass
assert (repair / "assets").resolve() == root

# Assert upstream's recorded script execution on the real interpreter. These
# fetched test fixtures are not part of the distributable plugin closure.
script_account = account("Script replay") / "zquest-classic"
module.prepare_resources(script_account)
replay_result = subprocess.run(
    [
        executable,
        "-headless",
        "-assert",
        str(Path(fixtures) / "auto_scopes.zplay"),
        "-replay-exit-when-done",
        "-replay-output-dir",
        str(script_account),
    ],
    cwd=script_account,
    env=dict(os.environ, ZC_DISABLE_CHDIR="1"),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    timeout=90,
)
assert replay_result.returncode == 0, replay_result.stdout
assert "[Test] done" in replay_result.stdout, replay_result.stdout
print(
    f"ZQuest {system}: native launch, input, screenshot, save/reload, rename, account isolation and refusal checks passed"
)
