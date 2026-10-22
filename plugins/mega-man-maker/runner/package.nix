# The runner program: proton-launch.sh inside an FHS environment. Proton's
# prebuilt arm64 Wine expects /lib/ld-linux-aarch64.so.1, Python 3 and common
# desktop libraries at FHS paths. The library list follows the Steam plugin's
# FHS (korri-os/plugins plugins/steam/packages/steam-korri/fhs.nix), which
# runs the same Proton build on the Mini V2, without Steam-client-only
# packages. Proton ships its own Wine-side libraries in files/lib.
{ pkgs }:
let
  launch = pkgs.writeShellApplication {
    name = "mega-man-maker-proton-inner";
    runtimeInputs = [
      pkgs.coreutils
      pkgs.python3
    ];
    text = builtins.readFile ./proton-launch.sh;
  };
in
pkgs.buildFHSEnv {
  name = "mega-man-maker-proton";
  privateTmp = true;
  targetPkgs =
    p: with p; [
      bash
      coreutils
      python3
    ];
  multiPkgs =
    p: with p; [
      alsa-lib
      dbus.lib
      expat
      fontconfig
      freetype
      glib
      glibc
      gnutls
      libdrm
      libgbm
      libGL
      libpulseaudio
      libudev0-shim
      libxkbcommon
      sdl2-compat
      udev
      vulkan-loader
      wayland
      xorg.libX11
      xorg.libXcomposite
      xorg.libXcursor
      xorg.libXext
      xorg.libXfixes
      xorg.libXi
      xorg.libXinerama
      xorg.libXrandr
      xorg.libXrender
      xorg.libxcb
      xorg.libxshmfence
      zlib
    ];
  runScript = "${launch}/bin/mega-man-maker-proton-inner";
}
