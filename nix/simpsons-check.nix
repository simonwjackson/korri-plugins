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
  tsconfig = pkgs.writeText "simpsons-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/the-simpsons-game/plugin.ts" ];
    }
  );
  handoff = pkgs.writeScript "simpsons-handoff" (
    builtins.replaceStrings [ "@python@" ] [ "${pkgs.python3}/bin/python3" ] (
      builtins.readFile ./simpsons-handoff.py
    )
  );
  probe = pkgs.writeShellScript "simpsons-launch-probe" ''
    ${pkgs.coreutils}/bin/printf '%s\n' "$PWD" "$@"
  '';
in
pkgs.runCommand "korri-the-simpsons-game-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      pkgs.python3
    ];
  }
  ''
    mkdir -p work/plugins/the-simpsons-game work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/the-simpsons-game/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./simpsons-check.ts} work/nix/simpsons-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/simpsons-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin ${korridPackage}/bin/korrid ${probe}
    python3 -I ${./simpsons-launch-check.py} ${package} ${handoff}
    touch "$out"
  ''
