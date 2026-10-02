# Jak and Daxter trilogy

`@simonwjackson:opengoal` supplies OpenGOAL 0.3.8 for Linux x86_64 with AVX and desktop OpenGL 4.3. It has separate runners for Jak and Daxter: The Precursor Legacy, Jak II, and Jak 3. Jak II: Renegade uses the Jak II runner.

The user chose x86_64 first. Linux ARM is deferred. Upstream now ships an Apple Silicon build, so the old claim that OpenGOAL has no ARM backend is false. That macOS build does not establish Linux ARM support. See [the source evidence](../../docs/research/opengoal-support.md).

## Package boundary

The plugin includes the prebuilt runtime, native resources, and ISC license. It contains no retail game data. Its native runtime closure contains no OpenGOAL extractor, GOAL compiler, or C/C++ compiler executables.

`opengoal-tools` is a separate build-machine output. It contains upstream's extractor, GOAL compiler, and source resources. The plugin does not depend on it. There is no first-launch extraction, compilation, download, or automatic update on a target device.

The Linux release archive is pinned by SHA-256 in `package.nix`. The package patches its ELF loader and library search paths for Nix. It includes SDL's dynamically loaded graphics/audio libraries. Only optional Steam storage and PowerVR GLES libraries are excluded. A compatible device graphics driver remains required.

## Prepare your owned discs off-device

Run on an x86_64 build machine, never on a target device. Extract the `.7z` archive first. Keep the original archive and ISO unchanged.

```sh
nix run .#prepare-opengoal -- \
  --game jak2 \
  --iso '/path/to/owned/Jak II.iso' \
  --output '/path/to/new-prepared-data'
```

Use `jak1`, `jak2`, or `jak3`. Renegade uses `jak2`. The output parent must exist and the output directory must not exist. The command refuses existing paths, including symlinks. It copies the pinned upstream data tree, validates the disc, extracts its data, and compiles x86 GOAL code. It does not launch the game. Failed extraction/compilation removes its temporary data without publishing an output directory. A failure while publishing files can leave a partial new directory; do not register it.

Transfer the complete prepared directory to the device, not only `GAME.CGO`. Keep all upstream folders and filenames. Do not put retail assets or compiled game files in this repository, the plugin's Nix closure, or a public cache.

## Library input and launch

The library input is upstream's `out/<game>/iso/GAME.CGO` inside that prepared directory. This is a real game file emitted by each upstream `goal_src/<game>/game.gp`, not a Korri marker or manifest. The existing Fallout plugins use the same regular-file input pattern with `MASTER.DAT`.

Register the measured `sha256:` identity and file location through Core's existing library records. The plugin adds a runner to that release. It does not create game entries or claim `.iso`, `.cgo`, or any other extension. Scanning a folder alone does not register these games. The pinned Core cannot route directly to a directory, and broad `.iso` discovery conflicts with Skate 3's existing claim.

The launch callback selects the game from its runner ID, checks the upstream file-path suffix, and returns:

```sh
gk --game jak2 --proj-path '/path/to/prepared-data'
```

Core executes the approved program. The callback performs no effects, reads no game data, and changes no files. The source path comes through as one literal argument, including spaces and shell characters. Emulator cores, other game paths, and Korri launch overrides are rejected.

The hash identifies `GAME.CGO`, not its companion files or the entire installation. Core uses its recorded identity; this plugin does not rehash at launch. Missing or changed companion files can still prevent play. Different tooling versions, mods, or unmeasured editions need separate validation before extending the accepted hashes.

Saves retain upstream's `${XDG_CONFIG_HOME:-$HOME/.config}/OpenGOAL/<game>/saves` location. No save migration occurs. This preserves native behavior but does not isolate different Korri accounts using the same Linux runtime user. USA Jak II and Renegade share the native Jak II save namespace. Controller, graphics, and other settings remain in OpenGOAL's own menus.

## Verified inputs

The four archives came from the owner's `simon@myoko:~/Downloads/`. Preparation ran on zao with the pinned tools and `--instruction-set x86 --extract --validate --decompile --compile`.

| Disc | Whole ISO bytes | Whole ISO SHA-256 |
|---|---:|---|
| Jak and Daxter, USA | 1460535296 | `139086ffd50b5713ea71d3faa3d4cb1793291e3c575c0fb5418131d116481e7b` |
| Jak II, USA v1.00 | 4410671104 | `2884b2fcea2ce4e24691e7d40c7b02e2fab885d451348309f2e1db4ad6c25a15` |
| Jak II: Renegade, Europe/Australia | 4410376192 | `20d55a2c7f244b07e4ba5b596b024c180afb67826c9b22e0a572a4b02cc35ab0` |
| Jak 3, USA | 4516773888 | `e8b7486af6338790954700f8f2589c72ce6b01ba9fc644547a941fda2ca30b14` |

These ISO hashes are provenance, not runner identities. The accepted native files are:

| Input | `GAME.CGO` bytes | `GAME.CGO` SHA-256 |
|---|---:|---|
| Jak 1 USA | 8768544 | `3cda4bc7f551a51d2fa9c4d5949549237ea846ce4851437403dbe91548a52807` |
| Jak II USA | 12975344 | `6a673c9cf1e7aee115e82be459b1348fd1981fef49086569aae67a2a64c4cc14` |
| Renegade | 12975360 | `a8c829303340a1c572252e408f0730e2495d84505cdfcd94b3e34167fd9a6ad8` |
| Jak 3 USA | 14514592 | `442becdbf74aa11fe046e76c243b7ce0122d924593f6e20682ff06ae5dacd4f5` |

All four discs passed upstream validation and compilation twice. The repeat used the real `prepare-opengoal` Nix app from unrelated working directories. Each produced the same `GAME.CGO` hash and left the caller's directory unchanged. USA v2.01 is supported by upstream's validation database but was not supplied or tested here; no new identity for it is claimed.

## Build and checks

```sh
nix build --no-link .#korri-plugin-opengoal
nix build --no-link .#checks.x86_64-linux.korri-opengoal-plugin
```

The check verifies the packaged source, manifest, publisher identity, x86_64 ELF, native version, runtime/tool separation, strict launch types, host admission, and production sandboxed launch arguments. It also exercises the real extractor's rejection of invalid media and the preparation command's destination-preservation rules. It uses no retail data and proves no full game walkthrough.

## Owned-data runtime checks, 2026-10-02

| Input | Observed result on zao |
|---|---|
| Jak 1 USA | Reached the title and Press Start screen through the production plugin callback. |
| Jak II USA | Rendered Haven City and Press the Start Button through the callback. |
| Renegade | Rendered its startup city scene through the callback. |
| Jak 3 USA | Passed preparation and stayed running through the callback, but headless rendering acceptance failed. |

The graphical probes used Xvfb, Mesa software rendering, and isolated configuration directories. Jak 3 displayed its Dolby logo, then produced flat black or white frames. Sampling through 120 seconds and sending the upstream Start key did not establish a rendered game scene. Logs contain `GL_INVALID_OPERATION in glBlitFramebuffer(depth attachment format mismatch)`. The same error also appeared in Jak II logs despite visible scenes, so it does not prove the cause of Jak 3's failure. No engine patch was made. A separate native OpenGL capability probe passed on zao's NVIDIA GPU; that is not a Jak 3 gameplay test.

Do not equate a live process with playable startup. Jak 3 needs a successful visual test on a supported graphical target before gameplay acceptance. None of these probes proves audible sound, physical controller input, save reload, a systemd game unit, or a full walkthrough.

Private test data and captures remain under `/var/tmp/korri-opengoal-owned/` on zao. They are not repository files or CI artifacts. `prepared-jak1`, `prepared-jak2-usa`, `prepared-renegade`, and `prepared-jak3` contain the complete prepared directories. `repeat-*.log` records the real-app reproducibility checks. Runtime logs and `*-startup.png`/`jak3-frame-*.png` record the bounded graphical probes.

## Deployment

The supplied data host myoko has an AVX-capable x86_64 CPU, but no `korri-plugin` or `korrid` executable was found on its PATH. Its `korrid.service` was inactive. No live Korri installation or game-library registration is claimed.

The repository does not automatically publish signed packages. A target needs the bound `@simonwjackson` publisher key/cache, the exact signed output, normal approval, the prepared data, and registered game releases. Do not bypass those checks or build on the target.

After signed publication and target configuration, set `CACHE_URL` to the bound cache and `PACKAGE` to the exact plugin output. Read the inspection report, then use its `APPROVAL` value:

```sh
sudo korri-plugin inspect "$CACHE_URL" "$PACKAGE"
sudo korri-plugin install "$CACHE_URL" "$PACKAGE" "$APPROVAL"
sudo korri-plugin enable @simonwjackson:opengoal
```

These commands do not register game data. Do not use the test-only `seed` command for live installation.
