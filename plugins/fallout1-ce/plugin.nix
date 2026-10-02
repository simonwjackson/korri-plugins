{ pkgs }:
let
  engine = pkgs.fallout-ce.overrideAttrs (old: {
    # The nixpkgs build applies its upstream case-sensitive save/load fix.
    postInstall = (old.postInstall or "") + ''
      install -Dm644 ${old.src}/LICENSE.md "$out/share/doc/fallout-ce/LICENSE.md"
      install -Dm644 ${notice} "$out/share/doc/fallout-ce/NOTICE"
    '';
  });
  notice = pkgs.writeText "fallout-ce-NOTICE" ''
    Fallout Community Edition by alexbatalov and contributors.
    This build is modified by the pinned nixpkgs derivation. It applies
    upstream commit fbd25f00e9ccfb5391e394272d536206bb86678b to fix
    save/load on case-sensitive filesystems and uses packaged dependencies.
    Korri adds integration source and installs these license notices.
    The Sustainable Use License in LICENSE.md applies to the engine.
    Commercial game data is not included.
  '';
in
{
  packages.fallout-ce = engine;
  # bin/fallout-ce changes to XDG_DATA_HOME. The engine itself respects cwd.
  files.fallout-ce = "${engine}/libexec/fallout-ce";
}
