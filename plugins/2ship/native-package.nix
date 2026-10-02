{ pkgs }:
let
  # Reuse nixpkgs' dependency packaging. Pin the tag's exact commit without
  # deepClone: the existing fetch fails its fixed-output hash check.
  revision = "f45acdd794712fefa0fae0bca86dcac22e040f09";
  native = (pkgs._2ship2harkinian.override { _2ship2harkinian = native; }).overrideAttrs (old: {
    src = pkgs.fetchFromGitHub {
      owner = "HarbourMasters";
      repo = "2ship2harkinian";
      rev = revision;
      hash = "sha256-4AKZfqAVOMZmapK6nTBLebU+uItUtwe/wAvmjzuSAWs=";
      fetchSubmodules = true;
      postFetch = ''
        printf '%s\n' "" > "$out/GIT_BRANCH"
        printf '%s\n' '${builtins.substring 0 7 revision}' > "$out/GIT_COMMIT_HASH"
        printf '%s\n' '3.0.1' > "$out/GIT_COMMIT_TAG"
      '';
    };
    patches = old.patches ++ [ ./linux-shutdown.patch ];
    # CMake applies SSE flags only on x86_64. Both architectures still need
    # real build and runtime checks; this metadata is not that evidence.
    meta = old.meta // {
      platforms = [
        "x86_64-linux"
        "aarch64-linux"
      ];
    };
  });
in
native
