# Package checks for the built Mega Man Rock N Roll plugin, against the Core
# contract of the korri input. The release and runner fields need a Core with
# ADR 0012 and ADR 0013 (see the plugin README). Build for the target system on
# a build machine; nothing here downloads the game or the FEX rootfs.
{
  pkgs,
  package,
  contract,
}:
let
  contractSource = builtins.path {
    path = contract;
    name = "korrid.ts";
  };
  isAarch64 = pkgs.stdenv.hostPlatform.isAarch64;
in
pkgs.runCommand "korri-mega-man-rock-n-roll-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      pkgs.python3
    ];
  }
  ''
    mkdir -p work/plugins/mega-man-rock-n-roll work/contracts/generated
    cp ${package}/plugin.ts work/plugins/mega-man-rock-n-roll/plugin.ts
    cp ${../plugins/mega-man-rock-n-roll/plugin.test.ts} work/plugins/mega-man-rock-n-roll/plugin.test.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    (cd work && tsc --noEmit --strict --skipLibCheck --target ES2022 --module ESNext \
      --moduleResolution Bundler plugins/mega-man-rock-n-roll/plugin.ts)
    (cd work/plugins/mega-man-rock-n-roll && HOME="$TMPDIR" bun test plugin.test.ts)

    python3 - ${package} ${if isAarch64 then "1" else "0"} <<'PY'
    import json
    import os
    from pathlib import Path
    import re
    import struct
    import subprocess
    import sys
    import tempfile

    package = Path(sys.argv[1])
    run_fex = sys.argv[2] == "1"
    manifest = json.loads((package / 'manifest.json').read_text())
    assert manifest['publisher'] == {'namespace': '@simonwjackson'}, manifest['publisher']
    assert manifest['sources'] == ['plugin.ts'], manifest['sources']
    assert manifest['services'] == {}, manifest['services']
    # No other publisher's package: @korri:fex is used only for its rootfs artifact.
    assert 'requires' not in manifest, manifest.get('requires')
    files = manifest['files']
    assert sorted(files) == ['fex-config', 'fex-launch', 'game-unpack'], files
    assert (Path(files['fex-config']) / 'Config.json').is_file(), files['fex-config']

    unpack = files['game-unpack']
    for arguments in ([], ['/nonexistent-work-dir'], ['/nonexistent-work-dir', '/nonexistent.zip']):
        result = subprocess.run([unpack, *arguments], capture_output=True)
        assert result.returncode == 1, (arguments, result)
        assert not result.stdout, result.stdout

    launch = files['fex-launch']
    # The bundled FEX is first on the launcher's PATH.
    search = re.search(r'export PATH="([^"]*)"', Path(launch).read_text()).group(1)
    interpreter = Path(search.split(':')[0]) / 'FEX'
    assert interpreter.is_file() and os.access(interpreter, os.X_OK), search
    assert subprocess.run([launch], capture_output=True).returncode == 2
    game = Path(tempfile.mkdtemp())
    (game / 'data.pck').write_bytes(b'pack')
    (game / 'MegaMan_RocknRoll').write_bytes(b'elf')
    runtime = {
        'HOME': tempfile.mkdtemp(),
        'KORRI_FEX_CONFIG': files['fex-config'],
        'KORRI_FEX_ROOTFS': '/nonexistent/fex/rootfs/archlinux-2026-01-08-mesa-26.1.2',
    }
    result = subprocess.run([launch, str(game)], env=runtime, capture_output=True)
    assert result.returncode == 2, result.stderr
    assert b'KORRI_FEX_ROOTFS is not a directory' in result.stderr, result.stderr

    if run_fex:
        # The bundled FEX runs an x86_64 game executable with this plugin's
        # config. This hand-assembled static ELF writes one line and exits 0,
        # so it needs nothing from a rootfs.
        message = b'x86_64 game ran\n'
        code = (bytes.fromhex('b801000000bf01000000488d35') + struct.pack('<i', 16)
                + b'\xba' + struct.pack('<I', len(message))
                + bytes.fromhex('0f05b83c00000031ff0f05') + message)
        base, offset = 0x400000, 64 + 56
        elf = (b'\x7fELF' + bytes([2, 1, 1, 0]) + bytes(8)
               + struct.pack('<HHIQQQIHHHHHH', 2, 0x3e, 1, base + offset, 64, 0, 0, 64, 56, 1, 0, 0, 0)
               + struct.pack('<IIQQQQQQ', 1, 5, 0, base, base, offset + len(code), offset + len(code), 0x1000)
               + code)
        (game / 'MegaMan_RocknRoll').write_bytes(elf)
        runtime['KORRI_FEX_ROOTFS'] = tempfile.mkdtemp()
        result = subprocess.run([launch, str(game)], env=runtime, capture_output=True, timeout=120)
        assert result.returncode == 0, result
        assert result.stdout == message, result
    PY
    touch "$out"
  ''
