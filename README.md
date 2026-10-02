# Personal Korri plugins

This is `simonwjackson/korri-plugins`, built separately from Korri OS.
The publisher namespace is `@simonwjackson`, following the existing personal
PICO-8 producer. A namespace declaration does not grant device trust.

## Packages

| Output | Plugin or contents | Platforms |
|---|---|---|
| `korri-plugin-skate-3` | `@simonwjackson:skate-3` | x86_64 Linux only |
| `korri-plugin-super-mario-world` | `@simonwjackson:super-mario-world` | x86_64 and aarch64 Linux |
| `korri-plugin-zelda3` | `@simonwjackson:zelda3` | x86_64 and aarch64 Linux |
| `zelda3` | Standalone native engine and owned-ROM launcher | x86_64 and aarch64 Linux |
| `korri-plugin-pico8-starter-pack` | `@simonwjackson:pico8-starter-pack` | x86_64 and aarch64 Linux |
| `pico8-starter-pack-cartridges` | Standalone cartridge pack without the plugin manifest | x86_64 and aarch64 Linux |

## Skate 3

[Skate 3](plugins/skate-3/README.md) adds a launcher to an existing library
game when its recorded whole-file hash matches an accepted disc. It reuses
the pinned prebuilt native launcher. The repository contains integration
source, tests, documentation and hashes, not an ISO, XEX, title update,
compiled recompilation or NAR archive.

The native release is unfree. Do not publish its binary closure without a
separate rights review and approval. This repository has no binary-cache
publication workflow. Device installation and gameplay remain outside the
package-only scope. Signature and permission checks must stay enabled.

Run on an x86_64 build machine, not a target device:

```sh
nix run .#help
nix build --no-link .#korri-plugin-skate-3
nix build --no-link .#checks.x86_64-linux.korri-skate3-plugin
```

The gate checks the actual packaged source, generated manifest, personal
publisher identity, strict launch-contract types, host admission, and
production sandboxed launch preparation with literal file paths.

## Super Mario World

[Super Mario World](plugins/super-mario-world/README.md) adds a native runner for
the measured USA ROM, with or without its copier header. It ships the pinned
`snesrev/smw` engine without retail data. Launch extracts owned assets into
separate Korri account storage and preserves the original ROM and existing saves.

```sh
nix build --no-link .#korri-plugin-super-mario-world
nix build --no-link .#checks.x86_64-linux.korri-super-mario-world-plugin
nix build --no-link .#checks.aarch64-linux.korri-super-mario-world-plugin
nix run .#verify-smw -- '/path/to/Super Mario World (U) [!].smc'
```

Run these on a build machine. The opt-in `verify-smw` test uses an owned ROM in
temporary storage. Builds and CI checks need no retail data. Package checks do not
establish physical-device gameplay, signed publication, or installation approval.

## Zelda3

[Zelda3](plugins/zelda3/README.md) launches the supported US A Link to the Past
ROM through a native engine on both Linux architectures. First launch extracts
assets locally. Configuration and saves remain in account-owned storage.
The package contains no ROM or extracted game data. Build machines compile the
engine; devices receive it prebuilt. Python asset extraction is not compilation.

```sh
nix build --no-link .#korri-plugin-zelda3
nix build --no-link .#checks.x86_64-linux.korri-zelda3-plugin
nix build --no-link .#checks.aarch64-linux.korri-zelda3-plugin
```

The checks cover packaging, native startup, host admission, launch arguments,
and invalid-ROM rejection. They do not establish gameplay or physical-device
acceptance. Its separate check-only workflow does not publish or install it.

## PICO-8 starter pack

`@simonwjackson:pico8-starter-pack` contains the 24 selected noncommercial games.
There are 25 original cartridge files because Into Ruins uses its author's two-file offline release.
[Credits and exact releases](plugins/pico8-starter-pack/CREDITS.md) identify every game and creator.
[Pack instructions](plugins/pico8-starter-pack/README.md) explain the FAKE-08 dependency and known limits.

The plugin requires the separate `@korri:fake08` plugin from `korri-os/plugins`.
Its exact native `requires` entry lets Core install and activate that dependency after normal approval.
FAKE-08 owns its runner, RetroArch and core; this pack does not copy those contributions.
The standalone cartridge output remains player-free.
There is no automatic library registration.
The games retain their CC BY-NC-SA 4.0 licenses.
No repository-wide license replaces those licenses.
The PICO-8 pack does not include the separate Skate 3 package.

### Build and verify the cartridge pack

Run these commands from this checkout on a Linux build machine, not a target device.
Both `x86_64-linux` and `aarch64-linux` cartridge-pack outputs are available.

```sh
nix run .#help
nix build --no-link .#checks.x86_64-linux.pico8-starter-pack
nix build --no-link .#checks.aarch64-linux.pico8-starter-pack
nix build .#pico8-starter-pack-cartridges --out-link result-cartridges
nix build .#korri-plugin-pico8-starter-pack --out-link result-plugin
```

The standalone pack is under `result-cartridges/share/pico8-starter-pack/`.
Copy that complete directory to your device and add its `cartridges/` folder manually to your player.
Keep the credits, license and notices with it when sharing it.
The plugin output contains `plugin.ts` and the manifest generated by Core's supported builder.
Its manifest references the same cartridge pack using existing packages/files fields.
Its native `requires` entry names the exact FAKE-08 plugin output, not a raw emulator binary.
The device must already trust both publisher namespaces through their separately bound full keys and cache URLs.
Building these packages does not configure that trust or approve installation.

The check builds the real pack and verifies original hashes and encoded cartridge structure.
It checks credit entries and the presence of license text and source notices.
It checks the generated manifest, exact FAKE-08 plugin dependency and native artifacts.
It typechecks the plugin source.
These checks do not verify device trust or all-game compatibility.
Into Ruins reached its second cartridge but failed a real FAKE-08 runtime test; see the pack instructions.
Creator names and license declarations were reviewed against the original developer pages, not proved by these checks.
It also proves rejection of changed cartridge bytes, a missing Into Ruins companion, a wrong license and missing credits.
It does not run the games or claim compatibility with a player or device.

Builds fetch original developer downloads pinned by SHA-256 in `cartridges.nix`.
Missing upstream files can stop a cold build.
Builds refuse changed bytes rather than silently replacing a selected release.
A completed pack needs no download to obtain its cartridge files.

## Publication boundary

The check-only GitHub workflow checks the PICO-8 pack and SMW plugin on both Linux architectures.
It does not build the unrelated Skate 3 closure or upload release assets.
It does not sign packages, configure cache keys or install anything on a device.
Source commits and package construction are separate from signed-cache publication and device approval.
Do not bypass Korri's signature, publisher binding or exact-package approval checks to install this pack.
Signed publication and physical-device acceptance still need separate approval.
