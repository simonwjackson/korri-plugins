{
  pkgs,
  package,
  engine,
  contract,
  hostPackage,
  korridPackage,
}:
let
  fixtures = import ./zquest-fixtures.nix { inherit pkgs engine; };
  contractSource = builtins.path {
    path = contract;
    name = "korrid.ts";
  };
  recordArguments = pkgs.writeShellScript "record-zquest-arguments" ''
    printf '%s\0' "$@"
  '';
  tsconfig = pkgs.writeText "zquest-plugin-tsconfig.json" (
    builtins.toJSON {
      compilerOptions = {
        target = "ES2022";
        module = "ESNext";
        moduleResolution = "Bundler";
        strict = true;
        noEmit = true;
        skipLibCheck = true;
      };
      include = [ "plugins/zquest-classic/plugin.ts" ];
    }
  );
in
pkgs.runCommand "korri-zquest-classic-plugin-check"
  {
    nativeBuildInputs = [
      pkgs.bun
      pkgs.typescript
      (pkgs.python3.withPackages (python: [ python.pillow ]))
      pkgs.xvfb-run
      pkgs.xdotool
    ];
    LIBGL_ALWAYS_SOFTWARE = "1";
    GALLIUM_DRIVER = "llvmpipe";
    LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.libGL
      pkgs.libGLU
      pkgs.mesa
    ];
    LIBGL_DRIVERS_PATH = "${pkgs.mesa}/lib/dri";
    __GLX_VENDOR_LIBRARY_NAME = "mesa";
  }
  ''
    export HOME="$TMPDIR/home"
    export XDG_CACHE_HOME="$HOME/.cache"
    mkdir -p "$XDG_CACHE_HOME" work/plugins/zquest-classic work/contracts/generated work/nix
    cp ${package}/plugin.ts work/plugins/zquest-classic/plugin.ts
    cp ${contractSource} work/contracts/generated/korrid.ts
    cp ${./zquest-check.ts} work/nix/zquest-check.ts
    cp ${tsconfig} work/tsconfig.json
    cd work
    tsc --project tsconfig.json
    bun nix/zquest-check.ts ${package} ${hostPackage}/bin/korri-plugin \
      ${korridPackage}/bin/korrid ${recordArguments}
    xvfb-run -a -s '-screen 0 800x600x24' python3 ${./zquest-runtime-check.py} \
      ${package} ${engine} ${korridPackage}/bin/korrid ${pkgs.stdenv.hostPlatform.system} ${fixtures}
    touch "$out"
  ''
