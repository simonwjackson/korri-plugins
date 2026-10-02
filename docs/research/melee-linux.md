# Melee Linux integration evidence

Checked 2026-10-02. The user chose `999sian/melee-pc` after reviewing the beta
limitations. Scope is native Linux x86_64 and aarch64 packaging and tests, not
public binary publication or device installation.

## Source and release

`doldecomp/melee` builds a GameCube `main.dol`, not a Linux game. The selected
port builds on that decompilation with aurora, SDL3, and Dawn/WebGPU.

- [Original build target](https://github.com/doldecomp/melee).
- [Pinned port source](https://github.com/999sian/melee-pc/tree/ed0843a6f0d7cbd846e7774925fc0952c522ed95).
- [Release v0.2.2-beta](https://github.com/999sian/melee-pc/releases/tag/v0.2.2-beta), published September 25, 2026.

The tag resolves to `ed0843a6f0d7cbd846e7774925fc0952c522ed95`. Both tarballs
were downloaded. Their sizes and measured SHA-256 values match GitHub's release
API. ELF inspection, not filename inference, confirms both architectures.

| Archive | Bytes | ELF machine | SHA-256 |
|---|---:|---|---|
| `melee-linux-x86_64.tar.gz` | 15,122,696 | x86-64 | `4d6183c93701c84d268b6d88128949470755e5bd35026024e535a0ba1568b05e` |
| `melee-linux-aarch64.tar.gz` | 14,660,118 | AArch64 | `a0ca17d43d8cef1a8d91d171acf74c6d58ef2f2f77324e9cef6367ee3c299a67` |

Downloads are under the release's `releases/download/v0.2.2-beta/` URL.
Both contain `melee`, `resources/`, `initial_pipeline_cache.db`, and bundled
`lib/libusb-1.0.so.0`. Direct linked dependencies include OpenSSL, curl, SQLite,
libstdc++, libgcc, and glibc. SDL and Vulkan also load runtime libraries.

## Owned input

The user supplied `Super Smash Bros. Melee (USA) (En,Ja) (v1.02).7z` on `myoko`.
The archive's named ISO member was extracted into private temporary storage on
the build machine. The source archive was not changed.

| Property | Measured value |
|---|---|
| Raw ISO bytes | `1459978240` |
| Header identity | `GALE01`, disc 0, revision 2 |
| SHA-1 | `d4e70c064cc714ba8400a849cf299dbd1aa326fc` |
| SHA-256 | `0de05981a34156b9cedcef73c73d4244ac05cf6149ab3c9cfed917698819e464` |

SHA-1 and size match the [port's disc reference](https://github.com/999sian/melee-pc/blob/ed0843a6f0d7cbd846e7774925fc0952c522ed95/README.md).
The plugin's release identity uses the measured whole-file SHA-256, following
Korri's existing `RunnerRecord.releases` contract. That contract does not require
`systems`. This slice adds no GameCube system identifier or broad ISO discovery
claim. It attaches to the measured release once registered in the library.
Compressed images require separate measured identities before admission, even
though the engine itself can read several compressed formats.

## Native launch and storage contract

The [pinned main.c](https://github.com/999sian/melee-pc/blob/ed0843a6f0d7cbd846e7774925fc0952c522ed95/src/pc/main.c)
parses `--dvd PATH`, `--version`, and `--no-card`. Use `--dvd` with one absolute
ISO path. Do not pass `--no-card` for normal launches.

The source uses `SDL_GetPrefPath(NULL, "melee-pc")` for user data. Setting
`XDG_DATA_HOME` to Korri's supplied account root preserves the native
`melee-pc` directory. The native `MELEE_CACHE_DIR` override controls the cache.
Settings, cards, and controller bindings must survive package updates.
`SDL_GetBasePath()` locates `resources/` beside the executable.

`pc_env_file_bootstrap` reads `melee-env.txt` from the working directory. Keep
the working directory in the immutable package, not the disc library or mutable
account directory. Clear inherited overrides that can redirect native state.

## Updater constraints

The [pinned updater](https://github.com/999sian/melee-pc/blob/ed0843a6f0d7cbd846e7774925fc0952c522ed95/src/pc/updater.cpp)
has no inspected disable switch. It can check GitHub for releases. It downloads
to `HOME/Downloads` if that directory exists, otherwise to the working directory.
On Linux, replacement and relaunch require `APPIMAGE`.

The managed tarball wrapper must unset `APPIMAGE`, keep HOME and the working
directory in the immutable package, and use XDG paths for account-owned state.
This prevents its updater writing a replacement or restarting an AppImage. It
does not disable update checks or network play. An update attempt can show an
upstream download error. Do not claim the updater has been removed or disabled.

## Limits and rights

The release warns: "Beta, for testing only. Expect crashes and missing features."
Upstream reports all game modes playable. These reports do not establish Korri
acceptance or a full playthrough. Linux needs Vulkan 1.1. ARM64 packaging does
not establish compatibility with every ARM GPU or handheld. Shader compilation
can cause stutter or temporarily missing effects. Netplay remains experimental.

The [license statement](https://github.com/999sian/melee-pc/blob/ed0843a6f0d7cbd846e7774925fc0952c522ed95/README.md#license)
distinguishes unlicensed recovered game code from GPL-3.0-or-later port code.
No retail data files in an archive does not imply permission to redistribute
its compiled game code. Keep binary closures private pending rights review and
publication approval. Package source must contain no disc, extracted assets,
memory cards, or compiled game binary.

Package and owned-disc test results belong in `plugins/melee-pc/README.md` once
run. Source inspection alone does not prove user-state isolation, updater
containment, rendering, audio, save/reload, or clean exit.
