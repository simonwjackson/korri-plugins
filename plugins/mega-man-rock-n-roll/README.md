# Mega Man Rock N Roll

`@simonwjackson:mega-man-rock-n-roll` declares Dennis Engelhard's Mega Man Rock N
Roll, public Linux 1.3 build, and plays it with a native Godot 2.1.4 runtime.
The ZIP holds `data.pck` (a Godot 2.1 pack) and `MegaMan_RocknRoll`, the stock
x86_64 export template "Godot Engine v2.1.4.stable.official". The template has
no custom modules, so stock Godot 2.1.4 and `data.pck` are the whole game. The
plugin builds Godot 2.1.4 from source for aarch64 and x86_64 and never runs the
ZIP's x86_64 executable. No x86 emulation is used.

It is the first game whose files korrid downloads (Korri ADR 0013,
`docs/adr/0013-declared-games-can-come-from-artifacts.md` in `korri-os/korri`).
The plugin ships only the URL and the SHA-256 values. The ZIP is not in the
plugin closure, and no build or check downloads it.

It was written in `korri-os/korri` (`plugins/mega-man-rock-n-roll`) and moved
here on 2026-10-20 under the `@simonwjackson` namespace. It first ran under
FEX. On the RG353M, x86 GLX under FEX got no fbconfig on Panfrost, so on
2026-10-21 the FEX runner, its FEX build, configuration and `@korri:fex/rootfs`
artifact were replaced by this native runner.

## Core requirement

The release's `artifacts` and its object `file`, and the `artifacts` launch
input need a Core with ADR 0012 and ADR 0013. The flake pins a Korri commit
that has both. The runner needs no artifact besides the game's own ZIP.

The package and both checks build on x86_64-linux and aarch64-linux. korrid
downloads the game's ZIP (97.5 MB) before the first launch.

## Declaration

| Export | Key | What it declares |
|---|---|---|
| `artifacts` | `game` | `@simonwjackson:mega-man-rock-n-roll/game`, version `1.3`: the ZIP's URL, `sha256:af916d57…abd9` and 97511960 bytes; unpack program `game-unpack` |
| `games` | `mega-man-rock-n-roll` | One release, `1.3`: `hashes` is the SHA-256 of `data.pck`; `artifacts` and `file` name `data.pck` in the `game` artifact |
| `runners` | `godot` | `@simonwjackson:mega-man-rock-n-roll/godot`: program `godot-launch`, `releases` holds the `data.pck` hash (`sha256:eb6fc015…bd41`), no `artifacts` |
| `handlers` | `launch.prepare` | The launch plan below |

There are no `systems`: the runner accepts the release by its hash
(SCRIPTING.md, "Native runners for specific content").

The plugin requires no other publisher's package and names no other plugin's
artifact.

## Files

| Key | File |
|---|---|
| `game-unpack` | `mega-man-rock-n-roll-unpack`: unpacks the verified ZIP; korrid runs it, the runner does not |
| `godot-launch` | `mega-man-rock-n-roll-godot`: the runner program, with `godot2-runtime` on its `PATH` |

The manifest also lists the package `godot2-runtime`, the engine that
`godot2/package.nix` builds.

## Godot 2.1.4 runtime

`godot2/package.nix` builds the engine from the upstream tag `2.1.4-stable`
(`github:godotengine/godot`, pinned by SHA-256) as an X11 export template:
`platform=x11 tools=no target=release bits=64`. The binary is
`bin/godot2-runtime`. Godot Engine is MIT licensed. The package installs
`LICENSE.txt` and `COPYRIGHT.txt` (third-party notices) under
`share/licenses/godot2-runtime`.

Build changes, each for one reason:

| Change | Reason |
|---|---|
| `clangStdenv`, `use_llvm=yes` | `platform/x11/detect.py` refuses GCC 6 and later for 2.1 and names Clang |
| `CXXFLAGS=-std=gnu++98` | The code is C++98 (`register`, narrowing in braces); Clang 21 defaults to C++17 |
| `CCFLAGS=-fno-delete-null-pointer-checks` | The engine tests and calls through null `Object` pointers; without it the x86_64 build crashed in `VisualServerRaster::_render_canvas_item` on the game's first scene |
| `builtin_openssl=yes` | 2.1.4 supports OpenSSL 1.0.x only; Nix has 3.x |
| Bundled GLEW 1.13, plus `libGLU` headers | System GLEW's header needs C++11; the bundled `glew.h` includes `GL/glu.h` |
| System freetype, libpng, zlib, libogg, libvorbis, libtheora, opus/opusfile, libwebp | The SCons options allow them |
| `scons-python3.patch` | Python 3 and SCons 4 for the build scripts this build reads (`print`, `string.split`, `has_key`, text-mode writes); `ENV=os.environ` so the Nix compiler wrapper sees its variables; a `CXXFLAGS` option |
| `aarch64-safe-refcount.patch` | 2.1.4 has reference counting for x86 and 32-bit ARM only; AArch64 gets the GCC atomic builtins that 2.1.6 uses |
| `postPatch` removes every platform except `x11` | `SConstruct` imports each platform's `detect.py`, and the others are Python 2 |

The version banner reads `v2.1.4.stable.custom_build`. The bundled OpenSSL is
1.0.2l from 2017. Only Godot's SSL classes use it.

## `game-unpack <work-dir> <zip>`

korrid invokes it with the verified ZIP (ADR 0012).

1. It refuses the whole ZIP before it writes anything if an entry is a
   symlink or another special file, is absolute, contains `..`, `.`, an empty
   segment or a backslash, or appears twice.
2. It extracts every file and directory into `<work-dir>`.
3. It requires each file that `game/contents` lists and gives it the listed
   mode: `data.pck` 0644, `MegaMan_RocknRoll` 0755. The ZIP has MS-DOS
   attributes and no Unix modes, so the executable bit comes from that list.
   Other files, such as `readme.txt`, get 0644. The native runner does not
   run `MegaMan_RocknRoll`.

It checks no hashes. korrid verified the whole ZIP against the SHA-256 that
`plugin.ts` pins before it runs the program, and that one hash fixes every
file in the ZIP. `plugin.ts` is the only source of the `data.pck` hash.

It writes only under `<work-dir>`. Exit status: 0 ready, 1 failed (including
usage). Diagnostics go to stderr; stdout carries nothing korrid reads.
Python comes from Nix. Nothing is compiled on the device.

## Launch

`launch.prepare` refuses a core, a raw config override and typed settings,
and requires an absolute `contentPath`. It takes the game directory from the
directory of `contentPath`, so a copy that discovery finds in a source plays
the same way as the download. It returns:

| Field | Value |
|---|---|
| `command`, `args` | `godot-launch <contentPath>` |
| `cwd` | the game directory |
| `env.HOME`, `directories` | `<accountRoot>/mega-man-rock-n-roll`; Godot 2 keeps settings and saves in `~/.godot/app_userdata/Megaman_RnR` |

`mega-man-rock-n-roll-godot` refuses with status 2 if it does not get exactly
one argument, if the pack is not an absolute file, or if `HOME` is not an
absolute directory. Otherwise it changes to the pack's directory, reads the
screen size from the X server with `xdpyinfo`, and runs
`godot2-runtime -r <width>x<height> -f -main_pack <pack>`. If the size cannot
be read, it runs `godot2-runtime -main_pack <pack>`. The exit status is the
engine's.

The game is X11 only. It uses the game unit's Xwayland `DISPLAY`; nothing
sets `WAYLAND_DISPLAY`. Godot uses GLES2 over OpenGL and PulseAudio, then ALSA.

The game's `engine.cfg` asks for a 1024x896 window with `stretch_mode`
`viewport` and `stretch_aspect` `keep`, and the game's own script then
requests fullscreen through EWMH. On the RG353M (sway, Xwayland) that
request sometimes lost a race: on a second launch sway marked the window
fullscreen at 640x480 while the game kept its 1024x896 window, so the game
showed in a smaller box. The launcher therefore opens the window at the
screen's own size and fullscreen from the start; the viewport stretch fits
the picture either way.

## Checks

Build these on a build machine, never on a device.

```sh
nix build --no-link .#packages.aarch64-linux.korri-plugin-mega-man-rock-n-roll
nix build --no-link .#checks.x86_64-linux.korri-mega-man-rock-n-roll-source
nix build --no-link .#checks.aarch64-linux.korri-mega-man-rock-n-roll-plugin
nix build --no-link .#checks.x86_64-linux.korri-mega-man-rock-n-roll-plugin
```

- `korri-mega-man-rock-n-roll-source` runs `game/test_unpack.py` against small
  generated ZIPs (success, modes, missing files, traversal, symlinks,
  duplicates, usage) and `runner/test_launch.py` with a recording
  `godot2-runtime` program (arguments, working directory, `HOME`, no
  `WAYLAND_DISPLAY`, exit status, refusals), then `bash -n` and shellcheck. It
  builds no engine and needs no Core.
- `korri-mega-man-rock-n-roll-plugin` checks the built package: the manifest
  (files, packages, no `requires`, license notices), strict TypeScript against
  the Core contract, `plugin.test.ts`, the unpack program's usage errors and
  the launcher's refusals. It runs the built `godot2-runtime -h` on the check's
  own system and requires the 2.1.4 banner, then runs the launcher on a file
  that is not a Godot pack and requires the engine's own refusal. On
  aarch64-linux this proves the engine executes on ARM.

## Not verified

On 2026-10-21, on the x86_64 build machine, the flake's x86_64 package ran the
real game: `game-unpack` unpacked the owner's ZIP (`data.pck` matched the
pinned hash), then the launcher played the intro for 30 seconds under Xvfb
640x480 with Mesa llvmpipe, openbox and a PulseAudio null sink. Godot opened a
PulseAudio stream and wrote `display.cfg`, `control_settings.cfg` and
`unlocks.dat` under `HOME`. Nothing tested input or gameplay.

The aarch64 engine has only run `-h` and the pack refusal on the ARM build
machine. Nothing has run the game on aarch64, inside korrid, on Panfrost or on
the RG353M. Controller input, audio output on the device, frame rate and the
compositor's handling of the fullscreen request are untested.
