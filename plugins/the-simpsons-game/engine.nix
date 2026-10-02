# Generated guest code is included upstream. Keep this output private.
{ pkgs }:
pkgs.llvmPackages_20.stdenv.mkDerivation {
  pname = "simpsons-recomp";
  version = "0.0.6.2";

  src = pkgs.fetchFromGitHub {
    owner = "YesterMester";
    repo = "TheSimpsonsGameRecomp";
    rev = "f63f57bcba29d3e7016fd867fad05adc85822bcb";
    hash = "sha256-bEsIhcMt8VErYE1xyCo2CG4FzALvFJ+2WEsc4DSOsYI=";
  };

  # Preserve native filenames, but put config and logs under user_data_root.
  patches = [ ./account-storage.patch ];

  nativeBuildInputs = with pkgs; [
    cmake
    ninja
    pkg-config
    python3
    autoPatchelfHook
    wrapGAppsHook3
  ];
  buildInputs = with pkgs; [
    gtk3
    glib
    xorg.libX11
    xorg.libxcb
    xorg.libXext
    xorg.libXrandr
    xorg.libXcursor
    xorg.libXi
    xorg.libXfixes
    xorg.libXScrnSaver
    libxkbcommon
    vulkan-headers
    vulkan-loader
    alsa-lib
    libpulseaudio
    pipewire
    systemd
    libusb1
    libunwind
    liburing
    dbus
  ];

  dontUseCmakeConfigure = true;
  configurePhase = ''
    runHook preConfigure
    cmake -S simpsons -B build -G Ninja \
      -DCMAKE_BUILD_TYPE=Release \
      -DREXSDK_DIR="$PWD/tools/rexglue-sdk" \
      -DREXGLUE_ENABLE_TRACY=OFF \
      -DFETCHCONTENT_FULLY_DISCONNECTED=ON
    runHook postConfigure
  '';
  buildPhase = ''
    runHook preBuild
    cmake --build build --target simpsons --parallel "$NIX_BUILD_CORES"
    runHook postBuild
  '';
  installPhase = ''
    runHook preInstall
    mkdir -p "$out/bin" "$out/lib"
    install -m755 build/simpsons "$out/bin/simpsons"
    install -m755 tools/rexglue-sdk/out/linux-*/librexruntime.so "$out/lib/"
    runHook postInstall
  '';
  # SDL_steamstorage.c marks this dlopen library as SUGGESTED, not required.
  # Korri uses the game's native saves rather than Steam remote storage.
  autoPatchelfIgnoreMissingDeps = [ "libsteam_api.so" ];

  preFixup = ''
    gappsWrapperArgs+=(
      --prefix LD_LIBRARY_PATH : "${
        pkgs.lib.makeLibraryPath [ pkgs.vulkan-loader ]
      }:/run/opengl-driver/lib"
    )
  '';

  # The upstream GPL covers handwritten code, not permission to redistribute
  # the translated retail executable. There is no public cache publication.
  meta = {
    description = "Native recompilation of The Simpsons Game for Xbox 360";
    homepage = "https://github.com/YesterMester/TheSimpsonsGameRecomp";
    license = pkgs.lib.licenses.unfree;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "simpsons";
  };
}
