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
  recordArguments = pkgs.writeShellScript "record-actraiser-launch" ''
    printf '%s\0' "$@"
    printf '%s\0' "AR_USER_DATA_DIR=$AR_USER_DATA_DIR"
  '';
  tsconfig = pkgs.writeText "actraiser-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/actraiser/plugin.ts" ];
    }
  );
in
pkgs.runCommand "korri-actraiser-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
    ];
  }
  ''
    mkdir -p work/plugins/actraiser work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/actraiser/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./actraiser-check.ts} work/nix/actraiser-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/actraiser-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin \
      ${korridPackage}/bin/korrid \
      ${recordArguments}
    touch "$out"
  ''
