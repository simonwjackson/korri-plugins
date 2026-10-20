# Mega Man Rock N Roll

`@simonwjackson:mega-man-rock-n-roll` declares Dennis Engelhard's Mega Man Rock N
Roll, public Linux 1.3 build, and plays it under FEX. The build is Godot
2.1.4 with an x86_64 executable. It is the first game whose files korrid
downloads (Korri ADR 0013, `docs/adr/0013-declared-games-can-come-from-artifacts.md`
in `korri-os/korri`). The plugin ships only the URL and the SHA-256 values.
The ZIP is not in the plugin closure, and no build or check downloads it.

It was written in `korri-os/korri` (`plugins/mega-man-rock-n-roll`) and moved
here on 2026-10-20 under the `@simonwjackson` namespace.

## Core requirement

The release's `artifacts` and its object `file`, the runner's `artifacts`, and
the `artifacts` launch input need a Core with ADR 0012 and ADR 0013. The flake
pins a Korri commit that has both.

The package and its plugin check are aarch64-linux only, because the bundled
`pkgs.fex` builds for ARM hosts only. The source check runs on both systems.

On a device, the runner also needs `@korri:fex` enabled at a build that
declares the `rootfs` artifact (ADR 0012). korrid downloads that rootfs
(about 1.19 GB) together with this game's ZIP (97.5 MB) before the first
launch.

## Declaration

| Export | Key | What it declares |
|---|---|---|
| `artifacts` | `game` | `@simonwjackson:mega-man-rock-n-roll/game`, version `1.3`: the ZIP's URL, `sha256:af916d57…abd9` and 97511960 bytes; unpack program `game-unpack` |
| `games` | `mega-man-rock-n-roll` | One release, `1.3`: `hashes` is the SHA-256 of `data.pck`; `artifacts` and `file` name `data.pck` in the `game` artifact |
| `runners` | `fex` | `@simonwjackson:mega-man-rock-n-roll/fex`: program `fex-launch`, `releases` holds the `data.pck` hash, `artifacts` is `@korri:fex/rootfs` |
| `handlers` | `launch.prepare` | The launch plan below |

There are no `systems`: the runner accepts the release by its hash
(SCRIPTING.md, "Native runners for specific content").

The plugin requires no other publisher's package. It uses `@korri:fex` only
through the `rootfs` artifact, which any enabled plugin may name. Its FEX
configuration is its own native file, `fex/Config.json`. It started as a copy
of `@korri:fex`'s `Config.json` on 2026-10-20 and is not kept aligned with it.

## Files

| Key | File |
|---|---|
| `game-unpack` | `mega-man-rock-n-roll-unpack`: unpacks the verified ZIP; korrid runs it, the runner does not |
| `fex-launch` | `mega-man-rock-n-roll-fex`: the runner program |
| `fex-config` | The FEX configuration directory holding `Config.json` |

## `game-unpack <work-dir> <zip>`

korrid invokes it with the verified ZIP (ADR 0012).

1. It refuses the whole ZIP before it writes anything if an entry is a
   symlink or another special file, is absolute, contains `..`, `.`, an empty
   segment or a backslash, or appears twice.
2. It extracts every file and directory into `<work-dir>`.
3. It requires each file that `game/contents` lists and gives it the listed
   mode: `data.pck` 0644, `MegaMan_RocknRoll` 0755. The ZIP has MS-DOS
   attributes and no Unix modes, so the executable bit comes from that list.
   Other files, such as `readme.txt`, get 0644.

It checks no hashes. korrid verified the whole ZIP against the SHA-256 that
`plugin.ts` pins before it runs the program, and that one hash fixes every
file in the ZIP. `plugin.ts` is the only source of the `data.pck` hash.

It writes only under `<work-dir>`. Exit status: 0 ready, 1 failed (including
usage). Diagnostics go to stderr; stdout carries nothing korrid reads.
Python comes from Nix. Nothing is compiled on the device.

## Launch

`launch.prepare` refuses a core, a raw config override and typed settings.
It takes the game directory from the directory of `contentPath`, so a copy
that discovery finds in a source plays the same way as the download. It
returns:

| Field | Value |
|---|---|
| `command`, `args` | `fex-launch <game directory>` |
| `cwd` | the game directory |
| `env.HOME`, `directories` | `<accountRoot>/mega-man-rock-n-roll`; Godot keeps settings and saves in `~/.godot/app_userdata/Megaman_RnR` |
| `env.KORRI_FEX_CONFIG` | `files["fex-config"]` |
| `env.KORRI_FEX_ROOTFS` | `artifacts["@korri:fex/rootfs"]` |

`mega-man-rock-n-roll-fex` refuses with status 2 if an input is missing or
is not a directory, or if the game directory lacks `data.pck` or
`MegaMan_RocknRoll`. It sets `FEX_ROOTFS` and `FEX_APP_CONFIG_LOCATION` as the
Steam session does, sets `FEX_APP_DATA_LOCATION` to `$HOME/.fex-emu/`, changes
to the game directory (Godot loads `res://data.pck`, and `res://` is the
working directory) and runs `FEX MegaMan_RocknRoll` with the `pkgs.fex` it
bundles. FEX 2608 names its interpreter `FEX`; there is no `FEXInterpreter`.
The game is X11 only. It uses the game unit's Xwayland `DISPLAY`; nothing
sets `WAYLAND_DISPLAY`.

## Checks

Build these on a build machine, never on a device.

```sh
nix build --no-link .#packages.aarch64-linux.korri-plugin-mega-man-rock-n-roll
nix build --no-link .#checks.x86_64-linux.korri-mega-man-rock-n-roll-source
nix build --no-link .#checks.aarch64-linux.korri-mega-man-rock-n-roll-plugin
```

- `korri-mega-man-rock-n-roll-source` runs `game/test_unpack.py` against small
  generated ZIPs (success, modes, missing files, traversal, symlinks,
  duplicates, usage) and `runner/test_launch.py` with a recording `FEX`
  program, then `bash -n` and shellcheck. It needs no Core.
- `korri-mega-man-rock-n-roll-plugin` checks the built package: the manifest,
  strict TypeScript against the Core contract, `plugin.test.ts`, the unpack
  program's usage errors and the launcher's refusals, then runs the launcher
  with the bundled FEX and this plugin's config on a hand-assembled static
  x86_64 ELF.

## Not verified

Nothing has unpacked the real ZIP inside korrid or run the game. The FEX
rootfs may lack libraries the game needs (`libGL`, `libX11`, `libXcursor`,
`libXinerama`, `libXrandr`, `libasound`, `libpulse`, `libpulse-simple`). GL
under FEX on Freedreno, controller input and audio are untested.
