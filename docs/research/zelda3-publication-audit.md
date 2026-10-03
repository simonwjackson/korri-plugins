# Zelda3 publication audit

Date: 2026-10-03.

## Answer and status

This audit cannot establish Nintendo clearance for the current binary. It omits the ROM and runtime-extracted `zelda3_assets.dat`. However, it embeds game-specific tilemap tables that match the original ROM exactly. This is a packaging concern, not proof of infringement.

The Korri integration source and recipes are already published in `simonwjackson/korri-plugins`, through commit `6affb39`. That repository does not contain the upstream engine source or compiled executable. The Nix recipe fetches the pinned upstream source. Signed binary delivery so far is private.

The owner requested a copyright check and publication. This audit does not upload public binaries, create releases, change signing keys or operate devices. Public binary publication awaits an owner decision on these findings. Existing source publication does not clear a future binary release.

## Exact artifacts

| Artifact | Inspected value |
|---|---|
| Upstream source | `snesrev/zelda3`, revision `fbbb3f967a51fafe642e6140d0753979e73b4090`. The inspected checkout has no changes. |
| ARM plugin | `/nix/store/ihc0ln79i1ii76v455ny7jj9jl5m93k1-korri-plugin`. |
| ARM executable | `/nix/store/xw2rzfjzzb5mnj9did344rq62lwgm4qg-zelda3-unstable-2023-08-17/libexec/zelda3`. |
| ARM executable SHA-256 | `eaa8d961397ba1c18d298dc1d5606adc1c2bd90a19717177c60887f572c2114e`. |
| x86_64 plugin | `/nix/store/d2gzpsp6bcr0dafwwkp84r2w32pz3c1y-korri-plugin`. |
| x86_64 executable | `/nix/store/q9w6vlz9i034jass90w4x7qfxnfsm9ir-zelda3-unstable-2023-08-17/libexec/zelda3`. |
| x86_64 executable SHA-256 | `69086610cdace64fa0c035e4df9c33602cd26be5f2ebf83f146c2d404d490e8b`. |
| Supported owned ROM SHA-256 | `66871d66be19ad2c34c927d6b14cd8eb6fc3181965b6e517cb361f7316009cfb`. |

The audit read both actual packaged ELFs, not a summary or substitute executable. It used ROM bytes privately for comparison. This report contains lengths, hashes and offsets, not copied ROM data.

## Verified packaging facts

[`package.nix`](../../plugins/zelda3/package.nix) selects the C-only `zelda3` Make target. It does not run the default asset-extraction target. The owned ROM is not a Nix build input. The launcher extracts the main asset bundle locally at runtime. The package retains the upstream MIT notice and bundled Opus BSD notice.

The native output also ships the INI, Python extraction modules, `assets/palette_usage.bin`, and `other/3x5_font.png`. Calling them extraction tools does not establish their provenance. [`sprite_sheets.py`](https://github.com/snesrev/zelda3/blob/fbbb3f967a51fafe642e6140d0753979e73b4090/assets/sprite_sheets.py) uses the font for annotations and the palette metadata for HUD icon palettes. The font's use does not establish its authorship. [`text_compression.py`](https://github.com/snesrev/zelda3/blob/fbbb3f967a51fafe642e6140d0753979e73b4090/assets/text_compression.py) also contains the game's text-compression alphabets and dictionaries.

The [upstream README](https://github.com/snesrev/zelda3/blob/fbbb3f967a51fafe642e6140d0753979e73b4090/README.md) describes a "reverse engineered clone". It acknowledges help from a Zelda disassembly and describes comparison against the original machine code. Those statements do not document clean-room provenance. The [MIT license](https://github.com/snesrev/zelda3/blob/fbbb3f967a51fafe642e6140d0753979e73b4090/LICENSE.txt) names snesrev and elzo_d, not Nintendo.

The supported statement is "no ROM or runtime-extracted asset bundle is shipped". The evidence does not support "no Nintendo-derived data or expression is shipped".

## ROM-matching compiled tables

The C source defines four `kAttract_Legendgraphics_*` arrays. [`Attract_BuildNextImageTileMap`](https://github.com/snesrev/zelda3/blob/fbbb3f967a51fafe642e6140d0753979e73b4090/src/attract.c#L954-L966) copies them into game RAM for the opening sequence. The executable embeds them, rather than reading them exclusively from the player's extracted asset bundle.

A local Nix-shebang script parsed those arrays and compared each complete byte sequence against the owner's supported ROM. It then searched both packaged ELFs. All four sequences matched the ROM and both executables.

| C array and definition line | Bytes | ROM offset | ARM ELF offset | x86_64 ELF offset |
|---|---:|---:|---:|---:|
| `kAttract_Legendgraphics_0`, line 46 | 158 | 424642 | 1131008 | 1043136 |
| `kAttract_Legendgraphics_1`, line 58 | 238 | 424799 | 1130768 | 1042880 |
| `kAttract_Legendgraphics_2`, line 75 | 200 | 425036 | 1130560 | 1042656 |
| `kAttract_Legendgraphics_3`, line 90 | 266 | 425235 | 1130288 | 1042368 |

[Source definitions](https://github.com/snesrev/zelda3/blob/fbbb3f967a51fafe642e6140d0753979e73b4090/src/attract.c#L46-L108). Offsets are decimal file offsets, not SNES CPU addresses. Adjacent ROM sequences overlap by one byte. The table lengths therefore do not count unique copied bytes.

Private evidence remains at `/tmp/zelda3-compiled-constant-audit.py` and `/tmp/zelda3-compiled-constant-audit.json`. The script read the supported 1,048,576-byte ROM and both exact ELF hashes above. Its output contains no original ROM byte sequence. This is a four-table spot check, not a complete provenance audit of the code, constants or dependencies.

The matches prove shared game-specific data. They do not prove the authors' acquisition method, protectability, applicable exceptions or a court's conclusion. Removing these four tables alone would not settle the remaining code and provenance questions.

## Legal boundary

This section uses the US framework. It is not a legal opinion or an assessment of every jurisdiction.

[17 USC 102(b)](https://www.copyright.gov/title17/92chap1.html#102) excludes ideas, processes, systems and methods of operation from copyright. Implementing the same behavior through reverse engineering is therefore not automatically infringement.

[Sections 101 and 106](https://www.copyright.gov/title17/92chap1.html#106) address derivative works, reproduction and public distribution. [Section 103(b)](https://www.copyright.gov/title17/92chap1.html#103) limits an author's copyright in a derivative work to contributed material. It does not grant rights in underlying preexisting material. The upstream MIT grant does not establish permission over any Nintendo material the authors do not own.

[Section 107](https://www.copyright.gov/title17/92chap1.html#107) requires a case-specific fair-use assessment. Cartridge ownership, user-supplied ROMs, free distribution and an MIT notice do not independently settle public redistribution rights. The audit does not conclude that reverse engineering is unlawful or that Nintendo has proven infringement.

## Recommendation and cost

I recommend keeping the integration source published and the current binaries private pending a provenance and legal assessment. The cost is no public prebuilt Zelda3 download from this publisher yet. Source-only distribution also does not settle the upstream engine's rights.

If the owner later authorizes binaries, use the existing signed Nix-cache publisher with freshly staged exact closures for both architectures. Do not upload a private device cache. Exclude ROMs, extracted assets, saves, screenshots and unrelated plugins. Keep notices, signature verification, append-only metadata and exact revision/path evidence. Device trust and installation approval remain separate decisions.

`zelda3.yml` is check-only. A passing build or signed NAR proves neither Nintendo permission nor public-release completion. This audit adds no publication workflow or rights-cleared package variant. Documentation-only edits leave both plugin output paths unchanged.
