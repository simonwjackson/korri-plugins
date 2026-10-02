{ pkgs }:
pkgs.stdenv.mkDerivation {
  pname = "snesrev-smw";
  version = "unstable-eae20c6";

  src = pkgs.fetchFromGitHub {
    owner = "snesrev";
    repo = "smw";
    rev = "eae20c65c58930c8b62c76188d259579ad4130f1";
    hash = "sha256:0kbydbh6nhbc7xw39l770rmbnqyk2qrg7b2ji54ac00d3k3s8ylz";
  };

  buildInputs = [ pkgs.SDL2 ];
  enableParallelBuilding = true;
  # The default target extracts a retail ROM. Build only the native engine.
  makeFlags = [ "smw" ];

  doCheck = true;
  checkPhase = ''
    runHook preCheck
    if ./smw --config /dev/null > missing-assets.log 2>&1; then
      echo "SMW unexpectedly started without game assets" >&2
      exit 1
    fi
    grep -F 'Failed to read smw_assets.dat' missing-assets.log
    runHook postCheck
  '';

  installPhase = ''
    runHook preInstall
    install -Dm755 smw "$out/bin/smw"
    install -Dm644 LICENSE.txt "$out/share/doc/snesrev-smw/LICENSE.txt"
    mkdir -p "$out/share/snesrev-smw/assets"
    install -m644 assets/*.py "$out/share/snesrev-smw/assets/"
    install -m644 smw.ini "$out/share/snesrev-smw/smw.ini"
    runHook postInstall
  '';

  meta = {
    description = "Super Mario World reimplementation without retail game assets";
    homepage = "https://github.com/snesrev/smw";
    license = pkgs.lib.licenses.mit;
    platforms = [
      "x86_64-linux"
      "aarch64-linux"
    ];
    mainProgram = "smw";
  };
}
