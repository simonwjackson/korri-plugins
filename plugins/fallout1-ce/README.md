# Fallout Community Edition

`@simonwjackson:fallout1-ce` supplies the native `fallout-ce` runner for Linux
x86_64 and aarch64. It uses nixpkgs' pinned Fallout CE 1.1.0, including the
upstream case-sensitive save/load fix. It contains no commercial game data.

## Input and launch behavior

The runner accepts the whole-file SHA-256 of the owner's installed `MASTER.DAT`:

```text
8cdb879ac4431dce48a25c3e02e9db4aee3449b73e7b185a63d69fef3982a509
```

That file is 333,674,504 bytes. It came from `fallout1/MASTER.DAT` inside
`Fallout (1997).zip`. The companion `CRITTER.DAT` is 158,022,057 bytes with
SHA-256 `aad9a53083e498fefe8f65652601ff9d9a9d2c1fb76d7fa97549214f17f0e694`.
Retain the installation's `DATA` directory, including music and patch files.
Do not register `CRITTER.DAT` or the enclosing archive as this release.

The plugin adds a route to an existing library release whose key is
`sha256:<the MASTER.DAT hash above>`. The release's file location must point to
that `MASTER.DAT`, with its companion files in the same installation.
The runner does not rehash the file on every launch. Korri owns release identity.
The identity covers `MASTER.DAT`, not the companion files, patches or mods.
Only this measured file is admitted. Other editions need separate checks.

There is deliberately no `discovery.fileReleases` contribution and no new system
ID. Korri's current scanner uses extension claims, not exact-file discovery rules.
Claiming `.dat` would label unrelated data files as Fallout. These plugins do not
create library entries, extract archives, install Windows software, or implement
the pending shared system-identification design. Automatic library import is not
provided by this slice. Existing catalog records must identify the installed
`MASTER.DAT`; simply adding its directory through the scanner does not do that.

The callback returns the approved engine program, no arguments, and the parent
of `MASTER.DAT` as `cwd`. It references the package's `libexec/fallout-ce`, not
nixpkgs' `bin/fallout-ce` wrapper, which changes to an XDG directory.
Korri performs the launch. The TypeScript declaration performs no effects.

The engine owns `fallout.cfg`, `f1_res.ini`, `DATA` and its native saves.
The plugin never rewrites configuration or copies saves. The runtime user must
have write access to the installation. This retains upstream behavior but shares
saves between accounts using that installation. It does not provide per-account
save isolation or synchronization. Use separate installations when needed.
Native mouse and keyboard input are required; gamepad mapping is not supplied.
Provide working desktop OpenGL libraries and a driver on the device. The headless
ARM builder required an explicit Mesa software driver for runtime tests.

## Prepare the owned installation

Follow the [upstream installation and configuration instructions](https://github.com/alexbatalov/fallout1-ce/blob/v1.1.0/README.md).
Work on an extracted copy, not the original archive. The observed archive also
contains a CD track and DOS executables; the native engine does not need those.
Its original `FALLOUT.CFG` contains `C:\\fallout1` and `D:` paths that do not work
on Linux. Correct those paths in the copy using the existing engine keys.

For the observed uppercase data tree, the native `fallout.cfg` uses:

```ini
[system]
master_dat=MASTER.DAT
critter_dat=CRITTER.DAT
master_patches=DATA
critter_patches=DATA
[sound]
music_path1=DATA/SOUND/MUSIC/
music_path2=DATA/SOUND/MUSIC/
```

These are upstream engine fields, grounded in the supplied installation's config
and `fallout1-ce/src/game/gconfig.cc`, not a new Korri configuration schema.
Preserve any other user settings. Do not ship retail assets or saved games in the
plugin source, build closure, tests, or CI artifacts.

## Build and verification

Run from the repository on a build machine:

```sh
nix build --no-link .#korri-plugin-fallout1-ce
nix build --no-link .#checks.x86_64-linux.korri-fallout1-ce-plugin
nix build --no-link .#checks.aarch64-linux.korri-fallout1-ce-plugin
```

The check verifies the packaged source and manifest, ELF architecture, shipped
license, strict launch types, real host admission, and the production JavaScript
callback evaluator and `cwd` executor.
It checks literal paths containing spaces and shell characters, preserved files,
and rejection of archives, other filenames, emulator cores and unsupported
settings. It invokes the callback CLI as an unprivileged user, not a live
systemd game unit. It does not install the plugin or need retail assets.

### Owned-data runtime check, 2026-10-02

Both packaged engines reached their first map through `korrid plugin-launch`
on x86_64. They wrote native slot files and reloaded them in fresh processes.
The native aarch64 builder loaded those same saves and rewrote them through each
game's Options > Save Game menu. Captured frames showed both Game Loaded and
Game Saved, and the slot files retained their native save headers.
Tests used isolated copies of the owned data, Xvfb, and dummy audio.
No retail assets or saves entered the package or CI.

The first headless ARM attempt lacked an OpenGL provider and crashed in SDL's
initialization-error path. Supplying Mesa software GL fixed startup without an
engine change. Synthetic F4 input did not open the save dialog in that test;
the normal Options menu did. This does not verify physical controllers, audible
sound, a systemd game unit, device GPU behavior, or a full walkthrough.

## License and deployment boundary

The engine uses the [Sustainable Use License](https://github.com/alexbatalov/fallout1-ce/blob/v1.1.0/LICENSE.md).
Distribution is limited to free-of-charge, non-commercial purposes under its
terms. Each engine output includes the license and a modification notice.
The flake permits only the two Fallout engines through its unfree-package gate.
It does not enable unrelated unfree packages.

This repository's workflow checks packages; it does not publish or sign them.
Deployment requires a signed package for the device architecture, the separately
bound `@simonwjackson` publisher key/cache, exact-package approval, and a registered
release. Never enable device builds or bypass signature checks. The supplied
asset host `myoko` had no active `korrid.service` when checked on 2026-10-02.
No live installation is claimed.

After signed publication and target configuration, use Core's existing commands.
`CACHE_URL` must be the bound publisher cache. `PACKAGE` must be the exact output
for the device architecture. Read the inspection report and use its `APPROVAL`:

```sh
sudo korri-plugin inspect "$CACHE_URL" "$PACKAGE"
sudo korri-plugin install "$CACHE_URL" "$PACKAGE" "$APPROVAL"
sudo korri-plugin enable @simonwjackson:fallout1-ce
```

These commands do not register game data or grant the runtime user write access
to an installation. Keep those separate, explicit deployment steps.

See [Fallout 2 CE](../fallout2-ce/README.md) for its distinct data and runner.
