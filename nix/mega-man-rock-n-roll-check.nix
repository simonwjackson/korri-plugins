# Package checks for the built Mega Man Rock N Roll plugin, against the Core
# contract of the korri input. The release field needs a Core with ADR 0012
# and ADR 0013 (see the plugin README). Build for the target system on a build
# machine; nothing here downloads the game.
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

    python3 - ${package} <<'PY'
    import json
    import os
    from pathlib import Path
    import re
    import subprocess
    import sys
    import tempfile

    package = Path(sys.argv[1])
    manifest = json.loads((package / 'manifest.json').read_text())
    assert manifest['publisher'] == {'namespace': '@simonwjackson'}, manifest['publisher']
    assert manifest['sources'] == ['plugin.ts'], manifest['sources']
    assert manifest['services'] == {}, manifest['services']
    # No other publisher's package and no artifact besides the game's ZIP.
    assert 'requires' not in manifest, manifest.get('requires')
    files = manifest['files']
    assert sorted(files) == ['game-unpack', 'godot-launch'], files
    assert sorted(manifest['packages']) == [
        'godot2-runtime', 'mega-man-rock-n-roll-godot', 'mega-man-rock-n-roll-unpack',
    ], manifest['packages']
    runtime_package = Path(manifest['packages']['godot2-runtime'])
    for notice in ('LICENSE.txt', 'COPYRIGHT.txt'):
        assert (runtime_package / 'share/licenses/godot2-runtime' / notice).is_file(), notice

    unpack = files['game-unpack']
    for arguments in ([], ['/nonexistent-work-dir'], ['/nonexistent-work-dir', '/nonexistent.zip']):
        result = subprocess.run([unpack, *arguments], capture_output=True)
        assert result.returncode == 1, (arguments, result)
        assert not result.stdout, result.stdout

    launch = files['godot-launch']
    # The bundled engine is first on the launcher's PATH.
    search = re.search(r'export PATH="([^"]*)"', Path(launch).read_text()).group(1)
    engine = Path(search.split(':')[0]) / 'godot2-runtime'
    assert engine.is_file() and os.access(engine, os.X_OK), search
    assert engine.resolve() == (runtime_package / 'bin/godot2-runtime').resolve(), engine

    home = tempfile.mkdtemp()
    game = Path(tempfile.mkdtemp())
    pack = game / 'data.pck'
    pack.write_bytes(b'not a Godot pack\n')
    refusals = [
        ([], {'HOME': home}, b'usage'),
        ([str(game / 'missing.pck')], {'HOME': home}, b'not an absolute file'),
        (['data.pck'], {'HOME': home}, b'not an absolute file'),
        ([str(pack)], {}, b'HOME must be an absolute path'),
        ([str(pack)], {'HOME': home + '/missing'}, b'HOME is not a directory'),
    ]
    for arguments, env, message in refusals:
        result = subprocess.run([launch, *arguments], env=env, capture_output=True)
        assert result.returncode == 2, (arguments, env, result)
        assert message in result.stderr, (arguments, result.stderr)

    # The built engine executes on this system. Godot 2.1.4 prints its banner
    # and usage for -h and exits 255.
    result = subprocess.run([engine, '-h'], env={'HOME': home}, capture_output=True, timeout=60)
    assert result.returncode == 255, result
    output = result.stdout + result.stderr
    assert b'Godot Engine v2.1.4.stable' in output, output
    assert b'Request Fullscreen' in output, output

    # Through the launcher, the engine opens the pack before any display and
    # refuses one that is not a Godot pack.
    result = subprocess.run([launch, str(pack)], env={'HOME': home}, capture_output=True, timeout=60)
    assert result.returncode == 255, result
    assert b"Couldn't load game path" in result.stdout + result.stderr, result
    PY
    touch "$out"
  ''
