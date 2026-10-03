{ pkgs }:
let
  src = import ./source.nix { inherit pkgs; };
  tools = import ./tools.nix { inherit pkgs; };
  rom = pkgs.requireFile {
    name = "drmario64.us.z64";
    sha256 = "bb2c0dec0a8287ad256929563d0509801c2f239df883c1cf52cab05b23bd77b6";
    message = ''
      This private build needs your owned US Dr. Mario 64 ROM in big-endian
      byte order as drmario64.us.z64 (4,194,304 bytes).
      On a private build machine: nix-store --add-fixed sha256 /path/to/drmario64.us.z64
      Keep the ROM and generated native code out of Git and public caches.
      The local Nix store is readable by other local accounts.
    '';
  };
in
pkgs.llvmPackages_19.stdenv.mkDerivation {
  pname = "drmario64-recomp";
  version = "1.0.0-af91e3b";
  inherit src;
  nativeBuildInputs = [
    pkgs.cmake
    pkgs.ninja
    pkgs.pkg-config
    pkgs.python3
    pkgs.llvmPackages_19.lld
  ];
  buildInputs = [
    pkgs.SDL2
    pkgs.gtk3
    pkgs.freetype
    pkgs.xorg.libX11
    pkgs.xorg.libXrandr
    pkgs.vulkan-loader
  ];
  postPatch = ''
    # Run the exact upstream decompressor without importing an entire MIPS
    # disassembler or compression tool just for byte IO, MD5 and CSV parsing.
    mkdir decomp-tools
    cp ${tools.decomp}/tools/compressor/{rom_decompressor.py,compression_common.py,compress_segments.us.csv} decomp-tools/
    substituteInPlace decomp-tools/rom_decompressor.py \
      --replace-fail 'import spimdisasm' 'import hashlib' \
      --replace-fail 'spimdisasm.common.Utils.readFileAsBytearray(inPath)' 'bytearray(inPath.read_bytes())' \
      --replace-fail 'spimdisasm.common.Utils.getStrHash(inRom)' 'hashlib.md5(inRom).hexdigest()'
    substituteInPlace decomp-tools/compression_common.py \
      --replace-fail 'import crunch64' '# crunch64 is only required by the unused compressor' \
      --replace-fail 'import spimdisasm' 'import csv' \
      --replace-fail 'spimdisasm.common.Utils.readCsv(segmentsPath)' 'list(csv.reader(segmentsPath.read_text().splitlines()))'
    # Use the same pinned DXC after fixing its ELF interpreter and library paths.
    # Set after platform selection so CMake retains all shader options.
    substituteInPlace CMakeLists.txt \
      --replace-fail 'build_vertex_shader(drmario64_recomp' 'set(DXC "${tools.dxc}/bin/dxc")
    build_vertex_shader(drmario64_recomp'
    substituteInPlace lib/rt64/CMakeLists.txt \
      --replace-fail 'set(ZSTD_LEGACY_SUPPORT OFF)' 'set(DXC "${tools.dxc}/bin/dxc")
    set(ZSTD_LEGACY_SUPPORT OFF)'
  '';
  preConfigure = ''
    python3 decomp-tools/rom_decompressor.py ${rom} drmario64_uncompressed.us.z64 decomp-tools/compress_segments.us.csv us
    ln -s ${tools.recompiler}/bin/N64Recomp N64Recomp
    ${tools.recompiler}/bin/N64Recomp drmario64.us.toml
    ${tools.recompiler}/bin/RSPRecomp aspMain.us.toml
    # Upstream's PatchesBin is not connected to the generated patches target.
    # Generate before CMake so dependency ordering cannot race.
    make -C patches CC=${pkgs.llvmPackages_19.clang-unwrapped}/bin/clang LD=${pkgs.llvmPackages_19.lld}/bin/ld.lld -j "$NIX_BUILD_CORES"
    ./N64Recomp patches.toml
  '';
  cmakeFlags = [
    "-GNinja"
    "-DCMAKE_BUILD_TYPE=Release"
    "-DCMAKE_POLICY_VERSION_MINIMUM=3.5"
    "-DRMLUI_SAMPLES=OFF"
    "-DRMLUI_TESTS=OFF"
  ];
  buildPhase = ''
    runHook preBuild
    ninja -j "$NIX_BUILD_CORES" drmario64_recomp
    runHook postBuild
  '';
  installPhase = ''
    runHook preInstall
    install -Dm755 drmario64_recomp "$out/libexec/drmario64_recomp"
    mkdir -p "$out/share/drmario64"
    cp -r ../assets ../icons "$out/share/drmario64/"
    install -Dm644 ../COPYING "$out/share/licenses/drmario64/COPYING"
    runHook postInstall
  '';
  allowSubstitutes = false;
  preferLocalBuild = true;
  meta = {
    description = "Private Dr. Mario 64 native recompilation from an owned US ROM";
    license = pkgs.lib.licenses.unfree;
    platforms = [ "x86_64-linux" "aarch64-linux" ];
  };
}
