{ pkgs }:
pkgs.stdenv.mkDerivation {
  pname = "fable-ii-extract-xiso";
  version = "2.7.1-unstable-2026-09-11";

  src = pkgs.fetchFromGitHub {
    owner = "XboxDev";
    repo = "extract-xiso";
    rev = "3f5b62cfe68f000b0e3c8a30104973f3a297948e";
    hash = "sha256-LvPSyCD8moyV3BLLuMWrXt83CIY/oNNGxoRLt836YIo=";
  };

  nativeBuildInputs = [
    pkgs.cmake
    pkgs.ninja
  ];
  # Upstream still declares CMake 3.5 compatibility.
  cmakeFlags = [ "-DCMAKE_POLICY_VERSION_MINIMUM=3.5" ];

  postInstall = ''
    install -Dm644 ../extract-xiso.c "$out/share/doc/extract-xiso/extract-xiso.c"
  '';

  meta = {
    description = "Xbox ISO extractor for locally owned Fable II discs";
    homepage = "https://github.com/XboxDev/extract-xiso";
    license = pkgs.lib.licenses.bsdOriginal;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "extract-xiso";
  };
}
