# mega-man-rock-n-roll-godot <data.pck>
#
# Run the game's data.pck with the native Godot 2.1.4 runtime, godot2-runtime,
# that plugin.nix bundles. plugin.ts passes the release's data.pck and HOME;
# Godot keeps settings and saves in ~/.godot/app_userdata/Megaman_RnR.
#
# The game is X11 only and uses the game unit's Xwayland DISPLAY. Do not set
# WAYLAND_DISPLAY.
#
# The game opens a 1024x896 window and then asks the window manager for
# fullscreen. On the RG353M that request sometimes loses a race with Xwayland:
# sway marked the window fullscreen at 640x480 while the game kept a 1024x896
# window, so it showed in a smaller box. Open the window at the screen's own
# size (-r, read from the X server) and fullscreen from the start (-f); the
# game's viewport stretch then fits the picture either way.
#
# Exit status: 2 if an input is missing or wrong; otherwise the engine's own.
set -Eeuo pipefail

fail() { printf 'mega-man-rock-n-roll-godot: %s\n' "$*" >&2; exit 2; }

(( $# == 1 )) || fail 'usage: mega-man-rock-n-roll-godot <data.pck>'
pack="$1"
[[ "$pack" == /* && -f "$pack" ]] || fail "pack is not an absolute file: $pack"
[[ "${HOME:-}" == /* ]] || fail 'HOME must be an absolute path'
[[ -d "$HOME" ]] || fail 'HOME is not a directory'

# Run from the game directory, the directory that holds the pack.
game="${pack%/*}"
cd "${game:-/}"
size=$(xdpyinfo 2>/dev/null | sed -n 's/^ *dimensions: *\([0-9][0-9]*x[0-9][0-9]*\) pixels.*/\1/p' | head -n 1 || true)
if [[ -n "$size" ]]; then
  exec godot2-runtime -r "$size" -f -main_pack "$pack"
fi
# No readable screen size: let the game request fullscreen itself.
exec godot2-runtime -main_pack "$pack"
