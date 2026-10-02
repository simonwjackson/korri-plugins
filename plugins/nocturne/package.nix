{ pkgs }:
let
  inherit (pkgs) lib;
  release =
    {
      x86_64-linux = {
        arch = "x64";
        sha256 = "3ac18750a351efdbc1a49adb90dd1b2b69250bcd12b778d7e7f3ff3cd0c111f9";
      };
      aarch64-linux = {
        arch = "arm64";
        sha256 = "d3dc4fd05e011f253ebbb72d3a88c2481c909933fdf50f260e01231dbed0d07e";
      };
    }
    .${pkgs.stdenv.hostPlatform.system};
  runtimeDependencies = [
    pkgs.vulkan-loader
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
    pkgs.libxtst
    pkgs.fribidi
    pkgs.libthai
    pkgs.openxr-loader
  ];
  runtimeLibraries = lib.makeLibraryPath runtimeDependencies;
in
pkgs.stdenv.mkDerivation (finalAttrs: {
  pname = "nocturnerecomp";
  version = "1.4.5";
  src = pkgs.fetchurl {
    url = "https://github.com/birabittoh/NocturneRecomp/releases/download/v${finalAttrs.version}/nocturnerecomp-v${finalAttrs.version}-linux-${release.arch}.tar.gz";
    inherit (release) sha256;
  };
  sourceRoot = ".";
  nativeBuildInputs = [ pkgs.autoPatchelfHook ];
  buildInputs = runtimeDependencies ++ [
    pkgs.stdenv.cc.cc.lib
    pkgs.curl
  ];
  # Optional Steam Input library, loaded at runtime only when present.
  autoPatchelfIgnoreMissingDeps = [ "libsteam_api.so" ];
  dontConfigure = true;
  dontBuild = true;
  # Retain the released code. Only ELF interpreter/library paths are changed.
  dontStrip = true;
  installPhase = ''
    runHook preInstall
    mkdir -p "$out/libexec/nocturnerecomp" "$out/bin" "$out/share/doc/nocturnerecomp"
    install -m755 nocturnerecomp "$out/libexec/nocturnerecomp/nocturnerecomp"
    install -m644 *.so "$out/libexec/nocturnerecomp/"
    cp -r shaders "$out/libexec/nocturnerecomp/"
    install -m644 README.md "$out/share/doc/nocturnerecomp/UPSTREAM-README.md"
    install -m644 ${./UPSTREAM-LICENSE} "$out/share/doc/nocturnerecomp/HOST-SOURCE-LICENSE"
    substitute ${./launcher.py} "$out/bin/nocturne" \
      --subst-var-by python ${pkgs.python3} \
      --subst-var-by out "$out" \
      --subst-var-by runtimeLibraries ${lib.escapeShellArg runtimeLibraries}
    chmod +x "$out/bin/nocturne"
    runHook postInstall
  '';
  meta = {
    description = "NocturneRecomp native XBLA Symphony of the Night launcher";
    homepage = "https://github.com/birabittoh/NocturneRecomp";
    # The MIT grant covers host sources, not the translated retail code in
    # release executables. Do not publish this binary closure without review.
    license = lib.licenses.unfree;
    sourceProvenance = [ lib.sourceTypes.binaryNativeCode ];
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "nocturne";
  };
})
