# Additional Solarus quest candidates

Research date: 2026-10-03 UTC.

**Perlshaw's Problems is an additional positive licensing candidate.** Its inspected source has explicit standard-license or public-domain grants for all 310 image, font, audio, and editable-art files. That is permission evidence, not a claim that its current source is packaged correctly or its short game is complete and tested.

A broader repository search also found Blue Isle and Vegan on a Desert Island. Blue Isle has four runtime image-license gaps. Vegan on a Desert Island has a positive explicit asset-license statement, but its creator calls it unfinished.

This follows [the first quest audit](solarus-starter-quest-licensing.md). No game was installed, executed, built, modified, or published. No device was accessed. All downloaded source and media remain private under `/tmp/solarus-quest-research/`.

## New leads and practical limits

| Quest | Actual inspected licensing evidence | Remaining cost or limitation |
|---|---|---|
| [Perlshaw's Problems](https://github.com/AgentNintaku/perlshaws-problems) | GPL v3 repository license. Every one of 310 media/source-art files matches a CC BY, CC BY-SA, or public-domain record. | Best additional candidate for verification. The author calls it a short test game. Confirm packaging, actual content, completion, controls, and saving before bundling it. |
| [Blue Isle](https://gitlab.com/Cluedrew/blue-isle) | Explicit grants cover 317 of 324 media/source-art files. Most graphics and audio are CC BY-SA 4.0. Its additional font has an OFL record. | Ask the creator to license four runtime PNGs and three editable counterparts. The inspected quest has four registered maps, no version, and no release date. Completion is unverified. |
| [Vegan on a Desert Island](https://gitlab.com/voadi/voadi) | The creator explicitly declares GPL software and free-culture CC game assets. The actual database includes CC BY, CC BY-SA, and CC0 grants. | Licensing lead for a development game, not a finished-game recommendation. This pass inspected notices and metadata, not every media byte or a release artifact. |
| [The Mystery of Tama Village](https://github.com/ekureina/TheMysteryOfTamaVillage) | A real GPL repository exists, but its asset provenance is not explicitly mapped. | The accessible version has one room and empty map callbacks. It does not establish the finished mystery described in its README. Do not count it as a finished candidate. |

**Opinion:** verify Perlshaw's Problems next. It adds an adventure to the puzzle-heavy shortlist without introducing Word Breaker's custom music restrictions. The cost is its small test-game scope and uncertain source layout. This is not yet a third finished, accepted starter-pack game.

## Perlshaw's Problems

Inspected current [commit `cdc5ea95d84be7051da08a1c770e511648aae1b0`](https://github.com/AgentNintaku/perlshaws-problems/tree/cdc5ea95d84be7051da08a1c770e511648aae1b0), including the complete fixed-revision archive, root README and GPL text, quest metadata, per-file database, and all identified media bytes.

The [README](https://github.com/AgentNintaku/perlshaws-problems/blob/cdc5ea95d84be7051da08a1c770e511648aae1b0/README.md) says:

> Perlshaw's Problems is a short test game developed using the Solarus game engine.

The [actual quest metadata](https://github.com/AgentNintaku/perlshaws-problems/blob/cdc5ea95d84be7051da08a1c770e511648aae1b0/quest.dat) identifies version `0.8`, format `1.6`, author `Nintaku`, and a blank release date. Its description says:

> The town of Perlshaw has its share of troubles, and it's up to Eldran to solve them!

The [actual database](https://github.com/AgentNintaku/perlshaws-problems/blob/cdc5ea95d84be7051da08a1c770e511648aae1b0/project_db.dat) supplies these media grants:

| Grant in the source metadata | Files |
|---|---:|
| Public domain | 1 |
| CC BY 4.0 | 2 |
| CC BY-SA 4.0 | 301 |
| CC-BY-SA 4.0, the same license with different punctuation | 6 |
| **Total** | **310** |

The inventory consists of 148 PNGs, one TTF, 132 Oggs, and 29 Aseprite files. No file in this inventory lacks a matching license record. Specific contributors include Diarandor for hero artwork, Eduardo Dueñas for music, usr_share and Christopho for the bitmap font, and Jeti for Enter Command.

Native Pillow decoding found no PNG identical to the pinned ZSDX assets explicitly marked proprietary. This is a limited exact-image comparison. It cannot establish originality or detect cropped, recolored, or partial copies. The positive permission evidence comes from the actual file grants, not from the absence of a match.

The repository keeps `quest.dat` and `project_db.dat` at its root, while `main.lua` and the media are under `data/`. The database's asset paths are relative to that data directory. The audit maps those existing paths explicitly. It does not move files or alter the runtime layout. The creator's README instructs players to extract `data/`, so the intended native launch layout needs verification. This audit did not download a separately packaged release or execute the quest.

The root GPL and asset grants are commercially compatible. Preserve contributor credits, license notices, modification notices, and applicable source obligations. This is not a complete GPL compliance or underlying-rights certification.

## Blue Isle

Inspected [commit `1b55fb3f1a80a669ddfb5e2bf8b0737b50868881`](https://gitlab.com/Cluedrew/blue-isle/-/tree/1b55fb3f1a80a669ddfb5e2bf8b0737b50868881), including the complete source archive and actual metadata.

The [quest file](https://gitlab.com/Cluedrew/blue-isle/-/blob/1b55fb3f1a80a669ddfb5e2bf8b0737b50868881/data/quest.dat) describes a small island-exploration game by Cluedrew Kenfar Ink, using Solarus 1.6. Its version and release-date fields are empty. The database registers four maps.

The [database](https://gitlab.com/Cluedrew/blue-isle/-/blob/1b55fb3f1a80a669ddfb5e2bf8b0737b50868881/data/project_db.dat) has extensive explicit standard grants. Its fonts include public-domain `8_bit.png`, Jeti's CC BY 4.0 Enter Command, and Comic Neue Angular Bold under OFL 1.1. Script records include MIT and GPL grants.

Of 324 identified media/source-art files, 317 have an explicit matching grant. Four runtime PNGs remain without an established grant:

- `sprites/dialog/e-box.png` needs a license clarification.
- `sprites/doors/lab-door-1.png` needs a license clarification.
- `tilesets/abandoned-lab.tiles.png` needs a license clarification.
- `tilesets/post-0.tiles.png` needs a license clarification.

Three Aseprite counterparts are also unresolved: `sprites/dialog/e-box.aseprite`, `tilesets/abandoned-lab.aseprite`, and `tilesets/post-0.aseprite`. Some records name the creator but omit the license. An author field alone is not redistribution permission.

No current PNG matched the same explicitly proprietary ZSDX reference set. That does not clear the seven documentation gaps. No gameplay or completion test was performed.

## Vegan on a Desert Island

Inspected [commit `197105cb25eb0de1b7e6d4acc25303ece1be479f`](https://gitlab.com/voadi/voadi/-/tree/197105cb25eb0de1b7e6d4acc25303ece1be479f). This was a notice-and-metadata pass, not a full archive/media audit.

The [creator's README](https://gitlab.com/voadi/voadi/-/blob/197105cb25eb0de1b7e6d4acc25303ece1be479f/README.md) expressly says:

> Vegan on a Desert Island is Free Software, licensed under GPL-3.0.

> Game assets are licensed under a Free Culture Approved Creative Commons license.

The [actual resource database](https://gitlab.com/voadi/voadi/-/blob/197105cb25eb0de1b7e6d4acc25303ece1be479f/data/project_db.dat) specifies CC BY 3.0, CC BY 4.0, CC BY-SA 4.0, and CC0 grants, alongside GPL script records. These statements are a real asset-license lead, not just the engine's license.

The same README says:

> Vegan on a Desert Island is a work-in-progress 2D top-down adventure game for Linux, MacOS and Windows.

Its download instructions explicitly call the development version incomplete. The actual quest says version `0.3`, format `1.6`, and no release date. The premise is an original adventure about escaping an island without coercing its animals.

The linked credits wiki returned only a client-rendered page shell through this fetch. Do not claim that the complete wiki attribution list was inspected. A full file-level audit and release/completion check are still needed if a development-game slot is acceptable.

## Tama and other stops

The accessible [Tama commit `9a3526ce8a20727590cea94c210cafd6c70c3675`](https://github.com/ekureina/TheMysteryOfTamaVillage/tree/9a3526ce8a20727590cea94c210cafd6c70c3675) has one small map, empty map-event bodies, version 0.1, and no specific asset-license records. The supplied GitLab project could not be retrieved. Its repository description was a discovery lead, not proof of a released mystery game.

Creator-related [No Rest For Heroes](https://github.com/Renkineko/solarus-nrfh) expressly identifies Nintendo and Squaresoft/Square-Enix content and says it is not a real game. It is a design-test quest, not another cleared title.

[Hallow's Eve](https://maxatrillionator.itch.io/hallows-eve) is a released game. However, its [creator-linked source at `4e459a52516b39a5ecc87f4c5f429d520f20ec35`](https://gitlab.com/maxmraz/hallows-eve-open-code/-/tree/4e459a52516b39a5ecc87f4c5f429d520f20ec35) explicitly marks essential dialogue and maps `All Rights Reserved`. The newer public v1.2.0 release was not inspected in this pass. Separate whole-game permission is required before recommending redistribution.

## Evidence and verification

| Inspected artifact | SHA-256 |
|---|---|
| Perlshaw's Problems fixed-commit source archive | `ff05a636102c4bfc874c7ecf6ee449a71bc7afbe6dec0a936f4e7217d39b79b3` |
| Perlshaw's Problems actual `project_db.dat` | `37a0dcbec40e0bd0e5ce1e141578c07c81d7ec78756247f31751479c3ece3f6a` |
| Blue Isle fixed-commit source archive | `2f5ff290df4067bbdaa64cccb06fcdcfbcbf6eb3684eb6687e4fcd07e198dc69` |
| Blue Isle actual `project_db.dat` | `e8894d00687e6099e38ae1520a7d159bb973f9a47295fa25f3f7a4422141b4f2` |
| VOADI actual README | `77b4965f3913c92c275bfebead3c57a7d1753a6f1a138dcfbb5da54174da963f` |
| VOADI actual `project_db.dat` | `e4375be7c0299d3ab8e2e84c74c0d7aa67d2e222c2b9ef2853824fe81dccb402` |

Private evidence is in `more-discovery/`, `more-primary/`, `more-archive/`, and `more-tama/` under `/tmp/solarus-quest-research/`. The archive audits record every identified asset's file hash and matched notice. Native image comparison uses ZSDX commit `e904d7904d74a97a50992b1340431d5d8f341d69`, the same reference as the first audit.

The initial Perlshaw coverage attempt used repository-relative paths against data-relative editor records. It incorrectly reported all 310 files unmapped. Correcting only the audit's path mapping recovered all 310 explicit grants. The source and media were unchanged. Do not use that discarded attempt as evidence of missing licenses.

All scripts are local Nix-shebang research tools. Only those scripts ran. Downloaded project code did not run. These findings do not authorize installation, source-layout changes, or public packaging.
