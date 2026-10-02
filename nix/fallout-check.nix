{
  pkgs,
  package,
  name,
  program,
  contract,
  hostPackage,
  korridPackage,
}:
let
  contractSource = builtins.path {
    path = contract;
    name = "korrid.ts";
  };
in
pkgs.runCommand "korri-${name}-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
    ];
  }
  ''
    mkdir -p work/plugins/${name} work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/${name}/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./fallout-check.ts} work/nix/fallout-check.ts
    cd work
    tsc --noEmit --strict --skipLibCheck --target ES2022 --module ESNext \
      --moduleResolution Bundler plugins/${name}/plugin.ts
    bun nix/fallout-check.ts ${package} ${name} ${program} \
      ${toString (if pkgs.stdenv.hostPlatform.isAarch64 then 183 else 62)} \
      ${hostPackage}/bin/korri-plugin ${korridPackage}/bin/korrid \
      ${pkgs.coreutils}/bin/pwd
    touch "$out"
  ''
