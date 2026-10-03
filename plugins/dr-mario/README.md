# Dr. Mario NES Recomp

This plugin adds a native route for the owner's supported Europe NES ROM on
x86_64 and aarch64 Linux. Both native builds and owned-ROM checks passed.
It uses [mstan/DrMarioNesRecomp](https://github.com/mstan/DrMarioNesRecomp), not
Dr. Mario 64 or the Turbo ROM hack.

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

`account-storage.patch` redirects native writable paths to that working
directory. It preserves `config.ini`, `keybinds.ini`, `savestates/slotNN.sav`, and
native save formats. It removes executable-directory state lookup, not a second
fallback. Existing files are not rewritten by the wrapper. Launcher artwork
remains in the immutable package. No new Korri configuration language is added.
`literal-rom-path.patch` preserves positional ROM paths longer than upstream's
512-byte picker buffer. The verifier exercises such a path.

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
that default. Physical controller and audio acceptance require device testing.
Korri launch overrides and emulator-core arguments are rejected rather than
silently ignored.

## Sources and build policy

| Component | Pinned source |
|---|---|
| DrMarioNesRecomp | `a23472870e0a86dc0c94d88ac1ee3be5a7ea80f9` |
| nesrecomp | Upstream gitlink `7f6377b74f2c1e9d1171f707dc003f71c2dc236f`. |
| recomp-ui | Upstream gitlink `44f549c0f159df343cba9d8c3842dbc7e592eb08`. |

`engine.nix` compiles upstream's committed generated Europe C sources. No ROM,
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
It uses temporary account roots, private Xvfb, and dummy audio. It deletes its
copy of retail data when it finishes. It tests native frames, actual Core launch,
save/load hotkeys, native save-file loading, account isolation, diagnostic-output
suppression, concurrent-launch refusal, and clean exit. Those checks do not prove
restored gameplay. It does not test a physical screen, sound output, gamepad,
or ending.

| Check | x86_64 Linux | aarch64 Linux |
|---|---|---|
| Native engine build | Passed on `zao`. | Passed natively on `fuji`. |
| Strict contract, packaged manifest, host admission and invalid-ROM rejection | Passed on `zao`. | Passed on `fuji`. |
| Owned-ROM runtime check | Passed three consecutive runs after review fixes, including long paths and inherited-diagnostic suppression. | Passed the same verifier on `fuji`, including native save-file loading and account isolation. |
| Physical device installation and gameplay | Not run. | Signed Mini V2 installation, fullscreen capture and speaker routing verified. Physical controls/audio acceptance pending. |

The 2026-10-03 local verification also passed Nix formatting, Ruff formatting and
lint, strict TypeScript checking, and Git whitespace checks. The long-path test
failed against the earlier engine and passed after the positional-path patch.
The runtime test waits for a focusable X window because SDL can replace its
startup window while selecting a renderer. Review found no remaining blocker
in the fixes. Both architectures ran 600 native smoke frames with zero dispatch
misses and the same six sampled framebuffer hashes. This tests the exercised
startup path, not complete gameplay.

ARM runtime evidence is `/tmp/dr-mario-arm-evidence-nbrlgdo6/runtime.log` on `zao`.
The builder's private ROM copy, temporary GC root, and test directory were removed
after the test. The engine builds need no ROM. Neither architecture's native
output was published publicly. The owner subsequently approved private signed
installation on the Mini V2. [Device evidence](../../docs/deployments/2026-10-03-dr-mario-miniv2.md)
records its normal sandboxed launch and the remaining physical acceptance checks.
