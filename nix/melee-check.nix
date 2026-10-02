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
  recordArguments = pkgs.writeShellScript "record-melee-arguments" ''
    printf '%s\0' "$@"
  '';
  tsconfig = pkgs.writeText "melee-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/melee-pc/plugin.ts" ];
    }
  );
in
pkgs.runCommand "korri-melee-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      pkgs.python3
    ];
  }
  ''
    mkdir -p work/plugins/melee-pc work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/melee-pc/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./melee-check.ts} work/nix/melee-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/melee-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin \
      ${korridPackage}/bin/korrid \
      ${recordArguments}
    python3 ${./melee-runtime-check.py} ${package} ${pkgs.stdenv.hostPlatform.system}
    touch "$out"
  ''
