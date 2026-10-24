# Signed cache publication

The public cache is `https://simonwjackson.github.io/korri-plugins/`.
GitHub Pages serves signed metadata from `cache-index`; NARs, corresponding
source, architecture path lists and offline metadata stay in `build-*` releases.
The old `cache` release remains frozen and readable for existing receipts.

`nix/publish-cache.sh` pins the shared publisher to a full tested commit from
`korri-os/plugins`. This repository does not maintain another copy of that tool.
The wrapper requires `EXPECTED_SOURCE_SHA`, an exact checkout and a clean tree.
Run it on a build machine, never on a device.

For a reviewed publication, resolve the tested source tag to its full SHA.
Use that same tag in both dry-run and publication checkouts. Before any build
or upload, check:

```sh
test "$(git rev-parse HEAD)" = "$EXPECTED_SOURCE_SHA"
```

Build only the approved package names with `build --system SYSTEM --paths-file
PATHS PACKAGE...`. Export the exact paths with the existing personal signing key.
Prepare each architecture separately, retaining its paths file and revision,
then use `combine`. Follow the shared publisher's
[PAGES-MIGRATION.md](https://github.com/korri-os/plugins/blob/8562bb480a211033426894a94c69c97a83a5aa0f/PAGES-MIGRATION.md)
and [PUBLICATION.md](https://github.com/korri-os/plugins/blob/8562bb480a211033426894a94c69c97a83a5aa0f/PUBLICATION.md).

After the separate publication approval:

```sh
bash nix/publish-cache.sh publish prepared \
  --repo simonwjackson/korri-plugins --tag "$NAR_TAG" \
  --index-branch cache-index \
  --cache-url https://simonwjackson.github.io/korri-plugins/ \
  --revision "$EXPECTED_SOURCE_SHA"
```

The NAR tag must already point at the tested full SHA. The publisher uploads
and verifies binary assets before appending metadata. It dispatches the Pages
workflow and checks exact served bytes before reporting success. The signer
remains `simonwjackson-plugins-1`. No key rotation belongs to this change.

The one-off metadata migration copies only existing public release assets,
with identical bytes and signatures. It does not publish a private cache.
Check-only workflows still do not sign or upload binaries. `cache-pages.yml`
deploys metadata only and cannot grant plugin permissions.

Device bindings and approval receipts are separate from public hosting.
Existing Mini V2 and Odin personal `file://` caches stay bound until their
selected outputs have approved public sources and a reviewed receipt migration.
This cache move grants no rights to game content. Keep each plugin's existing
resource audit and corresponding-source requirements. Never publish all flake
packages, test closures, user data or private cache contents as a shortcut.
