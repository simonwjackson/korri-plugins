# Pagan Invaders cleanup assessment

Checked 2026-10-16 UTC. **Technically feasible as a substantial replacement project, not a one-MIDI cleanup. Publication is not cleared.** The conservative no-contact route replaces 12 nonempty sound samples, replaces or blanks 127 nonblank tiles, replaces the Venrob-derived intro library, removes the Zelda MIDI, and removes inherited template content. It also needs a reproducible script rebuild, cleared engine font/SFX dependencies, and gameplay regression tests. These are development costs, not just attribution work. No reliable person-day estimate is established.

**Inferred feasibility:** editable source and index-addressed media make this possible in principle. **Unresolved:** a cleaned, playable result has not been built or tested. Retaining rather than replacing an unresolved asset requires published evidence for that asset; a filename or absence of a Nintendo match is not that evidence. This assessment is not legal clearance.

No author or third party was contacted. No quest bytes, MIDI, PCM, tile images, or downloaded pages enter Git. Only this report is committed. No starter-pack, Tiny5 worktree, device, running game, upload, push, or deployment action occurred. No scrub, including a one-item proof, was performed.

## Identity and method

**Verified:** the quest was downloaded again from the [pinned creator raw URL][quest]. It is 5,247,617 bytes, SHA-256 `53ececcef40eeba2b5f275c309e1a8aa3809a5fe0047920391d9bfe8fb74b690`. This matches the earlier PureZC 742 receipt; this pass did not re-download PureZC's quest ZIP. The creator's [pinned tree][tree] has 25 files: three root files and 22 quest revisions. The root [LICENSE][license] is AGPLv3. This is a project-level grant, not the engine's license being applied to someone else's quest.

The existing `nix/zquest-midi-proof.py` loader and pinned `zquest-data` revision `a52b5d19cb73439137ef281110c8831774000c5e` were reused. No replacement QST decoder or encoder was written. The reader's native extension was built privately on this x86 build host, not on a target device.

Three narrow, private reader adapters were necessary:

- `FFSC` v18 has a two-byte ZASM metadata version **before** its size. The unadapted reader stops after 21 sections and misses `FFSC`, `SFX`, `DROP`, and `FAVS`. It reports no parsing exception. This is not evidence that those sections are absent.
- `ITEM` v45's reader skip is two words too long per item. The native producer/consumer has 14 words after `hxofs`/`hyofs`, not 16. The unadapted reader overruns by 2,048 bytes across 256 items.
- `INIT` v20's reader dictionary overwrites five earlier byte-sized fields with later word-sized fields. The adapter retains the five legacy bytes and the later six-word block in native order. This resolves the five-byte consumption deficit.

These changes live in private `inventory.py`, not in the pinned reader or repository tools. The remaining unsupported sections were read privately using the pinned engine's native layouts. Grounding is [the engine's `src/core/qst_*.cpp` readers][native], especially `qst_ffscript.cpp`, `qst_sfx.cpp`, `qst_items.cpp`, `qst_initdata.cpp`, and `qst_subscreen.cpp`; counts come from [`base/general.h`][counts]. No record layout was invented. Prose section names omit trailing spaces in native four-byte section IDs.

**Verified structural coverage:** all 25 section extents are contiguous from payload offset 31 through byte 17,794,839. The adapted reader consumes its 15 supported sections exactly. The private supplement consumes the other ten exactly. The inventory below concerns decoded data, not screenshots, audio listening, or filename-only ZIP inspection. Exact consumption is a format check, not ownership evidence or proof of every runtime reference.

## Component classification and counts

The following **13 audit groups** are the counting unit: **2 author-attributed/AGPL groups, 3 identifiable third-party groups, and 8 unresolved or mixed groups**. They are not 13 independent copyrighted works. Ownership of the two author-attributed groups is **inferred**, not independently proved. There are **zero independently cleared media works** from this pass. A third-party classification identifies origin; it does not imply a redistribution license was found.

| Group | Inventory | Classification and evidence |
|---|---|---|
| A1 | ZoriaRPG gameplay code in `Invaders.zh`, excluding identified imports and the credited library | **Inferred author-owned under AGPLv3.** Creator repository, source header naming ZoriaRPG, and detailed development history are the evidence. The published grant itself is **verified**. |
| A2 | Original intro/menu/result wording and game-specific title/HUD text | **Inferred author-owned under AGPLv3.** Appears in that source and game-specific quest edits. No separate author declaration for each sentence exists. |
| T1 | One embedded MIDI, slot 0 | **Identifiable third-party lead, verified embedded title:** `The Legend of Zelda A Link to the P`. **Inferred** Nintendo composition; sequence/arranger owner **unresolved**. Remove regardless of whether it plays. |
| T2 | Credited `Credits.zh V1.00`, adapted as namespace `crawl` | **Verified third-party attribution:** Venrob. Public successor source identifies Emily. Exact V1.00 permission remains **unresolved**; see below. |
| T3 | `std.zh`, `bitmap.zh`, transitive helpers, compiler-generated initialization | **Verified external engine/toolchain provenance.** Historical engine repository carries GPLv3. Exact Alpha 63 include closure and reproduction of this quest remain **unresolved**. Not artwork licensed by the quest creator. |
| U1 | 12 nonempty embedded PCM samples | **Unresolved ownership.** Custom names are not authorship statements. No embedded credit or asset license was found. None matches the inspected default collections byte-for-byte. |
| U2 | 127 nonblank 4-bit tiles, including sprites | **Unresolved ownership.** Two reference byte matches identify shared bytes, not owners or clearance. All other tiles remain unresolved too. |
| U3 | 63 combos, 8,192 aliases, two maps of 136 screens, door definitions | **Unresolved/mixed.** Game-specific edits coexist with inherited template records. Preserve mechanics and indices; do not treat numeric compatibility data as copied pixel artwork. |
| U4 | 6,701 color sets, 512 palette names, zero cycle records | **Unresolved/mixed.** Numerous Zelda-labelled palettes and 6,302 same-index color-set matches to a historical default. Neither names nor matches establish ownership of a palette. |
| U5 | Nine referenced engine font IDs; no embedded font collection | **Unresolved original glyph provenance.** The quest stores selectors, not those font pixels. Use documented replacements in the cleaned engine, not original `classic_fonts.dat`. |
| U6 | Eight populated legacy subscreens, including template text | **Unresolved/mixed.** 544 objects; includes unused `TRIFORCE` labels and a modified score HUD. Full details below. |
| U7 | Item/enemy/weapon names and definitions, hero sprite references, icons, miscellaneous tables | **Unresolved/mixed.** Extensive inherited franchise names and stale bytes after NULs. Numeric definitions and tile references are not themselves embedded sprite sheets. |
| U8 | Thirteen nonempty compiled scripts plus embedded source buffer | **Unresolved mixed build provenance.** Named source is available, but it differs from repository source and includes T2/T3. No compiler reproduction or instruction-to-contributor source map was made. |

The 47 zero-length sound records and 78,119 blank tile records contain no audible/pixel payload to attribute. They are structural inventory, not 47 or 78,119 cleared works. They are excluded from the group count.

## Embedded MIDI and sound inventory

### MIDI

**Verified:** 252 MIDI slots are represented; only slot 0 is populated. Its native title is `The Legend of Zelda A Link to the P`, volume 144, looping enabled, divisions 1,024. The exported SMF is 1,444 bytes, SHA-256 `bcf82e9649d84e84f9ef49d781c91613a324b9009fe1632ade197a00c894fbb2`.

All text-bearing MIDI metadata is `Piano` (track name) and `SmartMusic SoftSynth 1` (device name). No copyright, composer, sequencer, or other credit text was found in its MIDI events. Its other metadata comprises timing, tempo, key/time signatures, and end-of-track events. The Zelda title belongs to the quest's enclosing MIDI record, not a newly discovered composer credit.

**Inferred:** the title identifies an A Link to the Past composition lead owned by Nintendo. Exact composition, arranger, and sequencer are **unresolved**; it was not identified by listening. Nintendo's name or title is a problem-finding lead, not a license. Strip the entire record while preserving all other slot identities. Merely renaming it or selecting a different track is insufficient.

### Samples

**Verified:** `SFX` v7 contains 59 populated records: 12 with PCM and 47 with zero frames. PCM totals 3,447,814 bytes. Slots are **one-based** here, as in native `Audio->PlaySound`.

Every nonempty record is listed below. Each remains **unresolved**. The risk column is inferred from script calls and normal engine use, not a gameplay test. Durations are sample frames divided by sample rate.

| Slot | Stored name | PCM bytes | Seconds | Required treatment and risk |
|---|---|---:|---:|---|
| 1 | `paganinv_enemy_shoot` | 36,684 | 0.208 | Replace enemy-shot cue; silence loses warning. |
| 2 | `paganinv_playershoot` | 72,220 | 0.409 | Replace player-shot/menu cue; silence loses feedback. |
| 3 | `paganinv_enemy_step` | 5,492 | 0.029 | Replace step/menu cue; audible game rhythm changes. |
| 4 | `paganinv_startlvl` | 94,772 | 0.537 | Replace round-start cue. |
| 5 | `destroysaucer` | 256,000 | 1.451 | Replace UFO-destruction/menu cue. |
| 6 | `paganinv_enemy_die` | 41,268 | 0.234 | Replace destruction cue; retain enemy death configuration. |
| 7 | `addlife` | 37,706 | 0.428 | Replace extra-life cue. |
| 8 | `paganinv_saucer` | 66,916 | 0.379 | Replace UFO/menu cue; preserve start/stop behavior. |
| 9 | `gameover` | 219,044 | 1.141 | Replace result cue. |
| 12 | `win` | 192,512 | 1.091 | Replace round-256 win cue. |
| 13 | `slg` | 2,402,112 | 13.617 | Replace intro recording/tune, or use valid silence. Content/composition/recording owner unknown. |
| 19 | `playerhurt` | 23,088 | 0.524 | Replace engine player-damage cue; loss of feedback matters. |

Slots `14–18`, `20–61` are all named `silent` and have zero frames. Keep or replace with **valid** silent records at the same indices; do not assume every engine accepts zero-length samples. Slots `10` and `11` are absent. The native old-format loader supplies absent stock slots below `Z35` from the engine's `sfx.dat`. Slots `62–255` are absent and outside that stock fallback range. The presence mask's spare bit is not another sample.

**Verified comparison:** none of the 12 PCM payloads matches any sample payload in either inspected engine default collection:

- Current pinned `resources/sfx.dat`, SHA-256 `ddd7595fb1320cf758896d75e48cef14e331336601e215a99d54427d741040f7`.
- Historical `output/modules/default/default/default_sfx.dat`, SHA-256 `11128802b3e864546becdc31046bc654cd66dd4a87a5ac8869495aca1303723d`.

The existing reader's Allegro packed-stream implementation was reused for these collections. This tests exact PCM equality, not resampling, composition, or perceptual similarity. It supplies **no positive ownership finding**. `slg` is not cleared because it lacks a Zelda title. The two absent stock slots must remain on the cleaned engine's documented replacement sounds, or receive cleared in-quest replacements. No external WAV, music file, or media dependency is declared in the three root repository files; all decoded DMap enhanced-music filename buffers are zero.

## Graphics, palettes, maps, and fonts

### Tiles and sprite references

**Verified:** 78,246 tile records, all 127 nonblank records in format 1 (4-bit). Blank records must retain their indices. With ZC's 260-tiles-per-page convention, nonblank data occupies only pages 0, 100, and 300.

| Page | Exact nonblank tile IDs | Count | Origin / treatment |
|---|---|---:|---|
| 0 | `0–4` | 5 | **Unresolved.** Tiles 2 and 3 equal reference tiles 2 and 3. Replace or blank only after checking their uses. |
| 100 | `26180–26188`, `26190–26198` | 18 | **Unresolved.** No grant specific to these pixels found. Blank if proved unused; otherwise replace. |
| 300 | `78000–78007`, `78020–78027`, `78040–78047`, `78060–78075`, `78080–78081`, `78100–78102`, `78107`, `78120–78121`, `78140–78155`, `78160–78167`, `78180–78187`, `78190–78191`, `78200–78207`, `78214–78215`, `78220–78227`, `78233–78235`, `78245` | 104 | **Unresolved.** Game sprite bank; replace used pixels at the same IDs and blank any proven unused pixels. |

The reference is the pinned reader's `test_data/1st.qst`, SHA-256 `69741eda8fe7e5d09c575304cfa78c3cf3340d6b0d566a88baebfdeabf08f8eb`. The 2020 engine default quest has **zero** nonblank tile-byte matches to Pagan. That default is not the same reference as `1st.qst`. Neither result clears any unmatched tile or proves that the two matches are Nintendo artwork.

**Verified source references:** alien animation starts at `78000`, `78020`, `78040`; player animation starts at `78060`; shields draw a 3×2 tile block starting at `78213`, CSet 11. `78213` is blank, but `78214`, `78215`, `78233–78235` supply the other shield cells. Tile 5 is explicitly a blank. The source also uses sprite definitions for missiles and splat effects. Do not replace collision silhouettes casually: shields use rendered bitmap/GetPixel collision. Blank shields or sprites can change gameplay, not just appearance.

Combos `0–3` reference blank tile `10440`; combo `41` references tile `78140` with eight animation frames; combos `56–58` and `60–62` reference the shield block. Preserve walk masks and animation parameters. Combos and sprite definitions contain indices, not another hidden pixel collection. Numeric zero does not always mean “unused”: some template combo records point to tile 0.

**Verified template residue:** both maps contain 136 stored screens, including template screens with combo IDs beyond the quest's 63 stored combos. This is not a claim those screens are reached. Reachability remains **unresolved**. Do not delete or renumber maps, combos, NPCs, weapons, or FFC/script bindings based only on this inventory.

### Palettes

**Verified:** `CSET` v4 has 321,648 color bytes = 6,701 sets of 16 RGB entries; 512 fixed palette-name fields; zero cycling entries. Nonempty names are at indices `0–25` and `33–38`. Names `0–11` are `Zelda1 Overworld`, `Zelda1 Level-1` through `Zelda1 Level-9`, `Zelda1 Caves`, and `Zelda1Passageway`. Others include `Night Overworld`, `CSet 0/1/5`, `Caves 2`, `NQ1: …`, `ZCO:…`, and six `Z1: …` names. Full strings and color bytes remain in private decoded evidence.

The historical default quest has 6,302 equal same-index color sets and 399 different ones. Blank/default entries are included in that count; it is not 6,302 separately copied expressive palettes. Palette names are not identical as a whole.

**Unresolved:** who authored each actual palette and whether its selection/arrangement requires permission. For a conservative release, clear unused palette slots and names without shifting them; supply a documented game palette for used slots, including script-indexed colors. Renaming alone removes no color data. Cost: contrast and shield/player visibility need regression checks. Do not label common RGB values Nintendo property merely because a name contains Zelda.

### Fonts and text presentation

**Verified:** no standalone font section or font file is distributed in this quest/repository. Original engine font glyphs are a dependency, not embedded QST font bytes. The decoded tables and script source reference these nine IDs:

| ID | Native selector/name | Where observed | Original glyph provenance |
|---:|---|---|---|
| 0 | `FONT_Z1` / Zelda NES | Both message strings and inherited subscreens | **Unresolved**, explicit franchise-name lead. |
| 1 | `FONT_Z3` / Link to the Past | Scripted GAME OVER / YOU WIN | **Unresolved**, explicit franchise-name lead. |
| 29 | Amiga (`font_adosfont`) | Modified passive HUD text/counters | **Unresolved**. |
| 30 | `FONT_ALLEGRO` | Crawl's default font | **Unresolved** for the selected collection's pixels. |
| 34 | `FONT_AQUARIUS` | UFO score | **Unresolved**. |
| 49 | `FONT_GAIA` | SELECT SKILL | **Unresolved**. |
| 58 | `FONT_PET` | Intro narrative | **Unresolved**. |
| 61 | `FONT_SCIFI` | Intro header and difficulty choices | **Unresolved**. |
| 63 | `FONT_SINQL` | Intro narrative | **Unresolved**. |

Names/IDs were checked against historical `std_constants.zh` and the current engine's [`fonts.cpp`][fonts]. The 2020 reference is commit `a0eafc331de0ef24401c9a2fb1c059f526c1a428` of `ZoriaRPG/zc255_devhistory`, identified as Alpha 64, **not** proof of the quest's exact Alpha 63 build environment. Its header/source dependency is a near-contemporary reference only.

**Verified packaging distinction:** local `main` already generates replacement fonts from the explicitly licensed ProggyVector TTF through `plugins/zquest-classic/public-assets.nix` / `.py`. This pass only read that configuration. Do not restore original `classic_fonts.dat` to reproduce the old appearance. **Inferred:** using the cleaned collection avoids redistributing those original glyphs; actual nine-ID rendering and metrics still need testing with the eventual cleaned quest. Tiles remain a separate graphics audit even when engine fonts are replaced.

## Strings, title, credits, and other stored tables

**Verified game text:** the embedded source contains these eleven visible strings (padding omitted for the two results):

- `GAME OVER`; `YOU WIN`.
- `It is the year 5780...`; `...the spring time in the month of Nisan`.
- `The PAGANS are INVADING!!`; `You must RESCUE HUMANITY from their`; `IDOLATRY, and their misguided beliefs!`.
- `SELECT SKILL`; `NORMAL`; `EXPERT`; `MASSOCHIST`.

Their authorship is **inferred** from the creator source, under its AGPL grant. This is an opening narrative, not an author-credit roll. Names used to resolve script bindings are also strings but not visible narrative. The `Credits.zh` heading is a source attribution, not an in-game credits screen.

**Verified header:** visible title `Pagan Invaders Gamma 2`, visible author `ZoriaRPG`, version `0.6.0`. The fixed buffers also retain post-NUL text: title suffix `ta/test thingy...` and author suffix `Phantom Menace, BigJoe, Riverman, 4matsy` with a leading space. These are present distributed bytes. Their origin and continuing relevance are **unresolved**. Preserve genuine retained-code notices in the release's notices file; do not erase attribution under the pretext of removing template garbage. Also remove the stale build-machine module path when preparing a release; it is not a required external dependency.

**Verified `STR`:** exactly two records: slot 0 `(none)` and slot 1 `This is a basic string.` followed by spaces. Slot 1 references tile 237, which is blank; both select font 0 and SFX 18. This is not a large hidden dialogue/credits collection.

**Verified `SUBS`:** 128 stored groups, only slots `0–7` have objects; 544 objects total. Each has the following text objects. Duplicate words are listed per group, not collapsed out of the inventory.

| Slot / name | Objects | Stored text | Classification / action |
|---|---:|---|---|
| 0 `Active (Alt, B)` | 75 | `TRIFORCE`, `TIME-` | **Unresolved inherited template.** Blank unused group preserving slot. |
| 1 `Active (Alt, B+A)` | 75 | `TRIFORCE`, `TIME-` | Same. |
| 2 `Passive (Alt, B)` | 67 | `-LIFE-`, `-MAGIC-`, `B`, `A` | Same. |
| 3 `Passive (Alt, B+A)` | 64 | `-LIFE-`, `-MAGIC-`, `B`, `A` | Same. |
| 4 `Active (New, B)` | 67 | `TRIFORCE`, `TIME-` | Same; active subscreen is disabled by the game script, not removed from the file. |
| 5 `Active (New, B+A)` | 68 | `TRIFORCE`, `TIME-` | Same. |
| 6 `Passive (New, B)` | 56 | `-LIFE-`, `-SCORE-`, `-HIG\|H SCORE-`, `R` | **Mixed/inferred game edit.** Keep/rebuild the score HUD, replace its font dependency; do not blank the functional HUD. |
| 7 `Passive (New, B+A)` | 72 | `B`, `A`, `-LIFE-`, `-MAGIC-` | **Unresolved inherited template.** Blank if unused. |

The backslash above only escapes Markdown's pipe; the stored text is `-HIG|H SCORE-`. The table lists the full group set, not only what a screenshot would show. Template minitile/frame objects point to many blank or out-of-range tile IDs; a reference is not an additional embedded image. Slot 6 is the modified passive score layout; DMap passive selector 2 counts passive groups, not raw group slot 2.

**Verified other text-bearing tables:**

- `ITEM`: 256 names and definitions. Includes `Triforce (Fragment)`, `Triforce (Whole)`, `Din's Fire`, `Farore's Wind`, `Nayru's Love`, `Lens of Truth`, and post-NUL suffixes.
- `GUY`: 512 names/definitions. Includes `Zelda`, `Ganon`, many Zelda enemy names, and game-specific `Invader Swarmleader` (38), `Invader UFO` (39), and `Invader (1)` through `(4)` (180–183). Names 39 and 181–183 retain post-NUL template suffixes.
- `WPN`: 256 names/definitions. Includes franchise item/effect names and game-specific `Splat` at 34, also with a post-NUL suffix.
- `DMAP`: 512 records. Names are empty; title/intro fields contain spaces; enhanced-music filename arrays are zero. Their numeric MIDI selection is not a license.
- `DOOR`: decoded definitions include `Z1 CSet 0` with post-NUL suffix `ors`; the full definitions remain private. `LINK` contains hero tile/animation references, not a hidden Link image sheet. `ICON` references `78007`, `78007`, `31270`, `31276`; the last two tiles are blank.
- `MISC`: 16 shops, 16 information records, nine warp rings, eight fragment-position bytes, an ending-string reference, shop string IDs, 32 quest-misc values and 32 fixed labels, last compile version 18. All shop/info names and all 32 labels are empty.
- `DROP`: thirteen named distributions: `None`, `Default`, `Bombs`, `Rupees`, `Life`, `Bombs 100%`, `Super Bombs 100%`, `Magic`, `Magic + Bombs`, `Magic + Rupees`, `Magic + Life`, `Magic 100%`, `Tall Grass Combos`.
- `CHT`: enabled flag 1, flags 0, four empty 41-byte cheat-code buffers. `FAVS`: numeric combo/alias favorites. `MCLR`: numeric colors and tile references. `CMBA`: 8,192 numeric aliases, not another pixel sheet. `RULE`/`INIT`: flags, counters, settings and references; no additional title/credits text.

**Unresolved:** inherited text/data authorship and which dormant records are safe to remove. Clean names and residual buffer bytes without renumbering live definitions; keep relevant notices separately. Do not wholesale erase engine parameters or confuse a name like `Ganon` in an unused definition with a newly found Ganon sprite. Detailed per-record JSON, including every name and tile reference, remains private rather than republishing the complete asset data.

## Scripts and Venrob provenance

### Compiled inventory

**Verified:** `FFSC` v18, ZASM metadata v2. Exactly thirteen script records have non-terminator instructions. Blank slots remain present. Compiled record authors are empty except autogenerated `~Init`, which says `ZQ_PARSER`; blank metadata is not sole-authorship evidence.

| Kind | Slot | Name | Non-terminator instructions | Contributor assessment |
|---|---:|---|---:|---|
| FFC | 1 | `bunker` | 132 | **Inferred** ZoriaRPG plus standard helpers. |
| FFC | 2 | `killall` | 93 | Same. |
| NPC | 1 | `theinvaders` | 2,696 | Same. |
| NPC | 2 | `splatted` | 328 | Same. |
| NPC | 3 | `ufo` | 837 | Same. |
| Global | 0 | `~Init` | 68 | **Verified** compiler attribution; exact source ownership mix **unresolved**. |
| Global | 1 | `inv` | 884 | **Inferred** ZoriaRPG plus standard helpers. |
| Global | 4 | `intro` | 2,276 | **Mixed:** ZoriaRPG narrative/menu, credited Venrob-derived crawl, engine helpers. |
| Global | 5 | `newgame` | 243 | **Inferred** ZoriaRPG plus standard helpers. |
| Player | 1 | `initial` | 44 | Same. |
| Player | 2 | `playeractive` | 180 | Same. |
| LWeapon | 1 | `player_missile` | 949 | Same. |
| EWeapon | 1 | `enemy_missile` | 617 | Same. |

There are no other nonempty item, legacy-weapon, screen, DMap, item-sprite, or combo script records. The stored binding tables were decoded and retained privately. Attribution above uses source structure, not an instruction-level source map.

**Verified source mismatch:** the embedded editable source is 40,276 bytes, SHA-256 `417fa19209b286753734559fc0113d6e288fb5a91ad5f440c1d9080ea39887c4`. Repository `Invaders.zh` is 40,316 bytes, SHA-256 `80141cb83e0f88655fca200c0be399e2f35abb66b3db83f6824e413933e8deab`. A text diff finds the repository adds the `0.6.1` typo-fix history line and changes `MASSOCHIST` to `MASOCHIST`. Do not call the repository file a byte-identical build source. The compiler/header closure and successful reproduction are still **unresolved**.

### Published Venrob evidence

**Verified:** repository `Invaders.zh` lines 1274 onward credit `Credits.zh`, `V1.00`, `Venrob`. The following `crawl` namespace implements bitmap creation/resizing, line/header layout, scrolling, and input suppression. It ends before the `intro` script. It is about 220 lines of source, not merely a one-line attribution. The embedded source contains the same credit and library.

Published primary evidence inspected:

| Source | Finding | What it does not establish |
|---|---|---|
| [PureZC script 365, Credits.zh][credits] | Creator displayed as Emily; release history: `05 Dec, 2019 - V1.0 Release`; `31 May, 2021 - V1.01 - no longer uses 'bitmap.zh' header`. Describes the same line-by-line bitmap/scroll functions. | No express redistribution/relicensing terms in the inspected listing. |
| [Author-linked script download][credits-download] | ZIP contains only `Credits.zh`, V1.01, credit Emily. No license file or in-file license declaration. ZIP SHA-256 `1ed3c40b8518d5138ba3d2ae73931ff02ab495f129fef7ca817a1313da8e3a8c`. | This is a successor, not the exact V1.00 bytes. Instructions to call the library do not expressly authorize AGPL relicensing. |
| [EmilyV99/ScriptBank at `be611eb`][scriptbank] | Contains `Credits.zh` with the same V1.01 credit, constants, and function structure. File SHA-256 `f72b6815d4434ad0570762142c222b2bd77a475af83ea8382806f4efa4151e2d`. Tree has no LICENSE/COPYING file; repository license metadata is null. History attributes its initial import to that account on 2024-03-05. | A GitHub import/public view is not an explicit downstream grant. |
| `EmilyV99/misc-scripts` tree `68b0b1c89dcdad9811184a068f50d9ff49568152` | Only a README; no Credits source or license. | Repository name alone supplies no grant. |
| [PureZC license-policy discussion, both pages][policy] | Proposal expressly excludes quests and says old contributors must explicitly grant terms. | A proposal is not a retroactive license for Credits.zh. No Credits-specific grant was found there. |

**Inferred provenance:** the V1.01 library is the successor to the credited V1.00, and Emily is the current credit for this contribution. The actual V1.00-to-V1.01 license chain remains **unresolved**. No inspected source supplies a verified AGPL-compatible permission for this exact contribution. This is a bounded search result, not a claim that no permission exists anywhere.

**Recommended action:** independently replace the crawl implementation, or remove the intro and rebuild a small original difficulty menu. Cost: preserve difficulty selection and its state initialization; do not delete `intro` wholesale and accidentally remove game setup. Do not merely remove the Venrob comment, replace only the embedded source, or link the unlicensed successor: the compiled `intro` and initialization must be rebuilt too. A public grant found later could avoid this rewrite, but author contact is excluded.

## AGPLv3 obligations for a public pack

The following quotes are from the actual pinned [project LICENSE][license], SHA-256 `8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef`. **Verified text; inferred application** to this distribution. The repository does not separately state “or later”; do not silently relabel it AGPLv3+.

| Provision | License quote | Pack consequence |
|---|---|---|
| §1, source | “The ‘source code’ for a work means the preferred form of the work for making modifications to it.” Corresponding Source includes “all the source code needed to generate, install, and … run the object code and to modify the work”. | Supply the cleaned editable quest, matching script source, required source/header inputs and build/edit instructions/scripts. Assess preferred editable media forms too. A dirty upstream quest, different revision, or disassembly alone is not a source substitute. General-purpose unmodified tools/System Libraries have the stated exceptions. |
| §4, license/notices | “keep intact all notices” of applicable license terms and absence of warranty; “give all recipients a copy of this License along with the Program”. | Bundle AGPLv3 text, appropriate copyright and retained-author notices, and warranty notices. Preserve additional valid notices for incorporated code. Attribution cannot cure missing rights. |
| §5(a), marking changes | “prominent notices stating that you modified it, and giving a relevant date.” | Identify the cleaned derivative, date, and what was removed/replaced. Do not present it as ZoriaRPG's unmodified Gamma 2. |
| §5(c), copyleft | “You must license the entire work, as a whole, under this License”. | License the modified covered quest under AGPLv3. Use compatible replacement inputs, or obtain terms that permit this combination. Do not add pack restrictions that take away recipients' AGPL rights. |
| §6(d), internet object-code distribution | “offer equivalent access to the Corresponding Source … through the same place at no further charge”. | Put the matching source download alongside the quest download, or clear adjacent directions to an equally accessible source server. Maintain availability; an unspecified “source on request” promise or upstream link alone is insufficient. |
| §6(b), physical distribution alternative | A written offer must be “valid for at least three years” and for as long as the stated support/spares condition applies. | This is a specific physical-product route, not a universal three-year promise that replaces §6(d) for online packs. Device/User Product distribution can also require Installation Information under §6. |
| §13, network interaction | A modified version must “prominently offer all users interacting with it remotely through a computer network (if your version supports such interaction)” its Corresponding Source. | No remote game interaction was established here. A downloadable pack still has §6 duties. If remote interaction is added, provide the §13 source access too. |

**Verified qualifications:** §5(d) contains an exception where the original interactive interface did not display Appropriate Legal Notices; do not invent an unconditional new in-game credit-screen requirement. A release README/notices file and clear modification marking remain prudent. §5's aggregate paragraph says inclusion does not make AGPL apply to independent works in an aggregate. Merely placing this quest beside other independent games does not automatically relicense the whole starter pack. §13 expressly permits combination with GPLv3 code, while that code remains GPLv3. That provision is relevant to engine helper code, not a license for Nintendo media or the unresolved Venrob source.

No obligation here authorizes distribution of material the licensor does not own. Do not ship all 22 dirty quest revisions as “source” for the cleaned derivative.

## Conservative scrub list and feasibility gate

Actions below are a proposed no-contact route, not work performed. **Blank-preserving-index** means a valid native empty record at the same index, with array/presence semantics preserved. It does not mean deleting arbitrary bytes or truncating a section.

| Item | Action | Evidence status / gameplay cost |
|---|---|---|
| MIDI slot 0 | **Remove**, preserve all other indices | **Verified bytes/title**; no remaining embedded music if removal is correctly serialized. Recheck selectors and fallback behavior. |
| Twelve nonempty PCM slots listed above | **Replace** at same sound IDs with original/compatibly licensed cues; valid silence only by explicit choice | Ownership **unresolved**. All 12 payloads leave the derivative. Silence loses cues; intro/win conditions need tests. |
| Forty-seven zero-frame samples | **Keep**, or **replace** with validated silent records | **Verified empty payloads**. Loader validity is not proved for a future rewritten file. |
| Absent sound slots 10/11 and stock runtime defaults | **Keep** only with cleaned engine replacements, or **replace** in quest | **Verified fallback path**. Do not restore original SFX data to get the old sound. |
| Tiles 0–4 and page 100's 18 tiles | **Blank-preserving-index** if unused; otherwise **replace** | Ownership/use **unresolved**. Two exact reference matches are not a complete graphic finding. |
| Page 300's 104 nonblank tiles | **Replace** used sprites/shields at same indices; **blank-preserving-index** proven unused cells | Ownership **unresolved**. Shield collision uses pixels; preserve dimensions/silhouettes or deliberately retune collision and test. |
| Palettes/names | **Replace** used color sets with documented palettes; **blank-preserving-index** unused sets and template labels | Provenance **unresolved**. Script-indexed colors and contrast are gameplay/UI constraints. |
| Venrob-derived crawl | **Replace** implementation, or **remove** crawl and replace difficulty UI/setup | Attribution **verified**, permission **unresolved**. Recompile, preserving startup and all difficulty paths. |
| Compiled scripts and embedded source | **Replace** together with a reproducible build of cleaned source | Mixed provenance/build **unresolved**. Preserve 13 live script identities/bindings; do not leave old code in unassigned slots. |
| ZoriaRPG logic and eleven game-specific visible strings | **Keep** under AGPLv3 with notices and modification marking | Ownership/grant scope **inferred**. Keeping story/title is a separate product/editorial choice, not legal clearance. |
| Functional passive score HUD | **Keep/rebuild**; **replace** original font dependency | Mixed origin **unresolved**. Score, lives, round and high score must remain usable. |
| Unused subscreens and franchise/template text | **Blank-preserving-index**; keep legally required retained-source notices separately | Stored residue **verified**. Establish use before clearing; disabled is not absent. |
| Inherited item/NPC/weapon/door/drop/palette names and stale post-NUL bytes | **Blank-preserving-index** or **replace** expressive labels; **keep** required numeric mechanics | Presence **verified**, ownership/use **unresolved**. Name lookup, enemy creation, missiles, and effects can break if live definitions change. |
| Unused map/template screens, aliases, favorites, miscellaneous references | **Blank-preserving-index** only after reference audit; otherwise **keep** numeric structures pending review | Inventory **verified**, reachability **unresolved**. No shifting of maps/screens/combos. |
| Original engine font pixels/default tiles | **Remove** from release dependencies; **replace** fonts through cleaned engine | **Verified dependency distinction.** Header tile flag is 1: the quest embeds tiles and does not require `190_tiles.qst`. Still test all nine font selectors and ending/menu paths. |
| Other 21 quest revisions in creator repo | **Remove** from the proposed pack/source bundle | Tree inventory **verified**, their components were not decoded or cleared. They are not required to convey the cleaned version's source. |

**Inferred verdict:** this is feasible as an AGPL derivative with replacement media and a small source rewrite. It is **not established as a low-cost, ready-made starter**. The known work surface is 12 PCM records, up to 127 nonblank tile slots, the palette/template residue, the approximately 220-line library, and an exact-source/compiler rebuild. Replacing everything unresolved avoids needing new author contact, but costs the original audiovisual presentation and can change collision behavior. Deleting the MIDI alone leaves all these problems.

**Unresolved release gates:** source reproduction; evidence for any original media retained; clean editable source packaging; complete static reference audit before blanking; new-game/restart, all three difficulties, scoring/high score, shield damage/regeneration, UFO, player damage, game over and round-256 win; sound initialization and actual cues; target rendering/controller compatibility. No new runtime was run. The earlier 1,800-frame exit-0 observation with 144 GetPixel diagnostics remains only the earlier bounded observation, not verification of this plan.

## Repository-file scope

**Verified:** `README.md` is 78 bytes and says Pagan Invaders requires ZQuest Creator 2.55 Alpha 60 or later. `Invaders.zh` and `LICENSE` were read in full. The exact pinned Gamma 2 was decoded above. The other 21 QSTs were inventoried from the pinned tree's names, sizes and Git blob IDs, **not downloaded/decoded in this pass**. Do not extend this assessment to them.

They are `PaganInvaders.qst`; numbered suffixes `_2`, `_3`, `_4`, `_6`, `_7`, `_8`, `_10`, `_11`, `_13`, `_14`, `_15`, `_16`, `_17`, `_20`, `_21`, `_32`, `_41`, `_50`; and `_Gamma_1`, `_Gamma_2_for_2.55_A60`, all under `bin/` with extension `.qst`. Together with the inspected `_Gamma_2`, these are 22 revisions of one game. No standalone sound, graphics, font, or contributor-license files appear in that tree.

## Private receipts and validation

Durable evidence is `/home/simonwjackson/.local/state/zquest-pagan-audit`, mode **0700**. Downloads have adjacent `.receipt.json` files with URL, resolved URL, status, UTC time, byte count, and SHA-256. HTTP failure bodies are not permission evidence. Raw pages contain session links and remain private. Evidence is not a public source release.

| Private artifact | Contents |
|---|---|
| `PaganInvaders_Gamma_2.qst`, `LICENSE`, `Invaders.zh`, `README.md`, `pagan-tree.json` | Pinned creator evidence and receipts. |
| `inventory.py`, `supplement.py`, `decoded/` | Existing reader reuse, native-schema adapters, all section hashes and per-record inventories; MIDI/PCM remain private. |
| `compare.py`, `old-sfx.py` | Exact tile/palette/PCM comparisons; no perceptual or ownership inference built into matching. |
| `credits365*`, `emily-scriptbank-*`, `emily-credits-history.json` | Primary contributor evidence, ZIP and receipts. |
| `engine/`, `old-engine/` | Pinned native schemas, license, dependency/default references and receipts. Historical reference is not asserted to be the exact quest build. |
| `verify.py`, `verification.txt` | Receipt hashes, evidence mode, input hash/size, complete section-boundary coverage, inventory assertions. |

**Verified checks:** receipt verification passed for 74 downloads; the input hash/size passed; all 25 contiguous section hashes/extents passed; inventory count assertions passed. Native supplements require exact byte consumption, including `FFSC` and all PCM lengths. The unadapted reader's ITEM/INIT/FFSC limitations were reproduced and corrected only for private inspection. No parser exception is being interpreted as an empty section. Markdown lint passed with only line-length and table-alignment rules disabled (`MD013`, `MD060`); `git diff --check` passed. Typechecking is not applicable to this documentation-only repository change. No official editor resave, source compilation, native gameplay, full test suite, or legal review was performed.

The source changes to publish, if separately approved, must be a later slice. Keep this branch unmerged until the parent reviews the assessment. The recommendation does not authorize adding this quest to the public pack.

[quest]: https://raw.githubusercontent.com/ZoriaRPG/PaganInvaders/9ef5923df39d901a2f1fac9d9d47c9a635ce0bf6/bin/PaganInvaders_Gamma_2.qst
[tree]: https://api.github.com/repos/ZoriaRPG/PaganInvaders/git/trees/9ef5923df39d901a2f1fac9d9d47c9a635ce0bf6?recursive=1
[license]: https://github.com/ZoriaRPG/PaganInvaders/blob/9ef5923df39d901a2f1fac9d9d47c9a635ce0bf6/LICENSE
[native]: https://github.com/ZQuestClassic/ZQuestClassic/tree/882c906b17e35b4105188e6305ae2929aeba30e3/src/core
[counts]: https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/base/general.h
[fonts]: https://github.com/ZQuestClassic/ZQuestClassic/blob/882c906b17e35b4105188e6305ae2929aeba30e3/src/core/fonts.cpp
[credits]: https://www.purezc.net/index.php?page=scripts&id=365
[credits-download]: https://www.purezc.net/index.php?page=download&section=Scripts&id=365
[scriptbank]: https://github.com/EmilyV99/ScriptBank/blob/be611eb94b1bfa2fadd84738f9a7891fc93ca8ca/Credits.zh
[policy]: https://www.purezc.net/forums/index.php?showtopic=78284
