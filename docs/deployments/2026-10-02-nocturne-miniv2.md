# Nocturne on the Mini V2: installed, rendering unverified

The owner approved Nocturne installation on the Retroid Pocket Mini V2 on
2026-10-02. Installation and launch succeeded, but the default renderer produced
a mostly black image. The owner then requested that the game stop and that device
use require a readiness prompt. The agent verified that Nocturne stopped and
Korri had no active session. Later testing moved to the Odin with explicit approval.

## Installed state

| Item | Value |
|---|---|
| Plugin | `@simonwjackson:nocturne` |
| Package | `/nix/store/wz2fd5jwmvdsdijv194f3ba7nwh6ydy6-korri-plugin` |
| Native package | `/nix/store/pnj0blm7nr8wnd70hw4nj8sj0ik00v85-nocturnerecomp-1.4.5` |
| Approval | `9b225b07519a211d68683a53a2613bf433a89e45625ddf6cdf7aefe26e1f5ad0` |
| Game ID | `01M3YZKV3QNFRJR780FGY9SMX3` |
| Private cache | `file:///var/lib/korri-private-cache.h6odJOu2/cache` |

The device's existing personal publisher binding was reused without changes.
The private cache was extended without replacing prior records. Inspection,
exact-digest installation, enablement, and recursive signature verification
passed. Device builds and remote build dispatch stayed disabled. The system
generation, partitions, and boot files were not changed.

The library importer preserved 27 games and 27 releases and registered the
verified XBLA `default.xex` under the owner's archive directory name in
`/var/lib/korri/roms/`. Only the newly imported title scalar was changed from the
executable filename to `Castlevania: Symphony of the Night`. The existing parent
scan root was reused. Runtime read/traverse ACLs were scoped to the new subtree.
All source and private-copy asset hashes matched.

The first launch ran under `korri`, without capabilities and with
`NoNewPrivileges=yes`. Its window was visible, focused, and fullscreen at
1240×1080. This ruled out the hidden-window failure previously seen with Zelda3,
but did not prove game rendering. Screenshots were mostly black and identical.
The log selected Turnip Adreno 650 and reported skipped presentation after an
asynchronous placeholder shader draw.

## Paused renderer experiment

The account's native `settings.toml` initially contained `fullscreen = true`.
The agent backed that file up and added `gpu_plugin = ""` to select upstream's
built-in native renderer. The process started, but the user requested a stop
before rendering was verified. That configuration remains an unverified experiment,
not an accepted fix. The original settings backup is
`/var/tmp/nocturne-miniv2-deploy-k0rt66xf/before-native-renderer-settings.toml`.

The stop RPC briefly returned `HostRecoveryBlocked`. Later checks established
successful unit completion, an empty host-session journal, and `SessionCompleted`.
The agent did not delete or rewrite recovery records. After the second launch,
the owner-requested stop was also verified as idle. The final stopped launch ID
was `0ece1ec9f3465bf27642cb5f6fd56f97`.

A later local test of the built-in native renderer produced a black screen and a
SPIR-V parsing error on software Vulkan in both fullscreen and windowed modes.
That is evidence against treating the renderer switch as a general solution,
not proof of its behavior on the Mini V2's GPU.

## Concurrent changes and limits

All earlier plugin selection hashes matched immediately after installation.
A later check detected a separate Zelda3 update from
`/nix/store/gdk49lhyv59aia0f6z55xnljfqjwgqcq-korri-plugin` to
`/nix/store/ihc0ln79i1ii76v455ny7jj9jl5m93k1-korri-plugin`.
The agent left it untouched. Do not report that all selections remained unchanged
throughout the later renderer investigation.

Two failed units predated this installation: `korri-plugin-host.service` and the
missing `korri-sunshine-input-setup.service`. They were not repaired here.

No Mini V2 gameplay, controls, audio, save/load, or rendering acceptance is claimed.
The plugin is installed and enabled, and the game was last verified stopped.
Do not relaunch it without the owner's readiness approval.
