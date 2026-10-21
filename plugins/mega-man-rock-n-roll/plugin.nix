# Mega Man Rock N Roll. plugin.ts declares the game, its ZIP artifact and the
# FEX runner, and names the files below. The ZIP is not in the closure:
# korrid downloads the file plugin.ts pins into its cache and runs
# game-unpack on it. The runner uses @korri:fex only for its rootfs artifact,
# which korrid downloads (ADR 0012/0013); it requires no other publisher's
# package. The FEX configuration is this plugin's own native file.
{ pkgs }:
let
  unpack = pkgs.writeShellApplication {
    name = "mega-man-rock-n-roll-unpack";
    runtimeInputs = [ pkgs.python3 ];
    text = ''exec python3 ${./game/unpack.py} ${./game/contents} "$@"'';
  };
  # Korri runs games in a systemd unit with RestrictSUIDSGID=yes. Its seccomp
  # filter refuses openat2, which FEX uses with RESOLVE_IN_ROOT to look guest
  # files up in the RootFS; FEX then treated every RootFS library as missing
  # ("libX11.so.6: cannot open shared object file" on the RG353M). The patch
  # falls back to openat relative to the RootFS, as FEX already does for EXDEV.
  fex = pkgs.fex.overrideAttrs (old: {
    patches = (old.patches or [ ]) ++ [ ./runner/fex-openat2-seccomp-fallback.patch ];
  });
  launch = pkgs.writeShellApplication {
    name = "mega-man-rock-n-roll-fex";
    runtimeInputs = [ fex ];
    text = builtins.readFile ./runner/fex-launch.sh;
  };
  fexConfig = pkgs.runCommand "mega-man-rock-n-roll-fex-config" { } ''
    mkdir -p "$out/share"
    cp -r ${./fex} "$out/share/fex-emu"
  '';
in
{
  packages = {
    mega-man-rock-n-roll-unpack = unpack;
    mega-man-rock-n-roll-fex = launch;
    mega-man-rock-n-roll-fex-config = fexConfig;
  };
  files = {
    game-unpack = "${unpack}/bin/mega-man-rock-n-roll-unpack";
    fex-launch = "${launch}/bin/mega-man-rock-n-roll-fex";
    fex-config = "${fexConfig}/share/fex-emu";
  };
}
