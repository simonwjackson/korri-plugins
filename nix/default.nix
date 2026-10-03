{
  korri,
  nixpkgs,
  flake-utils,
  skate3,
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
          "drmario-nes-recomp"
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
      };
    drMarioEngine = import ../plugins/dr-mario/engine.nix { inherit pkgs; };
    drMarioPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/dr-mario;
      plugin =
        _:
        import ../plugins/dr-mario/plugin.nix {
          inherit pkgs;
          engine = drMarioEngine;
        };
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
    solarusPackage = import ../plugins/solarus/package.nix { inherit pkgs; };
    solarusPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/solarus;
      plugin = _: import ../plugins/solarus/plugin.nix { inherit solarusPackage; };
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
    zelda3Package = import ../plugins/zelda3/package.nix { inherit pkgs; };
    zelda3Plugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/zelda3;
      plugin = _: import ../plugins/zelda3/plugin.nix { inherit zelda3Package; };
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
    nocturnePackage = import ../plugins/nocturne/package.nix { inherit pkgs; };
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
    verifyDrMario = pkgs.writeShellApplication {
      name = "verify-dr-mario";
      runtimeInputs = [
        pkgs.xorg.xorgserver
        pkgs.xdotool
      ];
      text = ''
        exec ${pkgs.python3}/bin/python3 -I ${./dr-mario-runtime-check.py} \
          ${drMarioPlugin} ${drMarioEngine} ${korri.packages.${system}.korrid}/bin/korrid "$@"
      '';
    };
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
    verifyZelda3 = pkgs.writeShellApplication {
      name = "verify-zelda3";
      text = ''
        exec ${pkgs.python3}/bin/python3 ${./zelda3-owned-rom-check.py} \
          ${zelda3Plugin} ${korri.packages.${system}.korrid}/bin/korrid "$@"
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
    help = pkgs.writeShellApplication {
      name = "korri-plugins-help";
      text = ''
        printf '%s\n' \
          'Run on a build machine, not a target device:' \
          '  nix build --option builders "" --option post-build-hook "" .#korri-plugin-dr-mario' \
          '  nix build --option builders "" --option post-build-hook "" .#checks.${system}.korri-dr-mario-plugin' \
          '  nix run --option builders "" --option post-build-hook "" .#verify-dr-mario -- /path/to/owned-Europe.nes' \
          'Dr. Mario requires approval before sending builds to fuji. Native outputs stay private.' \
          'Super Mario World supports x86_64 and aarch64 Linux:' \
          '  nix build --no-link .#korri-plugin-super-mario-world' \
          '  nix build --no-link .#checks.x86_64-linux.korri-super-mario-world-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-super-mario-world-plugin' \
          '  nix run .#verify-smw -- /path/to/owned/USA-ROM.smc  # optional, temporary assets only' \
          'Solarus supports x86_64-linux and aarch64-linux:' \
          '  nix build --no-link .#korri-plugin-solarus' \
          '  nix build --no-link .#checks.x86_64-linux.korri-solarus-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-solarus-plugin' \
          'Solarus discovers .solarus quests and keeps saves in the account root supplied by Korri.' \
          'Zelda3 supports x86_64-linux and aarch64-linux:' \
          '  nix build --no-link .#korri-plugin-zelda3' \
          '  nix build --no-link .#checks.x86_64-linux.korri-zelda3-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-zelda3-plugin' \
          '  nix run .#verify-zelda3 -- /path/to/owned/USA-ROM.sfc' \
          'ZQuest Classic supports x86_64 and aarch64 Linux:' \
          '  nix build --no-link .#korri-plugin-zquest-classic' \
          '  nix build --no-link .#zquest-classic-source' \
          '  nix build --no-link .#checks.x86_64-linux.korri-zquest-classic-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-zquest-classic-plugin' \
          '  nix run .#zquest-classic -- /path/to/quest.qst /path/to/test-state' \
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
          'SMW/Zelda3 builds need no ROM. Their verify apps explicitly use owned ROMs.' \
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
      dr-mario-engine = drMarioEngine;
      korri-plugin-dr-mario = drMarioPlugin;
      verify-dr-mario = verifyDrMario;
      korri-plugin-super-mario-world = smwPlugin;
      korri-plugin-solarus = solarusPlugin;
      solarus = solarusPackage;
      korri-plugin-zelda3 = zelda3Plugin;
      zelda3 = zelda3Package;
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
    };
    checks = {
      korri-dr-mario-plugin = import ./dr-mario-check.nix {
        inherit pkgs;
        package = drMarioPlugin;
        engine = drMarioEngine;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
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
      korri-solarus-plugin = import ./solarus-check.nix {
        inherit pkgs solarusPackage;
        package = solarusPlugin;
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
      korri-zelda3-plugin = import ./zelda3-check.nix {
        inherit pkgs;
        package = zelda3Plugin;
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
    };
    formatter = pkgs.nixfmt;
    apps = {
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
      verify-dr-mario = {
        type = "app";
        program = "${verifyDrMario}/bin/verify-dr-mario";
        meta.description = "Verify Dr. Mario with an owned Europe ROM on a build machine.";
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
      verify-zelda3 = {
        type = "app";
        program = "${verifyZelda3}/bin/verify-zelda3";
        meta.description = "Test Zelda3 extraction, native startup and snapshot reload with an owned ROM on a build machine.";
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
