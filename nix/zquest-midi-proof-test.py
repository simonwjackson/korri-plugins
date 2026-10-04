#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p 'python3.withPackages (ps: [ ps.numpy ps.pillow ])'
"""Integration checks against a privately supplied real quest, not a mock."""

import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

MODULE_PATH = Path(__file__).with_name("zquest-midi-proof.py")
spec = importlib.util.spec_from_file_location("midi_proof", MODULE_PATH)
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)
runtime_spec = importlib.util.spec_from_file_location(
    "midi_runtime", Path(__file__).with_name("zquest-midi-proof-runtime.py")
)
runtime = importlib.util.module_from_spec(runtime_spec)
runtime_spec.loader.exec_module(runtime)


class EditingProof(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="zquest-midi-test-")
        self.root = Path(self.directory.name)
        self.output = self.root / "outputs"
        self.before = INPUT.read_bytes()

    def tearDown(self):
        self.assertEqual(INPUT.read_bytes(), self.before)
        self.directory.cleanup()

    def run_proof(self, **changes):
        arguments = {
            "input_path": INPUT,
            "expected_hash": EXPECTED,
            "reader_root": READER,
            "output_dir": self.output,
            "slot": 0,
        }
        arguments.update(changes)
        with redirect_stdout(io.StringIO()):
            return proof.prove(**arguments)

    def test_real_roundtrip_and_single_slot_removal(self):
        self.run_proof()
        reader_type, ids, _, _ = proof.load_reader(READER)
        source = proof.read_midi(INPUT, reader_type, ids)
        copied = proof.read_midi(self.output / "roundtrip.qst", reader_type, ids)
        edited = proof.read_midi(self.output / "slot-0-removed.qst", reader_type, ids)
        self.assertEqual(source.b.data, copied.b.data)
        self.assertIsNone(edited.midis[0])
        before = proof.sections(source)
        after = proof.sections(edited)
        self.assertEqual(
            [key for key in before if before[key] != after[key]], [ids.MIDIS]
        )
        for slot in range(1, len(source.midis)):
            if source.midis[slot] is not None:
                self.assertEqual(vars(source.midis[slot]), vars(edited.midis[slot]))
        self.assertEqual(self.output.stat().st_mode & 0o777, 0o700)
        self.assertIn(
            "OTHER MEDIA AND RIGHTS REMAIN UNRESOLVED",
            (self.output / "receipt.txt").read_text(),
        )

    def test_bad_hash_rejected_before_creating_output(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.run_proof(expected_hash="0" * 64)
        self.assertFalse(self.output.exists())

    def test_slot_bounds_rejected(self):
        for slot in (-1, 252):
            with (
                self.subTest(slot=slot),
                self.assertRaisesRegex(ValueError, "between 0 and 251"),
            ):
                self.run_proof(slot=slot)
        self.assertFalse(self.output.exists())

    def test_empty_slot_rejected_without_output(self):
        reader_type, ids, _, _ = proof.load_reader(READER)
        source = proof.read_midi(INPUT, reader_type, ids)
        empty = next(i for i, midi in enumerate(source.midis) if midi is None)
        with self.assertRaisesRegex(ValueError, "already empty"):
            self.run_proof(slot=empty)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_not_overwritten(self):
        self.output.mkdir()
        marker = self.output / "marker"
        marker.write_text("preserve me")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.run_proof()
        self.assertEqual(marker.read_text(), "preserve me")
        self.assertEqual(list(self.output.iterdir()), [marker])

    def test_git_checkout_output_is_rejected(self):
        checkout = self.root / "checkout"
        checkout.mkdir()
        (checkout / ".git").write_text("gitdir: external-worktree-metadata")
        output = checkout / "candidate"
        with self.assertRaisesRegex(ValueError, "outside Git"):
            self.run_proof(output_dir=output)
        self.assertFalse(output.exists())

    def test_source_parent_output_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "source quest"):
            self.run_proof(output_dir=INPUT.parent)

    def test_native_result_requires_success_and_achieved_frame(self):
        # These three fields are present in the observed native result file.
        result = self.root / "proof.zplay.result.txt"
        result.write_text("frame: 6000\nsuccess: true\nstopped: true\n")
        self.assertEqual(runtime.replay_frame(result, 6000), 6000)
        for fields in (
            "frame: 5500\nsuccess: true\nstopped: true\n",
            "frame: 6000\nsuccess: false\nstopped: true\n",
            "frame: 6000\nsuccess: true\nstopped: false\n",
            "success: true\nstopped: true\n",
            "frame: unknown\nsuccess: true\nstopped: true\n",
        ):
            with self.subTest(fields=fields), self.assertRaises(RuntimeError):
                result.write_text(fields)
                runtime.replay_frame(result, 6000)

    def test_native_timeout_kills_descendants(self):
        script = self.root / "hang.py"
        script.write_text(
            "#!/usr/bin/env nix-shell\n"
            "#! nix-shell -i python3 -p python3\n"
            "from pathlib import Path\n"
            "import subprocess, sys, time\n"
            "if sys.argv[1] != 'child':\n"
            "    child = subprocess.Popen([sys.executable, __file__, 'child'])\n"
            "    Path(sys.argv[1]).write_text(str(child.pid))\n"
            "time.sleep(30)\n"
        )
        pid_file = self.root / "child-pid"
        with (
            (self.root / "timeout.log").open("w") as log,
            self.assertRaises(subprocess.TimeoutExpired),
        ):
            runtime.run_private_command(
                [sys.executable, str(script), str(pid_file)],
                cwd=self.root,
                env=os.environ,
                log=log,
                timeout=2,
            )
        status = Path(f"/proc/{int(pid_file.read_text())}/status")
        for _ in range(100):
            try:
                # An init-owned zombie is dead; it no longer runs or holds FDs.
                state = next(
                    line
                    for line in status.read_text().splitlines()
                    if line.startswith("State:")
                )
            except FileNotFoundError:
                return
            if "Z (zombie)" in state:
                return
            time.sleep(0.05)
        self.fail("Timed-out probe left a live descendant")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--reader-root", required=True, type=Path)
    args, remaining = parser.parse_known_args()
    INPUT = args.input.resolve(strict=True)
    EXPECTED = args.expected_sha256
    READER = args.reader_root.resolve(strict=True)
    if hashlib.sha256(INPUT.read_bytes()).hexdigest() != EXPECTED:
        parser.error("Fixture bytes differ from the supplied receipt")
    unittest.main(argv=[str(__file__), *remaining], verbosity=2)
