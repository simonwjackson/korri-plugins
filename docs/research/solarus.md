# Solarus plugin preparation

## Request and current state

The owner requested a Solarus Korri plugin for x86 and ARM in this repository.
Existing repository outputs define those platforms as `x86_64-linux` and
`aarch64-linux`. Work is isolated on `feat/solarus` in `.worktree/solarus`.
The implementation uses the existing plugin contract and nixpkgs recipe.
It pins Solarus 2.1.4 without changing the repository-wide flake lock.
No signed publication or device change has run.

## Checked sources

- This repository's locked nixpkgs evaluates `solarus.version` to `2.0.2`.
  The current upstream nixpkgs recipe packages `2.1.4` with `solarus-run` as
  its main program. Do not update the whole lock just to change this engine.
  Source: https://raw.githubusercontent.com/NixOS/nixpkgs/nixos-unstable/pkgs/by-name/so/solarus/package.nix
- The Solarus download page advertises `2.1.4`. The editor and desktop launcher
  are separate from the runtime needed by Korri.
  Source: https://www.solarus-games.org/download/
- Upstream `QuestFiles.cpp` in both `v2.0.2` and `v2.1.4` directly mounts a
  supplied quest archive or directory. It also looks for `data`, `data.solarus`,
  and `data.solarus.zip` beneath a supplied directory. It requires `quest.dat`.
  Source: https://gitlab.com/solarus-games/solarus/-/raw/v2.1.4/src/core/QuestFiles.cpp
- Linux saves use `PHYSFS_getUserDir()`, followed by the native `.solarus`
  directory and the quest's own write directory. The source does not consult
  `XDG_STATE_HOME` for that purpose. Runtime save/reload behavior is not tested.
- The current upstream nixpkgs recipe lists GPL-3.0-or-later for code and
  CC-BY-SA 3.0/4.0 for assets. Quest licensing is separate.

## Existing Korri grounding

The read-only `legacy` branch in `/home/simonwjackson/code/sandbox/korri` has:

- `product/platform/library/config/app-integrations.ts`: the `solarus` app
  uses `solarus-run` and one content-path argument.
- `product/platform/library/config/app-materializer.ts`: Solarus sets
  `XDG_STATE_HOME` to a temporary `solarus-state` directory. The upstream code
  above shows why this does not establish isolated saves. Do not copy this
  behavior and claim account isolation.
- `work/.archive/01KT2T2J2W97YT10B9FH6SGB93-refactor-launch-config-app-module/plan.md`:
  an example names a `solarus` system and `.solarus`/`.zip` extensions. This is
  an old proposal, not proof of a deployed content record. Claiming every ZIP
  is a Solarus quest risks identifying unrelated archives.

Use the real plugin builder, launch contract, host seed/declaration validation
and callback executor as the existing Zelda3 and Fallout checks do. No new Core schema or
source import mechanism is required merely to package a standalone runner.
Do not bundle quests or install an editor without scope approval.

## Owner decision

The owner selected separate saves per Korri account in response to
`solarus-save-location`. The runner sets `HOME` to the existing
`PluginLaunchInput.accountRoot`, retaining upstream's `.solarus` directory and
quest-defined write directory. It also uses accountRoot as cwd because native
Solarus can write `error.txt` relative to cwd. Core provisions accountRoot through
the existing launch output. Nothing imports, moves or deletes desktop saves.

The pinned Core's `services/korrid/src/launcher/linux_plugin.rs:79` always
supplies `root.join("users/default")`. The runner honors whichever accountRoot
Core supplies. Tests of two explicit roots prove that contract, not selected
account routing or a multi-account UI. No Core behavior changes in this slice.

The runner retains legacy's `solarus` identity and direct content-path argument.
Discovery claims only `.solarus`, an upstream archive suffix. This deliberately
omits `.zip` from legacy's example because the actual Core scanner matches file
extensions without inspecting archive contents. A ZIP claim would misidentify
unrelated games. Explicit launches still accept upstream ZIPs and directories.

The quest fixture's fields come from upstream's
`tests/testing_quest/data/quest.dat`. Its script exercises the native save API
used by upstream's `1533_savegame_write_escape.lua` regression. The fixture
contains no retail or third-party game assets. It is test-only, not bundled.

## Verification

Both native package checks passed on 2026-10-02. The actual engine loaded
an archive, a data directory and `data.solarus.zip`. Five launches persisted
and reloaded the first account's counter; a second account started at one.
Desktop saves and archive bytes stayed unchanged. The same check validates
ELF architecture, manifest identity, host seed/declaration validation, strict launch types,
literal arguments, unsupported launch inputs, and malformed-archive behavior.
It uses Core's production callback executor, with a test-only launcher that
adds Solarus's native headless flags.

A separate x86_64 test used the manifest's real program path with no headless
wrapper. It created an isolated Xvfb display, initialized `GlRenderer` with
Mesa 26.0.2 llvmpipe/OpenGL 4.5, ran the simulation loop, and reloaded a save
in a second process. OpenAL used its null output. RTKit was unavailable and
the engine printed an unsupported-operation message, but both processes
completed and wrote the expected save counters. This checks window and GL
initialization, not visible gameplay, physical input or audible sound.
The one-off build-machine script is `/tmp/solarus-window-check.py`.

The final command completed successfully on the x86_64 build machine and
its configured native ARM64 builder, `fuji`:

```sh
nix build --no-link .#checks.x86_64-linux.korri-solarus-plugin .#checks.aarch64-linux.korri-solarus-plugin --print-out-paths --print-build-logs
```

| Target | Successful check output |
|---|---|
| x86_64 Linux | `/nix/store/y58v5di502gqwpps3wnnajy2i0q62xdb-korri-solarus-plugin-check` |
| aarch64 Linux | `/nix/store/b7iw91maja6z6w1b1jvzri9fsd6dmscg-korri-solarus-plugin-check` |

A read-only review found no implementation blocker. It caught an overstated
account-selection claim, now corrected above, and narrowed host validation
claims to the actual `seed` operation. This does not prove signed-cache import,
full device admission, or account selection in Core.

Signed publication and device approval are separate from building. Existing
repository documentation requires approval for signed publication and physical
device acceptance. Do not bypass signature checks, change publisher trust, or
build from a target device.
