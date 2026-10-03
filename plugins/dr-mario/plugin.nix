{ pkgs, engine }:
let
  launcher = pkgs.runCommand "dr-mario-launcher" { } ''
    mkdir -p "$out/bin"
    substitute ${./launch.py} "$out/bin/dr-mario" \
      --replace-fail '@python@' '${pkgs.python3}/bin/python3' \
      --replace-fail '@engine@' '${engine}/bin/DrMarioRecomp'
    chmod +x "$out/bin/dr-mario"
  '';
in
{
  packages.dr-mario = launcher;
  files.dr-mario = "${launcher}/bin/dr-mario";
}
