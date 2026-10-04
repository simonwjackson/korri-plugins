# Signs of Rain on Odin, 2026-10-04

## Verified installation; not yet launched

The owner requested Odin after RG353M at `192.168.1.239` was unreachable.
USB reported `Odin 2 Portal NixOS`; the actual device tree confirmed
`AYN Odin 2 Portal`. Administrative SSH used `10.42.4.1:2222` and the existing
trusted `[192.168.1.103]:2222` host-key alias. No SSH host trust changed.
The offered key matched that existing entry before effects.

The owner explicitly approved configuring the existing `@simonwjackson`
publisher on Odin. The device's four existing personal receipts already used
`file:///var/lib/korri-private-cache.ns0pahye/cache`, but only `@korri` was
bound. The pre-existing plugin-host boot unit failed to restore those receipts.

The approved personal binding now uses:

```text
simonwjackson-plugins-1:4SchQgTMNU3syZ2ZzN/cJXPMigc/PIt+EaqHAStgJs8=
file:///var/lib/korri-private-cache.ns0pahye/cache
```

Only public configuration and signed NARs reached Odin. Private signing keys
stayed on their existing build machines. All prior publisher bindings and
trusted public keys remained. The personal public key was the only added key.

## Owner configuration

Root-owned configuration lives in `/var/lib/korri-owner-personal-publisher/`:
`publishers.json`, `nix.conf`, and a supported NixOS `publisher.nix` fragment.
The Nix wrapper includes `/etc/static/nix/nix.conf` and adds the personal key.
It does not freeze or replace the system's other Nix settings.

`/etc/tmpfiles.d/korri-owner-personal-publisher.conf` uses the existing tmpfiles
startup to expose only these two owner files at the normal publisher and Nix
configuration paths. Exact prior contents and symlink targets were retained
under the private `before/` directory. No new service or Core contract was
created. The active Nix daemon was told to reread configuration; no Korri
service restarted in this operation.

Both current configuration consumers and the tmpfiles application passed.
A reboot or full NixOS switch was not tested. The publisher JSON preserves the
current official binding rather than merging future official changes. Cost:
a later publisher/key change must be reconciled with this owner file. The
stored module fragment uses the existing
`services.korri.pluginHost.publishers` option. Future owner host composition
should import it and retire the two tmpfiles overrides after checking the
resulting bindings and Nix keys. Do not silently adopt new signing keys.

Download-only policy remained `max-jobs = 0`, empty builders,
`fallback = false`, and `require-sigs = true`. No handheld build ran.

## Exact fullscreen package

The published fix is `f961ca9a075f6379bb15c8bd9c90acf2fb0c0000`.
It requests Godot `--fullscreen` before the `--` user-argument separator.
The exact argv test failed before the implementation fix and passed afterward.
The final rebased source passed both x86_64 and aarch64 real Core admission,
types and sandbox launch-contract checks. ARM work ran on the approved fuji
builder, not the handheld. The native source still pins game `a5a3206`.

| Record | Verified value |
| --- | --- |
| Plugin | `@simonwjackson:signs-of-rain` |
| Package | `/nix/store/qp5pgxkl0bzbq91nfzq748mcq0100i21-korri-plugin` |
| Exact approval | `30a3e7e588fc16baed4dd80d36c94834dc4daaf5975232a298acfe1cc8b1c55a` |
| ARM check | `/nix/store/p8m5c485lkym94g47c8vd222vlyd2icm-korri-signs-of-rain-plugin-check` |
| Game package | `/nix/store/97nckav385lcmp3myk4lcjmnmf2kyc8s-signs-of-rain` |
| Delivered PCK SHA-256 | `02d21b4f97879f4106d7446a707d36434315d18089d05366bbda07d5a3111479` |
| Current desired state | `Enabled` |

Normal `korri-plugin inspect`, exact-digest `install` and `enable` succeeded.
The inspected package declared no native units, services, ports or plugin
requirements. Actual recursive `nix store verify --sigs-needed 1` passed on
Odin. No signature bypass or device compiler was enabled.

The cache publisher compared every existing same-path NAR fingerprint before
adding records. It published payloads before metadata and kept prior records.
It reused the coherent exact fuji PCK from the Mini delivery, not the different
workstation PCK with the same store path. Export-byte repeatability remains
unresolved; see the [Mini record](2026-10-04-signs-of-rain-miniv2.md).

The first enable attempt refused an existing unfinished Fable selection:

```text
korri-plugin: plugin @simonwjackson:fable-ii-recomp has an unfinished selection
```

The game stayed installed and disabled after that attempt. A later read-only
check found Fable's pending root absent and its active root matching its
unchanged committed package. This operator did not repair Fable or run
`restore-all`. A retry of only Signs of Rain enablement passed. All 25 prior
selection-file SHA-256 values remained unchanged throughout delivery.

## Remaining gates

Read-only Core session status reported `NoActiveSession`. Odin has three
authored releases: two tagged `xbox-360` and one `snes`. It has no authored
Linux release or authored system definition. The existing `linux` label is
established on Mini, not yet in Odin's authored releases. No catalog, device
storage, game location or save file was changed here.

Library registration and actual launch remain pending. Do not reuse a console
label for the native PCK or invent a Core system definition to make it match.
Use the normal exact release and literal file location after the owner resolves
the native classification. Preserve the three existing game/release records.

Obtain current Odin readiness before launch, display, sound, physical-control
or timed testing. Mini readiness does not authorize Odin tests. No Odin GPU
context, automatic fullscreen visibility, screenshot, physical controls, audio,
sustained frame time, temperature, throttling or 60 FPS result is claimed.
The Mini installation and session were left unchanged during this work.
