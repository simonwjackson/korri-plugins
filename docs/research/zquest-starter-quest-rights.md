# ZQuest Classic starter quest rights

Checked 2026-10-03. **Zero quests qualify for the public Nintendo-free starter pack on the evidence checked here.** Do not add these candidates. This is a packaging decision, not a finding that every quest infringes copyright or that no eligible quest exists.

The audit found a concrete trap. All four downloaded Aevin-family quests contain the same embedded MIDI identified as Zelda: The Wind Waker's "Wind Temple". Removing their external soundtracks would leave that MIDI inside the distributed `.qst` files. Non-Zelda gameplay and original graphics do not make a package Nintendo-free.

No quest files, MIDI files, tile sheets, or soundtrack files are published with this report. No authors were contacted. The starter pack, Tiny5 worktree, and devices were not changed. The Deep on Mini V2 was not stopped.

## Acceptance criteria and scope

A qualifying release needs explicit permission to redistribute the quest and permission for every included component. That includes maps, scripts, text, graphics, unused tiles, music compositions, arrangements, sequences or recordings, sound effects, fonts, logos, and external dependencies. Attribution alone is not permission. The engine's GPL does not license quest media.

The release also needs meaningful gameplay on the cleaned player without restoring `190_tiles.qst`. Runtime and rights are independent checks. Public redistribution does not automatically require unrestricted commercial permission. A noncommercial grant needs its own distribution-scope check.

This pass screened the [official manifest](https://data.zquestclassic.com/manifest.json), inspected 11 original PureZC ZIPs, and decoded one quest file per candidate. Island Adventure and Space Adventure each also contain an English quest file. Those English files were inventoried and hashed, but not decoded or run. Other investigations inspected primary pages for the BotB catalog, itch releases, asset packs, and further PureZC candidates.

No candidate passed all rights checks. Once a candidate had a decisive content or permission blocker, the remaining media audit stopped. This is not a complete component inventory or legal clearance. External soundtrack archives, full in-game credits, sound samples, script ownership, and font provenance remain unchecked unless stated otherwise.

## Downloaded candidates

The links below identify the author-submitted primary listings. The ZIP endpoint for each ID is `https://www.purezc.net/index.php?page=download&section=Quests&id=<ID>`.

| Candidate | Checked permission evidence | Concrete media evidence | Decision |
|---|---|---|---|
| [Starshooter Supreme, 646](https://www.purezc.net/index.php?page=quests&id=646) | No public-pack grant found in the inspected listing or ZIP inventory. | Eight embedded MIDIs. Slot 6 is titled `SSBM_Brinstar_Depth` and credits Dave Phaneuf. Its declared source is a Nintendo-game music lead. 209 nonblank tiles match the classic reference bytes. | Not cleared. Music and graphic provenance need separate grants. |
| [Pagan Invaders, 742](https://www.purezc.net/index.php?page=quests&id=742) | Listing credits say "N/A". No public-pack grant found in inspected sources. | Embedded MIDI slot 0 is titled `The Legend of Zelda A Link to the P`. 127 nonblank tiles exist, including two reference byte matches. | Reject this unmodified file for the Nintendo-free claim. |
| [Block Smasher, 422](https://www.purezc.net/index.php?page=quests&id=422) | Author says "Do whatever you want with the questfile, it's unpassworded." This is real permission language in editing instructions. Its downstream distribution scope is not resolved here. | Seven embedded MIDIs. Metadata expressly identifies Donkey Kong Country 2 and 3, Rareware/Nintendo, and sequencers. 5,622 nonblank tiles match the reference. ZIP also includes `BlockSmasher.z`. | Reject this unmodified package. Even a broad author grant cannot clear unrelated music rights. |
| [Pong, 428](https://www.purezc.net/index.php?page=quests&id=428) | Author claims item ideas, graphics, and sounds. Listing credits also name the original MIDI pack, Atari, and Nintendo. No public-pack grant found. | Nine embedded MIDIs with third-party metadata. 5,605 nonblank tiles match the reference. | Not cleared. The visible paddles do not describe everything in the file. |
| [Island Adventure, 338](https://www.purezc.net/index.php?page=quests&id=338) | "Selfmade tileset" is a description, not a license. Credits also name DoR tiles, script contributors, and Bjorn Lynne. | German quest contains six MIDIs and 5,609 reference tile matches. MIDI 0 identifies "Sunny Morning" by Bjorn Lynne and says "All Rights Reserved. Licensed use only." | Not cleared. No license chain for this distribution was found. English edition remains unaudited. |
| [Space Adventure, 447](https://www.purezc.net/index.php?page=quests&id=447) | "Custom graphics" is not a license. Credits name DoR tiles, MoscowModder scripts, and VGMusic.com. No public-pack grant found. | German quest contains six MIDIs and 5,601 reference tile matches. | Not cleared. English edition and complete music/graphics rights remain unaudited. |
| [This is The Only Room, 840](https://www.purezc.net/index.php?page=quests&id=840) | Listing credits Kevin MacLeod's "Snare Bounce Polka" under CC-BY 4.0. That grant concerns the named external music, not the quest or its other assets. | MIDI parsing succeeds and finds the same Zelda-titled slot 0 as Pagan Invaders. The section reader fails for header, strings, palettes, and tiles. Do not treat those failures as empty sections. | Reject this unmodified file for the Nintendo-free claim. Other media remain unresolved. |
| [Hitodama DX, 494](https://www.purezc.net/index.php?page=quests&id=494) | Author claims a "completely original tileset". Listing sends the reader to in-game full credits. No public-pack grant found. | 38 embedded MIDIs, including slot 24 `Wind Waker - Wind Temple`. 27 reference tile byte matches. Manifest lists 20 external music entries. | Reject this unmodified file. Original-tiles claim does not clear retained music. |
| [Yuurei DX, 616](https://www.purezc.net/index.php?page=quests&id=616) | No public-pack grant found. Author recommends sharing its soundtrack directory with Yuurand and Hitodama. | Same 38 embedded MIDIs and 27 reference tile matches. Manifest lists 62 external music entries. | Reject this unmodified file. Local co-location advice is not public redistribution permission. |
| [Yuurand, 667](https://www.purezc.net/index.php?page=quests&id=667) | Russ reports Aevin's blessing for an update. That does not expressly license this publisher's public pack. Full credits are in-game. | Same 38 embedded MIDIs and 70 reference tile matches. Manifest lists 260 external music entries. | Reject this unmodified file. Every contributor and external resource would also need review. |
| [Reikon, 716](https://www.purezc.net/index.php?page=quests&id=716) | Listing names multiple contributors and directs readers to in-game full credits. No public-pack grant found. | Same 38 embedded MIDIs and 29 reference tile matches. Manifest lists 48 external music entries. | Reject this unmodified file. External music removal is insufficient. |

These tile counts measure shared bytes, not independent copyrighted works. Simple shapes, text glyphs, and generic tiles can match. A byte match alone does not establish ownership, copying, or infringement. This comparison cannot prove that unmatched tiles are original or licensed. Tile extraction and byte comparison include unused tiles. Visual inspection was only a sample, not a complete tile provenance audit.

## Embedded music evidence

The four Aevin-family ZIPs contain only their respective `.qst` files. Lossless local downloads replace the earlier research agent's lossy ZIP-as-text inspection.

In all four files, MIDI slot 24 has these embedded track-name events:

> The Legend of Zelda
>
> The Wind Waker
>
> Wind Temple
>
> Sequenced By
>
> Aevin Abstract

The exported MIDI SHA-256 is identical in all four files:

`010df36bf5a5ac37c32117ed76bcc24b027eac1a562dcb76708cdf9032519e92`

Other embedded titles include `GS2_Airs_Rock`, `GS Jupiter LighthouseNew`, `smetmar2`, and `DKC2: Wasp Hive`. Metadata includes "Super Metroid Maridia 2" and "(C) 2001-2003 Nintendo/CAMELOT". These are direct embedded declarations, not identifications inferred from external soundtrack filenames. Compositions were not independently identified by listening. No Nintendo redistribution grant was found.

Pagan Invaders and This is The Only Room each contain an exported slot-0 MIDI with SHA-256:

`bcf82e9649d84e84f9ef49d781c91613a324b9009fe1632ade197a00c894fbb2`

Both name it `The Legend of Zelda A Link to the P`. This remains part of the distributed file even if the game uses external music instead.

Block Smasher's embedded MIDI 1 says:

> Donkey Kong Country 2 by Rareware/Nintendo for the Super Nintendo Entertainment System.

It separately credits Andreas & Savas Oulassoglou as sequencers. Permission from a sequencer does not by itself establish permission for the underlying composition.

## Aevin external soundtrack scope

The [Yuurei DX announcement](https://www.purezc.net/forums/index.php?showtopic=75245), 2019-07-21, recommends keeping the quests together to avoid duplicate music. The [Hitodama DX announcement](https://www.purezc.net/forums/index.php?showtopic=75182), 2019-06-21, says "Enhanced music in place of the midi tracks." These statements do not remove the MIDIs observed in the downloaded files.

Yuurand's live listing says its complete soundtrack supplies Hitodama, Yuurei, and Reikon. The [8.0 announcement](https://www.purezc.net/forums/index.php?showtopic=79210) records a corrected music pack on 2024-12-26. Quest and soundtrack revisions therefore need separate receipts.

| Author-linked music package | Primary landing page | Check performed |
|---|---|---|
| Hitodama DX | [Dropbox](https://www.dropbox.com/s/mu9sbpn5e9p173y/HitodamaMusic.zip?dl=0) | Landing page only. No archive or complete credits audit. |
| Yuurei DX | [MediaFire](https://www.mediafire.com/file/eg9341xbp0mdftz/Yuurei_DX_Music.zip/file) | Landing page names `Yuurei DX Music.zip`, 201.55 MB. Archive not inspected. |
| Yuurand shared pack | [MediaFire](https://www.mediafire.com/file/rxfdo4r74ynap3q/Yuurand_Music.zip/file) | Landing page names `Yuurand Music.zip`, 789.27 MB. Archive not inspected. |
| Yuurand 8.0 update | [MediaFire](https://www.mediafire.com/file/8nfwt2vudfy3m2j/8.0+Update+Music.zip/file) | Landing page names `8.0 Update Music.zip`, 81.53 MB. Archive not inspected. |
| Reikon | [Dropbox](https://www.dropbox.com/s/x0y83yzzrakq7en/ReikonMusic.zip?dl=0) | Landing page only. No archive or complete credits audit. |

External filenames are not proof of composition or recording origin. OGG conversion and NSF/VGM extensions do not establish ownership. [The Spectral Web: Hitodama](https://aevin-abstract.itch.io/the-spectral-web-hitodama) is a later commercial product. Its advertised new songs do not clear the older PureZC quest.

## Site terms and further leads

The [PureZC rules](https://www.purezc.net/forums/index.php?showtopic=55197), marked updated 2025-02-06, say:

> Any copyrighted materials cannot be distributed without the explicit permission and credit of the original author(s)

This is a restriction, not a downstream grant. The full authenticated quest-submission agreement was not inspected.

The [2023 license proposal](https://www.purezc.net/forums/index.php?showtopic=78284), post 1, explicitly says:

> Quests are excluded from this - "assets" refer to everything in the database _but_ quests

It also says existing contributors need to grant a license explicitly. Post 5 changes the initial proposal toward a submission field for allowed uses. Neither a proposal nor community approval establishes permission for these quests. Adoption of a later submission policy is unresolved here.

| Further source | Verified primary-page evidence | Remaining cost or exclusion |
|---|---|---|
| [BotB license policy](https://battleofthebits.com/lyceum/View/BotB+CC+License) and [21-entry ZQUEST browser](https://battleofthebits.com/browser/Format/zquest) | Policy describes an Attribution NonCommercial ShareAlike license on entry pages. It separately grants BotB redistribution rights. Six individual entry pages returned HTTP 403. | Individual license version, package scope, and every media origin remain unresolved. NC alone does not rule out a genuinely noncommercial pack. No entry archive was audited. |
| [Evil Castle 2.0, 108](https://www.purezc.net/index.php?page=quests&id=108), [Winning The Lottery, 813](https://www.purezc.net/index.php?page=quests&id=813), [OverHead, 706](https://www.purezc.net/index.php?page=quests&id=706) | Nonstandard premises. No whole-quest grant found in inspected descriptions or credits. | Archives, embedded media, and runtime remain unchecked. These are leads, not eligible starters. |
| [Nargad's Trail, 605](https://www.purezc.net/index.php?page=quests&id=605) | Credits include a heavily modified DoR tileset and "Some custom music". | All non-custom music, contributor permissions, other media, and whole-quest grant remain unresolved. |
| [Green Ninja, 411](https://www.purezc.net/index.php?page=quests&id=411) | Credits explicitly name Nintendo and Metroid tiles. | Unsuitable for the Nintendo-free claim on this evidence. |
| [Boulder's Revenge, 313](https://www.purezc.net/index.php?page=quests&id=313) | Author describes a Pokémon boulder and Mt. Moon. | Franchise content remains. No complete clearance. |
| [The Titan's Quest, 406](https://www.purezc.net/index.php?page=quests&id=406), [Castle Haunt II, 152](https://www.purezc.net/index.php?page=quests&id=152), [barato, 833](https://www.purezc.net/index.php?page=quests&id=833) | Descriptions retain Zelda/Hyrule material. Castle Haunt II also specifies `sfx.dat`, MP3 files, and ZC 2.10. | Nintendo-free status fails on current evidence. Soundtrack and other rights remain separate gaps. |
| [100 Rooms of Wisdom, 750](https://www.purezc.net/index.php?page=quests&id=750), [2, 772](https://www.purezc.net/index.php?page=quests&id=772), [3, 818](https://www.purezc.net/index.php?page=quests&id=818) | Author descriptions retain Link and Triforce material. Music credits name VGMusic.com, and the third also names musescore.com. | Puzzle mechanics do not establish Nintendo-free content or media grants. |
| [Mike Murray's itch quests](https://king9999.itch.io/zelda-classic-custom-quests) | Author says they use "graphics from BS Zelda no Densetsu". | Exclude these versions from the Nintendo-free pack. |
| [Isle of Rebirth](https://madpriest.itch.io/isle-of-rebirth) | Author says it is based on The Legend of Zelda for NES. | Exact media and rights are unchecked. No Nintendo-free clearance. |
| [Koten v1.11](https://www.purezc.net/index.php?page=tilesets&id=87) | Author explicitly permits editing and redistribution, including commercial use, under CC-BY-SA 4.0. Credits name tiles, SFX, and palettes. | Asset-level grant only. Archive media and Nintendo-free character designs still need inspection. No complete game supplied or cleared. |
| [Zoria tileset](https://opengameart.org/content/zoria-tileset) | Creator grants CC-BY 4.0 for the artwork and describes original replacements for commercial Zelda graphics. | Artwork-level grant only. It does not license a complete quest, music, or unrelated resources. |
| [ZQuestClassic/commons README at `612c673`](https://github.com/ZQuestClassic/commons/blob/612c673aca4785ac03f3f6f3d4a19fc61b612470/README.md) | README claims developer ownership and permits included assets inside distributed ZQuest games. [`ZC Forever/CREDITS.txt`](https://github.com/ZQuestClassic/commons/blob/612c673aca4785ac03f3f6f3d4a19fc61b612470/ZC%20Forever/CREDITS.txt) names Beatscribe as composer. | ZQuest-only conditions remain. No complete playable quest. Ownership records, samples, and exact asset bytes were not audited here. |

The BotB targets were BlockStationary 81111, ephemeral visit 81109, A Dream, An Interlude 81116, Into the Forest 81107, Ghosts of Cypress 81108, and The Three Trials 72765. Failed entry access is not evidence against their creators or proof of incompatible licenses.

A review posted under the display name "Shigeru Miyamoto" on barato is not verified Nintendo authorization. Contributor names, unpassworded files, download buttons, and manifest `approval` fields are not licenses.

## Clean-player runtime checks

The local x86 test used the cleaned `public1` player from the [published release](https://github.com/simonwjackson/korri-plugins/releases/tag/zquest-public-31ebc60a054f). Plugin source is `31ebc60a054fdc64ab132f02595ff63c8237a2f2`; engine pin is `882c906b17e35b4105188e6305ae2929aeba30e3`.

Executable package:

`/nix/store/j07fyph19n8i524nwqps4hdir9q31fmf-zquest-classic-unstable-2026-06-18-public1`

Each replay-mode test used its own working directory, a direct quest path in a synthetic input replay, headless rendering, and no sound. Replays targeted 1,800 frames. No `190_tiles.qst` was restored. This was not an ARM or Mini V2 test, completion run, audio test, or proof of all controller mappings.

| Quest | Observed result | What it does not establish |
|---|---|---|
| Starshooter Supreme | Exit 0. Frame 1,700 screenshot shows the story introduction. | Shooter gameplay and completion remain untested. |
| Pagan Invaders | Exit 0. Frame 1,700 shows enemies, player, score 20, and three life indicators. Log contains 144 `Invalid coordinate for getpixel` diagnostics. | Full game and completion remain untested. The exit was not diagnostic-free. These messages do not establish incompatibility. |
| Block Smasher | Exit 0. Frame 1,700 shows the first level and "READY". | Meaningful level progression remains untested. |
| Pong | Exit 0. Frame 1,700 shows paddles, ball, and scores 30 and 10. | Every game mode and two-player controls remain untested. |
| Island Adventure, German | Exit 0. Frame 1,700 shows its island level. | The 100 levels, raft controls, and English edition remain untested. |
| Space Adventure, German | Exit 0. Frame 1,700 shows its space level. | The 100 levels and English edition remain untested. |
| This is The Only Room | Quest loads and frame 900 shows level 1, stage 1. Replay exits 1 at frame 1,034 with `rng desync! stopping replay`. | This synthetic replay failure does not prove an engine incompatibility. Continued gameplay remains untested. |
| Four Aevin-family quests | Not run. Their distributed files already fail the content gate. | No pinned-engine compatibility claim. |

Six exit-0 results do not mean six eligible or fully playable starters. See [the player publication audit](zquest-publication-audit.md) for the separate engine asset review.

## Evidence receipts and reproducibility

The manifest snapshot has 796 top-level entries, including 795 quests. SHA-256:

`3ebbfe892d9661abb8567417b104f4edfe67c223c4a9e350e80f284af8554d0d`

Private evidence lives in `/tmp/zquest-starter-research-evidence/`. Each numbered directory contains `page.html`, `receipt.json`, the original ZIP, and extracted files. The receipt records page hash, exact download URL, redirected URL, archive hash, and every archive member's size and SHA-256.

The private reader is [connorjclark/zquest-data](https://github.com/connorjclark/zquest-data) at `a52b5d19cb73439137ef281110c8831774000c5e`. It decoded selected header, strings, palette, tile, and MIDI sections. Reader section parsing failures are recorded in `decoded/inspection.json`. Sounds, scripts, and other sections were not fully decoded.

The tile reference is that revision's `test_data/1st.qst`, SHA-256 `69741eda8fe7e5d09c575304cfa78c3cf3340d6b0d566a88baebfdeabf08f8eb`. The first attempted reference, upstream `default.qst`, failed tile parsing and was not used. Tile sheets use raw palette indices, not guaranteed gameplay colors.

Private Nix-shebang helpers are `/tmp/zquest-starter-fetch-primary.py`, `/tmp/zquest-starter-inspect-qst.py`, and `/tmp/zquest-starter-native-smoke.py`. Findings can be repeated against the hashes below. These helpers and `/tmp` evidence are local research artifacts, not durable public downloads. Preserve them outside `/tmp` before continuing a binary audit. Do not republish the candidate files without permission.

### Checked quest file hashes

| ID | Decoded quest file | SHA-256 |
|---|---|---|
| 646 | `Starshooter Supreme 250.qst` | `bb9b16713d174605f459abf6e6681d6e52e167e3d2c374a8103e135666799b9b` |
| 742 | `PaganInvaders_Gamma_2.qst` | `53ececcef40eeba2b5f275c309e1a8aa3809a5fe0047920391d9bfe8fb74b690` |
| 422 | `Block_Smasher.qst` | `2fb1fc6d0a8e117fdf31f6fc92ba4feb980960e7f053e832010b48b53aef4f44` |
| 428 | `Pong.qst` | `ca42234093865f589e8e2d4e8aef9d6aaa3425964df4c3629de379065eaea723` |
| 338 | `Island_Adventure_Deutsch.qst` | `a91fe11e624475c77c2fb824f67100e49221f81e3b3f71ea72844432b9d5bb5f` |
| 447 | `Space_Adventure_Deutsch.qst` | `4c380ccc41b45424b0c98f68f388aeddb8f9de97d1e9dc6a6a8731ffb9ce9382` |
| 840 | `onlyroom.qst` | `c58d72fa95680e96fa83702fc7d67425da910871374f8733154efcfa9d04d7d5` |
| 494 | `HitodamaDX.qst` | `a01eb0ac9072c0b85df64cef8830ca7ba1041b096251cb86adca128111e8d3ed` |
| 616 | `YuureiDX.qst` | `77e89dfb3da1211920948126bfb9d81c1ccc170b0772b2439096b7cade51237e` |
| 667 | `Yuurand.qst` | `cbc4880a050cc57879d71209f3cab7d5ef5fb4a225afa939e43e8cf5a51fec1a` |
| 716 | `Reikon.qst` | `e944181e447571740d1b5eda4836cc7c4686aab350dbe0b261f0d466ab1e0868` |

The English files were only inventoried. Island Adventure English SHA-256 is `913a5f467f5fb986411345ea75a5578fdbf8640f1cc923adecce91eed8aa6bc4`. Space Adventure English SHA-256 is `02117da2f27066ff88d0450831d4f2d9e800d7eeecd5c6be56c71cdd237842e8`.

An independent evidence review found no blockers to the zero-candidate decision. It verified 11 ZIPs, 14 archive members, page receipts, counts, hashes, and the bounded runtime observations. The report records its runtime notes. It did not access devices or establish rights for any candidate.

## Decision and next permission request

Keep the public starter pack unchanged. Cost: this pass supplies none of the requested three to five games. It does not prove that permissions are unavailable.

Author contact needs approval. The narrow useful request is permission for an exact quest release plus a complete contributor/media inventory. Any cleaned replacement also needs modification permission and a new binary audit, including unused resources. New original content from licensed assets is another route, but it requires game development and does not satisfy this ready-made quest search.
