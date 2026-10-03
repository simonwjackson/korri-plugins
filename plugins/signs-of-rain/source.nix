{ pkgs, signsOfRainPackage }:
pkgs.runCommand "signs-of-rain-plugin-source" { } ''
  pack=${signsOfRainPackage}/share/signs-of-rain/signs-of-rain.pck
  test -f "$pack"
  hash=$(sha256sum "$pack" | cut -d ' ' -f 1)
  mkdir -p "$out"
  cp ${./plugin.ts.in} "$out/plugin.ts"
  substituteInPlace "$out/plugin.ts" --replace-fail '@PACK_SHA256@' "$hash"
''
