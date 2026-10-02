{ pkgs }:
let
  engine = import ./native-package.nix { inherit pkgs; };
  launcher = pkgs.runCommand "2ship-launcher" { } ''
    mkdir -p "$out/bin"
    substitute ${./launch.py} "$out/bin/2ship" \
      --replace-fail '@python@' '${pkgs.python3}/bin/python3' \
      --replace-fail '@engine@' '${engine}/bin/2s2h' \
      --replace-fail '@bundle@' '${engine}/2s2h' \
      --replace-fail '@version@' '${engine.version}'
    chmod +x "$out/bin/2ship"
  '';
in
{
  packages."2ship" = launcher;
  files."2ship" = "${launcher}/bin/2ship";
}
