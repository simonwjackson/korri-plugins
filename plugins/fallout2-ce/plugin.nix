{ pkgs }:
let
  engine = pkgs.fallout2-ce.overrideAttrs (old: {
    postInstall = (old.postInstall or "") + ''
      install -Dm644 ${old.src}/LICENSE.md "$out/share/doc/fallout2-ce/LICENSE.md"
      install -Dm644 ${notice} "$out/share/doc/fallout2-ce/NOTICE"
    '';
  });
  notice = pkgs.writeText "fallout2-ce-NOTICE" ''
    Fallout 2 Community Edition by alexbatalov and contributors.
    This build is modified by the pinned nixpkgs derivation. It applies
    upstream commit e770e64a48cd4d0a58a07f8db72839e4747e4c1e to fix
    save/load on case-sensitive filesystems and uses packaged dependencies.
    Korri adds integration source and installs these license notices.
    The Sustainable Use License in LICENSE.md applies to the engine.
    Commercial game data is not included.
  '';
in
{
  packages.fallout2-ce = engine;
  files.fallout2-ce = "${engine}/libexec/fallout2-ce";
}
