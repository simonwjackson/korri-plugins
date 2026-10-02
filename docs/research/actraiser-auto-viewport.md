# ActRaiser Auto viewport scope

The owner chose Auto viewport expansion for both flat and Diorama action
stages on 2026-10-02. Auto uses the drawable window dimensions, not a device
name or another fixed aspect-ratio list. It must reveal more of the scene,
not stretch or crop the original view.

This record defines the requested behavior and records the build-machine
verification. Device results belong in the deployment record.

## Existing implementation that defines the change

The baseline is upstream
`cdd76085a00e8beb090a7f0a07fcbc09a0e20670`.

| Existing source | What it owns |
|---|---|
| `src/app/settings.c` and `settings.h` | The native `extended_aspect` setting, enum labels, parser, persistence, and Screen ratio row. Auto extends this setting. |
| `src/host/host_display.c` | Drawable dimensions, horizontal render budget, pixel aspect, resource rebinding, and retained-frame invalidation. |
| `src/present/display_geometry.h` | The existing 120-column-per-side horizontal limit. |
| `src/actraiser/enhancements/actraiser_frame_plan.c` | Per-frame action-stage bounds and per-layer vertical clipping. |
| `src/actraiser/actraiser_action_bg.c` | Available rows above and below the original 225-row gameplay camera range. |
| `snesrecomp-go/runtime/src/runner/runner_ppu_services.c` | Actual extra-row rendering, with a 64-row-per-side limit. |
| `src/present/frame_slot.c` | Completed-frame capture geometry and the authentic source offset. |
| `src/present/present.c` | Flat upload, composition, and output viewport. The baseline uploads only 224 rows in the flat path. |
| `src/diorama/diorama.c` | Existing presentation of vertically expanded capture planes. |

The renderer already produces extra vertical rows. The flat renderer does
not yet display that full capture in the baseline. Simply enabling the
Diorama row budget for flat mode would truncate the native scene during
upload. The upload, composition, HUD, effects, and output transforms must
agree about the expanded frame.

## Required behavior

Auto preserves the original 256x224 scene and its selected pixel aspect.
For a wider window, it expands horizontally. For a narrower window, it
expands vertically. Square output and the observed Mini V2 output of
1240x1080 are required cases. Both CRT pixel aspect and square pixels remain
selectable.

The requested display canvas and the available captured rows are separate.
At a finite level boundary, unavailable rows must not change the scale of
the native scene or wrap to unrelated tiles. Existing per-layer bounds
remain in force. The gameplay camera does not move to manufacture missing
world content.

Auto must respond to actual drawable-size changes, including pixel-density
changes. A resize event must not force the window back to a preset size.
Paused redraws must not describe new geometry while displaying old pixels.
Switching between Auto and a manual ratio must preserve the manual ratio's
existing behavior. Auto must persist through the native setting path.

Classic town and Mode 7 screens keep their current framing. Their vertical
scanline state cannot be expanded merely by requesting more action-stage
rows. Existing manual Diorama vertical extension remains available outside
Auto. Package defaults and existing account settings do not change merely
because a new package is installed.

## Cost and limits

The existing capture limits remain 120 columns and 64 rows per side.
Extreme window shapes can retain borders when those limits are reached.
A finite room can have no content beyond an edge. Auto cannot invent that
content or repair every upstream tile-streaming seam.

This change does not establish campaign completion or campaign save/reload.
Runtime verification uses an isolated account, the owned ROM, and upstream's
existing replay and SRAM fixtures. It must not alter the player's account.
No ROM, generated source, private executable, or gameplay screenshot belongs
in the public integration repository.

## Implementation

`plugins/actraiser/auto-viewport.patch` is the hand-written source change
against the pinned upstream revision: 49 paths in `src/`, `tests/`,
`CMakeLists.txt`, `snesbuild.ini`, and the interface message catalog.
It contains no ROM data or generated game code.

| Area | Change |
|---|---|
| Setting | `kScreenAspect_Auto` is appended to `extended_aspect`. Saved indices and labels for the manual ratios keep their meaning. |
| Geometry | A pure solver expands one axis of 256x224 from the drawable size and pixel aspect, rounded to whole pixels per side and capped at 120 columns and 64 rows. An unusable size (for example a minimized window) keeps the previous budget. Resizes never call `SDL_SetWindowSize`. |
| Frame | Each completed frame keeps the requested canvas and the captured rows as separate values. Rows that a room cannot supply stay empty; the valid rows are never rescaled to fill them. |
| Flat path | Upload, composition, FX masks, HD replacements, HUD and title cards use the requested canvas. The HUD status groups stay anchored to the canvas top. |
| Diorama path | Planes stay normalized to 224 world rows; only the automatic fit uses the requested canvas. Manual orbit, zoom and tilt still work. |
| Scope | Auto acts only in action map groups outside Mode 7 and towns. Non-action screens report a 256x224 canvas with no budget. |

Review found two defects, both fixed with regression tests. At startup,
before a drawable existed, Auto could coerce a saved `display_mode` to 4:3 and
leave margin sprites culled. A failed background provider kept positive
vertical clip rows and could read unrelated tilemap rows; failed layers now
get zero extra rows while the canvas stays the same. A third defect let a
fatal render still report a successful composite capture; it now reports a
failed capture.

Capture-only diagnostics support the acceptance test. They run only for a
scheduled final-composite screenshot and add no work to ordinary frames.
`[viewport-check]` records the drawable, budget, live margins, logical canvas
and the viewport that the real draw returned. `[viewport-hud]` lists the HUD
rectangles from the HUD layout code for that same frame. `[viewport-projection]`
lists the projected screen bounds of each Diorama plane's native and extended
bands, taken from the triangles that were actually drawn.

## Verification on build machines

The engine build runs 21 targeted native tests on both architectures; all
passed. Three are new (`auto_canvas`, `host_viewport_trace`,
`dev_tools_capture_trace`); the others were extended. Six of them also passed
under ASan, UBSan and leak detection on an earlier snapshot of the patch,
before the review fixes and diagnostics were added.

`verify-actraiser-auto` ran the packaged plugin through production
`korrid plugin-launch` with software Vulkan (llvmpipe, Mesa 25.3.2) in an
owned Xvfb. Each of four isolated accounts (flat and Diorama, square and CRT
pixels) saved Auto through the native settings path, reloaded it without
environment overrides, and replayed upstream's Aitos fixture for exactly 3000
frame presents with no re-presents. The harness resized the game's own window
between captures. The x86_64 result:

| Drawable | Square budget (L/R/T/B) | CRT budget | Real scene content found outside the 256x224 view |
|---|---|---|---|
| 800x800 | 0/0/16/16 | 0/0/37/37 | Below (flat); above and below (Diorama CRT) |
| 1240x1080 (Mini V2) | 1/1/0/0 | 0/0/18/18 | Left and right (flat square); rendered rows below (flat CRT); none detected (Diorama) |
| 1600x900 | 71/71/0/0 | 43/43/0/0 | Left and right, all four cases |
| 320x1200 | 0/0/64/64 | 0/0/64/64 | Above or below, all four cases |
| 2400x400 | 120/120/0/0 | 120/120/0/0 | Left and right, all four cases |

The same test on the aarch64 build machine (llvmpipe, Mesa 25.3.2) passed all
four cases with the same budgets, live margins and content results.

In room 04/05 at 320x1200, the room supplied only 24 of the 64 requested rows
above the view. The capture kept the full 352-row canvas and left the missing
rows empty: no stretch and no wrapped tiles. The classic screen before the
action stage (map 00/09) kept a 256x224 canvas with no budget under Auto.

Two limits of this evidence matter:

- At 1240x1080 with CRT pixels, the 18 extra rows above the view sit under the
  relocated HUD, and the rows below show uniform floor and backdrop in the
  captured frames. The census can show that those rows are rendered, not
  cleared. It cannot show distinct scenery there. In Diorama at this size,
  the few extra rows project inside the excluded native-plane bounds, so the
  census has nothing to count. Distinct scenery outside the view was shown at
  the other sizes, through the same code paths.
- The pixel checks run with CRT, host FX, Diorama blur, rim light, edge
  anti-aliasing, shadows, skybox, shoebox, backdrop and Diorama sprites
  turned off, in temporary accounts only. FX placement under Auto has unit
  tests with real SDL rendering, not GPU-capture proof.

## Menu treatment

The existing native Screen ratio row remains in place. Auto is another
selectable value with help that says it expands action stages to the window.
No settings-page redesign or new Korri configuration format is needed.
[Higgsfield's settings selector](https://mobbin.com/screens/e21d4298-6072-4e14-a1e3-eecd4f23fd2e)
also places Auto beside explicit options with nearby help. That selection
pattern is relevant; its modal styling is not appropriate for the game's
existing controller-driven menu.
