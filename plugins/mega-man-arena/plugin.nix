# Mega Man Arena. plugin.ts declares the game, its ZIP artifact and the
# Proton runner, and names the files below. Neither the ZIP nor Proton is in
# the closure: korrid downloads both into its cache (ADR 0012/0013). The ZIP
# is this plugin's artifact; Proton-CachyOS arm64 is @korri:proton's. The
# runner is an FHS environment for Proton's glibc binaries (runner/fhs.nix).
{ pkgs }:
let
  unpack = pkgs.writeShellApplication {
    name = "mega-man-arena-unpack";
    runtimeInputs = [ pkgs.python3 ];
    text = ''exec python3 ${./game/unpack.py} ${./game/contents} "$@"'';
  };
  launch = import ./runner/fhs.nix { inherit pkgs; };
in
{
  packages = {
    mega-man-arena-unpack = unpack;
    mega-man-arena-proton = launch;
  };
  files = {
    game-unpack = "${unpack}/bin/mega-man-arena-unpack";
    proton-launch = "${launch}/bin/mega-man-arena-proton";
  };
}
