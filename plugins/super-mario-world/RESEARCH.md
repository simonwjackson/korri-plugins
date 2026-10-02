# Super Mario World native plugin investigation

Investigated 2026-10-02 against `snesrev/smw` commit
`eae20c65c58930c8b62c76188d259579ad4130f1`.
Evidence below comes from the pinned source, the owner's ROM, native builds,
and real packaged launch tests. Earlier inventory claims are not used as evidence.

## Verified source behavior

- [README](https://github.com/snesrev/smw/blob/eae20c65c58930c8b62c76188d259579ad4130f1/README.md)
  calls this a reverse-engineered reimplementation and says the game is playable
  from start to end. That is an upstream claim, not our gameplay acceptance result.
  It uses LakeSnes PPU and DSP code. Do not describe it as containing no emulation.
- [Makefile](https://github.com/snesrev/smw/blob/eae20c65c58930c8b62c76188d259579ad4130f1/Makefile)
  compiles C sources with SDL2 and libm. `make smw` builds the engine without ROM
  extraction. The default `all` target also creates `smw_assets.dat` from retail data.
- [LICENSE.txt](https://github.com/snesrev/smw/blob/eae20c65c58930c8b62c76188d259579ad4130f1/LICENSE.txt)
  contains an MIT license for snesrev and elzo_d, plus an Opus notice. Preserve the
  supplied license. This is not permission to distribute Nintendo ROMs or extracted assets.
- [assets/util.py](https://github.com/snesrev/smw/blob/eae20c65c58930c8b62c76188d259579ad4130f1/assets/util.py)
  accepts the USA ROM with SHA-1 `6B47BB75D16514B6A476AA0C73A683A2A4C18765`.
  Its copier-header test only matches lengths whose low 20 bits equal 512.
  This misses the owner's 524800-byte headered ROM. Removing the first 512 bytes
  from a temporary copy yields the required SHA-1. Preserve hash checks.
- [assets/restool.py](https://github.com/snesrev/smw/blob/eae20c65c58930c8b62c76188d259579ad4130f1/assets/restool.py)
  accepts `--rom PATH`. Its `--no-include-rom` option excludes the verification ROM.
  [compile_resources.py](https://github.com/snesrev/smw/blob/eae20c65c58930c8b62c76188d259579ad4130f1/assets/compile_resources.py)
  otherwise embeds the ROM in `smw_assets.dat` and writes that file in the current directory.
  Local extraction with `--no-include-rom` produced 353820 bytes. The native game
  started without the normalized ROM after extraction.
- [src/main.c](https://github.com/snesrev/smw/blob/eae20c65c58930c8b62c76188d259579ad4130f1/src/main.c)
  consumes `--config PATH` first. Supplying it skips the executable-directory search.
  Assets come from `smw_assets.dat` or `assets/smw_assets.dat` relative to the working directory.
  Startup creates `saves/`. Passing a ROM argument alone does not replace the required assets.
- [src/config.c](https://github.com/snesrev/smw/blob/eae20c65c58930c8b62c76188d259579ad4130f1/src/config.c)
  otherwise tries `smw.user.ini`, then `smw.ini`.
  [smw.ini](https://github.com/snesrev/smw/blob/eae20c65c58930c8b62c76188d259579ad4130f1/smw.ini)
  provides native settings and controller mappings. It names SDL, SDL-Software,
  and OpenGL output methods. Renderer and controller behavior remain untested.
- [src/common_rtl.c](https://github.com/snesrev/smw/blob/eae20c65c58930c8b62c76188d259579ad4130f1/src/common_rtl.c)
  stores SRAM as `saves/<game title>.srm`, with a `.bak`, and snapshots under `saves/`.
  Preserve this native layout rather than inventing new save formats.

## Verification

`engine.nix` builds the executable, asset tools, configuration, and license without
retail assets. Native builds passed locally on x86_64 and on the configured aarch64
builder `fuji`. No target device compiled anything. The locked nixpkgs `SDL2` resolves
to `sdl2-compat`.

| Check | x86_64 Linux | aarch64 Linux |
|---|---|---|
| Native build and missing-assets refusal | Passed locally. | Passed on `fuji`. |
| Packaged TypeScript contract, manifest and host admission | Passed. | Passed. |
| Sandboxed launch with literal paths and invalid-input preservation | Passed. | Passed. |
| Owned-ROM startup, snapshot write/reload, config preservation | Passed. | Passed on `fuji`. |
| Headered and normalized input, concurrent-launch refusal | Passed. | Passed on `fuji`. |
| Physical graphics, audio, controllers, complete gameplay | Not tested. | Not tested. |

The owned-ROM test is `nix/smw-runtime-check.py`, exposed as `nix run .#verify-smw`.
It exercises the packaged source through Core's actual `plugin-launch` executor.
Tests used the headered file below, dummy SDL video/audio, and SDL-Software output.
They removed all temporary retail data and verified the source file stayed unchanged.
The same test ran on the ARM build machine using its prebuilt package and Core.
These results do not establish device acceptance or widescreen support.

## Integration grounding

The existing Skate 3 plugin demonstrates exact-release runner selection, native
package registration, host admission, and `launch.prepare`. Korri's
`ArtifactIdString` only accepts whole-file `sha256:<64 lowercase hex characters>`.
The upstream SHA-1 above is not a valid runner release identifier. Do not invent a
SHA-256 or claim every SNES ROM works.

The user supplied their SNES library directory. The selected file is
`Super Mario World (U) [!].smc`. No matching save file existed beside it.
Measurements from the actual file, not a catalog, are:

| Form | Bytes | SHA-256 |
|---|---:|---|
| Whole file with copier header | 524800 | `d70c9c7716ad12c674fc7dd744736aa48d4d7b4237f58066be620fda26024872` |
| Header removed in temporary copy | 524288 | `0838e531fe22c077528febe14cb3ff7c492f1f5fa8de354192bdff7137c27f5b` |

The normalized copy matches upstream's SHA-1. Only these measured representations
are advertised. Other ROM hacks in the library are not accepted by extension alone.

The user approved separate account storage after reviewing its backup and portability
cost. The layout is `<accountRoot>/smw`, using Core's existing account-root treaty,
the upstream executable name, and upstream's native filenames. No legacy SMW runner
existed to migrate. The legacy `smwcentral` plugin is an acquisition plugin.

The SNES identity and title follow the publisher's existing
`plugins/libretro/cores.nix` at `4f2ca37bfacdb475bf112292d62f60dcbde0eabc`.
The plugin adds a native route to the existing game. It ships no retail assets,
performs no target compilation, and adds no configuration schema or service.

Signed binary publication and physical-device installation remain outside the
verified work. No publisher trust, permission, or signature checks were changed.
