# ZQuest Classic on the Mini V2

On 2026-10-02, the owner approved installing ZQuest Classic on the Retroid Pocket
Mini V2 through its existing signed-cache route. The owner rebooted the device
before installation, clearing earlier failed units. The ARM64 plugin is installed
and enabled. Native execution, software-MIDI initialization, and fullscreen
rendering were verified under the unprivileged runtime-user sandbox. No community
quest was added to the permanent game library.

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
stopped and its temporary directory was removed. No game unit remained active.

## What is and is not verified

| Check | Result |
|---|---|
| Signed import from the existing private cache | Passed; exact signed closure verified on device. |
| Exact-package approval and update | Passed; previous selection updated and enabled. |
| Native unprivileged sandbox execution | Passed; UID 1000, zero effective capabilities, `NoNewPrivileges=yes`. |
| Audio driver initialization | Passed; native log confirmed `Initializing sound driver... OK` with software MIDI. |
| Fullscreen display rendering | Passed; Sway confirmed 1240x1080 fullscreen window and `grim` captured gameplay pixels. |
| Quest loading and save/reload | Passed in tests on native x86_64 and ARM64 build machines and in device smoke. |
| Physical gamepad input and audible speaker sound | Not tested. No physical buttons were pressed; no human listened to device speakers. |
| Permanent library registration | Not performed. No quest file was added to `/var/lib/korri/roms`. |

## Limits

The plugin discovers `.qst` files only in folders selected for scanning.
Installation did not create permanent library records or user saves. The
packaged player is a development snapshot from June 2026, using the ZScript
interpreter and FreePats software MIDI. Later engine features or hardware MIDI
remain unsupported.
