# The Simpsons Game on Mini V2

The signed ARM64 plugin was installed and launched on the owner's Mini V2 on
2026-10-02. A device capture showed gameplay in The Land of Chocolate.
The owner reported that the game was open. An arbitrary-aspect experiment
looked stretched, so the owner requested a return to 16:9 and a pause before
relaunch. That pause is the last verified device state in this record.

## Installed artifacts

| Artifact | Exact value |
|---|---|
| Source landing commit | `84eaa35f620c4535e9fbfd58c944fed57f10cbf0` |
| Upstream source | `YesterMester/TheSimpsonsGameRecomp`, `f63f57bcba29d3e7016fd867fad05adc85822bcb`, v0.0.6.2 |
| Plugin ID | `@simonwjackson:the-simpsons-game` |
| Plugin output | `/nix/store/s3xvfzaiq4jrns90vv6z9d84g3n14jsa-korri-plugin` |
| Native engine output | `/nix/store/rlh7yi06vy5sldmqi7s9rq9k8f9sz872-simpsons-recomp-0.0.6.2` |
| Native launcher output | `/nix/store/v6fsx9974wh26za639c9hb4cmwzky7nn-simpsons-launcher` |
| Library game ID | `01M3Z5T06H74H01GYKH9CEGN59` |
| Runner ID | `@simonwjackson:the-simpsons-game/simpsons` |

The x86_64 and aarch64 package checks passed on native build hosts. The ARM
build needed the upstream FFmpeg hidden-visibility fix recorded in the plugin
README. The native engine did not compile on the device.

At the owner's request, competing builds on fuji were temporarily frozen.
Detection was extended to remote Nix build workers after a newly dispatched
build was found. The build-exit cleanup resumed all paused work. The kernel's
frozen cgroup was confirmed absent afterwards.

## Private delivery and approval

The deployment reused the device's existing `@simonwjackson` publisher binding
and private Nix file cache. No key was added or transferred, and no trust setting
changed. The build machine signed the private cache with the existing personal
publisher key. No generated game binary, ISO or extracted asset was published
publicly.

An initial unsigned copy into the build machine's local store was refused.
Rather than bypass signature checks, the verified fuji output was exported
directly into a locally signed private file cache. The final device output was
absent before its signed import.

The actual `korri-plugin inspect` report requested no native service, port or
required plugin. It disclosed the normal unprivileged game-launch authority.
The exact-digest `install` and `enable` operations completed. Recursive
`nix store verify --sigs-needed 1` passed. Prior plugin selections were
hash-checked and remained unchanged through installation.

Device policy remained `max-jobs = 0`, empty `builders`, `fallback = false`,
and `require-sigs = true`. Root remained `/dev/sda22` and the ESP `/dev/sda21`.
No system generation, partition, firmware or boot-chain change was made.

## Owned media and library

The owner supplied `The Simpsons Game X360.rar` on myoko. Its ISO member was
measured before copying, and the device verified the copied bytes again:

| Media | Bytes | SHA-256 |
|---|---:|---|
| `simpsons-ntscu-cs.iso` | 7835492352 | `fd794e7a3025c3fd1340d25301658bac8c829a65d5e5e47d2663b431f869531b` |
| Extracted `default.xex` | 14200832 | `71d99dad06be1b512fc3058123b84fdad71339205a7e9249058ac5e34a82a231` |

The original archive stayed unchanged. The device copy is
`/var/lib/korri/roms/The Simpsons Game.iso`, beneath the existing ROM root.
Only that new file received the runtime user's read ACL. A real read check as
`korri` passed. No library-directory, controller or input-policy permissions
were widened.

The native catalog importer registered the file using the existing managed
`/var/lib/korri` scan. It preserved all 31 previous games and releases and
added no redundant scan root. Discovery state was not edited by hand.
The importer reported unclaimed and unreadable entries elsewhere, but the
new release and preservation assertions passed.

The owner chose separate storage for each Korri account. On this device,
installation, native settings and saves use
`/var/lib/korri/users/default/simpsons`. Extraction produced 7,968 files,
totaling 4,385,078,597 bytes. The installed XEX hash matched the build-host result.

## Native launch and display

Core's `app.local-games.runner.set` selected the exact installed runner for
this game. `app.local-games.launch.selected` started it through the normal
runtime-user service. The actual native executable ran as UID/GID 1000,
with zero effective capabilities and `NoNewPrivileges=yes`. It opened
`Korri Seat P1` through `P4` through the existing input route.

The initial native window was running but hidden behind the fullscreen kiosk.
The account's existing native `fullscreen` setting was enabled. Shared package
defaults remained unchanged. The owner then reported the game open.

At the owner's request, a later restart used `resolution = "1240x1080"` to
match the Mini V2's observed display dimensions. A captured frame showed
The Land of Chocolate with Homer, the HUD and the jump tutorial. This proves
that the native ARM engine reached gameplay and produced display output.
It does not prove correct arbitrary-aspect projection: both the owner and
the agent observed apparently stretched proportions.

The upstream parser accepts custom dimensions, but that is not equivalent to
verified camera/HUD adaptation. The presenter uses the reported video-mode
aspect ratio. The game-specific projection response still needs a matched-scene
comparison before claiming 1:1 or Mini V2 aspect support.

## Last verified state and limits

The owner asked to stop the game, restore 16:9, and ask before relaunching.
The exact game session was closed. The following native settings were written,
with a backup and preservation of unrelated settings and file ownership:

```toml
resolution = "720p"
fullscreen = true
present_letterbox = true
```

Core reported no active session and the old service's main PID was zero.
No relaunch was performed. Visual verification of the restored 16:9 mode is
pending the owner's readiness confirmation. Do not resume device testing
from this record alone.

The documentation follow-up passed formatting, lint and local artifact-reference
checks. Its fresh full-build attempt did not pass: the pinned upstream source
download hit certificate verification failure and then HTTP 403. No source pin,
TLS setting or signature policy was weakened. That fetch failure does not undo
the earlier successful build checks or change the installed artifact.

Native save creation and reload were verified on the x86 build host, not on
Mini V2. Opening controller descriptors does not prove physical button response.
Audible output, device save/reload, full-game completion and sustained handheld
performance remain unverified. No performance tuning or camera/HUD patch was
shipped as part of the resolution experiment.

Two pre-existing failed units, `korri-plugin-host.service` and
`korri-sunshine-input-setup.service`, remained unchanged at the device checks.
The game also logged accessibility-bus and audio CPU-info warnings. They did
not prevent the observed launch. These are separate from the aspect-ratio issue.
