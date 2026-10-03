# Nocturne on the Odin 2 Portal

The owner selected the online Odin for a short renderer test on 2026-10-03.
The signed ARM64 plugin was installed, registered in the library, and launched
through the device's own korrid. A captured screen showed the Castlevania main
menu. The game was stopped after the test. Korri then reported no active session.

## Installed artifacts

| Artifact | Value |
|---|---|
| Plugin ID | `@simonwjackson:nocturne` |
| Plugin source commit | `56729d4` |
| Plugin output | `/nix/store/wz2fd5jwmvdsdijv194f3ba7nwh6ydy6-korri-plugin` |
| Native output | `/nix/store/pnj0blm7nr8wnd70hw4nj8sj0ik00v85-nocturnerecomp-1.4.5` |
| Exact approval digest | `1f652ffe1828f4d3ffa81bb270f53deb4a27bdb7f3ed63e378815eb0a0e50cfd` |
| Library game ID | `01M41A1EG9WD53DYQW0VRMRG56` |
| Selected runner | `@simonwjackson:nocturne/nocturne` |
| Test launch ID | `c9c2080afc836ea5294e0d9b32dabcaa` |

The device identified itself through its physical USB console as AYN Odin 2
Portal, running aarch64 NixOS. Its network SSH key matched the console fingerprint
before network administration. Root and ESP were `/dev/mmcblk0p2` and
`/dev/mmcblk0p1`. No partition, boot file, firmware, or bootloader state changed.
The Mini V2 was not contacted during this Odin test.

## Approved publisher trust

The Odin initially trusted only `@korri`. The owner explicitly approved adding
`@simonwjackson` with the existing personal publisher key:

```text
simonwjackson-plugins-1:4SchQgTMNU3syZ2ZzN/cJXPMigc/PIt+EaqHAStgJs8=
```

The bound private cache is
`file:///var/lib/korri-private-cache.ns0pahye/cache`.
The prebuilt closure was already signed on the build machine. No signing secret
was transferred, no public cache was published, and no signature check was
bypassed. Core's real `inspect`, exact-digest `install`, and `enable` operations
completed. Recursive `nix store verify --sigs-needed 1` passed.

This deployment replaced only the `/etc/korri-plugin-host/publishers.json` and
`/etc/nix/nix.conf` symlinks with root-owned local configuration copies. It did not
modify their immutable store targets. The `@korri` binding and existing Nix
configuration were preserved. The approved key was added through Nix's native
`extra-trusted-public-keys` setting. The active Nix daemon was restarted to read
that configuration. All prior plugin selections retained their hashes.

These are operational overrides, not a rebuilt system generation. A later NixOS
activation can replace them, including boot-time activation. The permanent system
configuration still needs the approved `services.korri.pluginHost.publishers`
entry before relying on plugin restoration across an activation. No reboot or
activation persistence is claimed here.

Exact original symlinks and resolved contents are backed up on the Odin under:

```text
/var/tmp/nocturne-miniv2-deploy-k0rt66xf/trust-backup/
```

The staging directory retained its transfer name from the earlier Mini V2 work.
It is on the Odin; it is not a reference to a mounted Mini V2 filesystem.
`odin-receipt.json` in that directory records the cache and package.

The effective policy stayed `max-jobs = 0`, empty `builders`, `fallback = false`,
and `require-sigs = true`. The device compiled nothing. The system generation
remained unchanged.

## Library and runtime

The Odin had no authored games, releases, or scan roots. The agent copied the
owner's verified extracted assets into:

```text
/var/lib/korri/roms/Castlevania - Symphony of the Night (World) (XBLA)/assets/
```

The directory name preserves the owner's archive name. The runtime user received
read and traverse ACLs only on this new library subtree. Catalog files and private
daemon state retained their existing restrictions. Every transferred asset hash
matched the measured source, including this executable:

```text
26a58b074c5dd6185b77a8111a0012866d11cba674b4b0810d79dbf07ad68aa6
```

The native catalog importer created the game, release, location, and one scan
root covering this game directory. It did not scan private account assets.
The importer names games from filenames, so the agent changed only the new
GameRecord's title scalar to `Castlevania: Symphony of the Night`. The rest of
the YAML remained unchanged. The first attempt encountered an empty catalog
without a `games` key and restored the exact backup before restarting korrid.
The successful retry handled that observed empty document.

Core selected the exact installed Nocturne runner for this game and launched it
through `app.local-games.launch.selected`. The native process ran as `korri`
with zero effective capabilities and `NoNewPrivileges=yes`. Its private asset
copy matched all source hashes. No original asset files were modified.

The new account's native `settings.toml` contains:

```toml
fullscreen = true
gpu_plugin = "xenos"
async_shader_compilation = false
```

These are upstream Nocturne/ReXGlue settings. They are not new Korri fields.
Fullscreen requests presentation above the portal. Synchronous shader compilation
was the renderer experiment prompted by the Mini V2's incomplete-frame warning.
Its cost is possible pauses during shader compilation. It was not compared
against asynchronous compilation on the Odin, so this test does not prove that
disabling it was necessary.

The log selected `Turnip Adreno (TM) 740`, not software Vulkan. Sway identified
one game-owned window that was visible, focused, fullscreen, and 1920×1080.
Two screenshots three seconds apart differed. The agent opened the later image
and verified the main menu, including `Single Player`, `Leaderboards`, and
`Achievements`. No failed systemd units were present during this test.

## Stop and limits

The stop RPC initially returned `HostRecoveryBlocked` during shutdown, as it had
on the Mini V2. Subsequent checks established that the exact game unit had stopped
and Core reported no active session. No recovery record was deleted or rewritten
by the agent. The plugin remains installed and enabled; the game is stopped.

Rendering and signed installation are verified. Physical input, audible sound,
gameplay, save/load, full completion, and reboot persistence are not verified.
The owner must authorize another device-testing window before the next launch.

Device evidence remains under `/var/tmp/nocturne-miniv2-deploy-k0rt66xf/`:
`inspection.json`, `installed-selection.json`, `runtime.json`, `window.json`,
`native-latest.log`, `paused.json`, and the two `nocturne-odin*.png` captures.
The later screenshot SHA-256 is
`a26a234cc1afe47ee15d1040416def95f1d3ef6d356e27593672061bc9e82f30`.
Private assets and screenshots are not committed to this repository.
