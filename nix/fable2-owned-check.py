#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Owned-ISO extraction and native-entry check on a build machine, not a GPU test."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("package", type=Path)
parser.add_argument("korrid")
parser.add_argument("iso", type=Path)
args = parser.parse_args()
iso = args.iso.resolve(strict=True)
manifest = json.loads((args.package / "manifest.json").read_text())
launcher = Path(manifest["files"]["fable_ii"])
module = runpy.run_path(str(launcher), run_name="fable2_owned_validation")
expected = json.loads(Path(module["GAME_FILES"]).read_text())
needed = module["DISC_BYTES"] + sum(expected.values())
if shutil.disk_usage(tempfile.gettempdir()).free < needed:
    raise SystemExit(
        "First-run validation needs about 15 GB free. Set TMPDIR to a larger private filesystem."
    )
with iso.open("rb") as source:
    before = hashlib.file_digest(source, "sha256").hexdigest()
if before != module["DISC_SHA256"] or iso.stat().st_size != module["DISC_BYTES"]:
    raise SystemExit("ISO is not the measured USA/Europe GOTY disc")

with tempfile.TemporaryDirectory(prefix="fable2-owned-check-") as temporary:
    root = Path(temporary)
    account = root / "account"
    directory = account / "fable_ii"
    directory.mkdir(parents=True)
    configuration = directory / "fable_ii.toml"
    configuration.write_text("# owned validation settings; preserve this file\n")
    launch = {
        "runnerId": "@simonwjackson:fable-ii-recomp/fable_ii",
        "program": str(launcher),
        "contentPath": str(iso),
        "accountRoot": str(account),
        "files": manifest["files"],
    }
    environment = os.environ.copy()
    # Deliberately fail at the real SDL video entry after extraction, without
    # opening a user's display. This cannot establish rendering or gameplay.
    environment["SDL_VIDEO_DRIVER"] = "fable2-validation-disabled"
    environment.pop("DISPLAY", None)
    environment.pop("WAYLAND_DISPLAY", None)
    identity = None
    for label in ("first installation", "existing installation"):
        print("Checking " + label, flush=True)
        result = subprocess.run(
            [
                args.korrid,
                "plugin-launch",
                str(args.package / "plugin.ts"),
                json.dumps(launch),
            ],
            env=environment,
            capture_output=True,
            text=True,
            timeout=900,
        )
        if (
            result.returncode != 1
            or "SDL_InitSubSystem(SDL_INIT_VIDEO) failed"
            not in result.stdout + result.stderr
        ):
            raise SystemExit(
                f"Unexpected native-entry result {result.returncode}:\n{result.stdout}\n{result.stderr}"
            )
        game = directory / "assets-extracted/00007000"
        actual = {}
        for path in game.rglob("*"):
            if path.is_symlink():
                raise SystemExit("Extracted symlink found")
            if path.is_file():
                actual[str(path.relative_to(game))] = path.stat().st_size
        if actual != expected:
            raise SystemExit("Extracted paths/sizes differ from the measured disc")
        with (game / "default.xex").open("rb") as source:
            if (
                hashlib.file_digest(source, "sha256").hexdigest()
                != module["XEX_SHA256"]
            ):
                raise SystemExit("Extracted executable differs from the compiled input")
        current = (game / "default.xex").stat().st_ino
        if identity is not None and current != identity:
            raise SystemExit("Second launch replaced existing game data")
        identity = current
        if (
            configuration.read_text()
            != "# owned validation settings; preserve this file\n"
        ):
            raise SystemExit("Launcher changed native settings")
        if list(directory.glob(".fable-ii-extract-*")):
            raise SystemExit("Extraction left temporary data")
with iso.open("rb") as source:
    if hashlib.file_digest(source, "sha256").hexdigest() != before:
        raise SystemExit("Original ISO changed")
print(
    "PASS: owned ISO preserved, all 451 files verified, cached data reused, real native SDL entry reached"
)
print(
    "No GPU, gameplay, save/reload, device-trust or installation acceptance is claimed by this check."
)
