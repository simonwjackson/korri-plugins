# No-contact ZQuest cleanup proof

Verified 2026-10-04 UTC. **Block Smasher can be saved, reloaded, and edited to remove one embedded MIDI slot without changing any other decoded section.** Nine checks and six native replay runs passed through Nix apps. The checks cover seven input/editing cases, native result validation, and timeout cleanup.

This is a private format-editing proof, not a cleaned public starter. Six embedded MIDIs remain. Graphics, sounds, text, fonts, scripts, maps, and their rights have not passed a complete audit. Zero whole quests are cleared for publication by this work.

No authors were contacted. No candidate bytes were committed or published. No starter-pack, Tiny5, device, or running-game changes occurred. The work adds off-device research tools only.

## Approved boundary

Use existing public permission evidence. Do not contact authors or ask them for clarification. Do not silently reinterpret an ambiguous grant as a standard license. If the evidence cannot support publication, keep the candidate private or exclude it.

The earlier report's author-contact recommendation is superseded. The [initial rights audit](zquest-starter-quest-rights.md) still records the media blockers.

## Existing public permission evidence

The [Block Smasher listing](https://www.purezc.net/index.php?page=quests&id=422) explicitly permits editing. The finished ZIP supplies the quest and `BlockSmasher.z`.

The [author's announcement](https://www.purezc.net/forums/index.php?showtopic=60275), post 11, 2013-08-07 12:44 PM, contains stronger wording:

> I will at any time leave the quest unpassworded, so anyone can do whatever they want with it

This is a public grant to "anyone", not a private response to one requester. The page identifies the creator as Avaro and its edit metadata as Avataro. Post 1 was updated to link the finished release. Post 14 expressly says all the music comes from Donkey Kong games.

| Question | Evidence and confidence |
|---|---|
| Is editing authorized? | Verified. The listing expressly invites edits, and the author supplies the broader public statement. |
| Does the broader statement support sharing a modified author-owned quest? | Inferred. That is a reasonable literal reading of "anyone" and "whatever", but redistribution is not expressly named. |
| Is it a named standard license with known conditions? | No standard license was found in the inspected sources. Do not invent one. |
| Does the author grant cover Nintendo music or independently owned contributions? | Not established. A creator cannot grant rights they do not own. |
| Is the separately supplied `.z` file expressly included in the grant? | Unresolved. The statement names the questfile, not the separate source file. |
| Is the current full package cleared? | No. Permission for separable author-owned logic does not clear the bundled media. |

The broader statement improves the no-contact candidate assessment. It does not establish a complete rights chain. It is not necessary to reject ordinary-language permission merely because it is not a Creative Commons label.

### BotB follow-up

The [BotB policy](https://battleofthebits.com/lyceum/View/BotB+CC+License) asserts mandatory Attribution NonCommercial ShareAlike licensing for submitted entries. Noncommercial terms do not automatically exclude a public pack. The exact individual version and contribution scope remain unresolved.

The normal public API returned six entry records. For each entry, both its supplied download URL and supplied file-view URL returned HTTP 403. All twelve response bodies explicitly request login and state that guests are blocked. No challenge or authentication restriction was bypassed.

| Entry | Official public record | File and individual terms result |
|---|---|---|
| BlockStationary 81111 | [API](https://battleofthebits.com/api/v1/entry/load/81111) | Metadata accessible. Quest bytes and individual license unavailable to this guest check. |
| ephemeral visit 81109 | [API](https://battleofthebits.com/api/v1/entry/load/81109) | Same result. |
| A Dream, An Interlude 81116 | [API](https://battleofthebits.com/api/v1/entry/load/81116) | Same result. |
| Into the Forest 81107 | [API](https://battleofthebits.com/api/v1/entry/load/81107) | Same result. API credits `kleeder`. |
| Ghosts of Cypress 81108 | [API](https://battleofthebits.com/api/v1/entry/load/81108) | Same result. |
| The Three Trials 72765 | [API](https://battleofthebits.com/api/v1/entry/load/72765) | ZIP metadata accessible. ZIP members and individual terms uninspected. |

No package-level license was read. This does not mean that none exists. Private, legitimately obtained files and entry-license pages can reopen this route without author contact. Do not send login credentials or bypass the guest restriction.

## Format-editing proof

The tool uses [zquest-data](https://github.com/connorjclark/zquest-data) at `a52b5d19cb73439137ef281110c8831774000c5e`. Its native producer schema already describes MIDI section version 4 as a 252-slot table with a 32-byte presence mask. No new quest format was invented.

The tool reads the header and MIDI section only. It verifies an unchanged MIDI serialization before editing. All other sections remain raw bytes, so unsupported sections cannot be silently rewritten.

The proof performs these checks:

1. Verify the source against the downloaded quest's SHA-256 receipt.
2. Encode the unchanged decoded payload, reload it, and compare every decoded byte.
3. Set MIDI slot 0 to absent without shifting any remaining slot.
4. Serialize that one section with the upstream serializer and reload the result.
5. Verify that only `MIDI` changed, all remaining MIDI objects are identical, and the original file stayed unchanged.

The saved files use the upstream encoder's unencrypted compressed PACKFILE mode. Their outer-file hashes therefore differ from the legacy encoded input. The unchanged copy's decoded payload is identical. This is not an official ZQuest editor `-copy-qst` test.

| Artifact | SHA-256 |
|---|---|
| Original `Block_Smasher.qst` | `2fb1fc6d0a8e117fdf31f6fc92ba4feb980960e7f053e832010b48b53aef4f44` |
| Original decoded payload | `956062eed044dfc6dbac2a723ab05c5bcd875911f9b0df930e20c0a6681e8625` |
| Unchanged `roundtrip.qst` | `a206550883d5911c8f36e2e130e3f00275b12658fa73141c7e724fcdfa746cd4` |
| `slot-0-removed.qst` | `feeb5bb8158248eaf3ce0edddc45335e6e5f998a4269f00b0e9cd75c16bc9e21` |

Slot 0 is named `world1`; its MIDI metadata identifies Donkey Kong Country 2's "Brambles". The populated slot list changes from `[0, 1, 2, 3, 4, 5, 6]` to `[1, 2, 3, 4, 5, 6]`. The 53,712-byte MIDI record is removed. The other 24 complete section records are byte-identical. This is removal of actual MIDI bytes, not deletion of a title or disabling playback.

Outputs use private directories and are refused inside Git checkouts. Existing output directories, source-containing output locations, bad input hashes, empty MIDI slots, invalid slot numbers, and unsupported MIDI versions are rejected. Quest inputs and outputs are runtime arguments, never Nix derivation inputs.

## Native verification

The comparison uses the cleaned x86 `public1` player pinned in the [initial audit](zquest-starter-quest-rights.md). Its store path is:

`/nix/store/j07fyph19n8i524nwqps4hdir9q31fmf-zquest-classic-unstable-2026-06-18-public1`

The existing production launcher selects software MIDI through `ALLEGRO`. The comparison uses its existing configuration:

`/nix/store/g2cf5nqcsf88pbv0fhbl0qn6n9q49qq8-zquest-classic-software-midi/share/zquestclassic-audio`

Each variant runs in a new directory and an isolated network namespace. Xvfb provides the display. The harness configures a private PulseAudio null sink and points `PULSE_SERVER` at it. No audio recording or stream-routing receipt was inspected. No target device or production session is started or stopped.

| Check | Original | Unchanged roundtrip | Slot-0 removal |
|---|---|---|---|
| 6,000-frame headless replay | Exit 0. | Exit 0. | Exit 0. |
| Logical image pixels at frames 300, 900, 2,400, 5,500 | Reference hashes. | Identical hashes at all four samples. | Identical hashes at all four samples. |
| 600-frame windowed replay with audio enabled | Exit 0. | Exit 0. | Exit 0. |
| Sound initialization | Log says `Initializing sound driver... OK`. | Same result. | Same result. |
| Logical image pixels at frames 300 and 500 | Reference hashes. | Identical hashes at both samples. | Identical hashes at both samples. |

The harness reads the native `proof.zplay.result.txt` output and requires `success: true`, `stopped: true`, and the requested final `frame`. The report records achieved frames, not only requested length.

These checks establish bounded load, replay, rendering, and audio-initialization behavior. They do not prove audible silence, correct replacement music, completion, every level, ARM compatibility, or every controller action. Screenshots show ball movement in the first level; they do not establish level completion or score progression.

This harness trusts the supplied player, reader, and private input. Network isolation is not a hostile-input filesystem or device sandbox. It inherits the host filesystem and environment.

The runtime harness gives each replay its own process group. It kills that group's remaining descendants on timeout or wrapper exit. The SIGTERM handler runs the same scoped cleanup. It never signals a production game's process group.

All six runs log an attempted quest-catalog fetch followed by a DNS failure. The network namespace prevents external requests or uploads. The runs are not diagnostic-free. No player upload-policy fix is included in this slice.

The first audio probe omitted `ALLEGRO` and crashed before loading the unmodified quest while opening the ALSA sequencer. Restoring the production launcher's setting fixed the harness. The player and quest logic were not patched to hide that failure.

## Reproduce on a build host

Run these apps from `korri-plugins`, never from a target device. Provide the already built private reader at the exact revision above. The tools do not download quest files or build that reader automatically. Its compiled Python extension must match the interpreter ABI.

The following commands record the verified run. Use fresh output directories when repeating them. Existing directories are deliberately refused.

```sh
nix run --option builders '' --option post-build-hook '' .#zquest-midi-proof -- \
  --input /tmp/zquest-starter-research-evidence/422/archive/Block_Smasher.qst \
  --expected-sha256 2fb1fc6d0a8e117fdf31f6fc92ba4feb980960e7f053e832010b48b53aef4f44 \
  --reader-root /tmp/zquest-starter-data-reader \
  --output-dir /tmp/zquest-block-smasher-midi-proof-app \
  --remove-slot 0

nix run --option builders '' --option post-build-hook '' .#zquest-midi-proof-test -- \
  --input /tmp/zquest-starter-research-evidence/422/archive/Block_Smasher.qst \
  --expected-sha256 2fb1fc6d0a8e117fdf31f6fc92ba4feb980960e7f053e832010b48b53aef4f44 \
  --reader-root /tmp/zquest-starter-data-reader

nix run --option builders '' --option post-build-hook '' .#zquest-midi-proof-runtime -- \
  --engine /nix/store/j07fyph19n8i524nwqps4hdir9q31fmf-zquest-classic-unstable-2026-06-18-public1 \
  --audio /nix/store/g2cf5nqcsf88pbv0fhbl0qn6n9q49qq8-zquest-classic-software-midi/share/zquestclassic-audio \
  --original /tmp/zquest-starter-research-evidence/422/archive/Block_Smasher.qst \
  --expected-sha256 2fb1fc6d0a8e117fdf31f6fc92ba4feb980960e7f053e832010b48b53aef4f44 \
  --roundtrip /tmp/zquest-block-smasher-midi-proof-app/roundtrip.qst \
  --edited /tmp/zquest-block-smasher-midi-proof-app/slot-0-removed.qst \
  --output-dir /tmp/zquest-block-smasher-native-proof-app-scoped
```

Seven integration checks use a real privately supplied quest. They cover the roundtrip/edit invariant and six rejection or preservation cases. An eighth check uses the observed native result fields to reject early stops, failure, and missing counters. A ninth uses an owned hanging script to verify that timeout cleanup kills descendants, not only the direct wrapper process. No copyrighted fixture is shipped in the repository or Nix store. The three apps are listed by `nix run .#help`.

Private evidence:

- `/tmp/zquest-block-smasher-midi-proof-app/receipt.txt` records source/output hashes and every before/after section hash.
- `/tmp/zquest-block-smasher-native-proof-app-scoped/native-results.json` records the six native exits, frame counts, sampled pixel hashes, diagnostics, and log paths.
- `/tmp/zquest-no-contact-permissions-result.md` records the public-grant search and its interpretation limits.
- `/tmp/zquest-no-contact-archive-permissions.md` records the twelve guest-blocked links and API results.
- `/tmp/zquest-no-contact-archive-evidence/` contains private API and failure receipts. Response headers contain guest cookies and must not be published.

`/tmp` is not durable storage. Preserve private evidence outside Git before continuing the full audit.

## Next bounded slice

The format-writing risk is reduced for this exact MIDI case. The next cleanup slice can remove the other unresolved embedded tracks and test every referenced track change. It still needs an allowlist audit for graphics, sounds, fonts, text, maps, scripts, and all external files.

Do not label this edited quest Nintendo-free or ready for the starter pack. Publication remains gated on complete media rights and a defensible reading of existing public grants. No author-contact route is part of that work.
