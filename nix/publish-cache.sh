#!/usr/bin/env -S nix shell nixpkgs#bash nixpkgs#git nixpkgs#nix -c bash
# Build-machine entry point. Use the shared publisher, not a local fork.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
: "${EXPECTED_SOURCE_SHA:?Set EXPECTED_SOURCE_SHA to the full tested plugin source commit}"
[[ "$EXPECTED_SOURCE_SHA" =~ ^[0-9a-f]{40}$ ]]
test "$(git rev-parse HEAD)" = "$EXPECTED_SOURCE_SHA"
test -z "$(git status --porcelain)"
exec nix run github:korri-os/plugins/8562bb480a211033426894a94c69c97a83a5aa0f#korri-cache -- "$@"
