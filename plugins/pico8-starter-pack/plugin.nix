{ pkgs, fake08Plugin }:
let
  cartridges = import ./cartridges-package.nix { inherit pkgs; };
  payload = "${cartridges}/share/pico8-starter-pack";
in
{
  # Exact plugin-output dependency, using the original native builder's
  # requires field from Core f3aa66d91. FAKE-08 owns the runner and runtime.
  requires = [ fake08Plugin ];
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
