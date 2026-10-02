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
  recordArguments = pkgs.writeShellScript "record-nocturne-arguments" ''
    printf '%s\0' "$@"
  '';
  tsconfig = pkgs.writeText "nocturne-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/nocturne/plugin.ts" ];
    }
  );
in
pkgs.runCommand "korri-nocturne-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      pkgs.python3
    ];
  }
  ''
    mkdir -p work/plugins/nocturne work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/nocturne/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./nocturne-check.ts} work/nix/nocturne-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/nocturne-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin \
      ${korridPackage}/bin/korrid \
      ${recordArguments}
    python3 ${./nocturne-runtime-check.py} ${package} ${pkgs.stdenv.hostPlatform.system}
    touch "$out"
  ''
