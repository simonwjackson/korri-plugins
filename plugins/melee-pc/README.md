# Melee PC

`@simonwjackson:melee-pc` packages `999sian/melee-pc` v0.2.2-beta for Linux
x86_64 and aarch64. This is a native port, not Dolphin. It needs Vulkan 1.1 and
remains beta software. Upstream warns about crashes, shader compilation stutter,
and incomplete netplay. Package checks do not establish gameplay acceptance.

## Content and discovery

The runner attaches to an already registered library release with this measured
whole-file identity:

| Input | Value |
|---|---|
| Disc | Super Smash Bros. Melee, USA 1.02, GALE01 revision 2 |
| Bytes | `1459978240` |
| SHA-1 | `d4e70c064cc714ba8400a849cf299dbd1aa326fc` |
| SHA-256 | `0de05981a34156b9cedcef73c73d4244ac05cf6149ab3c9cfed917698819e464` |

Extract the ISO from your own archive before registering it. The launcher checks
the size and SHA-256 before it creates state or starts the game. A renamed file
with the same bytes works. An archive, compressed disc, other revision, or PAL
disc does not. Upstream supports more formats, but those are not measured inputs
for this plugin.

No general GameCube system or scanner is added. This plugin does not claim all
`.iso` files, create library entries, register folders, or extract game data.
The declaration uses the existing release-specific runner contract without a
system claim.

## Native state and updates

The host supplies `accountRoot`. SDL's native `melee-pc` preference name places
settings, cards and controller bindings in `<accountRoot>/melee-pc`. The launcher
also sends the native pipeline cache and `melee-pc.log` there. The wrapper does
not replace existing settings or saves. The native game still updates its own
state. A directory lock rejects concurrent launches in the same account. Separate accounts use separate directories.

The launcher clears inherited `MELEE_*` settings and uses the explicit disc
argument. This prevents host-wide test, recording, log or cache settings from
redirecting a launch. Native settings remain available in the game's F1 menu.
Korri core/config/settings overrides are not implemented and are rejected.

The executable and resources stay in the immutable package. `HOME` and the
working directory point there, and `APPIMAGE` is unset. The pinned updater checks
`HOME/Downloads` and then the working directory for downloads. Neither is writable,
and its replace/relaunch path requires `APPIMAGE`. Update checks can still contact
GitHub, but the updater cannot download into those paths or replace the managed
binary. This is packaging policy, not a general process sandbox. Netplay is not
blocked and remains subject to upstream's beta limits. No firewall or trust
settings change.

## Build and check

Run on build machines, never target devices:

```sh
nix build --no-link .#korri-plugin-melee-pc
nix build --no-link .#checks.x86_64-linux.korri-melee-plugin
nix build --no-link .#checks.aarch64-linux.korri-melee-plugin
nix run .#verify-melee -- /path/to/owned/USA-1.02.iso
```

Both builds consume pinned native release tarballs. They do not compile on a
device or need a game image. The ROM-free checks execute the target architecture's
actual ELF, check version and resources, validate the packaged declaration through
the real host, and exercise `korrid plugin-launch` with literal paths. They also
reject wrong-size and same-size invalid images without changing existing state.
`verify-melee` explicitly uses the owned ISO outside Nix inputs. It creates
private temporary account state and an authenticated Xvfb display. Vulkan uses
the build machine's hardware GPU. The port rejects CPU Vulkan adapters, so
Lavapipe alone is not sufficient. Logs and screenshots stay in the printed
private temporary directory. The test uses dummy audio, not physical speakers.

### Verification on 2026-10-02

| Check | x86_64 on `zao` | aarch64 on `fuji` |
|---|---|---|
| Native package, ELF/version, host admission, launch contract, invalid-disc rejection | Passed | Passed natively |
| Owned ISO through `korrid plugin-launch` | Passed | Not tested |
| Vulkan main menu and keyboard navigation | Passed on NVIDIA RTX 3060 Laptop GPU | Not tested |
| Same-account lock and unchanged input ISO | Passed | Not tested |
| Existing native card reopened and saved VSync preference applied | Passed | Not tested |
| Native window-close event, two launches | Exit 0 on both | Not tested |

The successful owned-disc run kept evidence at
`/tmp/korri-melee-owned-jtxor6n2`. The second launch logged the account's existing
card directory and applied `vsync 0` through a changed presentation mode.
The native game rewrites the card during startup, so byte-identical card files
are not the acceptance rule. These tests do not prove full matches, gameplay
save/load, physical controllers or speakers, netplay, or handheld performance.
No physical device installation or gameplay acceptance occurred.

For an explicit standalone launch, the same wrapper accepts an owned ISO and a
separate account root:

```sh
nix run .#melee-pc -- /path/to/owned/melee.iso /path/to/private/account
```

## Pin and rights

The upstream tag `v0.2.2-beta` resolves to
`ed0843a6f0d7cbd846e7774925fc0952c522ed95`. `package.nix` pins each release
archive by independently measured SHA-256, also checked against the GitHub release
asset digest. Its portable runtime includes no separate retail disc assets.

Recovered Nintendo/HAL game code is unlicensed. GPL-3.0-or-later covers only the
port code. `UPSTREAM-LICENSE.md` and `UPSTREAM-COPYING` preserve that distinction.
Do not publish native binaries or their Nix closures to public releases or caches.
Signing, public binary publication, and device installation need separate approval.
This repository adds no publication workflow for the package.

Sources: [native port](https://github.com/999sian/melee-pc),
[pinned release](https://github.com/999sian/melee-pc/releases/tag/v0.2.2-beta),
[main.c](https://github.com/999sian/melee-pc/blob/ed0843a6f0d7cbd846e7774925fc0952c522ed95/src/pc/main.c),
and [updater.cpp](https://github.com/999sian/melee-pc/blob/ed0843a6f0d7cbd846e7774925fc0952c522ed95/src/pc/updater.cpp).
