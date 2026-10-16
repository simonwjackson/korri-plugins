# Tiny5 public-player validation, 2026-10-16

`unstable-2026-06-18-public2` passed off-device checks on x86_64 and aarch64
Linux. It is not published or installed by this change. No device was contacted.
The implementation and static graphics baseline are commits `2442cc6` and
`e92e81b`. The engine pin remains `882c906b17e35b4105188e6305ae2929aeba30e3`.

Tiny5 replaces common game glyphs. Font IDs, advances, heights and bank layout
stay unchanged. Uncovered glyphs retain ProggyVector. Complete Tiny5 OFL and
ProggyVector notices accompany the generated bank and corresponding source.
This is not a larger-text setting or clearance of user quests.

## Checked outputs

| Architecture | Plugin | Native acceptance check |
| --- | --- | --- |
| x86_64-linux | `/nix/store/g4l7p0nrmh956yi2wpfh36iqldpavak1-korri-plugin` | `/nix/store/01ssd26frz4ihqvaays8a3k2gi8kc2wm-korri-zquest-classic-plugin-check` |
| aarch64-linux | `/nix/store/yqc52bk85hcaxhq32cymly97nry6fl85-korri-plugin` | `/nix/store/x0qh07smcpa1dri3wyyjmi4giammdr2m-korri-zquest-classic-plugin-check` |

| Gate | Result |
| --- | --- |
| Both plugin builds | Passed. ARM compilation ran on the configured native `fuji` builder. Other native build dependencies also used the configured `yari` builder. No target-device build or binfmt emulation was used. |
| Deterministic font generation, both architectures | Passed. Two byte-identical resource sets per architecture; 13,095 exactly fitting Tiny5 glyphs checked against the source pixels. Every original metric is retained, printable ASCII is nonblank, and changed glyph/license inputs are rejected. The font test is now part of the normal Nix check. |
| Native asset/MIDI validators, both architectures | Passed. Real Allegro loader, 61 PCM samples, 101 font slots and metrics, seven silent MIDI timelines and two indexed bitmaps. Native MIDI timers cover the ending and overworld loop bounds. |
| Plugin typecheck and runtime acceptance, both architectures | Passed. Strict TypeScript, manifest, admission, sandboxed launch, native sound initialization, input, screenshots, save/reload, account/rename/release isolation, refusal controls and generated win-room ending. |
| Interpreter replay | Passed on both architectures with static Tiny5 graphics expectations. Before rebaselining, all 100 non-graphics events matched upstream exactly. Only 26 `C <frame> g <hash>` records differ from upstream; metadata is unchanged. The old public1 graphics baseline failed as expected. |
| Production menu-fit preview, x86_64 | Passed. The actual packaged Tiny5 bank rendered all four difficulty lines in The Deep, including the fourth line. Both prior-font and Tiny5 native replays completed 1,500 frames. At frame 1,200, pixels below the HUD were byte-identical. This private test quest and its screenshots are not release inputs. |
| Python lint and syntax | Ruff and `py_compile` passed for the five changed Python files. |
| Nix formatting | `nixfmt --check` passed for the four changed Nix files. |
| Git whitespace check | One known, intended warning: upstream `tiny5-OFL.txt` line 21 contains one trailing space. The pinned license stays byte-exact. No exemption or check change was added. Commit secret-scanning hooks passed. |

## Corresponding source

| Architecture | Source output | Archive SHA-256 |
| --- | --- | --- |
| x86_64-linux | `/nix/store/lgrlp3s8qdc38rbmqa8s4q069c40spzk-zquest-classic-corresponding-source-x86_64-linux` | `2ac2bd57aa96d592ab7750724a6bd7ff49beff0308a019498957bd8cc17f14db` |
| aarch64-linux | `/nix/store/yx34giyjflvzi0nd6ig0kxl73xhwgprq-zquest-classic-corresponding-source-aarch64-linux` | `7a650275aa1fae087b6848b185fc09b09b1e27d86e1d7671f61ed0613ad09fee` |

Both archives were regenerated after rebasing onto current main. Each archive
passed its SHA-256 check, all 3,408 listed source hashes, and the extracted
whole-bundle archive audit. The audit requires the exact Tiny5 table and complete
OFL both at the root and in `recipe/`, plus the generated runtime notice.
The pinned Pillow 12.0.0/FreeType 2.13.3 toolchain regenerated all 14 resource
files byte-for-byte from each archive. Both architectures' generated resources
also match each other byte-for-byte. Extracted standalone player compilation
was not rerun; native plugin builds used the repository recipe.

An initial manual regeneration used the ambient Pillow 12.1.0. Only its
self-reported version in provenance differed. The pinned-toolchain rerun passed
without changing the generator or relaxing the comparison.

## Empty ARM output investigation

The earlier `/tmp` output and command logs no longer exist, so their historical
failure cause cannot be established. The current native ARM package build and
acceptance check both succeeded. The exact command below emitted the nonempty
plugin store path shown above:

```sh
nix build --no-link --print-out-paths --option post-build-hook '' --option secret-key-files '' .#packages.aarch64-linux.korri-plugin-zquest-classic
```

A separate cached run without `--print-out-paths` exited 0 with zero stdout bytes.
Thus an empty redirected stdout file is not a package failure. Missing that flag
is a possible explanation for the old file, not a verified historical cause.
No ARM code fix was needed.

## Reproduction and evidence

Run on build machines, never on a target device:

```sh
nix build --no-link --print-out-paths --option post-build-hook '' --option secret-key-files '' .#packages.x86_64-linux.korri-plugin-zquest-classic .#packages.aarch64-linux.korri-plugin-zquest-classic
nix build --no-link --print-out-paths --option post-build-hook '' --option secret-key-files '' .#checks.x86_64-linux.korri-zquest-classic-plugin .#checks.aarch64-linux.korri-zquest-classic-plugin
nix build --no-link --print-out-paths --option post-build-hook '' --option secret-key-files '' .#packages.x86_64-linux.zquest-classic-source .#packages.aarch64-linux.zquest-classic-source
nix log /nix/store/7v6ar5p615cd43kwhf4z1z6zwpazc6lb-korri-zquest-classic-plugin-check.drv
nix log /nix/store/agzdjy2b90sadxmka9miv012jrwvskqa-korri-zquest-classic-plugin-check.drv
```

Temporary evidence is in `/tmp/zquest-tiny5-finish/`: `final-x86{,-detail}.log`,
`final-arm{,-detail}.log`, `final-source-audit.log`, `rebaseline.log`,
`menu-fit.log`, `font-test.log`, `ruff.log` and `nixfmt.log`. Nix retains the native
check logs until their derivations are collected. Temporary images and scripts
are not durable release evidence.

`require-sigs` remained true. No release keys, cache uploads, signing, public
publication, Git push or device operations ran. Push, approved source/binary
publication and a separately approved idle-device update remain. Publication
must use the exact checked outputs and upload corresponding source before
binary publication. Do not reuse the public1 source tag or claim its device
acceptance applies to public2. Physical input, audible sound and arbitrary
community-quest layouts remain unverified.
