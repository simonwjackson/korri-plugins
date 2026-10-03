# Public player replacement resources

These resources replace the default media in ZQuest Classic revision
`882c906b17e35b4105188e6305ae2929aeba30e3`. They contain no quests.
They do not establish rights to user-supplied quests, music or graphics.

## Inventory and origin

| Output | Origin and license |
| --- | --- |
| `sfx.dat` | 61 original procedural cues from `public-assets.py`, one per required sample slot. Integer triangle-wave sweeps and seeded filtered noise; no recordings, transcriptions, melodies or upstream sample bytes. MIT terms below. |
| `assets/{dungeon,ending,gameover,level9,overworld,title,triforce}.mid` | Generated format-0 MIDI: tempo 120 BPM, all-notes-off controller, 255 quarter-note-spaced markers and end-of-track at beat 256. No note events. The timeline covers the engine's ending loop (129–225) and overworld loop (17–EOF); a one-beat empty track cannot safely use those loop points. MIT terms below. Only engine defaults are silent; quest-provided music is not changed. |
| `modules/classic/classic_fonts.dat` | **Korri Compatibility Raster**, a pixel-rasterized, resized derivative of the licensed ProggyVector TTF. The full embedded copyright and license entries are in `public-assets-font-license.txt`. MIT, public-domain DejaVu contributions, and Bitstream Vera font terms apply as described there. Do not sell these fonts by themselves. |
| `assets/cursor.bmp` | Original generic outlined pointer, generated geometrically. MIT terms below. |
| `assets/gui_pal.bmp` | Generated grayscale and RGB-cube palette with required engine black/white indices. MIT terms below. |
| `public-assets-provenance.json` | Generator/input hashes, renderer versions, slot inventory and output hashes. Generated without absolute source/store paths or timestamps. MIT terms below. |

The TTF input is `resources/ProggyVector-Regular.ttf` from the pinned source,
SHA-256 `dae80a9b9bb23a37f60465dd93de9365a8ddd43300adc304d96f91ce54c28dd5`.
The generator refuses other font inputs. It does not modify or emit the
original TTF. The player package retains that TTF separately for its debugger,
and the corresponding-source archive includes it with its embedded notices.

Font slots keep their historical compatibility identifiers, not their original
visual designs. `public-assets-metrics.json` contains only measured numeric
heights and byte-character advance widths, obtained with the pinned Allegro
reader from `classic_fonts.dat` (SHA-256
`e1008c6ea910a67071ef5825a9dfe5324fbacd15af2e050d0a5325e13f880958`).
It contains no glyph pixels. Rebuilding does not read the original datafile.
ASCII text keeps the measured advances and line heights; glyph appearance
changes. Accents and narrow cells can lose detail at six/eight-pixel sizes.
Byte 132/133 in `FONT_NES` map to left/right arrows as required by `title.cpp`.
Other C1 control slots show a replacement character. Latin slots use Unicode;
custom symbolic, fictional and non-Latin legacy alphabets are not reproduced.
This is not full compatibility with quests that use those decorative symbols.

## Format and reproducibility

`public-assets.py --output DIR --source SOURCE --font TTF` requires an empty
output directory and Python with Pillow/FreeType. It reads only the explicit
TTF, source slot/version headers, numeric metrics and this notice. It performs
no network access, device access or upstream-media fallback. `public-assets.nix`
provides the dependencies and writes a flat resource tree directly to `$out`.
Import it with `{ pkgs, source = pinnedSource; }`.
Use the locked Nix inputs for repeatable font rasterization; different
Pillow/FreeType versions can produce different pixels.

The datafile/packfile encoder follows the pinned Allegro reader in
`third_party/allegro_legacy/src/datafile.c` and `file.c`. It writes uncompressed
`ALL.` datafiles, typed uncompressed chunks, signature objects, and the font
loader's `longtan` password encoding. This password is a format requirement,
not a security measure. There are 62 sound objects and 103 physical font-file
objects: signature at slot zero, 101 fonts at slots 1–101, and `GrabberInfo`
(type `info`) at slot 102 with newly authored metadata text. The Allegro
loader calls its callback 103 times and adds an uncounted `DAT_END` terminator.
ZQuest's `load_datafile_count` subtracts one callback for metadata, returning
the required 102. No engine-loader adjustment is needed.

Run `public-assets-validate.py --resources DIR` for structural checks. Add
`--allegro-library /path/to/liballeg.so` to validate using the actual upstream
reader with `SYSTEM_NONE`; it opens no display or sound device. Add
`--midi-playback` to test the native timer/sequencer with the silent `MIDI_NONE`
driver, including two passes through each default loop boundary and natural
completion of non-looping defaults. This initializes the native A5 system but
opens no window and installs no audio/input driver. A 60-second subprocess
timeout catches sequencer hangs. Also test the integrated player's text,
cursor, sound and built-in ending behavior before publication.

## MIT license for new generator code and original procedural assets

Copyright (c) 2026 Korri plugin contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

These MIT terms do not replace the font's separate notices or the engine's
and dependencies' licenses. Keep all applicable notices with distribution.
