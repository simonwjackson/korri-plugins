# Solarus quests for a redistributable starter pack

Research date: 2026-10-03 UTC.

**Word Breaker is the strongest licensing lead. This audit did not establish three finished quests with resolved asset permissions for commercial redistribution.** 3D Tic-Tac-Toe has one unresolved bitmap. CastleSolarus needs additional permissions and completion evidence. The Solarus Sample Quest has the clearest standard-license asset coverage, but it is explicitly unfinished.

[Follow-up repository research](solarus-additional-quest-candidates.md) adds Perlshaw's Problems as a positive licensing candidate, plus Blue Isle and Vegan on a Desert Island as further leads. It does not establish three finished, accepted games.

The audit found concrete reasons to exclude the inspected Children of Solarus, Closed Circle, and The Epic of Den versions. Do not turn their general GPL or CC descriptions into an all-assets permission claim.

No quest was installed, executed, modified, built, or published. No device was accessed. Downloads and comparison media remain private under `/tmp/solarus-quest-research/`. This is an engineering permissions audit, not a legal determination about infringement or copyright protection.

## Result and recommended follow-up

| Quest | Verified permission evidence | Decision and cost |
|---|---|---|
| [Word Breaker](https://www.solarus-games.org/games/word-breaker/) | All 118 identified runtime media files have specific grants. The actual packaged quest includes font, flag, and music notices. | Best candidate for a controlled reissue. Accept or replace its custom-licensed music, check attribution, and test controller use. It is not an all-standard-license title. |
| [3D Tic-Tac-Toe](https://gitlab.com/llamazing/3d_tic-tac-toe) | GPL scripts and explicit CC BY-SA 4.0 grants for two of its three PNGs. No audio or font files in the inspected source. | Ask the author to clarify the third PNG. This is a small permission gap, but a controller-ready packaged release is not verified. |
| [CastleSolarus](https://gitlab.com/jrdasm/CastleSolarus) | Extensive per-file grants. Twelve initially uncredited PNGs exactly match an upstream CC BY 3.0 resource. | Hold. Five runtime images and seven editable art files still lack specific grants. Completion is unverified. This requires more work than the two puzzle games. |
| [Solarus Sample Quest](https://gitlab.com/solarus-games/solarus-sample-quest) | All 395 inspected image, audio, font, icon, and editable-art files match explicit standard-license or public-domain records. | Licensing fallback if a demonstration is acceptable. Its own description says there is not much to play. It does not meet the finished-game preference. |
| [Children of Solarus](https://www.solarus-games.org/games/children-of-solarus/) | Some replacement art and most audio have positive free-license evidence. Eight current images match explicitly proprietary predecessor assets. | Exclude this source revision. It also has unresolved notices, Zelda story references, and no published release. Fixing eight images alone does not clear it. |
| [Closed Circle](https://boaromayo.itch.io/closed-circle) | A released small game with extensive GPL and CC BY-SA records. Its actual release contains a used CC BY-NC font. | Exclude the current release from a commercial pack. Resolve or replace that font and the WolframTones-derived music, then audit the revised release. |
| [The Epic of Den](https://boaromayo.itch.io/den) | Explicit GPL, CC, and custom music/font grants, with substantial upstream sound provenance. | Exclude from the finished-game set. The release is a pre-alpha demo and has attribution and provenance gaps. Music replacement alone does not solve these. |

**Opinion:** pursue Word Breaker and the small Tic-Tac-Toe permission request before curating an unfinished adventure. The cost is a puzzle-heavy shortlist. This does not provide three finished games or prove handheld suitability.

## Method and license rules

The first pass fetched the official Solarus catalog and complete game pages, first-party repository APIs, and five Solarus Jam creator pages. Explicit game-specific licenses determined which leads received archive inspection. A generic website footer did not override a game's `Unknown` or proprietary license field. Source availability and free download buttons were not permission grants.

The second pass inspected immutable source archives, actual packaged quests where available, per-file editor metadata, code notices, fonts, music notices, credits, and exceptions. Comparisons used file hashes and independently decoded image pixels. Downloaded quest code was never executed.

Initial delegated catalog reports used search excerpts only. They are discovery leads, not clearance evidence. The conclusions here use actual primary pages and inspected bytes.

[GPL permits commercial distribution](https://www.gnu.org/licenses/gpl-faq.html#DoesTheGPLAllowMoney). [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.en) and [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.en) also permit commercial sharing, subject to their conditions. Copyright ownership is not itself a blocker. Missing permission, NC restrictions, and contradictory third-party rights are blockers.

A per-file grant is stronger evidence than a repository badge. It is not an independent warranty that the contributor owns every underlying right. A missing metadata record is a documentation gap, not automatic proof of an unlicensed work. Attribution, source obligations, ShareAlike, modification notices, and restrictions still need compliance review before publication.

## Word Breaker

Inspected [commit `d3a333d76cb54d5c4e4b86257b166d06595b0cc7`](https://gitlab.com/llamazing/word_breaker/-/tree/d3a333d76cb54d5c4e4b86257b166d06595b0cc7). The official page links the `.solarus` file at this same revision, although its game-specific license field says `Unknown`.

The source and embedded release each contain 236 quest files. Only `quest.dat` and `project_db.dat` differ. The source says version `0.2.1`, while the actual packaged quest says `0.2`. Their parsed per-file license records are identical. Every other file is byte-identical. Do not silently label the packaged metadata `0.2.1`.

The [actual project database](https://gitlab.com/llamazing/word_breaker/-/blob/d3a333d76cb54d5c4e4b86257b166d06595b0cc7/data/project_db.dat) covers all 118 runtime media files:

| Declared license | Files | Inspected material |
|---|---:|---|
| SIL OFL 1.1 | 11 | TTF fonts, with bundled family notices. |
| MIT | 2 | Go Squared flag images, with bundled notices. |
| CC0 1.0 | 8 | Declared artwork resources. |
| CC BY-SA 4.0 | 86 | Declared graphics and audio resources. |
| Soundimage International Public License | 11 | Eric Matyas music, with a separate bundled license. |

The code declares GPL v3, including individual script notices. The dictionary has a Llamazing CC0 record. Its actual `dictionary.dat` is a short-word list, not a file of copied definitions. Its header and loader provide no external supplier attribution. That establishes the declared grant, not independent proof of how the collection originated.

The [bundled music license](https://gitlab.com/llamazing/word_breaker/-/blob/d3a333d76cb54d5c4e4b86257b166d06595b0cc7/data/musics/license.txt) identifies the Soundimage text dated 25 Apr 2020. Section 2 explicitly permits reproduction, sharing, and adaptations. Its extra Section 3 condition says:

> The use of the Licensed Material in media that violates Youtube community guidelines is prohibited.

The [current licensor page](https://soundimage.org/sample-page/) instead states:

> The use of the Licensed Material in media that is obscene or pornographic is prohibited.

These are different texts. Do not silently replace the bundled conditions with the current page. Neither is ordinary CC BY 4.0. The [composer explicitly permits commercial use](https://soundimage.org/) and [requires attribution in the actual game](https://soundimage.org/attribution-info/). Check the applicable grant, track attribution, and notices before a reissue. Alternatively, replace the music under a confirmed standard license. Replacement changes the experience and requires audio testing.

Some font notices contain `All Rights Reserved` followed by an explicit OFL grant. That phrase alone does not negate the grant. Preserve the OFL notices and reserved-font-name conditions.

The official page describes mouse and keyboard controls. This audit did not test gamepad input, completion, saving, or Solarus 2.1.4 behavior.

## 3D Tic-Tac-Toe

Inspected [commit `6ec1faa5f7e5c3cfbb116e54be4c2df38a5f48d7`](https://gitlab.com/llamazing/3d_tic-tac-toe/-/tree/6ec1faa5f7e5c3cfbb116e54be4c2df38a5f48d7). The source has 18 quest files, format 1.6, version 0.1, and three PNGs. It includes GPL text and GPL-or-later script notices.

The [project database](https://gitlab.com/llamazing/3d_tic-tac-toe/-/blob/6ec1faa5f7e5c3cfbb116e54be4c2df38a5f48d7/data/project_db.dat) explicitly credits Llamazing under CC BY-SA 4.0 for `sprites/board.png` and `sprites/spots.png`. `tilesets/default.tiles.png` has no matching record. The repository GPL text does not establish an unambiguous separate grant for that image in this mixed-license tree.

Ask for an explicit grant covering that bitmap and the intended release. Its simple appearance is not permission. No packaged release was found in the inspected archive. Runtime, computer-opponent behavior, and handheld input remain untested.

## CastleSolarus

Inspected [commit `967d70be96b1a2f37582c2b5ba70c93fd5253d85`](https://gitlab.com/jrdasm/CastleSolarus/-/tree/967d70be96b1a2f37582c2b5ba70c93fd5253d85). The quest declares version 0.2.0, format 2.0, authors Clément and Cyrille Pontvieux, and overall CC BY-SA 4.0. Individual inherited scripts also have GPL grants. Preserve that split rather than relabeling every file.

Of 484 runtime image/font/audio files, 17 initially lacked matching editor records. Twelve are byte-identical to [Antifarea's RPG Sprite Set 1](https://opengameart.org/content/antifareas-rpg-sprite-set-1-enlarged-w-transparent-background-fixed), published under CC BY 3.0. The repository itself contains a link to this exact upstream page. The matching files are the female and male healer, mage, ninja, ranger, townfolk1, and warrior images under `sprites/items/rpgsprites1/`. Record the upstream attribution and grant before packaging.

Five runtime PNGs remain unresolved:

- `sprites/doors/cabin.png` lacks a matching grant.
- `sprites/doors/wooden_castle_door_24px.png` lacks a matching grant.
- `sprites/enemies/ice_boss.png` lacks a matching grant.
- `sprites/enemies/ice_miniboss.png` lacks a matching grant.
- `sprites/menus/outside_world_clouds.png` lacks a matching grant.

The wider inventory includes 29 Aseprite files and seven XCF files. All seven XCFs lack matching file-specific records. The total is 520 media and editable-art files. Two `.url` text shortcuts are separate from that count. An image grant can also cover its editable form, but this audit did not establish those seven mappings.

The source contains unfinished design notes. Its release-date field is blank. This does not prove no usable game exists, but it does not establish a finished campaign or published accepted release. No game was run.

## Solarus Sample Quest

Inspected [commit `3769e10248f7bc5e9bb687c2bd016ab2f3ebd85c`](https://gitlab.com/solarus-games/solarus-sample-quest/-/tree/3769e10248f7bc5e9bb687c2bd016ab2f3ebd85c).

The [license file](https://gitlab.com/solarus-games/solarus-sample-quest/-/blob/3769e10248f7bc5e9bb687c2bd016ab2f3ebd85c/license.txt) grants GPL v3 for Lua scripts and describes mostly CC BY-SA 4.0 data with public-domain exceptions. The actual database maps all 395 inspected media and editable-art files to explicit grants. That count includes 230 PNGs, 133 Oggs, one TTF, one ICO, one ICNS, and 29 Aseprite files. Standard CC BY and CC BY-SA grants and the public-domain entry account for every file in that inventory.

The actual quest description says:

> There is not much to play yet, but any help is appreciated!

It is a good rights baseline, not an established finished starter-pack game. The source says format 2.0 and version 2.0.0. No packaged-release or gameplay acceptance test was performed.

## Why Children of Solarus fails the deeper check

Inspected [commit `ea57c2b76cc43690efa28f222082f9438d4d2e6d`](https://gitlab.com/solarus-games/games/children-of-solarus/-/tree/ea57c2b76cc43690efa28f222082f9438d4d2e6d). Its official page says:

> All proprietary content is replaced by 100% libre content: custom sprites, tilesets, musics, sounds, and so on!

Its [current license](https://gitlab.com/solarus-games/games/children-of-solarus/-/blob/ea57c2b76cc43690efa28f222082f9438d4d2e6d/license.txt) still says:

> Files that include content from Nintendo (to be removed):

That warning alone is not enough to classify every listed file. Eighty-six warning-matched current paths have printed Diarandor CC BY-SA notices, consistent with replacements. Do not call all 118 warning-matched paths Nintendo assets.

However, independent native Pillow decoding verified eight current images with pixels and dimensions identical to entries marked `Proprietary (Fair use)` in [ZSDX commit `e904d7904d74a97a50992b1340431d5d8f341d69`](https://gitlab.com/solarus-games/games/zsdx/-/blob/e904d7904d74a97a50992b1340431d5d8f341d69/data/project_db.dat). Seven reference author fields mention Nintendo. The eighth credits Metallizer.

| Current path under `data/` | Reference author |
|---|---|
| `fonts/green_digits.png` | Nintendo. |
| `fonts/small_green_digits.png` | Nintendo. |
| `fonts/small_white_digits.png` | Nintendo. |
| `fonts/white_digits.png` | Nintendo. |
| `languages/en/images/title_screen_initialization.png` | Metallizer. |
| `sprites/entities/the_end.png` | Nintendo. |
| `sprites/hud/gameover_fade.png` | Nintendo. |
| `sprites/menus/quest_status_dungeons.png` | Nintendo, Newlink. |

Two also have identical whole-file hashes. The other comparisons survive PNG recompression and metadata differences. This is direct image identity, not a filename or visual-resemblance guess. It does not determine whether every simple shape is copyright-protected. No transferable redistribution permission was found.

The full audit inventories 531 media/source-art files. Its final classifications identify 25 further unresolved root exceptions and 38 game-package media paths without a resolved specific grant. Many files do have positive provenance. For example, 136 audio files exactly match the referenced free resource pack. `sounds/magic_bar.ogg` remains unmapped.

The existing CMake glob selects all eight problematic images even if gameplay never loads them. Current English dialogs also retain `Triforce` and `Hyrule`. The official page says `Not released yet`, and both inspected tags and releases API responses are empty. The current changelog says `v1.0.0 (in progress)`.

This is a high-priority exclusion, not a claim that all of its replacement artwork is proprietary. It needs rights, story, packaging, and completion work before reconsideration.

## Closed Circle and The Epic of Den

Closed Circle's actual public v1.2.1 launcher download contains a `data.solarus` matching all 364 source data files at [commit `3ae5bc863b3e74258048e0100fe88623f0968d46`](https://gitlab.com/boaromayo/ld50/-/tree/3ae5bc863b3e74258048e0100fe88623f0968d46). The package adds two `.DS_Store` files. It is a released jam game with ending code, not merely an unfinished template. It was not played through.

The [actual database, line 178](https://gitlab.com/boaromayo/ld50/-/blob/3ae5bc863b3e74258048e0100fe88623f0968d46/data/project_db.dat#L178) says:

> `file{ path = "fonts/square_digits.png", author = "boaromayo", license = "CC BY-NC 4.0" }`

The shipped clock, score, health, pause, and ending code use this font. The broad README claim of GPL and CC BY-SA does not override its NC exception.

The creator also credits WolframTones for intro music. The sole music file instead has a boaromayo CC BY-SA record. [Current WolframTones terms](https://www.wolfram.com/legal/terms/wolfram-tones.html) say:

> Unless otherwise specified, this Site and content presented on this Site are for your personal and noncommercial use.

They also prohibit copying and distribution without a separate grant. The [default paid content agreement](https://www.wolfram.com/legal/agreements/wolfram-tones.html) does not grant redistribution either. The exact historical terms and any separately negotiated permission are unknown. This is a rights gap, not a proven historical breach. Obtain a valid downstream grant or replace the track. Unmapped artwork and one WAV also need reconciliation.

The Epic of Den's public v0.1.2 package identifies itself as `0.1.2 (Pre-alpha Demo)`. Its current creator repository is [GitLab `boaromayo/EoD-noncanon`](https://gitlab.com/boaromayo/EoD-noncanon), not the archived GitHub copy. The inspected tag is [commit `43cf8c4b91f038ce4c61a028bd86fe2ce9cd336e`](https://gitlab.com/boaromayo/EoD-noncanon/-/tree/43cf8c4b91f038ce4c61a028bd86fe2ce9cd336e). The actual released quest differs from that source tag, so source-only clearance would be insufficient.

Its music uses Soundimage's custom grant, not CC BY-NC. Commercial use is permitted subject to its extra content restriction. Its actual in-game credits have the wrong Soundimage domain and omit track attribution and another musician. Two shipped music files lack an established source match. All 94 shipped sounds do match explicitly licensed free-pack files.

Its Lunchtime Doubly So font has a custom commercial-bundling grant. The converter's own page also identifies older game-font bitmap origins. This audit does not settle those underlying rights. Accepting the custom licenses does not turn the pre-alpha demo into a finished game.

## Other discovery leads

The five fetched Solarus Jam creator pages were Monitor Lizard Protocol, Proper Conduct, Nanobot, Crow Jam, and Le Défi de Zeldo: The Beamos Factory. They supplied no detected explicit all-assets license or source link. Free downloads alone do not qualify them. This is insufficient evidence, not proof that their authors prohibit redistribution.

Book of Moon's identity was not established from the search-only lead. It is not a confirmed Solarus candidate. Yarntown remains subject to the separate [asset-provenance hold](solarus-asset-provenance.md). This research did not alter the installed private verification copy.

## Immutable evidence

Archive hashes identify the inspected bytes. GitLab can regenerate archive wrappers, so the commit and individual file hashes remain important. Actual releases are separate artifacts from source snapshots.

| Source or actual packaged artifact | Revision or release | SHA-256 |
|---|---|---|
| Word Breaker source archive | `d3a333d76cb54d5c4e4b86257b166d06595b0cc7` | `bd29e69a3c956e7e4de2e38ea72038efa6d1f9a800171d553966c87248776774` |
| Word Breaker actual `.solarus` | Packaged metadata `0.2` | `f022d1eb5970b5fd7e272b0d363c63e6b218da928bb305205ba36795b41a771f` |
| 3D Tic-Tac-Toe source archive | `6ec1faa5f7e5c3cfbb116e54be4c2df38a5f48d7` | `b97ea50900d18caa914c2d005a24aa27a48de655d3fdbe1fb56e78ed9212e0c0` |
| CastleSolarus source archive | `967d70be96b1a2f37582c2b5ba70c93fd5253d85` | `d4c286854229968471594f808e77641f5d38946b67949be7161cfd60b3e11276` |
| Sample Quest source archive | `3769e10248f7bc5e9bb687c2bd016ab2f3ebd85c` | `a339a546934f1a62cb2521027abeec44b74f55dfde7ed18435de7ee42fc3f8a6` |
| Children of Solarus source archive | `ea57c2b76cc43690efa28f222082f9438d4d2e6d` | `a36fff727878386c92d099c4d306b83e3c0ffd070ad6b3fbee837aa17d9e3b87` |
| Closed Circle actual `data.solarus` | Public launcher v1.2.1 | `d9b3f461e5316f61a8e67599bb5f76036b72551410c7a4bf4e0581df101abc48` |
| The Epic of Den actual `data.solarus` | Public launcher demo v0.1.2 | `40493cd9b1fa5fa6ee6b2de97db143259dc87f2937f5ada5974e480b620b31b7` |
| Antifarea upstream sprite archive | `rpgsprites1_1.zip` | `c487a3284ad31ad027059ef8c32abf52c04cb0ace014b32ca46eaa05c40e6f4a` |

Private evidence includes `catalog-primary/`, `puzzle-inspection/`, `sample-inspection/`, `antifarea-comparison/`, `children-deep/`, and `den-deep/`. These hold primary responses, exact archives, per-file hashes, notices, and comparison results. The two deep delegate reports are `children-deep.md` and `den-deep.md`. They are supporting analysis, not replacements for their cited original files.

Parent verification additionally produced `children-pillow-verification.json`, `candidate-proprietary-pixel-checks.json`, and `comprehensive-license-coverage.json`. Native decoding found no identical proprietary-reference PNGs in Word Breaker's 17 images, Tic-Tac-Toe's three, CastleSolarus's 344, or Sample Quest's 230. This comparison cannot detect cropped, recolored, partial, or otherwise modified copies. It is not an originality certificate.

## Before any starter-pack release

1. Resolve each selected quest's exact permission gaps and custom-license choices. Do not silently remove notices or change license labels.
2. Choose an immutable source and a verified matching quest artifact. Preserve the actual version and hash, not the catalog label alone.
3. Supply complete contributor credits and required license notices. Review corresponding-source, ShareAlike, modification, and downstream-use conditions.
4. Test the selected artifact with Solarus 2.1.4 on x86_64 and ARM64. Separately test handheld controls, audible sound, saving, reloading, and the playable game loop.
5. Keep quests outside the engine/plugin closure and public cache until that content has explicit release approval. This research authorizes no installation or publication.
