# Yarntown verification for Solarus

Yarntown v1.0.6 is installed on the Retroid Pocket Mini V2 and launched through
Korri. Host gameplay and save/reload passed. Device rendering passed after a
manual focus correction. The owner verified gameplay with the left stick, A rolling, and B attacking.
The owner reported all four D-pad directions inverted. The native SDL lookup
check reproduced that inversion in the engine's bundled controller database.
The correction passes native checks and CI on both architectures and is
installed on the Mini V2. The original direction trace now passes native SDL
lookup against the updated device database. Physical acceptance of the
correction, audible sound, and device save/reload remain unverified.

The owner authorized choosing any Solarus quest and required an `ask_user`
decision before device work. The owner then chose idle-only installation and
launch. Session checks found the previous Castlevania session completed and
no running game units. No running game was stopped.

## Selected release

[Yarntown](https://www.solarus-games.org/games/yarntown/) is an action RPG
published through the official Solarus quest library. The page links directly
to the author's GitLab quest-package artifact. This is a playable quest, not
the synthetic save fixture used by the plugin checks.

| Fact | Observed value |
|---|---|
| Release | Yarntown v1.0.6 |
| Original file | `yarntown-v1.0.6.solarus` |
| Archive size | 20527236 bytes |
| Measured SHA-256 | `1337d1074dac824de876924c5b0c043ad62d1bcc2fb4851d8b389af02dd04c5a` |
| Quest format | `solarus_version = "1.6"` in the original `quest.dat` |
| Native write directory | `write_dir = "yarntown_saves"` in that same file |
| Native game save | `save_1`, selected by `scripts/menus/title.lua` |
| Declared quest resolution | `416x240` |

Official download:
`https://gitlab.com/maxmraz/yarntown/-/jobs/artifacts/v1.0.6/raw/yarntown-v1.0.6.solarus?job=quest-package`

The download resolved to GitLab job `710051292`. ZIP integrity checks passed.
The hash above identifies the measured bytes; it is not an independently
published checksum. The quest archive is unchanged and remains outside Git.

The official page lists GPL v3, CC-BY-SA 4.0 and proprietary components.
This is a personal-use staging download, not a new redistribution package.
Do not put the quest into the plugin repository, a Nix closure, CI assets, or
a public binary cache as part of this test.

## Local evidence

The private stage is `/tmp/solarus-yarntown-c78t8ahk`.
`receipt.json` records the original URL, resolved URL, size and hash.
`quest.dat`, `main.lua`, the title/pause menu scripts and `archive-files.txt`
were read directly from that archive without modifying it.

The host test uses the packaged Solarus runner through `korrid plugin-launch`,
an isolated Xvfb display, Mesa software rendering, OpenAL null output and a
new temporary account root. No host or device player save is used.
Host gameplay and save/reload passed. The original archive ran through the
actual packaged `solarus-run` program and the production launch callback.
Screenshots showed the title menu, playable Hunter's Dream scene, HUD, and
native pause/save dialog. Simulated keyboard input selected New Game, fired
the pistol, opened the pause menu, and saved.

The first save contained `quicksilver_bullet_amount = 19`. After a normal exit
and a fresh process, Continue restored that game and the HUD showed 19 bullets.
Another shot and native save produced `quicksilver_bullet_amount = 18`.
Both runs closed normally without Solarus errors. The archive hash stayed
unchanged. The test save remains only in the temporary host account.

| Evidence | Private artifact |
|---|---|
| Gameplay | `host-new-game.png`, `host-moved.png` |
| Native save menu | `host-save-dialog.png` |
| Reloaded gameplay with 19 bullets | `host-loaded-game.png` |
| Second save | `host-saved-again.png`, `host-verification.json` |
| Engine logs | `host-run-1.log`, `host-run-2.log` |

These checks used x86_64, Xvfb and Mesa llvmpipe. OpenAL used null output, so
no audible sound is verified. Keyboard simulation is not physical gamepad
acceptance. These host checks do not establish device controls, audible sound, or device
save/reload. Device rendering evidence is recorded below. The test process and its isolated X server were stopped afterward.

## Native controls and settings

The original quest source binds Return or Space to title-menu confirmation.
Down selects New Game from the initial Continue entry. In play, D opens the
pause/save dialog, C attacks, X fires the pistol, and Space performs actions
or dodges. F11 toggles fullscreen through `sol.video.set_fullscreen`.
The quest saves native engine settings through `sol.main.save_settings` on
normal exit. These are quest behaviors, not new Korri override fields.

## Device installation and launch

The original archive was copied to `/var/lib/korri/roms/Yarntown.solarus`.
Its SHA-256 still matches the measured download. No host save was transferred.
The quest remains outside the Nix store and binary cache.

The existing scan root `/var/lib/korri` covers that file. No scan root was added.
The native `korrid catalog import` ran as `korrid`, with the daemon stopped while
its catalog files were updated. The control socket and daemon restarted after
import. Backups retain the prior catalog, device configuration, and discovery
state. Assertions verified all 38 existing game records, all 38 existing
release records, all existing locations, and all scan roots remained unchanged.
Only the new quest received a read ACL for user `korri`.

Native discovery produced game ID `01M41ARXREEDSH00H11N2NYMJ8` and one Solarus
route. `app.local-games.routes` reports the existing signed plugin output
`/nix/store/22bnbln32hn8kj978kqrmqx9zxmm4gcf-korri-plugin` and no route warnings.
The device's `app.local-games.list` and `app.discovery.snapshot` calls are
unsupported. The importer and route RPC were used instead. No catalog schema
was edited manually.

After another idle check, `app.local-games.launch.selected` started launch
`63d0fd11e1ef4a7c0b79156c25d43395`. The native engine ran as UID/GID 1000, the
existing `korri` user, with no effective capabilities and `NoNewPrivileges`.
An initial verification script expected the name `korri` in systemd's `User`
property. Systemd returned `1000`; process credentials verified the correct
user. The script now accepts the verified name or UID.

### Display limitation

The first compositor capture showed Korri's error dialog rather than Yarntown.
The Solarus window existed but was hidden behind the fullscreen portal.
A scoped `swaymsg` command focused and fullscreened the exact live Solarus PID.
The compositor then reported the window visible, focused, and fullscreen.
No persistent compositor configuration was changed.

The first session ended normally after about 26 seconds. The engine logged
`Simulation finished` and `Closed Lua`; systemd reported successful exit.
A native `settings.dat` existed, but no `save_1` was present.

After the owner's request to continue, another session check found the device
idle. Launch `94c10f684ddb1cec3ce0aeafe0c16f60` started through the same RPC.
The same scoped focus correction was applied. A fresh compositor capture
showed Yarntown's language selector with English selected. Korri reported the
session `running` and the native engine ran as `korri`.

This verifies rendering on the Mini V2. It does not prove that a future portal
launch brings the game forward automatically. That integration issue remains
unresolved and is outside this plugin test.

### Remaining acceptance checks

The engine connected to `Built-in Audio Speaker Playback` after a PipeWire
connection error. This verifies an audio connection, not audible sound.
The engine opened `/dev/input/event8` through `/dev/input/event11`. The owner
later verified left-stick gameplay, A rolling, and B attacking, but reported
an inverted D-pad. A native `save_1` then existed in account storage.
Audible sound and native save/reload still need acceptance testing. Do not stop or
replace a running game without explicit permission.

### D-pad diagnosis and scoped correction

The owner tapped physical Up, Right, Down, Left in that order. A passive
read-only evdev capture recorded the player seat's `ABS_HAT0Y = -1`,
`ABS_HAT0X = 1`, `ABS_HAT0Y = 1`, and `ABS_HAT0X = -1`, each followed by release.
These are the correct Linux hat directions. The capture did not grab or
inject input, restart services, or change any controller mapping.

A native SDL probe used Solarus's actual initialization sequence. It set
`SDL_GAMECONTROLLERCONFIG_FILE` to the installed engine database before
`SDL_Init(SDL_INIT_GAMECONTROLLER)`. All four Korri-seat GUIDs matched the
bundled Linux Xbox 360 entry. That entry bound `dpup:h0.4`, `dpright:h0.8`,
`dpdown:h0.1`, and `dpleft:h0.2`. These are the opposite hat directions.
The default SDL mapping was correct before that database was loaded.

`plugins/solarus/xbox360-dpad.patch` changes only those four bindings to
`dpup:h0.1`, `dpright:h0.2`, `dpdown:h0.4`, and `dpleft:h0.8`.
All button and stick bindings remain unchanged. Quest bytes, quest settings,
account saves, and Korri's controller routing are not part of this correction.
The fix applies to Solarus's Linux Xbox 360 entry; it does not fix OpenGOAL/Jak.

`nix/solarus-controller-check.py` loads the packaged database through native
SDL's GUID lookup. It checks the generic Xbox 360 GUID and all four observed
Korri-seat GUIDs. The original database fails with
`dpup: expected h0.1, got h0.4`. Both architecture checks pass after the patch,
including the existing engine launch, account isolation, and save/reload tests.
Formatting and Python lint checks also pass.

The user's A/B observations match the quest's roll/action and sword/attack
behavior. This correction does not swap the face buttons. Separately, the
engine logs `No such custom entity model: 'ephemeral_effect'` when rolling.
This error comes from `scripts/action/dash_manager.lua:55`. The earlier host
smoke test did not test rolling. It does not establish error-free real-game
compatibility, and the D-pad correction does not repair this quest error.

The owner explicitly permitted stopping and restarting the current quest for
diagnosis. A restart loads a saved checkpoint, not unsaved gameplay progress.
The [signed D-pad update](../deployments/2026-10-03-solarus-dpad-miniv2.md)
records the corrected output, approval, normal close, preserved saves, restart,
and native device verification. Physical acceptance remains required.

The private device stage is `/var/tmp/solarus-yarntown-c78t8ahk`.
It contains `before-library-import/`, `import-summary.json`, `library-import.log`,
`routes.json`, `launch.json`, `running.json`, `sway-tree-visible.json`, and
`yarntown-visible.png`. The host retains the last screenshot in its private
stage. These files are not plugin release assets.
