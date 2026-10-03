# Dr. Mario NES Recomp on Mini V2

Verified on 2026-10-03: the signed ARM64 plugin is installed and enabled on the
Retroid Pocket Mini V2. Normal Korri launch runs the native executable as the
unprivileged runtime user. A compositor capture shows the game on screen.
The owner subsequently reported that the game works but feels faster than
expected. The package recorded below has an NTSC timing bug. It is installation
evidence, not proof of correct Europe playback speed. The PAL correction needs
separate device deployment approval.

## Installation and preservation

The owner approved device testing and stopping the existing game. The existing
ZQuest Classic session entered `stop-sigterm` and briefly returned
`HostRecoveryBlocked`. It completed before the scoped force-kill script passed
its identity gate, so that script sent no kill signal. No recovery record was
edited or removed manually.

| Item | Verified value |
|---|---|
| Source on main | `172e67c`, including implementation commit `f4b0022`. |
| Plugin | `@simonwjackson:dr-mario` |
| Package | `/nix/store/iz2l86l8cx55jysqg66nnv7yck8xkj03-korri-plugin` |
| Approval | `0d53d6b96c7e40fac368a3784876d7b68a978b936347aad74df9d2e653e17fce` |
| Native executable | `/nix/store/704adb3dmhx22mp6nw0fldp9mhawvn2g-drmario-nes-recomp-0-unstable-a234728/bin/DrMarioRecomp` |
| Existing cache | `file:///var/lib/korri-private-cache.h6odJOu2/cache` |
| Game ID | `01M41MF6N61VHNC9WTYGZ8G4DB` |
| Running unit | `korri-game-7f52bd81f0d31605d2332c63f073fd90.service` |

The package was absent before import. The build machine exported a private
signed cache using the existing personal publisher key. Signing material stayed
on the build machine. Normal inspection, exact-package approval, installation,
activation, and recursive signature verification passed. The declaration has
no services, ports, or required plugins. No public binary release was created.

The device retained `max-jobs = 0`, empty `builders`, `fallback = false`, and
`require-sigs = true`. It performed no builds or flake evaluation. No firmware,
partition, boot entry, system generation, or publisher trust changed. Final
checks preserved all 35 previous plugin selections and found no failed units.

The existing catalog importer added the owned Europe ROM while preserving all
2332 previous games, 2332 releases, scan roots, and existing locations. The ROM
is `/var/lib/korri/roms/Dr. Mario (Europe).nes` and retains SHA-256
`83914c08f82fc70779121760a48392af3a5988f015794eb53cbe1aa0a165c821`.
It was not placed in a Nix output or binary cache. Launch selected the native
runner explicitly and did not change persistent runner preferences.

## Runtime observations

| Check | Result |
|---|---|
| Normal launch | `app.local-games.launch.selected` started the exact native executable. |
| Sandbox | UID/GID 1000, `NoNewPrivileges=yes`, effective capabilities zero. |
| Display | Game window visible, focused and fullscreen in the 1240 × 1080 compositor output. The captured NES image keeps black margins. |
| Input access | The game opens `Korri Seat P1` and `Korri Seat P2`. This does not prove physical button response. |
| Audio routing | The DrMarioRecomp PipeWire client has a running output stream and two links to the speaker sink. |
| ROM and configuration | ROM unchanged. Native configuration and keybinds remain in account storage. |
| Save/load | Both build architectures passed the owned-ROM save-file loading test. Device save/load has not been exercised. |
| Physical acceptance | Owner reports the game works, but gameplay feels fast. Timing correction pending. |

The game runs in a PID namespace. Its audio client reports process ID 1 rather
than the host PID, so audio attribution used the client executable identity and
stream-to-sink links, not a host-PID match.

For this handheld only, the previously absent native
`/var/lib/korri/users/default/DrMarioRecomp/config.ini` sets `Fullscreen = 1` and
`Player1Source = 2`. These are upstream settings, not a plugin-wide default or
new schema. Native `keybinds.ini` was generated. Back up this account directory
separately from the ROM.

A game-board capture is not proof of user input, completed play, or save
correctness. No frame-rate or audible-quality claim is made.

## PAL correction, not yet installed

The owner approved correcting PAL clocks and rebuilding privately on `fuji`.
The corrected x86_64 and native aarch64 engines passed owned-ROM tests off-device.
Both measured 33247.497 CPU cycles/frame and 881.877 audio samples/frame. Timed
native saves bounded speed around 50 frames/second. Digital audio production
measured about 44.1 kHz, with no post-warm-up underrun, overflow or concealment
growth through the private PulseAudio null sink. Both ran 600 smoke frames with
zero dispatch misses and identical sampled framebuffer hashes. Source pins,
generated game code and native save format remain unchanged.

The earlier engine fails the new CPU regression at 29780.508 cycles/frame.
Earlier smoke and save checks did not measure playback speed. SDL's dummy audio
driver also supplied an inaccurate test clock. The final audio check uses a
private virtual sink and isolates both server and client state.

No PAL package replacement or game interruption is approved yet. The device
still has the package recorded above. No handheld PAL frame-rate, physical audio,
or restored-gameplay result exists. Deployment must retain existing account
files, catalog entries, plugin selections, signatures and publisher trust.

## Evidence

Private device stage: `/var/tmp/dr-mario-miniv2-deploy-l34j_bac`.
Private build-host export: `/tmp/dr-mario-miniv2-deploy-l34j_bac`.

The device stage retains `inspection.json`, `preservation.json`,
`installed-selection.json`, `before-catalog-import/`, `catalog-preservation.json`,
`routes.json`, `launch.json`, `sway-tree.json`, `dr-mario-running.png`,
`audio-nodes.json`, `audio-links.json`, and `final-verification.txt`.
The local capture is `/tmp/dr-mario-miniv2-running.png`.
