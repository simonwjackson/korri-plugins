{
  korri,
  nixpkgs,
  flake-utils,
  skate3,
  plugin-publisher,
}:
flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (
  system:
  let
    pkgs = import nixpkgs {
      inherit system;
      config.allowUnfreePredicate = pkg: nixpkgs.lib.getName pkg == "nocturnerecomp";
    };
    mkPlugin = korri.lib.${system}.mkPlugin { inherit pkgs; };
    opengoalPackages = import ../plugins/opengoal/package.nix { inherit pkgs; };
    prepareOpengoal = pkgs.writeShellApplication {
      name = "prepare-opengoal";
      text = ''
        exec ${pkgs.python3}/bin/python3 ${../plugins/opengoal/prepare.py} ${opengoalPackages.tools} "$@"
      '';
    };
    packages =
      pkgs.lib.optionalAttrs (system == "x86_64-linux") {
        opengoal = opengoalPackages.runtime;
        opengoal-tools = opengoalPackages.tools;
        korri-plugin-opengoal = mkPlugin {
          publisher.namespace = "@simonwjackson";
          source = ../plugins/opengoal;
          plugin =
            _:
            import ../plugins/opengoal/plugin.nix {
              opengoalRuntime = opengoalPackages.runtime;
            };
        };
      }
      // {
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
    nocturnePackage = import ../plugins/nocturne/package.nix { inherit pkgs; };
    nocturnePlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/nocturne;
      plugin = _: import ../plugins/nocturne/plugin.nix { inherit nocturnePackage; };
    };
    source = ../plugins/pico8-starter-pack;
    cartridges = import (source + /cartridges-package.nix) { inherit pkgs; };
    fake08Plugin = plugin-publisher.packages.${system}.korri-plugin-fake08;
    plugin = mkPlugin {
      inherit source;
      publisher.namespace = "@simonwjackson";
      plugin = _: import (source + /plugin.nix) { inherit pkgs fake08Plugin; };
    };
    originals = import (source + /cartridges.nix) { inherit pkgs; };
    # Test inputs come from fetchurl's real attributes, not a second manifest.
    pins = pkgs.writeText "pico8-original-fetchurl-pins.json" (
      builtins.toJSON (map (cart: { inherit (cart) name outputHash url; }) originals)
    );
    python = pkgs.python3.withPackages (packages: [ packages.pillow ]);
    check = pkgs.runCommand "pico8-starter-pack-check" { } ''
      ${python}/bin/python ${./check-pack.py} \
        ${cartridges}/share/pico8-starter-pack ${pins} ${plugin} ${fake08Plugin}
      ${pkgs.typescript}/bin/tsc --noEmit --strict --target es2022 ${source}/plugin.ts
      touch "$out"
    '';
    verifyActraiser = pkgs.writeShellApplication {
      name = "verify-actraiser";
      text = ''
        exec ${pkgs.python3}/bin/python3 ${./actraiser-runtime-check.py} \
          ${actraiserPlugin} ${korri.packages.${system}.korrid}/bin/korrid "$@"
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
    help = pkgs.writeShellApplication {
      name = "korri-plugins-help";
      text = ''
        printf '%s\n' \
          'Run on a build machine, not a target device:' \
          '  nix build .#pico8-starter-pack-cartridges --out-link result-cartridges' \
          '  nix build .#korri-plugin-pico8-starter-pack --out-link result-plugin' \
          '  nix build --no-link .#checks.x86_64-linux.pico8-starter-pack' \
          '  nix build --no-link .#checks.aarch64-linux.pico8-starter-pack' \
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
          'Fallout CE engines support x86_64 and aarch64 Linux:' \
          '  nix build --no-link .#korri-plugin-fallout1-ce .#korri-plugin-fallout2-ce' \
          '  nix build --no-link .#checks.x86_64-linux.korri-fallout1-ce-plugin .#checks.x86_64-linux.korri-fallout2-ce-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-fallout1-ce-plugin .#checks.aarch64-linux.korri-fallout2-ce-plugin' \
          'Fallout runners need registered MASTER.DAT releases and writable installed data folders.' \
          'NocturneRecomp supports x86_64-linux and aarch64-linux:' \
          '  nix build --no-link .#korri-plugin-nocturne' \
          '  nix build --no-link .#checks.x86_64-linux.korri-nocturne-plugin' \
          '  nix build --no-link .#checks.aarch64-linux.korri-nocturne-plugin' \
          '  nix run .#verify-nocturne -- /path/to/extracted/default.xex' \
          'OpenGOAL trilogy supports x86_64 Linux; game preparation runs off-device:' \
          '  nix build --no-link .#korri-plugin-opengoal' \
          '  nix build --no-link .#checks.x86_64-linux.korri-opengoal-plugin' \
          '  nix run .#prepare-opengoal -- --game jak2 --iso /path/to/owned.iso --output /path/to/new-data' \
          'OpenGOAL requires registered out/<game>/iso/GAME.CGO releases and their complete prepared directories.' \
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
          'ActRaiser requires an owned USA ar.sfc in the private build machine store. See plugins/actraiser/README.md.' \
          'Never publish ActRaiser outputs or its ROM input to public caches or releases.' \
          'No signing, binary publication or device installation runs here.'
      '';
    };
  in
  {
    packages = packages // {
      pico8-starter-pack-cartridges = cartridges;
      korri-plugin-pico8-starter-pack = plugin;
      korri-plugin-super-mario-world = smwPlugin;
      korri-plugin-solarus = solarusPlugin;
      solarus = solarusPackage;
      korri-plugin-zelda3 = zelda3Plugin;
      zelda3 = zelda3Package;
      korri-plugin-fallout1-ce = fallout1Plugin;
      korri-plugin-fallout2-ce = fallout2Plugin;
      nocturne = nocturnePackage;
      korri-plugin-nocturne = nocturnePlugin;
      verify-nocturne = verifyNocturne;
      actraiser = actraiserPackage;
      korri-plugin-actraiser = actraiserPlugin;
    };
    checks = {
      korri-actraiser-plugin = import ./actraiser-check.nix {
        inherit pkgs;
        package = actraiserPlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      pico8-starter-pack = check;
      korri-solarus-plugin = import ./solarus-check.nix {
        inherit pkgs solarusPackage;
        package = solarusPlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
      korri-fallout1-ce-plugin = falloutCheck "fallout1-ce" "fallout-ce" fallout1Plugin;
      korri-fallout2-ce-plugin = falloutCheck "fallout2-ce" "fallout2-ce" fallout2Plugin;
      korri-nocturne-plugin = import ./nocturne-check.nix {
        inherit pkgs;
        package = nocturnePlugin;
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
    }
    // pkgs.lib.optionalAttrs (system == "x86_64-linux") {
      korri-opengoal-plugin = import ./opengoal-check.nix {
        inherit pkgs;
        package = packages.korri-plugin-opengoal;
        tools = opengoalPackages.tools;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
    };
    formatter = pkgs.nixfmt;
    apps = {
      verify-actraiser = {
        type = "app";
        program = "${verifyActraiser}/bin/verify-actraiser";
        meta.description = "Privately verify native ActRaiser boot, frames and settings with an owned ROM.";
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
