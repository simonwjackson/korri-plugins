# Dr. Mario 64 Recompiled

This plugin adds a native runner for the owner's measured US ROM, using
[`theboy181/drmario64_recomp_plus`](https://github.com/theboy181/drmario64_recomp_plus/tree/af91e3bf56b1ffc329ff4327fdc2380515463de7).
It is not an emulator and does not add a game to the library automatically.
Its Nix outputs target Linux x86_64 and aarch64. Target declarations do not
establish gameplay or ARM build acceptance.

## Private builds

The owner supplied a US ROM and authorized private local work. Ask the owner
before sending any sources, ROM inputs, closures, or build jobs to `fuji`.
No transfer to that builder, public publication, signing, or device installation
is authorized by these package definitions.

Upstream generates native code from the ROM. Keep the ROM, generated code,
compiled engine, plugin closure, and private build logs out of public caches
and release assets. GPL-3.0 covers the upstream integration source, not a grant
to distribute Nintendo data. This repository contains source, patches, and
hashes only.

The local Nix store is readable by other local accounts. Private builds do not
encrypt the ROM. Use only trusted build machines. The commands below disable
remote builders, post-build publication hooks, and automatic store signing. The private derivations also
refuse substitution. These controls do not stop a separate manual `nix copy` or
an administrator from distributing the closure.

Never compile or dispatch builds from a target device. Devices receive prebuilt
artifacts through the approved signed installation path.

## Supported input

Both identities were measured from the same owner-supplied 4,194,304-byte ROM.
The runtime validates the entire file before changing native state.

| Byte order | SHA-256 |
|---|---|
| Original swap16 dump | `613778b244784492a881c0d72d6017f82c39026706a406bd7ef95c6f33e53b89` |
| Canonical big-endian dump | `bb2c0dec0a8287ad256929563d0509801c2f239df883c1cf52cab05b23bd77b6` |

Upstream's `GameEntry` accepts the US ROM with XXH3-64
`0x960e3703f29d996d`. This is not the SHA-256 used for Korri discovery.
ZIP archives and other regions are not discovery inputs. Extract your archive
locally and register its bare ROM in the library. The launcher does not change
that file.

## Prepare and build

Run these on a build machine. The preparation command needs no native engine
or retail data in the Nix store. It refuses to overwrite an existing output.
Its output directory must already exist.

```sh
nix run --option builders '' --option post-build-hook '' --option secret-key-files '' \
  .#prepare-drmario64 -- '/private/Dr. Mario 64 (USA).n64' /private/drmario64.us.z64
nix-store --add-fixed sha256 /private/drmario64.us.z64

nix build --no-link --option builders '' --option post-build-hook '' --option secret-key-files '' \
  .#korri-plugin-drmario64
nix build --no-link --option builders '' --option post-build-hook '' --option secret-key-files '' \
  .#checks.x86_64-linux.korri-drmario64-plugin
```

Use `checks.aarch64-linux.korri-drmario64-plugin` on an approved ARM64 build
machine after permission to transfer the private input. No target-side compiler
or recompiler is included in the runtime closure.

`source.nix` pins the exact engine and recursive submodules. `tools.nix` pins
the README's generation tools, N64Recomp `a13e5cf` and decomp `91dab37`.
The build retains the upstream decompression algorithm and segment table.
Python standard-library file, MD5, and CSV calls replace helper imports that
otherwise pull in unused disassembly and compression packages. Nix supplies
SDL2 and patched shader tools rather than requiring target-side builds.
`fetch.gitconfig` changes only Git transport from public GitHub SSH URLs to
HTTPS. A clean source fetch needs no user SSH keys and retains the pinned hash.

## Launch and native state

`plugin.ts` follows the existing N64 discovery and hash-specific runner contract.
It receives `accountRoot` from Core and selects `<accountRoot>/drmario64.us`,
using upstream's registered `game_id`. It does not add a Korri configuration
schema or account selector.

The launcher validates the original ROM, locks the account directory, and
atomically installs its canonical copy as `drmario64.us.z64`. That filename comes
from `GameEntry::stored_filename()`. It links immutable packaged `assets` and
`icons`, refusing to replace unrelated links or real resource directories.
It supplies upstream's `APP_FOLDER_PATH` and the Vulkan loader path.

`native-launch.patch` adds `--start`, which checks the native ROM import and
queues the same game as upstream's Start event after the first completed VI.
Starting before that callback skipped dummy-video initialization and crashed
`vi_thread_func()` in the local test. The patch also fixes SDL initialization's
error check to report negative return codes. It avoids a second ROM picker
and launcher confirmation. No-argument native launches retain upstream behavior.
The patch adds no new settings or save format. A controller assignment prompt
is not invoked in direct-start mode; physical controller mapping still needs
acceptance testing.

Upstream owns `general.json`, `graphics.json`, `controls.json`, `sound.json`,
mods, and `saves/drmario64.us.bin`. Its Eep4k save buffer is 512 bytes. The wrapper
never rewrites settings or saves. The account lock remains open through native
execution to refuse concurrent launch into the same state directory.

`native-shutdown.patch` fixes the observed idle-thread access after memory
release. It waits for the game's existing IDLE hook to acknowledge shutdown,
then finishes EEPROM, mod configuration, and native settings writes. It reports
persistence errors through a nonzero exit code. It does not hide crashes.

The cost is process-lifetime storage. RDRAM, the detached timer's storage, and
parked worker contexts remain allocated until the process ends. The patch skips
global destructors only after the explicit persistence steps. It does not add
in-process restart or power-loss durability. A game that never reaches IDLE,
a blocked filesystem, or an existing native error dialog can delay shutdown.

Upstream otherwise uses the inherited `MarioKart64Recompiled` Linux config
namespace. The explicit account path avoids mixing those settings. A
`portable.txt` in the account directory selects the same directory, not another
account. Back up the entire account directory before manual state changes.

## Verification

The package check typechecks the packaged plugin against the pinned contract,
checks host admission, executes the sandboxed launch callback, verifies literal
paths, and tests invalid-ROM preservation and rejected overrides. It also runs
the native binary's non-graphical help and invalid-option paths. A C++ probe
compiles the patched production PI and file helpers. It tests a pending
512-byte save, native reload, pre-initialization exit, failed opens, and a
write/close failure through `/dev/full` that must preserve the previous save.
The probe sets up the native save context directly; it does not run the game's
EEPROM entrypoints or campaign. Although these checks do not boot retail data,
building the engine still requires the private ROM.

The opt-in test uses the owned ROM, temporary account storage, dummy audio,
software Vulkan, and a private X11 display on the build machine:

```sh
nix run --option builders '' --option post-build-hook '' --option secret-key-files '' \
  .#verify-drmario64 -- '/private/Dr. Mario 64 (USA).n64' /private/test-artifacts
```

The optional artifact directory receives screenshots and logs, not ROM imports
or saves. The test exercises launch through Core, source preservation, startup-time exit,
the native game-state initialization path, keyboard delivery, concurrent-launch
refusal, shutdown ordering, and restart. It checks distinct native volume
settings in two accounts, unsafe resource links, and failed-save reporting.
It does not establish full playability, audible sound, physical controllers,
campaign save/reload, or pending mod-settings persistence. Upstream itself reports
"Very lightly tested overall."

### Current acceptance

Verified on the local x86_64 build machine and the aarch64 builder `fuji` on
2026-10-03. The owner authorized the private ARM work after competing builds
finished. Neither run used a physical device. The two runtime stop
methods are SIGTERM and a direct ICCCM `WM_DELETE_WINDOW` request. The test uses
a small X11 sender because Xvfb has no window manager to relay an EWMH request.

| Gate | Result |
|---|---|
| Private x86_64 engine build | Passed locally with both startup and shutdown patches. |
| Clean recursive source fetch | Passed over HTTPS without user SSH configuration. |
| Owned-ROM preparation and overwrite refusal | Passed locally. |
| Plugin typecheck, packaged launch contract and admission | Passed on both architectures against the pinned host. |
| Native save IO probe | Passed exact 512-byte write/reload and failed-open/write preservation checks on both architectures. |
| x86_64 owned-ROM rendering | Inspected the rendered Classic game board reached through Core and keyboard input. |
| aarch64 owned-ROM rendering | Inspected the rendered Classic setup menu reached through Core and keyboard input. This does not establish ARM gameplay. |
| Owned-ROM shutdown and restart | Both architectures passed three startup-time exits and three normal launches with two separate account roots. |
| Failed native save | Both returned failure and preserved the prior save when the save directory was read-only. |
| Window-close request | Both passed direct ICCCM close requests during startup and after game launch. |
| Private aarch64 engine build | Passed on `fuji`. The actual binary is AArch64 ELF64, with no compiler in its runtime closure and no signature on private outputs. |
| aarch64 package and runtime checks | Passed after adding the pinned ARM header directory to the save-test compiler command. |
| Signed installation and physical-device gameplay | Not authorized or performed. |

Update these results only with direct evidence. A declaration, evaluation,
build, startup window, and playable game are different checks.
