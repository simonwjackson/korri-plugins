# Focused source checks for Mega Man Arena. They unpack small generated ZIPs
# and run the launcher with a recording python3 in place of Proton. Nothing
# here downloads the game or Proton, needs a Core, or runs on a device.
{ pkgs }:
pkgs.runCommand "korri-mega-man-arena-source-check"
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
    cp -r ${../plugins/mega-man-arena/game} plugin/game
    cp -r ${../plugins/mega-man-arena/runner} plugin/runner
    chmod -R u+w plugin
    (cd plugin && python3 -m unittest -v game/test_unpack.py runner/test_launch.py)
    bash -n plugin/runner/proton-launch.sh
    shellcheck -s bash plugin/runner/proton-launch.sh
    touch "$out"
  ''
