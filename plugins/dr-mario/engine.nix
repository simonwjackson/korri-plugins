{ pkgs }:
let
  framework = pkgs.fetchFromGitHub {
    owner = "mstan";
    repo = "nesrecomp";
    rev = "7f6377b74f2c1e9d1171f707dc003f71c2dc236f";
    hash = "sha256-IO9C+HpUVJ+gEzjwwN5eHIQF0ox8f2BEB2ETP30WZ3k=";
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
  version = "0-unstable-a234728";
  src = pkgs.fetchFromGitHub {
    owner = "mstan";
    repo = "DrMarioNesRecomp";
    rev = "a23472870e0a86dc0c94d88ac1ee3be5a7ea80f9";
    hash = "sha256-0G4PKkWeSr1ceTyXrEGUOTgzJz5+RfGc3HDaSkv5aRk=";
  };

  # These are the upstream gitlinks. Netplay is disabled and needs no nested
  # recomp-net checkout. The committed generated C builds without a retail ROM.
  postUnpack = ''
    cp -R ${framework}/. "$sourceRoot/nesrecomp/"
    cp -R ${launcherUi}/. "$sourceRoot/recomp-ui/"
    chmod -R u+w "$sourceRoot"
  '';
  patches = [
    ./account-storage.patch
    ./literal-rom-path.patch
    # Europe-only runner: derive video, CPU and audio from PAL hardware clocks.
    ./pal-timing.patch
  ];
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
    homepage = "https://github.com/mstan/DrMarioNesRecomp";
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
