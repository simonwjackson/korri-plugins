{ pkgs, engine }:
let
  # The Git LFS pointers at the engine's exact revision supply these hashes.
  base = "https://media.githubusercontent.com/media/ZQuestClassic/ZQuestClassic/${engine.src.rev}/tests/replays/playground";
  quest = pkgs.fetchurl {
    url = "${base}/playground.qst";
    sha256 = "ceef9045491b14f207dff578562886ec7aeb010c474094064f308fe8c97d001c";
  };
  replay = pkgs.fetchurl {
    url = "${base}/auto_scopes.zplay";
    sha256 = "f6adf427d207d4e9c545fd1ea3e53ac84dc1ebe45553438ef36a77bfef717e11";
  };
in
pkgs.runCommand "zquest-script-replay-fixture" { } ''
  mkdir -p "$out"
  cp ${quest} "$out/playground.qst"
  cp ${replay} "$out/auto_scopes.zplay"
''
