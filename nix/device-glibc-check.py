"""The native engines must use Korri's libc to load device graphics drivers."""

import json
from pathlib import Path
import re
import subprocess
import sys

package, engine, expected_glibc, patchelf = sys.argv[1:]
manifest = json.loads((Path(package) / "manifest.json").read_text())
if engine == "2ship":
    launcher = Path(manifest["files"]["2ship"]).read_text()
    wrapper = Path(re.search(r"/nix/store/[a-zA-Z0-9._+-]+/bin/2s2h", launcher)[0])
    native = Path(re.search(r'exec -a "\$0" "([^"]+)"', wrapper.read_text())[1])
elif engine == "opengoal":
    native = Path(manifest["files"]["opengoal"])
elif engine == "godot2-runtime":
    native = Path(manifest["packages"][engine]) / "bin/godot2-runtime"
else:
    raise ValueError(f"Unknown engine: {engine}")
interpreter = subprocess.check_output(
    [patchelf, "--print-interpreter", str(native)], text=True
).strip()
assert Path(interpreter).parent == Path(expected_glibc) / "lib", (
    f"{engine} uses {interpreter}, not Korri's {expected_glibc}; "
    "device Mesa drivers can require GLIBC_ABI_GNU2_TLS"
)
print(f"{engine}: native interpreter uses Korri's glibc: {interpreter}")
