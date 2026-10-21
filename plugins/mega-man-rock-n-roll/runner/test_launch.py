"""Run the real launcher with a recording program named godot2-runtime on its PATH."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).parent

# Records what the launcher handed the engine, then exits with a chosen status.
RECORDER = f"""#!{sys.executable}
import json, os, sys
with open(os.environ["RECORD"], "w") as record:
    json.dump({{"argv": sys.argv[1:], "cwd": os.getcwd(), "env": dict(os.environ)}}, record)
sys.exit(int(os.environ.get("RECORDER_STATUS", "0")))
"""


class LaunchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.game = root / "cache/mega-man-rock-n-roll/game/1.3"
        self.game.mkdir(parents=True)
        self.pack = self.game / "data.pck"
        self.pack.write_bytes(b"GDPC\n")
        self.home = root / "accounts/a/mega-man-rock-n-roll"
        self.home.mkdir(parents=True)
        tools = root / "bin"
        tools.mkdir()
        (tools / "godot2-runtime").write_text(RECORDER)
        (tools / "godot2-runtime").chmod(0o755)
        self.record = root / "record.json"
        self.env = {
            "PATH": f"{tools}:{os.environ['PATH']}",
            "RECORD": str(self.record),
            "HOME": str(self.home),
            "DISPLAY": ":1",
        }

    def run_launch(self, *arguments, env=None):
        return subprocess.run(["bash", str(HERE / "godot-launch.sh"), *map(str, arguments)],
                              env=env or self.env, cwd="/", capture_output=True, text=True,
                              timeout=60)

    def test_runs_the_pack_with_the_runtime_from_the_game_directory(self):
        result = self.run_launch(self.pack)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(self.record.read_text())
        self.assertEqual(record["argv"], ["-main_pack", str(self.pack)])
        self.assertEqual(record["cwd"], str(self.game))
        env = record["env"]
        self.assertEqual(env["HOME"], str(self.home))
        self.assertEqual(env["DISPLAY"], ":1")
        self.assertNotIn("WAYLAND_DISPLAY", env)

    def test_returns_the_engine_status(self):
        result = self.run_launch(self.pack, env=self.env | {"RECORDER_STATUS": "7"})
        self.assertEqual(result.returncode, 7, result.stderr)

    def test_missing_or_wrong_inputs_exit_2_before_the_engine(self):
        missing = self.game / "missing.pck"
        cases = [
            ([], {}, "usage"),
            ([self.pack, self.pack], {}, "usage"),
            (["data.pck"], {}, "not an absolute file"),
            ([missing], {}, "not an absolute file"),
            ([self.game], {}, "not an absolute file"),
            ([self.pack], {"HOME": ""}, "HOME must be an absolute path"),
            ([self.pack], {"HOME": "relative"}, "HOME must be an absolute path"),
            ([self.pack], {"HOME": str(self.home / "missing")}, "HOME is not a directory"),
        ]
        for arguments, changes, message in cases:
            with self.subTest(arguments=arguments, changes=changes):
                result = self.run_launch(*arguments, env=self.env | changes)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(message, result.stderr)
                self.assertFalse(self.record.exists())


if __name__ == "__main__":
    unittest.main()
