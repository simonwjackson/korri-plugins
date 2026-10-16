# Tiny5 public2 publication: source published, binaries blocked

The tested revision `4b80347334b69675868ff272ec92438b60e49032` was pushed to
`main`. Both new tags point to that exact revision. No device was contacted.
Binary publication stopped at the append-only metadata preflight. No binary
payload or new cache metadata was uploaded.

| Release | State |
| --- | --- |
| [Corresponding source](https://github.com/simonwjackson/korri-plugins/releases/tag/zquest-public-4b80347334b6-source) | Public; release ID `415076514`. Both archives, `SHA256SUMS` and `revision.txt` passed anonymous HTTP SHA-256 verification. |
| `zquest-public-4b80347334b6` | Empty draft; release ID `415078700`. The binary release notes link to corresponding source. |
| [Shared signed cache](https://github.com/simonwjackson/korri-plugins/releases/tag/cache) | Unchanged. All nine existing asset IDs, sizes and digests match the preflight snapshot. |

## Exact tested packages

| Architecture | Package |
| --- | --- |
| x86_64-linux | `/nix/store/g4l7p0nrmh956yi2wpfh36iqldpavak1-korri-plugin` |
| aarch64-linux | `/nix/store/yqc52bk85hcaxhq32cymly97nry6fl85-korri-plugin` |

These public2 packages are not yet available from the public cache. Their
[off-device validation](2026-10-16-zquest-tiny5-validation.md) remains valid;
this publication attempt did not rebuild or modify either output.

## Public corresponding-source SHA-256

| Archive | SHA-256 |
| --- | --- |
| `zquest-classic-source-x86_64-linux.tar.xz` | `2ac2bd57aa96d592ab7750724a6bd7ff49beff0308a019498957bd8cc17f14db` |
| `zquest-classic-source-aarch64-linux.tar.xz` | `7a650275aa1fae087b6848b185fc09b09b1e27d86e1d7671f61ed0613ad09fee` |

Both archives were anonymously downloaded and hash-verified before the binary
publication phase. Their source release also carries the exact tested revision.

## Checks and blocker

- Reviewed the two exact runtime closures: 138 paths each, 276 distinct paths
  and 29,682 files. Eight paths are custom plugin/player/launcher/MIDI outputs.
  No user quest, save, replay, private key or unrelated plugin was included.
  The filename scan's two `root.key` files were reviewed public DNSSEC trust
  anchors, not private keys. Both final player resource gates passed.
- The existing personal private key's derived public key matched the established
  `simonwjackson-plugins-1` key. No key or trust configuration changed.
- Exported only the exact two plugin roots with the existing `korri-cache` tool.
  Nix verified contents and signatures for all 138 exported paths per architecture
  against the published personal key. Build jobs and fallback were disabled
  during export. `require-sigs` stayed true.
- Preparation verified 134 paths per architecture against `cache.nixos.org`.
  The combined local batch contains eight custom NARs, eight narinfos, both
  offline metadata archives, architecture path manifests and `revision.txt`.
- Append-only preflight rejected `4w4n7izrxpmj0sb4z0jf9qpkjksjh7ly.narinfo`,
  the unchanged ARM software-MIDI output. Its published metadata has both
  `fuji-1` and `simonwjackson-plugins-1` signatures. The fresh export has only the
  personal signature. NAR identity, compressed-file hash/size and personal
  signature match, but the missing additional signature is not an allowed
  URL-only change.
  The check was not weakened; no signature or existing asset was replaced.

The source draft initially needed another read after GitHub's release list did
not yet expose it. The identical upload then passed all source checks. The
later signature conflict is the terminal blocker, not that initial lookup.

Private commands, receipts, exact asset snapshots, signed local caches and
non-private validation logs are retained under
`~/.local/state/zquest-tiny5-publication/`. `commands.log`, `receipts.jsonl`,
`closure-audit.log`, `metadata-conflict.json` and `conflict-diagnosis.log` record
the partial state. Private preview screenshots and quests were not uploaded.

Resume requires preserving the existing signature under the normal append-only
publisher contract. Public plugin narinfo/NAR retrieval, public path manifests
and public offline metadata verification remain unperformed because binaries
were not published. No installation, device trust change or device acceptance
is claimed.
