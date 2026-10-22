# Focused source checks for Mega Man Maker. They unpack small generated ZIPs
# and run the launcher script with a recording Proton. Nothing here builds
# the FHS environment, downloads the game or Proton, needs a Core, or runs on
# a device.
{ pkgs }:
pkgs.runCommand "korri-mega-man-maker-source-check"
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
    cp -r ${../plugins/mega-man-maker/game} plugin/game
    cp -r ${../plugins/mega-man-maker/runner} plugin/runner
    chmod -R u+w plugin
    (cd plugin && python3 -m unittest -v game/test_unpack.py runner/test_launch.py)
    bash -n plugin/runner/proton-launch.sh
    shellcheck -s bash plugin/runner/proton-launch.sh
    touch "$out"
  ''
