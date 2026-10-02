{ pkgs }:
let
  src = import ./source.nix { inherit pkgs; };
  tools = import ./tools.nix { inherit pkgs; };
  sdl = import ./sdl.nix { inherit pkgs; };
  # Same requireFile boundary as skate-3-flake/package-source.nix. This exact
  # headerless input is specified by upstream and measured from the owned ROM.
  rom = pkgs.requireFile {
    name = "ar.sfc";
    sha256 = "b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0";
    message = ''
      ActRaiser needs your owned, headerless USA ROM as ar.sfc (1,048,576 bytes).
      On a private build machine, use: nix-store --add-fixed sha256 /path/to/ar.sfc
      The ROM and build outputs must not enter public caches or release assets.
      The local Nix store is readable by other local accounts.
    '';
  };
in
pkgs.stdenv.mkDerivation {
  pname = "actraiser";
  version = "0-unstable-cdd7608";
  inherit src;
  nativeBuildInputs = [
    pkgs.cmake
    pkgs.ninja
    pkgs.pkg-config
  ];
  buildInputs = [
    sdl.sdl3
    sdl.ttf
  ];
  preConfigure = ''
    ${tools.builder}/bin/actraiser-builder native-source --root . --rom ${rom}
    ${tools.snesbuild}/bin/snesbuild regen --root . --rom ${rom} --allow-stubs
  '';
  cmakeFlags = [
    "-DCMAKE_BUILD_TYPE=Release"
    "-DBUILD_TESTING=OFF"
    "-DACTRAISER_ENABLE_RUN_DIR_BY_DEFAULT=OFF"
    "-DSNESRECOMP_ENABLE_TRACE_RECORDER=OFF"
    "-DSNESRECOMP_ENABLE_TRACE=OFF"
    "-DSNESRECOMP_WATCHDOG=OFF"
    # Build the helper separately with pinned Go modules. CMake otherwise
    # invokes Go with a network-dependent module cache inside the C build.
    "-DACTRAISER_GO_EXECUTABLE=ACTRAISER_GO_EXECUTABLE-NOTFOUND"
  ];
  installPhase = ''
    runHook preInstall
    install -Dm755 ActRaiserRecomp "$out/libexec/ActRaiserRecomp"
    ln -s ${tools.builder}/bin/actraiser-builder "$out/libexec/actraiser-builder"
    resources="$out/share/ActRaiserRecomp"
    mkdir -p "$resources/defaults/game-assets" "$resources/game-assets"
    cp ../installer/packaging/templates/config.ini ../diorama-layers.ini "$resources/defaults/"
    cp ../installer/internal/builder/assets/manifest.ini "$resources/defaults/game-assets/"
    cp -r ../game-assets/fonts "$resources/game-assets/"
    cp -r ../game-assets/languages "$resources/game-assets/"
    install -Dm644 ../LICENSE "$resources/licenses/ActRaiser.txt"
    install -Dm644 ../snesrecomp-go/THIRD_PARTY_NOTICES.md "$resources/licenses/runner-notices.md"
    install -Dm644 ../snesrecomp-go/runtime/LICENSE "$resources/licenses/runner-MIT.txt"
    install -Dm644 ../snesrecomp-go/runtime/licenses/Snaggletooth-LICENSE.txt "$resources/licenses/Snaggletooth.txt"
    install -Dm644 ../third_party/sheenbidi/LICENSE "$resources/licenses/SheenBidi.txt"
    runHook postInstall
  '';
  allowSubstitutes = false;
  preferLocalBuild = true;
  meta = {
    description = "Private native ActRaiser build from an owned USA ROM";
    license = pkgs.lib.licenses.unfree;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
  };
}
