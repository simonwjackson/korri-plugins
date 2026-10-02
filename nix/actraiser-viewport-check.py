#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3 python3Packages.pillow xdotool
"""Private, external Auto viewport acceptance through korrid plugin-launch.

The caller owns DISPLAY/Xvfb and the Mesa/Vulkan environment. No display is
created, mapped, focused, or closed here. --artifacts must name a NEW private
directory; captures contain owned game content and must not enter public caches.

Required native diagnostic, at EVERY scheduled final-composite capture:
  [viewport-check] gf=1400 aspect=Auto par=square scene=Action2D map=04/04
    drawable=800x800 budget=0/0/16/16 live=0/0/16/16
    source=0/0/256/256 native=0/16/256/224 dest=0/0/800/800
(on ONE line). par is square or crt; scene is Action2D or Action3D.
Margins are left/right/top/bottom. source/native describe the logical canvas
and authentic 256x224 band, not a valid texture ROI or projected 3D rectangle.
Require source_kind=logical-canvas, mapping=flat/perspective,
comparison=enhanced and visible=1. dest is the actual PresentFrame return
value from this screenshot draw. drawable is actual RGB readback size.
budget excludes Diorama allocation overscan; live is captured geometric
availability, not proof of nonempty world pixels. capture/capture_native and
render_live describe the valid PPU capture and its authentic origin. Blank
boundary padding must not enlarge valid content. Diorama needs independent
perspective evidence; applying the flat pixel-band transform is not valid.

Every selected action capture also needs the same-slot HUD layout:
  [viewport-hud] gf=N count=C coords=xywh precision=chunk-layout-pre-crt ...
  [viewport-hud] gf=N index=I rect=X/Y/W/H   (exactly C lines)
HUD rectangles are excluded before counting extra-band content, so the
relocated HUD cannot pass as expanded scenery.

Diorama captures need the actual projected mesh bounds:
  [viewport-projection] gf=N map=GG/MM plane=P band=B stage=scene-pre-post
    coords=xyxy precision=uv-clipped-triangle-aabb composite_ok=1
    evidence_ok=1 projection_valid=1 ... ok=O source_ok=S bounds=X0/Y0/X1/Y1
    output_viewport=X/Y/W/H heat=0
for planes bg1/bg1-high/bg2/bg2-high and bands native/left/right/top/bottom.
The UNION of native bounds is excluded; extension bounds are search areas, not
proof. Bounds precede post-processing, so the isolated account disables CRT,
action FX, Diorama blur/rim/edge AA/shadow, skybox, shoebox, backdrop, and
sprites. These settings exist only in temporary test accounts.

One earlier classic capture checks that Auto leaves non-action framing native.
Missing evidence fails closed.
"""

import argparse
import base64
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import time

from PIL import Image, ImageDraw

ROM_HASH = "b8055844825653210d252d29a2229f9a3e7e512004e83940620173c57d8723f0"
CASES = {f"{mode}-{par}": (mode, par)
         for mode in ("flat", "diorama") for par in ("square", "crt")}
# Resize AFTER the preceding capture. The pinned natural route stays in a
# classic non-action screen (map 00/09) until gf=1323, then plays Aitos 04/04
# and enters the smaller 04/05 room at gf=2573. The 3000-tick replay budget
# did not reach gf=2800 in the real Vulkan pilot, so every selected frame is
# at or below gf=2600. 1240x1080 recurs to test a return to an earlier size;
# gf=2600 at 320x1200 is the measured room-boundary clipping case.
CLASSIC_FRAME = 1200
SCHEDULE = [(CLASSIC_FRAME, (1240, 1080)), (1400, (800, 800)),
            (1600, (1240, 1080)), (1800, (1600, 900)),
            (2000, (320, 1200)), (2200, (2400, 400)),
            (2400, (1240, 1080)), (2500, (1240, 1080)),
            (2600, (320, 1200))]
PLANES = ("bg1", "bg1-high", "bg2", "bg2-high")
BANDS = ("left", "right", "top", "bottom")
# Existing native setting names (src/app/settings.c descriptors). Isolation
# keeps post effects, host FX and non-world planes out of the pixel proof.
ISOLATION = {
    "crt_enabled": "Off", "action_effect_lighting": "Off",
    "action_effect_particles": "Off", "action_environmental_effects": "Off",
    "gpu_fx_dof": "Off", "gpu_fx_rim": "Off", "gpu_fx_edgeaa": "Off",
    "gpu_fx_shadow": "Off", "gpu_interp_enabled": "Off",
    "diorama_skybox": "Off", "diorama_shoebox": "Off",
    "diorama_layer_backdrop": "Off", "diorama_layer_obj": "Off",
    "diorama_hud_flat": "On",
}
FAILURES = re.compile(
    r"\bVK_ERROR_[A-Z_]+\b|\bFATAL\b|\[session-fatal\]|"
    r"capture=(?:failed|native-framebuffer)|Wayland display connection closed|"
    r"SDL_Init failed|SDL_CreateWindow failed|graphics.*failed|"
    r"Graphics startup preparation failed|frame present failed|"
    r"settings.*(?:write failed|flush failed)|\[input-replay\].*(?:failed|error)",
    re.I,
)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def check_log(text):
    failure = FAILURES.search(text)
    require(failure is None, f"Native failure: {failure[0] if failure else ''}")


def wait_for(test, process, log_path, description, deadline):
    while time.monotonic() < deadline:
        text = log_path.read_text(errors="replace")
        check_log(text)
        result = test(text)
        if result:
            return result
        require(process.poll() is None,
                f"Exited before {description}; see {log_path}")
        time.sleep(0.05)
    raise RuntimeError(f"Timed out waiting for {description}; see {log_path}")


def terminate(process):
    # The launcher and its native children are in our new session/group only.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=5)
    # A launcher can exit before a native child. Do not leave descendants in
    # our owned group alive just because the group leader has already exited.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def xdotool(*arguments, optional=False):
    result = subprocess.run(["xdotool", *map(str, arguments)],
                            capture_output=True, text=True, timeout=5)
    if not optional:
        require(result.returncode == 0, f"xdotool {arguments}: {result.stderr}")
    return result.stdout if result.returncode == 0 else ""


def process_identity(pid, group):
    """Linux start time prevents acting on a PID reused during readiness."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        if int(stat[2]) != group:  # field 5: process group
            return None
        executable = Path(f"/proc/{pid}/exe").resolve(strict=True)
        if executable.name != "ActRaiserRecomp":
            return None
        return stat[19]  # field 22: starttime
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return None


def owned_window(process):
    matches = []
    for directory in Path("/proc").iterdir():
        if not directory.name.isdigit():
            continue
        pid = int(directory.name)
        identity = process_identity(pid, process.pid)
        if identity is None:
            continue
        # Hidden SDL headless-video windows are intentionally included. Never
        # fall back to a title search, a global visible search, or another PID.
        for window in xdotool("search", "--pid", pid, optional=True).splitlines():
            owner = xdotool("getwindowpid", window, optional=True).strip()
            if owner == str(pid):
                matches.append((pid, identity, window))
    require(len(matches) <= 1, f"Ambiguous native windows in own group: {matches}")
    return matches[0] if matches else None


def verify_owner(process, window):
    pid, identity, window_id = window
    require(process_identity(pid, process.pid) == identity,
            "Own native child exited or PID was reused")
    require(xdotool("getwindowpid", window_id).strip() == str(pid),
            "Native window ownership changed")


def window_size(process, window):
    verify_owner(process, window)
    geometry = xdotool("getwindowgeometry", "--shell", window[2])
    values = dict(line.split("=", 1) for line in geometry.splitlines() if "=" in line)
    return int(values["WIDTH"]), int(values["HEIGHT"])


def resize(process, window, size, log_path, deadline):
    verify_owner(process, window)
    # No --sync: xdotool can wait forever if the window ignores ConfigureNotify.
    xdotool("windowsize", window[2], *size)
    wait_for(lambda _: window_size(process, window) == size, process, log_path,
             f"own drawable resize to {size}", min(deadline, time.monotonic() + 10))


def setting_applied(text, key, value):
    return re.search(rf"\[settings\] gf=\d+ {re.escape(key)}={re.escape(value)}"
                     r" -> (?:applied|unchanged)(?:\s|$)", text) is not None


def saved_setting(path, key, value):
    require(path.is_file(), f"Native settings not saved: {path}")
    require(re.search(rf"^{re.escape(key)}\s*=\s*{re.escape(value)}\s*$",
                      path.read_text(), re.M), f"Missing persisted {key}={value}")


def shot_records(text):
    return {int(frame): (name, int(width), int(height))
            for name, frame, width, height in re.findall(
                r"\[shot\] (.+) at gf=(\d+) \((\d+)x(\d+)\) "
                r"[^\n]*capture=final-composite", text)}


def tuple_value(values, key, count, separator="/"):
    require(key in values, f"Missing native viewport field {key}")
    result = tuple(map(float, values[key].split(separator)))
    require(len(result) == count and all(math.isfinite(n) for n in result),
            f"Invalid viewport field {key}={values[key]}")
    return result


def viewport_evidence(text, frame, size, mode, par):
    lines = [line for line in text.splitlines() if line.startswith("[viewport-check] ")]
    records = [dict(re.findall(r"(\w+)=([^\s]+)", line)) for line in lines]
    records = [record for record in records if record.get("gf") == str(frame)]
    require(len(records) == 1,
            f"Need one native [viewport-check] at gf={frame}; found {len(records)}. "
            "Coordinate the diagnostic contract in this script's docstring.")
    record = records[0]
    require(record.get("source_kind") == "logical-canvas"
            and record.get("mapping") == ("flat" if mode == "flat" else "perspective")
            and record.get("comparison") == "enhanced" and record.get("visible") == "1",
            f"Wrong capture mapping/comparison/visibility: {record}")
    cx, cy, cw, ch = tuple_value(record, "capture", 4)
    cnx, cny, cnw, cnh = tuple_value(record, "capture_native", 4)
    require(cnw == 256 and cnh == 224 and cx <= cnx and cy <= cny
            and cnx + cnw <= cx + cw and cny + cnh <= cy + ch,
            f"Actual capture crops the authentic band: {record}")
    require(record.get("aspect") == "Auto" and record.get("par") == par,
            f"Persisted Auto/PAR not loaded at gf={frame}: {record}")
    require(record.get("scene") == ("Action2D" if mode == "flat" else "Action3D")
            # The pinned natural route entered 04/05 at gf=2573 in the
            # real Vulkan pilot. Its small room supplies the boundary case.
            and record.get("map") in {"04/04", "04/05"},
            f"Wrong action scene: {record}")
    require(tuple_value(record, "drawable", 2, "x") == size,
            f"Native drawable differs from requested X11 size: {record}")
    budget = tuple_value(record, "budget", 4)
    live = tuple_value(record, "live", 4)
    for index, (requested, actual) in enumerate(zip(budget, live)):
        cap = 120 if index < 2 else 64
        require(requested.is_integer() and actual.is_integer()
                and 0 <= actual <= requested <= cap, f"Unsafe action margins: {record}")
    # Independent worked acceptance examples, not a copy of the native resolver.
    expected = {
        "square": {(800, 800): (0, 16), (1240, 1080): (1, 0),
                   (1600, 900): (71, 0), (320, 1200): (0, 64),
                   (2400, 400): (120, 0)},
        "crt": {(800, 800): (0, 37), (1240, 1080): (0, 18),
                (1600, 900): (43, 0), (320, 1200): (0, 64),
                (2400, 400): (120, 0)},
    }[par][size]
    require(all(abs(observed - wanted) <= 1 for observed, wanted in
                zip(budget, (expected[0], expected[0], expected[1], expected[1]))),
            f"Wrong drawable expansion budget: {record}; expected near {expected}")
    sx, sy, sw, sh = tuple_value(record, "source", 4)
    nx, ny, nw, nh = tuple_value(record, "native", 4)
    dx, dy, dw, dh = tuple_value(record, "dest", 4)
    require(nw == 256 and nh == 224 and sw >= nw and sh >= nh,
            f"Authentic native extent changed: {record}")
    require(sx <= nx and sy <= ny and nx + nw <= sx + sw and ny + nh <= sy + sh,
            f"Boundary crops authentic native view: {record}")
    require(nx - live[0] >= sx - 1 and nx + nw + live[1] <= sx + sw + 1
            and ny - live[2] >= sy - 1 and ny + nh + live[3] <= sy + sh + 1,
            f"Presented source crops declared live scene content: {record}")
    require(256 + live[0] + live[1] - 1 <= sw <= 256 + budget[0] + budget[1] + 1
            and 224 + live[2] + live[3] - 1 <= sh <= 224 + budget[2] + budget[3] + 1,
            f"Presented source exceeds budget or crops room-bounded expansion: {record}")
    require(0 <= dx and 0 <= dy and dw > 0 and dh > 0
            and dx + dw <= size[0] + 1 and dy + dh <= size[1] + 1,
            f"Destination outside drawable: {record}")
    pixel_ratio = 7 / 6 if par == "crt" else 1
    require(abs(dw / (sw * pixel_ratio) - dh / sh) <= max(2 / sw, 2 / sh),
            f"Native view stretched at room boundary: {record}")
    return record


def classic_evidence(text, frame, size, par):
    """Auto must keep the classic (non-action) frame at its native canvas."""
    records = [dict(re.findall(r"(\w+)=([^\s]+)", line)) for line in text.splitlines()
               if line.startswith("[viewport-check] ")]
    records = [record for record in records if record.get("gf") == str(frame)]
    require(len(records) == 1, f"Need one classic [viewport-check] at gf={frame}")
    record = records[0]
    require(record.get("aspect") == "Auto" and record.get("par") == par
            and record.get("comparison") == "enhanced" and record.get("visible") == "1"
            and record.get("mapping") == "flat"
            and record.get("scene") not in {"Action2D", "Action3D"}
            and not record.get("map", "").startswith("04/"),
            f"Classic capture is not a non-action Auto frame: {record}")
    require(tuple_value(record, "drawable", 2, "x") == size
            and tuple_value(record, "budget", 4) == (0, 0, 0, 0)
            and tuple_value(record, "source", 4) == (0, 0, 256, 224)
            and tuple_value(record, "native", 4) == (0, 0, 256, 224),
            f"Auto changed classic framing: {record}")
    dx, dy, dw, dh = tuple_value(record, "dest", 4)
    pixel_ratio = 7 / 6 if par == "crt" else 1
    require(dw > 0 and dh > 0
            and abs(dw / (256 * pixel_ratio) - dh / 224) <= 2 / 224,
            f"Classic native frame stretched: {record}")
    return record


def rectangle(value, kind):
    x0, y0, a, b = map(int, value.split("/"))
    return (x0, y0, x0 + a, y0 + b) if kind == "xywh" else (x0, y0, a, b)


def grow(box, pixels):
    return (box[0] - pixels, box[1] - pixels, box[2] + pixels, box[3] + pixels)


def hud_exclusions(text, frame, dest):
    """Actual same-slot HUD chunk destinations from the native producer."""
    headers, rectangles = [], {}
    for line in text.splitlines():
        if not line.startswith("[viewport-hud] "):
            continue
        fields = dict(re.findall(r"(\w+)=([^\s]+)", line))
        if fields.get("gf") != str(frame):
            continue
        if "count" in fields:
            headers.append(fields)
        else:
            index = int(fields["index"])
            require(index not in rectangles, f"Duplicate HUD chunk at gf={frame}")
            rectangles[index] = rectangle(fields["rect"], "xywh")
    require(len(headers) == 1 and headers[0].get("coords") == "xywh"
            and headers[0].get("precision") == "chunk-layout-pre-crt"
            and headers[0].get("viewport") == dest,
            f"Need one native [viewport-hud] header for viewport {dest} at gf={frame}")
    require(sorted(rectangles) == list(range(int(headers[0]["count"]))),
            f"Incomplete HUD chunk list at gf={frame}")
    return [rectangles[index] for index in sorted(rectangles)]


def projection_evidence(text, frame, record):
    """Actual projected Diorama mesh bounds from the screenshot draw."""
    entries = {}
    for line in text.splitlines():
        if not line.startswith("[viewport-projection] "):
            continue
        fields = dict(re.findall(r"(\w+)=([^\s]+)", line))
        if fields.get("gf") != str(frame):
            continue
        key = (fields.get("plane"), fields.get("band"))
        require(key not in entries, f"Duplicate projection record {key} at gf={frame}")
        entries[key] = fields
    require(set(entries) == {(plane, band) for plane in PLANES
                             for band in ("native", *BANDS)},
            f"Incomplete [viewport-projection] set at gf={frame}: {sorted(entries)}")
    for fields in entries.values():
        require(fields.get("stage") == "scene-pre-post" and fields.get("coords") == "xyxy"
                and fields.get("precision") == "uv-clipped-triangle-aabb"
                and fields.get("composite_ok") == "1" and fields.get("evidence_ok") == "1"
                and fields.get("projection_valid") == "1" and fields.get("heat") == "0"
                and fields.get("map") == record["map"]
                and fields.get("output_viewport") == record["dest"],
                f"Projection evidence is not the successful screenshot draw: {fields}")
    natives = []
    for plane in PLANES:
        native = entries[(plane, "native")]
        if native.get("mesh") == "1" or native.get("skybox") == "1":
            require(native.get("ok") == "1",
                    f"Drawn {plane} lacks native projection evidence: {native}")
        if native.get("ok") == "1":
            natives.append(rectangle(native["bounds"], "xyxy"))
    require(natives, f"No projected native world plane at gf={frame}")
    extensions = [[rectangle(entries[(plane, band)]["bounds"], "xyxy")
                   for plane in PLANES
                   if entries[(plane, band)].get("ok") == "1"
                   and entries[(plane, band)].get("source_ok") == "1"]
                  for band in BANDS]
    return natives, extensions


DEPTH_COPIES = re.compile(r"\b(?:stack|thick|voxel|copies):|^\s*bg[12]-virtual\b", re.M)


def assert_single_depth_planes(path, rooms=("04:04", "04:05")):
    """Projection bounds exclude authored depth copies, skirts and virtual
    planes. Prove the account's native layer manifest adds none in the
    measured rooms, so native rows cannot pass as expanded content."""
    require(path.is_file(), f"Missing native Diorama layer manifest: {path}")
    section = None
    for line in path.read_text().splitlines():
        header = re.match(r"\s*\[layers:([0-9A-Fa-f]{2}:[0-9A-Fa-f]{2})(?::[^\]]*)?\]", line)
        if header:
            section = header[1].upper()
            continue
        if section in rooms and not line.lstrip().startswith("#"):
            require(DEPTH_COPIES.search(line) is None,
                    f"Depth copies in [layers:{section}] break projection proof: {line}")


def band_census(image, box, exclusions):
    """Return (pixels, colours, black) outside every exclusion."""
    x0, y0 = max(0, box[0]), max(0, box[1])
    x1, y1 = min(image.width, box[2]), min(image.height, box[3])
    if x1 - x0 < 1 or y1 - y0 < 1:
        return 0, 0, 0
    # Paint exclusions with one sentinel colour and drop it from the census.
    # A genuine pixel of that exact colour is also dropped: conservative.
    sentinel = (1, 2, 3)
    crop = image.crop((x0, y0, x1, y1))
    draw = ImageDraw.Draw(crop)
    for ex0, ey0, ex1, ey1 in exclusions:
        ex0, ey0 = max(ex0, x0) - x0, max(ey0, y0) - y0
        ex1, ey1 = min(ex1, x1) - x0, min(ey1, y1) - y0
        if ex1 > ex0 and ey1 > ey0:
            draw.rectangle((ex0, ey0, ex1 - 1, ey1 - 1), fill=sentinel)
    colors = [(count, color) for count, color in
              crop.getcolors(crop.width * crop.height) if color != sentinel]
    black = sum(count for count, color in colors if color == (0, 0, 0))
    return sum(count for count, _ in colors), len(colors), black


def band_has_content(image, box, exclusions):
    """More than 8 colours in at least 256 pixels outside every exclusion."""
    pixels, colours, _ = band_census(image, box, exclusions)
    return pixels >= 256 and colours > 8


def band_rendered(image, box, exclusions):
    """Flat Auto clears unavailable rows to black. At least 90% non-black
    pixels in a live band shows PPU-rendered rows (tiles or backdrop), not
    padding. Weaker than band_has_content: a uniform backdrop row passes."""
    pixels, _, black = band_census(image, box, exclusions)
    return pixels >= 256 and black * 10 <= pixels


def capture_evidence(path, record, size, hud, projection):
    parts = path.read_bytes().split(b"\n", 3)
    require(len(parts) == 4 and parts[0] == b"P6" and parts[2] == b"255",
            f"Invalid native PPM: {path}")
    width, height = map(int, parts[1].split())
    require((width, height) == size and len(parts[3]) == width * height * 3,
            f"Incomplete final-composite capture: {path}")
    image = Image.frombytes("RGB", size, parts[3])
    require(len(image.resize((128, 128)).getcolors(16384) or []) > 16,
            f"Blank/degenerate game composite: {path}")
    hud_boxes = [grow(box, 2) for box in hud]
    if record.get("mapping") == "flat":
        sx, sy, sw, sh = tuple_value(record, "source", 4)
        nx, ny, nw, nh = tuple_value(record, "native", 4)
        dx, dy, dw, dh = tuple_value(record, "dest", 4)
        left, right, top, bottom = tuple_value(record, "live", 4)

        def physical(x0, y0, x1, y1):
            return (math.ceil(dx + (x0 - sx) * dw / sw), math.ceil(dy + (y0 - sy) * dh / sh),
                    math.floor(dx + (x1 - sx) * dw / sw), math.floor(dy + (y1 - sy) * dh / sh))
        # Only live captured margins, never blank boundary padding.
        candidates = [[physical(max(sx, nx - left), ny, nx, ny + nh)],
                      [physical(nx + nw, ny, min(sx + sw, nx + nw + right), ny + nh)],
                      [physical(nx, max(sy, ny - top), nx + nw, ny)],
                      [physical(nx, ny + nh, nx + nw, min(sy + sh, ny + nh + bottom))]]
        natives = [physical(nx, ny, nx + nw, ny + nh)]
        native_guard = 3
    else:
        require(projection is not None, "Perspective capture needs projected mesh bounds")
        natives, candidates = projection
        native_guard = 4
    exclusions = [grow(box, native_guard) for box in natives] + hud_boxes
    visible_bands = [index for index, boxes in enumerate(candidates)
                     if any(band_has_content(image, box, exclusions) for box in boxes)]
    rendered_bands = ([index for index, boxes in enumerate(candidates)
                       if any(band_rendered(image, box, exclusions) for box in boxes)]
                      if record.get("mapping") == "flat" else None)
    return {"sha256": digest(path), "size": size, "content_bands": visible_bands,
            "rendered_bands": rendered_bands, "hud_chunks": len(hud),
            "native_exclusions": natives}


def completed(text, frames):
    check_log(text)
    cadence = re.findall(r"\[present-cadence\] tick-presents=(\d+) re-presents=(\d+)", text)
    require(cadence, "Missing GPU presentation completion evidence")
    ticks, represents = map(int, cadence[-1])
    # The native settings action exits by WRAM game-frame, which is not the
    # SNES tick counter. The setup's AR_QUIT_FRAMES=180 is an upper bound.
    # The replay still requires its complete 3000-tick presentation budget.
    require(represents == 0 and (ticks == frames if frames else 0 < ticks <= 180),
            f"Incomplete GPU schedule; expected {frames or '1..180'} ticks, no re-presents")
    require("[graphics-prepare] completed" in text
            and "[lifecycle] game session ready" in text and "Loaded ROM:" in text
            and "[runner-trace]" in text, "Incomplete packaged native readiness evidence")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("plugin", type=Path)
    parser.add_argument("korrid", type=Path)
    parser.add_argument("source", type=Path, help="Pinned upstream source with fixtures/tools")
    parser.add_argument("rom", type=Path)
    parser.add_argument("--artifacts", type=Path, help="NEW private evidence directory")
    parser.add_argument("--case", choices=CASES, action="append", help="Repeat to select cases")
    args = parser.parse_args()
    plugin, korrid, source, rom = (path.resolve(strict=True) for path in
                                  (args.plugin, args.korrid, args.source, args.rom))
    require(os.environ.get("DISPLAY"), "Caller must provide its own X11 DISPLAY")
    require(shutil.which("xdotool"), "xdotool must be on PATH")
    original_hash = digest(rom)
    require(original_hash == ROM_HASH and rom.stat().st_size == 1048576,
            "Unsupported owned USA ROM")
    fixture_root = source / "tests/fixtures/benchmark"
    fixtures = [fixture_root / name for name in
                ("aitos-r4-natural-inputs.json", "action-routes-seed.srm.b64",
                 "action-render-checkpoints.json", "action-render-settings.ini")]
    helper = source / "tools/compare_pipeline_performance.py"
    input_hashes = {str(path): digest(path) for path in [rom, helper, *fixtures]}
    checkpoints = json.loads(fixtures[2].read_text())["checkpoints"]
    seed = base64.b64decode(b"".join(fixtures[1].read_bytes().split()), validate=True)
    require(len(seed) == 8192 and all(hashlib.sha256(seed).hexdigest() ==
            checkpoints[key]["sram_sha256"] for key in ("aitos-flat", "aitos-diorama")),
            "Declared action fixture SRAM length/hash mismatch")
    spec = importlib.util.spec_from_file_location("upstream_pipeline", helper)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    replay = module.replay_bytes(fixtures[0])
    require(len(replay) == (json.loads(fixtures[0].read_text())["frames"] + 1) * 8,
            "Incomplete supported replay payload")
    manifest = json.loads((plugin / "manifest.json").read_text())
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith(("AR_", "SNESRECOMP_", "SNESREF_"))}
    environment.update(SDL_VIDEODRIVER="x11", SDL_AUDIODRIVER="dummy", AR_HEADLESS="1",
                       AR_HEADLESS_VIDEO="1", AR_WS_HEADLESS="1", AR_PACE="1",
                       AR_NO_RUN_DIR="1", AR_WINDOW_MODE="Windowed",
                       AR_PERFORMANCE_OVERLAY="Off", AR_REFRESH_MODE="Unlimited")
    selected = list(dict.fromkeys(args.case or CASES))
    with tempfile.TemporaryDirectory(prefix="actraiser-auto-private-") as temporary:
        work = Path(temporary)
        work.chmod(0o700)
        evidence = args.artifacts.resolve() if args.artifacts else work / "evidence"
        evidence.mkdir(mode=0o700, parents=True, exist_ok=False)
        print(f"Private evidence: {evidence}", flush=True)
        owned = work / "Owned '; $(touch injected) %.sfc"
        shutil.copyfile(rom, owned)
        owned.chmod(0o400)
        report = {"status": "running", "inputs": input_hashes, "cases": {}}
        try:
            for name in selected:
                mode, par = CASES[name]
                case_dir = evidence / name
                case_dir.mkdir(mode=0o700)
                account = work / name / "Player '; $(touch injected) %s"
                data = account / "ActRaiserRecomp/game"
                saves = data / "saves"
                saves.mkdir(parents=True, mode=0o700)
                settings = data / "settings.ini"
                lines = [line for line in fixtures[3].read_text().splitlines()
                         if line.split("=", 1)[0].strip() not in ISOLATION]
                lines += [f"{key} = {value}" for key, value in ISOLATION.items()]
                settings.write_text("\n".join(lines) + "\n")
                request = {"runnerId": "@simonwjackson:actraiser/actraiser",
                           "program": manifest["files"]["actraiser"],
                           "contentPath": str(owned), "accountRoot": str(account),
                           "files": manifest["files"]}
                command = [str(korrid), "plugin-launch", str(plugin / "plugin.ts"),
                           json.dumps(request)]
                par_text = "Square pixels" if par == "square" else "4:3 CRT"
                # Replay deliberately disables settings persistence. Use a real
                # non-replay native session for events and durable Auto saving.
                setup_env = environment | {
                    "AR_QUIT_FRAMES": "180", "AR_EXTENDED_ASPECT_RATIO": "16:10",
                    "AR_ASPECT_PAR": par_text,
                    "AR_SETTING_SET": "extended_aspect=Auto", "AR_SETTING_AT_GF": "120",
                    "AR_SETTING_SET_2": "exit_desktop=run", "AR_SETTING_AT_GF_2": "121"}
                setup_log = case_dir / "settings.log"
                with setup_log.open("w") as log:
                    process = subprocess.Popen(command, cwd=work, env=setup_env,
                                               stdout=log, stderr=subprocess.STDOUT,
                                               start_new_session=True)
                    try:
                        require(process.wait(timeout=60) == 0, f"Native settings failed: {setup_log}")
                    finally:
                        terminate(process)
                setup_text = setup_log.read_text(errors="replace")
                completed(setup_text, None)
                require(setting_applied(setup_text, "extended_aspect", "Auto")
                        and "exit_desktop=run -> applied action" in setup_text,
                        "Native Auto setting / durable native exit action not accepted")
                saved_setting(settings, "extended_aspect", "Auto")
                saved_setting(settings, "pixel_aspect", par_text)
                for key, value in ISOLATION.items():
                    saved_setting(settings, key, value)
                saved_hash = digest(settings)
                shutil.copyfile(settings, case_dir / "settings.ini")
                (saves / "save.srm").write_bytes(seed)
                seed_path = work / name / "seed.srm"
                seed_path.write_bytes(seed)
                replay_path = work / name / "input.rec"
                replay_path.write_bytes(replay)
                run_env = environment | checkpoints[f"aitos-{mode}"]["env"]
                # Auto/PAR MUST load from native persisted settings, not env.
                for key in ("AR_EXTENDED_ASPECT_RATIO", "AR_ASPECT_PAR", "AR_DIORAMA_AT"):
                    run_env.pop(key, None)
                run_env.update(AR_QUIT_FRAMES="3000", AR_INPUT_REPLAY=str(replay_path),
                               AR_REPLAY_NOSTOP="1", AR_SAVE_NATIVE_PATH=str(seed_path),
                               AR_SHOT_REQUIRE_COMPOSITE="1",
                               AR_SHOT_FROM=str(CLASSIC_FRAME),
                               AR_SHOT_TO=str(SCHEDULE[-1][0]), AR_SHOT_EVERY="100")
                if mode == "diorama":
                    run_env.update(AR_SETTING_SET="diorama_mode=On", AR_SETTING_AT_GF="1330")
                log_path = case_dir / "native.log"
                captures, pending = {}, []
                report["cases"][name] = captures
                with log_path.open("w") as log:
                    process = subprocess.Popen(command, cwd=work, env=run_env,
                                               stdout=log, stderr=subprocess.STDOUT,
                                               start_new_session=True)
                    try:
                        # Bound, not expected duration: aarch64 llvmpipe Diorama on
                        # a shared builder needed more than 150 s for 3000 frames.
                        deadline = time.monotonic() + 600
                        wait_for(lambda text: "[lifecycle] game session ready" in text,
                                 process, log_path, "native GPU readiness", deadline)
                        window = wait_for(lambda _: owned_window(process), process,
                                          log_path, "exact own native X11 window", deadline)
                        pid, identity, window_id = window
                        (case_dir / "window.json").write_text(json.dumps(
                            {"pid": pid, "starttime": identity, "window": window_id}))
                        for frame, size in SCHEDULE:
                            if window_size(process, window) != size:
                                resize(process, window, size, log_path, deadline)
                            # Check for native resize feedback while waiting. The
                            # capture's own drawable field is checked later.
                            def captured(text):
                                shot = shot_records(text).get(frame)
                                if shot is None:
                                    require(window_size(process, window) == size,
                                            f"Native resize feedback at gf={frame}; expected {size}")
                                return shot
                            shot = wait_for(captured, process, log_path,
                                            f"GPU final-composite gf={frame}", deadline)
                            text = log_path.read_text(errors="replace")
                            shot_path = (data / shot[0]).resolve(strict=True)
                            require(shot_path.is_relative_to(saves.resolve()),
                                    "Native shot escaped isolated account saves")
                            shutil.copyfile(shot_path, case_dir / f"shot_{frame}.ppm")
                            require(shot[1:] == size, "Capture log size differs from drawable")
                            # Geometry is checked now; pixels after the run, so
                            # analysis time cannot delay the next resize.
                            if frame == CLASSIC_FRAME:
                                record = classic_evidence(text, frame, size, par)
                                report["cases"][name + "-classic"] = {
                                    "sha256": digest(shot_path), "geometry": record}
                            else:
                                pending.append((frame, size, viewport_evidence(
                                    text, frame, size, mode, par)))
                        def finished(_):
                            if process.poll() is not None:
                                require(process.returncode == 0, f"Native run failed: {log_path}")
                                return True
                            # The native child can exit and destroy its window
                            # before the launcher (group leader) exits.
                            try:
                                current = window_size(process, window)
                            except RuntimeError:
                                if process_identity(pid, process.pid) != identity:
                                    return False
                                raise
                            require(current == SCHEDULE[-1][1],
                                    "Native resize feedback after final capture")
                            return False
                        wait_for(finished, process, log_path, "bounded native completion", deadline)
                    finally:
                        terminate(process)
                text = log_path.read_text(errors="replace")
                completed(text, 3000)
                for frame, size, record in pending:
                    projection = (projection_evidence(text, frame, record)
                                  if mode == "diorama" else None)
                    captures[str(frame)] = capture_evidence(
                        case_dir / f"shot_{frame}.ppm", record, size,
                        hud_exclusions(text, frame, record["dest"]), projection)
                    captures[str(frame)]["geometry"] = record
                (evidence / "results.json").write_text(json.dumps(report, indent=2) + "\n")
                # Periodic captures between selected frames are not evidence.
                require({frame for frame, _ in SCHEDULE} <= set(shot_records(text)),
                        "Missing selected scheduled composite frames")
                if mode == "diorama":
                    require(setting_applied(text, "diorama_mode", "On"),
                            "Native Diorama event was not accepted")
                    assert_single_depth_planes(data / "diorama-layers.ini")
                    shutil.copyfile(data / "diorama-layers.ini", case_dir / "diorama-layers.ini")
                require(digest(settings) == saved_hash and seed_path.read_bytes() == seed
                        and (saves / "save.srm").read_bytes() == seed,
                        "Replay changed protected native settings or fixture SRAM")
                require(any(any(actual < requested for actual, requested in zip(
                            tuple_value(capture["geometry"], "live", 4),
                            tuple_value(capture["geometry"], "budget", 4)))
                            for capture in captures.values()),
                        "No captured room-boundary clipping; boundary preservation is unverified")
                require(any(any(band in (2, 3) for band in capture["content_bands"])
                            for capture in captures.values()),
                        "No captured content above/below authentic native view")
                require(any(any(band in (0, 1) for band in capture["content_bands"])
                            for capture in captures.values()),
                        "No captured content left/right of authentic native view")
                if mode == "flat" and par == "crt":
                    # Mini V2 shape: the top rows sit under the relocated HUD,
                    # so require PPU-rendered (not cleared) rows below.
                    mini = [capture for capture in captures.values()
                            if tuple(capture["size"]) == (1240, 1080)]
                    require(mini and all(3 in capture["rendered_bands"] for capture in mini),
                            "Mini V2-shaped CRT capture lacks rendered rows below native view")
                report["cases"][name] = captures
                (evidence / "results.json").write_text(json.dumps(report, indent=2) + "\n")
                print(f"PASS {name}: native Auto reload, {len(SCHEDULE)} Vulkan composites, own-window resize", flush=True)
            require(not (work / "injected").exists(), "Unsafe path expansion")
            report["status"] = "passed"
        except BaseException as error:
            report["status"] = "failed"
            report["error"] = f"{type(error).__name__}: {error}"
            raise
        finally:
            unchanged = all(digest(Path(path)) == expected for path, expected in input_hashes.items())
            report["inputs_unchanged"] = unchanged and digest(owned) == original_hash
            if not report["inputs_unchanged"]:
                report["status"] = "failed"
            (evidence / "results.json").write_text(json.dumps(report, indent=2) + "\n")
            require(report["inputs_unchanged"], "Owned source ROM or pinned fixture/helper changed")
        print("PASS: owned ROM and declared fixtures unchanged; selected cases only", flush=True)
        if not args.artifacts:
            print("Temporary private captures will be removed; use --artifacts to retain evidence.")


if __name__ == "__main__":
    main()
