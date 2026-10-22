# mega-man-arena-proton <data.win>
#
# Run Mega Man Arena's Windows x86_64 build with Proton-CachyOS arm64, inside
# the FHS environment that runner/fhs.nix builds. plugin.ts passes the
# release's data.win, HOME, and KORRI_PROTON_CACHYOS: the ready directory of
# the @korri:proton/cachyos artifact. That Proton build carries its own FEX
# (lib/wine/aarch64-windows/libarm64ecfex.dll), so no x86 Linux rootfs is
# needed.
#
# There is no Steam client. Proton still requires a compat data path and a
# client install path, so both live under HOME: compatdata holds the Wine
# prefix, where GameMaker keeps the game's settings and saves.
#
# The game directory is korrid's read-only artifact directory. Proton maps it
# as the install path and the game runs from it.
#
# Exit status: 2 if an input is missing or wrong; otherwise Proton's own.
set -Eeuo pipefail

fail() { printf 'mega-man-arena-proton: %s\n' "$*" >&2; exit 2; }

(( $# == 1 )) || fail 'usage: mega-man-arena-proton <data.win>'
data="$1"
[[ "$data" == /* && -f "$data" ]] || fail "data.win is not an absolute file: $data"
[[ "${HOME:-}" == /* && -d "$HOME" ]] || fail 'HOME must be an absolute directory'
proton="${KORRI_PROTON_CACHYOS:-}"
[[ "$proton" == /* && -f "$proton/proton" ]] || fail "KORRI_PROTON_CACHYOS is not a Proton directory: $proton"

game="${data%/*}"
game="${game:-/}"
exe="$game/MegaManArena.exe"
[[ -f "$exe" ]] || fail "MegaManArena.exe is missing beside data.win: $exe"

export STEAM_COMPAT_DATA_PATH="$HOME/compatdata"
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$HOME/steam"
export STEAM_COMPAT_INSTALL_PATH="$game"
# Proton's protonfixes needs a game ID and finds none without Steam. umu's
# generic ID selects its no-op default fix, as legacy Korri's launcher did.
export UMU_ID=umu-default
export STORE=none
mkdir -p "$STEAM_COMPAT_DATA_PATH" "$STEAM_COMPAT_CLIENT_INSTALL_PATH"

cd "$game"
exec python3 "$proton/proton" waitforexitandrun "$exe"
