#!/usr/bin/env nix-shell
#!nix-shell -i python3 -p python3 python3Packages.pillow xdotool
"""Private, external Auto viewport acceptance through korrid plugin-launch.

The caller owns DISPLAY/Xvfb and the Mesa/Vulkan environment. No display is
created, mapped, focused, or closed here. --artifacts must name a NEW private
directory; captures contain owned game content and must not enter public caches.

Evidence comes only from upstream's own logs and the screenshot pixels:
  [video-geometry] Auto 4:3-PAR -> 0 extra columns/side
    (render width 256, requested canvas 256x260)
  [shot] <path> at gf=N (WxH) margins=L/R mode=M capture=final-composite
  [shot-state] gf=N room=GGMM ...
The last geometry line before a capture is its active canvas; upstream logs
only changed geometry. The canvas must match independent worked examples for
the drawable size. Readback size must equal the X11 drawable, and the window
must keep the size this script set (no native resize feedback).

Pixel bands are the area outside the native 256x224 fit and inside the fitted
Auto canvas, which a 4:3 frame leaves black. Flat Auto keeps the native band
centred at the same scale, so a flat band is the expansion itself. Diorama is a
perspective view: a band there shows only that Auto fills the area 4:3 leaves
black, not where native content ends. The top band is not counted, because the
status HUD sits at the canvas top. Room-boundary clipping is not checked:
upstream does not log live vertical margins.

The isolated account disables CRT and post effects, so the fit geometry holds
in final pixels. These settings exist only in temporary test accounts.

One earlier classic capture checks that Auto keeps that non-action screen at
native height: rows outside its native fit stay black.
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

from PIL import Image

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
# Existing native setting names (src/app/settings.c descriptors). Isolation
# keeps CRT warps, post effects and host FX out of the pixel bands.
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


GEOMETRY = re.compile(
    r"\[video-geometry\] (\S+) (\S+) -> (\d+) extra columns/side "
    r"\(render width (\d+), requested canvas (\d+)x(\d+)\)")
SHOT_STATE = re.compile(r"\[shot-state\] gf=(\d+) room=([0-9a-f]{4}) ")
# Independent worked examples (extra columns, extra rows per side), not a copy
# of the native resolver. Measured unchanged from the original Auto patch.
EXPECTED = {
    "square": {(800, 800): (0, 16), (1240, 1080): (1, 0),
               (1600, 900): (71, 0), (320, 1200): (0, 64),
               (2400, 400): (120, 0)},
    "crt": {(800, 800): (0, 37), (1240, 1080): (0, 18),
            (1600, 900): (43, 0), (320, 1200): (0, 64),
            (2400, 400): (120, 0)},
}


def shot_offset(text, frame):
    match = re.search(rf"\[shot\] .+ at gf={frame} \(\d+x\d+\) [^\n]*"
                      r"capture=final-composite", text)
    require(match is not None, f"Missing final-composite [shot] at gf={frame}")
    return match.start()


def geometry_at(text, frame):
    """The last native geometry resolution logged before this capture.
    Upstream logs only changed geometry, so it is the active canvas."""
    end = shot_offset(text, frame)
    records = list(GEOMETRY.finditer(text, 0, end))
    require(records, f"No [video-geometry] before gf={frame}")
    aspect, par, _, _, width, height = records[-1].groups()
    return {"aspect": aspect, "par": par, "canvas": (int(width), int(height))}


def room_at(text, frame):
    rooms = [room for shot_frame, room in SHOT_STATE.findall(text)
             if int(shot_frame) == frame]
    require(len(rooms) == 1, f"Need one [shot-state] at gf={frame}; found {rooms}")
    return rooms[0]


def fit(size, content_width, content_height, par):
    """Centred aspect fit of a logical canvas with this pixel aspect ratio."""
    ratio = 7 / 6 if par == "crt" else 1
    scale = min(size[0] / (content_width * ratio), size[1] / content_height)
    width, height = content_width * ratio * scale, content_height * scale
    x0, y0 = (size[0] - width) / 2, (size[1] - height) / 2
    return (x0, y0, x0 + width, y0 + height)


def viewport_evidence(text, frame, size, mode, par):
    geometry = geometry_at(text, frame)
    require(geometry["aspect"] == "Auto"
            and geometry["par"] == ("4:3-PAR" if par == "crt" else "square-PAR"),
            f"Persisted Auto/PAR not active at gf={frame}: {geometry}")
    room = room_at(text, frame)
    # The pinned natural route entered 04/05 at gf=2573 in the real Vulkan
    # pilot. Its small room supplies the boundary case.
    require(room in {"0404", "0405"}, f"Wrong action room at gf={frame}: {room}")
    columns, rows = EXPECTED[par][size]
    width, height = geometry["canvas"]
    require(abs(width - (256 + 2 * columns)) <= 2 and abs(height - (224 + 2 * rows)) <= 2,
            f"Wrong drawable expansion at gf={frame}: {geometry}; "
            f"expected near {256 + 2 * columns}x{224 + 2 * rows}")
    return {"room": room, "mode": mode, **geometry}


def classic_evidence(text, frame, size, par):
    geometry = geometry_at(text, frame)
    require(geometry["aspect"] == "Auto", f"Auto not active at gf={frame}: {geometry}")
    room = room_at(text, frame)
    require(not room.startswith("04"), f"Classic capture is an action room: {room}")
    return {"room": room, **geometry}


def read_ppm(path, size):
    parts = path.read_bytes().split(b"\n", 3)
    require(len(parts) == 4 and parts[0] == b"P6" and parts[2] == b"255",
            f"Invalid native PPM: {path}")
    width, height = map(int, parts[1].split())
    require((width, height) == size and len(parts[3]) == width * height * 3,
            f"Incomplete final-composite capture: {path}")
    image = Image.frombytes("RGB", size, parts[3])
    require(len(image.resize((128, 128)).getcolors(16384) or []) > 16,
            f"Blank/degenerate game composite: {path}")
    return image


def band_census(image, box):
    """Return (pixels, colours, black) inside an integer box."""
    x0, y0 = max(0, math.ceil(box[0])), max(0, math.ceil(box[1]))
    x1, y1 = min(image.width, math.floor(box[2])), min(image.height, math.floor(box[3]))
    if x1 - x0 < 1 or y1 - y0 < 1:
        return 0, 0, 0
    colors = image.crop((x0, y0, x1, y1)).getcolors((x1 - x0) * (y1 - y0))
    black = sum(count for count, color in colors if max(color) <= 8)
    return sum(count for count, _ in colors), len(colors), black


def band_has_content(image, box):
    """More than 8 colours in at least 256 pixels."""
    pixels, colours, _ = band_census(image, box)
    return pixels >= 256 and colours > 8


def band_rendered(image, box):
    """At least 90% non-black pixels: rendered rows (tiles or backdrop), not
    cleared padding. Weaker than band_has_content."""
    pixels, _, black = band_census(image, box)
    return pixels >= 256 and black * 10 <= pixels


def classic_capture(path, record, size, par):
    """Auto keeps classic action-free framing at native height: the rows
    outside the native 256x224 fit stay black, so nothing was stretched."""
    image = read_ppm(path, size)
    native = fit(size, 256, 224, par)
    guard = 3
    bars = [(0, 0, size[0], native[1] - guard), (0, native[3] + guard, size[0], size[1])]
    census = [band_census(image, bar) for bar in bars]
    require(all(pixels == 0 or black * 100 >= pixels * 99
                for pixels, _, black in census),
            f"Classic capture draws outside its native-height fit: {census}")
    return {"sha256": digest(path), "size": size, "native_fit": native,
            "bars": census, **record}


def capture_evidence(path, record, size, par):
    """Bands are the area outside the native 256x224 fit and inside the fitted
    Auto canvas: exactly what a 4:3 frame leaves black. Flat Auto keeps the
    native band centred at the same scale, so a flat band is the expansion
    itself. Diorama is a perspective view; for it, a band shows only that Auto
    fills the area 4:3 leaves black, not where native content ends.
    The top band is not counted: the status HUD sits at the canvas top."""
    image = read_ppm(path, size)
    canvas = fit(size, *record["canvas"], par)
    native = fit(size, 256, 224, par)
    guard = 4
    hud_rows = (native[3] - native[1]) * 48 / 224
    bands = {
        "left": (canvas[0] + guard, native[1] + hud_rows, native[0] - guard, native[3] - guard),
        "right": (native[2] + guard, native[1] + hud_rows, canvas[2] - guard, native[3] - guard),
        "bottom": (native[0] + guard, native[3] + guard, native[2] - guard, canvas[3] - guard),
    }
    return {"sha256": digest(path), "size": size, "canvas_fit": canvas,
            "native_fit": native,
            "content_bands": [name for name, box in bands.items()
                              if band_has_content(image, box)],
            "rendered_bands": [name for name, box in bands.items()
                               if band_rendered(image, box)],
            **record}


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
                                classic = (frame, size, classic_evidence(
                                    text, frame, size, par))
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
                frame, size, record = classic
                report["cases"][name + "-classic"] = classic_capture(
                    case_dir / f"shot_{frame}.ppm", record, size, par)
                for frame, size, record in pending:
                    captures[str(frame)] = capture_evidence(
                        case_dir / f"shot_{frame}.ppm", record, size, par)
                (evidence / "results.json").write_text(json.dumps(report, indent=2) + "\n")
                # Periodic captures between selected frames are not evidence.
                require({frame for frame, _ in SCHEDULE} <= set(shot_records(text)),
                        "Missing selected scheduled composite frames")
                if mode == "diorama":
                    require(setting_applied(text, "diorama_mode", "On"),
                            "Native Diorama event was not accepted")
                require(digest(settings) == saved_hash and seed_path.read_bytes() == seed
                        and (saves / "save.srm").read_bytes() == seed,
                        "Replay changed protected native settings or fixture SRAM")
                require(any("bottom" in capture["content_bands"]
                            for capture in captures.values()),
                        "No captured content below the native 4:3 fit")
                require(any({"left", "right"} & set(capture["content_bands"])
                            for capture in captures.values()),
                        "No captured content beside the native 4:3 fit")
                if mode == "flat" and par == "crt":
                    # Mini V2 shape: the top rows sit under the relocated HUD,
                    # so require PPU-rendered (not cleared) rows below.
                    mini = [capture for capture in captures.values()
                            if tuple(capture["size"]) == (1240, 1080)]
                    require(mini and all("bottom" in capture["rendered_bands"]
                                         for capture in mini),
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
