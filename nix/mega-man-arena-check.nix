# Package checks for the built Mega Man Arena plugin, against the Core
# contract of the korri input. Build for aarch64-linux on a build machine;
# nothing here downloads the game or Proton.
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
pkgs.runCommand "korri-mega-man-arena-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      pkgs.python3
    ];
  }
  ''
    mkdir -p work/plugins/mega-man-arena work/contracts/generated
    cp ${package}/plugin.ts work/plugins/mega-man-arena/plugin.ts
    cp ${../plugins/mega-man-arena/plugin.test.ts} work/plugins/mega-man-arena/plugin.test.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    (cd work && tsc --noEmit --strict --skipLibCheck --target ES2022 --module ESNext \
      --moduleResolution Bundler plugins/mega-man-arena/plugin.ts)
    (cd work/plugins/mega-man-arena && HOME="$TMPDIR" bun test plugin.test.ts)

    python3 - ${package} <<'PY'
    import json
    import subprocess
    import sys
    from pathlib import Path

    package = Path(sys.argv[1])
    manifest = json.loads((package / 'manifest.json').read_text())
    assert manifest['publisher'] == {'namespace': '@simonwjackson'}, manifest['publisher']
    assert manifest['sources'] == ['plugin.ts'], manifest['sources']
    assert manifest['services'] == {}, manifest['services']
    # @korri:proton reaches the runner as an artifact, not a required package.
    assert 'requires' not in manifest, manifest.get('requires')
    files = manifest['files']
    assert sorted(files) == ['game-unpack', 'proton-launch'], files
    assert sorted(manifest['packages']) == [
        'mega-man-arena-proton', 'mega-man-arena-unpack',
    ], manifest['packages']

    unpack = files['game-unpack']
    for arguments in ([], ['/nonexistent-work-dir'], ['/nonexistent-work-dir', '/nonexistent.zip']):
        result = subprocess.run([unpack, *arguments], capture_output=True)
        assert result.returncode == 1, (arguments, result)
        assert not result.stdout, result.stdout

    launch = Path(files['proton-launch'])
    assert launch.is_file(), launch
    PY
    touch "$out"
  ''
