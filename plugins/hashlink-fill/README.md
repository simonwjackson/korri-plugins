# HashLink Fill

`@simonwjackson:hashlink-fill/fill` is an opt-in launch modifier for Dead Cells
(Steam app `588650`). Enable it for that game, not for the whole device:

```sh
korri play dead-cells --set @simonwjackson:hashlink-fill/fill.enabled=true --keep
```

It removes the two stage-size clamps in `Main.onResize` so the game can fill the
window without a 16:9 box. It does not stretch the image. Other runners return
unchanged plans. Other Steam apps execute unchanged. The effect runs in the
launched `hl-fill` program as the runtime user, never in plugin declaration code.

The Rust reader accepts HLB version 4. It locates the named method, reads the
whole bytecode, and proves a byte-exact no-edit round trip before changing any
operand. The JSON fix describes the opcode pattern, two required matches and
one operand replacement per match. It is this patcher's format, not a Korri
configuration contract. Known hashes for build `23762174` / v35 are:

| File | SHA-256 |
| --- | --- |
| Original | `59350cad475a2375b9e39d7cd13fdb6e4ed9a027fd827ae5140f913c1c07ce7e` |
| Patched | `c977689376ffce6d3400e50bb396de57ab8013846beb963e581b983acd6ac5ed` |

Unknown builds must parse, round-trip and match exactly twice. Known originals
must also produce their known patched hash. Missing files, unsupported formats,
wrong match counts and filesystem failures log a warning and launch unchanged.
With `NOTIFY_SOCKET`, the program also attempts `systemd-notify --status`.
It replaces itself with the original command, preserving signals and exit codes.

Backups stay in `${STEAM_HOME}/.korri/hashlink-fill/<original-sha256>`.
`PluginComposeInput` has no cache root; the existing Steam account root is the
writable fallback. No backup is overwritten. Patching uses a verified temporary
file and atomic rename, retaining owner and mode. Already-known patched files
are not written again. For an unknown build, a cache receipt is checked against
its saved original and the same patch before accepting the patched hash.
Removing the modifier does not restore the file. To undo, end the game and
restore the appropriate backup, or use Steam's verification feature.

## Limits

1. The modifier runs **before steam-session**. A Steam update during that launch
   overwrites the patched file, so that one launch runs unpatched. The next
   launch patches it again.
2. It changes Steam's game file on disk. Steam **Verify files** will flag or
   download it again. The backup is private game data and must not be published.
3. Earlier wrappers must pass the Steam program through as an argv element.
   Compose finds `steam-session` directly or inside Gamescope's argv and accepts
   only a positive numeric app ID. It wraps the whole plan, keeping Gamescope
   and its output-size and streaming behavior. Shell-command strings are not
   inspected. An unrecognized plan launches unchanged.

A clean future design needs a Core contract for a per-game Steam command prefix.
This plugin does not implement that contract or add another launch path.

## Build and test

Run on a build machine, never on a target device:

```sh
nix build --no-link .#korri-plugin-hashlink-fill
nix build --no-link .#checks.x86_64-linux.korri-hashlink-fill-plugin
nix build --no-link .#checks.aarch64-linux.korri-hashlink-fill-plugin
```

The package runs synthetic Rust tests. The Nix check runs strict TypeScript,
compose and real Core sandbox admission checks. CI needs no game data. The
existing Core pin `62432aa04b199caf47399bee23e25ae949efdb92` already supports
`PluginComposeInput`, explicit `<plugin-id>/<key>` modifier IDs, and modifiers
without settings handlers. No Core pin change is needed.

For an optional local integration test, pass the built patcher binary:

```sh
nix/hashlink-fill-owned-check.py /nix/store/…-hl-fill-0.1.0/bin/hl-fill
```

It reads `~/deadcells-rescue/arfix/hlboot.orig.dat`, skips if absent, and uses a
private temporary directory outside the repository and Nix store. It checks the
exact patched hash, offsets `3088883` and `3088928`, original backup, mode,
idempotence, corrupt-file refusal and child exit status. Never put game bytes
in a derivation, source tree, release, cache or fixture committed to Git.

## Credits and license

The patch algorithm is from TLin-Y's MIT
[DEAD-CELLS-Any-Aspect-Ratio mod, `deadcells_ARFix.cpp`, `PatchStage`](https://github.com/TLin-Y/SteamAnyAspectRatioMods/tree/main/Dead%20Cells).
It recognizes `ToInt r; JSGte r,w,+2; Mov d,r; JAlways +1; Mov d,w` twice and
changes the comparison's first register to its second. The bytecode layout
follows the Haxe Foundation's MIT HashLink `src/code.c` and `src/opcodes.h`.
See [LICENSE](LICENSE). The plugin contains no game data. Dead Cells and its
files remain the property of their respective rights holders.
