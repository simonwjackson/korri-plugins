# mega-man-rock-n-roll-godot <data.pck>
#
# Run the game's data.pck with the native Godot 2.1.4 runtime, godot2-runtime,
# that plugin.nix bundles. plugin.ts passes the release's data.pck and HOME;
# Godot keeps settings and saves in ~/.godot/app_userdata/Megaman_RnR.
#
# The game is X11 only and uses the game unit's Xwayland DISPLAY. Do not set
# WAYLAND_DISPLAY. There is no -f: the game requests fullscreen itself.
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
exec godot2-runtime -main_pack "$pack"
