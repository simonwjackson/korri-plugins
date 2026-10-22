"""Run the real launcher script against a recording program named `proton`.

The launcher runs `python3 $KORRI_PROTON/proton waitforexitandrun <exe>`. The
fake Proton records its arguments, working directory and environment, then
exits with a chosen status. Nothing here needs an FHS environment, Wine, the
game or a display.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).parent

RECORDER = """import json, os, sys
with open(os.environ["RECORD"], "w") as record:
    json.dump({"argv": sys.argv[1:], "cwd": os.getcwd(), "env": dict(os.environ)}, record)
sys.exit(int(os.environ.get("RECORDER_STATUS", "0")))
"""


class LaunchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.game = root / "cache/mega-man-maker/game/1.10.4.2"
        self.game.mkdir(parents=True)
        self.data = self.game / "data.win"
        self.data.write_bytes(b"FORM\n")
        self.exe = self.game / "MegaMaker.exe"
        self.exe.write_bytes(b"MZ\n")
        self.home = root / "accounts/a/mega-man-maker"
        self.home.mkdir(parents=True)
        self.proton = root / "cache/proton/cachyos/11.0-20260601-slr-arm64"
        self.proton.mkdir(parents=True)
        (self.proton / "proton").write_text(RECORDER)
        self.record = root / "record.json"
        tools = {Path(shutil.which(name)).parent for name in ("bash", "python3", "mkdir")}
        self.env = {
            "PATH": ":".join(map(str, sorted(tools))),
            "RECORD": str(self.record),
            "HOME": str(self.home),
            "KORRI_PROTON": str(self.proton),
            "DISPLAY": ":1",
        }

    def run_launch(self, *arguments, env=None):
        return subprocess.run(["bash", str(HERE / "proton-launch.sh"), *map(str, arguments)],
                              env=env if env is not None else self.env, cwd="/",
                              capture_output=True, text=True, timeout=60)

    def test_starts_the_exe_beside_data_win_with_proton_from_the_game_directory(self):
        result = self.run_launch(self.data)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(self.record.read_text())
        self.assertEqual(record["argv"], ["waitforexitandrun", str(self.exe)])
        self.assertEqual(record["cwd"], str(self.game))
        env = record["env"]
        self.assertEqual(env["STEAM_COMPAT_DATA_PATH"], str(self.home / "compatdata"))
        self.assertEqual(env["STEAM_COMPAT_CLIENT_INSTALL_PATH"], str(self.home / "steam-client"))
        self.assertEqual(env["STEAM_COMPAT_INSTALL_PATH"], str(self.game))
        self.assertEqual(env["STEAM_COMPAT_LIBRARY_PATHS"], str(self.game))
        # Proton starts a non-Steam game through umu.exe, not steam.exe.
        self.assertEqual(env["UMU_ID"], "umu-default")
        self.assertEqual(env["STORE"], "none")
        self.assertEqual(env["DISPLAY"], ":1")
        self.assertNotIn("WAYLAND_DISPLAY", env)
        self.assertTrue((self.home / "compatdata").is_dir())
        self.assertTrue((self.home / "steam-client").is_dir())

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
            ([self.data], {"HOME": ""}, "HOME must be an absolute path"),
            ([self.data], {"HOME": "relative"}, "HOME must be an absolute path"),
            ([self.data], {"HOME": str(self.home / "missing")}, "HOME is not a directory"),
            ([self.data], {"KORRI_PROTON": ""}, "KORRI_PROTON is not a Proton directory"),
            ([self.data], {"KORRI_PROTON": str(self.game)}, "KORRI_PROTON is not a Proton directory"),
        ]
        for arguments, changes, message in cases:
            with self.subTest(arguments=arguments, changes=changes):
                result = self.run_launch(*arguments, env=self.env | changes)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(message, result.stderr)
                self.assertFalse(self.record.exists())

    def test_refuses_data_win_without_the_exe_beside_it(self):
        self.exe.unlink()
        result = self.run_launch(self.data)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("MegaMaker.exe is missing", result.stderr)
        self.assertFalse(self.record.exists())


if __name__ == "__main__":
    unittest.main()
