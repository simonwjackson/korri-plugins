{
  korri,
  nixpkgs,
  flake-utils,
  signs-of-rain,
}:
flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (
  system:
  let
    pkgs = import nixpkgs {
      inherit system;
      config.allowUnfreePredicate =
        pkg:
        builtins.elem (nixpkgs.lib.getName pkg) [
          "2ship2harkinian"
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
      }
      // pkgs.lib.optionalAttrs (system == "aarch64-linux") {
        korri-plugin-mega-man-arena = megaManArenaPlugin;
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
    twoShipPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/2ship;
      plugin = _: import ../plugins/2ship/plugin.nix { inherit pkgs; };
    };
    verifySmw = pkgs.writeShellApplication {
      name = "verify-smw";
      text = ''
        exec ${pkgs.python3}/bin/python3 ${./smw-runtime-check.py} \
          ${smwPlugin} ${korri.packages.${system}.korrid}/bin/korrid "$@"
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
          'SMW builds need no ROM. Its verify app explicitly uses an owned ROM.' \
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
      verify-opengoal = verifyOpengoal;
      korri-plugin-2ship = twoShipPlugin;
      verify-2ship = verifyTwoShip;
      korri-plugin-mega-man-rock-n-roll = megaManRockNRollPlugin;
      korri-plugin-mega-man-maker = megaManMakerPlugin;
    };
    checks = {
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
      korri-mega-man-rock-n-roll-source = import ./mega-man-rock-n-roll-source-check.nix {
        inherit pkgs;
      };
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
      verify-opengoal = {
        type = "app";
        program = "${verifyOpengoal}/bin/verify-opengoal";
        meta.description = "Test native OpenGOAL startup with prepared owned data on a build machine.";
      };
      verify-2ship = {
        type = "app";
        program = "${verifyTwoShip}/bin/verify-2ship";
        meta.description = "Test 2 Ship extraction, startup, saves and shutdown with an owned ROM on a build machine.";
      };
      verify-smw = {
        type = "app";
        program = "${verifySmw}/bin/verify-smw";
        meta.description = "Test SMW startup and snapshot reload with an owned ROM on a build machine.";
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
