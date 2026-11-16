{
  pkgs,
  package,
  contract,
  hostPackage,
}:
let
  contractSource = builtins.path {
    path = contract;
    name = "korrid.ts";
  };
  tsconfig = pkgs.writeText "hashlink-fill-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/hashlink-fill/plugin.ts" ];
    }
  );
in
pkgs.runCommand "korri-hashlink-fill-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
    ];
  }
  ''
    mkdir -p work/plugins/hashlink-fill work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/hashlink-fill/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./hashlink-fill-check.ts} work/nix/hashlink-fill-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/hashlink-fill-check.ts ${package} ${hostPackage}/bin/korri-plugin
    touch "$out"
  ''
