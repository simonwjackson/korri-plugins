# Skate 3

`@simonwjackson:skate-3` is a native launcher for the existing library game. It does not
create a separate game tile. Core must support runner `releases`, introduced
in `korri-os/korri` commit `13a074832`.

## Native package

The output is `korri-plugin-skate-3` on both Linux architectures. It uses
`packages.<system>.default` from `simonwjackson/skate-3-flake`, pinned at
`0d98437232e56c172357850db17e8503b5a81d66`.

| Architecture | Native package | Build requirements |
|---|---|---|
| x86_64 Linux | Prebuilt `skate3` launcher around upstream `Skate3Recomp-Linux.zip` v2.0.2 | No disc files at build time. The flake patches library paths. |
| aarch64 Linux | Native `skate3-source` launcher and recompiled game | Build on an ARM64 builder with the two owned XEX files below. Never compile on a target device. |

The ARM64 source build includes four runtime fixes for FFmpeg linking,
XEX delta patching, suspended threads, and null Vulkan pipelines. It also
includes the native flake's guest-memory cleanup fix. These are native
package patches, not a different plugin declaration.

`plugin.nix` names that package and its executable. `plugin.ts` declares the
runner and returns a launch plan. Neither declaration reads, hashes, writes,
downloads, or starts anything. Core performs the launch effects. The native
game installs and downloads its title update after launch.

Upstream publishes no redistribution license. The native binary contains
code generated from EA's game. Do not publish this closure to the public
plugin cache without a separate rights review and approval. A local build
and an admission check grant no publication or device installation approval.

## Accepted disc

The runner accepts this measured whole-file identity:

| Disc | Bytes | SHA-256 |
|---|---:|---|
| Skate 3 (USA, Europe) (En,Fr,De,Es,It,Nl).iso | 7838695424 | `bd8d430188aa61b0ebf2e33e5672822dd7e59c9080fc09e802195e1ee75ebff0` |

The measurement streamed the one ISO inside the owner's
`~/Downloads/Skate 3 (USA, Europe) (En,Fr,De,Es,It,Nl).zip` on aka. Python's ZIP
reader checked its CRC while reading. The archive stayed unchanged and no
ISO was extracted to disk. This is not the archive hash or the game's XEX
hash. Other dumps are not accepted until measured and verified.

The field follows Core's `RunnerRecord.releases` and existing
`config::ArtifactIdString` validator. Several accepted entries would mean
any one dump. The `@simonwjackson` namespace follows the personal publisher
composition already used by this repository's PICO-8 worktree. Native launch variables come from the pinned flake's
`launcher.nix`, not a new Korri configuration schema.

## Launch and limits

Core passes the matched file through `PluginLaunchInput.contentPath`. The
callback sets `SKATE3_INSTALL_ISO` to that exact path and sets
`SKATE3_INSTALL_TU=download`. The native launcher handles writable game data,
logs, first-run windowing, and library paths. The game needs internet for its
first title-update download and a working Vulkan driver at
`/run/opengl-driver`. Later launches reuse the installed game files.

Discovery needs the bare `.iso` in an existing library folder. The ZIP is
not discoverable through this claim. The claim assigns `.iso` to `xbox-360`;
a different system claiming `.iso` still causes Core's `ClaimConflict`.
The plugin adds no archive extraction, hash-based discovery, or launch-time
rehashing. Both architectures use the same hash gate and launch callback.

On the Mini V2, a manual ARM64 trial froze presentation during intro movies
while audio continued. ARM64 packaging does not fix that renderer bug or
establish gameplay performance. Controls must use a normal korrid launch;
a process started outside korrid does not receive the protected Korri seat
input. Installation alone does not prove that route works.

## Build and verify

Run these commands on a build machine, never on a device. Before an ARM64
build, add the original `default.xex` and `data/webkit/EAWebkit.xex` from your
owned Xbox 360 disc to that builder's Nix store. The pinned native flake's
`requireFile` declarations verify their hashes. These commands use the
existing native launcher's installed-game paths:

```sh
nix-store --add-fixed sha256 \
  ~/.local/share/skate3/game/default.xex \
  ~/.local/share/skate3/game/data/webkit/EAWebkit.xex
```

The source build fetches the pinned Title Update 3 and applies it during
code generation. Do not provide already patched XEX files. Keep the inputs
and generated output private; ordinary public CI cannot build this package
without the owned inputs.

| Builder | Package command | Check command |
|---|---|---|
| x86_64 Linux | `nix build --no-link .#packages.x86_64-linux.korri-plugin-skate-3` | `nix build --no-link .#checks.x86_64-linux.korri-skate3-plugin` |
| aarch64 Linux | `nix build --no-link .#packages.aarch64-linux.korri-plugin-skate-3` | `nix build --no-link .#checks.aarch64-linux.korri-skate3-plugin` |

On either builder, `nix build --no-link .#korri-plugin-skate-3` selects its
native architecture. The check uses the actual packaged source. It typechecks against Core's
exported contract, checks the generated manifest and measured hash, runs
host admission, and invokes the production sandboxed callback and launch
executor with the real `env` program. Paths with spaces and shell syntax
must reach `SKATE3_INSTALL_ISO` unchanged. The check performs no game
installation or download. It does not establish gameplay, controller, or
device acceptance. Installation still needs a compatible Core runtime,
normal signature and permission checks, and a selected device.
