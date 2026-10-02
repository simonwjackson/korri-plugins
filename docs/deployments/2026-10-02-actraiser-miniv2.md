# ActRaiser on the Mini V2

On 2026-10-02, the owner chose private builds from an owned USA ROM and
installation on the Retroid Pocket Mini V2. Both Linux architectures passed
native startup and acceptance checks. The signed ARM64 plugin was installed,
registered in the library, and launched through the normal korrid route.
The owner then confirmed audible sound and working controls.

## Initial installed artifacts

These values identify the initial installation, before the Auto viewport work.

| Artifact | Exact value |
|---|---|
| Integration source revision | `f5ef3f02775cdb5ddd210216f21d4fcb8fa92307` |
| Upstream source revision | `cdd76085a00e8beb090a7f0a07fcbc09a0e20670` |
| Plugin ID | `@simonwjackson:actraiser` |
| ARM64 plugin | `/nix/store/gkjl28k6gnlal1msya200imbsb7mv9gg-korri-plugin` |
| ARM64 engine | `/nix/store/zsksw41hnvsggxk24nw3z2s3m1d2h3x5-actraiser-0-unstable-cdd7608` |
| Library game ID | `01M3Z1NPSEDWHN7ZBYGSSB171W` |
| Selected runner | `@simonwjackson:actraiser/actraiser` |
| ROM SHA-256 | `b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0` |

The x86_64 build ran on a build machine. The aarch64 build ran on `fuji`.
Neither build ran on the device. The existing personal publisher key signed
the private closure locally; the secret key was not transferred to `fuji`
or the device. No ROM, generated game code, private executable, closure,
or gameplay capture was published.

The device accepted the real inspection, exact-package approval, installation,
and enable operations. Recursive signature verification passed. Previous
plugin selections, publisher bindings, and the system generation remained
unchanged. The build prohibition remained `max-jobs = 0`, empty `builders`,
`fallback = false`, and `require-sigs = true`. No partition or firmware write
was performed.

## Library and runtime verification

Live discovery returned `OperationUnsupported` with the message
`discovery is available only from the Android brain`. After the session was
idle, a backed-up offline import used the existing native catalog CLI.
It preserved all 28 existing games and 28 releases, reused the existing
storage registration, and added ActRaiser. Only ActRaiser's runner selection
changed. The ROM remained under the existing SNES library directory.

| Check | Observed result |
|---|---|
| Packaged contract and real sandbox launch arguments | Passed on x86_64 and aarch64. |
| Native startup and nonblank PPU frames | Passed on both build architectures. |
| Final GPU composite | Passed with software Vulkan on both build architectures and with Turnip on the actual device. |
| Native audio setting persistence and reload | Passed on both architectures and the device. This is not an audible-output test. |
| Managed resource update and unrelated-data preservation | Passed. Existing settings, saves, and the source ROM were preserved. |
| Concurrent native launch | A second launch using the same account directory was refused. |
| Corrupt and uninitialized saves | The game refused invalid edits and preserved corrupt input. No campaign save was fabricated. |
| Normal selected-runner launch | Started the exact installed native executable as UID 1000, the existing `korri` account. |
| Physical sound and controls | The owner reported that both worked. |

The device test used the production `korrid plugin-launch` executor, a temporary
account directory, dummy audio, and real Turnip/Wayland rendering. The normal
interactive launch used X11/Xwayland and reported
`Turnip Adreno (TM) 650`, Mesa `25.3.2`.

## Account-only fullscreen correction

The first normal launch ran successfully but Sway kept its window hidden behind
the fullscreen portal. The game-owned window had a 0x0 rectangle and no focus.
This was a presentation failure, not failed ROM validation or native startup.

Only the test's exact launch was stopped through `app.session.stop`. The native
account settings were backed up, then only `window_mode = Fullscreen` changed
in `ActRaiserRecomp/game/settings.ini`. Package defaults and global compositor
rules remained unchanged.

A fresh selected-runner launch made the native window visible, focused, and
fullscreen at 1240x1080 without a command to focus that new window. A private
device screenshot showed the game's name-entry scene. The subsequent owner
report confirmed physical sound and controls. Fullscreen alone does not imply
that the game viewport expands to the display ratio.

## Screen ratio Auto update

The owner then chose Screen ratio Auto for flat and Diorama action stages.
Source `aa844704e1858ef4d44b3519263b45ec23200d9a` landed on main. Its research
record, `docs/research/actraiser-auto-viewport.md`, holds the build-machine
results on x86_64 and aarch64.

| Artifact | Exact value |
|---|---|
| ARM64 plugin | `/nix/store/gcjq95ryl6wdn26pjrsfnrhsb3sn4l8z-korri-plugin` |
| ARM64 engine | `/nix/store/5fz1vfc9aswlqwv530pliarxgnz807pn-actraiser-0-unstable-cdd7608` |
| Exact-package approval | `ec26f3b17c27aeea7d1a3c219fa684aa83cb8eab827224417c34c2170c4632f4` |
| Retained previous package | `/nix/store/gkjl28k6gnlal1msya200imbsb7mv9gg-korri-plugin` |

`fuji` built the landed revision. Its closure is identical to the closure that
passed aarch64 acceptance, except the top-level plugin path: that path changed
only because the plugin README in its source input changed. The existing
personal key signed the closure locally. The device ran `korri-plugin update`
while no ActRaiser process was running. The update kept the previous approved
package as `previous` for rollback. Recursive signature verification passed.
ActRaiser settings and saves, other plugin selections, publisher bindings and
the system generation stayed unchanged. No session was stopped or started.

Installing the update does not select Auto. The player's Screen ratio stays as
saved until the player chooses Auto in the game's settings menu.

### Auto on the device panel

After korrid had reported no session for 120 seconds, a check ran three
isolated temporary accounts through production `korrid plugin-launch`. Each
used the installed package, a fullscreen Wayland window, Turnip Adreno 650
(Mesa 25.3.2), Auto saved in that account, and upstream's Aitos replay. The
checked frames are the classic screen (gf 1200, map 00/09), Aitos 04/04
(gf 1600) and the smaller room 04/05 (gf 2600). The same parser as the build
machine test evaluated the captures.

| Case | Drawable | Budget L/R/T/B | Final viewport | Result |
|---|---|---|---|---|
| Classic screen, all cases | 1240x1080 | 0/0/0/0 | unchanged native frame | Passed |
| Flat, CRT pixels | 1240x1080 | 0/0/18/18 | 0/0/1240/1079 | Scenery below the original view in 04/05; rendered rows below it in 04/04 |
| Diorama, CRT pixels | 1240x1080 | 0/0/18/18 | 0/0/1240/1079 | Scenery below the original view in 04/05 |
| Flat, square pixels | 1240x1080 | 1/1/0/0 | 0/2/1240/1076 | Scenery left and right of the original view in 04/04 |

With CRT pixels, the 256x224 view alone fits this panel at 1240x930, as the
classic screen's viewport shows, leaving 75-pixel bars above and below. In
the action stages Auto fills 1240x1079 instead.
All three runs exited 0. The system generation, publisher bindings and the
player's ActRaiser data tree had the same hashes before and after. No
ActRaiser process remained.

The panel runs at its real refresh rate, so each run reported about 2950
tick presents and 51 to 56 re-presents for 3000 game ticks. The build machine
tests are the exact-cadence evidence. The device check covers only the panel
shape; resizing is covered by the build machine tests. With the default
Diorama camera, the tilted planes still leave a thin background edge at the
top and bottom of the panel. Auto does not change the player's camera.

## Limits and retained evidence

Campaign save/reload, full campaign completion, and reboot persistence were
not tested. The owner report is the evidence for physical audio and controls;
the agent did not independently operate them.

Two pre-existing failures were recorded and left unchanged:
`korri-plugin-host.service` failed restoring Sunshine, and
`korri-sunshine-input-setup.service` was not found. They did not prevent the
verified ActRaiser launch, but boot-wide plugin restoration remains unverified.
After the device's clean reboots at 22:27 and 22:58 UTC, before the Auto
update, the failed-unit list was empty. After the first of those reboots,
korrid briefly reported `HostRecoveryBlocked` for session status; after the
second it reported no active session. Neither was changed by this work.

Initial device receipts and logs are in
`/var/tmp/actraiser-miniv2-deploy-gf_riq51/` on the device. The corresponding
private local receipt is `/tmp/actraiser-deployment-receipt.json`.
These temporary locations are diagnostic evidence, not a durable delivery
service. Another device still needs private delivery, a publisher binding,
and exact-package approval.
