{ pkgs, engine }:
let
  extractor = import ./extractor.nix {
    inherit pkgs;
    inherit (engine) src;
  };
  # The existing runner release declaration owns the accepted disc identity.
  digest = builtins.head (builtins.match ".*sha256:([0-9a-f]{64}).*" (builtins.readFile ./plugin.ts));
  launcher = pkgs.runCommand "simpsons-launcher" { } ''
    mkdir -p "$out/bin"
    substitute ${./launch.py} "$out/bin/simpsons" \
      --replace-fail '@python@' '${pkgs.python3}/bin/python3' \
      --replace-fail '@engine@' '${engine}/bin/simpsons' \
      --replace-fail '@extractor@' '${extractor}/bin/extract-xiso' \
      --replace-fail '@config@' '${./simpsons.toml}' \
      --replace-fail '@discHash@' '${digest}'
    chmod +x "$out/bin/simpsons"
  '';
in
{
  packages.simpsons = launcher;
  files.simpsons = "${launcher}/bin/simpsons";
}
