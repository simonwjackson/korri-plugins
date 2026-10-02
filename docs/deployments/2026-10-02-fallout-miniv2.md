# Fallout CE on the Mini V2

On 2026-10-02, the owner requested both Fallout CE plugins on the USB-connected
Retroid Pocket Mini V2. Both signed ARM64 plugins were installed, enabled and
added to the library. Both launched through korrid and rendered on the device.
Fallout 2 was left running at its main menu.

## Installed artifacts

The installed source revision is `44d2add4435d4058af42bce02af1f7104f159286`.

| Item | Fallout | Fallout 2 |
| --- | --- | --- |
| Plugin ID | `@simonwjackson:fallout1-ce` | `@simonwjackson:fallout2-ce` |
| Plugin output | `/nix/store/h7gg4mlskmihyz6ag4iwf1rmf5iy1xz1-korri-plugin` | `/nix/store/b3xm08d8m1sj9mgl0c4nc8x7ks3amxrm-korri-plugin` |
| Engine output | `/nix/store/wc132cyxfix606wckaq1iwqqcyd2g0ax-fallout-ce-1.1.0` | `/nix/store/02lq47jd1hgk8cczk71vj7m80zbghxbq-fallout2-ce-1.3.0` |
| Game ID | `01M3Z3PW4SCWQB7E2YFH33Z5SW` | `01M3Z3PW4S1E68DMMFPMY9EQ5W` |
| Selected runner | `@simonwjackson:fallout1-ce/fallout-ce` | `@simonwjackson:fallout2-ce/fallout2-ce` |
| Installed data | `/var/lib/korri/users/default/fallout-ce/` | `/var/lib/korri/users/default/fallout2-ce/` |

Each plugin output was absent before import. The build machine exported its
prebuilt closure to a private Nix cache using the owner's existing personal
signing key. The export extended the device's already-bound cache without
replacing prior entries. No key was transferred, trust binding changed, or
binary published publicly.

Native `korri-plugin inspect`, exact-digest `install`, and `enable` succeeded.
Recursive `nix store verify --sigs-needed 1` passed for both closures.
The device retained `max-jobs = 0`, empty `builders`, `fallback = false`, and
`require-sigs = true`. Nothing compiled on the device.

All 25 prior plugin selections matched their original hashes immediately after
installation. Before final acceptance, another deployment updated Zelda3 from
`gdk49lhyv59aia0f6z55xnljfqjwgqcq-korri-plugin` to
`ihc0ln79i1ii76v455ny7jj9jl5m93k1-korri-plugin`. Its previous selection retained
the original output. That concurrent update was identified and left unchanged;
the other 24 original selection hashes still matched.

## Owned data and catalog

Fresh copies came from the owner's supplied archives. No source archive or
existing save was overwritten. The new installations contain `MASTER.DAT`,
`CRITTER.DAT`, `DATA`, and native configuration. Fallout 2 also contains the
supplied UK patch's `patch000.dat`. No build-machine test saves were copied.
The DAT hashes match the [Fallout](../../plugins/fallout1-ce/README.md) and
[Fallout 2](../../plugins/fallout2-ce/README.md) source records.

Fresh native config files point to the supplied data and music with relative
Linux paths, using upstream's existing keys. No resolution INI was supplied;
the engines retained their upstream display defaults. Data folders follow the
observed default-account root and upstream's native engine directory names.
Ownership and permissions were set only on these new folders, matching the
account's existing `korrid:korri` writable layout. Both the game user and daemon
passed real read checks; the game user passed write checks.

The plugins intentionally have no generic `.dat` discovery claim. The operation
therefore added explicit authored records using Core's existing `GamePayload`,
`ReleasePayload`, and `Location::File` fields. It did not change their schemas or
edit private discovery state. Each release identifies its measured `MASTER.DAT`.
The existing `/var/lib/korri` storage binding supplies its relative location.
No scan root was added. `dos` preserves the first-party DOSBox convention for the
supplied Fallout DOS data; `windows` preserves legacy's Windows system identity
for the Fallout 2 Windows 95 media.

The operation backed up the current native catalog and device document before
editing them with the daemon and control socket stopped. It preserved existing
text and verified every prior record after insertion. All 29 previous games,
29 releases, storage records and locations remained unchanged. Native route
validation and `app.catalog.snapshot` confirmed both new games. Native per-game
runner selection chose each exact installed package.

## Runtime acceptance

The owner explicitly authorized stopping the current ActRaiser session. Korri's
normal exact-session stop succeeded; no force-kill was needed. The installer
then tested Fallout, stopped only that test session, and tested Fallout 2.

Both native engines ran as UID 1000, the existing `korri` user, with zero
effective capabilities and `NoNewPrivileges` set. Their working directories
matched the installed game folders. Sway reported visible, focused fullscreen
windows on the 1240 by 1080 output. Captured frames showed the Interplay startup
animation for both engines. A later Fallout 2 frame showed its main menu.
One later capture was black. A new capture after waking the existing output
showed the menu. No game or idle policy changed.

The system generation, internal root and ESP remained unchanged. No reboot,
partition write, firmware write, ACL change outside the new installations, or
input-policy change was needed.

## Limits

This device pass verified signed installation, library routes, native execution
and visible rendering. It did not independently verify audible sound, physical
touch/controller response, device save/load, or a complete game walkthrough.
The earlier native x86_64 and ARM64 build-machine save/load checks still stand.
No controller-to-mouse mapping was added. Saves remain in each native installation.

The pre-existing `korri-plugin-host.service` and missing
`korri-sunshine-input-setup.service` failures remained. No new failed unit appeared.
That separate Sunshine boot-restore problem was not repaired, and post-reboot
acceptance was not repeated. The installed selections were `Enabled` at final
verification. Another device still needs its own trusted delivery route and
exact-package approval.
