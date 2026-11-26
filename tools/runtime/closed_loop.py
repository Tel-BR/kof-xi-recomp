#!/usr/bin/env python3
"""
Closed-loop keyboard probe for the GPU runner: title -> main menu -> navigation -> mode screen.

Every step waits for visual evidence in the runtime's frame captures before the next key
press, and keys are real WM_KEYDOWN/WM_KEYUP messages posted to the game window, so the
interactive keyboard path is the one under test. Milestones, in order:

    TITLE        the title logo matches a private reference capture and the Start prompt shows
    MENU         Start opened the main menu with ARCADE highlighted
    NAV          Down moved the highlight to TEAM and Up back to ARCADE
    MODE_VISIBLE Cross left the menu and the next screen (character select) renders lit and
                 colourful for several consecutive captures (issue #12; it used to stay black)
    FPS          the median internal rate after boot stays at or above --fps-floor
    AUDIO        with --audio, at least 85% of mixer seconds from the main menu onward have
                 RMS > 150, including 12 seconds of capture after mode entry

    python tools/runtime/closed_loop.py --title-reference private/scratch/diag/title_find/reference_title_at_dump.png

The verdict line is `GREEN title+menu+nav+mode_visible` or `RED <milestone> ...` (`RED MODE_BLACK`
when the screen after the menu never lights up, as before the fix); exit code 0
(green), 1 (red) or 2 (setup error). Captures, logs and the classified mode-screen frame stay in a
run directory under private/ (default private/scratch/diag/loop_*). Do not type into the game
window during a run: stray keys contaminate it. Windows only (the runner and the key posting).
"""

import argparse
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
RELEASE = REPO / "private/tools/PS2Recomp-Fixer/build/ps2recomp/ps2xRuntime/Release"

WM_KEYDOWN, WM_KEYUP = 0x0100, 0x0101
HEADER_MIN_PIXELS = 2500  # orange "MAIN MENU" header box
ROW_MIN_PIXELS = 300      # orange highlight band of the selected row
TITLE_MIN_IOU = 0.70      # green logo mask against the reference title capture
MODE_MIN_LIT = 0.5        # fraction of non-black pixels on the screen after the menu
MODE_MIN_COLOURFUL = 0.05 # fraction of saturated pixels (rules out white or grey flashes)
FPS_FLOOR = 45.0          # median game frames/s with 0.25 s captures (about 59.9 without them)
AUDIO_FLOOR = 0.85
AUDIO_RMS_THRESHOLD = 150
AUDIO_RATE = 48000
AUDIO_FRAME_BYTES = 4     # 16-bit stereo mixer output
MIX_HEADER_BYTES = 44    # Fixed header written by DOD_SPU2_WAV
AUDIO_MODE_SECONDS = 12
ROWS = {"ARCADE": (176, 202), "TEAM": (209, 235), "SINGLE": (242, 268),
        "ENDLESS": (275, 301), "CHALLENGE": (308, 334), "PRACTICE": (341, 367)}
VK = {"START": 0x0D, "CROSS": 0x58, "UP": 0x26, "DOWN": 0x28}
NUMPAD_VK = {"START": 0x6B, "CROSS": 0x61, "UP": 0x20, "DOWN": 0x53}
EXTENDED_VK = {VK["UP"], VK["DOWN"]}  # arrows: without lParam bit 24 GLFW maps them to the numpad
MODE_STREAK = 3


def as_frame(image):
    """640x448 RGB uint8 array from a PIL image or an array."""
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    return np.asarray(image.convert("RGB").resize((640, 448)))


def orange(a):
    return (a[:, :, 0] > 200) & (a[:, :, 1] > 110) & (a[:, :, 1] < 200) & (a[:, :, 2] < 120)


def menu_header(frame):
    """True while the main menu's orange header is on screen, highlighted row or not."""
    return int(orange(as_frame(frame))[6:56, 14:318].sum()) > HEADER_MIN_PIXELS


def menu_row(frame):
    """The highlighted main-menu row, or None when the frame is not the main menu."""
    if not menu_header(frame):
        return None
    mask = orange(as_frame(frame))
    row = max(ROWS, key=lambda name: mask[slice(*ROWS[name]), 40:290].sum())
    return row if mask[slice(*ROWS[row]), 40:290].sum() > ROW_MIN_PIXELS else None


def mode_screen_visible(frame):
    """A lit, colourful frame that is not the main menu (the screen after Cross)."""
    if menu_header(frame):
        return False
    pixels = as_frame(frame).astype(int)
    lit = (pixels.sum(axis=2) > 60).mean()
    colourful = ((pixels.max(axis=2) - pixels.min(axis=2)) > 60).mean()
    return bool(lit > MODE_MIN_LIT and colourful > MODE_MIN_COLOURFUL)


def green_mask(frame):
    reduced = np.asarray(Image.fromarray(as_frame(frame)).resize((160, 112)), dtype=np.int16)
    red, green, blue = np.moveaxis(reduced, -1, 0)
    return (green > 90) & (green > red + 16) & (green > blue + 19)


def title_score(frame, references):
    """Best intersection-over-union of the frame's green logo mask against the reference frames."""
    mask = green_mask(frame)
    if not mask.any():
        return 0.0
    scores = []
    for reference in references:
        reference_mask = green_mask(reference)
        scores.append(float((mask & reference_mask).sum() / (mask | reference_mask).sum()))
    return max(scores)


def start_prompt_visible(frame):
    return int((as_frame(frame)[314:333, 235:405] > 222).all(axis=2).sum()) >= 320


def median_fps(err_text, first_field=900):
    rates = [float(r) for f, r in re.findall(r"\[fps\] field (\d+): ([.\d]+) game frames/s", err_text)
             if int(f) >= first_field]
    return round(statistics.median(rates), 1) if rates else None


def apply_fps_floor(verdict, fps, floor):
    """Turn a GREEN verdict RED when the frame rate is missing or below the floor."""
    if not verdict.startswith("GREEN"):
        return verdict
    if fps is None:
        return "RED FPS: no frame-rate samples"
    return verdict if fps >= floor else f"RED FPS: median {fps} < floor {floor}"


def audio_activity(path, start_frame):
    """Count full one-second mixer windows above the RMS threshold from the menu onward."""
    if not path.is_file():
        return 0, 0
    offset = MIX_HEADER_BYTES + start_frame * AUDIO_FRAME_BYTES
    window_bytes = AUDIO_RATE * AUDIO_FRAME_BYTES
    # The runner is terminated after capture. Use the file length because its WAV size fields
    # are periodically updated and may lag the actual mixer data.
    windows = max(0, (path.stat().st_size - offset) // window_bytes)
    active = 0
    with path.open("rb") as capture:
        capture.seek(offset)
        for _ in range(windows):
            samples = np.frombuffer(capture.read(window_bytes), dtype="<i2").astype(np.float64)
            active += int(np.mean(samples * samples) > AUDIO_RMS_THRESHOLD ** 2)
    return active, windows


def _windows():
    import ctypes
    user32 = ctypes.windll.user32
    user32.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint64, ctypes.c_int64]
    user32.MapVirtualKeyW.argtypes = [ctypes.c_uint, ctypes.c_uint]
    user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    return ctypes, user32


def find_hwnd(pid):
    ctypes, user32 = _windows()
    found = []
    enum_callback = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def on_window(hwnd, _):
        p = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True

    user32.EnumWindows(enum_callback(on_window), 0)
    return found[0] if found else None


def tap(hwnd, button, hold=0.15, *, keys=VK):
    _, user32 = _windows()
    vk = keys[button]
    down = 1 | (user32.MapVirtualKeyW(vk, 0) << 16) | ((1 << 24) if vk in EXTENDED_VK else 0)
    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, down)
    time.sleep(hold)
    user32.PostMessageW(hwnd, WM_KEYUP, vk, down | (1 << 30) | (1 << 31))


def run(executable, references, run_root, timeout, fps_floor=FPS_FLOOR, *, check_audio=False, keys=VK):
    # Absolute: the runner starts in its own directory, so a relative capture path would land there.
    case = Path(tempfile.mkdtemp(prefix="loop_", dir=Path(run_root).resolve()))
    env = dict(os.environ, KOF_VBLANK_WAKE1="1", KOF_GS_DISPFIX="1", DOD_FPS="1", DOD_MUTE="1",
               DOD_WINDOW_UNFOCUSED="1", DOD_PAD_TRACE="1",
               DOD_FRAME_CAPTURE_DIR=str(case), DOD_FRAME_CAPTURE_EVERY="0.25")
    mix = case / "mix.wav"
    if check_audio:
        env.update(DOD_SPU2_WAV=str(mix), DOD_SPU2_STATS="1")
    audio_start = None
    log = (case / "driver.log").open("w", encoding="utf-8")

    def say(message):
        print(message, flush=True)
        print(message, file=log, flush=True)

    verdict = "RED setup"
    with (case / "out").open("wb") as out, (case / "err").open("wb") as err:
        process = subprocess.Popen([str(executable)], cwd=executable.parent, env=env, stdout=out, stderr=err)
        say(f"run {case.name} pid={process.pid}")
        try:
            hwnd = None
            window_deadline = time.monotonic() + 30
            while hwnd is None and time.monotonic() < window_deadline and process.poll() is None:
                hwnd = find_hwnd(process.pid)
                time.sleep(0.2)
            if hwnd is None:
                say("RED setup: no runtime window")
                return 2, case
            state, previous, streak = "TITLE", None, 0
            deadline = time.monotonic() + timeout
            next_retry = 0.0
            verdict = "RED TITLE: no title with Start prompt"
            while time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.12)
                latest = max(case.glob("present_*.bmp"), key=lambda p: int(p.stem.split("_")[1]), default=None)
                if latest is None or latest == previous:
                    continue
                try:
                    frame = as_frame(Image.open(latest))
                except OSError:
                    continue  # capture still being written
                previous = latest
                now = time.monotonic()
                row = menu_row(frame)
                if state == "TITLE":
                    if title_score(frame, references) >= TITLE_MIN_IOU and start_prompt_visible(frame):
                        say(f"TITLE {latest.stem}")
                        tap(hwnd, "START", keys=keys)
                        state, next_retry, deadline = "MENU", now + 2.5, now + 20
                        verdict = "RED MENU: Start did not open the main menu"
                elif state == "MENU":
                    if row == "ARCADE":
                        say(f"MENU {latest.stem}")
                        if check_audio and mix.exists():
                            audio_start = max(0, (mix.stat().st_size - MIX_HEADER_BYTES) // AUDIO_FRAME_BYTES)
                        time.sleep(0.9)
                        tap(hwnd, "DOWN", keys=keys)
                        state, deadline, next_retry = "TEAM", now + 10, now + 1.5
                        verdict = "RED NAV: Down did not reach TEAM"
                    elif now >= next_retry and start_prompt_visible(frame):
                        say("retry START")
                        tap(hwnd, "START", keys=keys)
                        next_retry = now + 2.5
                elif state == "TEAM" and row == "TEAM":
                    say(f"NAV down {latest.stem}")
                    time.sleep(0.5)
                    tap(hwnd, "UP", keys=keys)
                    state, deadline, next_retry = "BACK", now + 10, now + 1.5
                    verdict = "RED NAV: Up did not return to ARCADE"
                elif (state, row) in (("TEAM", "ARCADE"), ("BACK", "TEAM")) and now >= next_retry:
                    # A press during the highlight animation can be dropped: repeat it on a stable row.
                    arrow = "DOWN" if state == "TEAM" else "UP"
                    say(f"repeat {arrow} on stable {row} row")
                    tap(hwnd, arrow, keys=keys)
                    next_retry = now + 1.5
                elif state == "BACK" and row == "ARCADE":
                    say(f"NAV up {latest.stem}")
                    time.sleep(0.9)
                    tap(hwnd, "CROSS", keys=keys)
                    state, deadline = "LEAVE", now + 15
                    verdict = "RED MODE_VISIBLE: Cross did not leave the main menu"
                elif state == "LEAVE":
                    # Two captures without the header: a single one can be a mid-animation frame.
                    streak = 0 if menu_header(frame) else streak + 1
                    if streak >= 2:
                        say(f"left menu {latest.stem}")
                        state, deadline, streak = "MODE", now + 45, 0
                        verdict = "RED MODE_BLACK: the screen after the menu never rendered"
                elif state == "MODE":
                    streak = streak + 1 if mode_screen_visible(frame) else 0
                    if streak >= MODE_STREAK:
                        Image.fromarray(frame).save(case / "mode_visible.png")
                        say(f"MODE_VISIBLE {latest.stem} (saved mode_visible.png)")
                        verdict = "GREEN title+menu+nav+mode_visible"
                        if check_audio:
                            try:
                                process.wait(timeout=AUDIO_MODE_SECONDS)
                                verdict = "RED AUDIO: runner exited during capture"
                            except subprocess.TimeoutExpired:
                                pass
                        break
        finally:
            if process.poll() is None:
                process.terminate()
            process.wait(timeout=10)
    err_text = (case / "err").read_text(errors="replace")
    fps = median_fps(err_text)
    say(f"fps median={fps}")
    verdict = apply_fps_floor(verdict, fps, fps_floor)
    if check_audio:
        active, windows = audio_activity(mix, audio_start) if audio_start is not None else (0, 0)
        fraction = active / windows if windows else 0.0
        if windows:
            say(f"audio active={fraction:.1%} ({active}/{windows} seconds with RMS > {AUDIO_RMS_THRESHOLD})")
        else:
            say("audio unmeasured: no complete mixer windows after menu entry")
        if verdict.startswith("GREEN"):
            if re.search(r"can't create PSM|PSMTBF_Create fails", err_text, re.IGNORECASE):
                verdict = "RED AUDIO: CRI ADX stream creation failed"
            elif windows < AUDIO_MODE_SECONDS:
                verdict = f"RED AUDIO: incomplete mixer capture ({windows} seconds)"
            elif fraction < AUDIO_FLOOR:
                verdict = f"RED AUDIO: active fraction {fraction:.1%} < {AUDIO_FLOOR:.0%}"
            else:
                verdict += "+audio"
    say(verdict)
    log.close()
    return (0 if verdict.startswith("GREEN") else 1), case


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--title-reference", type=Path, required=True,
                    help="private capture of the reference title screen (game-derived, never committed)")
    parser.add_argument("--executable", type=Path, default=RELEASE / "ps2EntryRunner.exe")
    parser.add_argument("--run-root", type=Path, default=REPO / "private/scratch/diag")
    parser.add_argument("--timeout", type=float, default=150)
    parser.add_argument("--fps-floor", type=float, default=FPS_FLOOR)
    parser.add_argument("--audio", action="store_true",
                        help="require at least 85%% active mixer audio from the menu through mode capture")
    parser.add_argument("--numpad", action="store_true",
                        help="drive the GPU profile with numpad + and 1, S and Space")
    args = parser.parse_args(argv)
    reference = Image.open(args.title_reference).convert("RGB")
    width, height = reference.size
    references = [as_frame(reference), as_frame(reference.crop((int(.035 * width), 0, int(.965 * width), height)))]
    code, _ = run(args.executable.resolve(), references, args.run_root, args.timeout, args.fps_floor,
                  check_audio=args.audio, keys=NUMPAD_VK if args.numpad else VK)
    return code


if __name__ == "__main__":
    sys.exit(main())
