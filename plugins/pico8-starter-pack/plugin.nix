{ pkgs }:
let
  cartridges = import ./cartridges-package.nix { inherit pkgs; };
  payload = "${cartridges}/share/pico8-starter-pack";
in
{
  # Existing mkPlugin packages/files fields carry the data. No invented game
  # contribution, install hook, service, or runtime dependency is required.
  packages = { inherit cartridges; };
  files = {
    cartridges = "${payload}/cartridges";
    credits = "${payload}/CREDITS.md";
    license = "${payload}/CC-BY-NC-SA-4.0.txt";
    notices = "${payload}/notices";
    checksums = "${payload}/SHA256SUMS";
    instructions = "${payload}/README.md";
  };
}
