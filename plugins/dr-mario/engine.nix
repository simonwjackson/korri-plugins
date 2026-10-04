{ pkgs }:
let
  framework = pkgs.fetchFromGitHub {
    owner = "simonwjackson";
    repo = "nesrecomp";
    rev = "e3d9f1944661e9afe2a8ccf42e39b9af82410968";
    hash = "sha256-Xp2oPmzjG0z3EKL9wD9mTp8SuhQ7nBuW5JV2YhLseWY=";
  };
  launcherUi = pkgs.fetchFromGitHub {
    owner = "mstan";
    repo = "recomp-ui";
    rev = "44f549c0f159df343cba9d8c3842dbc7e592eb08";
    hash = "sha256-MntZvAc+NoASRXEttrP380mizBzvuh19OqMilU7PNBA=";
  };
in
pkgs.stdenv.mkDerivation {
  pname = "drmario-nes-recomp";
  version = "0-unstable-f814fda";
  src = pkgs.fetchFromGitHub {
    owner = "simonwjackson";
    repo = "DrMarioNesRecomp";
    rev = "f814fda8da7fcbeb863e48bdc632cb3527761474";
    hash = "sha256-VLH1umijNGn1X0tkL03sgEGIDiO3zWpXYaBb5jF32wU=";
  };

  # These are the maintained game's gitlinks; the UI remains upstream.
  # Netplay needs no nested recomp-net checkout. Generated C needs no ROM.
  postUnpack = ''
    cp -R ${framework}/. "$sourceRoot/nesrecomp/"
    cp -R ${launcherUi}/. "$sourceRoot/recomp-ui/"
    chmod -R u+w "$sourceRoot"
  '';
  nativeBuildInputs = [ pkgs.cmake ];
  buildInputs = [
    pkgs.SDL2
    pkgs.libGL
    pkgs.xorg.libX11
  ];
  cmakeFlags = [
    "-DDRMARIO_REGION=eu"
    "-DNESRECOMP_ENABLE_TRACE=OFF"
    "-DNESRECOMP_ENABLE_NET=OFF"
    "-DSDL2_DIR=${pkgs.SDL2.dev}/lib/cmake/SDL2"
  ];
  installPhase = ''
    runHook preInstall
    install -Dm755 DrMarioRecomp "$out/bin/DrMarioRecomp"
    cp -R assets "$out/bin/assets"
    licenses="$out/share/licenses/DrMarioRecomp"
    mkdir -p "$licenses"
    cp ../LICENSE "$licenses/DrMario-LICENSE.txt"
    cp ../nesrecomp/LICENSE "$licenses/NESRecomp-LICENSE.txt"
    cp ../recomp-ui/src/third_party/imgui/LICENSE.txt "$licenses/ImGui-LICENSE.txt"
    cp ../recomp-ui/assets/common/fonts/NOTICE.md "$licenses/font-NOTICE.md"
    cp ../recomp-ui/src/third_party/tinyfiledialogs.c "$licenses/tinyfiledialogs.c"
    runHook postInstall
  '';

  meta = {
    description = "Dr. Mario NES static recompilation for the owned Europe ROM";
    homepage = "https://github.com/simonwjackson/DrMarioNesRecomp";
    # Upstream PolyForm Noncommercial 1.0.0, with translated retail game code.
    # This is not permission to publish native binaries or retail data.
    license = pkgs.lib.licenses.unfree;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "DrMarioRecomp";
  };
}
