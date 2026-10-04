{ pkgs, src }:
# Scene Expansion mod from github:simonwjackson/nocturne-encore, built against
# the ReXGlue SDK nightly that NocturneRecomp v1.4.5 pins in .sdk-version.
# The mod must link the same librexruntime.so ABI as the release binary.
let
  inherit (pkgs) lib;
  sdkTag = "sotn-nightly-20260817-7766f971";
  sdk =
    {
      x86_64-linux = {
        arch = "amd64";
        hash = "sha256-zaEGB/B8vjbWtgqFufyhqcEBfzWcZjHj4wiVc9y2ckY=";
      };
      aarch64-linux = {
        arch = "arm64";
        hash = "sha256-rE6adg1sk9fYD41xvXU3wn0+ghBhsCtERM/ZweTFIIM=";
      };
    }
    .${pkgs.stdenv.hostPlatform.system};
  sdkZip = pkgs.fetchurl {
    url = "https://github.com/birabittoh/rexglue-sdk/releases/download/${sdkTag}/rexglue-sdk-0.9.0-dev.g7766f97-linux-${sdk.arch}.zip";
    inherit (sdk) hash;
  };
in
pkgs.stdenv.mkDerivation {
  pname = "nocturne-scene-expansion";
  version = "0.3.0";
  inherit src;
  nativeBuildInputs = [
    pkgs.cmake
    pkgs.ninja
    pkgs.unzip
    pkgs.llvmPackages_20.clang
  ];
  dontUseCmakeConfigure = true;
  # Keep NEEDED librexruntime.so unresolved by path. At load time it must bind
  # to the copy the game already mapped, never to a second runtime from the SDK.
  dontPatchELF = true;
  buildPhase = ''
    runHook preBuild
    mkdir sdk
    unzip -q ${sdkZip} -d sdk
    cmake -S src/scene_expansion -B build -G Ninja \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_PREFIX_PATH="$PWD/sdk/linux-${sdk.arch}" \
      -DCMAKE_CXX_COMPILER=clang++ \
      -DCMAKE_SKIP_RPATH=ON
    cmake --build build
    runHook postBuild
  '';
  installPhase = ''
    runHook preInstall
    mkdir -p "$out/scene_expansion/code"
    install -m644 build/libscene_expansion.so "$out/scene_expansion/code/libscene_expansion.so"
    install -m644 src/scene_expansion/mod.toml "$out/scene_expansion/mod.toml"
    install -m644 src/scene_expansion/README.md "$out/scene_expansion/README.md"
    runHook postInstall
  '';
  meta = {
    description = "NocturneRecomp mod that shows scenery beside the original view";
    homepage = "https://github.com/simonwjackson/nocturne-encore";
    license = lib.licenses.mit;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
  };
}
