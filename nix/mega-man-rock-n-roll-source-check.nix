# Focused source checks for Mega Man Rock N Roll. They unpack small generated
# ZIPs and run the launcher with a recording godot2-runtime. Nothing here
# builds the engine, downloads the game, needs a Core, or runs on a device.
{ pkgs }:
pkgs.runCommand "korri-mega-man-rock-n-roll-source-check"
  {
    nativeBuildInputs = with pkgs; [
      bash
      coreutils
      python3
      shellcheck
    ];
  }
  ''
    mkdir plugin
    cp -r ${../plugins/mega-man-rock-n-roll/game} plugin/game
    cp -r ${../plugins/mega-man-rock-n-roll/runner} plugin/runner
    chmod -R u+w plugin
    (cd plugin && python3 -m unittest -v game/test_unpack.py runner/test_launch.py)
    bash -n plugin/runner/godot-launch.sh
    shellcheck -s bash plugin/runner/godot-launch.sh
    touch "$out"
  ''
