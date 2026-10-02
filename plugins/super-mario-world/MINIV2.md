# Mini V2 device test

Verified on 2026-10-02: the signed ARM64 plugin is installed and enabled on the
Retroid Pocket Mini V2. The native engine renders fullscreen and passes a snapshot
save/reload test in Korri's normal runtime-user sandbox. The owner confirmed that
movement, jumping, and speaker audio work after entering a level. Complete gameplay
has not been tested.

## Installed output and trust

| Item | Verified value |
|---|---|
| Plugin commit | `31e97bca21cf279b916501de94f74340e669a2e2` |
| Plugin output | `/nix/store/vrqkrccrpzlfdsm5jzpvvwj694a80r5k-korri-plugin` |
| Native engine | `/nix/store/cq9bgssgj070cxnfjp6l8gk98nyzavz0-snesrev-smw-unstable-eae20c6/bin/smw` |
| Plugin identity | `@simonwjackson:super-mario-world` |
| Runner | `@simonwjackson:super-mario-world/smw` |
| Exact approval | `88f10ac4e882feeb5b47b3f807b7033aca2bb2d7b8f1243a8305e13dd26fe56b` |
| Existing cache binding | `file:///var/lib/korri-private-cache.h6odJOu2/cache` |

The attached serial console identified the device. SSH's public-key fingerprint
matched that console before network access. No host-key check was bypassed.

The build host exported the prebuilt closure using the existing personal publisher
key. Signing material stayed on the build host. The package was absent before
`korri-plugin inspect` imported it through the already-bound cache. Inspection
reported no services, ports, or required plugins. Normal exact-package approval,
installation, activation, and recursive `--sigs-needed 1` verification passed.
No public binary release was created.

Device Nix policy remains `max-jobs = 0`, empty `builders`, `fallback = false`, and
`require-sigs = true`. The device performed no builds or flake evaluation.
Internal root `/dev/sda22`, ESP `/dev/sda21`, firmware, boot entries, and the system
generation stayed unchanged.

## Library and native runtime

The owned `Super Mario World (U) [!].smc` was copied into the existing SNES folder
under `/var/lib/korri/roms/`. Its SHA-256 remains
`d70c9c7716ad12c674fc7dd744736aa48d4d7b4237f58066be620fda26024872`.
It never entered the binary cache or a Nix output.

The native offline importer rescanned existing locations. It added game
`01M3YW9TAEQTAJDGVDH5139219` while preserving all 26 prior games, all 26 prior
releases, and all scan roots. Both Snes9x and the exact native SMW build appear as
routes. No persistent default-runner choice was changed.

Launch used `app.local-games.launch.selected`, not a direct administrator process.
The exact native executable runs as UID/GID 1000, user `korri`, with
`NoNewPrivileges=yes` and an empty effective capability set.
It opens `Korri Seat P1` through `Korri Seat P4` through the normal input boundary.
Opening those devices is not proof of physical button response.

Extracted assets are 353820 bytes with SHA-256
`3b66781c5c66522fc2106d400f96b56939a88c4a2128094132a9ace87f068f02`.
Configuration, assets, and saves remain under `/var/lib/korri/users/default/smw/`.

## Display, sound, and saves

| Check | Result |
|---|---|
| Stock windowed launch | The engine ran but the fullscreen portal obscured it. Normal session thaw exposed a tiled game window. |
| Scoped native `Fullscreen = 1` | A compositor capture showed the SMW title/demo across the 1240 × 1080 display. |
| Audio routing | The game's running SDL output linked to the active speaker sink. |
| Speaker monitor signal | Captured 274176 signed 16-bit samples. RMS was 1840.95 and peak was 11096. This does not prove audible speaker quality. |
| Snapshot save/reload | Normal session stop wrote `saves/save0.sav`. A fresh native launch loaded it without an open error and saved an advanced snapshot. |
| Configuration after testing | Fullscreen stays enabled on this handheld. Temporary `Autosave = 1` was restored to upstream default `0`. |
| ROM preservation | The original host file and the device copy retain the expected SHA-256. |

The second snapshot was 268928 bytes. Native logs confirmed both loading and saving
slot 0. This verifies snapshot persistence, not a completed level's SRAM save or
compatibility with emulator saves. No package-wide default changed.

## Sunshine blocker and remaining limits

The device already had a failed `korri-plugin-host.service` at the first probe.
Sunshine depended on the missing `korri-sunshine-input-setup.service` and retained an
unfinished enabled selection. SMW activation initially refused that condition.

The owner explicitly approved disabling Sunshine. `korri-plugin disable
@korri:sunshine` completed normal cleanup without removing its package or data.
SMW then enabled normally. Hash comparisons verified that Sunshine was the only
pre-existing plugin selection changed. Sunshine remains disabled until repaired.
The two historical failed-unit markers remain; this test did not repair Sunshine
or claim reboot acceptance.

The owner selected "Controls and audio both work" after the physical test request.
This is owner-reported acceptance of the handheld controls and audible sound, not
an automated measurement. SMW is left running. No full-game completion or frame-rate
measurement is claimed.

## Operational evidence

Device staging: `/var/tmp/smw-miniv2-deploy-7ucgzut6`.
Build-host export: `/tmp/smw-miniv2-deploy-7ucgzut6`.

The device stage contains `inspection.json`, `installed-selection.json`,
`before-library-import/`, `routes.json`, `audio-signal.json`, `save-roundtrip.json`,
`save-reload.log`, `smw-original.ini`, and `final-device-state.json`.
The compositor capture is `smw-running.png`. These private test artifacts are not
part of the plugin or its binary cache.
