{ pkgs }:
let
  inherit (pkgs) lib;
  version = "0.3.8";
  runtimeLibraries = map lib.getLib [
    pkgs.libglvnd
    pkgs.libpulseaudio
    pkgs.libx11
    pkgs.libxcursor
    pkgs.libxext
    pkgs.libxfixes
    pkgs.libxi
    pkgs.libxrandr
    pkgs.gtk3
    pkgs.vulkan-loader
    pkgs.alsa-lib
    pkgs.udev
    pkgs.libxrender
    pkgs.wayland
    pkgs.libxkbcommon
    pkgs.libdecor
  ];
in
pkgs.clangStdenv.mkDerivation {
  pname = "opengoal-runtime";
  inherit version;
  src = pkgs.fetchFromGitHub {
    owner = "open-goal";
    repo = "jak-project";
    rev = "6445b4a50a7540df512e3c82c62216521421410c";
    hash = "sha256-BLNlZ1rygOFk+y+cG7MP2HF1PtnUas+YtKVgap8NZxU=";
  };
  patches = [ ./patches/linux-arm64.patch ];
  nativeBuildInputs = [
    pkgs.cmake
    pkgs.ninja
    pkgs.pkg-config
    pkgs.wayland-scanner
    pkgs.patchelf
  ];
  buildInputs = [
    (pkgs.openssl.override { static = true; })
    pkgs.alsa-lib
    pkgs.libpulseaudio
    pkgs.libglvnd
    pkgs.libxcb
    pkgs.libffi
    pkgs.libx11
    pkgs.libxcursor
    pkgs.libxext
    pkgs.libxfixes
    pkgs.libxi
    pkgs.libxrandr
    pkgs.libxkbcommon
    pkgs.wayland
    pkgs.wayland-protocols
    pkgs.libdecor
    pkgs.udev
  ]
  ++ runtimeLibraries;
  cmakeFlags = [
    "-DCMAKE_POLICY_VERSION_MINIMUM=3.10"
    "-DSTATICALLY_LINK=ON"
    "-DCMAKE_EXE_LINKER_FLAGS=-Wl,-z,noexecstack"
  ];
  postConfigure = ''
    # OpenGOAL needs desktop OpenGL, not an SDL build with only GLES support.
    grep -F '#define SDL_VIDEO_OPENGL 1' \
      third-party/SDL/include-config-release/build_config/SDL_build_config.h
    # Release archives have no .git directory for write_revision_h().
    cat > ../common/versions/revision.h <<'EOF'
    #define BUILT_TAG "v${version}-linux-arm64"
    #define BUILT_SHA "6445b4a50a7540df512e3c82c62216521421410c"
    EOF
  '';
  # Upstream's SDL and cubeb backends use dlopen.
  NIX_LDFLAGS = "-rpath ${lib.makeLibraryPath runtimeLibraries}";
  ninjaFlags = [
    "gk"
    "goalc-test"
  ];
  doCheck = true;
  checkPhase = ''
    runHook preCheck
    cd ..
    # The release archive has no jak-project/ path; the test runner discovers data
    # next to its executable before looking for that development directory name.
    ln -s .. build/data
    export HOME="$TMPDIR/home" XDG_CONFIG_HOME="$TMPDIR/home/.config"
    mkdir -p "$XDG_CONFIG_HOME"
    test "$(uname -m)" = aarch64
    build/goalc-test --gtest_filter='ARM64*:Arm64*:NEON*:SkyBlend*' \
      --gtest_output=xml:build/arm-tests.xml
    grep -E '<testsuites tests="[1-9][0-9]*" failures="0"' build/arm-tests.xml
    cd build
    runHook postCheck
  '';
  installPhase = ''
    runHook preInstall
    install -Dm755 game/gk "$out/libexec/opengoal/gk"
    install -Dm644 ../LICENSE "$out/share/licenses/opengoal/LICENSE"
    mkdir -p "$out/bin" "$out/share/opengoal/data/game/graphics/opengl_renderer" \
      "$out/share/opengoal/data/launcher" "$out/share/opengoal/data/log"
    cp -r ../game/assets "$out/share/opengoal/data/game/"
    cp -r ../game/graphics/opengl_renderer/shaders "$out/share/opengoal/data/game/graphics/opengl_renderer/"
    cp -r ../custom_assets "$out/share/opengoal/data/"
    cp ../.github/scripts/releases/error-code-metadata.json "$out/share/opengoal/data/launcher/"
    ln -s ../../share/opengoal/data "$out/libexec/opengoal/data"
    ln -s ../libexec/opengoal/gk "$out/bin/gk"
    runHook postInstall
  '';
  # stdenv shrinks RUNPATH to DT_NEEDED libraries. Restore the SDL/cubeb dlopen
  # backends afterwards so they remain reachable without a launcher wrapper.
  postFixup = ''
    patchelf --add-rpath ${lib.makeLibraryPath runtimeLibraries} "$out/libexec/opengoal/gk"
  '';
  doInstallCheck = true;
  installCheckPhase = ''
    runHook preInstallCheck
    "$out/bin/gk" --version | tee version.txt
    grep -F 'v${version}-linux-arm64' version.txt
    "$out/bin/gk" --help > help.txt
    grep -F -- --proj-path help.txt
    test ! -e "$out/bin/extractor"
    test ! -e "$out/bin/goalc"
    test ! -e "$out/share/opengoal/data/goal_src"
    runHook postInstallCheck
  '';
  meta = {
    description = "OpenGOAL native ARM64 runtime without retail data or preparation tools";
    homepage = "https://opengoal.dev/";
    license = lib.licenses.isc;
    platforms = [ "aarch64-linux" ];
    mainProgram = "gk";
  };
}
