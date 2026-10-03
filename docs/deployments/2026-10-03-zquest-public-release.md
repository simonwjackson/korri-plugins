# ZQuest Classic public release, 2026-10-03

The quest-free public player is published for x86_64 and aarch64 Linux.
Both native runtime checks and both extracted-source rebuilds passed.
Anonymous public downloads and native Nix signature/content verification passed.
The cleaned build was installed and ran a native diagnostic replay on the
Mini V2. No active game was stopped.

## Published source and cache

- [Versioned binary payloads and corresponding source](https://github.com/simonwjackson/korri-plugins/releases/tag/zquest-public-31ebc60a054f).
- [Mutable signed-cache metadata](https://github.com/simonwjackson/korri-plugins/releases/tag/cache).
- Cache URL: `https://github.com/simonwjackson/korri-plugins/releases/download/cache/`.
- Exact source revision: `31ebc60a054fdc64ab132f02595ff63c8237a2f2`.
- Public key: `simonwjackson-plugins-1:4SchQgTMNU3syZ2ZzN/cJXPMigc/PIt+EaqHAStgJs8=`.

This is an unofficial modified `unstable-2026-06-18-public1` player.
Its engine pin remains `882c906b17e35b4105188e6305ae2929aeba30e3`.
The release tag identifies the tested source, not a later shared `main` tip.

| Architecture | Exact plugin output |
| --- | --- |
| x86_64-linux | `/nix/store/c77fm7yxzamrdcyw33cx89i273p37c14-korri-plugin` |
| aarch64-linux | `/nix/store/mwj2nnj88jag2dx3cn0m9d1l24375nl7-korri-plugin` |

Each release has `paths-SYSTEM.txt`, `revision.txt`, and an architecture-specific
offline registration metadata archive. Offline metadata grants no publisher trust.

| Corresponding-source archive | SHA-256 |
| --- | --- |
| `zquest-classic-source-x86_64-linux.tar.xz` | `ce68fa54511e534aa85ba6030808c66f1d0f611dfe574d66221898b69830810c` |
| `zquest-classic-source-aarch64-linux.tar.xz` | `1fd6693030d84f10e2565de3ef8a1a923ff49c60bf77c9280ce1ef587ba6b709` |

## What is included

The player has original procedural sound cues, silent default MIDI tracks,
licensed ProggyVector-derived compatibility fonts, and neutral built-in graphics
and ending text. It retains the licensed ZC Commons assets and their notices.
It includes no bundled quest or NSF soundtrack. User quest music is unchanged.

Quests needing the omitted legacy default tile bank fail with an explicit error.
Compatibility identifiers and generic engine logic remain. Font advances and
heights match the original slots, but glyph designs differ. The package does not
provide a starter quest. User content needs its own redistribution rights.

Runtime resources contain `PUBLIC-CHANGES.txt`, upstream GPL/AUTHORS, native
library notices, FreePats notices, and asset/font licenses. Source archives
include the cleaned patched engine, four explicit CMake dependency sources,
generators, inputs, integration recipes, notices and a standalone Nix recipe.
They exclude 190 non-build dependency media files. Their source-media gate also
rejects unreviewed binary/media files outside the runtime resources directory.

The [publication audit](../research/zquest-publication-audit.md) records why the
old media was excluded. Byte and provenance checks are not full legal clearance.
The old private packages and old unclean source archives were not published.

## Verified behavior

| Gate | Result |
| --- | --- |
| Native x86_64 and aarch64 runtime checks | Passed. Real Core admission and launch, input, screenshots, saves/reload, rename identity, account isolation, concurrent-session refusal and resource protection were exercised. |
| Native generated-asset reader | Passed on both architectures. It loaded 61 PCM samples, 101 font slots and metrics, seven MIDI tracks and two bitmaps. |
| Silent MIDI playback | Passed on both architectures. Every default timer/loop boundary was exercised, including ending loop 129–225 and overworld loop 17–EOF. |
| Original generated win-room | Passed on both architectures. The built-in ending accepted acknowledgement, wrote the save and backup, and returned to the quest. |
| Interpreter replay | Passed on both architectures. Only 26 graphics hashes were rebaselined for the replacement fonts. Upstream traces, RNG, timing and controls remain exact. |
| Extracted corresponding source | Passed on both architectures. All 3,404 listed hashes per archive and whole-bundle media checks passed. Each extracted `default.nix` built the native player. ARM compilation used the existing `fuji` builder. |
| Runtime closure review | Passed. There are 138 paths per architecture, 276 distinct paths total, and 79 reviewed engine resources. No quest, NSF, save, secret file or unrelated private plugin was found by the closure file/path scans. |
| Signed staging and public retrieval | Passed. Fresh exact-root caches, personal signatures, both offline archives, source hashes and committed revision were checked. Anonymous downloads matched the staged bytes. Nix checked all eight public custom NARs and their signatures. |

Both source archives were uploaded and digest-verified before binary publication.
The standard Korri publisher then published payloads before mutable metadata.
Upstream system-library metadata and signatures were verified against
`https://cache.nixos.org`; those payloads were not copied into this release.
No private device cache, user quest, save, test closure or signing secret was
an upload input.

These off-device checks do not prove audible physical output,
physical-controller behavior or all-quest compatibility. The native device test
below establishes startup, fullscreen rendering and sound-driver initialization.
The previous private Mini V2 installation remains documented separately in
[2026-10-02-zquest-miniv2.md](2026-10-02-zquest-miniv2.md).

## Mini V2 installation and native smoke

Initial preflight found another active game. The owner was asked whether to
stop it. Before any stop action, a later read-only preflight reported
`SessionCompleted`, no game units and no other application windows. This session
performed no stop. Installation and testing proceeded only after that idle gate.
The other game's identity and session details remain in private evidence.

The device imported the exact published ARM plugin through its existing private
signed-cache binding. It retained that binding, required signatures, and used
normal inspection, exact-package approval, update and enable commands.

- Installed package: `/nix/store/mwj2nnj88jag2dx3cn0m9d1l24375nl7-korri-plugin`.
- Approval: `02c4a05975a4f0682cdda74d8f6250892d3efbc16d734f84b9862c3c2345a060`.
- Device evidence: `/var/tmp/zquest-miniv2-deploy-wrrf2gdo`.

The one-off diagnostic ran the installed engine and launcher's resource setup
with an original generated room in an isolated account. It used a Core-equivalent
systemd sandbox, not a library entry or Core-managed session. It ran as UID/GID
1000, with zero effective capabilities and `NoNewPrivs=1`. The compositor reported
a visible fullscreen window. The captured 1240×1080 framebuffer showed the
original geometric room and hero, not a blank screen. The native log confirmed
sound-driver initialization.
The launcher resolved P1 to joystick index 3. The bounded native replay exited
itself with `Result=success` and `ExecMainStatus=0`; no forced stop was used.

All 33 other plugin selections, publisher bindings, system generation and korrid
PID matched their before-install records. The user's quests and saves were not
inputs to the diagnostic or publication. The device kept `max-jobs=0`, empty
builders, `require-sigs=true` and `fallback=false`. No compilation, firmware or
partition write occurred on the device. The public cache URL was not adopted.

This device smoke does not establish physical-controller input, audible speaker
output, save/reload on the device, or a playable community quest on the cleaned
build. Save/reload and the ending were verified in the native build-machine
checks. The diagnostic images and user content remain private.
