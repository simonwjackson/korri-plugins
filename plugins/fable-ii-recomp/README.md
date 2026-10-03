# Fable II

`@simonwjackson:fable-ii-recomp` adds a native runner to the existing Xbox 360 ISO release. It uses `Oery/fable-ii-recomp`, not the Windows-only `himdo/Fable-2-Recomp` release.

This is an experimental port.

| Target | Verified evidence | Not established |
|---|---|---|
| x86_64 Linux | Nix package/contract checks; owned-ISO extraction; packaged Wayland rendering, copied-save load, movement and account-local log/config lookup. The earlier source build also verified save creation and nonzero audio. | Full campaign, physical-controller acceptance, new settings-file creation and long-session stability. |
| aarch64 Linux | Nix package/contract checks, actual native ELF architecture, installed Wayland backend, real fixture extraction and launch/account guarantees. | ARM rendering, gameplay and handheld performance. |

## Owned input

Only this measured disc is registered. Other dumps need their own verification.

| Input | Bytes | SHA-256 |
|---|---:|---|
| Owner's `Fable 2 PLT.iso`, USA/Europe GOTY | 7838695424 | `2cdaafead95680e2c6fe8886a89f1ae3d5e41549857c7fc125a12aab1cb99ad9` |
| Its `default.xex` | 21217280 | `88c4ef2e18e65409444d1b068eff921d1f7e180a5ae64edc64ba6b0872372662` |

The executable is title `4D5307F1`, media `716F0A0D`, version `0.0.0.26`. No title update is applied. Oery originally used French GOTY. This package generates code from the measured USA/Europe executable and checks its exact hash.

The repository contains no ISO, XEX, generated guest code, save files or native game binaries. `game-files.json` contains only the 451 measured filenames and sizes, using Oery's existing `docs/re/game-files.json` format.

## Launch and storage

`plugin.ts` returns a launch declaration. It does not read, download, extract, write or start anything. Core supplies the selected account directory and performs the launch. The packaged native launcher handles installation and execution.

The account directory is `accountRoot/fable_ii`. `accountRoot` comes from Core's launch treaty; `fable_ii` is the upstream application name. The rest follows existing native producers:

| Relative location | Grounding |
|---|---|
| `assets-extracted/00007000` | Oery's `fable_ii_manifest.toml` game root. |
| `fable_ii.toml` | ReXGlue's application-name-based native configuration filename. |
| Native title/XUID save directories | ReXGlue's existing `user_data_root` layout, unchanged. |
| `cache/` | ReXGlue's default cache under `user_data_root`. |
| `logs/` | ReXGlue's log directory and sequential filenames. |
| `runtime/update-empty/` | Oery's `scripts/run` update root. It must stay empty. |

A narrow SDK patch moves configuration and default logs away from the read-only executable directory into `user_data_root`, following the existing Simpsons plugin. It does not introduce a Korri configuration language. Native TOML settings remain user-controlled. Core config-file overrides, typed runner settings and emulator cores are rejected.

First launch copies the ISO into a private temporary directory while checking its size and SHA-256. Extraction reads that verified copy, not a path that another process can replace after hashing. The launcher validates the native file map and XEX hash, then publishes the completed directory. It leaves the original ISO unchanged.

This needs about **15 GB free during first installation**. About **7 GB of extracted data remains per account**. The temporary ISO copy is removed afterward. The ISO must remain available for later launches, which hash it again before reusing the installed files. That check adds disk I/O. Existing invalid installations cause an error; the launcher does not erase or silently repair them. Existing settings and saves are not overwritten.

An account-directory lock prevents concurrent launches and remains held by the running process. Existing account data, including nested saves, must not contain symlinks. This adds a directory scan on launch and refuses intentionally linked saves. It is not a security boundary against another process running as the same OS user.

The runtime launcher has no compilation or download step. It calls a prebuilt extractor and game executable. No global input, display, service, key or cache configuration is changed.

## Private builds

Run these steps on a build machine, never a target device. Native builders exist for `x86_64-linux` and `aarch64-linux`; this expression does not implement cross-compilation.

Set `ISO` to the owned disc and `EXTRACTED` to a **new private extraction directory**. Verify the whole-disc hash against the table before using the extractor. Stop if either hash differs.

```sh
sha256sum "$ISO"
nix run .#fable-ii-extract-xiso -- -x "$ISO" -d "$EXTRACTED"
sha256sum "$EXTRACTED/default.xex"
nix-store --add-fixed sha256 "$EXTRACTED/default.xex"
```

The XEX becomes a fixed-hash local Nix input. Nix store files are locally readable. Do not upload that input or the generated game output to a public cache.

```sh
nix build -L --no-link --cores 3 --max-jobs 1 \
  --option builders "" --option post-build-hook "" \
  .#korri-plugin-fable-ii-recomp

nix build -L --no-link --cores 3 --max-jobs 1 \
  --option builders "" --option post-build-hook "" \
  .#checks.x86_64-linux.korri-fable-ii-recomp-plugin
```

Use the `aarch64-linux` check on an ARM build machine with the same owned XEX supplied there. Do not enable builds on a device to work around a missing prebuilt output.

The check uses the actual packaged source, generated manifest, Core admission and sandboxed launch callback. It also tests the real extractor with a small non-retail XISO, literal paths, rejection, atomic installation, account locks, cached-file preservation, native ELF architecture and the installed SDL Wayland backend. Its recording child verifies the exec boundary; it does not emulate or validate gameplay.

An additional owned-disc check needs about 15 GB of temporary free space:

```sh
nix run --option builders "" --option post-build-hook "" \
  .#verify-fable-ii -- "$ISO"
```

This runs the real callback, extracts the disc, verifies all file paths/sizes and the XEX, tests cached reuse, and reaches the actual SDL entry point. It deliberately disables the video backend. It is not a rendering, gameplay or save/reload test. The separate source-build acceptance evidence is in [the research record](../../docs/research/fable2-upstream.md).

## Sources and publication limits

| Component | Pinned source |
|---|---|
| Game | `Oery/fable-ii-recomp` at `f3ae1ad1fcb9d94bfa200ef2d3b018dec917c092`. |
| SDK | `rexglue/rexglue-sdk` at `c94f5ebdcb3c9d1a460ca48e04f9758448f8d518`, including exact recursive submodules. |
| Extractor | `XboxDev/extract-xiso` at `3f5b62cfe68f000b0e3c8a30104973f3a297948e`. |

The SDK keeps Oery's published keep-open and Vulkan tessellation fixes. No new game hooks or generated-code edits are included. Both `wayland-scanner` and EGL development files from `libglvnd` are required at build time. Missing either caused SDL to silently disable Wayland during validation; configure and installed-runtime checks now reject that result.

The packaged gameplay smoke still recorded duplicate-cvar and `BaseHeap::AllocFixed` warnings. They did not prevent the observed save-load and movement sequence. They are not diagnosed or declared harmless.

Upstream provides no root redistribution license for the game project. The compiled engine also contains code translated from the retail executable. The engine is marked unfree, and substitution is disabled for these private outputs. Those settings do **not** prevent a manual cache upload.

No binary-cache publication or target installation is approved by this package. Keep signature, publisher binding and exact-package approval checks enabled. Deployment needs a private, prebuilt delivery route and an approved target. The package must not compile anything on that target.

For a later approved ARM installation, the verified package output is `/nix/store/4683zc4b4dlg4pha11lwi9gffpmibba8-korri-plugin`. First stage and sign its closure in the publisher's already-bound private cache. Set `CACHE_URL` to that exact existing binding, then inspect on the device:

```sh
sudo korri-plugin inspect "$CACHE_URL" /nix/store/4683zc4b4dlg4pha11lwi9gffpmibba8-korri-plugin
```

Review the report before assigning its digest to `APPROVAL`. Only after approval:

```sh
sudo korri-plugin install "$CACHE_URL" /nix/store/4683zc4b4dlg4pha11lwi9gffpmibba8-korri-plugin "$APPROVAL"
sudo korri-plugin enable @simonwjackson:fable-ii-recomp
```

These are Core's existing download-only import commands, not flake builds. They do not supply signing material, establish trust, copy the ISO or constitute device acceptance.
