# Zelda3

`@simonwjackson:zelda3` adds a native runner for A Link to the Past on Linux
x86_64 and aarch64. The library entry remains the player's ROM. The package
contains no ROM, extracted game assets, reference saves, or MSU music.

## Source and accepted ROM

The native engine and extractor come from
[`snesrev/zelda3` at `fbbb3f967a51fafe642e6140d0753979e73b4090`](https://github.com/snesrev/zelda3/tree/fbbb3f967a51fafe642e6140d0753979e73b4090).
Upstream declares the MIT license and says the game is playable from start
to finish. This package does not independently verify that completion claim.

Upstream's README requires the unheadered US ROM with this whole-file SHA-256:

```text
66871d66be19ad2c34c927d6b14cd8eb6fc3181965b6e517cb361f7316009cfb
```

The runner uses Core's existing `releases` field to select that exact file.
It does not claim every SNES game. Discovery accepts `.sfc` and `.smc` files
under the existing `snes` system identity used by Snes9x. Headered dumps,
other revisions, translations, randomizers, and archives are not accepted.
The launcher checks the hash again on every launch, even when assets exist.

## Build and launch boundary

`package.nix` builds only upstream's `zelda3` Make target on a build machine.
It does not run the default target, which also extracts game data. Devices
receive the native executable, Python with Pillow/PyYAML, extraction scripts,
the extractor's annotation font and palette-usage table, and upstream's INI.
No compiler or game-data download runs at launch.

`plugin.ts` returns the approved executable and two literal arguments: the
ROM path and `${input.accountRoot}/zelda3`. It performs no effects. Core
runs the declared launcher as the game user under its existing policy.
The launcher performs extraction and starts the engine. It does not grant
filesystem access beyond that user's existing permissions.

The user chose automatic ROM extraction and account-owned storage on
2026-10-02. The storage root follows Korri's existing PPSSPP runner pattern.
The layout inside that root comes directly from upstream:

| Path beneath the account's `zelda3/` directory | Purpose |
|---|---|
| `zelda3_assets.dat` | Cached extraction from the validated ROM. |
| `zelda3.ini` | Upstream defaults, copied once and then left editable. |
| `saves/` | Upstream SRAM and snapshot files. |

The launcher locks that directory for the whole session. A second launch
for the same account fails rather than sharing writable saves. Different
accounts have separate state. Extraction uses a temporary writable copy of
the shipped tools and ROM, then renames only the completed asset file into
place. Failed extraction does not publish a partial asset file. It leaves
existing configuration and saves unchanged. No game data enters the Nix
store through this process.

The engine receives `--config` with the exact INI path. This disables its
parent-directory configuration search. It receives no ROM argument, which
would enable upstream's optional emulation comparison mode.

## Configuration and limits

Edit the native `zelda3.ini` while the game is stopped. Upstream defaults
remain unchanged, including windowed mode and 4:3 rendering. The file
documents fullscreen, widescreen, SDL/OpenGL output, audio, keyboard and
controller settings. Optional MSU music, shaders, and sprite replacements
must be supplied separately. Korri launch overrides are rejected rather
than silently ignored. No RetroArch session controls are declared.

The first launch has Python extraction overhead and needs writable space
for temporary files and cached assets. Later launches reuse the cache.
To recover a corrupt asset cache, stop the game and remove only
`zelda3_assets.dat`; the next valid launch extracts it again. Do not remove
`saves/` or `zelda3.ini` to repair the asset cache. There is no automatic
migration from another port's saves or configuration.

## Build and verify

Run on build machines, not target devices:

```sh
nix build --no-link .#packages.x86_64-linux.korri-plugin-zelda3
nix build --no-link .#packages.aarch64-linux.korri-plugin-zelda3
nix build --no-link .#checks.x86_64-linux.korri-zelda3-plugin
nix build --no-link .#checks.aarch64-linux.korri-zelda3-plugin
```

Both checks passed on native build machines on 2026-10-02. They verify the
actual ELF architecture, linked executable startup, packaged dependencies,
generated manifest, strict launch types, effect-free host admission, and
production sandboxed callback execution. They test literal paths containing
spaces and shell syntax, unsupported overrides, invalid ROM rejection,
cache revalidation, and preservation of existing configuration and saves
on rejection. They contain no retail ROM or game assets.

The ROM-free checks do not exercise successful extraction or gameplay.
The check-only GitHub workflow runs on both architectures. It neither
publishes binaries nor installs a plugin.

### Owned-ROM runtime check

The opt-in test uses an owned ROM at runtime, outside Nix build inputs:

```sh
nix run .#verify-zelda3 -- "$ROM"
```

It runs the real production `korrid plugin-launch` callback and launcher
with dummy video/audio drivers. It retains a private temporary directory
with test assets, snapshots, and logs for diagnosis. The original ROM and
existing account saves remain unchanged. No retail data goes to CI.

On 2026-10-02, the supported ROM from the owner's `myoko` Downloads archive
passed headless tests on x86_64 and aarch64 build machines. Both extracted
683888 bytes with SHA-256
`0fe2e4bd75d70f06fb9a74cd3a9cb336c838149b831b56e8792114a89292c793`.
The tests checked cold extraction, copied default configuration, refusal of
a concurrent session, cached launch without asset replacement, native
snapshot save/reload, preserved edited configuration, and an unchanged ROM.

Headless tests do not verify visible rendering, audible output, physical
controllers, in-game SRAM saves, full-game completion, or device installation.

For an interactive test on a build machine, build `.#zelda3`, then run its
`bin/zelda3` with the supported ROM and a separate writable test directory:

```sh
nix build .#zelda3 --out-link result-zelda3
./result-zelda3/bin/zelda3 -- "$ROM" "$TEST_DIRECTORY"
```

## Device installation

No live installation or signed publication has been performed for this
slice. A target device and an approved publisher/cache binding have not
been selected. Local package builds and `seed` checks do not establish
publisher trust or install approval.

After publishing the exact architecture-specific output through an approved
signed cache, use Core's existing raw-cache approval flow on the device:

```sh
sudo korri-plugin inspect "$CACHE_URL" "$PACKAGE"
# Review the report before setting APPROVAL to its exact digest.
sudo korri-plugin install "$CACHE_URL" "$PACKAGE" "$APPROVAL"
sudo korri-plugin enable @simonwjackson:zelda3
```

`CACHE_URL` must match the device's approved `@simonwjackson` binding.
`PACKAGE` must be the published plugin output, not the standalone engine,
flake URL, or derivation. A missing cache output or signature must fail
without building on the device or disabling signature checks.
