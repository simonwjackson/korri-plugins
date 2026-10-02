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
  tsconfig = pkgs.writeText "smw-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/super-mario-world/plugin.ts" ];
    }
  );
  probe = pkgs.writeShellScript "smw-launch-probe" ''
    ${pkgs.coreutils}/bin/printf '%s\n' "$PWD" "$@"
  '';
in
pkgs.runCommand "korri-super-mario-world-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
    ];
  }
  ''
    mkdir -p work/plugins/super-mario-world work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/super-mario-world/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./smw-check.ts} work/nix/smw-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/smw-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin \
      ${korridPackage}/bin/korrid ${probe}
    touch "$out"
  ''
