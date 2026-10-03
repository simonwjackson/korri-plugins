# Melee preparation on the Odin 2 Portal

The owner approved copying and installation on 2026-10-03. Launch requires a
separate question through the question tool and an explicit answer. The agent
must not treat installation approval as launch approval.

## Target and preflight

The existing verified SSH route identified the target as `AYN Odin 2 Portal`
and `aarch64`. Its active system was:

```text
/nix/store/f2w50achvn2xklzdckys34pz20a4qqn6-nixos-system-odin2portal-sd-card-26.05.20251221.a653104
```

The device reported 425 GiB available. No systemd units failed at preflight.
The hardware Vulkan driver directory contained the Freedreno ICD. This file's
presence does not prove Melee rendering on the GPU.

Nocturne was already running. Korri reported game `01M41A1EG9WD53DYQW0VRMRG56`,
launch `3e585de98d0f8663b9faf0dc0db5897c`, phase `running`. The agent did not stop
it, restart korrid, or change its selected plugin while preparing Melee.

The device retained `max-jobs = 0`, empty `builders`, `fallback = false`, and
`require-sigs = true`. Its existing `@simonwjackson` publisher binding used:

```text
simonwjackson-plugins-1:4SchQgTMNU3syZ2ZzN/cJXPMigc/PIt+EaqHAStgJs8=
file:///var/lib/korri-private-cache.ns0pahye/cache
```

No additional publisher, key, or public distribution route is approved here.
The binding's activation-persistence limit is documented in the earlier
[Nocturne deployment](2026-10-03-nocturne-odin.md).

## Artifacts and delivery

The implementation source is commit `727c528`. The ARM64 output is:

```text
/nix/store/dzvzhpg0fw228318znziz2wsl55j99lp-korri-plugin
```

The build machine `fuji` recreated this exact output from the pinned packaging
source. The handheld performed no build and dispatched no build. An unsigned
build-host copy was refused by Nix. The agent signed the existing output with
fuji's existing cache key instead of bypassing signature verification. The
personal publisher signs the private delivery cache on the development machine.
No signing secret is copied to the device.

The owner ISO identity remains:

```text
0de05981a34156b9cedcef73c73d4244ac05cf6149ab3c9cfed917698819e464
```

## Preparation status

The signed plugin is installed and enabled. Its approval digest is:

```text
1b8e611014e87c1acb4ec475afc3cb31843582b8a35eed51d3946b250f9c1132
```

Core's `inspect`, exact-digest `install`, and `enable` commands succeeded.
Recursive `nix store verify --sigs-needed 1` passed. The owner ISO was copied to:

```text
/var/lib/korri/roms/Super Smash Bros. Melee (USA) (En,Ja) (v1.02)/melee.iso
```

The transferred and installed ISO hashes matched the measured source. The
runtime user received read and traverse ACLs on this new subtree, not write
access. Existing plugin selections, catalog YAML, device YAML, Nix settings,
and publisher settings retained their hashes. The system generation did not
change. No service was restarted. Nocturne retained the same running launch ID.
At the end of preparation, Melee had not started. Launch approval was still
pending.

The first cache merge stopped because an existing dependency's `.narinfo`
contained fewer additional signatures. Its NAR identity and every non-signature
field were identical. The retry preserved existing entries after checking
those fields. It did not overwrite signatures or disable Nix verification.

Evidence is on the device under `/var/tmp/melee-odin-deploy-46nm4yxx/`:
`transfer-receipt.json`, `inspection.json`, `installed-selection.json`,
`existing-files-sha256.json`, `session-after-install.json`, and `prepared.json`.
The private staging directory retains a second ISO copy and a cache copy.
These copies use additional storage and are not public releases.

The plugin matches only the measured release. It declares no GameCube system
or generic ISO discovery claim. This preparation does not create catalog
records or add a discovery claim to obtain a library launch. Library registration
remains separate work. A standalone runtime test does not prove library launch,
Core session ownership, or physical controller routing. The renderer
experiment invokes the installed `plugin-launch` callback under a transient
runtime-user unit. `/var/tmp/melee-odin-runtime-profile.json` records the actual
running Nocturne unit's sandbox and its filtered display/audio environment.
The profile retains zero capabilities, `NoNewPrivileges=yes`, private PID and
temporary namespaces, and the existing inaccessible control paths. Capturing
this profile did not start a game process or change the active game.

## Approved renderer test

The owner selected `stop-nocturne-and-launch` in question
`melee-odin-launch-approval`, ask `51fe5256-eedd-49bb-becc-3c7a86bff871`.
The agent issued a stop request only for the recorded Nocturne session.
Core returned `HostRecoveryBlocked`. The unit was still in `stop-sigterm`,
and Core still reported phase `stopping`. Melee was not started at that point.
A later check verified that Nocturne had no process and Core was idle. No
recovery record was deleted, and no daemon was restarted to force that result.

The installed callback then started Melee in `melee-renderer-test.service`.
The native executable was:

```text
/nix/store/i6gqn5j5v59hjmsggp3s5nrs0ihh0rxz-melee-pc-0.2.2-beta/libexec/melee-pc/melee
```

The native PID was `35372`, UID `1000`, account `korri`. Its effective capability
mask was zero and `/proc/35372/status` reported `NoNewPrivs: 1`. The transient
unit reused the observed host sandbox, including its private PID and temporary
namespaces and inaccessible control paths. It is not a Core-owned game session.

The display was initially powered off. The first capture waited for the display
and exceeded its timeout. The agent powered on `DSI-1`, then made only Melee's
recorded window fullscreen. The next observation reported a visible, focused
window named `melee-pc`, fullscreen mode `1`, with a 1920×1080 rectangle.

The native log selected:

```text
graphics backend: vulkan (auto), adapter: Turnip Adreno (TM) 740 [5143:43050a01], driver: turnip Mesa driver: Mesa 25.3.2
```

The agent opened `melee-odin-later.png`. It showed the first-run prompt:
"The Memory Card in Slot A has no saved Game Data. Create Game Data?"
The `Yes` option was selected. This is observed rendering, not an inference
from a live process or the GPU log. Two captures three seconds apart had the
same hash, consistent with an unanswered static prompt. Their SHA-256 was:

```text
2f686aba20b6483cc0b366c22cfcbb26f669e3fb292c2b564db65aefbdda8f12
```

The log also reported `Failed to open /proc/cpuinfo` and two
`Failed to close file at idx: 0` messages. Their effect on gameplay or saving
has not been established. The sandbox was not weakened to remove them.
No systemd units failed during observation. Original catalog, device settings,
plugin selections, Nix settings, publisher settings, and the system generation
still matched the preparation snapshot.

Additional private evidence is in the same staging directory:
`nocturne-stop-request.json`, `nocturne-stopped.json`, `standalone-launch.json`,
`melee-observed.json`, `runtime-profile.json`, `melee-window.json`,
`melee-native.log`, and `melee-odin*.png`.

| Acceptance item | Result |
|---|---|
| Signed ARM64 installation | Verified with recursive signature checking. |
| Native startup and hardware Vulkan rendering | Verified at the first-run memory-card prompt. |
| Runtime user and sandbox | Verified UID, zero capabilities, and `NoNewPrivs`. |
| Korri library launch and Core session ownership | Not verified; no library record was registered. |
| Physical controls | The owner reported no D-pad response in the standalone test. Managed-session input is untested. |
| Audible sound, gameplay, save/reload, performance, and netplay | Not verified. |

The owner attributed the D-pad result to the input permissions normally acquired
by the launcher. Main's `host/session_state.rs` calls `begin_session` and acquires
an input-seat lease before starting the game unit. The standalone invocation did
not take that path. The exact device-side permission failure was not inspected.

The agent closed only the recorded renderer window through Sway. Its process
exited and systemd reported `Deactivated successfully`. The ISO hash remained
unchanged. Core reported `SessionCompleted` for the old Nocturne session.
`renderer-exit.log` and `renderer-stopped.json` record these results.

The subsequent read-only catalog check found only the Nocturne game and release.
The installed system declarations contained no GameCube record, and Melee's
measured release was not registered. `registration-facts.json` records that
check. The existing `config/catalog.rs` contract requires a release's `system`;
its value is unresolved for this disc. Normal launcher preparation must reuse
an existing GameCube catalog or wait for the owner to choose that identifier.
It must not assign a system from the ISO extension or its directory name.
No managed Melee launch has occurred.

Binary closures and the owner's disc remain private. Public binary publication
has not been approved.
