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
    pkgs = import nixpkgs { inherit system; };
    mkPlugin = korri.lib.${system}.mkPlugin { inherit pkgs; };
    # Namespace matches the personal repository's existing PICO-8 producer.
    # The native flake provides a prebuilt release only for x86_64 Linux.
    packages = pkgs.lib.optionalAttrs (system == "x86_64-linux") {
      korri-plugin-skate-3 = mkPlugin {
        publisher.namespace = "@simonwjackson";
        source = ../plugins/skate-3;
        plugin =
          _:
          import ../plugins/skate-3/plugin.nix {
            skate3Package = skate3.packages.${system}.skate3;
          };
      };
    };
    smwPlugin = mkPlugin {
      publisher.namespace = "@simonwjackson";
      source = ../plugins/super-mario-world;
      plugin = _: import ../plugins/super-mario-world/plugin.nix { inherit pkgs; };
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
    verifySmw = pkgs.writeShellApplication {
      name = "verify-smw";
      text = ''
        exec ${pkgs.python3}/bin/python3 ${./smw-runtime-check.py} \
          ${smwPlugin} ${korri.packages.${system}.korrid}/bin/korrid "$@"
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
          'Skate 3 is x86_64 only:' \
          '  nix build --no-link .#korri-plugin-skate-3' \
          '  nix build --no-link .#checks.x86_64-linux.korri-skate3-plugin' \
          'Builds do not extract game data. verify-smw explicitly uses an owned ROM.' \
          'No signing, binary publication or device installation runs here.'
      '';
    };
  in
  {
    packages = packages // {
      pico8-starter-pack-cartridges = cartridges;
      korri-plugin-pico8-starter-pack = plugin;
      korri-plugin-super-mario-world = smwPlugin;
    };
    checks = {
      pico8-starter-pack = check;
      korri-super-mario-world-plugin = import ./smw-check.nix {
        inherit pkgs;
        package = smwPlugin;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
    }
    // pkgs.lib.optionalAttrs (system == "x86_64-linux") {
      korri-skate3-plugin = import ./skate3-check.nix {
        inherit pkgs;
        package = packages.korri-plugin-skate-3;
        contract = korri.lib.${system}.pluginContract;
        hostPackage = korri.packages.${system}.korri-plugin-host;
        korridPackage = korri.packages.${system}.korrid;
      };
    };
    formatter = pkgs.nixfmt;
    apps.verify-smw = {
      type = "app";
      program = "${verifySmw}/bin/verify-smw";
      meta.description = "Test SMW startup and snapshot reload with an owned ROM on a build machine.";
    };
    apps.help = {
      type = "app";
      program = "${help}/bin/korri-plugins-help";
      meta.description = "List build and check commands.";
    };
  }
)
