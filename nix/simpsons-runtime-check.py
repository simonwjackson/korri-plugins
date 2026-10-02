#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3
"""Opt-in owned-ISO installation check on a build host, without opening a window."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def digest(path: Path) -> str:
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: verify-simpsons PACKAGE KORRID OWNED_ISO")
    package, korrid, content = sys.argv[1:]
    package = Path(package)
    content = Path(content).resolve()
    expected = "fd794e7a3025c3fd1340d25301658bac8c829a65d5e5e47d2663b431f869531b"
    if digest(content) != expected:
        raise SystemExit("Supply the measured USA Xbox 360 ISO")
    manifest = json.loads((package / "manifest.json").read_text())
    with tempfile.TemporaryDirectory(prefix="korri-simpsons-owned-disc-") as temporary:
        account = Path(temporary) / "account '; $(exit 19) #"
        directory = account / "simpsons"
        launch = {
            "runnerId": "@simonwjackson:the-simpsons-game/simpsons",
            "program": manifest["files"]["simpsons"],
            "contentPath": str(content),
            "accountRoot": str(account),
            "files": manifest["files"],
        }
        command = [
            korrid,
            "plugin-launch",
            str(package / "plugin.ts"),
            json.dumps(launch),
        ]
        environment = dict(os.environ, DISPLAY="", WAYLAND_DISPLAY="")
        inode = None
        for attempt in range(2):
            result = subprocess.run(
                command, env=environment, capture_output=True, text=True, timeout=600
            )
            assert result.returncode == 1, result
            assert "Failed to initialize GTK+" in result.stderr, result.stderr
            executable = directory / "gamedata/default.xex"
            assert (
                digest(executable)
                == "71d99dad06be1b512fc3058123b84fdad71339205a7e9249058ac5e34a82a231"
            )
            assert (directory / "gamedata/movies").is_dir()
            assert not list(directory.glob(".simpsons-*"))
            config = directory / "simpsons.toml"
            if inode is None:
                inode = executable.stat().st_ino
                assert "gpu_shader_max_cf_iterations = 0" in config.read_text()
                config.write_text("# existing native settings\nfullscreen = false\n")
                (directory / "content").mkdir()
                (directory / "content/progress.fixture").write_bytes(
                    b"existing progress"
                )
            else:
                assert executable.stat().st_ino == inode, (
                    "Cached installation was replaced"
                )
                assert (
                    config.read_text()
                    == "# existing native settings\nfullscreen = false\n"
                )
                assert (
                    directory / "content/progress.fixture"
                ).read_bytes() == b"existing progress"
            print(
                f"Attempt {attempt + 1}: owned ISO installation and native loader passed"
            )
    assert digest(content) == expected, "Source ISO changed"
    print(
        "Temporary retail files removed. Graphics, input, audio and gameplay were not tested."
    )


if __name__ == "__main__":
    main()
