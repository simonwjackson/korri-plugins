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
  tsconfig = pkgs.writeText "2ship-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/2ship/plugin.ts" ];
    }
  );
  probe = pkgs.writeShellScript "2ship-launch-probe" ''
    ${pkgs.coreutils}/bin/printf '%s\n' "$PWD" "$SHIP_HOME" "$@"
  '';
in
pkgs.runCommand "korri-2ship-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
    ];
  }
  ''
    mkdir -p work/plugins/2ship work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/2ship/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./2ship-check.ts} work/nix/2ship-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/2ship-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin \
      ${korridPackage}/bin/korrid ${probe}
    touch "$out"
  ''
