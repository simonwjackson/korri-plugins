#!@python@ -I
"""Child processes for the native launch contract test, not a game implementation."""

import hashlib
import json
import os
from pathlib import Path
import runpy
import sys

if sys.argv[1] == "--fixture":
    launcher, iso, program = sys.argv[2:]
    module = runpy.run_path(launcher, run_name="simpsons_handoff_test")
    with open(iso, "rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    # Configure the real installer with a real generated XISO and an executable
    # that records its launch contract. The production CLI has no such flags.
    module["launch"](Path(iso), engine=program, disc_sha256=digest)
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
                        "REX_CACHE_PATH",
                        "REX_LOG_FILE",
                        "DISABLE_LSFG",
                        "REX_VSYNC",
                    )
                },
            }
        ),
        flush=True,
    )
    # The parent observes the held lock before allowing this real process to exit.
    sys.stdin.read(1)
