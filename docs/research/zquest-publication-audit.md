# ZQuest Classic publication audit

Date: 2026-10-03. This is a release-preparation audit, not legal clearance.
No engine code, device configuration, or public binary cache was changed.

## Decision

Do not publish the current engine output as a Nintendo-material-free package.
Replace the required audio/font data, remove optional unapproved material, and
resolve the title/ending and old-quest tile dependencies before release. Ship
no community quests until their complete assets and redistribution permissions
are verified. Removing assets from the engine does not clean a user's `.qst`.

An unresolved license is not proof of infringement. The conservative release
rule proposed here is to omit or replace assets whose redistribution rights
have not been established. The game names on fonts alone do not prove their
provenance. Distinguish those cases from metadata explicitly naming Nintendo.

## Evidence inspected

- The exact ARM64 engine archive exported for plugin
  `/nix/store/c58xydd7x02m23s2q9hlc4fsjchvjvi6-korri-plugin`, source revision
  `f21eb779516b2c6a09f3651aef90fe63a394ef6c`. Its receipt names engine
  `/nix/store/6w26ck31vxmbhysvjxznzd8g7ykbx9yq-zquest-classic-unstable-2026-06-18`.
  The archive was restored outside the Nix store for inspection, without
  executing it. It contains **388 files** under `share/zquestclassic`.
- The pinned engine source at
  [882c906b17e35b4105188e6305ae2929aeba30e3](https://github.com/ZQuestClassic/ZQuestClassic/tree/882c906b17e35b4105188e6305ae2929aeba30e3).
- The plugin's [package definition at the deployed revision](https://github.com/simonwjackson/korri-plugins/blob/f21eb779516b2c6a09f3651aef90fe63a394ef6c/plugins/zquest-classic/package.nix).
  Upstream [installs the resource tree](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/packaging/CMakeLists.txt#L158-L177).
  The plugin currently deletes only `quests/` and `tilesets/` from that tree.
- NSF header strings, text metadata within MIDI files, the embedded TTF license,
  and the full text of the packaged music license. Music was not compared
  acoustically with original recordings, and every sound sample was not audited.

All asset paths below are relative to `share/zquestclassic` unless stated otherwise.

## Audio and optional assets

| Files | Evidence | Proposed publication treatment |
|---|---|---|
| `modules/classic/zelda.nsf` | Header names `The Legend of Zelda`, `Konchano`, and `1987 Nintendo`. | Remove from the distribution. Audit or replace fallback MIDI too. |
| `music/Isabelle_Z1.nsf`, `music/Isabelle_Z2.nsf` | Headers name `The Legend of Zelda Remade` with Koji Kondo, and `The Adventure of Link Remade` with Akito Nakatsuka. The accompanying license explicitly defines its music as based on Nintendo's Zelda series. | Remove both rearrangements from the Nintendo-free release. The arranger's grant is not evidence of permission from the underlying composition's rightsholder. |
| `Classic.nsf`, `5thmusic.nsf` | The first has 30 tracks and blank credit fields. The second has 10 tracks and names BigJoe/Aidan_Strickland with 2016. These headers alone establish no redistribution terms or complete composition provenance. | Omit unless separately cleared. Do not label them confirmed Nintendo copies merely from their filenames. |
| `assets/dungeon.mid`, `ending.mid`, `gameover.mid`, `level9.mid`, `overworld.mid`, `title.mid`, `triforce.mid` | All seven are mandatory in `Z_init_sound`. `dungeon.mid` includes `Original tune (c) 1986 by Koji Kondo (Nintendo)`. `gameover.mid` includes a Nintendo copyright credit. Other files have absent or incomplete credit metadata. | Replace the seven-file default set with documented original/licensed compositions or valid silent MIDI files. Do not merely mute playback or remove credit strings. |
| `sfx.dat` | Mandatory loader, signature validation and sample-slot check; see below. This audit did not establish a rights chain for each sample. | Replace the sample collection with cleared sounds, retaining the file structure and slot numbers, unless each existing sample is cleared. Valid silence is an option but loses gameplay cues. |
| `assets/editor/tunes.mid` | Its metadata identifies `The Travels of Link- A Zelda Medley` and names compositions from several Zelda games. | Remove with unnecessary editor resources. |
| `customfonts/example fonts/` | The archived package contains 99 bitmap examples, including files named for Pokemon, Super Mario World, Wario Land, and other commercial games. Each font's origin and rights remain unaudited. | Omit these optional examples. This does not remove the mandatory runtime font collection discussed below. |
| Other editor assets, templates, docs/images, headers and includes | The current install copies editor/development material even though no editor binary is shipped. Not every such file is infringing or necessary. | Prefer an explicit approved runtime-file list. Retain required licenses. Verify dependencies before dropping files rather than assuming each directory is unused. |
| Community quests, including *The Deep* | No community quest is in this engine output. *The Deep* was separately added to the Mini V2 library. Its [author's credits](https://www.purezc.net/index.php?page=quests&id=810) name Nintendo graphics and commercial-game soundtrack sources. | Keep it out of the public starter pack and release images. Do not copy device libraries, saves or private cache contents into a public release. |

### Loader consequences

- The [`sfx.dat` load](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zalleg/zalleg.cpp#L250-L278)
  occurs before the sound-disable branch. A missing file is fatal even with
  `-nosound`. [`src/sfx.h`](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/sfx.h)
  defines the datafile indices; a valid replacement must preserve required
  objects, not just create an empty file.
- [`Z_init_sound`](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zc/zc_sys.cpp#L6105-L6125)
  fails on any missing default MIDI file. Generate playable empty MIDI tracks
  or original compositions instead of deleting these files.
- [`try_zcmusic`](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/music_playback.cpp#L13-L48)
  can select MIDI when external music is missing. Removing an NSF alone does
  not establish that its musical content is gone.
- The arranger's [`music-license.pdf`](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/resources/music/music-license.pdf)
  grants bundling, modification and distribution rights to the musician's
  material with credit. It expressly describes Zelda-based music. That grant
  does not meet the user's separate requirement of no Nintendo material.

## Visual assets, legacy defaults, and embedded data (narrow source audit)

**Verified:** removing `quests/` and `tilesets/` does not remove all visual-content dependencies. `classic_fonts.dat` is mandatory at startup. `title_gfx.dat` supplies player-menu and ending tiles/palettes. `190_tiles.qst` is a runtime fallback for old quests, not merely an editor template. `default.qst` is the strongest removal candidate for this player-only build.

Scope: inspected `/tmp/korri-zquest-baseline`, whose Git HEAD is `882c906b17e35b4105188e6305ae2929aeba30e3`, and local `plugins/zquest-classic/package.nix` (lines 30–45, 82–126). These are static-source findings, not runtime tests or a copyright clearance. No binary resource was decoded or visually attributed. **Provenance remains unresolved** unless separately documented; game names and filenames are audit leads, not proof of copied artwork. Audio and license compliance are outside this section.

### Remove / replace / audit decisions

| Asset or data | Verified dependency | Smallest plausible change; cost or risk |
|---|---|---|
| `resources/modules/classic/default.qst` | `init_tiles`, `init_combos`, and `init_colordata` load this template. Located callers are editor operations. `reset_items` and `reset_wpns` explicitly load it only for `App::zquest`. Editor map-template loading also opens it. See [src/core/qst.cpp:804–866](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/core/qst.cpp#L804-L866), [src/zq/zquest.cpp:3017–3085](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zq/zquest.cpp#L3017-L3085), and [src/zq/zq_class.cpp:290–310](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zq/zq_class.cpp#L290-L310). | **Remove from installed player resources**, then test new saves and representative quest loads. No active player template dependency was found in these call sites. This is not proof about every possible script or future upstream change. It would break editor template operations if an editor were later included. |
| `resources/modules/classic/title_gfx.dat` | `null_quest()` loads its tile and color-set sections, skips the other sections, and does not inspect `loadquest`'s result. `init_NES_mode()` calls it. Player save selection and built-in ending call `init_NES_mode()`. See [src/zc/zc_sys.cpp:620–646](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zc/zc_sys.cpp#L620-L646), [src/zc/title.cpp:285–310](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zc/title.cpp#L285-L310), and [src/zc/ending.cpp:513–518](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zc/ending.cpp#L513-L518). | **Replace**, rather than simply delete. Lowest-code option: author a valid quest-format resource containing cleared tiles/palettes at the expected indices. Alternative: replace the built-in menu/ending drawing and remove this load. Cost: index compatibility and ending coverage need tests. It is not only a startup logo file. Source contains a TODO about embedding it, not evidence that it is currently embedded. |
| `resources/modules/classic/classic_fonts.dat` | `zalleg` fatally rejects missing data, wrong object count, or wrong signature. `initFonts` maps datafile slots into font IDs, including GUI and quest-visible fonts. See [src/zalleg/zalleg.cpp:312–331](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zalleg/zalleg.cpp#L312-L331), [src/core/fonts.cpp:229–285](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/core/fonts.cpp#L229-L285), and [src/fontsdat.h:1–100](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/fontsdat.h#L1-L100). | **Audit each font or replace the collection**. Smallest loader change is none: rebuild a compatible Allegro datafile with cleared font objects at the same indices and valid signature/count. Alternative: replace loading and map every font ID to cleared fonts in code. Cost: glyph coverage, special subscreen symbols, metrics, and quest text layout can change. `fontsdat.h` embeds indices, not glyph pixels. Names such as `FONT_NES` and `FONT_ACTRAISER` alone do not establish provenance. |
| `resources/assets/190_tiles.qst` | `readtiles()` uses it when `Header->data_flags[ZQ_TILES]` is false and `from_init` is false. Failure only traces an error, then returns success. See [src/core/qst_tiles.cpp:51–77](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/core/qst_tiles.cpp#L51-L77) and [src/core/qst.cpp:799–802](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/core/qst.cpp#L799-L802). | **Replace or explicitly drop this legacy compatibility**. Smallest honest removal: reject quests needing absent default tiles, instead of continuing with an error trace. Cost: those quests stop working. A compatible cleared tile replacement preserves loading but changes appearance. Do not describe removal as harmless editor cleanup. |
| `resources/assets/cursor.bmp`, player logo/icon | Cursor absence is fatal; logo has a text fallback; Linux window icon is loaded externally. See [src/zc/zc_sys.cpp:573–598](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zc/zc_sys.cpp#L573-L598), [src/zc/title.cpp:231–248](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zc/title.cpp#L231-L248), and [src/zalleg/zalleg.cpp:132–151](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zalleg/zalleg.cpp#L132-L151). | **Audit or replace** remaining visible branding and cursor. Preserve cursor sheet layout and palette conventions. Removing a custom logo alone still selects `assets/zc/ZC_Logo.png`; remove/replace the fallback too. No attribution established here. |

### Compiled data: separate pixels from compatibility parameters

- **Verified embedded glyph pixels:** [third_party/allegro_legacy/src/font.c:11–40](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/third_party/allegro_legacy/src/font.c#L11-L40) contains the default 8×8 glyph table. [src/core/fonts.cpp:261](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/core/fonts.cpp#L261) selects Allegro's `font`. Its header directs readers to Allegro copyright information; this audit does not independently establish glyph provenance. Review the bundled Allegro license/history before using this as the cleared replacement font. Deleting external `.dat` files cannot remove this table.
- **Verified embedded cursor/image tables:** [third_party/allegro_legacy/src/mouse.c:82–125](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/third_party/allegro_legacy/src/mouse.c#L82-L125) contains default arrow/busy pixels. [third_party/allegro_legacy/cmake/FileList.cmake:19–43](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/third_party/allegro_legacy/cmake/FileList.cmake#L19-L43) lists both font and mouse implementation files. [src/zc/zc_sys.cpp:650–710](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zc/zc_sys.cpp#L650-L710) also contains triangle pixel-mask tables. Audit as compiled visual data, but do not classify generic cursor/geometry data as commercial artwork without evidence. Final binary retention was not checked.
- **Verified compiled item/enemy defaults, not sprite pixel sheets:** [src/defdata.cpp:197–210](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/defdata.cpp#L197-L210) and [src/defdata.cpp:330–338](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/defdata.cpp#L330-L338) define item/enemy parameters, tile references, palettes, animation and behavior values. This file is in [modules/zelda/ZeldaCore.txt:7–18](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/modules/zelda/ZeldaCore.txt#L7-L18). [src/core/qst_guys.cpp:422–437](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/core/qst_guys.cpp#L422-L437) copies defaults into `guysbuf`; the quest reader calls it at [lines 1999–2002](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/core/qst_guys.cpp#L1999-L2002). [src/sprite_data.cpp:7–15](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/sprite_data.cpp#L7-L15) copies tile/animation references from item data, not embedded artwork. **Do not remove these tables as an artwork-cleanup shortcut:** legacy compatibility can break without removing any pixels. Audit expressive names/data separately if publication policy requires it.

### Automatic quest downloads

**No native automatic default-quest download was found in the inspected player paths.** Quest fetching in [src/zc/saves.cpp:1720–1728](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zc/saves.cpp#L1720-L1728) and replay path resolution in [src/zc/zelda.cpp:3914–3942](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zc/zelda.cpp#L3914-L3942) are behind `__EMSCRIPTEN__`. [scripts/package.py:245–251](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/scripts/package.py#L245-L251) describes web-only lazy downloading. This is not a network trace or a whole-dependency proof. Keep any later web build separate from the native publication decision; a resource absent from a web archive may still be supplied remotely.

### First implementation step and unresolved checks

Start with `plugins/zquest-classic/package.nix`: extend player-resource exclusions for the editor template, then provide cleared replacements for mandatory resources. Do not publish on the basis of exclusions alone. Test missing-template startup, save selection, standalone quest startup, an old quest without tiles, and the built-in ending. The four named binary resources exist locally as real byte files, but their internal artwork, font ownership, and clearance were not established. A cleared tile/font inventory and a final output/binary inventory remain required. This source audit does not claim an exhaustive inventory of embedded third-party visual data.

## Other compiled content and material to retain

The player's [built-in ending](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/zc/ending.cpp#L42-L100)
contains the Nintendo staff-credit sequence and original-game ending text.
It also uses Hyrule text and quest tile indices during the ending.
Replace the stock presentation with neutral content for this release, and test
it. Do not confuse this with deleting license notices or ownership attribution
for retained code. Generic gameplay logic and numeric compatibility IDs are
not automatically copied artwork and do not need wholesale removal.

There is also material with explicit permissions that need not be discarded:

| Material | Basis and obligations |
|---|---|
| `assets/zc/ZC_Forever_HD.mp3` and the ZC logos/icons | Packaged [LICENSE.txt](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/resources/assets/zc/LICENSE.txt) permits use related to ZQuest, including distribution with ZQuest games. [CREDITS.txt](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/resources/assets/zc/CREDITS.txt) identifies Eduardc/Connor for art and Beatscribe for music. Retain terms and credits. This is not an unrestricted CC0 grant. |
| `ProggyVector-Regular.ttf` | Embedded name-table license covers ProggyVector/Hack work under MIT, DejaVu work under public domain, and Bitstream Vera under its font license. Preserve the applicable notices and naming conditions. It is a possible source for replacement fonts, not an already-generated compatible `.dat`. |
| FreePats software-MIDI instruments | The plugin uses this separate sound bank and copies its `COPYING` and `README`; see [audio.nix](https://github.com/simonwjackson/korri-plugins/blob/f21eb779516b2c6a09f3651aef90fe63a394ef6c/plugins/zquest-classic/audio.nix). Do not confuse synthesizer instruments with the songs being played. Retain and satisfy its license, separately from the song audit. |
| Engine and third-party libraries | Preserve licenses and notices and provide the required source. The engine's GPL label alone does not clear every media asset in the upstream repository. |

## Release work and acceptance gates

1. Produce a separate cleaned engine output. Use an approved runtime-file list
   rather than copying the complete upstream resource tree. A launcher that
   hides files is insufficient: it still references the original engine store
   output, which a recursive Nix export includes.
2. Generate replacement sound, MIDI, font and tile resources from documented
   sources. Preserve required binary structures and IDs. Never copy an old
   template and assume an empty map removed its embedded graphics or music.
3. Remove the editor-only `default.qst` after verifying player startup without
   it. Replace the default-template test fixture with a rights-cleared quest.
   Resolve old quests requiring `190_tiles.qst`: provide a cleared replacement,
   or explicitly reject that unsupported case. Do not silently return broken
   graphics as a successful load.
4. Inspect the final x86_64 and aarch64 outputs, including resource containers,
   embedded binary data and recursive runtime dependencies. Check test fixtures,
   screenshots, source archives and downloadable release artifacts separately.
   A search for the word `Nintendo` is not a clearance test.
5. Run sound-enabled startup, native save/reload, controller, text/glyph, menu,
   legacy-tile failure and ending tests against the cleaned output. Then verify
   the new private signed build on the Mini V2. Do not stop an active game
   without the owner's explicit approval.
6. Provide the corresponding source for the exact released binaries, including
   patches, resource-generation sources and necessary build/install scripts.
   Keep GPL and dependency notices, replacement-asset licenses, authorship and
   modification records. [GPLv3 sections 1, 5 and 6](https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/LICENSE#L134-L299)
   define the source and distribution requirements. Publishing a wrapper repo
   or linking only to upstream's default branch is not the whole source plan.
   Do not repackage removed commercial assets into a public source archive.
7. Publish only the audited package and closure, not the existing private cache.
   Retain a per-asset origin/license record for what is shipped. Resolve unclear
   permissions with the relevant rightsholder or qualified legal review before
   describing the package as cleared.

Costs: replacement audio changes the sound; replacement fonts and tiles change
appearance and can affect text layout. Dropping legacy default tiles reduces
quest compatibility. A quest-free plugin provides no starter game. None of
these changes clears third-party quests or proves that the entire project is
free of legal risk. This audit establishes a concrete cleanup scope, not
completion of that scope.
