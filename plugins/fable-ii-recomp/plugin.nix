{ pkgs, engine }:
let
  extractor = import ./extractor.nix { inherit pkgs; };
  # The runner declaration owns the accepted whole-disc identity, as in Simpsons.
  digest = builtins.head (builtins.match ".*sha256:([0-9a-f]{64}).*" (builtins.readFile ./plugin.ts));
  launcher = pkgs.runCommand "fable-ii-launcher" { allowSubstitutes = false; } ''
    mkdir -p "$out/bin"
    substitute ${./launch.py} "$out/bin/fable_ii" \
      --replace-fail '@python@' '${pkgs.python3}/bin/python3' \
      --replace-fail '@engine@' '${engine}/bin/fable_ii' \
      --replace-fail '@extractor@' '${extractor}/bin/extract-xiso' \
      --replace-fail '@discHash@' '${digest}' \
      --replace-fail '@xexHash@' '${engine.xexSha256}' \
      --replace-fail '@gameFiles@' '${./game-files.json}'
    chmod +x "$out/bin/fable_ii"
  '';
in
{
  packages.fable_ii = launcher;
  files.fable_ii = "${launcher}/bin/fable_ii";
}
