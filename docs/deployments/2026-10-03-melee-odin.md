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
No Melee process has been launched, and no launch approval is recorded.

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
Core session ownership, or physical controller routing. The next renderer
experiment can invoke the installed `plugin-launch` callback under a transient
runtime-user unit. `/var/tmp/melee-odin-runtime-profile.json` records the actual
running Nocturne unit's sandbox and its filtered display/audio environment.
The profile retains zero capabilities, `NoNewPrivileges=yes`, private PID and
temporary namespaces, and the existing inaccessible control paths. Capturing
this profile did not start a game process or change the active game.

ARM64 graphics, audio, physical controls, gameplay, save/reload, performance,
and netplay remain unverified. Binary closures and the owner's disc remain
private. Public binary publication has not been approved.
