#!@python@ -I
"""Real child processes for launcher tests; this does not implement a game."""

import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

if sys.argv[1] == "-q" and "FABLE2_SNAPSHOT_SOURCE" in os.environ:
    # Mutate only the test's original fixture after launcher hashing, then
    # delegate extraction to the real program using the supplied snapshot path.
    original = Path(os.environ["FABLE2_SNAPSHOT_SOURCE"])
    with original.open("r+b") as source:
        data = source.read()
        marker = b"XEX2fixture"
        assert data.count(marker) == 1, "Fixture executable must occur once in the XISO"
        source.seek(data.index(marker))
        source.write(b"Y")
    extractor = os.environ["FABLE2_REAL_EXTRACTOR"]
    os.execv(extractor, [extractor, *sys.argv[1:]])
elif sys.argv[1] == "--fixture":
    launcher, iso, program, files, xex_hash = sys.argv[2:]
    module = runpy.run_path(launcher, run_name="fable2_handoff_test")
    with open(iso, "rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    module["launch"](
        Path(iso),
        engine=program,
        disc_sha256=digest,
        disc_bytes=Path(iso).stat().st_size,
        xex_sha256=xex_hash,
        game_files=files,
    )
else:
    print(
        json.dumps(
            {
                "args": sys.argv[1:],
                "cwd": os.getcwd(),
                "env": {
                    key: os.environ.get(key)
                    for key in (
                        "REX_GAME_DATA_ROOT",
                        "REX_USER_DATA_ROOT",
                        "REX_UPDATE_DATA_ROOT",
                        "REX_CACHE_ROOT",
                        "REX_METADATA_ROOT",
                        "REX_LOG_FILE",
                        "REX_VSYNC",
                    )
                },
            }
        ),
        flush=True,
    )
    # The parent checks the inherited account lock while this process is alive.
    sys.stdin.read(1)
