# The Simpsons Game

`@simonwjackson:the-simpsons-game` adds a native runner to the existing Xbox 360
library game. It does not add a duplicate game tile or use a CPU emulator.

## Native package

The plugin builds [The Simpsons Game Recompiled v0.0.6.2](https://github.com/YesterMester/TheSimpsonsGameRecomp/tree/f63f57bcba29d3e7016fd867fad05adc85822bcb)
at commit `f63f57bcba29d3e7016fd867fad05adc85822bcb`. The upstream repository
contains generated game code and a vendored ReXGlue SDK. The ARM recipe applies
ReXGlue's [FFmpeg visibility fix](https://github.com/rexglue/rexglue-sdk/commit/d82ec280809f3505001ef7396477612cfde16864)
so its NEON constants can link into the shared runtime. That patch does not change
the x86 recipe. Compilation happens on a build host, not on the handheld. The plugin still ships TypeScript source
for Korri's runtime interpreter.

| Build target | Requirement and limitation |
|---|---|
| `x86_64-linux` | Uses upstream's default `x86-64-v3` CPU floor, including AVX2. It is not a generic x86-64 binary. |
| `aarch64-linux` | Uses upstream's ARM64 source paths. Upstream ships no Linux ARM release binary. A build alone does not establish handheld compatibility. |

Both targets need a working Vulkan driver and X11 or Xwayland. No Android,
32-bit ARM, FEX, box64 or streaming fallback is included.

The native output contains code translated from EA's executable. Upstream's
GPL license for handwritten code does not grant rights to the original game.
Keep this binary closure private. No public cache upload, signing, trust change
or device installation is part of these build commands.

## Accepted disc

The only admitted release is this measured whole ISO:

| Member | Bytes | SHA-256 |
|---|---:|---|
| `simpsons-ntscu-cs.iso` | 7835492352 | `fd794e7a3025c3fd1340d25301658bac8c829a65d5e5e47d2663b431f869531b` |

The measurement streamed the ISO from the owner's `The Simpsons Game X360.rar`
on myoko. This is not the RAR hash or an XEX hash. Upstream targets the USA
release, title ID `45410809`. Other regions and dumps are not admitted.

Add the bare ISO to an existing library folder. The scanner does not unpack
RAR or ZIP files. The existing `RunnerRecord.releases` contract matches its
whole-file hash. The discovery claim follows the existing Skate 3 producer,
assigning `.iso` to `xbox-360`. A different system claiming `.iso` still causes
Core's `ClaimConflict`.

The native launcher checks the ISO hash on every launch. This reads about
7.84 GB even when the game is already installed. It avoids a new verification
cache format and rejects a file changed since library scanning. This is not
protection against another process modifying the same open file during a launch.

## Account storage

The user chose separate installation, settings and saves for each Korri account
on 2026-10-02. Core creates `<accountRoot>/simpsons` and runs the native launcher
there. The directory name follows upstream's application identity `simpsons`.
Native names and formats remain unchanged:

| Native item | Grounding and account location |
|---|---|
| Installed assets | Upstream `launcher/launcher.py` uses `gamedata/`. The plugin extracts the ISO there under the selected account directory. |
| Settings | Upstream uses `simpsons.toml`. `account-storage.patch` moves it from the immutable executable directory to `user_data_root`. |
| Saves and shader cache | The engine already accepts `--user_data_root`. The launcher passes the account directory and keeps upstream's content and cache layout. |
| Logs | The patch moves upstream's `logs/` directory to `user_data_root`, keeping its native sequential filenames. |

`simpsons.toml` contains the two release defaults from upstream's
`.github/workflows/release.yml`. The launcher installs it only when absent.
The in-game settings editor remains available. Existing configuration and
progress are not overwritten. Korri typed settings, emulator cores and generic
configuration overrides are rejected rather than silently ignored.

Extraction uses upstream's bundled `extract-xiso`, built on the build host.
It publishes a complete directory with a same-filesystem rename. A failed
extraction leaves no installed directory. An incomplete existing installation
causes an error rather than automatic deletion. Move it aside before retrying.
A directory lock remains held for the game's lifetime and prevents two launches
from writing the same account's data. Different accounts use different locks.

The launcher removes inherited `REX_GAME_DATA_ROOT`, `REX_USER_DATA_ROOT`,
`REX_UPDATE_DATA_ROOT`, `REX_CACHE_PATH` and `REX_LOG_FILE`. ReXGlue applies
these environment overrides after CLI arguments, so retaining them can redirect
one account into another. Other native environment settings remain available.
This changes inherited path customization. It does not sandbox a same-user
process against arbitrary filesystem changes.

The measured extraction contains 7,968 files totaling 4,385,078,597 bytes.
Each account needs its own copy, plus saves and shader cache. The source ISO
and original archive remain unchanged. The copied `default.xex` is 14,200,832
bytes with SHA-256 `71d99dad06be1b512fc3058123b84fdad71339205a7e9249058ac5e34a82a231`.

## Differences from upstream's desktop launcher

Korri starts the native engine directly. It does not include upstream's separate
Python launcher UI, updater, mod manager, artwork extraction, save repair or
backup automation. Normal plugin updates own executable replacement. Native
in-game settings own configuration. Upstream also documents scripted-sequence
bugs at 60 FPS, including the dam in "Lisa the Tree Hugger".

`DISABLE_LSFG=1` follows upstream's launch behavior because that Vulkan layer
can hang this renderer. SDL's optional Steam-storage `libsteam_api.so` is not
required. The packaging check ignores that one suggested dlopen dependency,
not missing mandatory libraries.

## Build and verify

Run on a build machine of the corresponding architecture:

```sh
nix build --no-link .#korri-plugin-the-simpsons-game
nix build --no-link .#checks.x86_64-linux.korri-the-simpsons-game-plugin
nix build --no-link .#checks.aarch64-linux.korri-the-simpsons-game-plugin
```

The package check typechecks the actual shipped plugin source against Core's
contract, checks the generated manifest, runs host admission, and exercises
Core's sandboxed callback and command executor. Paths with spaces and shell
syntax must remain literal. Rejected overrides must fail.

Native tests create a small real XISO with the pinned extractor. They check
atomic installation, cached reuse, corrupt media, missing files, FIFOs,
concurrent launches, inherited environment cleanup, config preservation and
lock lifetime through `exec`. The successful handoff observer is a real child
process, not the game. A separate native-loader check reaches the game's GTK
startup without a display. Neither test proves rendering, audio, input or saves.

The opt-in check below uses your actual disc through the packaged callback and
launcher. It requires about 5 GB of temporary space, removes its temporary retail
files, and verifies both first installation and cached reuse without opening a
window:

```sh
nix run .#verify-simpsons -- /path/to/owned/simpsons-ntscu-cs.iso
```

### Verified results on 2026-10-02

The x86_64 package and check passed on zao. The aarch64 package and check passed
on fuji after the FFmpeg link fix. Both checks read the native engine and extractor
ELF headers, rather than trusting platform metadata.
The owned-ISO check passed first installation and cached reuse through the
packaged Core callback and launcher.

A separate native run used Xvfb, lavapipe Vulkan and an ALSA null sink. It rendered
the title and menus, accepted keyboard input with upstream's `mnk_mode` enabled,
and played the opening cutscene. It created a 114800-byte native save plus a
328-byte header beneath the selected account directory. After restart, the game
listed that slot as "The Land of Chocolate", accepted loading it, and showed
"Continue Game". Native config, logs and shader cache remained under that account.

This verifies early startup and save reload, not full-game completion or playable
handheld performance. Audible sound and physical controllers remain untested.
Intel Vulkan initialized in Xvfb but could not present without DRI3; lavapipe
rendered the same game. No production code change was made for that virtual-display
limitation. ARM rendering and physical-device acceptance are still pending.

Device acceptance still needs an approved private prebuilt delivery route,
a bound publisher key, exact-package approval and a selected compatible device.
Never disable signatures or compile on a device to bypass missing delivery.

This product includes software developed by in <in@fishtank.com>, the author of
`extract-xiso`. Its source and license notice are installed with the extractor.
