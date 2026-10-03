# ZQuest Classic on the Mini V2

On 2026-10-02, the owner approved installing ZQuest Classic on the Retroid Pocket
Mini V2 through its existing signed-cache route. The owner rebooted the device
before installation, clearing earlier failed units. The ARM64 plugin is installed
and enabled. Native execution, software-MIDI initialization, and fullscreen
rendering were verified under the unprivileged runtime-user sandbox. No community
quest was added to the permanent game library.

Corrections, added later the same day:

- Save reload was verified only by the build-machine checks. The device smoke
  loaded the quest and wrote a save. It did not reload one.
- The diagnostic smoke unit did not exit on SIGTERM. It was stopped with
  `systemctl kill -s KILL`.
- Upstream's default quest is its blank template module, not a playable quest.

A later update added a library quest and the kiosk launcher. See
[Kiosk launcher update](#kiosk-launcher-update).

## Exact installed artifacts

| Item | Verified value |
|---|---|
| Source revision | `ac24126c05396f0aa9f38dbe68ded48df2d2acd3` |
| Plugin ID | `@simonwjackson:zquest-classic` |
| Runner ID | `@simonwjackson:zquest-classic/zplayer` |
| Plugin output | `/nix/store/qrs0bab7yg35xkxcx32820p521bjp944-korri-plugin` |
| Native launcher | `/nix/store/5n3np8mlmnsy18isdl961s7sfwhbm7a8-zquest-classic-launcher-unstable-2026-06-18/bin/zplayer` |
| Native engine | `/nix/store/6w26ck31vxmbhysvjxznzd8g7ykbx9yq-zquest-classic-unstable-2026-06-18/bin/zplayer` |
| Audio configuration | `/nix/store/4w4n7izrxpmj0sb4z0jf9qpkjksjh7ly-zquest-classic-software-midi/share/zquestclassic-audio` |
| Approval digest | `5fc1864629d917c614df5820ee601c9a89560b79066d151b407b9144410159ba` |
| Existing publisher cache | `file:///var/lib/korri-private-cache.h6odJOu2/cache` |

SSH used the existing USB gadget link (`10.42.3.1`, port 2222) previously
checked through the attached serial console. The read-only preflight checked
`Retroid Pocket Mini V2`, `aarch64`, the existing publisher binding, the
no-build policy, zero active game units, zero other application windows, and an
idle session before import.

## Delivery, activation and native verification

The build machine exported the prebuilt ARM64 closure using the existing
personal publisher key. The key's owner, permissions, and derived public key
matched the already-bound publisher. No signing material left the build machine.
The device's existing private cache gained the signed records and NAR files
without deleting or replacing prior records. Nothing was published to a public
binary cache.

The real `korri-plugin inspect` imported the package through that cache. Its
report identified ZQuest Classic, its single native launcher, and the
`zelda-classic` system. The reviewed approval digest was passed to
`korri-plugin update`, followed by `enable`. The installed selection reports
`Enabled`, and `/run/korri-plugin-host/enabled-packages.json` contains that
exact output. Recursive `nix store verify --sigs-needed 1` passed for the
closure. Hash checks confirmed that all pre-existing plugin receipts and the
publisher binding file stayed unchanged.

A temporary diagnostic unit (`korri-zquest-smoke-wPUwWf.service`) launched
upstream's default quest through Core's `plugin-launch` entry point under the
runtime-user sandbox (`korri`, UID 1000, GID 1000). The process status
confirmed:

```text
Uid:        1000    1000    1000    1000
Gid:        1000    1000    1000    1000
CapEff:     0000000000000000
NoNewPrivs: 1
```

The native engine initialized Allegro, confirmed the active software-MIDI
configuration, loaded the default quest, and wrote a standalone save:

```text
Initializing Allegro... SFX.Dat...OK
Initializing sound driver... OK
ZQuest Classic Player, 3.0.0+local
OK
OK
Initializing music... OK
gfx mode set: 1 8bpp 640 x 480 
Loading Saved Games
...
write save: saves/sha256:2c9f827d17c88656ee1d5069856c35a4075051d162af602aa241d58240b58a05.sav
Finished Loading Saved Games
...
[QUEST METADATA]
Path: /var/lib/korri-zquest-smoke.wPUwWf/default.qst
ZC Version: 3.0.0-prerelease.163+2026-03-01.local
ZC Build Date: 2026-3-4 19:47:09 UTC
Gained item 93: Shield 1
Continue screen set to 0
global Script ~Init has exited.
```

Sway's IPC tree confirmed a visible, focused, fullscreen window:

```json
[
  {
    "pid": 6880,
    "name": "ZQuest Classic",
    "visible": true,
    "focused": true,
    "fullscreen_mode": 1,
    "rect": {
      "x": 0,
      "y": 0,
      "width": 1240,
      "height": 1080
    }
  }
]
```

A screenshot captured through `grim` verified rendered game content on the
device display: Link, life hearts, magic meter, item boxes, and minimap in full
1240x1080 fullscreen orientation. After verification, the diagnostic unit was
stopped with SIGKILL and its temporary directory was removed. No game unit
remained active.

## What is and is not verified

| Check | Result |
|---|---|
| Signed import from the existing private cache | Passed; exact signed closure verified on device. |
| Exact-package approval and update | Passed; previous selection updated and enabled. |
| Native unprivileged sandbox execution | Passed; UID 1000, zero effective capabilities, `NoNewPrivileges=yes`. |
| Audio driver initialization | Passed; native log confirmed `Initializing sound driver... OK` with software MIDI. |
| Fullscreen display rendering | Passed; Sway confirmed 1240x1080 fullscreen window and `grim` captured gameplay pixels. |
| Quest loading and save/reload | Passed in build-machine checks on x86_64 and ARM64. On the device, the quest loaded and a save was written; no save was reloaded. |
| Physical gamepad input and audible speaker sound | Not tested. No physical buttons were pressed; no human listened to device speakers. |
| Permanent library registration | Not performed. No quest file was added to `/var/lib/korri/roms`. |

## Limits

The plugin discovers `.qst` files only in folders selected for scanning.
Installation did not create permanent library records or user saves. The
packaged player is a development snapshot from June 2026, using the ZScript
interpreter and FreePats software MIDI. Later engine features or hardware MIDI
remain unsupported.

## Kiosk launcher update

### Library quest

The owner asked for any available quest. *The Deep* ships with upstream at the
pinned revision as `resources/quests/the_deep.qst`. The build machine fetched
its Git LFS object and checked SHA-256
`e37f20e41b90586575097214e01b96aa68c4b5c6b7eadfde781157311a640074` and size
5754150 bytes. It is at `/var/lib/korri/roms/zelda-classic/The Deep.qst`.
`korrid catalog import /var/lib/korri` added it as game
`01M3ZF1J9C008DSRE4Q5DPFD15`, with the ZQuest runner selected for the game.
The import kept the existing games, releases and storage locations. Backups
are in `/var/tmp/zquest-library-backup/`.

### Controller fault

A Core launch opened `Korri Seat P1` to `P4`, but the gamepad did nothing.
Allegro numbers joysticks in unsorted `/dev/input` order. The device lists
`event12` first, then `event11` (`P4`) down to `event8` (`P1`). The player's
joystick 0 was therefore `P4`, while Korri routes the device's controls to
`P1`. An injected B-East press on `P1` did not change the screen. The same
press on `P4` opened the quest's difficulty menu. Setting `joystick_index=3` by
hand fixed it, and the owner confirmed that the controls worked.

### Installed artifacts

| Item | Verified value |
|---|---|
| Source revision | `f21eb779516b2c6a09f3651aef90fe63a394ef6c` |
| Plugin output | `/nix/store/c58xydd7x02m23s2q9hlc4fsjchvjvi6-korri-plugin` |
| Native launcher | `/nix/store/fihhi3hzs0na4fkdd3x4mlxccj62wn0i-zquest-classic-launcher-unstable-2026-06-18/bin/zplayer` |
| Native engine | Unchanged: `6w26ck31vxmbhysvjxznzd8g7ykbx9yq` |
| Approval digest | `a40bc10138f025ed672ba9a91c0fbc5310379595551aba4463b172a6ad97c391` |
| Previous output | `/nix/store/qrs0bab7yg35xkxcx32820p521bjp944-korri-plugin` |

The update used the same preflight, signed private cache, inspection, exact
approval, `update` and `enable` steps as above. The declaration is unchanged:
no services, ports, native units or requirements. Korrid's PID, the publisher
binding and all 33 other plugin selections stayed unchanged.

The cache's `cache/` and `cache/nar/` directories were owned by UID 1000
(`korri`). Ten entries, including both directories, had that owner. They date
from 02:56 UTC on 2026-10-03, probably from another session's deployment. The
parent directory is still root-owned with mode 700, so other users cannot
reach the cache. Signatures stay required. The
inspection script now checks the parent instead of the cache directory's
owner. Ownership was not changed.

### Verification through Core

`app.local-games.launch.selected` started unit
`korri-game-8a05ba32205b1254cd44e481bd847789.service` from the new launcher.

| Check | Result |
|---|---|
| Command line | `zplayer -fullscreen -standalone "/var/lib/korri/roms/zelda-classic/The Deep.qst" sha256:e37f20e4….sav` |
| Fullscreen | Sway: visible, focused, `fullscreen_mode` 1, 1240x1080. The earlier manual `fullscreen = 1` was removed first. |
| `zc.cfg` | `replay_upload_prompt = 1`, `clicktofreeze = 0`. `replay_upload` is absent, so it stays off. |
| `controls.cfg`, scheme `Custom` | `joystick_index = 3`, `btn_menu = 0`. |
| Home (BTN_MODE) injected on `P1` | A still screen did not change. |
| Tap injected at the touchscreen centre | The screen did not change. No positive control shows that the tap reached the game. |
| A (B-East) injected on `P1` | The screen changed from the quest intro to gameplay. |
| Physical touch and Home | Not tested by a person. |

The account's `controls.cfg` also has `btn_s=8`, set by hand. Allegro's gamepad
button 8 is Start, and upstream's default `btn_s=10` is the left stick button.
Upstream's default `btn_ex2=8` is also Start, so Start now triggers both. The
original is in `controls.cfg.before-seat-fix`.
