{ pkgs }:
let
  fixes = pkgs.writeTextDir "deadcells.json" (builtins.readFile ./fixes/deadcells.json);
  patcher = pkgs.rustPlatform.buildRustPackage {
    pname = "hl-fill";
    version = "0.1.0";
    src = pkgs.lib.fileset.toSource {
      root = ./.;
      fileset = pkgs.lib.fileset.unions [
        ./patcher/Cargo.toml
        ./patcher/Cargo.lock
        ./patcher/src
        ./patcher/tests
        ./fixes
        ./LICENSE
      ];
    };
    cargoRoot = "patcher";
    buildAndTestSubdir = "patcher";
    cargoLock.lockFile = ./patcher/Cargo.lock;
    postPatch = ''
      substituteInPlace patcher/tests/exec.rs \
        --replace-fail '"/bin/sh"' '"${pkgs.runtimeShell}"'
    '';
    postInstall = ''
      install -Dm644 LICENSE "$out/share/licenses/hl-fill/LICENSE"
      for crate in "$cargoDeps"/*; do
        test -d "$crate" || continue
        for notice in "$crate"/LICENSE* "$crate"/COPYING* "$crate"/COPYRIGHT*; do
          test -f "$notice" || continue
          install -Dm644 "$notice" \
            "$out/share/licenses/hl-fill/dependencies/$(basename "$crate")/$(basename "$notice")"
        done
      done
    '';
    meta = {
      description = "Fail-open, byte-exact HashLink stage fill patcher";
      license = pkgs.lib.licenses.mit;
      platforms = pkgs.lib.platforms.linux;
      mainProgram = "hl-fill";
    };
  };
in
{
  packages.patcher = patcher;
  files.patcher = "${patcher}/bin/hl-fill";
  files."deadcells.json" = "${fixes}/deadcells.json";
}
