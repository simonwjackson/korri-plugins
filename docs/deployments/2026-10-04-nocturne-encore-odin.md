# Scene Expansion on the Odin 2 Portal

The owner approved the update with "Go". The signed ARM64 Nocturne plugin
from commit `755e2e3` is installed and enabled on the Odin. It bundles Scene
Expansion from `simonwjackson/nocturne-encore` commit
`c0e341e908b8b3568c633c673edf94a7dc1d3428`.

The device recorded the startup at 2026-10-04 03:12:03. The game reached its
main menu. This verifies installation and mod loading, not expanded gameplay.
The test stopped after a shutdown timeout. The Mini V2 was not contacted.

## Exact selection

| Artifact | Value |
|---|---|
| Plugin ID | `@simonwjackson:nocturne` |
| Plugin output | `/nix/store/iip682cjz5y225gwv0pp07hvv1bg7qwh-korri-plugin` |
| Native output | `/nix/store/wkg94sx9530d03r2a10jv0wn4491i5wb-nocturnerecomp-1.4.5` |
| Odin approval | `a82d2b1a0c6005eef1e0277a065cc263d5e3cf2c09d21ebf294e0f04072298ed` |
| Previous plugin | `/nix/store/wz2fd5jwmvdsdijv194f3ba7nwh6ydy6-korri-plugin` |
| Game ID | `01M41A1EG9WD53DYQW0VRMRG56` |
| Test launch ID | `4ea786070ac59ae021abbf8e687c90f2` |

The build machine reused the compiled mod and native package. The final ARM
plugin wrapper and package check ran on the fuji builder. The existing personal
publisher key signed a private file-cache export. No signing secret or game
assets were transferred. Nothing was published to a public binary cache.

The Odin's existing bound cache received four new immutable files. Prior cache
entries stayed unchanged. The package was absent from the target store before
inspection. Core's real `inspect` and exact-digest `update` completed.
Recursive `nix store verify --sigs-needed 1` passed. The new selection stayed
`Enabled`, and its `previous` selection retains the original package and approval.

The device policy remained `max-jobs = 0`, empty `builders`, `fallback = false`,
and `require-sigs = true`. No trust configuration changed. The Odin compiled
nothing and dispatched no build. No firmware, partition, boot file, bootloader
state, or system generation changed.

## Runtime checks

Core's `app.local-games.routes` identified the new exact runner build. The game
launched through `app.local-games.launch.selected` on the Odin's own korrid.
The native process ran as `korri` with zero effective capabilities and
`NoNewPrivileges=yes`.

The fresh native log contains:

```text
Mod code plugin 'scene_expansion' loaded (libscene_expansion.so)
[scene_expansion] override main iter ok
[scene_expansion] expand install ok
```

The launcher linked `mods/scene_expansion` to the installed package. Process
maps show that exact mod library and only one `librexruntime.so`, from the same
native package. `SCENE_PROBE_DIR` was absent from the process environment.
The fresh log contains no scripted-pad installation message.

The log selected `Turnip Adreno (TM) 740`. Sway reported one visible, focused,
fullscreen game window at 1920x1080. Two captures three seconds apart differ.
The agent opened the later capture and verified the Castlevania main menu.
Its SHA-256 is
`264a75492e507cd8d66605a3a786b702e1d38392b6fb9ee4f51a7aaf7ec8bd21`.

## Preservation and shutdown

| Check | Result |
|---|---|
| Original library and private asset copies | All 216 measured file hashes match in both locations. |
| Settings | `settings.toml`, `nocturnerecomp.toml`, and `mods/graphics_settings.cfg` retain their pre-test bytes. |
| Other plugin selections and host configuration | All 26 protected file hashes match. |
| Native per-title profile | One byte differs between the running-state and post-stop checks. Both versions are retained. Its meaning is unknown. |
| Game stop | The stop RPC returned `HostRecoveryBlocked`. Systemd killed the exact test process after its existing 90-second stop timeout. |
| Final session | The game PID is gone and Core returns `SessionCompleted`. No failed units remain in the final query. |

The changed file is
`/var/lib/korri/users/default/nocturnerecomp/58410847/profile/Player/63E83FFF`.
Both versions are 18 bytes. Only offset 17 differs. The SDK's
`src/system/xam/user_profile.cpp` identifies this as a native title-specific
binary profile setting. It does not establish the meaning of its contents.
The agent did not overwrite it or claim that all account data stayed
byte-identical. The pre-test backup is under the evidence directory's
`state-backup/58410847/profile/Player/63E83FFF`; `profile-after` holds the later
version.

The earlier [Odin test](2026-10-03-nocturne-odin.md) also observed
`HostRecoveryBlocked`. This update does not fix it or establish clean shutdown.
Five duplicate-cvar registration errors in the current log also appear in the
Odin's earlier logs without Scene Expansion. No recovery record was deleted or
rewritten by the agent.

## Limits and rollback

Expanded rooms, HUD docking during gameplay, tearing, physical controls, audible
sound, save reload, and full-game acceptance remain unverified on the Odin.
This pass did not change the native graphics settings or advance into gameplay.
Further device testing needs the owner's approval.

The previous exact signed plugin is retained. With no active game, the normal
administrator rollback command is:

```sh
sudo korri-plugin restore @simonwjackson:nocturne
```

This swaps software selections. It does not restore profile data or settings.

Private evidence is on the device under
`/var/tmp/nocturne-encore-odin-41lh3zre/`. Build-host copies are under
`/tmp/nocturne-encore-odin-41lh3zre/evidence/`. Reports include `inspection.json`,
`installed-selection.json`, `runtime.json`, `observation.json`, `stop-facts.json`,
`profile-facts.json`, and `final.json`. Screenshots, game binaries, profile data,
and signing material are not committed to this repository.
