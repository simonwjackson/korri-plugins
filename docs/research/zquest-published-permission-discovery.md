# ZQuest published permission discovery

Checked 2026-10-04 UTC. **The eleven-package audit did not establish that zero redistributable quests exist.** Its zero-clearance result was too narrow to answer availability. The later MIDI proof did not expand that search.

A broader permission-first pass found public CC0 statements covering Mitsukara's own contributions to three completed quests, an AGPLv3 repository containing the exact previously audited Pagan Invaders file, and a cached author statement permitting another quest package with ZC forks. These are real permission leads. They are not five fully cleared, Nintendo-free packages.

No author contact, software builds, asset replacements, native gameplay runs, starter changes, uploads, or device actions occurred in this discovery pass. One existing quest was downloaded privately from its creator's repository to verify its identity. No candidate bytes enter this repository.

## Broad published grants

| Completed quest | Published permission evidence | Scope and remaining cost |
|---|---|---|
| [The Zelda Legend (1984 Arcade), 759](https://www.purezc.net/index.php?page=quests&id=759), Mitsukara | Author explicitly dedicates author-owned content to public domain/CC0 and permits copying, reuse, and editing. | Explicitly excludes Nintendo and otherwise credited material. The listing credits Nintendo music/SFX, Windows 3 sounds, bootleg-game music, and contributed sprites. This miniquest is a cleanup candidate, not an unmodified Nintendo-free game. |
| [Link and Zelda: Panoply of Calatia, 618](https://www.purezc.net/index.php?page=quests&id=618), Mitsukara | Explicitly named in the same retrospective CC0 grant. Its own listing permits alteration and making new/variant quests. | Large franchise-based game with a separate support pack and contributed code. Its author's reported Moosh permission is not an independent inspection of Moosh's grant. Third-party media and underlying franchise content remain separate. |
| [6th Quest Entry - Through the Inverse Glass, 710](https://www.purezc.net/index.php?page=quests&id=710), Mitsukara and Deedee | Explicitly named in the CC0 statement as "6th Quest Contest Entry: Through the Inverse Looking Glass". Its corresponding completed listing identifies Mitsukara and the sixth-quest premise. | Grant covers Mitsukara-owned content, not automatically Deedee's or other contributors' work. The listing identifies a mirrored Zelda 1 overworld, 128 costumes, contributed scripts, and extensive third-party music. Removing music alone is insufficient. |
| [Pagan Invaders, creator repository](https://github.com/ZoriaRPG/PaganInvaders/tree/9ef5923df39d901a2f1fac9d9d47c9a635ce0bf6), ZoriaRPG | Repository carries AGPLv3, script source, and compiled quests. Its `bin/PaganInvaders_Gamma_2.qst` is byte-identical to the audited PureZC 742 file. | Strong project-level licensing evidence absent from the previously inspected listing. The license does not clear independently owned Nintendo music. Contributor and media provenance still need review. Distribution must satisfy applicable copyleft/source conditions. |
| [TLoZ 2.5 Classic + Koten 1.3, 591](https://www.purezc.net/index.php?page=quests&id=591), Anthus | Cached official manifest preserves explicit author permission to package the quest with ZC forks. | Current listing fetch returned 403. Evidence is cached text, not a newly read live page or inspected ZIP. Four first/second-quest variants are one package. Nintendo layouts, story, characters, and `zelda.nsf` prevent treating this as a low-cost Nintendo-free starter. |

Do not collapse creator permission, complete component clearance, and Nintendo-free playability into one result. Ordinary-language grants count. A named standard license is not required for every valid permission. Noncommercial terms alone do not exclude a genuinely noncommercial public pack.

## Mitsukara's explicit grant

The [author-submitted Credits for 759](https://www.purezc.net/index.php?page=quests&id=759) say:

> All elements of this quest that were made by me (but not those owned by Nintendo or those otherwise credited) are public domain (CC0 / no rights reserved).

The next paragraph expressly includes Panoply, the sixth-quest entry, and the author's 2017 ocean sailing demo. The author then says:

> In other words, I'm 100% okay with you using, reusing, copying, or editing any and all of my Zelda Classic fangame content, ideas, scripts, design elements, etc in any way for any of your own purposes.

This is public permission for the author's contributions. It is not merely an unlocked-file observation or permission given to one requester. No author contact is needed to establish this stated permission. No linked CC0 legal instrument was inspected; the ordinary-language grant is also explicit.

The ocean sailing release is a demo, not a fourth complete starter game. Its exact file was not inspected. The explicit exclusions remain in force for every named work.

## Pagan Invaders: licensed repository, matching bytes

The [pinned repository LICENSE](https://github.com/ZoriaRPG/PaganInvaders/blob/9ef5923df39d901a2f1fac9d9d47c9a635ce0bf6/LICENSE) is GNU Affero General Public License version 3. The [pinned tree](https://api.github.com/repos/ZoriaRPG/PaganInvaders/git/trees/9ef5923df39d901a2f1fac9d9d47c9a635ce0bf6?recursive=1) contains `Invaders.zh`, `LICENSE`, and 22 `.qst` files. The 22 files are revisions of one game, not 22 starter candidates.

I downloaded the [pinned Gamma 2 quest](https://raw.githubusercontent.com/ZoriaRPG/PaganInvaders/9ef5923df39d901a2f1fac9d9d47c9a635ce0bf6/bin/PaganInvaders_Gamma_2.qst) and directly compared all bytes against the original audited PureZC download. They are identical:

- File size is 5,247,617 bytes.
- SHA-256 is `53ececcef40eeba2b5f275c309e1a8aa3809a5fe0047920391d9bfe8fb74b690`.
- Git blob identity is `84fffee91aa4c72bae3cc55e6cdc85b7f025204b`.

This is the quest's creator repository, not the engine's GPL being applied to unrelated media. The original report's "no public-pack grant found" concerned the inspected listing. It missed this project-level source.

Do not extend that repository license to a Nintendo composition or assume every credited contributor's rights are established. `Invaders.zh` includes a credited Venrob contribution. Its complete licensing provenance has not been checked. The known embedded Zelda-titled MIDI remains in this exact file. Sound and other media still need inspection.

The previous bounded native observation also remains unchanged: exit 0 over 1,800 replay frames, with 144 `Invalid coordinate for getpixel` diagnostics. No new compatibility or full-playability claim is made here.

## Additional narrower permissions

| Completed quest | Published statement | Verified scope |
|---|---|---|
| [Pacman, 826](https://www.purezc.net/index.php?page=quests&id=826), Captain Crispy | Encourages opening the file, inspecting its operation, and making new mazes. | Editing/maze creation. Public redistribution remains unresolved; Namco content is a separate concern. |
| [The Trouble With Exiled Warriors 2, 386](https://www.purezc.net/index.php?page=quests&id=386), dcsyxx | "The quest file is not passworded so feel free to mess about in ZQuest." | Actual editing invitation. Not an explicit copying grant or third-party media license. |
| [Antiquity, 385](https://www.purezc.net/index.php?page=quests&id=385), Saffith | "The quest is unpassworded, and all scripts used are in the buffer. Feel free to use them." | Script reuse. Not a whole-quest/maps/music grant. |

Do not add these narrower statements to the broad-grant count. A separate original-media lead, [Saint James Place, 825](https://www.purezc.net/index.php?page=quests&id=825), claims sole authorship and self-composed music. That is worth investigating, but it is not a redistribution grant.

## Evidence that does not supply a complete game

[NightmareJames/Open_ZC_Quests](https://github.com/NightmareJames/Open_ZC_Quests) has a GPLv3 license. Its [inspected tree at `4e1b9fd`](https://api.github.com/repos/NightmareJames/Open_ZC_Quests/git/trees/4e1b9fd202231643a4a73df114017a0d94bc4788?recursive=1) contains only `.gitignore`, `LICENSE`, and `README.md`. No quest file is present in that tree. Do not count a repository title and license as an available game.

The Rebirth contest's public invitation to modify an incomplete base does not supply a complete starter quest. The known BotB policy remains a noncommercial permission lead, but the guest-blocked packages have not received a binary audit. These are not grounds for a universal negative.

## Coverage and private receipts

This pass changes the evidence, not the eligibility criteria:

- The delegated investigator screened permission keywords across the cached 795-quest manifest. That is text screening, not 795 package audits.
- The investigator attempted 16 new listing/release/thread pages. Twelve of 13 quest listings succeeded; Anthus 591 returned 403. Three forum pages were also read. Navigation and raw duplicates made 21 fetch calls in that investigation.
- The parent used 12 serialized web searches and three official GitHub repository-metadata queries. Those returned 52, 3, and 4 rows with overlap. Metadata discovery is not a deep license audit of every repository.
- The parent inspected the two repository trees and relevant primary license/source pages. It preserved Mitsukara and Panoply pages and privately fetched the pinned Pagan quest to verify the exact bytes.

Private discovery notes are `/tmp/zquest-broader-purezc-permissions.md`. GitHub discovery responses are under `/tmp/zquest-broader-github-permissions/`. Original HTTP bodies and SHA-256 receipts are under `/tmp/zquest-broader-primary-evidence/`, mode 0700. The local Nix-shebang helpers are `/tmp/zquest-license-repository-search.py` and `/tmp/zquest-broader-primary-evidence.py`.

The live Mitsukara grant HTML SHA-256 is `1b4382631e4307a5bbe144846ea8a4ca1743d399e28cfb05627c4b2036e7d2c3`. The pinned Pagan LICENSE SHA-256 is `8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef`. The cached official manifest's SHA-256 remains `3ebbfe892d9661abb8567417b104f4edfe67c223c4a9e350e80f284af8554d0d`.

These receipts stay private. Raw pages contain session links and the evidence directory contains a quest binary. `/tmp` is not durable storage.

## Decision

Continue permission-first discovery and cleanup assessment. **Existing public permission is available; a ready-to-publish Nintendo-free package is not yet verified.** Do not repeat the eleven-package result as a claim of catalog-wide absence.

My next cleanup preference is Pagan Invaders, followed by the small 1984 Arcade quest. This is a judgement, not a proved feasibility ranking. Cost: Pagan still needs complete media/contributor checks and gameplay investigation; the arcade quest requires removing franchise content and excluded third-party media. No finished replacement assets or publication are approved by this note.
