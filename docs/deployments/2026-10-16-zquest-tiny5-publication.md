# Tiny5 public2 signed-cache publication, 2026-10-16

Both tested packages and their corresponding source are public. Both release
tags point to `4b80347334b69675868ff272ec92438b60e49032`, not a later documentation
commit. The initial signature-preservation blocker was resolved with native Nix.
No device was contacted or installed.

| Release | Verified state |
| --- | --- |
| [Corresponding source](https://github.com/simonwjackson/korri-plugins/releases/tag/zquest-public-4b80347334b6-source) | Public; existing release ID `415076514`. Both archives, `SHA256SUMS` and `revision.txt` passed anonymous HTTP SHA-256 verification before binary publication and again afterward. |
| [Binary batch](https://github.com/simonwjackson/korri-plugins/releases/tag/zquest-public-4b80347334b6) | Public; existing draft ID `415078700` was reused. All 13 assets passed anonymous download/hash checks. Its notes link to corresponding source. |
| [Shared signed cache](https://github.com/simonwjackson/korri-plugins/releases/tag/cache) | Six new narinfos added. All nine pre-existing asset IDs, sizes and digests remain unchanged. Existing software-MIDI narinfos retain their original NAR URLs and signatures. |

Public cache: `https://github.com/simonwjackson/korri-plugins/releases/download/cache/`.
The existing public key remains
`simonwjackson-plugins-1:4SchQgTMNU3syZ2ZzN/cJXPMigc/PIt+EaqHAStgJs8=`.
No key, trust configuration or publisher check changed. `require-sigs` stayed true.

## Exact tested packages

| Architecture | Package |
| --- | --- |
| x86_64-linux | `/nix/store/g4l7p0nrmh956yi2wpfh36iqldpavak1-korri-plugin` |
| aarch64-linux | `/nix/store/yqc52bk85hcaxhq32cymly97nry6fl85-korri-plugin` |

The [off-device validation](2026-10-16-zquest-tiny5-validation.md) lists native
font, MIDI, interpreter, input, save/reload and ending checks. Publication did
not rebuild or change either package. No quest or private preview image was
included in either release.

## Public corresponding-source SHA-256

| Archive | SHA-256 |
| --- | --- |
| `zquest-classic-source-x86_64-linux.tar.xz` | `2ac2bd57aa96d592ab7750724a6bd7ff49beff0308a019498957bd8cc17f14db` |
| `zquest-classic-source-aarch64-linux.tar.xz` | `7a650275aa1fae087b6848b185fc09b09b1e27d86e1d7671f61ed0613ad09fee` |

The source archives were re-downloaded anonymously immediately before resuming
binary publication. The exact tested revision in both releases' `revision.txt`
and the architecture package path manifests passed verification.

## Signature-preservation resolution

The first attempt correctly stopped before binary uploads: the published ARM
software-MIDI narinfo had `fuji-1` and personal signatures, while the fresh local
export had only the personal signature. The publisher allows only URL changes
when retaining an existing narinfo. Its comparison was not weakened.

Before adopting signatures, native Nix verified the existing public dependency's
NAR contents and personal signature. Native local and remote `path-info` agreed
on NAR hash, size and references; `nix hash path` confirmed the local bytes.
Then the supported command imported both original signatures into the local
build store, without granting trust to another key:

```sh
nix store copy-sigs \
  --substituter https://github.com/simonwjackson/korri-plugins/releases/download/cache/ \
  --option substituters '' \
  /nix/store/4w4n7izrxpmj0sb4z0jf9qpkjksjh7ly-zquest-classic-software-midi
```

Nix reported `imported 2 signatures`. Both signature strings were preserved
byte-for-byte. The original `korri-cache export`, `prepare` and `combine`
commands regenerated ARM artifacts in fresh private directories. The unchanged
append-only preflight then passed. No prepared archive was hand-edited, and no
`fuji-1` signature was generated. The original publisher reused the existing
empty binary draft, published its verified payloads, then added cache metadata.

## Verification and limits

| Gate | Result |
| --- | --- |
| Exact runtime closure review | Passed: 138 paths per architecture, 276 distinct paths and 29,682 files. Eight custom paths only; no private quests, saves, replays, keys or unrelated plugins. Two `root.key` files are reviewed public DNSSEC trust anchors. Both final resource gates passed. |
| Signed local export | Native Nix content/signature verification passed for all 138 paths per architecture against the established personal key. Export disabled builds and fallback. |
| Upstream filtering | 134 paths per architecture verified against `cache.nixos.org`; those payloads were not uploaded. |
| Public binary assets | All 13 assets anonymously downloaded and SHA-256 checked: eight custom NARs, two offline metadata archives, two package path manifests and `revision.txt`. |
| Public metadata/NARs | All eight custom narinfos and their referenced compressed NAR bytes passed anonymous retrieval, identity and hash checks. Native Nix verified NAR contents and published-key signatures both from the downloaded files and directly through the public HTTP cache. |
| Offline metadata | Both public archives match the signed exports exactly, with 138 narinfos per architecture. |
| Append-only cache | All nine original assets remain byte-identical with unchanged IDs. Only the six expected new engine/launcher/plugin narinfos were added. |

Private commands, receipts, asset snapshots and validation logs remain under
`~/.local/state/zquest-tiny5-publication/`. Key receipts are `commands.log`,
`receipts.jsonl`, `native-preservation.log`, `preserved-prepare.log`,
`resumed-publish.log`, `public-download-verification.log`,
`native-public-http.log` and `public-verification.json`. The earlier partial
state is retained as history. No full test suite was rerun for documentation.

Publication does not establish physical-controller input, audible output,
arbitrary quest compatibility or device acceptance. No device trust, image pin,
installation or running session changed.
