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

## Land and publication (verified)

The source commit is `bcd95fb30c91b004e6b1ed8760a2c0b4589f6ed8`,
`feat: add HashLink Fill launch modifier for Dead Cells`.
It was rebased on `origin/main`, fast-forwarded and pushed to `main` with the
source tag `build-bcd95fb30c91-hashlink-fill`. Preparation and publication used
that detached tag with `EXPECTED_SOURCE_SHA` checked before builds and uploads.

| Published item | Verified result |
| --- | --- |
| [Release](https://github.com/simonwjackson/korri-plugins/releases/tag/build-bcd95fb30c91-hashlink-fill) | Public, 16 assets; tested tag resolves to the source SHA above |
| [Immutable public catalog](https://github.com/simonwjackson/korri-plugins/releases/download/build-bcd95fb30c91-hashlink-fill/catalog.json) | x86_64 and aarch64 signed native plugin archives |
| Catalog SHA-256 | `0c20fb26db499957ec1939e98dc80ad9b913a1eb74bd4d8b46b276fbb081bb9c` |
| Corresponding source | `hashlink-fill-source.tar.gz`, SHA-256 `1fd18678132c011693a5b4b10d535c1f10181eca0eb17a8b69a141053b44efa3` |
| Raw Nix cache | Six new narinfos, five distinct NAR payloads; `cache-index` advanced `cbf5c45` to `9d0add9` through the shared publisher |
| Existing personal catalog | All three existing records retained; two HashLink Fill architecture records appended with public GitHub archive URLs; exact served bytes checked at port 8450 |

| Architecture | Exact plugin output |
| --- | --- |
| x86_64-linux | `/nix/store/nk9ymx1r8xr9bzk7zh6ymrfdn925jczb-korri-plugin` |
| aarch64-linux | `/nix/store/8v8cafx1161wnb0fas9j3dqnxlb1k6g2-korri-plugin` |

Each runtime closure has nine paths. The inventories contain 1,024 files on
x86_64 and 1,023 on aarch64, including dependency license notices. They contain
no game files, saves, private keys or test closures. Native Nix verified contents
and personal-key signatures for all 18 exported paths. Upstream filtering kept
only three custom paths per architecture. Native Nix then verified all six
retained paths directly through the public Pages cache. The shared publisher
verified its public payloads and served metadata. Separate anonymous downloads
matched both plugin archives, catalog and corresponding source byte for byte.

## Checks (verified)

| Check | Result |
| --- | --- |
| `cargo test` | Six synthetic unit tests and two real process-exec tests pass |
| `cargo clippy --all-targets -- -D warnings` | Pass |
| `cargo fmt --check`, `nix fmt -- --check`, `git diff --check` | Pass |
| Focused Nix checks, both architectures | Strict TypeScript, direct/wrapped/non-matching compose, packaged files/licenses and real Core sandbox admission pass; ARM runs on fuji, not a device |
| `nix flake check --all-systems --keep-going --print-build-logs --option substituters https://cache.nixos.org` | All 25 check outputs pass; full suite ran once on the final implementation |
| Local owned-data integration | Exact v35 hash, two offsets, backup, mode, idempotence, corrupt-file refusal and child exit status pass with the final prebuilt binary |
| Source commit hook | Gitleaks passes; no bypass |

The cache override avoided a failing configured GitHub substituter. Existing
engine compilation and Fontconfig warnings did not fail the full suite.

## aka installation and setting (verified)

Review digest approved under the owner's no-units/no-ports rule:

`2113804405bb904de2acc3aa5d6e4c87494f31493d4c5479344804de911c07d8`

The review reported publisher `@simonwjackson`, state `Bound`, no native units,
TCP ports `[]`, UDP ports `[]`, and this warning:

> No native service is activated by this package. Approval covers the exact
> declaration and launch callback source. Game launch effects can access the
> runtime user's files and display; they must run in the existing runtime-user
> systemd sandbox, never as the administrator.

`korri plugins install` with that exact digest installed the plugin off.
`korri plugins on @simonwjackson:hashlink-fill` then enabled it.
No publisher trust or hosting configuration changed.

`korri launch-settings set --game dead-cells @simonwjackson:hashlink-fill/fill.enabled=true`
wrote Game/Any only. A fresh snapshot reports that origin and still reports
Gamescope enabled from Device/Any. No other game's setting changed.

## Live acceptance

The original was restored with the owner's `install -o korri -g korri -m 750`
command and its SHA-256 verified. The first launch attempt returned
`ActiveSessionConflict` and did not start Dead Cells. An end request had been
sent before the supervisor warned that the owner might be playing another game.
After that warning, the proof was paused and rewritten to require two idle
observations three minutes apart. It never ends an unrecognized launch ID.
No save file was restored or edited by the operator.

Two idle readings at 21:43:02 and 21:46:03 on 2026-11-15 (UTC−07:00)
preceded the successful proof. The accepted launches both reported a
2448×1848 display and no launch warnings:

| Evidence | Verified result |
| --- | --- |
| First launch | `e5c906fb3f87da18cb5f0026d79f1965`, accepted 04:46 UTC |
| Second launch | `ea41805fee25779342b890db5f18e01d`, accepted 04:49 UTC |
| Before first launch | Original SHA-256 `59350cad475a2375b9e39d7cd13fdb6e4ed9a027fd827ae5140f913c1c07ce7e` |
| Both launches, after about 60 seconds | Patched SHA-256 `c977689376ffce6d3400e50bb396de57ab8013846beb963e581b983acd6ac5ed` |
| Original backup | `${STEAM_HOME}/.korri/hashlink-fill/59350cad475a2375b9e39d7cd13fdb6e4ed9a027fd827ae5140f913c1c07ce7e`, exact original hash |
| Idempotence | Both observations: inode `48183823`, mtime `2026-11-16 04:46:06.233611346 +0000`, UID/GID `56774:1000`, mode `750` |
| Screenshot | `~/.local/state/hashlink-fill-publication/aka-dead-cells-fill.png`, 1224×924 from `grim -s 0.5`; visually inspected Dead Cells main menu fills the complete 2448×1848 view, without black bars |
| Saves | All four files (`dc_options.json`, `user_0.dat`, `user_1.dat`, `user_2.dat`) in `userdata/80924811/588650/remote/` retain exact mtime, ctime and size, including against the pre-pause snapshot |
| Final end | `korri end --yes` returned `phase: ended` for our second launch; fresh status reports `SessionCompleted` for that same ID |

The first evidence helper stopped after successful hash/stat capture because
an empty journal search returned status 1. Its guarded cleanup ended only the
recorded first Dead Cells launch. The second proof resumed without resetting
the file, captured the screenshot, and verified the unchanged inode/mtime.
No patcher journal entries were available; hashes, backup, metadata and the
actual screenshot are the live evidence. No controller or in-game save/load
acceptance is claimed.

Private receipts and reproducible Nix-shebang operator scripts remain in
`~/.local/state/hashlink-fill-publication/`. The obsolete unguarded proof script
is disabled locally and on aka. No game bytes or screenshots are included in
this public repository or release.

Remaining limits are intentional: a Steam update during startup can overwrite
the patch until next launch, Steam verification can download the modified file
again, and earlier wrappers must expose `steam-session` as an argv element.
A future per-game Steam command-prefix treaty would remove the pre-session
limitation; no such Core change was made here.
