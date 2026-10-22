# mega-man-maker-proton <data.win>
#
# Start the game's MegaMaker.exe, which sits beside data.win, with the
# Proton-CachyOS arm64 build that korrid passes in KORRI_PROTON. plugin.nix
# runs this script inside an FHS environment, because Proton's prebuilt
# binaries expect /lib/ld-linux-aarch64.so.1 and Python 3.
#
# No Steam client starts Proton here, so this script sets the variables
# Steam would set. The Wine prefix (compatdata) and an empty stand-in for the
# Steam client directory live under HOME, which plugin.ts sets to the
# account's Mega Man Maker directory. The game keeps its levels, settings and
# GIFs in %LOCALAPPDATA%\Megamaker inside that prefix.
#
# Proton's arm64 Wine runs the x86_64 game with its own FEX DLLs
# (libarm64ecfex.dll); no FEX rootfs is used. The game uses the game unit's
# Xwayland DISPLAY. Do not set WAYLAND_DISPLAY.
#
# Exit status: 2 if an input is missing or wrong; otherwise Proton's own.
set -Eeuo pipefail

fail() { printf 'mega-man-maker-proton: %s\n' "$*" >&2; exit 2; }

(( $# == 1 )) || fail 'usage: mega-man-maker-proton <data.win>'
data="$1"
[[ "$data" == /* && -f "$data" ]] || fail "data.win is not an absolute file: $data"
game="${data%/*}"
game="${game:-/}"
exe="$game/MegaMaker.exe"
[[ -f "$exe" ]] || fail "MegaMaker.exe is missing beside data.win: $exe"
[[ "${HOME:-}" == /* ]] || fail 'HOME must be an absolute path'
[[ -d "$HOME" ]] || fail 'HOME is not a directory'
[[ "${KORRI_PROTON:-}" == /* && -f "${KORRI_PROTON}/proton" ]] \
  || fail "KORRI_PROTON is not a Proton directory: ${KORRI_PROTON:-}"

export STEAM_COMPAT_DATA_PATH="$HOME/compatdata"
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/steam-client"
export STEAM_COMPAT_INSTALL_PATH="$game"
export STEAM_COMPAT_LIBRARY_PATHS="$game"
export STEAM_COMPAT_APP_ID=0
export SteamAppId=0
export SteamGameId=0
# Proton treats a set UMU_ID as "not a Steam game": it starts the program
# through its umu.exe instead of steam.exe, which would need Steam's native
# steamclient library. The values follow legacy's mega-man-maker-fex wrapper
# and umu-launcher.
export UMU_ID=umu-default
export STORE=none
mkdir -p "$STEAM_COMPAT_DATA_PATH" "$STEAM_COMPAT_CLIENT_INSTALL_PATH"

cd "$game"
exec python3 "$KORRI_PROTON/proton" waitforexitandrun "$exe"
