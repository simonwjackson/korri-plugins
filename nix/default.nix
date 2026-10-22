{
  korri,
  nixpkgs,
  flake-utils,
  skate3,
  signs-of-rain,
  nocturne-encore,
}:
flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (
  system:
  let
    pkgs = import nixpkgs {
      inherit system;
      config.allowUnfreePredicate =
        pkg:
        builtins.elem (nixpkgs.lib.getName pkg) [
          "nocturnerecomp"
          "2ship2harkinian"
          "melee-pc"
        ];
    };
    mkPlugin = korri.lib.${system}.mkPlugin { inherit pkgs; };
    opengoalPackages = import ../plugins/opengoal/package.nix { inherit pkgs; };
    verifyOpengoal = pkgs.writeShellApplication {
      name = "verify-opengoal";
      runtimeInputs = [
        pkgs.xorg.xorgserver
        pkgs.xorg.xauth
        pkgs.imagemagick
        pkgs.pulseaudio
        pkgs.dbus
      ];
      text = ''
        export LIBGL_DRIVERS_PATH=${pkgs.mesa}/lib/dri
        export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [ pkgs.mesa ]}
        export __GLX_VENDOR_LIBRARY_NAME=mesa
        exec dbus-run-session -- ${pkgs.python3}/bin/python3 ${./opengoal-owned-check.py} \
          ${packages.korri-plugin-opengoal} ${korri.packages.${system}.korrid}/bin/korrid "$@"
      '';
    };
    prepareOpengoal = pkgs.writeShellApplication {
      name = "prepare-opengoal";
      text = ''
        exec ${pkgs.python3}/bin/python3 ${../plugins/opengoal/prepare.py} ${opengoalPackages.tools} "$@"
      '';
    };
    packages =
      pkgs.lib.optionalAttrs (system == "x86_64-linux") {
        # The x86 tools cross-compile either instruction set off-device.
        opengoal-tools = opengoalPackages.tools;
      }
      // {
        opengoal = opengoalPackages.runtime;
        korri-plugin-opengoal = mkPlugin {
          publisher.namespace = "@simonwjackson";
          source = import ../plugins/opengoal/source.nix { inherit pkgs; };
          plugin =
            _:
            import ../plugins/opengoal/plugin.nix {
              opengoalRuntime = opengoalPackages.runtime;
            };
        };
        # The native flake's default is the prebuilt release on x86_64 and the
        # source build on aarch64. Native builds run on builders, never devices.
        korri-plugin-skate-3 = mkPlugin {
          publisher.namespace = "@simonwjackson";
          source = ../plugins/skate-3;
          plugin =
            _:
            import ../plugins/skate-3/plugin.nix {
              skate3Package = skate3.packages.${system}.default;
            };
        };
      }
      // pkgs.lib.optionalAttrs (system == "aarch64-linux") {
        korri-plugin-mega-man-arena = megaManArenaPlugin;
      };
    actraiserPackage = import ../plugins/actraiser/package.nix { inherit pkgs; };
    actraiserPlugin =
      (mkPlugin {
        publisher.namespace = "@simonwjackson";
        source = ../plugins/actraiser;
        plugin = _: import ../plugins/actraiser/plugin.nix { inherit actraiserPackage; };
      }).overrideAttrs
        {
          allowSubstitutes = false;
          preferLocalBuild = true;
        };
    smwPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/super-mario-world;
      plugin = _: import ../plugins/super-mario-world/plugin.nix { inherit pkgs; };
    };
    signsOfRainPackage = signs-of-rain.packages.${system}.signs-of-rain;
    signsOfRainPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = import ../plugins/signs-of-rain/source.nix {
        inherit pkgs signsOfRainPackage;
      };
      plugin = _: import ../plugins/signs-of-rain/plugin.nix { inherit signsOfRainPackage; };
    };
    zquestEngine = import ../plugins/zquest-classic/package.nix { inherit pkgs; };
    zquestLauncher = import ../plugins/zquest-classic/launcher.nix {
      inherit pkgs;
      engine = zquestEngine;
    };
    zquestPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = pkgs.lib.fileset.toSource {
        root = ../plugins/zquest-classic;
        fileset = ../plugins/zquest-classic/plugin.ts;
      };
      plugin = _: import ../plugins/zquest-classic/plugin.nix { launcher = zquestLauncher; };
    };
    # The ZIP is a korrid-downloaded artifact (Korri ADR 0013), not in the closure.
    megaManRockNRollPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = pkgs.lib.fileset.toSource {
        root = ../plugins/mega-man-rock-n-roll;
        fileset = ../plugins/mega-man-rock-n-roll/plugin.ts;
      };
      plugin = _: import ../plugins/mega-man-rock-n-roll/plugin.nix { inherit pkgs; };
    };
    # The ZIP is a korrid-downloaded artifact (Korri ADR 0013), not in the
    # closure. Its runner needs @korri:proton's Proton-CachyOS, an arm64-only
    # build, so the plugin exists for aarch64-linux only.
    megaManArenaPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = pkgs.lib.fileset.toSource {
        root = ../plugins/mega-man-arena;
        fileset = ../plugins/mega-man-arena/plugin.ts;
      };
      plugin = _: import ../plugins/mega-man-arena/plugin.nix { inherit pkgs; };
    };
    # The ZIP and Proton are korrid-downloaded artifacts (Korri ADR 0012/0013).
    megaManMakerPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = pkgs.lib.fileset.toSource {
        root = ../plugins/mega-man-maker;
        fileset = ../plugins/mega-man-maker/plugin.ts;
      };
      plugin = _: import ../plugins/mega-man-maker/plugin.nix { inherit pkgs; };
    };
    # The engines use the Sustainable Use License. Keep permission scoped to
    # these two packages instead of enabling every unfree dependency.
    falloutPkgs = import nixpkgs {
      inherit system;
      config.allowUnfreePredicate =
        pkg:
        builtins.elem (pkgs.lib.getName pkg) [
          "fallout-ce"
          "fallout2-ce"
        ];
    };
    fallout1Plugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/fallout1-ce;
      plugin = _: import ../plugins/fallout1-ce/plugin.nix { pkgs = falloutPkgs; };
    };
    fallout2Plugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/fallout2-ce;
      plugin = _: import ../plugins/fallout2-ce/plugin.nix { pkgs = falloutPkgs; };
    };
    falloutCheck =
      name: program: package:
      import ./fallout-check.nix {
        inherit
          pkgs
          package
          name
          program
          ;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
    meleePackage = import ../plugins/melee-pc/package.nix { inherit pkgs; };
    meleePlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/melee-pc;
      plugin = _: import ../plugins/melee-pc/plugin.nix { inherit meleePackage; };
    };
    nocturneSceneExpansion = import ../plugins/nocturne/scene-expansion.nix {
      inherit pkgs;
      src = nocturne-encore;
    };
    nocturnePackage = import ../plugins/nocturne/package.nix {
      inherit pkgs;
      mods = [ nocturneSceneExpansion ];
    };
    nocturnePlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/nocturne;
      plugin = _: import ../plugins/nocturne/plugin.nix { inherit nocturnePackage; };
    };
    simpsonsPkgs = import nixpkgs {
      inherit system;
      # Only this private recompilation needs unfree-code admission.
      config.allowUnfreePredicate = package: pkgs.lib.getName package == "simpsons-recomp";
    };
    simpsonsEngine = import ../plugins/the-simpsons-game/engine.nix { pkgs = simpsonsPkgs; };
    simpsonsPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/the-simpsons-game;
      plugin =
        _:
        import ../plugins/the-simpsons-game/plugin.nix {
          inherit pkgs;
          engine = simpsonsEngine;
        };
    };
    fablePkgs = import nixpkgs {
      inherit system;
      config.allowUnfreePredicate = package: pkgs.lib.getName package == "fable-ii-recomp";
    };
    fableEngine = import ../plugins/fable-ii-recomp/engine.nix { pkgs = fablePkgs; };
    fableExtractor = import ../plugins/fable-ii-recomp/extractor.nix { inherit pkgs; };
    fablePlugin =
      (mkPlugin {
        publisher.namespace = "@simonwjackson";
        source = ../plugins/fable-ii-recomp;
        plugin =
          _:
          import ../plugins/fable-ii-recomp/plugin.nix {
            inherit pkgs;
            engine = fableEngine;
          };
      }).overrideAttrs
        {
          allowSubstitutes = false;
          preferLocalBuild = true;
        };
    twoShipPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/2ship;
      plugin = _: import ../plugins/2ship/plugin.nix { inherit pkgs; };
    };
    # The viewport verifier still needs Pillow after the starter-pack move.
    python = pkgs.python3.withPackages (packages: [ packages.pillow ]);
    verifyActraiser = pkgs.writeShellApplication {
      name = "verify-actraiser";
      text = ''
        exec ${pkgs.python3}/bin/python3 ${./actraiser-runtime-check.py} \
          ${actraiserPlugin} ${korri.packages.${system}.korrid}/bin/korrid "$@"
      '';
    };
    verifyActraiserAuto = pkgs.writeShellApplication {
      name = "verify-actraiser-auto";
      runtimeInputs = [ pkgs.xdotool ];
      text = ''
        exec ${python}/bin/python3 ${./actraiser-viewport-check.py} \
          ${actraiserPlugin} ${korri.packages.${system}.korrid}/bin/korrid \
          ${import ../plugins/actraiser/source.nix { inherit pkgs; }} "$@"
      '';
    };
    verifySmw = pkgs.writeShellApplication {
      name = "verify-smw";
      text = ''
        exec ${pkgs.python3}/bin/python3 ${./smw-runtime-check.py} \
          ${smwPlugin} ${korri.packages.${system}.korrid}/bin/korrid "$@"
      '';
    };
    verifyNocturne = pkgs.writeShellApplication {
      name = "verify-nocturne";
      runtimeInputs = [
        pkgs.xorg.xorgserver
        pkgs.xorg.xauth
        pkgs.xdotool
        pkgs.imagemagick
        pkgs.pulseaudio
        pkgs.dbus
      ];
      text = ''
        export VK_DRIVER_FILES=${pkgs.mesa}/share/vulkan/icd.d/lvp_icd.${pkgs.stdenv.hostPlatform.parsed.cpu.name}.json
        exec dbus-run-session -- ${pkgs.python3}/bin/python3 ${./nocturne-owned-check.py} \
          ${nocturnePlugin} ${korri.packages.${system}.korrid}/bin/korrid "$@"
      '';
    };
    verifySimpsons = pkgs.writeShellApplication {
      name = "verify-simpsons";
      text = ''
        exec ${pkgs.python3}/bin/python3 -I ${./simpsons-runtime-check.py} \
          ${simpsonsPlugin} ${korri.packages.${system}.korrid}/bin/korrid "$@"
      '';
    };
    twoShipEarlyWindow = pkgs.runCommandCC "2ship-early-window" { } ''
      mkdir -p "$out/lib"
      $CC -Wall -Wextra -Werror -shared -fPIC ${./2ship-early-window.c} \
        -ldl -o "$out/lib/2ship-early-window.so"
    '';
    verifyTwoShip = pkgs.writeShellApplication {
      name = "verify-2ship";
      runtimeInputs = [
        pkgs.xorg.xorgserver
        pkgs.xorg.xauth
        pkgs.xdotool
      ];
      text = ''
        export LIBGL_DRIVERS_PATH=${pkgs.mesa}/lib/dri
        export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [ pkgs.mesa ]}
        export __GLX_VENDOR_LIBRARY_NAME=mesa
        export SDL_VIDEODRIVER=x11
        export KORRI_2SHIP_EARLY_WINDOW_PROBE=${twoShipEarlyWindow}/lib/2ship-early-window.so
        exec ${pkgs.python3}/bin/python3 ${./2ship-runtime-check.py} \
          ${twoShipPlugin} ${korri.packages.${system}.korrid}/bin/korrid "$@"
      '';
    };
    verifyMelee = import ./melee-owned-check.nix {
      inherit pkgs;
      package = meleePlugin;
      korridPackage = korri.packages.${system}.korrid;
    };
    verifyFable = pkgs.writeShellApplication {
      name = "verify-fable-ii";
      text = ''
        exec ${pkgs.python3}/bin/python3 -I ${./fable2-owned-check.py} \
          ${fablePlugin} ${korri.packages.${system}.korrid}/bin/korrid "$@"
      '';
    };
    zquestMidiProof = import ./zquest-midi-proof.nix { inherit pkgs; };
    help = pkgs.writeShellApplication {
      name = "korri-plugins-help";
      text = ''
        printf '%s\n' \
          'Run on a build machine, not a target device:' \
          'Super Mario World supports x86_64 and aarch64 Linux:' \
          '  nix build --no-link .#korri-plugin-super-mario-world' \
          '  nix build --no-link .#checks.x86_64-linux.korri-super-mario-world-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-super-mario-world-plugin' \
          '  nix run .#verify-smw -- /path/to/owned/USA-ROM.smc  # optional, temporary assets only' \
          'Signs of Rain has x86_64-linux and aarch64-linux package targets:' \
          '  nix build --no-link --option builders "" --option post-build-hook "" .#korri-plugin-signs-of-rain' \
          '  nix build --no-link --option builders "" --option post-build-hook "" .#checks.${system}.korri-signs-of-rain-plugin' \
          'Signs of Rain ARM plugin builds need an approved ARM builder; see plugins/signs-of-rain/README.md.' \
          'Register its exact packaged PCK in the existing library; no general PCK discovery is added.' \
          'ZQuest Classic supports x86_64 and aarch64 Linux:' \
          '  nix build --no-link .#korri-plugin-zquest-classic' \
          '  nix build --no-link .#zquest-classic-source' \
          '  nix build --no-link .#checks.x86_64-linux.korri-zquest-classic-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-zquest-classic-plugin' \
          '  nix build --no-link .#checks.x86_64-linux.zquest-gamepad-vm' \
          '  nix run .#zquest-classic -- /path/to/quest.qst /path/to/test-state' \
          'Private quest editing proof, not a complete sanitizer or rights clearance:' \
          '  nix run .#zquest-midi-proof -- --help' \
          '  nix run .#zquest-midi-proof-test -- --help' \
          '  nix run .#zquest-midi-proof-runtime -- --help' \
          'Keep quest inputs and outputs outside Git and public caches. No device work.' \
          'Fallout CE engines support x86_64 and aarch64 Linux:' \
          '  nix build --no-link .#korri-plugin-fallout1-ce .#korri-plugin-fallout2-ce' \
          '  nix build --no-link .#checks.x86_64-linux.korri-fallout1-ce-plugin .#checks.x86_64-linux.korri-fallout2-ce-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-fallout1-ce-plugin .#checks.aarch64-linux.korri-fallout2-ce-plugin' \
          'Fallout runners need registered MASTER.DAT releases and writable installed data folders.' \
          'Melee PC beta supports x86_64-linux and aarch64-linux:' \
          '  nix build --no-link .#korri-plugin-melee-pc' \
          '  nix build --no-link .#checks.x86_64-linux.korri-melee-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-melee-plugin' \
          '  nix run .#verify-melee -- /path/to/owned/USA-1.02.iso  # requires a hardware Vulkan GPU' \
          'Melee attaches only to the registered supported USA 1.02 ISO; no general GameCube scanner is added.' \
          'Keep Melee binaries private; public redistribution is not approved.' \
          'NocturneRecomp supports x86_64-linux and aarch64-linux:' \
          '  nix build --no-link .#korri-plugin-nocturne' \
          '  nix build --no-link .#checks.x86_64-linux.korri-nocturne-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-nocturne-plugin' \
          '  nix run .#verify-nocturne -- /path/to/extracted/default.xex' \
          'OpenGOAL supports x86_64-linux and aarch64-linux; builds and preparation run off-device:' \
          '  nix build --no-link .#korri-plugin-opengoal' \
          '  nix build --no-link .#checks.x86_64-linux.korri-opengoal-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-opengoal-plugin' \
          '  nix run .#prepare-opengoal -- --game jak2 --instruction-set arm64 --iso /path/to/owned.iso --output /path/to/new-data' \
          '  nix run .#verify-opengoal -- /path/to/prepared-data --game jak2  # build machines only' \
          'OpenGOAL requires architecture-matched out/<game>/iso/GAME.CGO releases and their complete prepared directories.' \
          '2 Ship 2 Harkinian supports x86_64 and aarch64 Linux:' \
          '  nix build --no-link .#korri-plugin-2ship' \
          '  nix build --no-link .#checks.x86_64-linux.korri-2ship-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-2ship-plugin' \
          '  nix run .#verify-2ship -- /path/to/owned/USA-ROM.n64  # temporary game assets only' \
          'Skate 3 supports x86_64 and aarch64 Linux:' \
          '  nix build --no-link .#korri-plugin-skate-3' \
          '  nix build --no-link .#checks.x86_64-linux.korri-skate3-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-skate3-plugin' \
          'Skate 3 ARM64 builds need two owned XEX files in the builder store; see plugins/skate-3/README.md.' \
          'SMW builds need no ROM. Its verify app explicitly uses an owned ROM.' \
          'ActRaiser private builds support x86_64-linux and aarch64-linux:' \
          '  NIXPKGS_ALLOW_UNFREE=1 nix build --impure --option builders "" --option post-build-hook "" .#korri-plugin-actraiser' \
          '  NIXPKGS_ALLOW_UNFREE=1 nix build --impure --option builders "" --option post-build-hook "" .#checks.${system}.korri-actraiser-plugin' \
          '  NIXPKGS_ALLOW_UNFREE=1 nix run --impure --option builders "" --option post-build-hook "" .#verify-actraiser -- /path/to/ar.sfc' \
          '  NIXPKGS_ALLOW_UNFREE=1 nix run --impure --option builders "" --option post-build-hook "" .#verify-actraiser-auto -- /path/to/ar.sfc  # requires X11 and a Vulkan GPU driver' \
          'ActRaiser requires an owned USA ar.sfc in the private build machine store. See plugins/actraiser/README.md.' \
          'Never publish ActRaiser outputs or its ROM input to public caches or releases.' \
          'Fable II private source builds target x86_64-linux and aarch64-linux:' \
          '  nix build --no-link --option builders "" --option post-build-hook "" .#korri-plugin-fable-ii-recomp' \
          '  nix build --no-link --option builders "" --option post-build-hook "" .#checks.${system}.korri-fable-ii-recomp-plugin' \
          '  nix run --option builders "" --option post-build-hook "" .#verify-fable-ii -- /path/to/owned/GOTY.iso' \
          'Fable II requires the verified owned GOTY default.xex in the builder store. See plugins/fable-ii-recomp/README.md.' \
          'Fable II ISO verification needs about 15 GB temporary free space and tests extraction/native entry, not gameplay.' \
          'Do not upload Fable II inputs, native outputs or checks to public caches.' \
          'The Simpsons Game has native x86_64 and aarch64 build targets:' \
          '  nix build --no-link .#korri-plugin-the-simpsons-game' \
          '  nix build --no-link .#checks.x86_64-linux.korri-the-simpsons-game-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-the-simpsons-game-plugin' \
          '  nix run .#verify-simpsons -- /path/to/owned/USA-disc.iso  # needs about 5 GB temporary space' \
          '  Keep Simpsons native binaries private; no publication is approved.' \
          'Simpsons builds do not extract game data; verify-simpsons explicitly uses owned media.' \
          'No signing, binary publication or device installation runs here.'
      '';
    };
  in
  {
    packages = packages // {
      korri-plugin-super-mario-world = smwPlugin;
      korri-plugin-signs-of-rain = signsOfRainPlugin;
      zquest-classic = zquestLauncher;
      zquest-classic-source = import ./zquest-source-release.nix {
        inherit pkgs;
        engine = zquestEngine;
      };
      korri-plugin-zquest-classic = zquestPlugin;
      korri-plugin-fallout1-ce = fallout1Plugin;
      korri-plugin-fallout2-ce = fallout2Plugin;
      melee-pc = meleePackage;
      korri-plugin-melee-pc = meleePlugin;
      verify-melee = verifyMelee;
      nocturne = nocturnePackage;
      nocturne-scene-expansion = nocturneSceneExpansion;
      korri-plugin-nocturne = nocturnePlugin;
      verify-nocturne = verifyNocturne;
      verify-opengoal = verifyOpengoal;
      actraiser = actraiserPackage;
      korri-plugin-actraiser = actraiserPlugin;
      korri-plugin-the-simpsons-game = simpsonsPlugin;
      korri-plugin-2ship = twoShipPlugin;
      verify-2ship = verifyTwoShip;
      fable-ii-recomp-native = fableEngine;
      fable-ii-extract-xiso = fableExtractor;
      korri-plugin-fable-ii-recomp = fablePlugin;
      korri-plugin-mega-man-rock-n-roll = megaManRockNRollPlugin;
      korri-plugin-mega-man-maker = megaManMakerPlugin;
    };
    checks = {
      korri-actraiser-plugin = import ./actraiser-check.nix {
        inherit pkgs;
        package = actraiserPlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-2ship-plugin = import ./2ship-check.nix {
        inherit pkgs;
        package = twoShipPlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-signs-of-rain-plugin = import ./signs-of-rain-check.nix {
        inherit pkgs signsOfRainPackage;
        package = signsOfRainPlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-fallout1-ce-plugin = falloutCheck "fallout1-ce" "fallout-ce" fallout1Plugin;
      korri-fallout2-ce-plugin = falloutCheck "fallout2-ce" "fallout2-ce" fallout2Plugin;
      korri-melee-plugin = import ./melee-check.nix {
        inherit pkgs;
        package = meleePlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-nocturne-plugin = import ./nocturne-check.nix {
        inherit pkgs;
        package = nocturnePlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-fable-ii-recomp-plugin = import ./fable2-check.nix {
        inherit pkgs;
        package = fablePlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-the-simpsons-game-plugin = import ./simpsons-check.nix {
        inherit pkgs;
        package = simpsonsPlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-super-mario-world-plugin = import ./smw-check.nix {
        inherit pkgs;
        package = smwPlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-zquest-classic-plugin = import ./zquest-check.nix {
        inherit pkgs;
        package = zquestPlugin;
        engine = zquestEngine;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-mega-man-rock-n-roll-source = import ./mega-man-rock-n-roll-source-check.nix { inherit pkgs; };
      korri-mega-man-arena-source = import ./mega-man-arena-source-check.nix { inherit pkgs; };
      korri-mega-man-rock-n-roll-plugin = import ./mega-man-rock-n-roll-check.nix {
        inherit pkgs;
        package = megaManRockNRollPlugin;
        contract = korri.lib.${system}.pluginContract;
      };
      korri-mega-man-maker-source = import ./mega-man-maker-source-check.nix { inherit pkgs; };
      korri-mega-man-maker-plugin = import ./mega-man-maker-check.nix {
        inherit pkgs;
        package = megaManMakerPlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-skate3-plugin = import ./skate3-check.nix {
        inherit pkgs;
        package = packages.korri-plugin-skate-3;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-opengoal-plugin = import ./opengoal-check.nix {
        inherit pkgs;
        package = packages.korri-plugin-opengoal;
        tools = if system == "x86_64-linux" then opengoalPackages.tools else null;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
    }
    // pkgs.lib.optionalAttrs (system == "aarch64-linux") {
      korri-mega-man-arena-plugin = import ./mega-man-arena-check.nix {
        inherit pkgs;
        package = megaManArenaPlugin;
        contract = korri.lib.${system}.pluginContract;
      };
    }
    # The VM needs KVM; it runs on the x86_64 build machine only.
    // pkgs.lib.optionalAttrs (system == "x86_64-linux") {
      zquest-gamepad-vm = import ./zquest-gamepad-vm.nix {
        inherit pkgs;
        launcher = zquestLauncher;
      };
    };
    formatter = pkgs.nixfmt;
    apps = {
      zquest-midi-proof = {
        type = "app";
        program = "${zquestMidiProof.proof}/bin/zquest-midi-proof";
        meta.description = "Privately prove unchanged QST save/reload and one MIDI-slot removal.";
      };
      zquest-midi-proof-test = {
        type = "app";
        program = "${zquestMidiProof.test}/bin/zquest-midi-proof-test";
        meta.description = "Run editing-proof and timeout-cleanup checks against a privately supplied quest.";
      };
      zquest-midi-proof-runtime = {
        type = "app";
        program = "${zquestMidiProof.runtime}/bin/zquest-midi-proof-runtime";
        meta.description = "Compare three private QSTs off-device with network isolation and null audio.";
      };
      verify-melee = {
        type = "app";
        program = "${verifyMelee}/bin/verify-melee";
        meta.description = "Test Melee native launch and state preservation with an owned ISO on a GPU-equipped build machine.";
      };
      verify-opengoal = {
        type = "app";
        program = "${verifyOpengoal}/bin/verify-opengoal";
        meta.description = "Test native OpenGOAL startup with prepared owned data on a build machine.";
      };
      verify-actraiser = {
        type = "app";
        program = "${verifyActraiser}/bin/verify-actraiser";
        meta.description = "Privately verify native ActRaiser boot, frames and settings with an owned ROM.";
      };
      verify-actraiser-auto = {
        type = "app";
        program = "${verifyActraiserAuto}/bin/verify-actraiser-auto";
        meta.description = "Privately verify Auto viewport expansion and resize using a real GPU and owned ROM.";
      };
      verify-2ship = {
        type = "app";
        program = "${verifyTwoShip}/bin/verify-2ship";
        meta.description = "Test 2 Ship extraction, startup, saves and shutdown with an owned ROM on a build machine.";
      };
      verify-nocturne = {
        type = "app";
        program = "${verifyNocturne}/bin/verify-nocturne";
        meta.description = "Test native Nocturne launch using owned extracted XBLA assets on a build machine.";
      };
      verify-smw = {
        type = "app";
        program = "${verifySmw}/bin/verify-smw";
        meta.description = "Test SMW startup and snapshot reload with an owned ROM on a build machine.";
      };
      verify-fable-ii = {
        type = "app";
        program = "${verifyFable}/bin/verify-fable-ii";
        meta.description = "Privately verify owned Fable II ISO extraction and native entry on a build machine.";
      };
      verify-simpsons = {
        type = "app";
        program = "${verifySimpsons}/bin/verify-simpsons";
        meta.description = "Test Simpsons ISO installation and native loading without a display.";
      };
      help = {
        type = "app";
        program = "${help}/bin/korri-plugins-help";
        meta.description = "List build and check commands.";
      };
    }
    // pkgs.lib.optionalAttrs (system == "x86_64-linux") {
      prepare-opengoal = {
        type = "app";
        program = "${prepareOpengoal}/bin/prepare-opengoal";
        meta.description = "Prepare owned PS2 game data on an x86_64 build machine, never on a target device.";
      };
    };
  }
)
