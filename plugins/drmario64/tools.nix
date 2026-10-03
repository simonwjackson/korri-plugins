{ pkgs }:
let
  source = import ./source.nix { inherit pkgs; };
  arch = if pkgs.stdenv.hostPlatform.isAarch64 then "arm64" else "x64";
in
{
  # These are the generation pins in upstream's README, not the different
  # N64Recomp/decomp gitlinks used to compile the runtime and MIPS patches.
  recompiler = pkgs.llvmPackages_19.stdenv.mkDerivation {
    pname = "drmario64-recompiler";
    version = "0-unstable-a13e5cf";
    src = pkgs.fetchgit {
      name = "N64Recomp-a13e5cf";
      url = "https://github.com/Mr-Wiseguy/N64Recomp";
      rev = "a13e5cff96686776b0e03baf23923e3c1927b770";
      hash = "sha256-r8TzxraPvRPib6nU4ddTYQJ/StwXP9yOBCEaXGb76sg=";
      fetchSubmodules = true;
    };
    nativeBuildInputs = [
      pkgs.cmake
      pkgs.ninja
    ];
    cmakeFlags = [
      "-GNinja"
      "-DCMAKE_POLICY_VERSION_MINIMUM=3.5"
    ];
    buildPhase = ''
      runHook preBuild
      ninja -j "$NIX_BUILD_CORES" N64RecompCLI RSPRecomp
      runHook postBuild
    '';
    installPhase = ''
      mkdir -p "$out/bin"
      cp N64Recomp RSPRecomp "$out/bin/"
    '';
  };

  decomp = pkgs.fetchFromGitHub {
    owner = "AngheloAlf";
    repo = "drmario64";
    rev = "91dab37987bdad4d100958685cc10a011d4917dd";
    hash = "sha256-3W09MIEM/yQWFB/9jBo/W8G7gz0nVgnmwW9G71i8zpc=";
  };

  # Preserve RT64's exact compiler binaries. They are build-only on Linux.
  dxc = pkgs.stdenv.mkDerivation {
    pname = "drmario64-dxc";
    version = "0-unstable-cc15e71";
    dontUnpack = true;
    nativeBuildInputs = [ pkgs.autoPatchelfHook ];
    buildInputs = [
      pkgs.stdenv.cc.cc.lib
      pkgs.zlib
    ];
    installPhase = ''
      mkdir -p "$out/bin" "$out/lib"
      cp ${source}/lib/rt64/src/contrib/dxc/bin/${arch}/dxc-linux "$out/bin/dxc"
      cp ${source}/lib/rt64/src/contrib/dxc/lib/${arch}/*.so "$out/lib/"
      chmod +x "$out/bin/dxc"
    '';
  };
}
