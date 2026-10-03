# Solarus 2.1.4 asset audit

The built Solarus plugin contains no identified Nintendo game assets.
Nintendo branding does appear in upstream documentation images, which are not
in either audited runtime closure. These images are candidates to omit from
an optional documentation or source bundle, not reasons to change the engine.
Yarntown remains a separate, mixed-license quest and is not approved for
redistribution by this audit.

Checked on 2026-10-03. This is an engineering inventory and provenance check,
not legal clearance. No asset, license, attribution, quest, or device state
was changed. No release artifact was published. The owner confirmed the
corrected D-pad and plans to use gamescope for window focus; that integration
is outside the remaining Solarus work.

## Actual runtime outputs

The audit queried the already-built outputs with
`nix path-info --recursive --json` and traversed their actual files. It did
not substitute an upstream source tree or a license declaration for the
published binary contents.

| Target | Plugin output | Runtime store paths |
|---|---|---|
| x86_64 Linux | `/nix/store/krfwvlfz28gfvacfc2m3831p0k74xm5m-korri-plugin` | 316 |
| ARM64 Linux | `/nix/store/1nqkm6qm41phg6jxi6a2b5dgfwq2k6d5-korri-plugin` | 318 |

Each plugin output contains only `manifest.json` and `plugin.ts`. The native
engine output contains `bin/solarus-run`, GPL and licensing notices, and its
manual page. The engine library output contains the shared library and its
symlinks, plus `share/solarus/gamecontrollerdb.txt`. There are no loose images,
fonts, sounds, music files, ROMs, or quests in these direct outputs.

Neither runtime closure contains the upstream engine source tree or Yarntown.
The extension-based media inventory found 419 image/font candidates per
architecture. All belong to six general dependencies, not Solarus quests:

| Dependency | Candidates | File categories observed |
|---|---|---|
| Python | 14 | IDLE and Python icons |
| GTK 4 | 10 | GTK demo/program icons |
| GTK 3 | 24 | GTK demo/program icons |
| Zenity | 369 | Zenity icon and localized help screenshots |
| DejaVu | 1 | `DejaVuSans.ttf` |
| libsamplerate | 1 | `share/doc/libsamplerate/SRC.png` |

No candidate path contains `nintendo`, `zelda`, `alttp`, `mario`, `metroid`,
or `yarntown`. That name check is supporting evidence, not proof of ownership.
It is not a pixel-by-pixel authorship audit of every dependency. The audit also
read the engine's resource-loading and install code. Fonts, sprites, sounds,
and window icons load from the quest; the install rule ships the controller
database, not a Zelda resource pack.

Nintendo controller names in the database are hardware compatibility entries,
not copied game graphics or audio. Removing them would reduce controller
support without addressing the asset question. The LGPL-attributed
`snes_spc` code provides a music decoder, not a bundled Nintendo soundtrack.

## Source documentation candidates

The exact fetched Solarus source is
`/nix/store/gkjwl6vmnihipdzfh5rqfq9pm61wvpv1-source`, pinned to `v2.1.4` by
`plugins/solarus/package.nix`. These findings concern that source, not the
runtime outputs above.

| Upstream path | Observed content | Removal/replacement scope |
|---|---|---|
| `doc/docs/tutorials/distribution/nintendo-switch-logo.svg` | Nintendo Switch logo, explicitly labeled by the adjacent documentation. | Omit or replace with plain platform text if bundling these docs. |
| `doc/docs/tutorials/getting-started/images/introduction/snes-crossed.png` | Super Nintendo wordmark and emblem with a line across them, verified by viewing the image. | Omit or replace with a text explanation if bundling these docs. |
| `doc/docs/tutorials/getting-started/images/introduction/solarus-launcher.png` | Launcher screenshot with multiple Zelda covers and Link artwork, verified by viewing the image. | Omit or replace with a screenshot of independently licensed quests if bundling these docs. |

These three files are absent from both runtime closures. None is necessary to
compile or run the engine. No optional source or documentation archive was
built in this audit. If producing one later, exclude the documentation images
while retaining the build sources, patches, license notices, and other files
needed to reproduce the modified engine. The source documentation's other
images were not exhaustively reviewed; this is a concrete candidate list,
not a claim that these are its only third-party marks.

The separate `images/creating-a-quest/solarus-launcher.png` screenshot shows
Children of Solarus and a description stating it uses free assets. That is
not evidence of a copied Nintendo image.

## Engine test assets and our fixture

Upstream `license-details.md` attributes the engine's testing quest to the
Solarus Free Resource Pack. The exact testing-quest `license.txt` declares
GPL v3 scripts, mostly CC BY-SA 4.0 data, and some public-domain data. Its
resource metadata names artists rather than Nintendo. Examples include
Diarandor's sounds and hero graphics, Jeti's `enter_command.ttf`, and the
public-domain `8_bit.png` font. These are verified upstream attributions,
not independent proof of each creator's authorship.

The official source documentation explicitly distinguishes the Free Resource
Pack from the separate Zelda packs. The Zelda-pack license acknowledges that
most graphics, sounds, and names belong to Nintendo. These packs are not
inputs to the Solarus plugin. Do not import them to supply a bundled demo.

Korri's `nix/solarus-quest/` test fixture contains only `main.lua`,
`project_db.dat`, and `quest.dat`. It exercises native save/reload without
graphics, fonts, sounds, or retail game assets. The Solarus CI workflow builds
that check and does not download Yarntown.

## Yarntown v1.0.6, separately

The audit opened the original archive directly with Python `zipfile`.
Its SHA-256 is
`1337d1074dac824de876924c5b0c043ad62d1bcc2fb4851d8b389af02dd04c5a`.
It contains 102 PNGs, one TTF, and 153 OGG files. There is no separately named
license/credits/README file in the archive, but `project_db.dat` does contain
217 per-file or directory attribution records. Missing standalone licensing
files must not be mistaken for missing all attribution.

No record names Nintendo as an author. Examples read directly from that exact
archive include:

| Quest path | Declared author | Declared license |
|---|---|---|
| `fonts/8_bit.png` | usr_share, Christopho | Public domain |
| `fonts/enter_command.ttf` | Jeti | CC BY 4.0 |
| `sounds/bomb.ogg`, `sounds/boomerang.ogg`, `sounds/heart.ogg` | Diarandor | CC BY-SA 4.0 |
| `sprites/hud/rupee_icon.png` | Olivier Cléro | CC BY-SA 4.0 |
| `tilesets/oceanset_outside.tiles.png` | Max Mraz | CC BY-SA 4.0 |
| `sprites/menus/splash_screens/moths.dat` | Max Mraz | All Rights Reserved |

Names such as `rupee`, `hookshot`, and `sword` do not establish Nintendo copying.
Seven suspiciously named sound files were compared with their same-named files
in the official ALttP pack: `sword1`, `sword2`, `heart`, `picked_item`, `jump`,
`bomb`, and `boomerang`. None has identical archive bytes or identical decoded
PCM samples. Native libsndfile decoded both sides; sample counts and rates
also differ in these comparisons. This excludes exact copies of those specific
pack files, not modified copies or every other possible source. Five of these
quest files have explicit Diarandor attribution; `sword1` and `sword2` lack
individual attribution records in the inspected database.

No Nintendo-copied quest asset was established. There is therefore no confirmed
Nintendo-removal list for Yarntown. An exhaustive originality audit would need
more provenance than names, metadata, and seven comparisons.

**Separate publication concern, high importance:** the official Yarntown page
lists GPL v3, CC BY-SA 4.0, and Proprietary components. The exact archive has
an All Rights Reserved record and no per-file credits for its four music
tracks. The page describes a Bloodborne homage; that is not permission to
redistribute Bloodborne media. PlayStation identifies Sony Interactive
Entertainment as Bloodborne's publisher. This is not a Nintendo attribution. Removing a Nintendo logo would not settle it.

The recommended release remains quest-free. Its cost is that users supply
their own quests; it does not provide a bundled playable demo. Redistributing
Yarntown or making a sanitized fork requires a separate permissions/provenance
check. No part of this audit authorizes deleting the owner's installed quest
or save, replacing audio, or changing gameplay.

## Sources and reproducibility

Primary sources read directly:

- [Solarus v2.1.4 licensing details](https://gitlab.com/solarus-games/solarus/-/blob/v2.1.4/license-details.md).
- [Exact testing-quest license](https://gitlab.com/solarus-games/solarus/-/blob/v2.1.4/tests/testing_quest/license.txt) and its `data/project_db.dat`.
- [Engine install rules](https://gitlab.com/solarus-games/solarus/-/blob/v2.1.4/cmake/AddInstallTargets.cmake), `src/core/FontResource.cpp`, and `src/core/MainLoop.cpp`.
- [Nintendo Switch documentation](https://gitlab.com/solarus-games/solarus/-/blob/v2.1.4/doc/docs/tutorials/distribution/nintendo-switch.md), its SVG, and the two PNGs listed above, inspected from the exact local source.
- [Resource-pack distinction](https://gitlab.com/solarus-games/solarus/-/blob/v2.1.4/doc/docs/resources/resource-packs.md).
- [ALttP pack license](https://gitlab.com/solarus-games/resource-packs/solarus-alttp-pack/-/blob/dev/license.txt) and seven `data/sounds/*.ogg` files, fetched from its first-party GitLab repository API. This branch is mutable; the comparison evidence retains each downloaded file and hash.
- [Official Yarntown page](https://www.solarus-games.org/games/yarntown/), fetched in full.
- [Official Bloodborne page](https://www.playstation.com/en-us/games/bloodborne/), fetched in full, naming Sony Interactive Entertainment as publisher.
- [Original Yarntown artifact](https://gitlab.com/maxmraz/yarntown/-/jobs/artifacts/v1.0.6/raw/yarntown-v1.0.6.solarus?job=quest-package), identified by the SHA-256 above, with `project_db.dat` read from that archive.
- Local `plugins/solarus/`, `nix/solarus-quest/`, and `.github/workflows/solarus.yml`.

Private evidence is in `/tmp/solarus-asset-audit/`. The two architecture
`*-inventory.json` files retain full runtime paths and media candidates.
`yarntown-project_db.dat` and `yarntown-attribution-summary.json` retain the
actual quest metadata. `alttp-decoded-comparisons.json` retains hashes, audio
formats, decoded hashes, and comparison URLs. The original quest and copied
comparison media remain outside Git, Nix outputs, CI assets, and releases.

The local Nix-shebang scripts are `/tmp/solarus-asset-inventory.py`,
`/tmp/solarus-compare-alttp-assets.py`,
`/tmp/solarus-decode-asset-comparison.py`, and
`/tmp/solarus-asset-attribution-summary.py`. They query already-built paths and
public source files. They neither evaluate device flakes nor build on devices.
