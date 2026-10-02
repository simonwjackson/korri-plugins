# Fable 2 native Linux feasibility

Checked on 2026-10-02 for a Fable 2 plugin in `simonwjackson/korri-plugins`, targeting x86_64 and aarch64 Linux.

No plugin or native package was implemented. No game build, launch, or device test ran. Source inspection establishes the blockers below, not runtime compatibility.

## Findings

There is no verified, ready-to-package solution for both requested architectures. `himdo/Fable-2-Recomp` publishes a Windows release. A separate project, `Oery/fable-ii-recomp`, already targets native Linux x86_64 and reports gameplay, but its full-game and ARM status remain unverified.

| Candidate | Primary evidence | Limit |
|---|---|---|
| [himdo/Fable-2-Recomp](https://github.com/himdo/Fable-2-Recomp/tree/dbcbefcd4ab2df0bc9de500f3f87258f717dd905) | The author reports completing the game. Release 1.4.0 supplies `Fable_2_recomp_v1.4.0_windows.zip`. | Linux and Vulkan remain unchecked in the README. The Linux request is open and labelled `Not Planned For a While`. |
| [Oery/fable-ii-recomp](https://github.com/Oery/fable-ii-recomp/tree/f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092) | The README reports working prologue and post-prologue saves on x86-64 Linux. Later investigation notes record NVIDIA gameplay and save/load tests. | These are upstream reports, not our tests. No full-campaign or Linux ARM acceptance was established. The supplied flake is a development shell, not a game package. |
| [Fable2Recomp/Fable2Recomp](https://github.com/Fable2Recomp/Fable2Recomp/blob/main/README.md) | Its README describes Windows/Linux goals, GOTY TU1, and ReXGlue build instructions. | The README does not establish completed gameplay or tested ARM support. This is a separate project, not the himdo release. |

The earlier Korri inventory, `docs/research/playable-decomp-recomp-games.md`, wrongly treated Fable's Linux support as verified. Do not use that inventory as acceptance evidence.

## himdo source findings

The inspected checkout is `dbcbefcd4ab2df0bc9de500f3f87258f717dd905` on `master`. The release page identifies 1.4.0 with short commit `525365e`; do not confuse that release with the inspected branch tip.

- [Release assets](https://github.com/himdo/Fable-2-Recomp/releases/expanded_assets/1.4.0) list one binary ZIP, named for Windows, plus two source archives. GitHub reports ZIP SHA-256 `158ac30804c4bc05349bef9966486d5b045ecc9c1c7cb676f4f088d193decec7`. The ZIP was not downloaded or executed.
- [README](https://github.com/himdo/Fable-2-Recomp/blob/dbcbefcd4ab2df0bc9de500f3f87258f717dd905/README.md#L3-L26) says the author completed the game but has not completed 100%. Linux builds and Vulkan support remain unfinished. [Issue #7](https://github.com/himdo/Fable-2-Recomp/issues/7) has no Linux delivery date.
- [CMakePresets.json](https://github.com/himdo/Fable-2-Recomp/blob/dbcbefcd4ab2df0bc9de500f3f87258f717dd905/CMakePresets.json) contains both Linux AMD64 and ARM64 presets. Their existence is not evidence of successful builds.
- [src/main.cpp:17](https://github.com/himdo/Fable-2-Recomp/blob/dbcbefcd4ab2df0bc9de500f3f87258f717dd905/src/main.cpp#L17) unconditionally includes the exception probe. [That probe](https://github.com/himdo/Fable-2-Recomp/blob/dbcbefcd4ab2df0bc9de500f3f87258f717dd905/src/diagnostics/fable2_av_probe.h#L39) unconditionally includes `Windows.h` and uses Windows exception APIs and x64 `CONTEXT` registers. This is a concrete source portability blocker, not a measured build failure.
- [CMakeLists.txt:34](https://github.com/himdo/Fable-2-Recomp/blob/dbcbefcd4ab2df0bc9de500f3f87258f717dd905/CMakeLists.txt#L34) requires `generated/rexglue.cmake`. Generated files and `default.xex` are excluded from Git. [build.cmd](https://github.com/himdo/Fable-2-Recomp/blob/dbcbefcd4ab2df0bc9de500f3f87258f717dd905/build.cmd#L130-L132) bootstraps generation with `rexglue.exe`. A Linux build needs a reproducible native SDK/codegen path and an owned, supported XEX.
- [OnConfigurePaths](https://github.com/himdo/Fable-2-Recomp/blob/dbcbefcd4ab2df0bc9de500f3f87258f717dd905/src/core/fable_2_app.h#L452-L497) accepts `--game_data_root`, but unconditionally places saves and caches beside the executable. Other hooks also load writable TOML there. This conflicts with a read-only Nix store. Changing only the working directory does not fix it.
- The SDK gitlink pins `himdo/rexglue-sdk` at `df2a36f97199b8a752bee8ed36a896a2828b5500`. [Runtime documentation](https://github.com/himdo/Fable-2-Recomp/blob/dbcbefcd4ab2df0bc9de500f3f87258f717dd905/docs/RUNTIME_FIXES.md) describes Windows validation and cites an older baseline. Use the actual gitlink and tracked patches when reproducing a build.
- [constants/game_versions.json](https://github.com/himdo/Fable-2-Recomp/blob/dbcbefcd4ab2df0bc9de500f3f87258f717dd905/constants/game_versions.json) owns supported XEX hashes and content requirements. The README's ISO hash is a different identity. Do not invent release identifiers or treat XEX hashes as whole-disc hashes.

[PR #30](https://github.com/himdo/Fable-2-Recomp/pull/30) is an open macOS port proposal. Its author reports Apple Silicon builds and a 45-second Metal startup check, with gameplay and save/load pending. It is a useful portability reference, not Linux ARM acceptance. The maintainer raises review and testing costs and suggests a separate Mac fork.

## Oery source findings

The inspected checkout is `f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092`.

- [flake.nix](https://github.com/Oery/fable-ii-recomp/blob/f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092/flake.nix) exposes only an x86_64 development shell. It selects software Vulkan for headless investigation. That is not a handheld runtime configuration.
- [scripts/build-sdk](https://github.com/Oery/fable-ii-recomp/blob/f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092/scripts/build-sdk) requires SDK revision `c94f5ebdcb3c9d1a460ca48e04f9758448f8d518` and hardcodes `-march=x86-64-v2`. The native Nix CMake preset does the same. ARM needs actual build work, not another advertised platform entry.
- [scripts/codegen](https://github.com/Oery/fable-ii-recomp/blob/f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092/scripts/codegen) checks a specific extracted XEX. [entry-xex.sha256](https://github.com/Oery/fable-ii-recomp/blob/f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092/docs/re/entry-xex.sha256) records `0e1ea96ded3407874cbbb3a9587d79f1340a57a9d1ba2feebcfdbc9ed1e4b6e5`, identified as French GOTY in the investigation notes. Compatibility with another owned dump must be established, not assumed.
- [src/fable_ii_app.h](https://github.com/Oery/fable-ii-recomp/blob/f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092/src/fable_ii_app.h) selects Xenos and leaves SDK path handling intact. This avoids himdo's explicit executable-adjacent save override, but actual SDK paths still need inspection.
- [docs/re/status.md](https://github.com/Oery/fable-ii-recomp/blob/f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092/docs/re/status.md#L1484-L1564) ends with September 12 gameplay, saves, intermittent street transparency, and unresolved performance. Its first summary is stale. The final notes also mention a local SDK commit and dirty instrumentation. Tracked SDK patches exist under `docs/re/patches/`, but a clean-checkout reproduction must prove that all required changes are present.

## Integration and decision boundary

The existing Skate 3 plugin uses Core's `RunnerRecord.releases`, immutable native file registration, and `launch.prepare`. Its declarations perform no effects. Those contracts remain the baseline; no new schema is proposed here.

Neither inspected game checkout has a root redistribution license. That observation does not resolve every source or dependency license. Public source access and upstream binary downloads do not by themselves authorize public cache publication. Keep commercial inputs and generated outputs private pending review.

Recommendation, not an approved decision: attempt a bounded, clean-checkout x86_64 build and gameplay check of Oery's Linux project before writing a new Linux port. The cost is an experimental baseline with narrower compatibility evidence. Success would not establish full-game completion or ARM handheld performance.

The alternative is to port himdo's release to Linux/Vulkan first. It has stronger completion reports, but brings Windows-specific code, writable-path changes, renderer validation, and ongoing fork maintenance. Neither route is a package-only task.

Before implementation, choose the native baseline and locate a matching owned game dump. Then reproduce the build, verify rendering/input/audio/save-load, test aarch64, and only expose working plugin outputs. Keep compilation on build machines and preserve signature and permission checks during any later installation.
