# Personal Korri plugins

This is `simonwjackson/korri-plugins`, built separately from Korri OS.
The publisher namespace is `@simonwjackson`, following the existing personal
PICO-8 producer. A namespace declaration does not grant device trust.

## Discovery v2

System file rules now live in `systems.<id>.content`. Discovery scans only
folders paired with a system or group. It does not scan plugin data.
Measured original-content hashes also declare games for 2 Ship 2 Harkinian
and Super Mario World. These declarations have no fixed `file`: a matching
discovered release joins the declared game. The runners keep their hash gates.

OpenGOAL and Fallout CE declare exact prepared-file paths relative to each
account root. Their READMEs list the paths and complete-tree move requirements.
Prepared releases have no invented system. None of these plugins declares
session controls. The contract names that optional export `controls`.

The pinned Korri input predates discovery v2. Admission and sandbox package
checks must run against the integrated Core before deployment. The focused
source check needs Node 24, no game data and no display:

```sh
node nix/discovery-check.ts
```

## Packages

| Output | Plugin or contents | Platforms |
|---|---|---|
| `korri-plugin-opengoal` | `@simonwjackson:opengoal`, Jak trilogy including Renegade | x86_64 and aarch64 Linux |
| `opengoal` | Native runtime without game assets or compiler | x86_64 and aarch64 Linux |
| `opengoal-tools` | Off-device disc preparation and GOAL compiler | x86_64 Linux build machine only |
| `korri-plugin-2ship` | `@simonwjackson:2ship` | x86_64 and aarch64 Linux |
| `korri-plugin-super-mario-world` | `@simonwjackson:super-mario-world` | x86_64 and aarch64 Linux |
| `korri-plugin-signs-of-rain` | `@simonwjackson:signs-of-rain`, exact packaged PCK | x86_64 and aarch64 Linux checked |
| `korri-plugin-zquest-classic` | `@simonwjackson:zquest-classic` | x86_64 and aarch64 Linux |
| `zquest-classic` | Standalone quest launcher with account-owned native state | x86_64 and aarch64 Linux |
| `korri-plugin-mega-man-rock-n-roll` | `@simonwjackson:mega-man-rock-n-roll`, downloaded ZIP on native Godot 2.1.4 | x86_64 and aarch64 Linux |
| `korri-plugin-mega-man-arena` | `@simonwjackson:mega-man-arena`, downloaded Windows ZIP on `@korri:proton` | aarch64 Linux |
| `korri-plugin-mega-man-maker` | `@simonwjackson:mega-man-maker`, downloaded Windows ZIP on Proton-CachyOS arm64 | aarch64 Linux runs it; x86_64 builds |
| `korri-plugin-fallout1-ce` | `@simonwjackson:fallout1-ce` | x86_64 and aarch64 Linux |
| `korri-plugin-fallout2-ce` | `@simonwjackson:fallout2-ce` | x86_64 and aarch64 Linux |

## Signs of Rain

[Signs of Rain](plugins/signs-of-rain/README.md) references the game's native
flake package and generates an exact-PCK release hash at build time. Register
that PCK manually in the existing library. No general Godot discovery or
automatic game tile is added. Native data uses the supplied Korri account root.

The game input pins published `a5a3206`. Both architectures pass package,
TypeScript, actual Core admission and sandbox launch checks. The ARM package
and checks ran on the owner-approved fuji builder. The actual ARM Godot engine
also loaded a copied pack in private storage and rejected a missing pack.
There is no RG353M graphics, controller or 60 FPS acceptance, device installation,
trust change, or Core schema change.

## Jak and Daxter trilogy

[OpenGOAL](plugins/opengoal/README.md) runs prepared Jak 1, Jak II, Jak II: Renegade,
and Jak 3 data. Devices receive native runtimes without game assets or compilers.
Build machines compile the Linux ARM runtime from pinned source with a Linux patch;
x86_64 uses the upstream release binary. Disc preparation runs explicitly on an
x86 build machine and selects `--instruction-set x86` or `arm64`. Transfer the
complete prepared tree afterwards. The runner matches only its architecture's
measured `out/<game>/iso/GAME.CGO` files. The plugin declares three games;
Renegade is a second release of Jak II. Discovery v2 checks the fixed
account-relative paths in the plugin README. It does not scan prepared trees
or claim ISO files. Signed publication and live
installation remain separate steps. Mini V2 validation requires owner readiness
approval before deployment.

```sh
nix build --no-link .#korri-plugin-opengoal
nix build --no-link .#checks.x86_64-linux.korri-opengoal-plugin
nix build --no-link .#checks.aarch64-linux.korri-opengoal-plugin
nix run .#prepare-opengoal -- --game jak2 --instruction-set arm64 --iso /path/to/owned.iso --output /path/to/new-data
nix run .#verify-opengoal -- /path/to/prepared-data --game jak2
```

## 2 Ship 2 Harkinian

[2 Ship 2 Harkinian](plugins/2ship/README.md) adds a native Majora's Mask runner
for the measured NTSC-U 1.0 ROM. The plugin packages stable engine 5.0.1 without retail
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
`https://simonwjackson.github.io/korri-plugins/`.
The old release URL remains readable for existing device receipts but receives
no new metadata. See [PUBLICATION.md](PUBLICATION.md) for the Pages publisher.
Publication does not change existing device trust or clear user quest rights.
See the plugin README for limitations, licenses and the publication procedure.

## Mega Man Rock N Roll

[Mega Man Rock N Roll](plugins/mega-man-rock-n-roll/README.md) declares the
public Linux 1.3 ZIP as an artifact that korrid downloads, verifies and
unpacks (Korri ADR 0012 and 0013). The plugin ships only the URL and hashes,
never the game. It plays the ZIP's `data.pck` with Godot 2.1.4, which the
plugin builds from the upstream tag for x86_64 and aarch64 (MIT license); it
replaced the FEX runner on 2026-10-21. It moved here from `korri-os/korri` on
2026-10-20. It needs a Core with ADR 0013, which the pinned Korri input has.
The x86_64 package played the game's intro under Xvfb on a build machine.
Nothing has run the game on aarch64 or on a device.

## Mega Man Arena

[Mega Man Arena](plugins/mega-man-arena/README.md) declares the public Windows
4.2.3 ZIP as an artifact that korrid downloads, verifies and unpacks (Korri ADR
0012 and 0013), and runs it with `@korri:proton`'s Proton-CachyOS arm64 inside
an FHS environment. It replaces legacy Korri's `mega-man-arena` plugin. It
exists for aarch64 only. On 2026-10-21 Korri's `plugin-run` prepared and ran
it to the main menu on the Odin 2 Portal inside the game unit's sandbox;
korrid's catalog and download flow and controller play remain unverified.

## Fallout 1 and 2 Community Edition

[Fallout 1 CE](plugins/fallout1-ce/README.md) and
[Fallout 2 CE](plugins/fallout2-ce/README.md) provide separate native runners.
They match the measured `MASTER.DAT` hashes from the owner's installations.
They launch from the writable installation folder and preserve native config and
save behavior. Discovery v2 checks the declared account-relative files
`fallout1/MASTER.DAT` and `fallout2/MASTER.DAT`. Move each complete installation,
not only that file. There is no archive extraction or `.dat` content rule.
Native saves stay with the installation.

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
They do not upload release assets.
They do not sign packages, configure cache keys or install anything on a device.
Source commits and package construction are separate from signed-cache publication and device approval.
Do not bypass Korri's signature, publisher binding or exact-package approval checks to install plugins.
Signed publication and physical-device acceptance still need separate approval.
