# ZQuest Classic

`@simonwjackson:zquest-classic` runs unpacked `.qst` files with the native
ZQuest Classic player on Linux x86_64 and aarch64. It does not include the
quest editor, a quest downloader, or automatic game registration.

## Source and integration

The engine pin, dependency pins, and ARM tile-rendering patch come from
Korri's read-only `legacy` branch at
`product/plugins/zquest-classic/packages/zquest-classic/`.
The source is [ZQuestClassic/ZQuestClassic at
882c906b17e35b4105188e6305ae2929aeba30e3](https://github.com/ZQuestClassic/ZQuestClassic/tree/882c906b17e35b4105188e6305ae2929aeba30e3),
from June 18, 2026. This is a development snapshot, not a claim to package
the latest stable release. Quests that require later engine changes can fail.

The system identity `zelda-classic`, title `Zelda Classic Quest`, runner name
`zplayer`, `.qst` discovery extension, and `-standalone` launch mode preserve
legacy's producer. The publisher changes to this repository's existing
`@simonwjackson` namespace. There is no alias for the old publisher.

The source declaration performs no effects. It returns the approved launcher,
the literal quest path, and an account-owned state directory. Core performs the
launch under its existing policy. No Core schema or permission expansion is
required. Unsupported launch overrides and libretro cores are rejected.

Build machines compile the native player. Devices receive prebuilt outputs.
Both architectures use the ZScript interpreter, following the legacy package.
The ARM patch selects upstream's scalar tile renderer instead of x86 SIMD.
This costs performance for script-heavy quests. The package disables the
updater, WebSocket scripting, and native file-dialog dependency. It preserves
upstream audio defaults, unlike legacy's muted MIDI configuration.

## Saves and configuration

The owner selected account-owned storage and content-hash save identity on
2026-10-02. State resides beneath `${input.accountRoot}/zquest-classic`,
following the existing Zelda3 account-storage pattern.

The launcher hashes the complete quest with SHA-256, as Core's file scanner
already does. It passes `sha256:<digest>.sav` as upstream's explicit standalone
save filename. There is one native save slot per quest release per account.

| Native path inside the account directory | Purpose |
|---|---|
| `zc.cfg` and `controls.cfg` | The player writes its native configuration and control schemes. |
| `saves/sha256:<digest>.sav` | The native standalone save for these exact quest bytes. |
| `saves/backup/` | The player keeps its native save backups here. |
| `replays/` and `allegro.log` | Upstream replay and diagnostic output remains account-owned. |
| Shipped resource names such as `assets/`, `modules/`, and `base_config/` | Links to immutable resources in the exact installed package. |

Moving or renaming a quest retains its save. A narrow engine patch makes
standalone mode use the newly selected path when loading an existing save.
Different quests with the same filename get different saves. Updating quest
bytes produces a separate save. Moving an older save to an updated quest is
an explicit user operation and depends on that quest's save compatibility.

The launcher holds a directory lock across native execution. A second session
for the same account fails rather than sharing configuration and saves.
Package updates refresh resource links. The launcher refuses to replace local
files or foreign links at those resource names. It does not replace the
player's native configuration. Edit `zc.cfg` while the player is stopped.
Changing upstream's `save_folder` setting changes where it writes saves.
Upstream starts windowed. A handheld compositor can require `fullscreen = 1`
in the native `[zeldadx]` section. Xvfb does not verify that compositor behavior.

Existing `/storage/saves/zquest-classic` data remains untouched. There is no
fallback read, dual write, or automatic migration from legacy.

Keep companion music files beside the quest as its author specifies. Archives
must be unpacked before discovery. Do not modify a quest while it is running.
Upstream asks whether to upload gameplay replays. The plugin does not consent
for the user. Normal signature and permission checks remain required.

## Build and verify

Run from this repository on a build machine:

```sh
nix build --no-link .#packages.x86_64-linux.korri-plugin-zquest-classic
nix build --no-link .#packages.aarch64-linux.korri-plugin-zquest-classic
nix build --no-link .#checks.x86_64-linux.korri-zquest-classic-plugin
nix build --no-link .#checks.aarch64-linux.korri-zquest-classic-plugin
```

The checks exercise the real manifest, strict launch types, host admission,
and production sandboxed callback. They run the packaged player through Core
on Xvfb, using upstream's default quest rather than retail data. They exercise
keyboard input, native screenshots, in-game save writes, reload after a rename,
separate accounts, changed-release isolation, concurrent-session refusal, and
preservation of local files. They also assert upstream's `auto_scopes.zplay`
script replay against the pinned interpreter. Its Git LFS files are fetched
by hash for tests only and are absent from the plugin closure.
Audio is disabled only in the tests. These checks do not establish audible
output, physical-controller support, all-quest compatibility, or device acceptance.
The check-only GitHub workflow runs both architectures and publishes nothing.

For an interactive run with separate test state:

```sh
nix run .#zquest-classic -- /path/to/quest.qst /path/to/test-state
```

## Publication and installation

The output contains upstream runtime resources, including its default module,
fonts, sounds, and music, plus license notices. It omits the editor binaries
and optional quest/tileset directories whose archive entries are Git LFS
pointers. It does not bundle a selection of community quests. Upstream declares
GPLv3 for the project. Public redistribution of included game-derived assets
requires a separate rights review; a successful build is not that review.

Signed publication and device installation require their existing approvals.
Do not build on a device or bypass publisher trust to install this package.
After publishing the architecture-specific output through an approved signed
cache, use Core's existing exact-package approval flow:

```sh
sudo korri-plugin inspect "$CACHE_URL" "$PACKAGE"
# Review the report, then set APPROVAL to its exact digest.
sudo korri-plugin install "$CACHE_URL" "$PACKAGE" "$APPROVAL"
sudo korri-plugin enable @simonwjackson:zquest-classic
```
