# ActRaiser Recomp: private Linux builds

This plugin runs `DerrickGold/ar-recomp` on x86_64 and aarch64 Linux. It adds a
native route for the supported SNES ROM, not an emulator or a bundled game.
The source pin is in `source.nix`. Runtime verification results belong below;
package availability alone does not establish playability.

## Private inputs and outputs

The user chose private builds from an owned ROM. Upstream generates native C
from the game's 65816 code at build time. Its MIT license explicitly excludes
that generated code and the original game data. The Builder helper also embeds
retail media outside MIT coverage. Keep the helper, generated code, completed
packages, and their closures out of public caches and GitHub release assets.
This repository contains integration source and hashes only.

The accepted input is the **standard USA cartridge**, not the Arcade/Nintendo
Super System version:

| Property | Required value |
|---|---|
| Internal title | `ACTRAISER-USA` |
| Size | 1,048,576 bytes, without a copier header |
| SHA-256 | `b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0` |

The hash is specified by upstream and was verified against the user's supplied
ROM. Other regions, Arcade dumps, and headered dumps are not advertised.
The launcher checks the size and hash before creating player state.

`requireFile` follows the existing private `skate-3-flake/package-source.nix`
pattern. Copy your supported ROM to a private working directory as `ar.sfc`,
then import it on the **build machine**:

```sh
nix-store --add-fixed sha256 /absolute/private/path/ar.sfc
```

The local Nix store is readable by other local accounts. "Private" here means
no public distribution, not encrypted storage or isolation from local users.
Use only build machines and private delivery destinations you trust.

## Build and test

Run these commands on a build machine of the matching architecture. Never run
compilation or dispatch builds from a target device. For ARM64, use an ARM64
build machine such as `fuji`; no compiler is included in the runtime package.

```sh
NIXPKGS_ALLOW_UNFREE=1 nix build --impure --no-link \
  --option builders '' --option post-build-hook '' \
  .#korri-plugin-actraiser

NIXPKGS_ALLOW_UNFREE=1 nix build --impure --no-link \
  --option builders '' --option post-build-hook '' \
  .#checks.x86_64-linux.korri-actraiser-plugin

NIXPKGS_ALLOW_UNFREE=1 nix run --impure \
  --option builders '' --option post-build-hook '' \
  .#verify-actraiser -- /absolute/private/path/ar.sfc
```

Use `checks.aarch64-linux.korri-actraiser-plugin` on the ARM64 build machine.
Disabling remote builders prevents an implicit transfer of the owned ROM.
Disabling post-build hooks prevents a configured hook from publishing outputs.
Neither setting stops a separate manual `nix copy`; inspect its destination.
Private derivations also refuse substitution. This is not a rights-management
system and does not prevent an administrator from copying the files.

The package check typechecks the actual packaged plugin and tests host
admission and production sandboxed launch arguments. It does not start the
game. `verify-actraiser` uses the owned ROM and temporary account storage to
check native startup, PPU frames, audio-setting reload, invalid-input refusal,
resource-link updates, concurrent native-launch refusal, and preservation of the
source ROM. It also checks refusal to overwrite corrupt or uninitialized saves.
It does not establish campaign save/reload.

Add `--video` to `verify-actraiser` only when a working X11/Wayland display and
SDL GPU driver are available. That test requires a final-composite capture;
it does not silently accept a CPU framebuffer instead.

## Runtime data

The raw game's native `AR_USER_DATA_DIR` selects its writable root. The plugin
passes `<accountRoot>/ActRaiserRecomp/game`, using Core's account-root contract
and upstream's existing `ActRaiserRecomp/game` namespace. The standalone
`actraiser` launcher uses upstream's Linux XDG location unless that environment
variable is set. The supplied ROM remains separate and unchanged.

The native game owns `config.ini`, `settings.ini`, `diorama-layers.ini`,
`game-assets/manifest.ini`, language packs, and `saves/`. No Korri configuration
format or save migration is added. Back up the complete writable root.

The launcher links only packaged defaults, fonts, and the ROM-derived Native
US language resource. It preserves live settings and save files. Unrelated
resource directories or symlinks cause an explicit refusal rather than an
overwrite. Launchers using the same root hold an exclusive Linux directory
lock. Different account roots remain independent.

The runtime includes the upstream helper for language/archive operations, but
not its compiler or the recompilation tool. Optional manuals and imported
regional media are not installed. The plugin supports no emulator core or
Korri configuration override and rejects either instead of ignoring it.

## Source and integration grounding

- [Upstream at the pinned commit](https://github.com/DerrickGold/ar-recomp/tree/cdd76085a00e8beb090a7f0a07fcbc09a0e20670) defines ROM validation, regeneration, runtime files, and licensing.
- `CMakeLists.txt` and `snesbuild.ini` remain the build/source lists. Korri does not copy their source enumeration.
- `installer/packaging/CMakeLists.txt` defines stock defaults and fonts. `installer/internal/appdata/path.go` defines the Linux data namespace. `src/app/application.c` implements `AR_USER_DATA_DIR`.
- `snesrecomp-go/internal/toolchain/sdl_pins.go` pins SDL 3.4.12. `sdl.nix` applies that version only here because the repository lock has SDL 3.2.26. Its updated Zenity source path and XTest dependency account for SDL's packaging changes. ARM tests retain their workload with a larger timeout after `testrwlock` exceeded its 20-second limit on the shared builder.
- The launcher supplies SDL's Vulkan loader path. SDL opens it dynamically, so ordinary ELF library resolution did not provide it. The video gate caught this startup failure; it passed after the launcher supplied the pinned loader.
- Existing SMW/Zelda3 plugins ground the SNES identity, hash-specific runner, discovery, and launch treaty. No identification or plugin schema is added.

Upstream reports completed USA action routes, but Northwall town events still
need validation. A native build, startup test, or screenshot does not prove a
complete campaign.

Signed private delivery and installation must preserve publisher binding,
package signatures, and exact-package approval. These builds do not publish,
configure device trust, or bypass installation checks.
