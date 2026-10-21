# Mega Man Rock N Roll. plugin.ts declares the game, its ZIP artifact and the
# native Godot runner, and names the files below. The ZIP is not in the
# closure: korrid downloads the file plugin.ts pins into its cache and runs
# game-unpack on it (ADR 0012/0013). The runner plays data.pck with Godot
# 2.1.4 built from source on a build machine (godot2/package.nix).
{ pkgs }:
let
  unpack = pkgs.writeShellApplication {
    name = "mega-man-rock-n-roll-unpack";
    runtimeInputs = [ pkgs.python3 ];
    text = ''exec python3 ${./game/unpack.py} ${./game/contents} "$@"'';
  };
  runtime = import ./godot2/package.nix { inherit pkgs; };
  launch = pkgs.writeShellApplication {
    name = "mega-man-rock-n-roll-godot";
    runtimeInputs = [
      runtime
      pkgs.xorg.xdpyinfo
      pkgs.gnused
      pkgs.coreutils
    ];
    text = builtins.readFile ./runner/godot-launch.sh;
  };
in
{
  packages = {
    mega-man-rock-n-roll-unpack = unpack;
    mega-man-rock-n-roll-godot = launch;
    godot2-runtime = runtime;
  };
  files = {
    game-unpack = "${unpack}/bin/mega-man-rock-n-roll-unpack";
    godot-launch = "${launch}/bin/mega-man-rock-n-roll-godot";
  };
}
