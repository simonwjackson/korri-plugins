# The FHS environment Proton-CachyOS arm64 runs in. Proton's binaries are
# built for a glibc distribution layout, so they cannot run from the Nix store
# directly. The library list is legacy Korri's Mega Man Arena aarch64 FHS
# environment (product/plugins/mega-man-arena/packages/mega-man-arena), less
# FEX: this Proton build emulates x86 Windows code itself.
{ pkgs }:
let
  launch = pkgs.writeShellApplication {
    name = "mega-man-arena-proton-launch";
    runtimeInputs = [ pkgs.coreutils ];
    text = builtins.readFile ./proton-launch.sh;
  };
in
pkgs.buildFHSEnv {
  name = "mega-man-arena-proton";
  executableName = "mega-man-arena-proton";
  privateTmp = true;
  includeClosures = true;

  targetPkgs =
    p: with p; [
      bash
      coreutils
      dbus
      file
      findutils
      gnugrep
      gnused
      pciutils
      python3
      util-linux
      xorg.xrandr
    ];

  multiPkgs =
    p: with p; [
      alsa-lib
      at-spi2-core
      cairo
      cups.lib
      dbus.lib
      expat
      fontconfig
      freetype
      fribidi
      gdk-pixbuf
      glib
      glibc
      gtk2
      harfbuzz
      libcap
      libdrm
      libgbm
      libGL
      libpulseaudio
      libudev0-shim
      libva
      libxkbcommon
      libxml2
      nspr
      nss
      openal
      pango
      pipewire
      sdl2-compat
      sqlite
      udev
      vulkan-loader
      wayland
      xorg.libICE
      xorg.libSM
      xorg.libX11
      xorg.libXcomposite
      xorg.libXcursor
      xorg.libXdamage
      xorg.libXext
      xorg.libXfixes
      xorg.libXi
      xorg.libXinerama
      xorg.libXrandr
      xorg.libXrender
      xorg.libXScrnSaver
      xorg.libXtst
      xorg.libxcb
      xorg.libxshmfence
      zlib
    ];

  profile = ''
    unset GIO_EXTRA_MODULES
  '';

  runScript = "${launch}/bin/mega-man-arena-proton-launch";
}
