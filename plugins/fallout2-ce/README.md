# Fallout 2 Community Edition

`@simonwjackson:fallout2-ce` supplies the native `fallout2-ce` runner for Linux
x86_64 and aarch64. It uses nixpkgs' pinned Fallout 2 CE 1.3.0, including the
upstream case-sensitive save/load fix. No commercial assets are included.

## Verified input layout

The accepted `MASTER.DAT` is 333,176,843 bytes, with SHA-256:

```text
bf349305c3749ce6501c1e3618689d3ccbecd732569d486183786a227fc79703
```

The companion `CRITTER.DAT` is 166,273,976 bytes, with SHA-256
`fb47a93d0baa85d337523a89716475928f7b60ef30b10da5354197b73f04c3bd`.
These are measured files from the owner's `Interplay-Fallout2-Win95.iso`.

Despite its suffix, that file is a raw Mode 2 Form 1 CD track: 305,050 sectors
of 2,352 bytes, totaling 717,477,600 bytes. Its SHA-256 is
`6a8ce0a842fa2fbf7801ca13d29dd4fe0f36ecb20bb48f6a7b9428f9e7754192`.
It is not a 2,048-byte-sector ISO. Inspection stripped each validated sector's
24-byte header and retained its 2,048-byte payload in a temporary copy.
The converted ISO contains `MASTER.DAT`, `CRITTER.DAT`, `DATA/SOUND/MUSIC`, and
`Patches/f2patch-uk.exe`. That patch is a self-extracting ZIP containing
`PATCH000.DAT`. Extract its data without executing the Windows installer.
`PROGRAM/WIN/CFGWIN.___` is an executable config generator, not a text config.

Prepare an installed copy with the two DAT files, `DATA` and the patch data.
The runtime test used `patch000.dat` from the supplied UK patch. Keep the original
track untouched. Do not point this runner at the ISO or the patch installer.

Follow the [upstream native installation and configuration instructions](https://github.com/alexbatalov/fallout2-ce/blob/v1.3.0/README.md).
The native `fallout2.cfg` fields for the observed uppercase tree are:

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

These names come from upstream `src/game_config.cc` and the actual media layout.
Preserve other native settings and existing saves. `f2_res.ini` remains the
engine's resolution configuration. The plugin does not write either file.

## Launch contract and limits

Register this exact `MASTER.DAT` as the library release's file location, with
its `sha256:` identity. The plugin offers a runner for that existing release.
It invokes the approved `libexec/fallout2-ce` directly from the file's parent
directory. The XDG wrapper in `bin/fallout2-ce` is not used.

The same [discovery, writable-folder, account-sharing and deployment limits](../fallout1-ce/README.md)
apply to both plugins. In particular, neither claims `.dat` or creates library
entries. Scanning a directory alone does not register these games. No archive
extractor, account save schema, controller mapper, or shared discovery change is
part of this plugin. Fallout 1 and Fallout 2 hashes are distinct; neither runner
claims the other's file. Other editions and mods are unverified.

## Build and license

Run on a build machine:

```sh
nix build --no-link .#korri-plugin-fallout2-ce
nix build --no-link .#checks.x86_64-linux.korri-fallout2-ce-plugin
nix build --no-link .#checks.aarch64-linux.korri-fallout2-ce-plugin
```

The tests check native architecture, packaged source, manifest, license, host
admission and the production callback evaluator and `cwd` executor without retail data. They do not prove device
installation or a complete game walkthrough.

The engine's [Sustainable Use License](https://github.com/alexbatalov/fallout2-ce/blob/v1.3.0/LICENSE.md)
permits distribution only free of charge for non-commercial purposes under its
terms. The package includes that license and a modification notice.
The owner-approved Mini V2 installation used the existing signed private cache
on 2026-10-02. Native launch and the visible main menu passed.
[Deployment evidence and limits](../../docs/deployments/2026-10-02-fallout-miniv2.md)
record the exact installed output. No public binary publication has been performed.
After the [shared inspection and approval steps](../fallout1-ce/README.md#license-and-deployment-boundary),
activate this exact plugin with `sudo korri-plugin enable @simonwjackson:fallout2-ce`.
