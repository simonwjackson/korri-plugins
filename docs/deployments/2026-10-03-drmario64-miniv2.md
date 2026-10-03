# Dr. Mario 64 preparation on the Mini V2

The owner authorized private signing and installation on the Retroid Pocket
Mini V2. The owner requires an Ask Questions approval before any game launch.
The signed ARM64 plugin is installed and enabled. Library registration and
native runner selection are verified. Preparation did not launch Dr. Mario 64.

## Exact artifacts

| Artifact | Value |
|---|---|
| Integration source | `389115cc33e3c30a56aa9d3afc9eed827806f9f9` |
| Upstream source | `af91e3bf56b1ffc329ff4327fdc2380515463de7` |
| Plugin ID | `@simonwjackson:drmario64` |
| ARM64 plugin | `/nix/store/afgh9vpkn9bk7qv2mbvhqcvv4jkpqvz8-korri-plugin` |
| ARM64 engine | `/nix/store/d4xghqzg5nbkkypsdqxzcab43ai8ijbm-drmario64-recomp-1.0.0-af91e3b/libexec/drmario64_recomp` |
| Exact-package approval | `6eba5e2312fbc0de8103e93a791c330525431278b29d3aa1e99b63444699c9f0` |
| Native runner | `@simonwjackson:drmario64/drmario64` |
| Library game ID | `01M41MGPRVK00QX6XRK7S5XZV6` |
| Library ROM | `/var/lib/korri/roms/Dr. Mario 64 (USA).n64` |
| Owned swap16 ROM SHA-256 | `613778b244784492a881c0d72d6017f82c39026706a406bd7ef95c6f33e53b89` |

## Verified installation

The x86_64 build ran on the development machine. The ARM64 build ran on
`fuji` after competing builds stopped. Both passed the checks recorded in
[the Linux research](../research/drmario64-linux.md).

The existing personal key signed a private file cache on the development
machine. The cache contains 369,161,446 bytes. The secret key stayed on that
machine. The device received only signed prebuilt artifacts and the owned ROM.
No ROM, generated game code, private executable, closure, or private log was
published.

The device used its existing publisher binding and private cache. Actual
`korri-plugin inspect` imported the previously absent exact package. Inspection
showed no native service, dependencies on other plugins, or exposed ports.
Approval covers the exact declaration and launch callback. A future game
launch has the existing runtime user's access to files and the display.
It must not run as the administrator.

Installation, enable, and recursive signature verification passed. Reading the
actual engine header verified AArch64 ELF64 without executing the engine.
All 34 previous plugin selections, publisher bindings, and the system
generation stayed unchanged. The policy remained `max-jobs = 0`, empty
`builders`, `fallback = false`, and `require-sigs = true`.
No device build, remote build dispatch, trust change, firmware write, or
partition operation occurred.

The first inspection stopped before import because its script incorrectly
required the cache itself to be root-owned. The actual cache belongs to
`korri`; its parent is root-owned. Both directories have mode `0700`.
The corrected guard checks that existing arrangement. No ownership or
permission changed.

## Verified library registration

Preparation did not stop The Deep. Its session ended while the registration
watcher waited. After three idle samples over 60 seconds, registration backed
up the catalog, device configuration, and private discovery state. The
existing offline catalog importer reused `/var/lib/korri` as the scan root.
The import preserved all 2,333 previous games, 2,333 releases, storage
registrations, and existing locations.

The owned ROM now resides in the existing ROM directory. Its SHA-256 still
matches the owned input. Only this game's runner selection changed. A fresh
`app.local-games.routes` response verified the selected native runner, exact
installed package, and no route warnings. The available RetroArch route was
not selected. Download-only policy remained unchanged.

## Pending physical validation

Ask Questions prompt `305bda40-680b-4781-8cfc-3e10719defe7` remains pending.
Do not repost it or infer launch approval from session changes. The prompt
mentions The Deep because registration was waiting when it was posted.
Registration has since finished. Another session, NES `Dr Mario`, was running
at the final readiness check. Its launch ID is
`7f52bd81f0d31605d2332c63f073fd90`. Approval to stop the earlier The Deep
session does not authorize silently stopping this different session.

GPU rendering, audible sound, controllers, gameplay, campaign save/reload,
and native settings persistence remain unverified on this device.
Signing and installation do not establish physical playability. Keep the
launch paused until the owner answers the next Ask Questions prompt.
