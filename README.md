# Personal Korri plugins

This is `simonwjackson/korri-plugins`, built separately from Korri OS.
The publisher namespace is `@simonwjackson`, following the existing personal
PICO-8 producer. A namespace declaration does not grant device trust.

## Packages

| Output | Plugin | Platforms |
|---|---|---|
| `korri-plugin-skate-3` | `@simonwjackson:skate-3` | x86_64 Linux only |

[Skate 3](plugins/skate-3/README.md) adds a launcher to an existing library
game when its recorded whole-file hash matches an accepted disc. It reuses
the pinned prebuilt native launcher. The repository contains integration
source, tests, documentation and hashes, not an ISO, XEX, title update,
compiled recompilation or NAR archive.

The native release is unfree. Do not publish its binary closure without a
separate rights review and approval. This repository has no binary-cache
publication workflow. Device installation and gameplay remain outside the
package-only scope. Signature and permission checks must stay enabled.

## Build and verify

Run on a build machine, not a target device:

```sh
nix run .#help
nix build --no-link .#korri-plugin-skate-3
nix build --no-link .#checks.x86_64-linux.korri-skate3-plugin
```

The gate checks the actual packaged source, generated manifest, personal
publisher identity, strict launch-contract types, host admission, and
production sandboxed launch preparation with literal file paths.
