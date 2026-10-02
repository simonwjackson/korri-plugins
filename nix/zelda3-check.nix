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
  recordArguments = pkgs.writeShellScript "record-zelda3-arguments" ''
    printf '%s\0' "$@"
  '';
  tsconfig = pkgs.writeText "zelda3-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/zelda3/plugin.ts" ];
    }
  );
in
pkgs.runCommand "korri-zelda3-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      pkgs.python3
    ];
  }
  ''
    mkdir -p work/plugins/zelda3 work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/zelda3/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./zelda3-check.ts} work/nix/zelda3-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/zelda3-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin \
      ${korridPackage}/bin/korrid \
      ${recordArguments}
    python3 ${./zelda3-runtime-check.py} ${package} ${pkgs.stdenv.hostPlatform.system}
    touch "$out"
  ''
