"""Run the real launcher with a recording program named python3 on its PATH."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

HERE = Path(__file__).parent

# Records what the launcher handed Proton's script, then exits with a chosen status.
RECORDER = f"""#!{sys.executable}
import json, os, sys
with open(os.environ["RECORD"], "w") as record:
    json.dump({{"argv": sys.argv[1:], "cwd": os.getcwd(), "env": dict(os.environ)}}, record)
sys.exit(int(os.environ.get("RECORDER_STATUS", "0")))
"""

# Records the arguments of the fullscreen request.
XDOTOOL = f"""#!{sys.executable}
import json, os, sys
with open(os.environ["XDOTOOL_RECORD"], "w") as record:
    json.dump(sys.argv[1:], record)
"""


class LaunchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.game = root / "cache/mega-man-arena/game/4.2.3"
        self.game.mkdir(parents=True)
        self.data = self.game / "data.win"
        self.data.write_bytes(b"FORM\n")
        (self.game / "MegaManArena.exe").write_bytes(b"MZ\n")
        self.proton = root / "cache/proton/cachyos/11.0-20260601-slr-arm64"
        self.proton.mkdir(parents=True)
        (self.proton / "proton").write_text("#!/usr/bin/env python3\n")
        self.home = root / "accounts/a/mega-man-arena"
        self.home.mkdir(parents=True)
        tools = root / "bin"
        tools.mkdir()
        (tools / "python3").write_text(RECORDER)
        (tools / "python3").chmod(0o755)
        (tools / "xdotool").write_text(XDOTOOL)
        (tools / "xdotool").chmod(0o755)
        self.record = root / "record.json"
        self.xdotool_record = root / "xdotool.json"
        self.env = {
            "PATH": f"{tools}:{os.environ['PATH']}",
            "RECORD": str(self.record),
            "XDOTOOL_RECORD": str(self.xdotool_record),
            "HOME": str(self.home),
            "KORRI_PROTON_CACHYOS": str(self.proton),
            "DISPLAY": ":1",
        }

    def run_launch(self, *arguments, env=None):
        return subprocess.run(["bash", str(HERE / "proton-launch.sh"), *map(str, arguments)],
                              env=env or self.env, cwd="/", capture_output=True, text=True,
                              timeout=60)

    def test_runs_the_exe_through_proton_from_the_game_directory(self):
        result = self.run_launch(self.data)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(self.record.read_text())
        self.assertEqual(record["argv"], [
            str(self.proton / "proton"), "waitforexitandrun", str(self.game / "MegaManArena.exe"),
        ])
        self.assertEqual(record["cwd"], str(self.game))
        env = record["env"]
        self.assertEqual(env["STEAM_COMPAT_DATA_PATH"], str(self.home / "compatdata"))
        self.assertEqual(env["STEAM_COMPAT_CLIENT_INSTALL_PATH"], str(self.home / "steam"))
        self.assertEqual(env["STEAM_COMPAT_INSTALL_PATH"], str(self.game))
        self.assertEqual(env["UMU_ID"], "umu-default")
        self.assertEqual(env["STORE"], "none")
        self.assertTrue((self.home / "compatdata").is_dir())
        self.assertTrue((self.home / "steam").is_dir())

    def test_asks_for_fullscreen_when_the_game_window_shows(self):
        result = self.run_launch(self.data)
        self.assertEqual(result.returncode, 0, result.stderr)
        for _ in range(100):
            if self.xdotool_record.exists() and self.xdotool_record.read_text():
                break
            time.sleep(0.05)
        self.assertEqual(json.loads(self.xdotool_record.read_text()), [
            "search", "--sync", "--onlyvisible", "--name", "^Mega Man Arena$",
            "windowstate", "--add", "FULLSCREEN",
        ])

    def test_returns_protons_status(self):
        result = self.run_launch(self.data, env=self.env | {"RECORDER_STATUS": "7"})
        self.assertEqual(result.returncode, 7, result.stderr)

    def test_missing_or_wrong_inputs_exit_2_before_proton(self):
        missing = self.game / "missing.win"
        cases = [
            ([], {}, "usage"),
            ([self.data, self.data], {}, "usage"),
            (["data.win"], {}, "not an absolute file"),
            ([missing], {}, "not an absolute file"),
            ([self.game], {}, "not an absolute file"),
            ([self.data], {"HOME": ""}, "HOME must be an absolute directory"),
            ([self.data], {"HOME": str(self.home / "missing")}, "HOME must be an absolute directory"),
            ([self.data], {"KORRI_PROTON_CACHYOS": ""}, "not a Proton directory"),
            ([self.data], {"KORRI_PROTON_CACHYOS": str(self.home)}, "not a Proton directory"),
        ]
        for arguments, changes, message in cases:
            with self.subTest(arguments=arguments, changes=changes):
                result = self.run_launch(*arguments, env=self.env | changes)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(message, result.stderr)
                self.assertFalse(self.record.exists())

    def test_a_game_directory_without_the_exe_exits_2(self):
        (self.game / "MegaManArena.exe").unlink()
        result = self.run_launch(self.data)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("MegaManArena.exe is missing", result.stderr)


if __name__ == "__main__":
    unittest.main()
