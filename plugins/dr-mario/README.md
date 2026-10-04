# Dr. Mario NES Recomp

This plugin adds a native route for the owner's supported Europe NES ROM on
x86_64 and aarch64 Linux. Both native builds and owned-ROM checks passed.
It uses the maintained
[simonwjackson/DrMarioNesRecomp](https://github.com/simonwjackson/DrMarioNesRecomp)
Europe-only fork, not Dr. Mario 64 or the Turbo ROM hack.

Upstream calls this a playable preview. It reports one-player virus clearing,
but leaves two-player mode and endings untested. Package checks are not proof
of a complete game or of handheld performance.

## ROM contract

Discovery accepts unpacked `.nes` files in an already registered library.
It does not claim ZIP files or register a library folder automatically.
Only the measured whole-file SHA-256 below gets this runner. The wrapper checks
it again before starting native code. It does not modify or extract the ROM.

| Input supplied by the owner | Bytes | Headerless CRC32 | Result |
|---|---:|---|---|
| Dr. Mario Europe | 65552 | `9735D267` | Supported and selected for this build. |
| Dr. Mario Japan/USA, without Rev 1 | 65552 | `198C2F41` | Rejected. |
| Dr. Mario Turbo | 262160 | `BA9E07F9` | Rejected. |

Europe whole-file SHA-256:
`83914c08f82fc70779121760a48392af3a5988f015794eb53cbe1aa0a165c821`.
Headerless SHA-256:
`9d39ca09c9fe9eb0c03ede1b506fd7297f50b985467739d1697ce809b3ab8736`.

The owner supplied `Dr. Mario (Europe).nes` in an attachment on 2026-10-02.
Both its 16-byte iNES header and data are covered by the whole-file hash.
Upstream also has a separate Japan/USA Rev 1 target with headerless CRC32
`DE581355`. This plugin does not advertise that unmeasured file or mix its
translated code with the Europe build.

## State and controls

The user approved `<accountRoot>/DrMarioRecomp` on 2026-10-02. The directory name
comes from upstream's executable. Core creates it and sets the working directory.
The launcher locks that directory across execution to prevent concurrent writes.
Back up this directory separately from the ROM. Core currently supplies its
existing account root; this plugin adds no account selector.

The maintained framework redirects native writable paths to that working
directory. It preserves `config.ini`, `keybinds.ini`, `savestates/slotNN.sav`, and
native save formats. It removes executable-directory state lookup, not a second
fallback. Existing files are not rewritten by the wrapper. Launcher artwork
remains in the immutable package. No new Korri configuration language is added.
The maintained launcher preserves positional ROM paths longer than upstream's
512-byte picker buffer. The verifier exercises such a path.

The maintained PAL runner corrects a speed bug in the pinned Europe build. Region
selection previously chose Europe game code but retained NTSC hardware clocks.
The owner reported fast gameplay. Local measurements confirmed 60 frames/second
and 29780.5 CPU cycles/frame instead of PAL's 50.007 frames/second and 33247.5
CPU cycles/frame. Earlier smoke and save tests did not check playback speed.

The runner derives game, CPU and sample timing from one PAL master clock. It
uses 312 scanlines, the 16:5 PPU-to-CPU ratio, PAL APU tables and sequencer
periods, and fractional CPU/sample budgets. An accumulated host deadline avoids
integer sleep drift and includes time already spent waiting for vsync. It keeps
upstream vsync, turbo, generated game code and save format unchanged.
This is a Europe-only correction, not a generic region selector.

The hardware values come from NESdev's [cycle chart](https://www.nesdev.org/wiki/Cycle_reference_chart),
[APU frame counter](https://www.nesdev.org/wiki/APU_Frame_Counter),
[noise](https://www.nesdev.org/wiki/APU_Noise), and
[DMC](https://www.nesdev.org/wiki/APU_DMC) documentation. The upstream immediate
`$4017` reset and simplified rendering remain. Correct PAL clocks do not prove
cycle-perfect emulation or complete gameplay.

The pinned source differs from the upstream README's old hotkey table:

| Action | Pinned native default |
|---|---|
| Start | Enter. |
| Move | Arrow keys. |
| A / B | Z / X. |
| Save a state | Shift+F1 through Shift+F12. |
| Load a state | F1 through F12. |
| Turbo | Tab. |
| Quit | Escape. |

The native `config.ini` owns controller routing. The upstream default assigns
player one to keyboard, not a gamepad. This plugin does not silently replace
that default. Physical controller mapping still needs device testing. The owner
accepted playback after the Mini V2 PAL update.
Korri launch overrides and emulator-core arguments are rejected rather than
silently ignored.

## Sources and build policy

| Component | Pinned source | Upstream baseline |
|---|---|---|
| [DrMarioNesRecomp](https://github.com/simonwjackson/DrMarioNesRecomp) | `f814fda8da7fcbeb863e48bdc632cb3527761474` | `a23472870e0a86dc0c94d88ac1ee3be5a7ea80f9` |
| [nesrecomp](https://github.com/simonwjackson/nesrecomp) | `e3d9f1944661e9afe2a8ccf42e39b9af82410968` | `7f6377b74f2c1e9d1171f707dc003f71c2dc236f` |
| recomp-ui | `mstan/recomp-ui` at `44f549c0f159df343cba9d8c3842dbc7e592eb08` | Unchanged. |

The owner approved creating both source forks and moving the tested fixes on
2026-10-03. Both default to `korri-dr-mario-eu`. The framework owns the former
account-storage, literal-ROM-path and PAL patches; packaging no longer applies
or duplicates them. CMake defaults to Europe and rejects other regions. The
fetched runtime files exactly match the tested patched sources, and all
committed generated game files remain unchanged. The UI stays upstream. This
requires maintaining two repositories, not a general PAL/NTSC framework.
GitHub Actions are disabled on both forks to prevent binary publication.

`engine.nix` compiles the committed generated Europe C sources. No ROM,
recompiler, compiler, or on-device build step is shipped. NES PPU/APU/mapper
simulation remains part of the native runtime; this is not a claim of zero
emulation. The developer TCP server and optional netplay are disabled at build
time. The wrapper also removes inherited `NESRECOMP_`, `RECOMP_AUDIO_`, `LNG_`,
and `NES_NET` environment overrides. Some upstream diagnostics open output files
even without the trace server. Native configuration files still work. Debugging
through those environment overrides requires an explicit raw-engine invocation.
The package links system SDL2, OpenGL, and X11 headers through Nix.

Upstream declares PolyForm Noncommercial 1.0.0. The generated source also comes
from retail game code. Keep native outputs private. This repository adds no
public binary publication, signing, installation, or trust changes for this
plugin. Upstream and bundled third-party notices remain in the native package.

Integration follows the existing SMW launch treaty and personal publisher
namespace. The `nes` identity and title come from the publisher's
`plugins/libretro/cores.nix`, including FCEUmm and Nestopia. No core schema changes
or imported legacy runtime are needed.

## Fork-pin verification

The fresh x86_64 package and owned-ROM run passed on 2026-10-03. It measured
33247.497 CPU cycles/frame and 881.877 samples/frame, with zero downstream
underrun, overflow or concealment growth after warm-up. All six 600-frame
framebuffer hashes match the earlier builds; there were zero dispatch misses.
CMake's unsupported-region refusal also passed. Formatting and Git whitespace
checks passed. The source archives fetched from GitHub matched the tested
runtime source, not just the local worktrees. The ARM package was not rebuilt,
and the device was not updated. This changes source ownership only. The ARM
results below belong to the earlier package, not a rebuilt fork-pin artifact.

Private evidence: `/tmp/dr-mario-fork-x86_64-outputs.txt`,
`/tmp/dr-mario-fork-x86_64-runtime.log` and `/tmp/dr-mario-fork-receipt.json`.

## Build and verify

Run on a build machine, never a target device. The user requires an explicit
`ask_user` prompt before sending any build to `fuji`. Keep distributed builders
disabled until that approval exists. Disable any post-build publication hook.
The owner subsequently approved continuing off-device work and requires another
`ask_user` pause before target-device installation or execution. On 2026-10-03,
the owner restored Tailscale access. The native ARM build and checks then ran on
`fuji`, after verifying its architecture, idle compiler state, and empty
post-build hook. No target device was contacted.

```sh
nix build --option builders '' --option post-build-hook '' .#korri-plugin-dr-mario
nix build --option builders '' --option post-build-hook '' .#checks.x86_64-linux.korri-dr-mario-plugin
nix run --option builders '' --option post-build-hook '' .#verify-dr-mario -- '/path/to/Dr. Mario (Europe).nes'
```

The opt-in verifier also accepts a ZIP containing exactly one supported ROM.
This is test input handling, not ZIP discovery or a production extraction path.
It uses temporary account roots and private Xvfb. The launch checks use dummy
audio. The audio timing check uses a private PulseAudio null sink, following the
existing OpenGOAL verifier. SDL's dummy driver truncates callback delays and
cannot supply a reliable audio clock. The private server does not open physical
audio devices or the owner's audio server. It deletes its copy of retail data
when it finishes. It tests native frames, actual Core launch,
save/load hotkeys, native save-file loading, account isolation, diagnostic-output
suppression, concurrent-launch refusal, and clean exit. The timing regression
also checks actual CPU clocks from upstream's private co-sim output, game frames
from timed native save files, and fractional sample totals from private PCM
capture. It checks post-bridge output and requires zero underrun, overflow or
concealment growth after a ten-second warm-up. Upstream's 200 ms pre-roll needs
at least about 9.3 seconds to drain toward its 60 ms target at maximum correction.
The capture checks about two seconds after warm-up. These are digital checks, not
proof of audible quality. Raw diagnostics remain disabled in normal plugin
launch. These checks do not prove
restored gameplay. It does not test a physical screen, sound output, gamepad,
or ending.

| Check | x86_64 Linux | aarch64 Linux |
|---|---|---|
| Native engine build | Rebuilt from the fork pins on `zao`. | Passed on `fuji` before the fork repin. No new fork-pin ARM build. |
| Strict contract, packaged manifest, host admission and invalid-ROM rejection | Passed again from the fork pins on `zao`. | Passed on `fuji` before the fork repin. |
| Owned-ROM runtime check | Fork-pin build passed PAL CPU/frame/audio timing, long paths and inherited-diagnostic suppression. | Same runtime source passed the PAL verifier on `fuji` before the repin, including native save-file loading and account isolation. |
| Physical device installation and gameplay | Not run. | Signed PAL update running on Mini V2. Live cadence measured 49.98 to 50.33 frames/second. Digital audio clocks and speaker routing passed. Owner accepted playback: "Feels good." |

The 2026-10-03 local verification also passed Nix formatting, Ruff formatting and
lint, strict TypeScript checking, and Git whitespace checks. The long-path test
failed against the earlier engine and passed after the positional-path patch.
The runtime test waits for a focusable X window because SDL can replace its
startup window while selecting a renderer. Review found no remaining blocker
in the fixes. Both architectures ran 600 native smoke frames with zero dispatch
misses and the same six sampled framebuffer hashes. This tests the exercised
startup path, not complete gameplay.

The owner approved the PAL fix and private `fuji` rebuild on 2026-10-03.
Both architectures measured 33247.497 CPU cycles/frame and 881.877 samples/frame.
One controlled run bounded game speed around 49.49 to 50.41 frames/second and
measured 44061.2 samples/second on x86_64 and 44083.8 on aarch64. Both had zero
post-warm-up bridge counter growth and produced nonzero post-bridge audio.
The new CPU regression rejects the earlier engine at 29780.508 cycles/frame.

PAL runtime logs are `/tmp/dr-mario-pal-x86_64-linux-runtime.log` and
`/tmp/dr-mario-pal-aarch64-linux-runtime.log` on `zao`. The builder's private ROM
copy, temporary GC root, and test directory were removed after each test. The
engine builds need no ROM. Neither architecture's native output was published
publicly. [Device evidence](../../docs/deployments/2026-10-03-dr-mario-miniv2.md)
records the signed installations, device measurements and owner acceptance.
The owner approved the PAL package update and launch. The Mini V2 now runs the
corrected native engine. Live readings confirm approximately 50
frames/second with turbo off and audio near 44.1 kHz without observed bridge
counter growth. All 35 other plugin selections, 2334 catalog games/releases and
the existing account files remain unchanged. The owner accepted playback:
"Feels good." Device save/load, physical button mapping and complete gameplay
remain unverified.
