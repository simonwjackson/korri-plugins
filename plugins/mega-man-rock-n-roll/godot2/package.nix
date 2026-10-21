# Godot 2.1.4 runtime: the X11 export template built from the pinned upstream
# tag, so the game's data.pck runs natively on aarch64 and x86_64. The game's
# own executable is the stock 2.1.4 template with no custom modules, so this
# engine plus data.pck is the whole game. Build machines compile it; devices
# receive the result.
{ pkgs }:
let
  inherit (pkgs) lib;
in
# x11/detect.py refuses GCC 6+ for this branch and names Clang instead.
pkgs.clangStdenv.mkDerivation {
  pname = "godot2-runtime";
  version = "2.1.4";

  src = pkgs.fetchFromGitHub {
    owner = "godotengine";
    repo = "godot";
    rev = "2.1.4-stable";
    sha256 = "0d2zczn5k7296sky5gllq55cxd586nx134y2iwjpkqqjr62g0h48";
  };

  patches = [
    # Python 3 and SCons 4 for the build scripts this build reads; pass the
    # Nix compiler wrapper's environment through; accept CXXFLAGS.
    ./scons-python3.patch
    # 2.1.4 has reference counting for x86 and 32-bit ARM only. AArch64 gets
    # the GCC atomic builtins that 2.1.6 uses; other targets are unchanged.
    ./aarch64-safe-refcount.patch
  ];

  # SConstruct imports every platform's detect.py, and the others are
  # Python 2. Only X11 is built.
  postPatch = ''
    find platform -mindepth 1 -maxdepth 1 -type d ! -name x11 -exec rm -r {} +
  '';

  nativeBuildInputs = [
    pkgs.scons
    pkgs.pkg-config
  ];

  buildInputs = with pkgs; [
    libx11
    libxcursor
    libxinerama
    libxrandr
    libxrender
    libGL
    # The bundled glew.h includes GL/glu.h.
    libGLU
    alsa-lib
    libpulseaudio
    freetype
    libpng
    zlib
    libogg
    libvorbis
    libtheora
    libopus
    opusfile
    libwebp
  ];

  sconsFlags = [
    "platform=x11"
    "tools=no"
    "target=release"
    "bits=64"
    "use_llvm=yes"
    "progress=no"
    # 2.1.4 supports OpenSSL 1.0.x only; Nix has 3.x.
    "builtin_openssl=yes"
    # The bundled GLEW 1.13 stays: system GLEW's header needs C++11.
    "builtin_libogg=no"
    "builtin_libvorbis=no"
    "builtin_libtheora=no"
    "builtin_opus=no"
    "builtin_libwebp=no"
    # The code is C++98 (register, narrowing in braces), like GCC 5's default.
    "CXXFLAGS=-std=gnu++98"
    # The engine tests and calls through null Object pointers. Without this
    # the x86_64 build crashed in VisualServerRaster::_render_canvas_item
    # on the game's first scene.
    "CCFLAGS=-fno-delete-null-pointer-checks"
  ];

  buildPhase = ''
    runHook preBuild
    scons -j "$NIX_BUILD_CORES" $sconsFlags
    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall
    install -Dm755 bin/godot.x11.opt.64.llvm "$out/bin/godot2-runtime"
    install -Dm644 LICENSE.txt "$out/share/licenses/godot2-runtime/LICENSE.txt"
    install -Dm644 COPYRIGHT.txt "$out/share/licenses/godot2-runtime/COPYRIGHT.txt"
    runHook postInstall
  '';

  meta = {
    description = "Godot Engine 2.1.4 X11 runtime (export template) for exported game packs";
    homepage = "https://github.com/godotengine/godot/tree/2.1.4-stable";
    license = lib.licenses.mit;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "godot2-runtime";
  };
}
