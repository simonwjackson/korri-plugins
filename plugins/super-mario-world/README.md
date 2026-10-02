# Super Mario World

`@simonwjackson:super-mario-world` adds a native runner to the existing library game
on x86_64 and aarch64 Linux. It does not add a separate game tile or claim to run
all SNES content. The output is `korri-plugin-super-mario-world`.

## Native engine and game data

The engine is [snesrev/smw](https://github.com/snesrev/smw), pinned at
`eae20c65c58930c8b62c76188d259579ad4130f1`. `engine.nix` builds only the executable,
asset tools, native configuration, and upstream license. Neither ROMs nor extracted
retail assets enter the build, Nix output, or binary cache. The upstream license
covers its source, not Nintendo game data.

The plugin accepts these measured whole-file identities:

| USA ROM representation | Bytes | SHA-256 |
|---|---:|---|
| `Super Mario World (U) [!].smc`, with copier header | 524800 | `d70c9c7716ad12c674fc7dd744736aa48d4d7b4237f58066be620fda26024872` |
| Same ROM without its copier header | 524288 | `0838e531fe22c077528febe14cb3ff7c492f1f5fa8de354192bdff7137c27f5b` |

The measurements came from the owner's library file and its normalized copy.
The normalized SHA-1 matches upstream's required
`6B47BB75D16514B6A476AA0C73A683A2A4C18765`. No other editions or ROM hacks are
advertised. Discovery claims `.smc` and `.sfc` under the existing `snes` system.
Core's exact `RunnerRecord.releases` match determines whether this runner is offered.
A compatible Core is required, as with this repository's Skate 3 plugin.

## Launch and storage

`plugin.ts` returns the existing `PluginLaunchOutput` declaration. Core creates
`<accountRoot>/smw`, selects it as the working directory, and starts the packaged
launcher with the selected ROM path as one literal argument. It adds no shell
command, service, settings schema, or custom permission path.

The user chose separate account storage. The `accountRoot` comes from Core's launch
treaty. `smw` is the upstream executable name. The native files inside the directory
come directly from upstream:

| Native data | Behavior |
|---|---|
| `smw_assets.dat` | Regenerated atomically from the supplied ROM on each launch. |
| `smw.ini` | Copied from the pinned upstream default only when absent. Existing edits stay unchanged. |
| `saves/` | Owned by the native game. Contains SRAM, snapshots and any enabled replay recording. |

The launcher reads at most 524801 bytes, normalizes the measured copier-header
representation in a temporary copy, and runs the pinned Python asset extractor.
Upstream's original header test misses this 512 KiB ROM size. Its USA hash check
stays enabled. Extraction uses `--no-include-rom`, so the game runs reconstructed
native logic rather than the background ROM-comparison mode. The engine still uses
upstream's PPU and DSP implementations.

After successful extraction, the launcher removes the temporary ROM and replaces
itself with the engine. The original library file stays untouched. A directory lock
stays held until the game exits, preventing simultaneous instances from writing the
same saves. Invalid ROMs leave existing configuration, assets and saves unchanged.
No network request or software compilation occurs during launch.

Regeneration adds extraction work to each launch but avoids persistent cache-version
metadata and stale assets after updates. Native configuration defaults remain
upstream's defaults, including windowed output and Autosave disabled. Edit `smw.ini`
for fullscreen, renderer, controller bindings, or automatic snapshots. Back up
`saves/` and any configuration edits separately from your ROM library.
There is no emulator-save migration, device-to-device sync, or Korri in-game menu.
Raw config overrides and unsupported typed settings are refused rather than ignored.

## Build and verify

Run these commands on a build machine, never a target device:

```sh
nix build --no-link .#korri-plugin-super-mario-world
nix build --no-link .#checks.x86_64-linux.korri-super-mario-world-plugin
nix build --no-link .#checks.aarch64-linux.korri-super-mario-world-plugin
```

The checks build and execute the native engine's missing-assets failure path.
They typecheck the packaged plugin against Core's exported contract, admit its
manifest, and run its callback through Core's production sandbox and launch executor.
They verify literal paths, unsupported-setting refusal, and invalid-ROM rejection
without changing existing native data. They use no retail assets.

For an opt-in test with an owned ROM on the build machine:

```sh
nix run .#verify-smw -- '/path/to/Super Mario World (U) [!].smc'
```

This uses temporary account storage and the actual packaged callback and launcher.
It checks startup with dummy SDL video/audio, snapshot writing and reload, config
preservation, both supplied and normalized ROM forms, and concurrent-launch refusal.
Temporary retail data is deleted. It does not prove physical graphics, audio,
controller input, SRAM compatibility with other engines, or complete gameplay.
See `RESEARCH.md` for evidence and current verification results.

## Installation boundary

This repository's workflow checks both architectures. It does not publish signed
binaries, establish publisher trust, or install the plugin on a device. Targets must
download prebuilt outputs through an approved, signed delivery route. Do not build
on a target or bypass signature, publisher-binding, or exact-package approval checks.
The [Mini V2 acceptance record](MINIV2.md) documents a signed installation through
its existing private cache, native fullscreen rendering, snapshot save/reload, and
owner-confirmed controls and speaker audio. The device uses `Fullscreen = 1` in
its native configuration; package defaults remain unchanged. Sunshine was disabled
with owner approval to clear a pre-existing activation blocker.
