{ pkgs }:
let
  inherit (pkgs) lib;
  release =
    {
      x86_64-linux = {
        arch = "x86_64";
        sha256 = "4d6183c93701c84d268b6d88128949470755e5bd35026024e535a0ba1568b05e";
      };
      aarch64-linux = {
        arch = "aarch64";
        sha256 = "a0ca17d43d8cef1a8d91d171acf74c6d58ef2f2f77324e9cef6367ee3c299a67";
      };
    }
    .${pkgs.stdenv.hostPlatform.system};
  # SDL3 is linked into the release and loads these Linux backends dynamically.
  runtimeDependencies = [
    pkgs.vulkan-loader
    pkgs.libglvnd
    pkgs.libxtst
    pkgs.libx11
    pkgs.libxcb
    pkgs.libxext
    pkgs.libxi
    pkgs.libxrandr
    pkgs.libxcursor
    pkgs.libxfixes
    pkgs.libxscrnsaver
    pkgs.libxkbcommon
    pkgs.wayland
    pkgs.libdecor
    pkgs.alsa-lib
    pkgs.libpulseaudio
    pkgs.pipewire
    pkgs.dbus
    pkgs.udev
    pkgs.libusb1
  ];
  runtimeLibraries = lib.makeLibraryPath runtimeDependencies;
in
pkgs.stdenv.mkDerivation (finalAttrs: {
  pname = "melee-pc";
  version = "0.2.2-beta";
  # Upstream tag resolves to ed0843a6f0d7cbd846e7774925fc0952c522ed95.
  # Tarballs contain no disc image. Recovered game code remains unlicensed.
  src = pkgs.fetchurl {
    url = "https://github.com/999sian/melee-pc/releases/download/v${finalAttrs.version}/melee-linux-${release.arch}.tar.gz";
    inherit (release) sha256;
  };
  nativeBuildInputs = [ pkgs.autoPatchelfHook ];
  buildInputs = runtimeDependencies ++ [
    pkgs.stdenv.cc.cc.lib
    pkgs.openssl
    pkgs.curl
    pkgs.sqlite
  ];
  # SDL's optional Steam Input loader and Android GLES1 fallback name.
  # Linux uses libGLESv1_CM from libglvnd; rendering itself requires Vulkan.
  autoPatchelfIgnoreMissingDeps = [
    "libsteam_api.so"
    "libGLES_CM.so.1"
  ];
  dontConfigure = true;
  dontBuild = true;
  dontStrip = true;
  installPhase = ''
    runHook preInstall
    mkdir -p "$out/libexec/melee-pc" "$out/bin" "$out/share/doc/melee-pc"
    install -m755 melee "$out/libexec/melee-pc/melee"
    cp -r resources "$out/libexec/melee-pc/"
    install -m644 initial_pipeline_cache.db "$out/libexec/melee-pc/"
    install -m644 ${./UPSTREAM-LICENSE.md} "$out/share/doc/melee-pc/LICENSE.md"
    install -m644 ${./UPSTREAM-COPYING} "$out/share/doc/melee-pc/COPYING"
    substitute ${./launcher.py} "$out/bin/melee-pc" \
      --subst-var-by python ${pkgs.python3} \
      --subst-var-by out "$out" \
      --subst-var-by runtimeLibraries ${lib.escapeShellArg runtimeLibraries}
    chmod +x "$out/bin/melee-pc"
    runHook postInstall
  '';
  meta = {
    description = "Native Melee PC beta with an owned-disc and account-state launcher";
    homepage = "https://github.com/999sian/melee-pc";
    # The GPL applies only to port code, not the recovered Nintendo/HAL code.
    license = lib.licenses.unfree;
    sourceProvenance = [ lib.sourceTypes.binaryNativeCode ];
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "melee-pc";
  };
})
