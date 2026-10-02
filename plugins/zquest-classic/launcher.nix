{ pkgs, engine }:
pkgs.runCommand "zquest-classic-launcher-${engine.version}" { meta = engine.meta; } ''
  mkdir -p "$out/bin"
  substitute ${./launcher.py} "$out/bin/zplayer" \
    --subst-var-by python ${pkgs.python3} \
    --subst-var-by engine ${engine}
  chmod +x "$out/bin/zplayer"
''
