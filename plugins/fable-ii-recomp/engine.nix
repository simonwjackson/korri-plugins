# Private source build: default.xex and all translated code must stay out of
# public caches. Only the public handwritten sources are fetched over the net.
{ pkgs }:
let
  inherit (pkgs) lib;
  sources = import ./source.nix { inherit pkgs; };
  xexSha256 = "88c4ef2e18e65409444d1b068eff921d1f7e180a5ae64edc64ba6b0872372662";
  defaultXex = pkgs.requireFile {
    name = "default.xex";
    sha256 = xexSha256;
    message = ''
      Fable II needs default.xex from your own USA/Europe GOTY disc, without
      a title update (SHA-256 ${xexSha256}). Extract your ISO locally, then run:

        nix-store --add-fixed sha256 /path/to/extracted/default.xex

      Do not upload the ISO, XEX, generated code, or engine to a public cache.
    '';
  };
  # Match the SDK's linux-amd64 / linux-arm64 native presets.
  isArm = pkgs.stdenv.hostPlatform.isAarch64;
  isa = if isArm then "armv8-a" else "x86-64-v2";
  sdkPlatform = if isArm then "linux-arm64" else "linux-amd64";
  # SDL is linked statically, but dlopens its video/audio/input backends.
  runtimeLibs = with pkgs; [
    stdenv.cc.cc.lib
    xorg.libX11
    xorg.libxcb
    xorg.libXext
    xorg.libXrandr
    xorg.libXcursor
    xorg.libXi
    xorg.libXfixes
    xorg.libXScrnSaver
    xorg.libXtst
    libxkbcommon
    libglvnd
    wayland
    libdecor
    alsa-lib
    libpulseaudio
    pipewire
    systemd
    libusb1
    libunwind
    liburing
    dbus
    vulkan-loader
    openxr-loader
  ];
in
assert pkgs.stdenv.buildPlatform.system == pkgs.stdenv.hostPlatform.system;
pkgs.llvmPackages_20.stdenv.mkDerivation {
  pname = "fable-ii-recomp";
  version = "0-unstable-f3ae1ad";
  src = sources.game;

  nativeBuildInputs = with pkgs; [
    cmake
    ninja
    pkg-config
    python3
    wayland-scanner
    autoPatchelfHook
    makeWrapper
  ];
  buildInputs =
    runtimeLibs
    ++ (with pkgs; [
      wayland-protocols
      vulkan-headers
    ]);

  postPatch = ''
    cp -r --no-preserve=mode,ownership ${sources.sdk} rexglue-sdk
    patch -p1 -d rexglue-sdk < ${./patches/sdk-keep-open.patch}
    patch -p1 -d rexglue-sdk < ${./patches/sdk-tessellation.patch}
    patch -p1 -d rexglue-sdk < ${./patches/account-storage.patch}

    # fetchgit removes .git. Check the pinned submodule directories instead.
    substituteInPlace rexglue-sdk/thirdparty/CMakeLists.txt \
      --replace-fail '"''${CMAKE_CURRENT_SOURCE_DIR}/''${submodule}/.git"' \
                     '"''${CMAKE_CURRENT_SOURCE_DIR}/''${submodule}"'

    # Feed the existing version producer the measured git-describe inputs.
    # This preserves 0.10.0.2-dev.gc94f5eb without Git at build time, including
    # when the SDK is a subdirectory of the game (CMAKE_SOURCE_DIR differs).
    # No version API or generated header is patched.
    substituteInPlace rexglue-sdk/CMakeLists.txt \
      --replace-fail 'rex_resolve_version(REXGLUE_FULL_VERSION' \
        'rex_compute_version(REXGLUE_FULL_VERSION
    GIT_DESCRIBE_LONG "v0.10.0-2-gc94f5eb"
    GIT_DESCRIBE_EXACT ""
    BRANCH_NAME ""'

    mkdir -p assets-extracted/00007000
    cp ${defaultXex} assets-extracted/00007000/default.xex
    echo '${xexSha256}  assets-extracted/00007000/default.xex' | sha256sum -c -
  '';

  dontUseCmakeConfigure = true;
  configurePhase = ''
    runHook preConfigure
    cmake -S rexglue-sdk -B sdk-build -G Ninja \
      -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX" \
      -DCMAKE_C_FLAGS=-march=${isa} -DCMAKE_CXX_FLAGS=-march=${isa} \
      -DFETCHCONTENT_FULLY_DISCONNECTED=ON
    grep -q '^#define SDL_VIDEO_DRIVER_WAYLAND 1$' \
      sdk-build/thirdparty/sdl3/include-config-relwithdebinfo/build_config/SDL_build_config.h
    runHook postConfigure
  '';
  buildPhase = ''
    runHook preBuild
    # The CLI needs its shared dependencies before the install/fixup phase.
    export LD_LIBRARY_PATH="$PWD/rexglue-sdk/out/${sdkPlatform}:${lib.makeLibraryPath runtimeLibs}"
    cmake --build sdk-build --target rexglue --parallel "$NIX_BUILD_CORES"
    rexglue-sdk/out/${sdkPlatform}/rexgluerd --version
    rexglue-sdk/out/${sdkPlatform}/rexgluerd codegen fable_ii_manifest.toml

    # Keep Oery's original UI/ImGui linkage. Consume the same patched SDK
    # source so its rex_app.cpp (including keep-open) is compiled into the host.
    cmake -S . -B build -G Ninja \
      -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DCMAKE_C_COMPILER="$CC" -DCMAKE_CXX_COMPILER="$CXX" \
      -DCMAKE_C_FLAGS=-march=${isa} -DCMAKE_CXX_FLAGS=-march=${isa} \
      -DREXSDK_DIR="$PWD/rexglue-sdk" \
      -DFETCHCONTENT_FULLY_DISCONNECTED=ON
    grep -q '^#define SDL_VIDEO_DRIVER_WAYLAND 1$' \
      build/rexglue-sdk/thirdparty/sdl3/include-config-relwithdebinfo/build_config/SDL_build_config.h
    cmake --build build --target fable_ii --parallel "$NIX_BUILD_CORES"
    runHook postBuild
  '';
  installPhase = ''
    runHook preInstall
    mkdir -p "$out/bin" "$out/libexec/fable-ii-recomp" "$out/share/doc/fable-ii-recomp"
    install -m755 build/fable_ii "$out/libexec/fable-ii-recomp/fable_ii"
    # The native GPU loader resolves the rd plugin beside the actual ELF.
    install -m755 rexglue-sdk/out/${sdkPlatform}/librexruntimerd.so \
      rexglue-sdk/out/${sdkPlatform}/libTracyClientrd.so \
      rexglue-sdk/out/${sdkPlatform}/librexgpu-xenosrd.so \
      "$out/libexec/fable-ii-recomp/"
    printf '%s\n' \
      'Oery/fable-ii-recomp ${sources.game.rev}' \
      'rexglue/rexglue-sdk ${sources.sdk.rev} (v0.10.0-2-gc94f5eb)' \
      'default.xex SHA-256 ${xexSha256}; no title update' \
      > "$out/share/doc/fable-ii-recomp/source-revisions.txt"
    runHook postInstall
  '';

  # Optional Steam Input is not required for native per-account saves.
  autoPatchelfIgnoreMissingDeps = [ "libsteam_api.so" ];
  preFixup = ''
    # The SDK links its libraries against its build output directory. Replace
    # that path before stdenv checks for /build references; autoPatchelf then
    # resolves the remaining native dependencies from declared buildInputs.
    for binary in "$out/libexec/fable-ii-recomp/"*; do
      patchelf --set-rpath '$ORIGIN' "$binary"
    done
    addAutoPatchelfSearchPath "$out/libexec/fable-ii-recomp"
    makeWrapper "$out/libexec/fable-ii-recomp/fable_ii" "$out/bin/fable_ii" \
      --set LD_LIBRARY_PATH "$out/libexec/fable-ii-recomp:${lib.makeLibraryPath runtimeLibs}:/run/opengl-driver/lib"
  '';

  allowSubstitutes = false;
  passthru = { inherit xexSha256; };
  meta = {
    description = "Private native Fable II recompilation from an owned GOTY executable";
    homepage = "https://github.com/Oery/fable-ii-recomp";
    license = lib.licenses.unfree;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "fable_ii";
  };
}
