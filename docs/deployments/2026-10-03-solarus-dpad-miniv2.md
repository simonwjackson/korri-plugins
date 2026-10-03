# Solarus D-pad correction on the Mini V2

The signed Solarus D-pad correction is enabled on the Retroid Pocket Mini V2.
Yarntown restarted through Korri using the corrected engine. Native SDL lookup
of the owner's recorded direction sequence now passes. The owner confirmed
that all four D-pad directions are correct and that the game plays well.

## Cause and correction

The owner reported that D-pad Up moved Down and Left moved Right. The left
stick worked correctly. The owner also reported A rolling and B attacking.
A passive evdev capture recorded physical Up, Right, Down, Left reaching
`Korri Seat P1` as the correct Linux hat values, each followed by release.

Solarus sets `SDL_GAMECONTROLLERCONFIG_FILE` before initializing controllers.
Its bundled Linux Xbox 360 entry overrides SDL's correct default mapping with
four inverted hat directions. A native probe reproduced that exact failure
using the installed library, database, and real Korri-seat GUIDs.

| Binding | Original entry | Corrected entry |
|---|---|---|
| Up | `dpup:h0.4` | `dpup:h0.1` |
| Right | `dpright:h0.8` | `dpright:h0.2` |
| Down | `dpdown:h0.1` | `dpdown:h0.4` |
| Left | `dpleft:h0.2` | `dpleft:h0.8` |

`plugins/solarus/xbox360-dpad.patch` changes only this Linux Xbox 360 entry.
The sticks and face buttons retain their original bindings. No Core input
routing, quest data, save bindings, or device controller settings were changed.
The correction does not repair OpenGOAL/Jak's separate input path.

## Installed artifacts

| Item | Verified value |
|---|---|
| Source revision | `ae9c46bf573de78bcc477072352d36b3cfb05cc6` |
| Plugin ID | `@simonwjackson:solarus` |
| New ARM64 output | `/nix/store/1nqkm6qm41phg6jxi6a2b5dgfwq2k6d5-korri-plugin` |
| New native engine | `/nix/store/xf296sr07m5w6nyih9cc6pwpl6j1cywg-solarus-2.1.4/bin/solarus-run` |
| New native database | `/nix/store/d82598bylazgnsfxrv7la9qgwzdd0bc3-solarus-2.1.4-lib/share/solarus/gamecontrollerdb.txt` |
| Exact approval | `78245cf387a08b10a57bfecb65231dd539daa668f632f2a57438de9d60bb3b46` |
| Previous output retained by the package manager | `/nix/store/22bnbln32hn8kj978kqrmqx9zxmm4gcf-korri-plugin` |
| Existing publisher cache | `file:///var/lib/korri-private-cache.h6odJOu2/cache` |
| Quest game ID | `01M41ARXREEDSH00H11N2NYMJ8` |
| Updated launch ID | `d5dddac61fcf2efc7176632519f01a68` |

The x86_64 output is `/nix/store/krfwvlfz28gfvacfc2m3831p0k74xm5m-korri-plugin`.
Native checks pass on both architectures, including SDL mapping lookup for the
generic Xbox 360 GUID and four observed Korri-seat GUIDs. The original database
fails the new regression test. Existing launch, literal-argument, unsupported
input, account-isolation, archive/directory, and native save/reload checks pass.
Nix formatting and Python formatting/lint checks pass.

[GitHub Actions run 37140649176](https://github.com/simonwjackson/korri-plugins/actions/runs/37140649176)
also passed for the landed revision on both architectures. It completed
successfully on 2026-10-03 at 17:42 UTC.

## Delivery and restart

The build machine exported the prebuilt ARM64 closure with the existing
publisher key. No key or quest data entered the exported closure. SSH retained
strict host-key checking. The device used its existing private cache and normal
`korri-plugin inspect` admission. Recursive signature verification passed.
The inspected declaration introduces no services, ports, or required plugins.

The cache directory was observed as owned by `korri`, unlike the original
installation's root-owned cache. Its parent remained root-owned with mode
`0700`, preventing runtime-user traversal. The update kept the observed owner,
group, and mode unchanged. Publisher bindings and signature enforcement stayed
unchanged. No ownership or permission repair was attempted.

The owner explicitly permitted closing and restarting the current quest.
A scoped compositor window close targeted the exact existing Yarntown process.
The engine logged `Simulation finished` and `Closed Lua`. Save backups retain
both the state before close and the state before package update.

The first package-manager call used `install` incorrectly. It refused because
Solarus was already installed and changed no selection. The correct command
is `korri-plugin update ID CACHE PACKAGE APPROVAL`. A concurrent package
operation briefly held the global operation lock, and a later state check
found that `zquest-classic` had changed independently. The updater stopped
before writing. Both snapshots were retained, and the next check preserved
the newly observed unrelated selections. The Solarus update did not revert
or rewrite `zquest-classic`.

The normal `update` and `enable` commands selected the new output. The enabled
registry and installed selection agree. The previous approved output remains
recorded by the package manager. Hash checks verified unchanged quest bytes,
account saves, catalog files, publisher bindings, unrelated current plugin
selections, and cache ownership. The selected NixOS system stayed unchanged.
The device performed no compilation, flake evaluation, build dispatch, trust
change, system activation, reboot, partition operation, or firmware write.

`app.local-games.routes` reported the new output and native program.
`app.local-games.launch.selected` started the updated launch as user `korri`.
The process has UID/GID 1000, no effective capabilities, and `NoNewPrivileges`.
The exact-PID focus/fullscreen workaround remained necessary. The compositor
reported the window visible and focused. A later screenshot showed Yarntown's
language selector. This is not a persistent fix for portal window handoff.
The owner declined further automatic-focus work and plans to use gamescope.

The original recorded direction sequence now passes the same native SDL probe
against the updated database on the device. The engine log verifies that this
new database was used during the real launch. `save_1` remained byte-identical
through update and relaunch before physical acceptance testing.

## Remaining limits

The owner confirmed physical D-pad gameplay after the correction: "All four
directions are correct." The owner has not explicitly confirmed audible sound.
Native save preservation is checked,
but device Continue/save/reload acceptance is not complete.

The earlier session logged `No such custom entity model: 'ephemeral_effect'`
when rolling, from `scripts/action/dash_manager.lua:55`. This is a separate
quest compatibility error. The D-pad patch does not change the quest or repair
that error. The host smoke test did not exercise rolling.

## Private evidence

The device stage is `/var/tmp/solarus-dpad-deploy-bv6kmeiu`.
It contains `inspection.json`, `installed-selection.json`,
`recursive-signature-verification.log`, `saves-before-close/`,
`saves-before-install/`, `saved-hashes.json`, `previous-session-exit.log`,
`preserved.json`, `preserved-at-update.json`, `concurrent-selections.json`,
`cache-ownership-before.json`, `routes.json`, `launch.json`, `running.json`,
`dpad-check-before.json`, `dpad-check-after.json`, `dpad-check-after.log`,
`updated-engine.log`, `sway-tree.json`, and `yarntown-updated.png`.
The later language-selector screenshot is retained on the build machine as
`/tmp/solarus-dpad-deploy-bv6kmeiu/yarntown-updated-title.png`.
These operational records and save backups are not public release assets.
