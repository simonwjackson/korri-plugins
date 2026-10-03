# Personal Korri plugins

This is `simonwjackson/korri-plugins`, built separately from Korri OS.
The publisher namespace is `@simonwjackson`, following the existing personal
PICO-8 producer. A namespace declaration does not grant device trust.

## Packages

| Output | Plugin or contents | Platforms |
|---|---|---|
| `korri-plugin-dr-mario` | `@simonwjackson:dr-mario`, owned Europe NES ROM | x86_64 and aarch64 Linux |
| `dr-mario-engine` | DrMarioNesRecomp Europe native executable without a ROM | x86_64 and aarch64 Linux targets |
| `korri-plugin-skate-3` | `@simonwjackson:skate-3` | x86_64 and aarch64 Linux |
| `korri-plugin-nocturne` | `@simonwjackson:nocturne` | x86_64 and aarch64 Linux |
| `korri-plugin-melee-pc` | `@simonwjackson:melee-pc`, beta | x86_64 and aarch64 Linux |
| `melee-pc` | Native Melee PC runtime and owned-disc launcher | x86_64 and aarch64 Linux |
| `nocturne` | NocturneRecomp native launcher for owned XBLA assets | x86_64 and aarch64 Linux |
| `korri-plugin-opengoal` | `@simonwjackson:opengoal`, Jak trilogy including Renegade | x86_64 and aarch64 Linux |
| `opengoal` | Native runtime without game assets or compiler | x86_64 and aarch64 Linux |
| `opengoal-tools` | Off-device disc preparation and GOAL compiler | x86_64 Linux build machine only |
| `korri-plugin-actraiser` | `@simonwjackson:actraiser`, private owned-ROM build | x86_64 and aarch64 Linux |
| `actraiser` | Private native executable and owned-ROM launcher | x86_64 and aarch64 Linux |
| `korri-plugin-the-simpsons-game` | `@simonwjackson:the-simpsons-game` | x86_64 with AVX2 and aarch64 Linux build targets |
| `korri-plugin-2ship` | `@simonwjackson:2ship` | x86_64 and aarch64 Linux |
| `korri-plugin-fable-ii-recomp` | `@simonwjackson:fable-ii-recomp`, private owned-XEX build | x86_64 and aarch64 Linux build targets |
| `korri-plugin-drmario64` | `@simonwjackson:drmario64`, private owned-ROM build | x86_64 and aarch64 Linux build targets |
| `drmario64` | Native Dr. Mario 64 launcher with account-owned state | x86_64 and aarch64 Linux build targets |
| `korri-plugin-super-mario-world` | `@simonwjackson:super-mario-world` | x86_64 and aarch64 Linux |
| `korri-plugin-zelda3` | `@simonwjackson:zelda3` | x86_64 and aarch64 Linux |
| `korri-plugin-zquest-classic` | `@simonwjackson:zquest-classic` | x86_64 and aarch64 Linux |
| `zquest-classic` | Standalone quest launcher with account-owned native state | x86_64 and aarch64 Linux |
| `zelda3` | Standalone native engine and owned-ROM launcher | x86_64 and aarch64 Linux |
| `korri-plugin-fallout1-ce` | `@simonwjackson:fallout1-ce` | x86_64 and aarch64 Linux |
| `korri-plugin-fallout2-ce` | `@simonwjackson:fallout2-ce` | x86_64 and aarch64 Linux |

## Fable II

[Fable II](plugins/fable-ii-recomp/README.md) matches the measured USA/Europe
GOTY ISO and uses Oery's native recompilation. Builds need the owned XEX on a
private build machine. Runtime extraction keeps the ISO unchanged and puts
native data and saves under the selected Korri account.

First installation needs about 15 GB of temporary free space; about 7 GB of
extracted files remains per account. Both Nix package checks passed. The
packaged x86_64 engine rendered the opening area, loaded a copied save and
responded to movement input. ARM gameplay and handheld acceptance are unverified.

Keep the XEX and compiled outputs out of public caches. The plugin instructions
cover private builds, package checks, and the owned-ISO verification task.
No publication, device trust change or target installation is included.

## Dr. Mario NES Recomp

[Dr. Mario](plugins/dr-mario/README.md) adds an exact-ROM native runner for the
owner's Europe cartridge. It stores native settings and save states separately
for each Korri account. The Turbo hack and the original Japan/USA ROM do not
match this build. Upstream calls it a playable preview, not a finished port.

```sh
nix build --option builders '' --option post-build-hook '' .#korri-plugin-dr-mario
nix build --option builders '' --option post-build-hook '' .#checks.x86_64-linux.korri-dr-mario-plugin
nix run --option builders '' --option post-build-hook '' .#verify-dr-mario -- '/path/to/Dr. Mario (Europe).nes'
```

Build off-device. The owner requires a prompt before sending builds to `fuji`
and a separate approval before device testing. Package and owned-ROM checks pass
on both architectures, including native save-file loading and account isolation.
Native outputs contain translated retail code and remain private. No signing, publication,
installation, or device trust change is included.

## The Simpsons Game

[The Simpsons Game](plugins/the-simpsons-game/README.md) matches the owner's
measured USA Xbox 360 ISO and builds the native recompilation for both Linux
architectures. Each Korri account gets separate installed assets, settings and
saves. It needs about 4.39 GB of extracted data per account, plus shader cache.
The original archive is not a discovery input; add its bare ISO to the library.

The native output contains translated retail code and must stay private.
No public binary publication or device trust change is approved. Package checks
and the opt-in `verify-simpsons` task are documented in the plugin README;
loader and extraction tests do not establish playable handheld performance.

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

## Melee PC

[Melee PC](plugins/melee-pc/README.md) adds a native beta runner for the measured
USA 1.02 ISO on both Linux architectures. It attaches to a registered release;
no general GameCube scanner is added. The launcher isolates native settings,
cache and cards per account. Upstream's updater cannot replace the managed binary.
Vulkan 1.1 is required. Game binaries remain private pending rights review.

```sh
nix build --no-link .#korri-plugin-melee-pc
nix build --no-link .#checks.x86_64-linux.korri-melee-plugin
nix build --no-link .#checks.aarch64-linux.korri-melee-plugin
nix run .#verify-melee -- /path/to/owned/USA-1.02.iso
```

Run on build machines. The opt-in owned-disc test requires a hardware Vulkan GPU.
Both architecture package checks passed. The x86_64 owned-disc test also passed
menu navigation, native card reopening, preference persistence and clean exit.
Full gameplay, ARM64 graphics, physical controls/audio and handheld performance
remain unverified. Public binary publication and device
installation are not approved.

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
and Jak 3 data. Devices receive native runtimes without game assets or compilers.
Build machines compile the Linux ARM runtime from pinned source with a Linux patch;
x86_64 uses the upstream release binary. Disc preparation runs explicitly on an
x86 build machine and selects `--instruction-set x86` or `arm64`. Transfer the
complete prepared tree afterwards. The runner matches only its architecture's
measured `out/<game>/iso/GAME.CGO` files in registered library releases. It does
not claim ISO files or create library entries. Signed publication and live
installation remain separate steps. Mini V2 validation requires owner readiness
approval before deployment.

```sh
nix build --no-link .#korri-plugin-opengoal
nix build --no-link .#checks.x86_64-linux.korri-opengoal-plugin
nix build --no-link .#checks.aarch64-linux.korri-opengoal-plugin
nix run .#prepare-opengoal -- --game jak2 --instruction-set arm64 --iso /path/to/owned.iso --output /path/to/new-data
nix run .#verify-opengoal -- /path/to/prepared-data --game jak2
```

## ActRaiser

[ActRaiser Recomp](plugins/actraiser/README.md) builds native code from the
supported owned USA cartridge on a private build machine. Devices receive
prebuilt packages. The Arcade/Nintendo Super System dump is not supported.

Unlike SMW and Zelda3, this build needs the ROM and produces copyrighted
ROM-derived code. Keep its inputs, helper, and output closures out of public
caches and release assets. Read the plugin instructions before building.
No publication or installation workflow is added.

The private build adds `Auto` to the game's native Screen ratio setting. It
fits flat and Diorama action stages to the window shape. The plugin README
describes its limits and the private GPU acceptance test.

## Dr. Mario 64 Recompiled

[Dr. Mario 64](plugins/drmario64/README.md) packages
`theboy181/drmario64_recomp_plus` from the owned US ROM. It adds a native,
hash-specific runner and keeps the original ROM unchanged. Native settings
and saves stay under the account root supplied by Core.

This is a private build. Keep retail inputs, generated code, and binary closures
out of public caches and releases. Run the documented commands with remote
builders, post-build hooks, and automatic signing disabled. Ask the owner before
sending files or build jobs to `fuji`. Read the plugin's acceptance table for
actual build and runtime coverage. Target declarations alone do not prove ARM support.

## 2 Ship 2 Harkinian

[2 Ship 2 Harkinian](plugins/2ship/README.md) adds a native Majora's Mask runner
for the measured NTSC-U 1.0 ROM. The plugin packages engine 3.0.1 without retail
data, extracts owned assets at launch, and preserves native configuration and saves.
Its Linux shutdown fix is covered by the opt-in owned-ROM test.

```sh
nix build --no-link .#korri-plugin-2ship
nix build --no-link .#checks.x86_64-linux.korri-2ship-plugin
nix build --no-link .#checks.aarch64-linux.korri-2ship-plugin
nix run .#verify-2ship -- /path/to/owned/USA-ROM.n64
```

Run these on build machines. CI uses no retail data. The optional runtime test
uses temporary assets and software rendering, not a physical handheld.
Signed publication and device installation require separate approval.

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

Solarus has moved to the official [korri-os/plugins](https://github.com/korri-os/plugins/tree/main/plugins/solarus)
repository. See that source for build instructions. This personal flake no longer
provides Solarus.

## Zelda3

[Zelda3](plugins/zelda3/README.md) launches the supported US A Link to the Past
ROM through a native engine on both Linux architectures. First launch extracts
assets locally. Configuration and saves remain in account-owned storage.
The package contains no ROM or runtime-extracted asset bundle. It does embed
opening-scene tilemap tables that match the original ROM. The upstream MIT license
does not establish Nintendo clearance. [The publication audit](docs/research/zelda3-publication-audit.md)
records the exact binary comparison and limits. Keep the current binaries private
pending a publication decision. Build machines compile the engine; devices receive
it prebuilt. Python asset extraction is not compilation.

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

## ZQuest Classic

[ZQuest Classic](plugins/zquest-classic/README.md) runs unpacked `.qst` files
through the native player. It preserves legacy's `zelda-classic` system and
standalone launch mode. Each account has separate native configuration and
saves. Saves use the quest's content hash, so renaming retains a save while
changed quest contents get a separate save. The editor and quest downloads
are outside this plugin's scope. The `public1` build removes bundled quests
and uncleared media. It supplies original sound cues, silent default music,
licensed replacement fonts, and neutral menu/ending graphics. Quests needing
legacy default tiles are explicitly unsupported; user quest music is unchanged.

```sh
nix build --no-link .#korri-plugin-zquest-classic
nix build --no-link .#checks.x86_64-linux.korri-zquest-classic-plugin
nix build --no-link .#checks.aarch64-linux.korri-zquest-classic-plugin
nix run .#zquest-classic -- /path/to/quest.qst /path/to/test-state
```

Build only on build machines. Checks use the real player, Core launch executor,
and Xvfb to exercise input, screenshots, save writes, and reload. They do not
establish physical-device, controller, or audio acceptance. The package retains
the legacy development snapshot and interpreter backend, not the latest stable
release. `zquest-classic-source` supplies a corresponding-source archive for
each architecture. The approved public cache is
`https://github.com/simonwjackson/korri-plugins/releases/download/cache/`.
Publication does not change existing device trust or clear user quest rights.
See the plugin README for limitations, licenses and the publication procedure.

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

The pack has moved to the official [korri-os/plugins](https://github.com/korri-os/plugins)
repository as `starter-pack` (`@korri:starter-pack`).
See that repository for source, credits, licenses and build instructions.
This personal flake no longer provides the pack.

## Publication boundary

The check-only GitHub workflows build plugin packages without retail game data.
It does not build the unrelated Skate 3 closure or upload release assets.
It does not sign packages, configure cache keys or install anything on a device.
Source commits and package construction are separate from signed-cache publication and device approval.
Do not bypass Korri's signature, publisher binding or exact-package approval checks to install plugins.
Signed publication and physical-device acceptance still need separate approval.
