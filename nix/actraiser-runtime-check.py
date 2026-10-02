"""Opt-in acceptance with an owned ROM, real plugin executor, and native game."""

import argparse
import hashlib
import json
import os
import re
import signal
from pathlib import Path
import subprocess
import tempfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("plugin", type=Path)
parser.add_argument("korrid", type=Path)
parser.add_argument("rom", type=Path)
parser.add_argument(
    "--video", action="store_true", help="Require a real SDL GPU composite capture"
)
args = parser.parse_args()
rom = args.rom.resolve(strict=True)
original = rom.read_bytes()
expected = "b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0"
assert hashlib.sha256(original).hexdigest() == expected, "Unsupported owned USA ROM"
manifest = json.loads((args.plugin / "manifest.json").read_text())
launcher = manifest["files"]["actraiser"]
# Remove inherited game diagnostics so the test defines its own conditions.
environment = {
    key: value for key, value in os.environ.items() if not key.startswith("AR_")
}
environment.update(
    SDL_AUDIODRIVER="dummy", AR_HEADLESS="1", AR_QUIT_FRAMES="600", AR_NO_RUN_DIR="1"
)

with tempfile.TemporaryDirectory(prefix="actraiser-private-check-") as temporary:
    work = Path(temporary)
    account = work / "Player '; $(touch injected) %s"
    data = account / "ActRaiserRecomp/game"
    owned = work / "Owned '; $(touch injected) %.sfc"
    owned.write_bytes(original)
    owned.chmod(0o400)
    launch_input = {
        "runnerId": "@simonwjackson:actraiser/actraiser",
        "program": launcher,
        "contentPath": str(owned),
        "accountRoot": str(account),
        "files": manifest["files"],
    }

    def launch(extra=None, *, accepted=True, content=None):
        request = dict(launch_input)
        if content is not None:
            request["contentPath"] = str(content)
        result = subprocess.run(
            [
                str(args.korrid),
                "plugin-launch",
                str(args.plugin / "plugin.ts"),
                json.dumps(request),
            ],
            cwd=work,
            env=environment | (extra or {}),
            capture_output=True,
            text=True,
            timeout=120,
        )
        output = result.stdout + result.stderr
        if accepted:
            assert result.returncode == 0, output
            assert "Loaded ROM:" in output, output
            assert "[runner-trace]" in output, output
            assert "FATAL" not in output and "[session-fatal]" not in output, output
        else:
            assert result.returncode != 0, output
        return output

    invalid = work / "Arcade.sfc"
    invalid.write_bytes(b"wrong ROM")
    assert "Unsupported ROM" in launch(accepted=False, content=invalid)
    invalid.write_bytes(bytes(len(original)))
    assert "Unsupported ROM" in launch(accepted=False, content=invalid)
    assert not data.exists(), "Invalid ROM created player state"

    capture = {"AR_SHOT_EVERY": "120", "AR_SHOT_FROM": "120", "AR_SHOT_TO": "600"}
    if args.video:
        capture.update(AR_HEADLESS_VIDEO="1", AR_SHOT_REQUIRE_COMPOSITE="1")
    output = launch(capture)
    assert "capture=" in output, output
    images = list((data / "saves").glob("shot_*.ppm"))
    assert images, output
    for image in images:
        content = image.read_bytes()
        assert content.startswith(b"P6\n"), image
        assert len(content) > 1000, image
    assert any(
        len(set(image.read_bytes().split(b"\n", 3)[-1])) > 16 for image in images
    ), "Only blank frames"
    if args.video:
        assert "capture=final-composite" in output, output
    assert (data / "config.ini").is_file()
    assert (data / "game-assets/manifest.ini").is_file()
    assert (
        data / "game-assets/fonts/noto/NotoSans-SemiCondensedExtraBold.ttf"
    ).is_file()
    assert (data / "game-assets/languages/native-us/pack.ini").is_file()
    print(
        "PASS: invalid-ROM refusal, native boot, resources and "
        + ("GPU composite" if args.video else "PPU")
        + " frames"
    )

    # Use the game's own setting actions and persistence path, never write SRAM.
    output = launch(
        {
            "AR_SETTING_SET": "audio_master_volume=25",
            "AR_SETTING_AT_GF": "120",
            "AR_SETTING_SET_2": "exit_desktop=run",
            "AR_SETTING_AT_GF_2": "121",
        }
    )
    assert "exit_desktop=run -> applied action" in output, output
    settings = data / "settings.ini"
    assert settings.is_file(), output
    saved_settings = settings.read_bytes()
    assert re.search(rb"^audio_master_volume\s*=\s*25%\s*$", saved_settings, re.M), (
        saved_settings
    )
    config = data / "config.ini"
    config.write_text(config.read_text() + "\n; private acceptance marker\n")
    launch({"AR_SETTING_SET": "exit_desktop=run", "AR_SETTING_AT_GF": "120"})
    # Re-save without an audio override proves the native loader restored it.
    # Native serialization also normalizes widescreen flags in headless mode;
    # byte-for-byte equality across a native re-save is not its contract.
    saved_settings = settings.read_bytes()
    assert re.search(rb"^audio_master_volume\s*=\s*25%\s*$", saved_settings, re.M), (
        saved_settings
    )
    assert "private acceptance marker" in config.read_text()
    print(
        "PASS: audio setting persistence and reload, cached launch and config preservation"
    )

    # Exercise updates and refusal through the actual launcher, not its helpers.
    retained = data / "saves/acceptance-preserve.bin"
    retained.write_bytes(b"user-owned bytes: not a valid campaign fixture")
    defaults = data / "defaults"
    current_defaults = os.readlink(defaults)
    defaults.unlink()
    defaults.symlink_to(
        "/nix/store/" + "0" * 32 + "-actraiser-previous/share/ActRaiserRecomp/defaults"
    )
    launch()
    assert os.readlink(defaults) == current_defaults
    fonts = data / "game-assets/fonts"
    current_fonts = os.readlink(fonts)
    fonts.unlink()
    fonts.symlink_to(work / "unrelated-fonts")
    assert "unrelated resource link" in launch(accepted=False)
    assert os.readlink(fonts) == str(work / "unrelated-fonts")
    fonts.unlink()
    fonts.mkdir()
    assert "existing resource directory" in launch(accepted=False)
    assert fonts.is_dir() and not fonts.is_symlink()
    fonts.rmdir()
    fonts.symlink_to(current_fonts)
    assert retained.read_bytes() == b"user-owned bytes: not a valid campaign fixture"
    assert settings.read_bytes() == saved_settings
    assert "private acceptance marker" in config.read_text()
    print(
        "PASS: managed resource update, collision refusal, and preservation of unrelated data"
    )

    log_path = work / "concurrent-launch.log"
    with log_path.open("w") as log:
        active = subprocess.Popen(
            [
                str(args.korrid),
                "plugin-launch",
                str(args.plugin / "plugin.ts"),
                json.dumps(launch_input),
            ],
            cwd=work,
            env=environment | {"AR_PACE": "1"},
            stdout=log,
            stderr=log,
            start_new_session=True,
        )
        try:
            deadline = time.monotonic() + 60
            while "[lifecycle] game session ready" not in log_path.read_text():
                assert active.poll() is None, log_path.read_text()
                assert time.monotonic() < deadline, log_path.read_text()
                time.sleep(0.05)
            assert "already running" in launch(accepted=False)
            assert active.wait(timeout=90) == 0, log_path.read_text()
        finally:
            if active.poll() is None:
                os.killpg(active.pid, signal.SIGTERM)
                active.wait(timeout=10)
    print("PASS: lock survives native execution and rejects an overlapping launch")

    output = launch(
        {
            "AR_SAVE_EDIT": "1",
            "AR_SETTING_SET": "save_lives=5",
            "AR_SETTING_AT_GF": "120",
            "AR_SETTING_SET_2": "save_apply_persist=run",
            "AR_SETTING_AT_GF_2": "121",
        }
    )
    # A title-screen boot has no completed campaign save. Upstream must reject
    # editing uninitialized SRAM instead of creating a plausible but invalid save.
    assert "save_apply_persist=run -> rejected action" in output, output
    assert "current SRAM has no valid save checksum" in output, output
    battery = data / "saves/save.srm"
    assert not battery.exists(), "An invalid save edit wrote a battery image"
    battery.write_bytes(b"deliberately truncated save")
    output = launch(accepted=False)
    assert "could not be loaded" in output, output
    assert battery.read_bytes() == b"deliberately truncated save"
    print("PASS: uninitialized-save refusal and corrupt-save preservation")

    assert owned.read_bytes() == original
    assert not (work / "injected").exists()

assert rom.read_bytes() == original, "Owned source ROM changed"
print("PASS: original ROM unchanged; no files written to the owned library")
print(
    "Not verified: campaign save/reload, physical-device gameplay, audio output, controller input, or full campaign completion"
)
