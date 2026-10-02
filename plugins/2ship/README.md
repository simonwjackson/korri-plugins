# 2 Ship 2 Harkinian

`@simonwjackson:2ship` adds a native Majora's Mask runner to an existing library
game. It does not add a separate game tile or include Nintendo game data.
The package targets x86_64 Linux and aarch64 Linux, not 32-bit ARM or Android.

## Input

Extract the bare ROM from your own ZIP before adding it to an existing library
folder. Discovery uses the existing `n64` system and `.n64`, `.z64`, `.v64`
extensions. The runner matches only these measured 32 MiB NTSC-U 1.0 identities:

| Whole-file form | SHA-256 |
|---|---|
| Owner's byte-swapped `.n64` | `8dc31559174f958a938ab7eccb25dd310a4167f98cb68a521181f4653b684431` |
| Same ROM in big-endian order | `efb1365b3ae362604514c0f9a1a2d11f5dc8688ba5be660a37debf5e3be43f2b` |

The wrapper validates upstream's SHA-1 after normalizing byte order. The filename
alone grants no compatibility. Other revisions, GameCube dumps, patched ROMs,
and existing game archives are not supported by this runner. ZIP extraction is
not part of this plugin. [Source and hash evidence](UPSTREAM.md) records the
measurements and upstream contracts.

## Native package and launch

The plugin reuses the pinned nixpkgs 2 Ship 3.0.1 package and dependencies.
`native-package.nix` pins source commit
`f45acdd794712fefa0fae0bca86dcac22e040f09`, fixes its source-fetch reproducibility,
and enables the aarch64 build. This is not a claim to package the latest release.
It also applies `linux-shutdown.patch` so SIGINT/SIGTERM request normal game
teardown rather than deadlocking in static audio destruction. The patch fixes
the native entry point's undefined return status on ARM.

`plugin.ts` contains declarations only. Core creates the writable directory and
starts the approved native wrapper with the literal ROM path. The wrapper
validates the ROM, invokes the packaged ZAPD extractor when needed, and replaces
itself with the game. Targets receive prebuilt native programs. Extraction
processes user data; it does not compile code or download anything.

Persistent data goes under `<accountRoot>/2ship`. Core supplies `accountRoot`;
`2ship` is upstream's own app-directory name. `SHIP_HOME` selects that directory.
The wrapper holds an account-directory lock until the game exits, preventing
concurrent sessions from overwriting the same native saves.

| Native path within the directory | Owner and behavior |
|---|---|
| `mm.o2r` | The wrapper extracts this game archive in a private temporary directory and installs it atomically. It reuses archives with matching native version records, mandatory resources, and valid ZIP CRCs. |
| `2ship2harkinian.json` | The game owns configuration. The wrapper never creates or replaces it. |
| `saves/` | The game owns its JSON saves and backups. The wrapper does not migrate emulator saves. |
| `mods/`, `logs/`, `imgui.ini` | Upstream owns these runtime files. |

First extraction took about 18 seconds on the tested x86 build machine. Runtime
checksums add work to each launch. An invalid ROM or failed extraction leaves
existing archives, configuration and saves unchanged. A failed game startup can
leave a successfully extracted archive for the next attempt.

This package uses upstream's Linux OpenGL renderer and default controls. It does
not force graphics settings, fullscreen, or controller mappings. Performance and
physical controls still need testing on each handheld. Do not reuse an arbitrary
shared `SHIP_HOME`; the wrapper binds it to Core's selected working directory.

## Build and verify

Run on build machines, never target devices:

```sh
nix build --no-link .#korri-plugin-2ship
nix build --no-link .#checks.x86_64-linux.korri-2ship-plugin
nix build --no-link .#checks.aarch64-linux.korri-2ship-plugin
```

The package gate checks the actual packaged TypeScript against Core's generated
contract, generated metadata, host admission, sandboxed launch preparation,
paths containing shell syntax, and invalid-ROM rejection without data changes.
CI runs that gate for both architectures without retail assets.

The optional runtime test needs your measured bare ROM:

```sh
nix run .#verify-2ship -- /path/to/owned/USA-ROM.n64
```

It uses temporary account data, Xvfb software rendering, and dummy audio. It tests
first extraction, keyboard-driven save creation, archive reuse with both ROM byte
orders, concurrent-launch refusal, save retention, SIGINT/SIGTERM shutdown, and
regeneration of an archive containing version records but no game resources.
Both x86_64 and aarch64 passed this test on 2026-10-02. The ARM run used the
exact prebuilt test program on the configured ARM build machine.
It deletes its temporary game data. It does not establish physical-display,
audio, gamepad, full-game completion, or signed-device installation acceptance.

## Publication boundary

The native package retains nixpkgs' unfree classification alongside its CC0/MIT
license declarations and notices. Building it does not approve redistribution of
its binary closure. No ROM or generated `mm.o2r` enters a Nix output, Git commit,
or public cache. Review redistribution rights before publishing the closure.

This repository does not yet provide a signed publication or device-installation
workflow for this plugin. Device installation needs a selected target, its bound
publisher key/cache, and normal exact-package approval. Keep signature and
permission checks enabled. Do not use a local admission test as proof of trust.
