#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Exercise actual patched native EEPROM IO without a ROM or full game process."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def main():
    if len(sys.argv) != 6:
        raise SystemExit(
            "Usage: save-check SOURCE COMPILER CPP LAUNCH_PATCH SHUTDOWN_PATCH"
        )
    source = Path(sys.argv[1])
    compiler = sys.argv[2]
    cpp = Path(sys.argv[3])
    patches = [Path(path) for path in sys.argv[4:]]
    with tempfile.TemporaryDirectory(prefix="drmario64-save-check-") as temporary:
        work = Path(temporary)
        # Keep each header beside its siblings: the two runtime modules both
        # use a quoted rsp.hpp with different contents. Include-path ordering
        # cannot preserve that lookup if only patched headers are copied.
        for directory in ("librecomp/include", "ultramodern/include"):
            relative = Path("lib/N64ModernRuntime") / directory
            shutil.copytree(source / relative, work / relative)
        # Copy the remaining files named by our patches, not generated retail C.
        for patch in patches:
            for line in patch.read_text().splitlines():
                if line.startswith("--- a/"):
                    path = Path(line.removeprefix("--- a/"))
                    target = work / path
                    if not target.exists():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(source / path, target)
        for path in work.rglob("*"):
            if not path.is_symlink():
                path.chmod(path.stat().st_mode | 0o200)
        for patch in patches:
            subprocess.run(
                ["patch", "--batch", "--fuzz=0", "-p1", "-i", str(patch)],
                cwd=work,
                check=True,
            )
        runtime = source / "lib/N64ModernRuntime"
        edited = work / "lib/N64ModernRuntime"
        # CMake generates this export marker for static miniz. The save probe
        # does not link or invoke miniz, but the public headers include it.
        (work / "miniz_export.h").write_text("#pragma once\n#define MINIZ_EXPORT\n")
        includes = [
            work,
            edited / "librecomp/include",
            edited / "ultramodern/include",
            edited / "librecomp/src",
            source / "include",
            source / "lib/rt64/src",
            runtime / "ultramodern/include",
            runtime / "thirdparty",
            runtime / "thirdparty/concurrentqueue",
            # ultramodern exposes this path to native ARM consumers in CMake.
            runtime / "thirdparty/sse2neon",
            runtime / "thirdparty/miniz",
            runtime / "librecomp/include",
            runtime / "librecomp/include/librecomp",
            runtime / "N64Recomp/include",
            runtime / "N64Recomp/lib/rabbitizer/cplusplus/include",
            runtime / "N64Recomp/lib/rabbitizer/include",
            runtime / "N64Recomp/lib/rabbitizer/tables",
        ]
        command = [
            compiler,
            "-std=c++20",
            "-UNDEBUG",
            "-pthread",
            "-ffunction-sections",
            "-fdata-sections",
        ]
        command.extend("-I" + str(path) for path in includes)
        command.extend(
            [
                str(cpp),
                str(runtime / "librecomp/src/files.cpp"),
                str(runtime / "ultramodern/src/error_handling.cpp"),
                "-Wl,--gc-sections",
                "-o",
                str(work / "save-check"),
            ]
        )
        subprocess.run(command, check=True)
        subprocess.run(
            [str(work / "save-check"), str(work / "state")], check=True, timeout=15
        )


if __name__ == "__main__":
    main()
