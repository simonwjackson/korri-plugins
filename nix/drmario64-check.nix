{
  pkgs,
  package,
  engine,
  contract,
  hostPackage,
  korridPackage,
}:
let
  contractSource = builtins.path {
    path = contract;
    name = "korrid.ts";
  };
  tsconfig = pkgs.writeText "drmario64-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/drmario64/plugin.ts" ];
    }
  );
  probe = pkgs.writeShellScript "drmario64-launch-probe" ''
    ${pkgs.coreutils}/bin/printf '%s\n' "$PWD" "$APP_FOLDER_PATH" "$@"
  '';
in
pkgs.runCommand "korri-drmario64-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      pkgs.python3
      pkgs.patch
    ];
    allowSubstitutes = false;
    preferLocalBuild = true;
  }
  ''
    python3 ${./drmario64-save-check.py} ${engine.src} \
      ${pkgs.llvmPackages_19.stdenv.cc}/bin/clang++ ${./drmario64-save-check.cpp} \
      ${../plugins/drmario64/native-launch.patch} ${../plugins/drmario64/native-shutdown.patch}
    mkdir -p work/plugins/drmario64 work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/drmario64/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./drmario64-check.ts} work/nix/drmario64-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/drmario64-check.ts ${package} \
      ${hostPackage}/bin/korri-plugin \
      ${korridPackage}/bin/korrid ${probe} ${engine}/libexec/drmario64_recomp
    touch "$out"
  ''
