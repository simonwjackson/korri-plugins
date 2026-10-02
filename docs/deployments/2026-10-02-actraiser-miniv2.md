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

## Limits and retained evidence

Campaign save/reload, full campaign completion, and reboot persistence were
not tested. The owner report is the evidence for physical audio and controls;
the agent did not independently operate them.

Two pre-existing failures were recorded and left unchanged:
`korri-plugin-host.service` failed restoring Sunshine, and
`korri-sunshine-input-setup.service` was not found. They did not prevent the
verified ActRaiser launch, but boot-wide plugin restoration remains unverified.

Initial device receipts and logs are in
`/var/tmp/actraiser-miniv2-deploy-gf_riq51/` on the device. The corresponding
private local receipt is `/tmp/actraiser-deployment-receipt.json`.
These temporary locations are diagnostic evidence, not a durable delivery
service. Another device still needs private delivery, a publisher binding,
and exact-package approval.
