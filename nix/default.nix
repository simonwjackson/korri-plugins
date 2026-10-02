{
  korri,
  nixpkgs,
  flake-utils,
  skate3,
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
    help = pkgs.writeShellApplication {
      name = "korri-plugins-help";
      text = ''
        printf '%s\n' \
          'Run on an x86_64 build machine, not a target device:' \
          '  nix build --no-link .#korri-plugin-skate-3' \
          '  nix build --no-link .#checks.x86_64-linux.korri-skate3-plugin' \
          'No binary publication, device installation or game extraction runs here.'
      '';
    };
  in
  {
    inherit packages;
    checks = pkgs.lib.optionalAttrs (system == "x86_64-linux") {
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
    };
  }
)
