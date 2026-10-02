# Skate 3 movie build update on Mini V2

The owner requested the verified movie build through the installed plugin so controller input can use korrid. The plugin update is installed and enabled. Library import and launch are pending because The Simpsons Game was running when the import preflight checked the active session. The import stopped before changing files or stopping korrid.

The owner also requires an explicit question-tool prompt before the next Skate 3 launch. Do not launch until that approval arrives.

## Verified artifacts

| Item | Value |
|---|---|
| Native flake | `4e58e784407326d4da9dab5ab2b44fd32eb03c22` |
| Plugin | `/nix/store/ahgzh5wlv8xy87ysiajn3qwxwyh4g21i-korri-plugin` |
| Launcher | `/nix/store/n378x2v9crqrahzk6v6965nzvwnak5xi-skate3` |
| Native build | `/nix/store/k41yg113gmzas8g29g4k3d8gqppjwhjp-skate3-source-unwrapped-2.0.2` |
| Approval digest | `0cc3c1b80b89e47bb4bd5a6ffe3e9fb50413a263fbd688e7daebbbf06e03bfb0` |
| Device evidence | `/var/tmp/skate3-miniv2-deploy-gvtpmi20` |
| Bare ISO | `/var/lib/korri/roms/Skate 3.iso` |

The ISO has 7,838,695,424 bytes and SHA-256 `bd8d430188aa61b0ebf2e33e5672822dd7e59c9080fc09e802195e1ee75ebff0`. It was streamed privately from the owner's ZIP on aka. Both ends verified its identity, and the ZIP reader verified its CRC. The original archive stayed unchanged.

Only the native flake pin, its lock entry, and documentation changed. The existing ARM64 plugin implementation, whole-ISO gate, launch callback, and other inputs are unchanged. Both architecture-specific plugin checks passed. The native game was already built and tested on fuji and the Mini, so this update reused that prebuilt output.

The normal `korri-plugin inspect` and `update` commands used the existing personal publisher and private cache. Recursive signature verification passed. The update added no services, ports, dependencies, permissions, or publisher bindings. Other plugin selections, system generation, and the korrid PID were unchanged during the update.

Native intro movies passed a 227-second run with complete captures and no new GPU fault. The owner reported no audio/video issues. Forced emulated fallback still has image corruption; native FMV must stay enabled. Controller routing, movie skipping, and gameplay remain unverified until the approved plugin launch.

## Pending steps

After the active game finishes, use the existing native `korrid catalog import /var/lib/korri` workflow with the daemon stopped and catalog backups. Reuse the existing parent scan instead of creating another child scan. Verify the discovered Skate 3 route selects the exact plugin above. Restore native FMV settings only after verifying the enabled plugin points to the fixed launcher.

Then prompt the owner before launch. Launch through `app.local-games.launch.selected`, not the manual diagnostic script. Verify the exact native executable, runtime-user sandbox, active korrid session, and protected controller route. Keep all build, signature, and input permission restrictions in force.
