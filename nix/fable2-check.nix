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
  tsconfig = pkgs.writeText "fable2-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/fable-ii-recomp/plugin.ts" ];
    }
  );
  handoff = pkgs.writeScript "fable2-handoff" (
    builtins.replaceStrings [ "@python@" ] [ "${pkgs.python3}/bin/python3" ] (
      builtins.readFile ./fable2-handoff.py
    )
  );
  probe = pkgs.writeShellScript "fable2-launch-probe" ''
    ${pkgs.coreutils}/bin/printf '%s\n' "$PWD" "$@"
  '';
in
pkgs.runCommand "korri-fable-ii-recomp-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      pkgs.python3
    ];
    allowSubstitutes = false;
  }
  ''
    mkdir -p work/plugins/fable-ii-recomp work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/fable-ii-recomp/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./fable2-check.ts} work/nix/fable2-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/fable2-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin ${korridPackage}/bin/korrid ${probe}
    python3 -I ${./fable2-launch-check.py} ${package} ${handoff}
    touch "$out"
  ''
