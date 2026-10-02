# Personal Korri plugins

This is `simonwjackson/korri-plugins`, built separately from Korri OS.
The publisher namespace is `@simonwjackson`, following the existing personal
PICO-8 producer. A namespace declaration does not grant device trust.

## Packages

| Output | Plugin or contents | Platforms |
|---|---|---|
| `korri-plugin-skate-3` | `@simonwjackson:skate-3` | x86_64 and aarch64 Linux |
| `korri-plugin-nocturne` | `@simonwjackson:nocturne` | x86_64 and aarch64 Linux |
| `nocturne` | NocturneRecomp native launcher for owned XBLA assets | x86_64 and aarch64 Linux |
| `korri-plugin-opengoal` | `@simonwjackson:opengoal`, Jak trilogy including Renegade | x86_64 Linux only |
| `opengoal` | Native runtime without game assets or compiler | x86_64 Linux only |
| `opengoal-tools` | Off-device disc preparation and GOAL compiler | x86_64 Linux build machine only |
| `korri-plugin-actraiser` | `@simonwjackson:actraiser`, private owned-ROM build | x86_64 and aarch64 Linux |
| `actraiser` | Private native executable and owned-ROM launcher | x86_64 and aarch64 Linux |
| `korri-plugin-super-mario-world` | `@simonwjackson:super-mario-world` | x86_64 and aarch64 Linux |
| `korri-plugin-solarus` | `@simonwjackson:solarus` | x86_64 and aarch64 Linux |
| `solarus` | Standalone Solarus 2.1.4 runtime | x86_64 and aarch64 Linux |
| `korri-plugin-zelda3` | `@simonwjackson:zelda3` | x86_64 and aarch64 Linux |
| `zelda3` | Standalone native engine and owned-ROM launcher | x86_64 and aarch64 Linux |
| `korri-plugin-fallout1-ce` | `@simonwjackson:fallout1-ce` | x86_64 and aarch64 Linux |
| `korri-plugin-fallout2-ce` | `@simonwjackson:fallout2-ce` | x86_64 and aarch64 Linux |
| `korri-plugin-pico8-starter-pack` | `@simonwjackson:pico8-starter-pack` | x86_64 and aarch64 Linux |
| `pico8-starter-pack-cartridges` | Standalone cartridge pack without the plugin manifest | x86_64 and aarch64 Linux |

## Skate 3

[Skate 3](plugins/skate-3/README.md) adds a launcher to an existing library
game when its recorded whole-file hash matches an accepted disc. It uses
the pinned prebuilt launcher on x86_64 and a native source build on aarch64.
The ARM64 build needs two owned XEX files in the builder's Nix store; see
the [build instructions](plugins/skate-3/README.md#build-and-verify).
The repository contains integration source, tests, documentation and hashes,
not an ISO, XEX, title update, compiled recompilation or NAR archive.

The native release is unfree. Do not publish its binary closure without a
separate rights review and approval. This repository has no binary-cache
publication workflow. Device installation and gameplay remain outside the
package-only scope. Signature and permission checks must stay enabled.

Run on a build machine of the matching architecture, not a target device:

```sh
nix run .#help
nix build --no-link .#korri-plugin-skate-3
nix build --no-link .#checks.x86_64-linux.korri-skate3-plugin
nix build --no-link .#checks.aarch64-linux.korri-skate3-plugin
```

The gate checks the actual packaged source, generated manifest, personal
publisher identity, strict launch-contract types, host admission, and
production sandboxed launch preparation with literal file paths.
ARM64 package support does not fix the observed Mini V2 intro-movie freeze
or establish gameplay acceptance.

## NocturneRecomp

[NocturneRecomp](plugins/nocturne/README.md) launches the XBLA version of
Castlevania: Symphony of the Night from its supported `default.xex` and complete
extracted assets. Both Linux architectures use pinned upstream v1.4.5 binaries.
The launcher keeps a private asset copy and native state per Korri account.
Builds contain no separate retail asset files and perform no game extraction.

```sh
nix build --no-link .#korri-plugin-nocturne
nix build --no-link .#checks.x86_64-linux.korri-nocturne-plugin
nix build --no-link .#checks.aarch64-linux.korri-nocturne-plugin
nix run .#verify-nocturne -- /path/to/extracted/default.xex
```

Run these on build machines. The opt-in test uses owned assets and private
software video/audio services. Startup checks do not establish full gameplay,
save/load, or clean shutdown. The native binary contains translated retail code;
public binary-cache publication needs separate rights review and approval.

## Jak and Daxter trilogy

[OpenGOAL](plugins/opengoal/README.md) runs prepared Jak 1, Jak II, Jak II: Renegade,
and Jak 3 data. The x86_64 plugin includes the prebuilt runtime, not game assets
or a compiler. Disc validation and GOAL compilation run explicitly on a build
machine. Transfer the complete upstream data tree to the target afterwards.
The runner matches measured `out/<game>/iso/GAME.CGO` files in registered library
releases. It does not claim ISO files or create library entries. Linux ARM is
deferred. Signed publication and live installation remain separate steps.

```sh
nix build --no-link .#korri-plugin-opengoal
nix build --no-link .#checks.x86_64-linux.korri-opengoal-plugin
nix run .#prepare-opengoal -- --game jak2 --iso /path/to/owned.iso --output /path/to/new-data
```

## ActRaiser

[ActRaiser Recomp](plugins/actraiser/README.md) builds native code from the
supported owned USA cartridge on a private build machine. Devices receive
prebuilt packages. The Arcade/Nintendo Super System dump is not supported.

Unlike SMW and Zelda3, this build needs the ROM and produces copyrighted
ROM-derived code. Keep its inputs, helper, and output closures out of public
caches and release assets. Read the plugin instructions before building.
No publication or installation workflow is added.

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

## Solarus

[Solarus](plugins/solarus/README.md) runs `.solarus` quests with native saves
under the account root supplied by Korri. It packages Solarus 2.1.4 without quests, an editor,
or game assets. Devices receive the engine prebuilt. Discovery does not claim
general ZIP files, and no library folder is registered automatically.

```sh
nix build --no-link .#korri-plugin-solarus
nix build --no-link .#checks.x86_64-linux.korri-solarus-plugin
nix build --no-link .#checks.aarch64-linux.korri-solarus-plugin
```

The checks exercise host seed/declaration validation, the production launch
callback, the native engine, archive loading, and save/reload in two supplied
account roots. Core currently always supplies `users/default`; this plugin does
not add account selection. The checks use a headless fixture, not a complete
game. Physical display, audio and controller acceptance remain separate. The check-only workflow does not sign, publish, or
install packages.

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
nix run .#verify-zelda3 -- '/path/to/owned/USA-ROM.sfc'
```

The ROM-free checks cover packaging, native startup, host admission, launch
arguments, and invalid-ROM rejection. The opt-in `verify-zelda3` test uses an
owned ROM to test extraction, cached launch, and snapshot save/reload through
Core's launch executor. It does not establish physical-device gameplay.
Its separate check-only workflow does not publish or install it.

## Fallout 1 and 2 Community Edition

[Fallout 1 CE](plugins/fallout1-ce/README.md) and
[Fallout 2 CE](plugins/fallout2-ce/README.md) provide separate native runners.
They match the measured `MASTER.DAT` hashes from the owner's installations.
They launch from the writable installation folder and preserve native config and
save behavior. There is no archive extraction, automatic library registration,
per-account save isolation, or `.dat` extension claim.

Both architectures have package checks for native ELF, license notices, manifest,
strict launch types, real host admission and the production callback executor.
The owned-data test reached gameplay, wrote saves and reloaded them on x86_64.
Both ARM64 engines also loaded and rewrote native saves on the ARM build machine.
These were headless tests, not physical-device, audio or controller verification.
CI requires no retail data. The engines use the Sustainable Use License, not an
unrestricted open-source license. Signed publication and device approval remain
separate from building these packages.

```sh
nix build --no-link .#korri-plugin-fallout1-ce .#korri-plugin-fallout2-ce
nix build --no-link .#checks.x86_64-linux.korri-fallout1-ce-plugin .#checks.x86_64-linux.korri-fallout2-ce-plugin
nix build --no-link .#checks.aarch64-linux.korri-fallout1-ce-plugin .#checks.aarch64-linux.korri-fallout2-ce-plugin
```

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
