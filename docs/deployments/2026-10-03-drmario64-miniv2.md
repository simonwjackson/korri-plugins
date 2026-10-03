# Dr. Mario 64 on the Mini V2

The owner authorized private signing and installation on the Retroid Pocket
Mini V2. The owner requires an Ask Questions approval before any game launch.
The signed ARM64 plugin is installed and enabled. Library registration and
native runner selection are verified. After both launch and session-stop
approvals arrived, the normal native route launched Dr. Mario 64.

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

## Approved native launch

The owner selected Start in Ask Questions prompt
`305bda40-680b-4781-8cfc-3e10719defe7`. NES `Dr Mario` had since replaced
The Deep. The owner separately approved stopping that exact NES session in
prompt `257cec8f-643e-4c02-8028-26e5e692af19`.

Core stopped only launch `7f52bd81f0d31605d2332c63f073fd90` through
`app.session.stop` with `expectedLaunchId`. No force-stop was needed.
`app.local-games.launch.selected` then started the exact installed native
Dr. Mario 64 runner with no warnings.

| Runtime observation | Verified value |
|---|---|
| Launch ID | `492191dc84fa26cdbe0c699d126010a2` |
| Systemd unit | `korri-game-492191dc84fa26cdbe0c699d126010a2.service` |
| Native PID | `56366` |
| Runtime account | `korri`, UID 1000 |
| Hardening | `NoNewPrivileges=yes` |
| Actual executable | The exact ARM64 engine listed above. |
| Core session phase | `running` |
| Video backend | SDL X11 on Xwayland. |

The first device screenshot showed the native title screen beside the portal.
The game window was focused and visible, but tiled at 620x1080.
An exact-window Sway command gave only that native window fullscreen space.
No global compositor rule or native settings file was edited. The resulting
window was focused, visible, and fullscreen at 1240x1080. A second inspected
screenshot showed the game's bottle tutorial. No synthetic controller input
was sent; these frames do not establish player-controlled gameplay.

The process mapped the device's Mesa 25.3.2 Vulkan drivers, including Turnip
and software Vulkan. Loaded driver libraries alone do not identify which
physical Vulkan device the renderer selected. The screenshots establish
rendered output on the actual device, not a complete GPU acceptance test.

## Remaining validation and notices

Audible sound, physical controllers, player-controlled gameplay, campaign
save/reload, native settings persistence, and restart behavior remain
unverified on this device. Leave the approved game running for the owner.

Startup logged `Failed to preload executable!` and a missing
`recompcontrollerdb.txt`, but the native title and tutorial rendered.
The mapping warning matters for the pending controller test. Do not infer
working controls from successful startup or loaded audio libraries.

The first screenshot also showed the portal's `BrainUnreachable` error.
Core's control-socket RPC remained available and the native game ran.
The portal error is separate from this successful native launch. Its cause
was not verified. No portal service or configuration was changed.

Captures and runtime receipts stay in the private deployment directories.
No ROM-derived screenshot or executable was published.
