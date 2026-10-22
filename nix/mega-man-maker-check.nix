# Package checks for the built Mega Man Maker plugin, against the Core
# contract of the korri input: strict TypeScript, plugin.test.ts, the
# generated manifest, Core's seed admission, and the packaged launch callback
# through Core's real sandbox and executor with a recording program. Build
# for the target system on a build machine; nothing here downloads the game
# or Proton, or starts Wine.
{
  pkgs,
  package,
  contract,
  hostPackage,
  korridPackage,
}:
let
  contractSource = builtins.path {
    path = contract;
    name = "korrid.ts";
  };
  probe = pkgs.writeShellScript "mega-man-maker-launch-probe" ''
    ${pkgs.coreutils}/bin/printf '%s\n' "$PWD" "$HOME" "$KORRI_PROTON" "$@"
  '';
in
pkgs.runCommand "korri-mega-man-maker-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
    ];
  }
  ''
    mkdir -p work/plugins/mega-man-maker work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/mega-man-maker/plugin.ts
    cp ${../plugins/mega-man-maker/plugin.test.ts} work/plugins/mega-man-maker/plugin.test.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./mega-man-maker-check.ts} work/nix/mega-man-maker-check.ts
    cd work
    tsc --noEmit --strict --skipLibCheck --target ES2022 --module ESNext \
      --moduleResolution Bundler plugins/mega-man-maker/plugin.ts
    (cd plugins/mega-man-maker && HOME="$TMPDIR" bun test plugin.test.ts)
    HOME="$TMPDIR" bun nix/mega-man-maker-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin ${korridPackage}/bin/korrid ${probe}
    touch "$out"
  ''
