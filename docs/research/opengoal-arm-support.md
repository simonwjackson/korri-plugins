# OpenGOAL Linux ARM work

## Approved scope and deployment gate

The owner approved native Linux ARM support for Mini V2 after the x86_64 plugin landed at `819e482`. This is native execution using upstream's ARM backend, not x86 translation.

Build and test on zao and the configured aarch64 builder fuji. The owner requires Fuji to have no other compilation running before starting our builds. Check compiler/build processes immediately before dispatch. If busy, continue local source work and defer our build; never stop another task. Do not access, install on, launch on, stop games on, or otherwise change Mini V2 during this stage. When off-device validation is ready, pause and use `ask_user` to ask whether the owner is ready for device deployment and validation. Approval for this work is not approval to deploy now.

At the previous read-only device check, Mini V2 reported `aarch64` and an active Zelda3 session. That is historical evidence, not its current state. Recheck active sessions only after the deployment gate opens.

## Grounding

- Upstream v0.3.8 is commit `6445b4a50a7540df512e3c82c62216521421410c`.
- It includes `game/kernel/asm_funcs_arm64.s`, `common/arm64/encoding.h`, the ARM emitter, and native emitter/trampoline tests.
- The existing prebuilt x86 extractor accepts `--instruction-set arm64`. Verify its output on a native Linux ARM runtime rather than treating successful compilation as playable support.
- The plugin already uses upstream `out/<game>/iso/GAME.CGO` files as library inputs. ARM output identities must be measured from the owned discs. Do not put x86 hashes in an ARM runner or fabricate new identities.
- Owned discs and existing x86 preparations remain in `/var/tmp/korri-opengoal-owned/` on zao. Commercial data stays outside the repository and Nix outputs.

## Verification required before asking to deploy

1. Build a portable Linux aarch64 native runtime on build infrastructure. Preserve the x86 package.
2. Exercise upstream ARM unit tests where available and record any exclusions.
3. Prepare the owned trilogy and Renegade for ARM off-device. Measure the actual native files and verify reproducibility.
4. Check both plugin architectures, wrong-architecture exclusion, and literal launch arguments through Core's real interpreter.
5. Run the native ARM runtime with prepared data on fuji. Record observed rendering and remaining hardware-specific gaps separately.
6. Land and publish source/tests without triggering device installation. Ask the owner before the first device deployment or validation action.

Do not claim ARM support is complete merely because the runtime links or its help command succeeds.

## Retail-data failure and signed-char correction

The first actual ARM Jak 1 launch reached GOAL kernel startup and then exited with SIGSEGV before its first capture. Its log had repeated `0xff` padding, corrupted filenames, and a subtitle load failure. OpenGL 4.5 and NEON initialized successfully. The 158 unit tests did not cover this case.

`game/kernel/common/kprint.h::format_struct` stores its unset sentinel as `char(-1)`. Linux ARM defaults to unsigned plain char. A small test including the actual upstream header reproduced sentinel `255` with `-funsigned-char` and sentinel `-1` with `-fsigned-char`. The formatter compares these fields with `-1` in all game variants.

The Linux ARM C++ flags now include `-fsigned-char`, and `ARM64Formatting.default_fields_have_negative_sentinels` checks the real reset method. The corrected native rebuild passed 159 tests from 22 suites in 15.808 seconds, with zero failures, disabled tests, or errors. Its runtime output is `/nix/store/a6kqjpx0n45l4xjb85fmx8fyssyqzqgz-opengoal-runtime-0.3.8`. The repeat ARM Jak 1 launch reached its rendered title and Press Start screen at 120 seconds. Its version numbers, filenames, and formatting are readable again. This confirms the observed startup crash is fixed; it does not establish complete gameplay. No device deployment is authorized by these source changes.

Private failure evidence: `/tmp/opengoal-arm-fuji-7pj8lu_3/jak1/unsigned-char-game.log` on zao, copied from the original failed run at `/tmp/opengoal-owned-check-r11t474h/game.log` on fuji. The successful retry is `jak1/game.log` and `jak1/frame-120.png` under the same local proof directory. The test copies on fuji omit only `iso_data` and `decompiler_out`; native runtime resources, source/editor fixtures, and all `out` files remain intact. Original prepared data on zao is unchanged.

## Verified native result

The corrected source build completed on fuji after an idle check. Its 159 native tests cover ARM emitters, NEON, register/stack preservation, C stubs, cache invalidation, SkyBlend, and the formatter sentinel. The package rejects a zero-test filter result. Both x86_64 and aarch64 plugin checks pass, including wrong-architecture release exclusion and production sandboxed launch arguments.

| Artifact | Verified value |
|---|---|
| Runtime | `/nix/store/a6kqjpx0n45l4xjb85fmx8fyssyqzqgz-opengoal-runtime-0.3.8` |
| ARM plugin | `/nix/store/m5lmzbd17x38rrk71h9b9zqkg7sypvb6-korri-plugin` |
| Off-device verifier | `/nix/store/cxin1mn6yq8mfwnyhcip2b5fh93d1rn5-verify-opengoal` |
| Native version | `v0.3.8-linux-arm64` |
| `gk` SHA-256 | `80062146df8729d0c9bc753c324df2b22343cc95098b95a8248bf3e970ad9ec7` |

The artifact is AArch64 ELF with a non-executable stack. SDL/cubeb backend RUNPATHs survive fixup. Scanning all 118 runtime closure paths found no preparation or compiler executables. The older `lj7k8wzkaylrfnam78qlpzjbw5ghcb3c` runtime predates the signed-char fix and is not a deployment candidate.

The managed build log is `/tmp/pi-processes-zey9XQ/proc_ec0d-stderr.log`. `/tmp/opengoal-arm-checked-paths.json` records the checked plugin and verifier. Private rendering evidence is under `/tmp/opengoal-arm-fuji-7pj8lu_3/` on zao.

| Native ARM input | Capture inspected at 120 seconds |
|---|---|
| Jak 1 USA | Title, Press Start, and rendered landscape. |
| Jak II USA v1.00 | Jak II title and Haven City scene. |
| Jak II: Renegade | Renegade title and Haven City scene. |
| Jak 3 USA | Opening 3D scene; the 60-second capture also shows opening credits. |

All four completed the production `korrid plugin-launch` render probe on fuji. Each used private Xvfb, PulseAudio and configuration services. Each passed both late-frame checks and retained its input `GAME.CGO` hash. The original failing native formatter log remains archived separately. The verifier closure was explicitly copied and temporarily GC-rooted on fuji; merely building a fixture on the controller did not make it available remotely.

These checks establish native startup and rendering on Neoverse-N1 with Mesa software rendering. They do not establish full gameplay, audible audio, physical controller input, save/load, Adreno behavior, or Mini V2 performance. No target-device operations occurred. Busy Fuji periods were waited out; no other build was stopped or frozen. The next step is the owner's deployment-readiness question.

## Off-device data results

All four owned discs compiled for `arm64` on zao using the pinned x86 OpenGOAL 0.3.8 extractor. Each was prepared again through the real Nix app from a different working directory. The second run produced the same `GAME.CGO` hash and made no writes in the caller directory. These results establish reproducible preparation, not native ARM gameplay.

| Input | Bytes | SHA-256 of ARM `GAME.CGO` |
|---|---:|---|
| Jak 1 USA | 9693712 | `6c838d001de990273431c2e2bdc900052a6637e91d3c64bb625e5965a0f0084b` |
| Jak II USA v1.00 | 14498672 | `d877c28cfa48074a7a6e02b81c67c38b70f27f8b0be9922642cf12c13bf055f6` |
| Jak II: Renegade | 14498672 | `65fe7daca4265a29e6308d1c5f089c488a1ce67ce1360dcc41a0142215de1b03` |
| Jak 3 USA | 16345984 | `7280fce6003568d10b36cc26cb7cac13a545959e44353b7bbe1bd1a73eadb58a` |

The prepared data is under `/var/tmp/korri-opengoal-owned/prepared-arm-*` on zao. `repeat-arm-*.log` records the repeat runs. No commercial data enters Nix inputs or repository files.

The plugin source now selects measured release identities for the same system as its native runtime. Source generation fixes a constant at package construction, with no device probing or compatibility fallback in JavaScript. The x86 package/contract regression check passes with the new source generation and ARM preparation option.

## Native port scope

The first build confirmed an x86-only ptrace register implementation in `common/cross_os_debug/xdbg.cpp`. Its `Regs` type exposes x86 GPRs and RIP. The approved minimum is an explicit unsupported result for ARM register inspection/modification, while retaining normal Linux thread and memory helpers. This is not a fabricated ARM-to-x86 register mapping or a new debugger design. Retail execution does not need that register debugger. The native build and unit tests subsequently passed; game and device validation remain separate.
