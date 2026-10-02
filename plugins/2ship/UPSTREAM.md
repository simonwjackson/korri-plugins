# 2 Ship 2 Harkinian integration evidence

Checked 2026-10-02. x86_64 and aarch64 runtime checks passed;
physical-device acceptance remains unverified.

## Source and package

The repository's pinned nixpkgs packages 2 Ship 3.0.1 in
`pkgs/by-name/_2/_2ship2harkinian/package.nix`. It builds the native program,
extractor, and engine resources without a game ROM. It installs `bin/2s2h`
and the runtime bundle under `2s2h/`.

The original nixpkgs source fetch failed its fixed-output hash check:

- Expected `sha256-EC8o5FIP/eXa+0LZt0C8EWHzKVAniv9SIXkZdbibcxg=`.
- Received `sha256-HQ8K2VKHEQL7BtUwtm6A6VLkxF/Hb4g3HsrMyfx/unw=`.

The cause is not proven. Do not replace that expected hash without inspection.
`native-package.nix` instead fetches the exact 3.0.1 commit without deep Git
history and writes deterministic build metadata. Its fetched tree hash is
`sha256-4AKZfqAVOMZmapK6nTBLebU+uItUtwe/wAvmjzuSAWs=`.

`git ls-remote` and a separate shallow clone resolved tag 3.0.1 to
`f45acdd794712fefa0fae0bca86dcac22e040f09`. The clone has these submodule commits:

| Submodule | Commit |
|---|---|
| OTRExporter | `32e088e28c8cdd055d4bb8f3f219d33ad37963f3` |
| ZAPDTR | `684f21a475dcfeee89938ae1f4afc42768a3e7ef` |
| libultraship | `5d498e780f25dc3c05804b0328db683121d96a2d` |

The pinned Nix source matches all 6,286 files in the separate upstream clone,
excluding Git directories and the three deterministic metadata files.
This selects the existing package version, not a claim that 3.0.1 is latest.

## ROM inputs and launch

The [3.0.1 README](https://github.com/HarbourMasters/2ship2harkinian/blob/3.0.1/README.md)
requires user-supplied game data. The actual
[supportedHashes.json](https://github.com/HarbourMasters/2ship2harkinian/blob/3.0.1/docs/supportedHashes.json)
contains two SHA-1 identities:

| Edition | SHA-1 |
|---|---|
| NTSC-U 1.0 | `d6133ace5afaa0882cf214cf88daba39e266c078` |
| NTSC-U GC | `9743aa026e9269b339eb0e3044cd5830a440c1fd` |

Korri's existing runner `releases` contract accepts SHA-256 identities only.
The user supplied `simon@myoko:~/Downloads/`. The relevant ZIP contains one
32 MiB file, `Legend of Zelda, The - Majora's Mask (USA).n64`.
Its magic bytes are `37 80 40 12`, meaning 16-bit byte-swapped order despite
its `.n64` name. Normalizing each byte pair gives upstream's NTSC-U 1.0 SHA-1.
The original remote archive was not modified.

| Measured whole-file form | SHA-256 |
|---|---|
| Original byte-swapped ROM | `8dc31559174f958a938ab7eccb25dd310a4167f98cb68a521181f4653b684431` |
| Normalized big-endian ROM | `efb1365b3ae362604514c0f9a1a2d11f5dc8688ba5be660a37debf5e3be43f2b` |

The plugin declares only those two release identities. It does not claim the
unmeasured GameCube edition, arbitrary N64 games, or ZIP discovery.

[BenPort.cpp](https://github.com/HarbourMasters/2ship2harkinian/blob/3.0.1/mm/2s2h/BenPort.cpp)
searches for `mm.o2r`, then `mm.zip`, then `mm.otr`. It loads `2ship.o2r` from
the install bundle. Missing game assets trigger interactive extraction dialogs.
Old asset archives trigger a regeneration prompt when major/minor versions differ.

[Extract.cpp](https://github.com/HarbourMasters/2ship2harkinian/blob/3.0.1/mm/2s2h/Extractor/Extract.cpp)
searches `.z64`, `.n64`, and `.v64` files, normalizes byte order, and validates
header and whole-ROM CRC values. Its `CallZapd` invokes the compiled exporter.
The plugin must not assume a positional ROM argument reaches this code.

[extract_assets.py](https://github.com/HarbourMasters/OTRExporter/blob/32e088e28c8cdd055d4bb8f3f219d33ad37963f3/extract_assets.py)
has a positional ROM input and `--non-interactive`, but it is a separate tool.
Its complete runtime packaging and error behavior still need verification.

## Persistence and rendering

[libultraship Context.cpp](https://github.com/kenix3/libultraship/blob/5d498e780f25dc3c05804b0328db683121d96a2d/src/ship/Context.cpp)
separates install resources from writable data. With `NON_PORTABLE`, resources
come from `CMAKE_INSTALL_PREFIX`. On Linux, `SHIP_HOME` overrides the writable
app directory; otherwise `SDL_GetPrefPath` selects it. Search order is the app
directory, install bundle, then current directory.

The game names its configuration `2ship2harkinian.json`.
[SaveManager.cpp](https://github.com/HarbourMasters/2ship2harkinian/blob/3.0.1/mm/2s2h/SaveManager/SaveManager.cpp)
names save records `file1.json` through `file3.json`, their backup variants,
and `global.json`. Do not invent Korri-specific replacements for these files.

The README documents OpenGL for Linux, not Vulkan. The pinned
[mm/CMakeLists.txt](https://github.com/HarbourMasters/2ship2harkinian/blob/3.0.1/mm/CMakeLists.txt)
applies SSE compiler flags only when `CMAKE_SYSTEM_PROCESSOR` matches x86_64.
This is evidence for attempting an ARM build, not evidence that it works.
The native package override enables both Linux architecture evaluations;
actual build and runtime checks remain required.

Both baseline native builds completed successfully. `file` identified the
x86 game as an x86-64 ELF, and the ARM game and extractor as aarch64 ELF files.
Both outputs contain `2ship.o2r`, controller mappings, and `assets/extractor/ZAPD.out`.
These checks establish construction and architecture, not gameplay.

Runtime testing exposed an upstream shutdown deadlock. The main thread was in
`pthread_cond_destroy` during static destruction after `Ship::ShutdownHandler`
called `exit(1)`. The audio worker still waited in `OTRAudio_Thread`.
The original package failed `nix/2ship-runtime-check.py` with
`Native shutdown hung after SIGINT/SIGTERM`.

`linux-shutdown.patch` installs flag-only signal handlers after upstream's
`InitCrashHandler` and before audio initialization. The graph loop reads that
flag and returns through `DeinitOTR`, where `OTRAudio_Exit` joins the worker.
It does not allocate, log, invoke SDL, or destroy objects in signal context.
This adds a downstream patch to maintain when the pinned engine is updated.

ARM testing then reached startup and save creation but exited with status 32.
Upstream maps `void SDL_main` to `void main` on Linux. The patch now uses an
`int` entry point and returns zero after `Heaps_Free`, rather than letting the
launcher suppress error statuses. Both corrected native builds passed the
owned-ROM test, including successful SIGINT/SIGTERM exit statuses.

A separate ARM test-environment failure came from `xvfb-run` reusing occupied
display `:99`, which lacked a usable GLX visual. A fresh display provided
llvmpipe OpenGL 4.5. The test now uses Xvfb `-displayfd`, Xauthority, and owned
process cleanup, matching `nix/nocturne-owned-check.py`. No production graphics
library or renderer change was needed.

## Boundaries and outstanding work

The nixpkgs package classifies the closure with CC0, MIT, and unfree licenses.
Do not infer public redistribution permission from the root license alone.
No ROM or extracted game archive belongs in a Nix output or cache.
This work has not approved signed publication or device installation.

The plugin now follows Core's existing `PluginLaunchInput.accountRoot`,
`PluginLaunchOutput`, and hash-bound runner contracts. Its writable directory
is `<accountRoot>/2ship`: `2ship` comes from upstream `appShortName` and its
SDL preference-directory consumer. `SHIP_HOME` selects that directory.
The first-party libretro producer already defines system `n64` and the three
ROM extensions. No new Core schema or save format was introduced.

The native wrapper copies `Extract::CallZapd`'s argument sequence. It validates
the normalized ROM against upstream SHA-1, extracts with the packaged executable
in a private temporary directory, and atomically installs `mm.o2r`. It reuses
archives only when native `portVersion` and `version` records match, required
resources exist, and ZIP CRCs pass. The records come from pinned
`OTRExporter/OTRExporter/Main.cpp`, not a plugin-specific cache schema.

Real x86 extraction of the owner's ROM produced 50,496 archive entries and a
36,258,854-byte `mm.o2r`. `portVersion` is `01000300000001`; `version` is
`015354631c`. All entry CRCs passed. Software-rendered startup reached the
name-entry screen and accepted keyboard input.

The final `verify-2ship` passed on both architectures. It exercised keyboard
save creation, archive reuse with the normalized ROM, save retention after
restart, concurrent-launch refusal, SIGINT/SIGTERM shutdown, stop at the first
visible window, failed-staging preservation, and incomplete-archive regeneration.

| Architecture | Verification |
|---|---|
| x86_64 Linux | Built and ran `nix run .#verify-2ship` on the local build machine. |
| aarch64 Linux | Built the `verify-2ship` package on the configured ARM builder, then ran its exact prebuilt program on `fuji`. |

The test uses A to advance the title/file screens and enter a name before Start.
A failed earlier sequence selected END while the name was empty; ARM screenshots
identified that test error. No production input change was needed.
Its Xvfb window checks are not automated pixel validation. PNG captures on both
architectures were visually inspected separately. Physical audio/controllers
and full-game completion are not established.

Both architecture package gates pass: packaged source typechecking, generated
manifest, host admission, real sandboxed launch preparation, literal paths,
and invalid-ROM rejection without changes to existing assets/config/saves.
These gates do not establish publisher trust, installation, or gameplay.

Local inspection clone: `/tmp/korri-2ship-upstream`. Worktree:
`/home/simonwjackson/code/github/simonwjackson/korri-plugins/.worktree/2ship`,
branch `feat/2ship`. Native build probes run on the x86 build machine and its
configured ARM builder, never on a target device.
