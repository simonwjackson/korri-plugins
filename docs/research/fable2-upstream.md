# Fable 2 native Linux feasibility

Checked on 2026-10-02 for a Fable 2 plugin in `simonwjackson/korri-plugins`, targeting x86_64 and aarch64 Linux.

Plugin integration is now under verification. Native x86_64 validation covers menu navigation, character selection, new-game save creation, save reload into Bowerstone Old Town, stick-controlled movement, and nonzero audio output. Full-campaign completion, physical-controller/device acceptance and ARM gameplay remain unverified. The sections below distinguish source findings from subsequent runtime tests.

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

Approved decision on 2026-10-02: validate Oery's Linux project first. Attempt a bounded, clean-checkout x86_64 build and gameplay check before writing a new Linux port. The cost is an experimental baseline with narrower compatibility evidence. Success would not establish full-game completion or ARM handheld performance.

The alternative is to port himdo's release to Linux/Vulkan first. It has stronger completion reports, but brings Windows-specific code, writable-path changes, renderer validation, and ongoing fork maintenance. Neither route is a package-only task.

Before a game build, locate a matching owned game dump. Then reproduce the build, verify rendering/input/audio/save-load, test aarch64, and only expose working plugin outputs. Keep compilation on build machines and preserve signature and permission checks during any later installation.

## First validation attempt

The upstream checkout at `f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092` remains clean. No game executable was generated or built.

A bounded read-only inventory found no Fable-named input in the checked locations. On `zao`, these included Downloads, local Korri data, and the Towada gaming/downloads trees. On `aka`, these included Downloads, build directories, local Korri data, and `/srv/games`. The scan stopped at five directory levels and did not follow symlinks. This is not proof that the owner has no copy. A host and path are needed before continuing.

The public reproduction also needs patch repair. This command against the unchanged upstream checkout fails with exit 128:

```sh
git apply --stat docs/re/patches/sdk-tessellation-cbuffer-set.patch
# error: No valid patches in input (allow with "--allow-empty")
```

The file contains a rendered side-by-side diff, not a machine-applicable patch. Its intended change moves the Vulkan tessellation uniform block from descriptor set 0 to set 1. The other two SDK patch files also contain side-by-side text on inspection; they were not applied. Reconstruct only needed changes against the pinned SDK, then verify them with real builds and runtime behavior. Do not treat the displayed patch text as an already reproducible dependency.

The first attempt stopped for the owned input. Oery's codegen hash gate expects French GOTY `default.xex` with SHA-256 `0e1ea96ded3407874cbbb3a9587d79f1340a57a9d1ba2feebcfdbc9ed1e4b6e5`. A different dump requires compatibility investigation, not bypassing that gate. Do not download replacement game files or invent a substitute fixture to claim gameplay acceptance.

## Supplied input and SDK build

The user supplied `simon@myoko:~/Downloads/`. The ISO there is named `Fable 2 PLT.iso`. Its contents identify USA/Europe GOTY, not Oery's French GOTY input.

| Measurement | Verified value |
|---|---|
| ISO bytes | `7838695424` |
| ISO SHA-256, original and local copy | `2cdaafead95680e2c6fe8886a89f1ae3d5e41549857c7fc125a12aab1cb99ad9` |
| Extracted `default.xex` bytes | `21217280` |
| Extracted XEX SHA-256 | `88c4ef2e18e65409444d1b068eff921d1f7e180a5ae64edc64ba6b0872372662` |
| XEX payload offset | `0x4000` |
| XEX payload SHA-256 | `84651650d00ccd62021847a39fad6e63da0f7c49ef587a733e215e5ec5a23a4a` |
| Title, media and version | `4D5307F1`, `716F0A0D`, `0.0.0.26` |
| Entry point and image base | `82CBB970`, `82000000` |
| Extracted regular files and total bytes | `451`, `6997047778` |

The remote ISO's size and modification time stayed unchanged across hashing. The local copy has the same whole-file hash. Extraction used [XboxDev/extract-xiso](https://github.com/XboxDev/extract-xiso/tree/3f5b62cfe68f000b0e3c8a30104973f3a297948e), compiled on `zao`, in extract-only mode. A private checksum manifest records every extracted file. Originals and generated code stay outside the plugin repository and public caches.

The XEX hash matches himdo's recorded USA/Europe GOTY image. Its payload hash also matches the USA/Europe payload in `docs/GERMAN_GOTY_SUPPORT.md`. The title ID, entry point and image base match Oery's record. These checks identify the input; they do not establish compatibility with every Oery hook. The private validation checkout pins this measured XEX hash in `docs/re/entry-xex.sha256` and generates code from that same file. It does not substitute a French executable or remove hash validation.

The SDK at `c94f5ebdcb3c9d1a460ca48e04f9758448f8d518` built on `zao` with its exact 22 top-level submodule pins. The only source changes reconstruct the published [keep-open](../../plugins/fable-ii-recomp/patches/sdk-keep-open.patch) and [tessellation descriptor-set](../../plugins/fable-ii-recomp/patches/sdk-tessellation.patch) fixes as valid unified diffs. The temporary fault diagnostic patch is excluded. Both diffs pass forward and reverse applicability checks against the pinned source.

Clang 20.1.8, CMake 4.3.4 and Ninja 1.13.2 built the native x86_64 CLI, runtime and Vulkan plugin in RelWithDebInfo mode. Running `rexgluerd --version` reports `0.10.0.2-dev.gc94f5eb`. This verifies the SDK build, not Fable gameplay. The artifacts contain absolute Nix dependencies and are not deployment packages. No device build or installation ran.

Game code generation and the native game build use an active supervisor that polls exit status and log progress every 30 seconds. Each stage has a timeout and retains its full log. ARM work and plugin publication remain gated on native validation.

## Native x86_64 results

Normal code generation passed in 128 seconds and wrote 589 files. The known large-function notice for `0x82242ED0` remained informational. No forced code generation or generated-source edit was used.

The source-backed game build completed all 1,111 steps in 1,077 seconds with three build jobs. The output is a native x86-64 ELF, not Wine, CPU translation or an emulator process. It remains a private development build, not a reproducible Nix deployment output.

The first launch stopped before the game with `SDL_InitSubSystem(SDL_INIT_VIDEO) failed: wayland not available`. CMake requested Wayland, but SDL's configure summary showed it disabled. `WAYLAND_SCANNER` was missing. Adding `wayland-scanner` to the private Oery devshell enabled `SDL_VIDEO_DRIVER_WAYLAND`; the rebuild took 29 seconds. This is a build-tool fix, not a game-code change.

A later run reached the Fable II title screen and attract video on an NVIDIA GeForce RTX 3060 Laptop GPU, driver 580.142. Screenshots were inspected directly. The game logged a six-channel, 48 kHz audio endpoint. The test used a private headless Sway display and a private PulseAudio null sink. This establishes startup and visible output, not sound quality or physical-controller acceptance. Startup time varies, and several runs remained white for minutes before advancing.

The first keyboard-based automation was inconclusive. A Wayland event viewer confirmed input delivery. A debugger launched as the game's parent confirmed `mnk_mode=true`, an attached SDK window, focus, and Space events reaching the SDK's MnK driver. Do not treat these early harness results as proof of a game input defect.

The successful test uses SDL's documented process-local virtual-gamepad API. The first version attached before ReXGlue installed its device-event watch, so ReXGlue never discovered the controller. Deferring attachment until after SDK startup fixed the harness. ReXGlue then logged the controller at connection order 0. The test creates no kernel input device, changes no system input permissions, and does not alter game code.

With that controller, the game accepted A and D-pad input, opened New Game, selected a character, and created `Hero000/mainsave.bin` with 130,483 bytes. This was a real bulk save, not just the 328-byte header. A new process using the same private `user_data_root` offered Continue, loaded Bowerstone Old Town, and showed the child hero with the opening objective. Left-stick input then moved the hero along the street. Screenshots were inspected before and after movement.

A ten-second capture from the isolated game-audio monitor contained 2,881,536 signed 16-bit samples across six channels at 48 kHz. Of those, 2,833,153 were nonzero; peak magnitude was 1,977 and RMS was 166.222. This verifies delivery of game audio data, not listening quality.

The test runtime loaded `librexruntimerd.so` and `libTracyClientrd.so` from the private pinned SDK output, verified through its process mappings. A link audit also found an inherited Korri `outputs/out/lib` entry in RUNPATH. The development artifacts therefore remain unsuitable for deployment; final Nix packaging must remove ambient build-environment paths.

An experiment removed Oery's direct UI/ImGui linkage from the executable. It linked successfully and removed duplicate cvar warnings, but did not establish an input improvement. The experiment was reverted. No such patch is part of the retained source changes.

## ARM source-build result

The supervised build passed on the existing `fuji` aarch64 build machine. Its private workspace is `/tmp/fable2-arm-20261002-4fb26a712c8d`. Source commits, all SDK gitlinks, both patches, and the owned XEX hash passed staging checks. Normal code generation passed in 163 seconds. The full game build completed 1,211 steps in 2,091 seconds.

The final check inspected the actual executable and libraries as ELF64/AArch64, resolved their dependencies, and matched the game-local GPU plugin to the newly built SDK plugin. The SDK CLI ran natively and reported `0.10.0.2-dev.gc94f5eb`. All 587 generated C++ and header files were byte-identical between the completed x86_64 and aarch64 builds. The comparison excluded build metadata and stamp files. The ARM game itself was not run.

Environment setup was slow. It completed while the parent was investigating the delay; the parent interrupted during SDK configuration, then resumed the same pinned build. No alternative environment, source version or machine-wide Nix setting was introduced.

The build resolves ISA flags and compiler names from the pinned SDK's `linux-arm64` preset. Only private build setup changes select `aarch64-linux`, add `wayland-scanner`, choose ARM output paths, and pin the measured USA/Europe XEX. Oery's game hooks and original UI linkage remain unchanged. Sources and owned/generated game code stay out of public caches. The isolated devshell passed to Nix contains only its flake and lock.

The supervisor polls every 30 seconds and propagates phase failures. Build limits are three compiler jobs, two hours for each SDK build stage, four hours for the game stage, and eight hours for aggregate native validation. These are limits, not time estimates. No ARM GUI or handheld acceptance follows from a successful build.

Verified outputs are `oery/build/native/fable_ii` and `sdk/out/linux-arm64/` under that private workspace. Evidence is in `logs/full-game-build.log` and `logs/native-elf-link-gates.log`. These are private development artifacts, not the final Nix plugin package.

## Plugin integration choice

The user chose ISO launch rather than requiring extracted files. The implementation follows the existing native-plugin account contract, keeps Oery's `assets-extracted/00007000` layout, and uses the upstream `fable_ii` application name. A verified temporary ISO snapshot protects extraction from later edits to the caller's file. First-run peak storage is about 15 GB; about 7 GB remains per account.

A clean Nix engine build compiled and linked successfully but failed fixup because the SDK libraries retained `/build/` RPATHs. The package now replaces those paths with `$ORIGIN` before standard fixup and dependency resolution. The forbidden-path check stays enabled. A subsequent dependency check required SDL's OpenXR loader, which is now declared rather than ignored.

The corrected clean x86_64 Nix engine build passed. The actual packaged declaration, host admission, sandboxed callback, native ELF, extractor, account-lock and preservation checks passed. A real owned-ISO run through Core verified all 451 extracted paths/sizes, the XEX hash, cached reuse and native SDL entry. It left the ISO unchanged. That check deliberately disabled video and does not establish packaged GUI gameplay.

A subsequent graphical test exposed another packaging omission: SDL's installed driver list was only `x11` and `offscreen`. Configure logs reported `No package 'egl' found`, so Wayland was disabled despite the scanner dependency. `libglvnd` is now declared. Both SDK/game configure stages require `SDL_VIDEO_DRIVER_WAYLAND`, and the package test queries the actual installed SDL driver list. This new test rejects the earlier package.

## Final package gates

The corrected Nix packages and contract/launcher checks passed on both native build machines. Their installed SDL runtimes include Wayland. The x86_64 owned-ISO check passed again against the corrected package.

| Artifact | Verified store path |
|---|---|
| x86_64 native engine | `/nix/store/1xgzkwqxj0nl1rl57ld0q9nnaza14dya-fable-ii-recomp-0-unstable-f3ae1ad` |
| x86_64 package check | `/nix/store/7mid2ms3snbq2a90vy9znhx9fj310k1f-korri-fable-ii-recomp-plugin-check` |
| aarch64 native engine | `/nix/store/32cr4gmb0bidfwz9d4m9xh8cx1837awj-fable-ii-recomp-0-unstable-f3ae1ad` |
| aarch64 plugin | `/nix/store/j48921lkgairx68vnp2n7lxk51ccmywz-korri-plugin` |
| aarch64 package check | `/nix/store/vv9b9i5ikq0znjg65wnk9l33qmyza2gr-korri-fable-ii-recomp-plugin-check` |

After final documentation, test formatting and rebase, both architecture checks passed again. The ARM rerun used repository snapshot `387a96f108d7ab954c715e15243367052836da1b`, which contains the unchanged Fable II implementation from `3e8e350`. It reused the exact verified engine above and built only the final plugin package and check.

The ARM rerun first waited for other builds on `fuji` to finish. Its last 90 seconds before launch recorded no build processes and CPU use of 4.50%, 5.22% and 4.37%. The package/check command then passed in six seconds. Evidence is `/tmp/fable2-final-arm-recheck.log` locally and `/tmp/fable2-final-check-387a96f/final-check.log` on `fuji`. No device installation, game launch, signature change or public publication ran.

A separate graphical test executed the actual corrected x86_64 Nix engine. Process mappings confirmed its packaged executable, runtime, GPU plugin and Tracy library, without raw development binaries. Continue loaded a copied save into Bowerstone Old Town. A three-second stick input moved the hero along the street. The original save files remained unchanged, and all test processes were stopped.

Native default logging wrote `user_data_root/logs/fable_ii_001.log`. A separate untouched-wrapper run read `user_data_root/fable_ii.toml` and honored its configured log destination while preserving the TOML bytes. New configuration-file creation was not tested. The graphical run used a process-local virtual controller, not physical handheld controls.

The packaged run retained 33 duplicate-cvar warnings and 3,856 `BaseHeap::AllocFixed` errors. They did not prevent the observed sequence, but their broader consequences are unverified. Do not call this full-campaign, graphics-fidelity, long-session, audible-speaker, ARM gameplay or device acceptance.

Final private evidence includes `/tmp/fable2-final-arm-package.log`, the `final-x86-package-check.log` and `final-owned-iso-check.log` files under the local validation directory, and `/tmp/fable2-packaged-smoke-result.md`. Original screenshots and process mappings are under `runtime-pkg2-lbcq8n4y` and `runtime-pkg2cfg-dcowcctt` in that directory. No game assets, screenshots, generated game code or native binaries were added to Git.
