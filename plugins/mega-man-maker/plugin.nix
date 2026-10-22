# Mega Man Maker. plugin.ts declares the game, its ZIP artifact and the Proton
# runner, and names the files below. Neither the ZIP nor Proton is in the
# closure: korrid downloads the game ZIP that plugin.ts pins and the
# @korri:proton cachyos artifact into its cache (ADR 0012/0013), and runs
# game-unpack on the ZIP. The runner reads only Proton's ready artifact
# directory, so the plugin requires no other package.
{ pkgs }:
let
  unpack = pkgs.writeShellApplication {
    name = "mega-man-maker-unpack";
    runtimeInputs = [ pkgs.python3 ];
    text = ''exec python3 ${./game/unpack.py} ${./game/contents} "$@"'';
  };
  launch = import ./runner/package.nix { inherit pkgs; };
in
{
  packages = {
    mega-man-maker-unpack = unpack;
    mega-man-maker-proton = launch;
  };
  files = {
    game-unpack = "${unpack}/bin/mega-man-maker-unpack";
    proton-launch = "${launch}/bin/mega-man-maker-proton";
  };
}
