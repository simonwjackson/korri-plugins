# Signs of Rain on Mini V2, 2026-10-04

## Verified delivery

The owner selected the connected Retroid Pocket Mini V2 instead of RG353M.
USB reported `RP Mini V2 NixOS`; SSH and the device tree confirmed the hardware.
The existing administrative endpoint was `root@10.42.3.1:2222`.

The existing `@simonwjackson` publisher bound the personal public key to the
private file cache. No publisher binding or Nix trusted key changed on Mini.
Private signing keys stayed on build machines. Download-only policy remained
`max-jobs = 0`, empty builders, `fallback = false`, and `require-sigs = true`.

Native `korri-plugin inspect`, exact-digest `install`, `enable`, and recursive
`nix store verify --sigs-needed 1` succeeded. The plugin declared no services,
ports, dependencies on other plugins, or native units. Every prior selection
hash remained unchanged.

| Record | Verified value |
| --- | --- |
| Plugin | `@simonwjackson:signs-of-rain` |
| Package | `/nix/store/ckfrb09yyf0k3z8smi7rknaai152sw5v-korri-plugin` |
| Approval | `1fd17335410b971212ee0d892f8a3277bd92392601d11b8e1c5a53c98c333486` |
| Game package | `/nix/store/97nckav385lcmp3myk4lcjmnmf2kyc8s-signs-of-rain` |
| PCK SHA-256 | `02d21b4f97879f4106d7446a707d36434315d18089d05366bbda07d5a3111479` |
| Game ID | `01M42ECFW6AHTYNF2138T4KA7N` |
| First Core launch | `1b643164f3b0c5ea48e2746c39bdc1e5` |

## Existing library contracts

Authored game, release and file-location records used the existing schema.
Four existing OpenGOAL releases established the device's `linux` system label.
The new exact-release route reused it without adding a system, family,
discovery extension or Core API. Its explicit storage root was the immutable
pack directory; no ROM copy or broader filesystem permission was required.

All 2,334 prior games and releases remained semantically unchanged. The real
Core routes response selected exactly the Signs of Rain runner. The real
catalog snapshot included its tile. No Korri service restarted.

The native reader reloads authored files without daemon restart. Publication
has no multi-file transaction: a concurrent read can reject the brief mixed
candidate. The operator staged all files, retained exact-byte backups, checked
for concurrent edits, and verified both real consumers after publication.

## Actual native graphics and fullscreen defect

After current owner readiness, Core launched the selected package as `korri`
under its normal systemd sandbox with `NoNewPrivileges=yes`. The process ran
the AArch64 Godot engine, not the argv observer used by build checks.

Its journal reported:

```text
OpenGL API OpenGL ES 3.2 Mesa 25.3.2 - Compatibility - Using Device: freedreno - FD650
```

An actual compositor screenshot initially showed the portal. Its window tree
showed `Signs of Rain (DEBUG)` hidden behind the fullscreen portal on the same
workspace. A transient fullscreen-and-focus command targeted only the exact
Godot PID. A subsequent actual screenshot showed the game and its 3D valley
beneath the introduction sheet. No compositor configuration changed.

The runner now passes Godot's `--fullscreen` before the user-argument separator.
The real Core argv contract test failed when its expected fullscreen argument
was absent from the launcher, then passed after the fix. Hardware acceptance
of the corrected automatic fullscreen request is a separate gate.

The owner switched the next installation target before reporting button or
sound results. Physical controls and audio remain unverified. No sustained
frame-time, temperature, throttling or 60 FPS result was obtained. The Mini
session was left untouched when the owner requested RG353M, then Odin.

## Export-byte mismatch

Workstation and fuji packs occupied the same Nix output path but had different
SHA-256 values:

| Export | Actual PCK SHA-256 |
| --- | --- |
| Workstation | `c2119d74d9a605867881901223605b29f67095acac85130ed5a24d12437d42fb` |
| Fuji | `02d21b4f97879f4106d7446a707d36434315d18089d05366bbda07d5a3111479` |

The actual Godot reader listed 98 members in each pack. Three compiled scene
members differed: the exported main scene and imported female and male
villager scenes. The other 95 member hashes matched. The cause is not proved;
this does not establish replay equivalence.

Delivery used the exact fuji pack and the generated plugin containing its
hash. Matching existing workstation dependencies were reused only after their
actual NAR hashes and reference lists matched fuji. Conflicting pack outputs
were never imported or mixed. Existing builder signatures and the approved
personal publisher signed the normal transfer; signature checks stayed on.

Pinned tools do not prove repeatable export bytes. Fix export repeatability
separately. Until then, inspect and approve actual package bytes, and register
only the PCK hash declared by that exact package.
