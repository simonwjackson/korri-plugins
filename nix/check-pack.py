#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3 python3Packages.pillow

"""Check the real cartridge payload and Core-generated plugin package."""

import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import urlparse

from PIL import Image


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_payload(payload, originals):
    require(len(originals) == 25, "expected 25 files for the 24 selected games")
    names = [entry["name"] for entry in originals]
    require(len(set(names)) == 25, "duplicate original cartridge names")
    cartridges = payload / "cartridges"
    require(
        {path.name for path in cartridges.iterdir()} == set(names),
        "unexpected or missing cartridge",
    )
    credits = (payload / "CREDITS.md").read_text()
    require(
        sum(line.startswith("| [") for line in credits.splitlines()) == 24,
        "expected credits for 24 games",
    )
    license_text = (payload / "CC-BY-NC-SA-4.0.txt").read_text()
    require(
        license_text.startswith(
            "Attribution-NonCommercial-ShareAlike 4.0 International"
        ),
        "wrong license",
    )
    require("Disclaimer of Warranties" in license_text, "missing warranty disclaimer")
    instructions = (payload / "README.md").read_text()
    require("no PICO-8 application" in instructions, "missing player exclusion")
    require(
        "does not perform that step or add game tiles" in instructions,
        "missing manual-registration limit",
    )
    notices = payload / "notices"
    require(len(list(notices.glob("*.txt"))) == 25, "missing publisher notices")
    source_notices = "\n".join(path.read_text() for path in notices.glob("*.txt"))
    checksums = {}
    for line in (payload / "SHA256SUMS").read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, "invalid checksum line")
        digest, name = match.groups()
        require(name not in checksums, "duplicate checksum entry")
        checksums[name] = digest
    require(set(checksums) == set(names), "incomplete checksum inventory")
    for entry in originals:
        name = entry["name"]
        require(
            Path(name).name == name and name.endswith(".p8.png"),
            "invalid original filename",
        )
        path = cartridges / name
        require(
            path.is_file() and not path.is_symlink(), "cartridge must be a regular file"
        )
        uri = urlparse(entry["url"])
        require(
            uri.scheme == "https"
            and uri.hostname in {"www.lexaloffle.com", "raw.githubusercontent.com"},
            "unexpected original source",
        )
        require(
            entry["url"] in source_notices and name in credits,
            "missing original source or credit mapping",
        )
        sri = entry["outputHash"]
        require(sri.startswith("sha256-"), "expected native SHA-256 SRI pin")
        expected = base64.b64decode(sri.removeprefix("sha256-"), validate=True)
        require(len(expected) == 32, "invalid SHA-256 pin")
        binary = path.read_bytes()
        digest = hashlib.sha256(binary).digest()
        require(
            digest == expected and digest.hex() == checksums[name],
            "changed original cartridge: " + name,
        )
        require(binary.startswith(b"\x89PNG\r\n\x1a\n"), "not a PNG cartridge")
        with Image.open(path) as image:
            require(
                image.size == (160, 205) and image.mode == "RGBA",
                "invalid cartridge dimensions or channels",
            )
            memory = bytes(
                (b & 3) | ((g & 3) << 2) | ((r & 3) << 4) | ((a & 3) << 6)
                for r, g, b, a in image.getdata()
            )
        require(
            len(memory) == 32800 and any(memory[0x4300:0x8000]),
            "missing encoded cartridge code",
        )
    require(
        {"intoruins.p8.png", "intoruins_main.p8.png"} <= set(names),
        "missing original offline pair",
    )
    require(
        "intoruins-7.p8.png" not in names, "BBS title is not the offline distribution"
    )


def check_plugin(plugin, payload):
    manifest = json.loads((plugin / "manifest.json").read_text())
    require(
        manifest["publisher"] == {"namespace": "@simonwjackson"},
        "wrong personal publisher",
    )
    require(
        manifest["entry"] == "plugin.ts" and manifest["sources"] == ["plugin.ts"],
        "unexpected source inventory",
    )
    require(
        manifest["services"] == {} and manifest["ports"] == {},
        "data pack must request no native services or ports",
    )
    require(set(manifest["packages"]) == {"cartridges"}, "unexpected runtime package")
    expected = {
        "cartridges": payload / "cartridges",
        "credits": payload / "CREDITS.md",
        "license": payload / "CC-BY-NC-SA-4.0.txt",
        "notices": payload / "notices",
        "checksums": payload / "SHA256SUMS",
        "instructions": payload / "README.md",
    }
    require(
        manifest["files"] == {name: str(path) for name, path in expected.items()},
        "wrong packaged file references",
    )
    require(
        all(path.exists() for path in expected.values()), "missing named payload file"
    )
    source = (plugin / "plugin.ts").read_text()
    require(
        set(re.findall(r"export const (\w+) =", source))
        == {"name", "title", "description"},
        "unexpected plugin contribution",
    )
    require(
        'export const name = "pico8-starter-pack"' in source, "wrong plugin identity"
    )


def negative_checks(payload, originals):
    with tempfile.TemporaryDirectory() as directory:
        damaged = Path(directory) / "pack"
        shutil.copytree(payload, damaged)
        damaged.chmod(0o755)
        for path in damaged.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        victim = damaged / "cartridges" / originals[0]["name"]
        victim.write_bytes(victim.read_bytes() + b"changed")
        expect_failure(
            lambda: check_payload(damaged, originals), "changed original cartridge"
        )
        shutil.copyfile(payload / "cartridges" / originals[0]["name"], victim)
        (damaged / "cartridges" / "intoruins_main.p8.png").unlink()
        expect_failure(
            lambda: check_payload(damaged, originals), "unexpected or missing cartridge"
        )
        shutil.copyfile(
            payload / "cartridges" / "intoruins_main.p8.png",
            damaged / "cartridges" / "intoruins_main.p8.png",
        )
        (damaged / "CC-BY-NC-SA-4.0.txt").write_text("wrong license")
        expect_failure(lambda: check_payload(damaged, originals), "wrong license")
        shutil.copyfile(
            payload / "CC-BY-NC-SA-4.0.txt", damaged / "CC-BY-NC-SA-4.0.txt"
        )
        (damaged / "CREDITS.md").write_text("no credits")
        expect_failure(lambda: check_payload(damaged, originals), "expected credits")


def expect_failure(action, fragment):
    try:
        action()
    except ValueError as error:
        require(fragment in str(error), "unexpected rejection: " + str(error))
    else:
        raise ValueError("invalid package was accepted: " + fragment)


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: check-pack.py PAYLOAD ORIGINAL_FETCHURL_PINS PLUGIN")
    payload, pins, plugin = map(Path, sys.argv[1:])
    originals = json.loads(pins.read_text())
    check_payload(payload, originals)
    check_plugin(plugin, payload)
    negative_checks(payload, originals)
    print(
        "Verified 25 original cartridge hashes, structure, 24 credit entries, notice presence, native manifest and four rejection cases."
    )


if __name__ == "__main__":
    main()
