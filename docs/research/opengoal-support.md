# OpenGOAL support evidence

Initial upstream research checked 2026-10-02. The user first chose x86_64, then approved native Linux ARM work. The [ARM report](opengoal-arm-support.md) records the later source port, native tests and four owned-data rendering probes. Mini V2 deployment remains gated on explicit readiness approval.

## Architecture correction

The [official FAQ](https://opengoal.dev/docs/faq/) still says the compiler only supports x86_64. That statement is stale.

The [v0.3.8 release](https://github.com/open-goal/jak-project/releases/tag/v0.3.8), published 2026-09-20, includes native Apple Silicon support. [PR #4390](https://github.com/open-goal/jak-project/pull/4390) merged on 2026-08-25 at `de25f394394187fe800d55505a426c18139f119e`. Its description covers the compiler, runtime, linker, kernel, and GOAL assembly. The release also includes #4419 and #4420, which change the compiler and extractor defaults on ARM.

The parent session fetched the complete GitHub release and PR API responses. These replace the initial research agent's search excerpts. The table describes upstream release evidence; it is not the later local port's acceptance report.

| Architecture | Direct evidence | Limit |
|---|---|---|
| Linux x86_64 | Installation docs require x86_64 with AVX. v0.3.8 ships `opengoal-linux-v0.3.8.tar.gz`. | Binary and runtime verification remain separate from documentation. |
| macOS ARM | v0.3.8 ships `opengoal-macos-arm-v0.3.8.tar.gz`. The merged PR reports native Apple Silicon execution. | This is not a Linux package. |
| Linux ARM | No separate Linux ARM asset appears in the v0.3.8 release. | Our later Linux port is separate from the upstream release. It uses the existing ARM compiler backend. |

The [top-level CMake file](https://github.com/open-goal/jak-project/blob/v0.3.8/CMakeLists.txt) still supplies `-mavx` for GCC and non-Apple Clang. AppleClang has separate architecture handling. This is a Linux ARM investigation point, not proof that all ARM code is absent.

## Game and runtime requirements

The FAQ says all three games are feature complete and fully completable. Jak II and Jak 3 remain beta because of audio and graphics issues. This is upstream's claim, not a local completion test.

The upstream Linux binary requires desktop OpenGL 4.3 and an AVX-capable x86_64 CPU. The FAQ recommends at least 2 GiB of available RAM. Our native ARM runtime has separate CPU requirements documented in its plugin instructions. OpenGL ES or Vulkan support alone does not prove compatibility.

## Game preparation

The [installation guide](https://opengoal.dev/docs/usage/installation/) requires a user-supplied retail PS2 disc image. It excludes demos and later PlayStation ports. Its documented commands are:

```sh
./extractor --game jak1 /path/to/owned.iso
./gk --game jak1
```

Replace `jak1` with `jak2` or `jak3` for the other games. The extractor workflow includes GOAL compilation. Korri forbids compilation on target devices, so do not put extraction and compilation in a first-launch target script. Inspect the source and output layout before defining the off-device preparation and transfer workflow.

The FAQ locates Linux saves at `~/.config/OpenGOAL/<GAME>/saves`. Preserve upstream save behavior rather than introducing a Korri-specific save schema.

## Package evidence

The release API records the Linux archive SHA-256 as `c98fc713e831f65f2954c680f4be4f2bc0259c308f9538284c06fee9429b089d`. This identifies engine tooling, not a retail ISO or prepared game.

Existing repository integration follows `plugins/skate-3/plugin.ts` and `plugin.nix`: an effect-free launch declaration plus native package/file references. The Skate 3 runner uses a measured whole-ISO hash. Do not reuse that game's identity, invent Jak hashes, or assign every `.iso` to PlayStation 2. Core currently rejects conflicting extension discovery claims.

## Implementation evidence

The Linux archive's measured SHA-256 matches the release API. Its `gk`, `extractor`, and `goalc` executables are x86_64 ELF files. The runtime and off-device tools are separate Nix derivations. The runtime closure contains no preparation or compiler executables.

The native extractor defaults to running every stage, including launch. Preparation therefore passes explicit `--extract --validate --decompile --compile --instruction-set x86` flags. It also sets both `--proj-path` and the process working directory to its isolated data tree. A regression check proved that omitting the working-directory setting fails isolation. Upstream actor compilation creates relative directories despite the project-path flag.

The owner supplied three USA discs and Jak II: Renegade from myoko. All four passed validation and compilation on zao. The plugin uses the observed upstream `out/<game>/iso/GAME.CGO` outputs as existing regular-file release identities. It does not claim directory discovery or broad ISO matching. [The plugin instructions](../../plugins/opengoal/README.md) record measured hashes, runtime evidence, and remaining deployment limits.

Package admission and the production callback/executor tests pass. Those tests do not establish audible audio, controllers, save reload, full gameplay, signed publication, or live deployment. Those remain separate acceptance steps.
