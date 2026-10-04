{ pkgs }:
let
  # Reuse nixpkgs' dependency packaging, but match 5.0.1's source and changed
  # FetchContent dependencies. No game data is used to construct this output.
  version = "5.0.1";
  revision = "8a24047fbce8915993804e7819f4df4fa591551f";
  prism = pkgs.fetchFromGitHub {
    owner = "KiritoDv";
    repo = "prism-processor";
    rev = "1de054450e7b3c5f777d2e3dfcb228ad120c329d";
    hash = "sha256-5MlscqbKlUm4nYW+Obf5KlnUdtHK/xlDUc4wxr52ySM=";
  };
  monocypher = pkgs.fetchFromGitHub {
    owner = "LoupVaillant";
    repo = "Monocypher";
    rev = "0d85f98c9d9b0227e42cf795cb527dff372b40a4";
    hash = "sha256-RrM8Ep/CM7U5Q4+4FAHfBknb6b0upohoiqy4f7eMye0=";
  };
  native = (pkgs._2ship2harkinian.override { _2ship2harkinian = native; }).overrideAttrs (old: {
    inherit version;
    src = pkgs.fetchFromGitHub {
      owner = "2ship2harkinian";
      repo = "2ship2harkinian";
      rev = revision;
      hash = "sha256-6ekHPC12xcz0emn4wLTXQ/lCRn+WIMRG9CZKiPifKiM=";
      fetchSubmodules = true;
      postFetch = ''
        printf '%s\n' "" > "$out/GIT_BRANCH"
        printf '%s\n' '${builtins.substring 0 7 revision}' > "$out/GIT_COMMIT_HASH"
        printf '%s\n' '${version}' > "$out/GIT_COMMIT_TAG"
      '';
    };
    patches = old.patches ++ [ ./linux-shutdown.patch ];
    cmakeFlags =
      builtins.filter (flag: !(pkgs.lib.hasPrefix "-DFETCHCONTENT_SOURCE_DIR_PRISM:" flag)) old.cmakeFlags
      ++ [
        (pkgs.lib.cmakeFeature "FETCHCONTENT_SOURCE_DIR_PRISM" "${prism}")
        (pkgs.lib.cmakeFeature "FETCHCONTENT_SOURCE_DIR_MONOCYPHER" "${monocypher}")
        # Keep upstream's default: do not add a runtime C compiler or script loader.
        (pkgs.lib.cmakeBool "ENABLE_SCRIPTING" false)
      ];
    postInstall = old.postInstall + ''
      install -Dm644 -t $out/share/licenses/2ship2harkinian/prism ${prism}/LICENSE
      install -Dm644 -t $out/share/licenses/2ship2harkinian/monocypher ${monocypher}/LICENCE.md
    '';
    # CMake applies SSE flags only on x86_64. Both architectures still need
    # real build and runtime checks; this metadata is not that evidence.
    meta = old.meta // {
      homepage = "https://github.com/2ship2harkinian/2ship2harkinian";
      platforms = [
        "x86_64-linux"
        "aarch64-linux"
      ];
    };
  });
in
native
