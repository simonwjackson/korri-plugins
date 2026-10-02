{
  pkgs,
  package,
  tools,
  contract,
  hostPackage,
  korridPackage,
}:
let
  contractSource = builtins.path {
    path = contract;
    name = "korrid.ts";
  };
  tsconfig = pkgs.writeText "opengoal-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/opengoal/plugin.ts" ];
    }
  );
  argvProgram = pkgs.writeShellScript "opengoal-argv" ''
    printf '%s\0' "$@"
  '';
in
pkgs.runCommand "korri-opengoal-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      pkgs.python3
    ];
  }
  ''
    mkdir -p work/plugins/opengoal work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/opengoal/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./opengoal-check.ts} work/nix/opengoal-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/opengoal-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin ${korridPackage}/bin/korrid ${argvProgram}
    python3 ${./opengoal-prepare-check.py} ${../plugins/opengoal/prepare.py} ${tools}
    touch "$out"
  ''
