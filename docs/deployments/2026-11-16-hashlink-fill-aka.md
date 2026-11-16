# HashLink Fill: aka acceptance

## Build contract (verified)

`@simonwjackson:hashlink-fill/fill` wraps only `@korri:steam/steam`.
The current pinned Core `62432aa04b199caf47399bee23e25ae949efdb92`
already carries `PluginComposeInput` and validates explicit modifier IDs against
`<plugin-id>/<key>`. No Core or shared publisher pin changes are needed.
There are no native units, ports, settings handlers or plugin requirements.

aka enables Gamescope at Device. Core folds that modifier before the Game
modifier, so the incoming plan can already be Gamescope-wrapped. The supervisor
chose to retain that owner setting and identify `steam-session` as the plan
command or an argv element, accepting only a positive numeric app ID. Compose
still wraps the whole plan. It never parses shell-command strings. This needs
no new Core field and preserves Gamescope's output size and streaming path.
The effect runs as the game's runtime user, not in the declaration sandbox.

The optional local owned-data test passed against build `23762174` / v35:

| Evidence | Verified result |
| --- | --- |
| Original SHA-256 | `59350cad475a2375b9e39d7cd13fdb6e4ed9a027fd827ae5140f913c1c07ce7e` |
| Patched SHA-256 | `c977689376ffce6d3400e50bb396de57ab8013846beb963e581b983acd6ac5ed` |
| Changed offsets | `3088883`, `3088928` only |
| Repeat preparation | Same inode, bytes and modification time |
| Corrupt HLB version | Refused patch; original command still exited with status 23 |
| Backup | Byte-identical original, named by its SHA-256 |

Eight synthetic Rust and process-exec tests passed. No game bytes entered the
repository or a Nix derivation. The local integration test creates temporary
copies outside both and skips when the owned original is absent.

## Existing publication and device path (verified)

The public repository publishes raw signed Nix cache metadata through the
shared `nix/publish-cache.sh` wrapper, pinned at
`korri-os/plugins/8562bb480a211033426894a94c69c97a83a5aa0f`.
GitHub Pages serves `https://simonwjackson.github.io/korri-plugins/`.
The established signer is `simonwjackson-plugins-1`.
That publisher predates plugin catalogs. Core's pinned `korri-publish repository`
can produce the signed plugin archives and catalog without changing the builder.

aka already consumes Simon's personal catalog at
`https://zao.hummingbird-lake.ts.net:8450/catalog.json`.
Tailscale Serve maps that URL to
`~/.local/share/korri/personal-plugin-repository` on zao.
The separate private catalog at port 8448 is not the destination for this plugin.
Use the existing personal catalog with the public GitHub release's archive URLs.
Retain its pre-existing plugin records. Do not add hosting or publisher trust.

Publication receipts and live-device acceptance are recorded below after those
operations. Package tests alone do not establish live gameplay or screen fill.
