{ pkgs }:
let
  system = pkgs.stdenv.hostPlatform.system;
in
assert builtins.elem system [
  "x86_64-linux"
  "aarch64-linux"
];
pkgs.runCommand "opengoal-plugin-source-${system}" { } ''
  mkdir -p "$out"
  cp ${./plugin.ts} "$out/plugin.ts"
  # The native package and its accepted prepared-code identities share one target.
  # This generates TS source, not precompiled plugin code or a runtime probe.
  substituteInPlace "$out/plugin.ts" \
    --replace-fail 'const system = "x86_64-linux"' 'const system = "${system}"'
''
