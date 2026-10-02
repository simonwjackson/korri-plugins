# Use the extractor shipped with the pinned upstream release.
{ pkgs, src }:
pkgs.stdenv.mkDerivation {
  pname = "simpsons-extract-xiso";
  version = "0.0.6.2";
  inherit src;
  postUnpack = ''
    sourceRoot="$sourceRoot/tools/extract-xiso"
  '';
  nativeBuildInputs = [
    pkgs.cmake
    pkgs.ninja
  ];
  postInstall = ''
    install -Dm644 ../extract-xiso.c "$out/share/doc/extract-xiso/extract-xiso.c"
  '';
  meta = {
    description = "Xbox ISO extractor shipped with The Simpsons Game Recompiled";
    license = pkgs.lib.licenses.bsdOriginal;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "extract-xiso";
  };
}
