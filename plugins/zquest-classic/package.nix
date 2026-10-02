{ pkgs }:
let
  inherit (pkgs) lib;
  # Pins and ARM tile fix harvested from Korri legacy's ZQuest package.
  stduuid = pkgs.fetchFromGitHub {
    owner = "mariusbancila";
    repo = "stduuid";
    rev = "3afe7193facd5d674de709fccc44d5055e144d7a";
    sha256 = "1y7jgf45dydq0jlac5clnanwcc22la4y8c83d5i0rp87x2zll6ij";
  };
  allegro5 = pkgs.fetchFromGitHub {
    owner = "connorjclark";
    repo = "allegro5";
    rev = "7fe12cad20d57e79273af0e51dbda897d60d8dfd";
    sha256 = "143ydhf1kig7hab3wg5li5v56x3aiy7wyf0sihbamx112rw5jivc";
  };
  gme = pkgs.fetchFromGitHub {
    owner = "libgme";
    repo = "game-music-emu";
    rev = "05a2aa29e8eae29316804fdd28ceaa96c74a1531";
    sha256 = "0hn5fvfnrcgsyg5k0ls17dcph9h7cr34q9pyjbawvw16qjl6v3sf";
  };
  poolSTL = pkgs.fetchFromGitHub {
    owner = "alugowski";
    repo = "poolSTL";
    rev = "26d95b90aea7c36732a2df50df1c6fa26c96f93e";
    sha256 = "1likzpanrhlqsvdji1dy0ya067knb7ixq4hnw5rl7m87qrj1cjr5";
  };
in
pkgs.stdenv.mkDerivation {
  pname = "zquest-classic";
  version = "unstable-2026-06-18";
  src = pkgs.fetchFromGitHub {
    owner = "ZQuestClassic";
    repo = "ZQuestClassic";
    rev = "882c906b17e35b4105188e6305ae2929aeba30e3";
    sha256 = "02fs0fm9wih9ly23ivxcvr346cj0dkg7yxsf97q7xzyw6vk36n2y";
  };
  patches = [
    ./standalone-quest-path.patch
  ]
  ++ lib.optional pkgs.stdenv.hostPlatform.isAarch64 ./aarch64-disable-x86-tile-simd.patch;
  patchFlags = [ "-p0" ];
  nativeBuildInputs = with pkgs; [
    cmake
    ninja
    pkg-config
    flex
    bison
    python3
    perl
  ];
  buildInputs = with pkgs; [
    curl
    freetype
    gtk3
    libGL
    libGLU
    freeglut
    xorg.libX11
    xorg.libXcursor
    xorg.libXext
    xorg.libXfixes
    xorg.libXinerama
    xorg.libXrandr
    xorg.libXrender
    alsa-lib
    libpulseaudio
    openssl
    util-linux
    zlib
  ];
  postPatch = ''
    substitute ${./FindLibuuid.cmake} cmake/FindLibuuid.cmake \
      --subst-var-by uuidLib ${lib.getLib pkgs.util-linux} \
      --subst-var-by uuidDev ${pkgs.util-linux.dev}
    substituteInPlace CMakeLists.txt \
      --replace-fail '-Werror=format' '-Werror=format -Wno-error=format-truncation'
    substituteInPlace packaging/CMakeLists.txt \
      --replace-fail 'list(APPEND ZC_INSTALL_TARGETS zlauncher zplayer zeditor zscript zcsound)' \
                     'list(APPEND ZC_INSTALL_TARGETS zplayer zcsound)'
  ''
  + lib.optionalString pkgs.stdenv.hostPlatform.isAarch64 ''
    substituteInPlace CMakeLists.txt --replace-fail 'add_compile_options(-mssse3)' '# x86-only SIMD disabled for aarch64'
  '';
  cmakeGenerator = "Ninja Multi-Config";
  NIX_LDFLAGS = [
    "-L${lib.getLib pkgs.util-linux}/lib"
    "-luuid"
  ];
  NIX_CFLAGS_COMPILE = lib.optional pkgs.stdenv.hostPlatform.isAarch64 "-fsigned-char";
  cmakeFlags = [
    "-DCOPY_RESOURCES=ON"
    "-DCMAKE_POLICY_VERSION_MINIMUM=3.5"
    "-DWANT_NFD=OFF"
    "-DWANT_ZUPDATER=OFF"
    "-DWANT_WEBSOCKETS=OFF"
    "-DWANT_GIT_HOOKS=OFF"
    "-DWANT_ZC_TESTS=OFF"
    "-DJIT_BACKEND=none"
    "-DFETCHCONTENT_SOURCE_DIR_STDUUID=${stduuid}"
    "-DFETCHCONTENT_SOURCE_DIR_ALLEGRO5=${allegro5}"
    "-DFETCHCONTENT_SOURCE_DIR_GME_EXTERNAL=${gme}"
    "-DFETCHCONTENT_SOURCE_DIR_POOLSTL=${poolSTL}"
  ];
  buildPhase = ''
    runHook preBuild
    cmake --build . --config Release --target zplayer --parallel "$NIX_BUILD_CORES"
    runHook postBuild
  '';
  installPhase = ''
    runHook preInstall
    cmake --install . --config Release --prefix "$out"
    # These optional editor/example assets contain Git LFS pointers in the
    # source archive. A player package must not advertise them as real quests.
    rm -r "$out/share/zquestclassic/quests" "$out/share/zquestclassic/tilesets"
    # FetchContent overrides bypass upstream's dependency-license collection.
    mkdir -p "$out/share/zquestclassic/licenses/pinned-dependencies"
    cp ${stduuid}/LICENSE "$out/share/zquestclassic/licenses/pinned-dependencies/stduuid.txt"
    cp ${allegro5}/LICENSE.txt "$out/share/zquestclassic/licenses/pinned-dependencies/allegro5.txt"
    cp ${gme}/license.txt "$out/share/zquestclassic/licenses/pinned-dependencies/gme.txt"
    cp ${gme}/license.gpl2.txt "$out/share/zquestclassic/licenses/pinned-dependencies/gme-gpl2.txt"
    cp ${poolSTL}/LICENSE-Boost.txt "$out/share/zquestclassic/licenses/pinned-dependencies/poolSTL-Boost.txt"
    cp ${poolSTL}/LICENSE-BSD.txt "$out/share/zquestclassic/licenses/pinned-dependencies/poolSTL-BSD.txt"
    cp ${poolSTL}/LICENSE-MIT.txt "$out/share/zquestclassic/licenses/pinned-dependencies/poolSTL-MIT.txt"
    runHook postInstall
  '';
  meta = {
    description = "ZQuest Classic native quest player";
    homepage = "https://github.com/ZQuestClassic/ZQuestClassic";
    license = lib.licenses.gpl3Plus;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "zplayer";
  };
}
