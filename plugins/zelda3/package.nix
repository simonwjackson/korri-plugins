{ pkgs }:
let
  python = pkgs.python3.withPackages (packages: [
    packages.pillow
    packages.pyyaml
  ]);
in
pkgs.stdenv.mkDerivation {
  pname = "zelda3";
  version = "unstable-2023-08-17";
  src = pkgs.fetchFromGitHub {
    owner = "snesrev";
    repo = "zelda3";
    rev = "fbbb3f967a51fafe642e6140d0753979e73b4090";
    hash = "sha256-oMSjTLPOWacOyQg5kZUPMZm3ciJGfteqbhNxFJD+2Xg=";
  };
  buildInputs = [ pkgs.SDL2 ];
  enableParallelBuilding = true;
  # Upstream's default target also extracts copyrighted assets. Build only C.
  buildFlags = [ "zelda3" ];
  installPhase = ''
    runHook preInstall
    install -Dm755 zelda3 "$out/libexec/zelda3"
    install -Dm644 zelda3.ini "$out/share/zelda3/zelda3.ini"
    install -Dm644 LICENSE.txt "$out/share/licenses/zelda3/LICENSE.txt"
    install -m644 third_party/opus-1.3.1-stripped/COPYING "$out/share/licenses/zelda3/OPUS-COPYING"
    mkdir -p "$out/share/zelda3/assets/sprites" "$out/share/zelda3/other" "$out/bin"
    cp assets/*.py assets/palette_usage.bin "$out/share/zelda3/assets/"
    # The extractor's annotation font, not an extracted game font.
    install -m644 other/3x5_font.png "$out/share/zelda3/other/3x5_font.png"
    substitute ${./launcher.py} "$out/bin/zelda3" \
      --subst-var-by python ${python} \
      --subst-var-by out "$out"
    chmod +x "$out/bin/zelda3"
    runHook postInstall
  '';
  meta = {
    description = "Zelda3 native engine with local extraction of player-owned ROM assets";
    homepage = "https://github.com/snesrev/zelda3";
    license = with pkgs.lib.licenses; [
      mit
      bsd3
    ];
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "zelda3";
  };
}
