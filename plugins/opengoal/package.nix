{ pkgs }:
let
  inherit (pkgs) lib;
  version = "0.3.8";
  src = pkgs.fetchurl {
    url = "https://github.com/open-goal/jak-project/releases/download/v${version}/opengoal-linux-v${version}.tar.gz";
    hash = "sha256-yY/HE+gx9l8pVMaA9L5PK8AlnDCPlTgoTAb+6UKbCJ0=";
  };
  licenseFile = pkgs.fetchurl {
    url = "https://raw.githubusercontent.com/open-goal/jak-project/v${version}/LICENSE";
    hash = "sha256-ZJg8IUge6rhenfh05LRSv235AFu19CL7FUcFqZMezlY=";
  };
  runtimeLibraries = map lib.getLib [
    pkgs.libglvnd
    pkgs.libpulseaudio
    pkgs.libx11
    pkgs.libxcursor
    pkgs.libxext
    pkgs.libxfixes
    pkgs.libxi
    pkgs.libxrandr
    pkgs.gtk3
    pkgs.vulkan-loader
  ];
  common = {
    inherit version src;
    sourceRoot = ".";
    nativeBuildInputs = [ pkgs.autoPatchelfHook ];
    buildInputs = [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
    ];
    dontConfigure = true;
    dontBuild = true;
    dontStrip = true;
    doInstallCheck = true;
    meta = {
      homepage = "https://opengoal.dev/";
      license = lib.licenses.isc;
      platforms = [ "x86_64-linux" ];
      sourceProvenance = [ lib.sourceTypes.binaryNativeCode ];
    };
  };
in
{
  runtime =
    if pkgs.stdenv.hostPlatform.isAarch64 then
      import ./arm-package.nix { inherit pkgs; }
    else
      pkgs.stdenvNoCC.mkDerivation (
        common
        // {
          pname = "opengoal-runtime";
          # SDL is statically linked, but its X11, audio and GL backends use dlopen.
          # Keep these in the ELF RUNPATH even though they are absent from DT_NEEDED.
          buildInputs = common.buildInputs ++ runtimeLibraries;
          runtimeDependencies = runtimeLibraries;
          # SDL's .note.dlopen also lists optional Steam storage and PowerVR GLES.
          # Neither is used by OpenGOAL's desktop OpenGL runtime.
          autoPatchelfIgnoreMissingDeps = [
            "libsteam_api.so"
            "libGLES_CM.so.1"
          ];
          installPhase = ''
            runHook preInstall
            install -Dm755 gk "$out/libexec/opengoal/gk"
            install -Dm644 ${licenseFile} "$out/share/licenses/opengoal/LICENSE"
            mkdir -p "$out/bin" "$out/share/opengoal/data"
            cp -r data/game data/custom_assets data/launcher data/log "$out/share/opengoal/data/"
            ln -s ../../share/opengoal/data "$out/libexec/opengoal/data"
            ln -s ../libexec/opengoal/gk "$out/bin/gk"
            # No launcher wrapper: pass --proj-path to a prepared writable data tree.
            # HOME/XDG_CONFIG_HOME and upstream save paths remain unchanged.
            runHook postInstall
          '';
          installCheckPhase = ''
            runHook preInstallCheck
            "$out/bin/gk" --version
            "$out/bin/gk" --help > help.txt
            grep -F -- --proj-path help.txt
            test ! -e "$out/bin/extractor"
            test ! -e "$out/bin/goalc"
            test ! -e "$out/share/opengoal/data/goal_src"
            runHook postInstallCheck
          '';
          meta = common.meta // {
            description = "OpenGOAL native runtime without retail game data or preparation tools";
            mainProgram = "gk";
          };
        }
      );

  tools = pkgs.stdenvNoCC.mkDerivation (
    common
    // {
      pname = "opengoal-tools";
      installPhase = ''
        runHook preInstall
        install -Dm755 extractor "$out/libexec/opengoal/extractor"
        install -Dm755 goalc "$out/libexec/opengoal/goalc"
        install -Dm644 ${licenseFile} "$out/share/licenses/opengoal/LICENSE"
        mkdir -p "$out/bin" "$out/share/opengoal"
        cp -r data "$out/share/opengoal/data"
        ln -s ../../share/opengoal/data "$out/libexec/opengoal/data"
        ln -s ../libexec/opengoal/extractor "$out/bin/extractor"
        ln -s ../libexec/opengoal/goalc "$out/bin/goalc"
        # Off-device only: copy data to a writable directory, then explicitly run
        # extractor --proj-path DATA --extract --decompile --compile --game GAME ISO.
        # Do not use --all: upstream also tries to launch gk in that mode.
        runHook postInstall
      '';
      installCheckPhase = ''
        runHook preInstallCheck
        "$out/bin/extractor" --help > extractor-help.txt
        "$out/bin/goalc" --help > goalc-help.txt
        grep -F -- --proj-path extractor-help.txt
        test -d "$out/share/opengoal/data/goal_src"
        test ! -e "$out/bin/gk"
        runHook postInstallCheck
      '';
      meta = common.meta // {
        description = "OpenGOAL off-device extraction and GOAL compilation tools";
        mainProgram = "extractor";
      };
    }
  );
}
