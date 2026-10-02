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
    help = pkgs.writeShellApplication {
      name = "korri-plugins-help";
      text = ''
        printf '%s\n' \
          'Run on a build machine, not a target device:' \
          '  nix build .#pico8-starter-pack-cartridges --out-link result-cartridges' \
          '  nix build .#korri-plugin-pico8-starter-pack --out-link result-plugin' \
          '  nix build --no-link .#checks.x86_64-linux.pico8-starter-pack' \
          '  nix build --no-link .#checks.aarch64-linux.pico8-starter-pack' \
          'Skate 3 is x86_64 only:' \
          '  nix build --no-link .#korri-plugin-skate-3' \
          '  nix build --no-link .#checks.x86_64-linux.korri-skate3-plugin' \
          'No signing, binary publication, device installation or game extraction runs here.'
      '';
    };
  in
  {
    packages = packages // {
      pico8-starter-pack-cartridges = cartridges;
      korri-plugin-pico8-starter-pack = plugin;
    };
    checks = {
      pico8-starter-pack = check;
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
    apps.help = {
      type = "app";
      program = "${help}/bin/korri-plugins-help";
      meta.description = "List build and check commands.";
    };
  }
)
