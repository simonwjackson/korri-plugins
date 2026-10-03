# Solarus on the Mini V2

On 2026-10-02, the owner approved installing Solarus on the Retroid Pocket Mini
V2 through its existing signed-cache route. The ARM64 plugin is installed and
enabled. The installed `solarus-run -help` command succeeds as user `korri`.
No quest was installed, registered, or launched during this plugin installation.
The later [Yarntown verification](../research/solarus-yarntown.md) records
quest installation and launch, including the manual display-focus correction
and the remaining acceptance checks.

## Exact installed artifacts

| Item | Verified value |
|---|---|
| Source revision | `e8e9dd8d43c03163f47db28aea26cba7f34b6b4d` |
| Plugin ID | `@simonwjackson:solarus` |
| Runner ID | `@simonwjackson:solarus/solarus` |
| Plugin output | `/nix/store/22bnbln32hn8kj978kqrmqx9zxmm4gcf-korri-plugin` |
| Native engine | `/nix/store/6532d3lb4xm2jdjgf3sbwmp6s1c6nj7z-solarus-2.1.4/bin/solarus-run` |
| Approval digest | `8b87c2a9a9964790a430387c3b608c53a94844a2b0b4622fc76d35c2059cbfb6` |
| Existing publisher cache | `file:///var/lib/korri-private-cache.h6odJOu2/cache` |

SSH used the existing host key previously checked through the attached serial
console. Host-key verification stayed enabled. The read-only preflight checked
`Retroid Pocket Mini V2`, `aarch64`, the existing publisher binding, and the
no-build policy before import. The exact plugin output was absent initially.

## Delivery and activation

The build machine exported the prebuilt closure using the existing personal
publisher key. The script checked the key's owner, permissions, and derived
public key against the already-bound publisher. No signing material left the
build machine. The device's existing private cache gained the signed records
and NAR files without deleting or replacing prior records. Nothing was
published to a public binary cache.

The real `korri-plugin inspect` imported the exact package through that cache.
Its report identified Solarus and its single native program. It declared no
services, ports, or required plugins. The reviewed digest was passed to the
normal `install` command, followed by `enable`. The installed selection reports
`Enabled`, and the runtime enabled-package registry contains that exact output.
Recursive `nix store verify --sigs-needed 1` passed for the plugin closure.

Hash checks verified that all pre-existing plugin selections and the publisher
binding file stayed unchanged. The running korrid PID and active state stayed
unchanged. Nix policy remained `max-jobs = 0`, empty `builders`,
`fallback = false`, and `require-sigs = true`. The device performed no builds,
flake evaluation, trust changes, or permission bypasses.

The selected NixOS system remained
`/nix/store/py2xkpryv812ssz6dlinkp7bffihh51m-nixos-system-rpminiv2-sd-card-26.05.20251221.a653104`.
Root stayed on `/dev/sda22`; `/boot` stayed on `/dev/sda21`.
No system activation, reboot, partition operation, or firmware write ran.

The README follow-up changes the package's Nix output path but not its contents.
Recursive comparisons found byte-identical `plugin.ts` and manifest files on
both architectures, with the same native references. Both package checks passed
again. The device retains the original signed and approved output above.

## What is and is not verified

| Check | Result |
|---|---|
| Signed import from the existing private cache | Passed with the plugin absent before import. |
| Exact-package approval and activation | Passed; enabled registry and selection agree. |
| Native target execution | The installed engine's `-help` ran as user `korri`. |
| Quest loading and save/reload | Passed earlier on native x86_64 and ARM64 build machines, not on this device. |
| Device display, physical input, audible sound, real-game compatibility | Not tested during plugin installation. See the later Yarntown verification for quest evidence and limits. |
| Account selection | The plugin respects supplied accountRoot. The pinned Core currently uses `users/default`. |

The plugin discovers `.solarus` files only in folders already selected for
scanning. The installation scripts do not register scan roots or library
records and do not copy quests or saves. They do not migrate desktop saves. A real quest test still needs an appropriate
quest and its existing library route.

## Existing failed units

Two failed-unit markers existed before installation and remain afterward:
`korri-plugin-host.service` and `korri-sunshine-input-setup.service`.
The Sunshine selection is already `Disabled`. Solarus activation succeeded
without changing that selection or clearing either marker. This operation does
not claim to repair plugin restoration or prove reboot acceptance.

## Evidence

The private device stage is `/var/tmp/solarus-miniv2-deploy-2t2lashr`.
It contains `inspection.json`, `installed-selection.json`,
`existing-selections.sha256`, `selections-after.txt`, `publishers-before.sha256`,
`system-before.txt`, `system-after.txt`, `korrid-before.txt`, `korrid-after.txt`,
`native-help.txt`, `package-before.txt`, and failed-unit snapshots.
The build-host export is `/tmp/solarus-miniv2-deploy-2t2lashr`.
These operational artifacts are not plugin contents or public release files.
