# Mega Man Maker

`@simonwjackson:mega-man-maker` declares Mega Man Maker, the public Windows
1.10.4.2 release from `megamanmaker.com`, and plays it with Proton-CachyOS for
arm64. The game is a 64-bit GameMaker program: `MegaMaker.exe` is the
GameMaker runner and `data.win` is the game.

korrid downloads two things before the first launch (Korri ADR 0012 and
ADR 0013): the game's ZIP (83 MB), which this plugin pins, and the
`@korri:proton/cachyos` artifact (336 MB), which the `@korri:proton` plugin
pins. Neither is in this plugin's closure, and no build or check downloads
them. Proton's arm64 Wine runs the x86_64 game with its own FEX DLLs
(`libarm64ecfex.dll`, `libwow64fex.dll`), so the FEX rootfs that Steam uses
is not needed.

Legacy Korri had `product/plugins/mega-man-maker`. That plugin also searched
and downloaded online levels for Korri's library. This one does not: the
game has its own online level browser (Play, Online, Find Levels), and Korri
ADR 0016 excludes Mega Man Maker as a search provider.

## Core requirement

The release's `artifacts` and object `file`, a runner's foreign `artifacts`,
and the `artifacts` launch input need a Core with ADR 0012 and ADR 0013. The
flake pins a Korri commit that has them. The `@korri:proton` plugin must be
installed and enabled on the device: the runner names its artifact, and
korrid requires every artifact a runner names to resolve (SCRIPTING.md,
"Declared artifacts").

## Declaration

| Export | Key | What it declares |
|---|---|---|
| `artifacts` | `game` | `@simonwjackson:mega-man-maker/game`, version `1.10.4.2`: the ZIP's URL, `sha256:3d214513…f6af` and 83060701 bytes; unpack program `game-unpack` |
| `games` | `mega-man-maker` | One release, `1.10.4.2`: `hashes` is the SHA-256 of `data.win`; `artifacts` and `file` name `data.win` in the `game` artifact |
| `runners` | `proton` | `@simonwjackson:mega-man-maker/proton`: program `proton-launch`, `releases` holds the `data.win` hash (`sha256:888d7eee…dca4`), `artifacts` is `@korri:proton/cachyos` |
| `handlers` | `launch.prepare` | The launch plan below |

There are no `systems`: the runner accepts the release by its hash. The
release identity is `data.win`, the game's content, not the ZIP or the
GameMaker runner. A copy of the game that discovery finds in a source joins
the same game by that hash.

The URL and ZIP hash are those of legacy
`product/plugins/mega-man-maker/packages/mega-man-maker/default.nix`. The URL
still served the same bytes on 2026-10-21.

The plugin requires no other package (no `plugin.nix` `requires`): it uses
only Proton's artifact, not `@korri:proton`'s files.

## Files

| Key | File |
|---|---|
| `game-unpack` | `mega-man-maker-unpack`: unpacks the verified ZIP; korrid runs it, the runner does not |
| `proton-launch` | `mega-man-maker-proton`: the runner program, `runner/proton-launch.sh` inside an FHS environment |

## `game-unpack <work-dir> <zip>`

The same program as Mega Man Rock N Roll's, with this plugin's `game/contents`.
It refuses the whole ZIP before it writes anything if an entry is a symlink or
another special file, is absolute, contains `..`, `.`, an empty segment or a
backslash, or appears twice. It extracts every file and directory into
`<work-dir>` and requires `data.win` (0644) and `MegaMaker.exe` (0755). Other
files get 0644. It checks no hashes: korrid verified the whole ZIP first.
Exit status: 0 ready, 1 failed. Nothing is compiled on the device.

## Launch

`launch.prepare` refuses a core, a raw config override, typed settings, a
relative `contentPath`, and a launch without the ready `@korri:proton/cachyos`
artifact. It returns:

| Field | Value |
|---|---|
| `command`, `args` | `proton-launch <contentPath>`, where `contentPath` is `data.win` |
| `cwd` | the game directory, the directory of `data.win` |
| `env.HOME`, `directories` | `<accountRoot>/mega-man-maker` |
| `env.KORRI_PROTON` | the ready Proton directory from `artifacts["@korri:proton/cachyos"]` |

`mega-man-maker-proton` is an FHS environment (`runner/package.nix`) because
Proton's prebuilt arm64 Wine expects `/lib/ld-linux-aarch64.so.1`, Python 3
and common desktop libraries at FHS paths. Its library list follows the Steam
plugin's FHS in `korri-os/plugins`, without Steam-client-only packages.
`/tmp` is private inside it.

`runner/proton-launch.sh` refuses with status 2 unless it gets exactly one
absolute `data.win` with `MegaMaker.exe` beside it, an absolute existing
`HOME`, and a `KORRI_PROTON` directory that holds `proton`. It then sets the
variables a Steam client would set, and runs
`python3 $KORRI_PROTON/proton waitforexitandrun <game>/MegaMaker.exe` from the
game directory:

| Variable | Value | Why |
|---|---|---|
| `STEAM_COMPAT_DATA_PATH` | `$HOME/compatdata` | The Wine prefix |
| `STEAM_COMPAT_CLIENT_INSTALL_PATH` | `$HOME/steam-client`, empty | Proton requires the variable |
| `STEAM_COMPAT_INSTALL_PATH`, `STEAM_COMPAT_LIBRARY_PATHS` | the game directory | The game's install |
| `STEAM_COMPAT_APP_ID`, `SteamAppId`, `SteamGameId` | `0` | No Steam app |
| `UMU_ID`, `STORE` | `umu-default`, `none` | Proton starts a non-Steam game through its `umu.exe`. Without it, Proton's `steam.exe` stops on a missing native `steamclient` library. Legacy's wrapper used the same values. |

The game keeps its profile, settings, levels and GIFs in
`%LOCALAPPDATA%\Megamaker`, which is
`$HOME/compatdata/pfx/drive_c/users/steamuser/AppData/Local/MegaMaker`. The
game directory stays read-only. The game uses the game unit's Xwayland
`DISPLAY`; nothing sets `WAYLAND_DISPLAY`.

## Checks

Build these on a build machine, never on a device.

```sh
nix build --no-link .#packages.aarch64-linux.korri-plugin-mega-man-maker
nix build --no-link .#checks.x86_64-linux.korri-mega-man-maker-source
nix build --no-link .#checks.aarch64-linux.korri-mega-man-maker-plugin
nix build --no-link .#checks.x86_64-linux.korri-mega-man-maker-plugin
```

- `korri-mega-man-maker-source` runs `game/test_unpack.py` against small
  generated ZIPs and `runner/test_launch.py` with a recording `proton`
  (arguments, working directory, the variables above, refusals, exit status),
  then `bash -n` and shellcheck.
- `korri-mega-man-maker-plugin` checks the built package: the manifest (files,
  packages, no `requires`, no `hosts`), strict TypeScript against the Core
  contract, `plugin.test.ts`, the unpack program's usage errors, Core's
  `korri-plugin seed` admission, and the packaged `launch.prepare` through
  Core's `korrid plugin-launch` sandbox and executor with a recording program.

## Verified on a build machine

On 2026-10-21, on the aarch64 build machine fuji, the built package ran the
real game without Steam: `game-unpack` unpacked the real ZIP (`data.win`
matched the pinned hash), the tree was made read-only, and the FHS launcher
started `MegaMaker.exe` with the pinned Proton-CachyOS arm64 build under Xvfb
1240x1080 with Mesa lavapipe (DXVK). Proton launched it through `umu.exe`. The
game showed its flashing-images warning, then its first-run profile screen,
and wrote `Settings/Settings.ini` in the prefix. Nothing tested input,
audio, a real GPU, korrid's download and unpack of the artifacts, or the
Korri game unit.

## Verified on the Mini V2

On 2026-10-22 the Retroid Pocket Mini V2 ran a Core from before ADR 0012
(no `artifacts` exports, no `app.acquisition.*`), so this plugin could not be
admitted there. A device-test variant with the same native packages ran
instead. It declared the release as an ADR 0003 prepared file under the
account root and took the Proton directory that the Steam plugin had already
prepared in korrid's cache. The game files were unpacked by `game-unpack`
under the account root, and the library entry, device location and
discovery record were written in the shapes the device holds for Fallout 2.

korrid then routed the game to `@simonwjackson:mega-man-maker/proton` and
started it in its normal game unit, nested in the device's Gamescope
modifier. Proton launched `MegaMaker.exe` through `umu.exe` on the device
GPU. Sway reported the Gamescope window `Mega Man Maker` focused and
fullscreen at 1240x1080, and a Gamescope screenshot showed the game's
first-run profile screen scaled to the whole display.

## Not verified

- This plugin itself on a device: korrid's download and unpack of the game
  ZIP and Proton, the library entry before download, and the release `file`
  in the artifact. These need a device Core with ADR 0012 and ADR 0013.
- Controller input, audio and frame rate. The first run asks for a typed
  username to create an online profile, or to log in; that step was not
  taken, because it creates an account on megamanmaker.com.
- Saves are not declared as `saveLocations` (ADR 0014); the pinned Core
  predates that field.
