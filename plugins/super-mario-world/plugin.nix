{ pkgs }:
let
  engine = import ./engine.nix { inherit pkgs; };
  launcher = pkgs.runCommand "smw-launcher" { } ''
    mkdir -p "$out/bin"
    substitute ${./launch.py} "$out/bin/smw" \
      --replace-fail '@python@' '${pkgs.python3}/bin/python3' \
      --replace-fail '@engine@' '${engine}/bin/smw' \
      --replace-fail '@resources@' '${engine}/share/snesrev-smw'
    chmod +x "$out/bin/smw"
  '';
in
{
  packages.smw = launcher;
  files.smw = "${launcher}/bin/smw";
}
