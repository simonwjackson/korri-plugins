# Nocturne integration verification

Verified on 2026-10-02 for source commit `56729d4`.

## Sources and input

The owner requested NocturneRecomp as a personal Korri plugin on Linux x86_64
and ARM64. Upstream v1.4.5 is commit
`5390d5ec91d4b0d0c87a6db35ea351343d04cd91`. Its pinned ReXGlue SDK is
`birabittoh/rexglue-sdk`, tag `sotn-nightly-20260817-7766f971`, commit
`7766f97126a40399d76105d431ae37c802eba740`.

The owner's file was on `myoko`:

```text
/home/simon/Downloads/Castlevania - Symphony of the Night (World) (XBLA).7z
```

The archive contained the LIVE/STFS package
`58410847/000D0000/9F2DAA064D494AA82B43B65362C59E9B89A88F8F58`, 99901440 bytes.
The agent extracted that package and its complete assets into a new sibling
directory. The original archive was not changed or replaced. The ready input is:

```text
/home/simon/Downloads/Castlevania - Symphony of the Night (World) (XBLA)/assets/default.xex
```

| File | Measured SHA-256 |
|---|---|
| Original `.7z` | `f3c0184b49b8e89c42634048a944f5e39cdf319b76f68f4e70a40255957b35cc` |
| LIVE/STFS package | `df41551dd71b7f0f46b4935b1b6d5ff9680acf37e5bbed27a44c1f9358e14ed8` |
| Extracted `default.xex` | `26a58b074c5dd6185b77a8111a0012866d11cba674b4b0810d79dbf07ad68aa6` |

The executable hash matches upstream's accepted input. The archive hash was
checked again on myoko after extraction. Remote tools were fetched prebuilt
with local and remote Nix builds disabled. No game data entered Git or Nix inputs.

## Verified packages

| Architecture | Plugin output | Native output |
|---|---|---|
| x86_64-linux | `/nix/store/f8hzmr2yf0g6b82ni8d3k0z7a8lh6bcq-korri-plugin` | `/nix/store/acnmwnfmwli9r99njbmgbg6pg1ihsyiw-nocturnerecomp-1.4.5` |
| aarch64-linux | `/nix/store/wz2fd5jwmvdsdijv194f3ba7nwh6ydy6-korri-plugin` | `/nix/store/pnj0blm7nr8wnd70hw4nj8sj0ik00v85-nocturnerecomp-1.4.5` |

Both architecture checks passed on their native build machines. These checked
release ELF architecture, dependency loading, strict contract types, actual
packaged source, Core admission, the sandboxed launch callback, literal argument
handling, and rejection of unsupported inputs. Rebase checks also passed for
both Fallout CE plugins on both architectures, preserving the concurrent change.

## Owned-data startup

The opt-in `verify-nocturne` test passed on Zao and Fuji using private copies of
the supplied assets. It ran through Core's real `plugin-launch` executor, with a
private Xvfb display, D-Bus session, PulseAudio null sink, and software Vulkan.
Both final cold-launch screenshots showed the KONAMI startup logo. The agent
opened the images, rather than treating process survival as rendering evidence.

The checks verified cold and cached launch, account locking, unchanged source
hashes, configuration preservation, and preservation of existing account data.
Hostile native environment variables were removed from the actual running
process. Saved path overrides and self-update settings were rejected. Escape
regressions target disposable test files, never the owner's original files.

| Build machine | Private evidence directory |
|---|---|
| Zao, x86_64 | `/tmp/nocturne-owned-check-1p6_yxw2` |
| Fuji, aarch64 | `/tmp/nocturne-owned-check-mdmzm40u` |

Each directory contains `cold.log`, `warm.log`, `cold.png`, `warm.png`, native
logs, and temporary account state. These are private temporary evidence, not
repository assets or permanent storage guarantees.

## Limits and deployment

Startup is verified, not full-game completion. Physical controllers, audible
output, gameplay saves, and handheld GPU performance are unverified.
The native process did not exit within 20 seconds of the test's window-close
request on either architecture. The test reports this and stops its own process.
It does not claim clean shutdown or turn a forced exit into a save/load result.

The supplied location identifies game storage, not a selected Korri deployment
target. Myoko had no loaded system or user Korri service when checked. No plugin
was installed there, no publisher trust changed, and no binary cache was
published. Target installation still needs a compatible Korri runtime and the
normal signed-cache, publisher-binding, and exact-package approval path. Public
publication of the translated native binary needs a separate rights review.
