# Mega Man Arena

`@simonwjackson:mega-man-arena` declares KishSquared's Mega Man Arena, the
public Windows x86_64 GameMaker build, and plays it with Proton-CachyOS arm64
from `@korri:proton`. That Proton build runs x86 Windows code with its own FEX
(`files/lib/wine/aarch64-windows/libarm64ecfex.dll` and `libwow64fex.dll`), so
the runner needs no x86 Linux rootfs. The ZIP's extension DLLs (`gme.dll`,
`libxprocess_x64.dll`, `rousrDissonance.dll`) are Windows code, so a native
engine cannot replace Proton the way Godot replaced FEX for Mega Man Rock N
Roll.

korrid downloads the game (Korri ADR 0012 and ADR 0013,
`docs/adr/0013-declared-games-can-come-from-artifacts.md` in `korri-os/korri`).
The plugin ships only the URL and the SHA-256 values. The ZIP is not in the
plugin closure, and no build or check downloads it.

It replaces legacy Korri's `product/plugins/mega-man-arena`, which shipped the
4.20 ZIP inside a Nix package and launched it through Bandai's FEX and Proton
10 runtime plugins. This plugin takes the current release, and korrid's
artifacts replace those runtime plugins.

## Core and system requirements

The release's `artifacts` and object `file`, the runner's `artifacts`, and the
`artifacts` launch input need a Core with ADR 0012 and ADR 0013. The flake pins
a Korri commit that has both.

The package and its plugin check exist for aarch64-linux only, because
`@korri:proton` carries only an arm64 Proton. The source check runs on both
systems. The first launch downloads the game's ZIP (61.5 MB) and, unless
another runner already did, Proton-CachyOS (335.8 MB).

## Declaration

| Export | Key | What it declares |
|---|---|---|
| `artifacts` | `game` | `@simonwjackson:mega-man-arena/game`, version `4.2.3`: `https://bit.ly/mmav423a`, `sha256:ea88237b…245e` and 61477538 bytes; unpack program `game-unpack` |
| `games` | `mega-man-arena` | One release, `4.2.3`: `hashes` is the SHA-256 of `data.win`; `artifacts` and `file` name `data.win` in the `game` artifact |
| `runners` | `proton` | `@simonwjackson:mega-man-arena/proton`: program `proton-launch`, `releases` holds the `data.win` hash (`sha256:1c9b5c77…a4f`), `artifacts` is `@korri:proton/cachyos` |
| `handlers` | `launch.prepare` | The launch plan below |

There are no `systems`: the runner accepts the release by its hash
(SCRIPTING.md, "Native runners for specific content").

The URL is the download page's own link (`megamanarena.com/download-page`,
read on 2026-10-21). It redirects three times, all HTTPS, to Dropbox's
`MegaManArena_v4.2.3.zip`. A new upstream release changes that link; the
pinned SHA-256 makes a changed file fail verification instead of installing.

The plugin requires no other publisher's package. Its runner names
`@korri:proton`'s artifact, which korrid resolves when `@korri:proton` is
enabled.

## Files

| Key | File |
|---|---|
| `game-unpack` | `mega-man-arena-unpack`: unpacks the verified ZIP; korrid runs it, the runner does not |
| `proton-launch` | `mega-man-arena-proton`: the runner program, an FHS environment that runs `runner/proton-launch.sh` |

`runner/fhs.nix` builds the FHS environment. Proton's binaries are built for a
glibc distribution layout and cannot run from the Nix store directly. The
library list is legacy Korri's aarch64 FHS environment for this game, less
FEX.

## `game-unpack <work-dir> <zip>`

The same program as Mega Man Rock N Roll's. It refuses unsafe entries before it
writes anything, extracts every file and directory into `<work-dir>`, and
requires the files that `game/contents` lists: `MegaManArena.exe` and
`data.win`, both 0644. Proton loads the `.exe`; nothing needs the executable
bit. It checks no hashes: korrid verified the whole ZIP first. Exit status: 0
ready, 1 failed.

## Launch

`launch.prepare` refuses a core, a raw config override and typed settings,
requires an absolute `contentPath`, and requires the ready
`@korri:proton/cachyos` directory in `input.artifacts`. It returns:

| Field | Value |
|---|---|
| `command`, `args` | `proton-launch <contentPath>` |
| `cwd` | the directory of `data.win` |
| `env.HOME`, `directories` | `<accountRoot>/mega-man-arena` |
| `env.KORRI_PROTON_CACHYOS` | the ready Proton directory |

`proton-launch.sh` refuses with status 2 unless it gets one absolute
`data.win`, an absolute `HOME` directory, a Proton directory, and
`MegaManArena.exe` beside `data.win`. It then runs
`python3 <proton>/proton waitforexitandrun <game>/MegaManArena.exe` from the
game directory with:

| Variable | Value | Why |
|---|---|---|
| `STEAM_COMPAT_DATA_PATH` | `$HOME/compatdata` | Proton's Wine prefix |
| `STEAM_COMPAT_CLIENT_INSTALL_PATH` | `$HOME/steam` | Proton requires it; there is no Steam client |
| `STEAM_COMPAT_INSTALL_PATH` | the game directory | |
| `UMU_ID`, `STORE` | `umu-default`, `none` | protonfixes needs a game ID and finds none without Steam; this selects umu's no-op default fix, as legacy did |

GameMaker writes the game's settings and saves to
`compatdata/pfx/drive_c/users/steamuser/AppData/Local/MegaManArena/` (for
example `mmasavefile42.sav`). The game directory is korrid's read-only
artifact directory, and the game runs from it without writing there.

## Checks

Build these on a build machine, never on a device.

```sh
nix build --no-link .#packages.aarch64-linux.korri-plugin-mega-man-arena
nix build --no-link .#checks.x86_64-linux.korri-mega-man-arena-source
nix build --no-link .#checks.aarch64-linux.korri-mega-man-arena-plugin
```

- `korri-mega-man-arena-source` runs `game/test_unpack.py` against small
  generated ZIPs and `runner/test_launch.py` with a recording `python3` in
  place of Proton (arguments, working directory, compat paths, umu variables,
  exit status, refusals), then `bash -n` and shellcheck.
- `korri-mega-man-arena-plugin` checks the built package: the manifest (files,
  packages, no `requires`), strict TypeScript against the Core contract,
  `plugin.test.ts`, and the unpack program's usage errors.

## Device run, 2026-10-21

On the AYN Odin 2 Portal (SM8550, Adreno 740, NixOS, korrid running):

- `game-unpack` unpacked the real 4.2.3 ZIP; `data.win` matched the pinned
  hash.
- Korri's `korrid plugin-run` (branch `fix/plugin-launch-fixture-entry`, built
  for aarch64 on a build machine) evaluated this `plugin.ts`'s
  `launch.prepare` with an `artifacts` input and executed the plan in a
  transient unit with the game unit's sandbox properties
  (`services/korrid/src/host/systemd_unit.rs`): runtime user, no new
  privileges, private /tmp and PIDs, X0 and Pulse binds only, `/run/user`
  hidden. The FHS environment's bubblewrap started inside it.
- DXVK created a D3D11 device on Turnip (feature level 11_1) and presented
  1280x896. The game showed its disclaimer, intro, title (`V4.2.3`) and main
  menu; X keyboard input moved through them. It wrote its save under the
  account storage above. Wine loaded `winepulse` and opened the `Korri Seat
  P1`–`P4` pads.

Not verified: korrid's own catalog, download and Confirm flow (the device's
installed korrid predates ADR 0012 and refused the `artifacts` field), the
plugin host's install and approval, a launch through the Gamescope modifier,
the bubblewrap wrapper of Korri ADR 0015, gameplay past the main menu,
controller buttons, audible sound, and frame rate.
