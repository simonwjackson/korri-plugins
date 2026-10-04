# Signs of Rain

`@simonwjackson:signs-of-rain` adds one native runner for the exact packaged
Signs of Rain PCK. It does not add a general Godot runner, a system, discovery
extension claims, automatic tiles, or catalog APIs.

## Package interface and input status

The public source input is `github:simonwjackson/signs-of-rain`, pinned to
`a5a320681fa0688a618b0894d04de1a00b1ad537`. It provides native Linux packages
for both architectures. The source includes controller routing, GLES renderer
selection and a lower-cost handheld graphics profile. Sustained RG353M 60 FPS
is unmeasured.

The required game-flake interface is:

- `packages.x86_64-linux.signs-of-rain` and
  `packages.aarch64-linux.signs-of-rain`.
- `bin/signs-of-rain`, accepting Godot's `--main-pack ABSOLUTE_PCK` arguments.
- `share/signs-of-rain/signs-of-rain.pck`, the actual exported game pack.

`source.nix` hashes that packaged PCK at build time. It generates a single
source-root `plugin.ts` from `plugin.ts.in`, with that exact SHA-256 in
`runner.releases`. Devices receive interpreted TypeScript and the native
package closure. The plugin performs no file, network, process, or device
operations. Neither plugin source nor release hashes are calculated on devices.

The launcher uses Core's explicit `--main-pack` content path, rather than
silently replacing it with a bundled pack. An off-device engine smoke test
loaded a copied pack with a shell-like filename and rejected a missing path.

## Manual library registration

The runner is `@simonwjackson:signs-of-rain/signs-of-rain`. It matches the
existing `RunnerRecord.releases` whole-file identity contract in Core's
`services/korrid/src/plugin.rs` and `services/korrid/SCRIPTING.md`.

After an approved build and delivery, manually register **that exact PCK**
through the existing library's release and local-file records:

1. Read the generated plugin's `runners["signs-of-rain"].releases[0]`.
2. Use that `sha256:<hash>` as the existing library release identity. Link it
   to the intended Signs of Rain game through the existing catalog record.
3. Record the absolute path of the unchanged packaged PCK, or an identical
   copy, in the existing library's local file location for that release.
4. Select the Signs of Rain runner through the existing launch route.

The plugin does not create these records or choose catalog/system metadata.
Use the library's existing record format; this change adds no registration RPC
or schema. A file ending in `.pck` is not discovered automatically. Renaming
another pack does not give it the accepted identity. Register a new exact
release when a changed pack is delivered. Core uses the library's recorded
identity; this plugin does not rehash content during launch.

## Launch and account storage

The launch plan calls the selected immutable native program with
`--main-pack contentPath --fullscreen --rendering-method gl_compatibility
--rendering-driver opengl3_es -- --handheld --graphics=fast`.
Godot requests fullscreen for this handheld runner. The first Mini launch
needed manual fullscreen and focus; automatic visibility still requires a
target check. Desktop and Android launch defaults do not change. Core executes these as literal
arguments, not shell text. The profile removes glow, shortens sun-shadow
coverage and lowers 3D resolution. It preserves all 24 people and simulation.
Cost: less sharpness and less distant lighting detail. Mesa's conformant G52
GLES path avoids an unsafe experimental Vulkan override. Unknown runners, emulator cores, launch overrides, and relative or
NUL-containing program, content, or account paths fail before execution.
An empty settings map is accepted and has no effect.

The existing game `project.godot` sets `config/use_custom_user_dir=true` and
`config/custom_user_dir_name="signs-of-rain"`. Linux Godot therefore places
`user://` under `$HOME/.local/share/signs-of-rain` when `XDG_DATA_HOME` is
unset. Native game code uses `user://settings.cfg` and
`user://last-replay.json`; the plugin defines no save schema.

Core's existing `PluginLaunchInput.accountRoot` supplies `HOME` and cwd.
Core creates that root through the existing `directories` output. The plan
unsets inherited `XDG_DATA_HOME`, `XDG_CONFIG_HOME`, and `XDG_CACHE_HOME` so
host desktop paths cannot override the account's native directories. It leaves
`XDG_RUNTIME_DIR`, graphics, audio, controller, and session variables inherited.
Distinct supplied account roots stay separate. This does not implement account
selection or change Core's current default-account behavior. Existing desktop
saves are not imported or changed. Account paths are not an extra OS sandbox,
and simultaneous launches retain the game's native save behavior.

## Build and checks

Run on a build machine, never a target device:

```sh
nix build --no-link --option builders '' --option post-build-hook '' .#packages.x86_64-linux.korri-plugin-signs-of-rain
nix build --no-link --option builders '' --option post-build-hook '' .#checks.x86_64-linux.korri-signs-of-rain-plugin
nix build --no-link --option builders '' --option post-build-hook '' .#packages.aarch64-linux.korri-plugin-signs-of-rain
nix build --no-link --option builders '' --option post-build-hook '' .#checks.aarch64-linux.korri-signs-of-rain-plugin
```

Both architectures have output definitions. ARM checks require an approved
local ARM build machine or local execution support; these commands do not
authorize remote builders, `fuji`, or on-device compilation.

The check type-checks the actual generated packaged source against Core's
contract. It compares the release hash to the actual packaged PCK, checks the
manifest and executable, and runs the real `korri-plugin seed` admission and
`korrid plugin-launch` sandbox/executor commands. A literal argv/environment
observer records the resulting process arguments and inherited session values.
Tests cover two account roots, directory creation, shell-like filenames,
unsupported input rejection, and removal of host XDG storage overrides.
There are no Mock/Stub Core adapters. The observer is not the game engine;
these checks do not prove native rendering, saving, audio, controller input,
handheld performance, or hardware acceptance. No physical controller acceptance is
claimed. Both native packages and real Core admission/launch checks pass. On
2026-10-03, the owner approved fuji for ARM builds. The ARM plugin and checks
built there from published plugin revision `4440bfe` and game revision `a5a3206`.
Its ARM Godot engine loaded a copied pack from private storage for 30 headless
frames and rejected a missing pack. This is actual ARM execution, not Mali
rendering, device audio, physical controller acceptance or a performance test.

Fuji rebuilt the resource pack through its existing x86 emulation after rejecting
an unsigned transfer. Signature checks stayed enabled. We changed no trusted
keys or device permission. The resulting outputs remain on fuji:

- `/nix/store/ckfrb09yyf0k3z8smi7rknaai152sw5v-korri-plugin`
- `/nix/store/xmczx513fb681khzn5s1fli4kiq9gxry-korri-signs-of-rain-plugin-check`

On 2026-10-04, the Mini V2 received a signed package through normal inspection,
exact approval, installation and enablement. Core loaded its exact-PCK library
route without restarting Korri services. Its actual game created a Freedreno
FD650 GLES 3.2 context. Physical controls, audio and sustained 60 FPS remain
unverified. See [the Mini deployment record](../../docs/deployments/2026-10-04-signs-of-rain-miniv2.md).

The owner approved the existing personal publisher on Odin. The fullscreen
package passed normal signed inspection, installation, enablement and recursive
signature verification there. After explicit owner approval, its first native
Linux-tagged release was registered with the existing library schema. Actual
Core routes and catalog responses verified the exact package route and entry.
The first launch still needs current Odin readiness. No Odin rendering or
hardware acceptance is claimed.
See [the Odin deployment record](../../docs/deployments/2026-10-04-signs-of-rain-odin.md).

Two off-device exports produced different PCK bytes under the same Nix output
path. The exact fuji pack and its matching generated plugin were delivered
without mixing workstation exports. Byte-for-byte export repeatability remains
unresolved; each accepted release must use the actual delivered pack hash.

Source publication and passing checks are not signing, cache publication,
device installation, a trust change, or device acceptance. The RG353M was offline
when implementation was validated. A later installation needs the
normal approved signed delivery and exact-package approval. Missing artifacts
must fail; do not enable compilation or installation as a fallback on devices.
Game and engine licenses remain with the upstream package and its closure.
