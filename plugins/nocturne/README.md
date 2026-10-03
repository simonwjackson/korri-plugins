# NocturneRecomp

`@simonwjackson:nocturne` adds a native runner for the Xbox Live Arcade version
of Castlevania: Symphony of the Night on x86_64 and aarch64 Linux. It uses
[NocturneRecomp v1.4.5](https://github.com/birabittoh/NocturneRecomp/releases/tag/v1.4.5),
not the separate SymphonyRecomp project or a PlayStation disc image.

## Input

Select `default.xex` inside a complete extracted XBLA package. Keep `DATA`,
`MEDIA`, and the other extracted files beside it. A bare executable is not a
complete game. The runner accepts this exact executable:

```text
sha256:26a58b074c5dd6185b77a8111a0012866d11cba674b4b0810d79dbf07ad68aa6
```

This is upstream's `GameDataSelectorSettings.default_xex_sha256`, measured
again from the owner's package. It is not the hash of the archive or STFS
container. The discovery claim covers `.xex` files under `xbox-360`, matching
Skate 3's existing system identity. Other executables do not match this runner.
The plugin does not scan `.7z` archives or extensionless STFS containers.
The initial owner's archive was extracted operationally, outside the plugin.

The package uses upstream's vanilla build. It needs no separate title update.
The plugin contains no retail executable, extracted asset files, or save data
as separate files. Its native binary does contain code translated from the game.

## Native packages

| Architecture | Release asset | SHA-256 |
|---|---|---|
| x86_64-linux | `nocturnerecomp-v1.4.5-linux-x64.tar.gz` | `3ac18750a351efdbc1a49adb90dd1b2b69250bcd12b778d7e7f3ff3cd0c111f9` |
| aarch64-linux | `nocturnerecomp-v1.4.5-linux-arm64.tar.gz` | `d3dc4fd05e011f253ebbb72d3a88c2481c909933fdf50f260e01231dbed0d07e` |

Both downloads and their ELF architectures were checked. Packaging patches ELF
interpreter and library paths. It does not compile the game or SDK. Devices
receive the finished package. The Vulkan driver comes from the device, including
NixOS's `/run/opengl-driver`. SDL uses the device's audio and input services.

Upstream's MIT grant covers host-side source, scripts, and CI configuration.
It does not establish redistribution rights for translated retail code.
The native package is marked unfree. Do not publish its binary closure without
a separate rights review and approval. No signing, cache upload, publisher-trust
change, or installation approval is part of this package.

## Launch and storage

`plugin.ts` returns a launch declaration using the existing
`PluginLaunchInput.contentPath` and `accountRoot` fields. It performs no effects.
`plugin.nix` binds the program through Core's existing packages/files contract.
The launcher uses `accountRoot/nocturnerecomp`, following Zelda3's account-owned
storage pattern and ReXGlue's native application directory name.

The native layout comes from the pinned SDK, not a Korri configuration schema:
`nocturnerecomp.toml` and `logs/` live beside the executable, `settings.toml`
lives under its user-data root, and `assets`, `mods`, `update`, and `cache`
retain their upstream meanings. Native configuration stays native TOML.

The launcher verifies the source executable on every launch. It copies the
complete game directory into private account storage on first use. This costs
one additional copy of the game per account. Upstream can delete `default.xexp`
when using its vanilla build, so a symlink to the owner's assets is not safe.
The source files remain unchanged, including any title-update file.

ReXGlue locates configuration through `/proc/self/exe`. The launcher refreshes
a private executable from the pinned package and links its libraries and shader
resources to immutable Nix paths. It keeps configuration and player data intact.
An account directory lock prevents concurrent game sessions from overwriting
saves. Symlinked source assets and storage overlapping the source are refused.
A changed or damaged library executable is refused even if cached assets exist.

Native configuration loads after command-line arguments in this SDK. The
launcher refuses saved path overrides that would redirect the game's private
roots, caches, or logs and refuses saved settings that re-enable self-updates.
Inherited `REX_*` overrides for those paths and self-updates are removed. External
cache/log locations are unsupported. Startup disables upstream self-update checks. These checks are not an OS sandbox against a user
or a native mod with the same account permissions. Core's existing publisher,
signature, and permission checks remain required.

## Build and verification

Run on build machines, never target devices:

```sh
nix build --no-link .#packages.x86_64-linux.korri-plugin-nocturne
nix build --no-link .#packages.aarch64-linux.korri-plugin-nocturne
nix build --no-link .#checks.x86_64-linux.korri-nocturne-plugin
nix build --no-link .#checks.aarch64-linux.korri-nocturne-plugin
```

The data-free checks use each architecture's actual ELF, packaged declaration,
strict TypeScript contract, Core admission, and production sandboxed launch
executor. They check literal paths and reject unsupported launch overrides and
wrong game files. Native startup reaches SDL with an intentionally unavailable
video driver; this checks loading, not graphics or gameplay.

The opt-in test takes owned files as runtime arguments, never as Nix inputs:

```sh
nix run .#verify-nocturne -- /path/to/extracted/default.xex
```

It uses a private Xvfb display, D-Bus session, Mesa's software Vulkan driver, and
a private PulseAudio null sink. The released SDL has no dummy audio driver; using that
unsupported driver produced a black window. Screenshots must contain nonblank
pixels and still need visual inspection. The test covers cold and cached launch,
account locking, config/data preservation, and unchanged source-file hashes.
It retains private logs and screenshots under the printed temporary directory.

This is a startup test, not full-game, physical-device, audible-output,
controller, or gameplay save/load acceptance. Window-close did not terminate the
upstream process within 20 seconds in the headless test. The test reports that
condition and kills only its own process. Clean shutdown remains unverified.

## Device results

The [Odin 2 Portal test](../../docs/deployments/2026-10-03-nocturne-odin.md)
reached the main menu on Turnip Adreno 740 with fullscreen enabled, Xenos selected,
and asynchronous shader compilation disabled. That native account configuration
is device-local; package defaults are unchanged. Disabling asynchronous compilation
can add pauses and was not proven necessary by an Odin A/B test. Controls and
save/load remain unverified. The game was stopped after the test.

The [Mini V2 installation](../../docs/deployments/2026-10-02-nocturne-miniv2.md)
remains rendering-unverified after a black-screen result. Its native-renderer
switch is an unverified experiment. The game is stopped pending owner approval.

The Odin's approved personal publisher binding is a backed-up `/etc` override,
not part of its immutable system generation. A future NixOS activation can replace
it. Read the deployment record before updating or relying on reboot restoration.
