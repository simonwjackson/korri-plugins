#!/usr/bin/env nix
#! nix shell nixpkgs#python3 --command python3
"""Regression for a colorful startup logo followed by a blank game window."""

import importlib.util
import sys

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("opengoal_owned_check", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

assert not module.has_late_rendered_frames([1024, 1, 1])
assert not module.has_late_rendered_frames([1024, 1024, 1])
assert not module.has_late_rendered_frames([1, 256, 1024])
assert not module.has_late_rendered_frames([1024])
assert module.has_late_rendered_frames([1, 1024, 2048])
print("OpenGOAL frame acceptance requires both late samples, not an early logo")
