# Menu/input feedback loop and test log · Fixer GPU build

Operational log for the closed-loop keyboard probe that drives the release criterion
(main menu → first mode → trio select → complete fight). English-only per repo convention.
Counts, addresses and outcomes only; every game-derived file stays under `private/`.
Companion to `runtime-av-handoff.md` (Codex's A/V handoff) and the bilingual diagnosis in
`docs/wayfinder/base-to-playable-fight/research/diagnose-runtime-performance-audio.md`.

## The loop

> Superseded for acceptance by the tracked `tools/runtime/closed_loop.py` (ticket 12 section below):
> title gate instead of the attract gate, `MODE_VISIBLE` milestone, fps floor. The private prototype
> below is kept for its history and its extra probe flags.

```
python private/scratch/diag/menu_loop.py --timeout 240 [--stop-at menu|mode] [--capture-every 0.5]
```

- Launches `private/tools/PS2Recomp-Fixer/build/ps2recomp/ps2xRuntime/Release/ps2EntryRunner.exe`
  with `DOD_WINDOW_UNFOCUSED=1`, `DOD_FRAME_CAPTURE_DIR=<run>`, `DOD_FRAME_CAPTURE_EVERY=0.5`,
  `DOD_PAD_TRACE=1`, `DOD_SPU2_OUT_WAV=<run>/queue.pcm`, `DOD_FPS=1`, `KOF_VBLANK_WAKE1=1`, `KOF_GS_DISPFIX=1`.
- Posts **real `WM_KEYDOWN`/`WM_KEYUP`** to the game window (found by PID via `EnumWindows`), so the
  interactive keyboard path is the one under test. No runtime rebuild needed.
- Waits for **visual evidence** (frame captures) before each press; never uses fixed host times.
- Steps: boot → colourful attract → START retry ladder (10 s apart, max 5) → MAIN MENU (ARCADE
  highlighted) → DOWN (expect TEAM) → UP (expect ARCADE) → CROSS → menu must disappear →
  45 s observation of the mode screen.
- Verdicts: `GREEN menu`, `GREEN menu+nav+mode`, `RED WAIT_MENU`, `RED WAIT_TEAM`, `RED WAIT_ARCADE`,
  `RED WAIT_MODE` (CROSS ignored), `RED MODE_BLACK` (left menu, nothing renders). Exit code 0/1/2.
- Each run dir `private/scratch/diag/ml_*` holds captures, `out`, `err`, `queue.pcm`, `mix.wav`,
  `driver.log`. The driver log names every press and gate with capture indices.
- **Do not click or type into the game window during a run**; stray physical keys contaminate state.

## Screen calibration (640×448 captures)

| Signal | Rule | Measured |
|---|---|---|
| MAIN MENU | orange px in header box x[14,318] y[6,56] > 2500 AND green bg fraction > 0.4 | 9602 px, 0.81 |
| Highlighted row | orange band sum x[40,290] > 300; rows ARCADE y[176,202], TEAM y[209,235], SINGLE y[242,268], ENDLESS y[275,301], CHALLENGE y[308,334], PRACTICE y[341,367] | ~900/band |
| Attract fight | lit fraction [0.015, 0.3] AND mean saturation of lit pixels > 20 | lit 0.06, sat 63 |
| Boot logos / autosave | lit 0.05–0.075 but **saturation 0** (grayscale) | sat 0.0 |
| Attract team lineup (6 fighters) | lit ≈ 0.18, sat ≈ 58 — colourful but NOT the demo fight | lit 0.178 |
| Black opening / broken screens | lit < 0.01 | 0.0 |

## Test log (what worked, what failed)

Earlier runs are Codex's; `ml_*` are this loop's. All under `private/scratch/diag/`.

| Run | Result | Lesson |
|---|---|---|
| `av_hgwveov_` (hands-off, 100 s) | black opening ~18–72 s, attract fighters 75–90 s, internal 59.9 fps | attract onset varies per run; never gate on host time |
| `av_nltx9zri` (script 52/62/66/92 s) | captures 15–22 (48–69 s) **black**; menu only in captures 30–33, after the 92 s START | the 52 s START landed on a black picture; menu is the only reliable visual anchor |
| `av_4tw1kiy7` (script + stray physical keys) | physical Space/A/S/KP presses at 12–32 s; START 52 ignored; captures 16–38 all black; UP/RIGHT/CROSS 101–113 no visible effect | open-loop fixed-time navigation fails; stray input contaminates; no retry = never reaches menu |
| `ml_k7v20box` (loop v1) | RED WAIT_MENU: lit-band detector fired on a grayscale boot logo at t≈6 s; START consumed (`code=257`) during boot | lit alone cannot separate logos/autosave from attract; use saturation |
| `ml_68x25l8c` (loop v2) | RED WAIT_MENU: sat detector fired on the 6-fighter lineup (t≈74 s); START consumed; 18 s of black afterwards | lineup ≠ demo fight; a single START is not enough |
| `ml_e7i49uxo` (loop v3, START ladder) | menu reached on 2nd START (capture 152, ARCADE). RED WAIT_TEAM: DOWN posted **without lParam bit 24** arrived as `code=322 mapped=0000` (GLFW numpad mapping) | ladder works; extended keys (arrows) need lParam bit 24 in posted messages |
| `ml_mt5vqmcf` (loop v4, bit 24 fixed) | DOWN→TEAM in ~1 s (capture 153), UP→ARCADE (154): **directional keyboard input verified end-to-end**. CROSS consumed; menu disappeared; 20 s black; RED WAIT_MODE because the gate demanded lit pixels | mode-entry screen renders black; gate must be "menu disappeared", then observe |
| `ml_ee8zmbx0` (loop v5, 45 s mode observation) | menu capture 153, DOWN/UP verified (154/155), CROSS left menu at 157, **45 s of lit=0.000**; median 58.5 fps; audio 7/99 active s | `RED MODE_BLACK`: mode-entry screen is a broken render path, not a slow load |

## Pitfalls (each cost at least one run)

1. `DOD_PAD_SCRIPT` is **host-time open-loop** (120 ms window sampled once per host frame). Game
   state at host time T varies across runs. Use the capture-gated loop instead.
2. `g_dodTestNewGameAt` / `g_dodTestRdram` are **never set anywhere in this tree**, so the
   `PS2_PAD_BOOT_SEQUENCE` / `DOD_PAD_SCRIPT_FRAMES` / `PS2_PAD_SCRIPT_HZ` game-frame clock is dormant.
3. `DOD_FRAME_CAPTURE_EVERY` is in **seconds** (min 0.05, default 5), max 720 captures; the GPU path
   writes `present_N.bmp` through `dodpcsx2::requestSnapshot`.
4. Posted `WM_KEYDOWN` for arrows needs **lParam bit 24** (extended key), else GLFW maps the scancode
   to the numpad (`code=322` = KP_2, unmapped). Letters/ENTER are non-extended and work as-is.
5. The picture **diverges from internal state**: opening and mode-entry screens render black while
   the game advances; the MAIN MENU renders reliably (libgraph draw-env forwarding in `GS.cpp`).
   START is only accepted once the game is internally in attract → retry ladder, stop at menu.
6. `proc.terminate()` loses the unflushed tail of `queue.pcm` (buffered writes); audio-second counts
   under-report on short runs.
7. Boot length varies (attract between ~50 s and ~75 s). The 65 s fallback in the ladder covers runs
   whose attract never becomes visible.
8. With 0.5 s captures + `DOD_PAD_TRACE` the median internal rate was 45–54 fps vs 59.9 hands-off at
   3 s captures. Overhead vs boot-phase sampling not yet isolated; do not treat it as a regression.

## Audio baseline (same runs)

`queue.pcm` (48 kHz stereo s16): 59–72 s captured, only **3–7 active seconds** (RMS > 150), peak
≈ 24 000. Intermittent effects, no continuous BGM verified — matches the owner's "som ruim".
The loop prints `audio={queue_seconds, queue_active_seconds, queue_peak}` each run.

## GIF traffic probe (`ml_2q2sdsi0`, loop + `--reglog --gs-capture 4300:1400`)

Analyzer: `python private/scratch/diag/gs_window_stats.py <gs.bin> [lo hi ...]` (or `per LO HI STEP`).
Field ≈ 58.8 × host seconds in these runs. Menu = fields ~4540–4650, transition gap 4662–4710,
mode screen (black) from ~4712.

- **All GIF traffic is path 3 (IMAGE uploads); path 1/2 = 0 across all 1400 fields**, including the
  menu's first draw and the DOWN/UP highlight moves. `PS2Memory::submitGifPacket` does forward
  PATH1/2 to `dodpcsx2::gif`, so the game simply sends no GIF draw packets here: the visible menu is
  rendered through another channel (Fixer HLE libgraph → PCSX2 DLL exports), not GIF draws.
- Menu window: constant ~1.84 MB/field, 45 packets/field, even while the menu is static.
- Mode window: uploads **grow** 15→28 packets/field (1.4→2.6 MB/field) while the picture stays black.
- Zero-traffic gaps at both screen transitions (4524–4538, 4662–4710).
- Reglog: `dispfb1`/`dispfb2` change **0x1400 → 0x148C** at mode entry; `pmode`, `smode`, `display1/2`
  unchanged. The game switches framebuffer and the new one presents black.
- Stall ruled out: `[fps]` stays 58–60 game frames/s and EE clock 294.9 MHz through the black window.

Refined hypotheses for `MODE_BLACK`, ranked:

1. **Stale framebuffer base in the draw channel**: mode-screen draws are submitted (via the HLE/DLL
   channel) against the old base (0x1400×64) while DISPFB points at 0x148C×64. Prediction: the DLL
   draw table shows draws in the mode window targeting the menu's base.
2. **Draw submission missing for that screen**: the HLE libgraph path never submits the mode screen's
   draws (only uploads arrive). Prediction: draw table empty in the mode window, populated in menu.
3. **Draws submitted but rejected by the DLL** (texture/format gate). Prediction: draw table present
   but frame PNGs black; DLL logs show rejected draws.

Next probe: `DOD_LINE_CAPTURE_DIR` (+ `DOD_LINE_CAPTURE_AT`) gives `draws/dod_draws.tsv` (one line per
draw) and frame PNGs from the DLL — run it once on the menu window and once on the mode window and
compare draw counts and target FRAME bases. Do not attribute the missing fight stage to the same
mechanism before a fight-field comparison with the Reference Emulator (handoff resume point 2).

## Where to resume

1. Read the newest `ml_*` verdict. `RED MODE_BLACK` persisting 45 s = broken render path, not load.
2. Run the draw-table probe above; it separates stale-base vs missing-submission vs rejected-draws.
3. Once the mode screen renders, extend the state machine: trio select (3 fighters + order) → fight →
   result screen, each step gated on captures. Keyboard delivery and menu navigation are already proven.
4. Audio: keep the per-second activity metric; compare a scene with known continuous BGM against the
   Reference Emulator before changing SPU2/ADX code.

## Ticket chain (GitHub, created 2026-11-25, separate from earlier tickets)

Specs published with `ready-for-agent`; native `blocked_by` edges make the chain sequential.
Agreed seam (owner-confirmed): this loop, promoted to tracked runtime tooling in #12, is the single
acceptance seam for every ticket; no per-module unit seams.

Chain order (execution order, not number order): #18 -> #12 -> #13 -> #14 -> #15 -> #16 -> #17.

| Issue | Scope | Blocked by |
|---|---|---|
| #18 | Main menu 3D background parity vs original (owner: buggy background elements); differential vs Reference Emulator | — |
| #12 | Render the first-mode entry screen (black after ARCADE PLAY); `MODE_BLACK` root cause + fix; loop promotion | #18 |
| #13 | Select a trio, confirm the order, preload a fight (loop extension; preload gated on game state, picture may be black until #14) | #12 |
| #14 | Render the fight stage and opening movie background (Reference Emulator differential) | #13 |
| #15 | Continuous BGM and clean SFX (per-scene audio activity gate) | #14 |
| #16 | Gate the flow up to fight preload: one green run with visuals + audio + fps floor | #15 |
| #17 | Complete a fight by keyboard (fight-time input fixes, FIGHT_FINISHED) and record the full green release certification | #16 |

Owner decisions (2026-11-25): fight completion moved out of #13 into #17, after the gate; #16's
conjunction stops at FIGHT_PRELOADED and #17 extends it with FIGHT_FINISHED. Main menu background
parity (#18) precedes everything; #12 is the post-menu entry screen render, NOT the main menu and
NOT trio selection (navigation stays in #13).
Frontier: #18 is the only unblocked ticket. Earlier issues (#1, #6–#11) and the local wayfinder
tickets are untouched by this chain.

## Ticket 18 — main-menu 3D background parity (2026-11-25)

Goal: the menu's 3D background matches the Reference Emulator (PCSX2 v2.8.2, same disc). The
foreground pills/highlight/logos and the upload path must stay intact. Acceptance seam is this loop.

### Visual differential (ground truth)

Reference menu = PCSX2 snap `snaps/…_20261113231211.png` and the embedded screenshot in its GS dump
(`…_20261113231211.gs.zst`, 640×480). Port menu = `ml_ee8zmbx0/present_153.bmp` (and the line-capture
frames below).

| Element | Reference | Port | Class |
|---|---|---|---|
| Rotating "THE KING OF FIGHTERS XI" ring emblem (green core, grey rings), upper-right | present, large, ~x520/640 | only a tiny clipped sliver at the right edge | wrong composition / missing |
| Radial fan of character icons (cyan), centre-right | present | absent | missing draw output |
| Blue curved swooshes, left | present | absent | missing draw output |
| Base fill behind everything | covered by the 3D layer | flat green visible | exposed base fill |
| Menu pills | translucent grey over the 3D layer | green (translucent over the green fill) | consequence of the missing layer, not a pill defect |
| Highlight / logos / navigation | correct | correct (GREEN menu+nav) | keep intact |

One root cause explains both the missing background and the green pills: the pills are translucent,
so with the 3D layer invisible they composite over the green base fill.

### Runs (this ticket)

| Run | Result | Lesson |
|---|---|---|
| `ml_dmj6ei27` (`--line-capture`, light) | GREEN menu+linecap, fps 54.0; menu capture 152; F8 posted at the menu dumped `linecap/capture_1/draws/dod_draws.tsv` | a posted F8 (VK 0x77) triggers `IsKeyPressed(KEY_F8)` after raylib `PollInputEvents`; capture-gated line capture works, no host-time guess |
| `ml_zvp29_n8` (`--line-capture --line-full`) | GREEN menu+linecap, fps 53.9; menu capture 150; full per-draw SaveInfo (context/vertex/transfers) + raw framebuffer PNGs | full mode gives the raw framebuffer after each draw and the decoded register context — the decisive artifacts |

Loop additions: `--line-capture` (post F8 at the menu, wait for `dod_draws.tsv`), `--line-full`
(full SaveInfo instead of light). Both stay capture-gated.

### GIF traffic differential (apples-to-apples)

New tools (private): `gsdump_ref_stats.py` (parses PCSX2 `.gs/.gs.zst`: header, embedded screenshot,
per-field path traffic, GIFtag FLG/PRIM, register histogram), `gs_port_draws.py` (same GIF logic over
the port's DOD `gs.bin` for a field window), `ref_reg_values.py` (last-write A+D register values).

- Reference menu dump: path 1/2 = 0, path 3 only, **PACKED** only; ~1.83 MB/field, 88 packets/field.
- Port menu window (fields 4540–4650 of `ml_2q2sdsi0/gs.bin`): path 1/2 = 0, path 3 only, PACKED;
  ~1.83 MB/field, 45 packets/field. **The background draw data reaches the port's DLL** — the earlier
  "menu shows only IMAGE uploads" note was an artifact of `gs_window_stats.py`'s byte-8 heuristic
  misreading PACKED vertex data. Defect is composition/rendering, not data delivery.
- The reference sends its draw-env via PACKED register lists, **not A+D** (`ref_reg_values.py` finds
  zero A+D writes), so register values must be decoded from PACKED to compare exactly.

### DLL draw table (menu window, `ml_zvp29_n8`)

Per frame the render target alternates `FBP 0x0 ↔ 0x1180` (double buffer). Six draws/frame:

| draw | kind | prim/verts | texture | notes |
|---|---|---|---|---|
| …765/772 | 2d-tri | tri 20 | TBP0 0x3480 P_8 256×512 | top band |
| …766/773 | fill | sprite 2 | none | full-screen base fill (the green) |
| …767/774 | 3d | tri 354/177 | TBP0 0x3580 **P_4** 256×256, CLUT **CBP 0x3e84** C_32 CLD 1 | background element |
| …768/775 | 3d | tri 1557/1539 | same 0x3580 P_4 | the radial fan |
| …769/776 | 2d-tri | tri 160 | TBP0 0x3680 P_8 256×512 | the pills (y176–368) |
| …770/777 | 2d-tri | tri 4 | TBP0 0x3480 P_8 1024×512 | full-screen quad |

3D background draw context: `ABE=1`, `ALPHA=(Cs−Cd)·As+Cd`, **`ATE=1 ATST=NOTEQUAL AREF=0`** (alpha≠0
to pass), `ZTE=1 ZTST=GEQUAL ZMSK=0`, `TFX=MODULATE TCC=RGBA`, vertex RGBA=128/128/128/128.

### What is ruled out

- **Display/composition read-out**: the *raw* framebuffer PNG after all draws (`176770_f04548_…00000…`,
  `176777_f04549_…01180…`) is still green → the draws themselves produce no background, not a DISPFB mix-up.
- **BGCOLOR**: reglog `bg 0` throughout → green is a rendered primitive (the fill), not the GS clear.
- **CLAMP**: context `WMS=WMT=1` (CLAMP) with MINU/MAXU=0 is fine — CLAMP mode clamps to the texture
  extent and ignores MINU/MAXU (only REGION_CLAMP uses them). Not the bug.
- **Missing draw submission**: the 3D draws are present in the DLL draw table with real vertex counts.

### Candidate root causes (unconfirmed — the next fork)

1. **CLUT / texture data not resident**: P_4 indices at TBP0 0x3580 sample a CLUT at CBP 0x3e84 that is
   zero/absent in the port's GS memory → sampled alpha 0 → `NOTEQUAL 0` alpha test discards the whole
   background. The pills' P_8 CLUT would be wrong too (green). Predicts: reference uploads to
   0x3580/0x3e84 that the port mis-addresses or drops.
2. **Vertex transform**: the SaveInfo vertex X/Y span wide negative/positive ranges; if the background
   vertices land off-screen the layer is invisible. BUT the SaveInfo "Z" is a raw 32-bit value (>24-bit),
   so its X/Y/Z decode is not trustworthy screen-space — do not conclude off-screen from it alone.

### Pitfalls (each cost time this ticket)

9. BMP captures are not model-viewable; convert to PNG first (PIL) under `private/`.
10. `gs_window_stats.py` reads byte 8 of every 16-byte chunk as a register → PACKED vertex/IMAGE bytes
    look like garbage regs and the menu was mislabelled "only IMAGE uploads". Use `gs_port_draws.py`.
11. Light line-capture frame PNGs are the *presented* frame, not the raw framebuffer; use `--line-full`
    for the per-draw raw framebuffer PNGs and register context.
12. The reference menu draw-env arrives as PACKED register lists, not A+D; an A+D-only extractor finds
    nothing. Comparing exact register/vertex values needs a PACKED decoder (PCSX2 `GIFPackedRegHandler*`).
13. SaveInfo `vertex.txt` Z is shown as a raw 32-bit word; X/Y/Z are not directly screen coordinates.

### Correction — GIFtag bit layout (invalidated the first parse)

The first parsers used FLG=39-40 / NREG=41-44 / REGS=45-108. **Wrong.** PCSX2 `GSRegs.h GIFTag` is
NLOOP 0-14, EOP 15, PRE 46, PRIM 47-57, **FLG 58-59, NREG 60-63, REGS = the whole high qword (64-127)**.
`makeGiftagAplusD` sets bit 60 (NREG=1) + high qword 0xE (REGS=A+D), which proved it. With the fix:

- Reference menu = PACKED vertices (600 tags) + IMAGE uploads (88) + A+D draw-env/upload setup
  (BITBLTBUF/TRXPOS/TRXREG/TRXDIR=88, TEX0_1/CLAMP_1=248). NOT "PACKED-only, no A+D" as first thought.
- Port menu window (`ml_8iqn8kz_`, fields 4550-4560) = same structure: PACKED 640, XYZ2/RGBAQ/UV≈74400,
  BITBLTBUF/TRXDIR=220, TEX0_1/CLAMP_1=190. So **no PACKED→A+D conversion bug**; stream shape matches.
- Port `FBP 0x1180` in the draw context is `0x8c×32`; reference FRAME_1 FBP=0x8c. Same render targets.
- `gs_packet_order.py` classifies by first tag only (a record leads with an A+D env tag then PACKED
  vertices), so it mislabels draws; use `gs_port_draws.py` (all tags) for histograms.

### CLUT sharing (the leading hypothesis)

`DOD_IMAGE_TRACE` (HLE `sceGsExecLoadImage` "load" + DLL-feed `gifxfer`/`draw` classification) shows the
menu uploads the P_4 background CLUT (64 B, w8 h2) to **dbp 0x3e84**, then a P_8 CLUT (1024 B, w16 h16)
to the **same 0x3e84**, overwriting it. Draw contexts: background P_4 CBP=0x3e84 CSA=0 CLD=1; pills P_8
CBP=0x3e84 CSA=0 CLD=1 (shared); top band P_8 CBP=0x3e80. Reference resident CLUT at 0x3e84 has alpha=64
(passes the background's `ATE=1 ATST=NOTEQUAL AREF=0`); the port background reads a wrong/zero CLUT and is
discarded. Whether the overwrite lands before the background draw (ordering) vs the CLUT cache failing to
snapshot is what the corrected DLL-feed trace decides.

### Reference motion capture (PCSX2)

`pcsx2_menu_capture.py` drives pcsx2-qt to the menu and bursts F8 screenshots. Pitfalls learned:

14. PCSX2 Qt boots the disc from the **positional** argument, not `-disc` (with `-disc` it stayed at the BIOS).
    Use `pcsx2-qt.exe -batch -fastboot -portable "<iso>"`. BIOS is PAL 30004R; the NTSC disc boots fine.
15. The port's menu classifier (green-bg fraction > 0.4) does NOT recognise the reference menu (white/blue bg,
    lit≈1.0). For reference captures, detect the menu by the orange header alone or by eye, not the port gate.
16. PCSX2 keyboard: Start=`1`, Cross=Numpad1, Screenshot=F8, Pause=Space; input via PostMessage to its window works.

Reference motion confirmed from samples `…_231211` (blue), `…_231233` (green), `…_20261125190402_(2)` (blue,
"Complete"): the emblem text ring + radial fan **rotate** and the palette **cycles blue/cyan ↔ green/lime**;
pills/header stay fixed. Owner closed the capture once samples were sufficient (also has the opening-video and
logo-screen references; the logo screen still does not appear in the port — separate ticket scope).
Parity checklist written to `docs/wayfinder/base-to-playable-fight/research/menu-background-parity.md`.

### Next probe (the fork)

Confirm root cause 1 vs 2 before any C++ change, by one of:
- (a) Decode the reference PACKED stream (registers + vertices + BITBLTBUF upload destinations) and
      diff against the port's forwarded stream / draw context — no rebuild.
- (b) Replay the reference `.gs` dump through the port's own `pcsx2gs.dll` (small harness): correct
      picture ⇒ DLL fine, port data wrong; green ⇒ DLL/config issue.
- (c) Instrument the Fixer CLUT/texture upload addressing (P_4 + CLUT) and the menu vertex path, rebuild,
      re-run this loop.
Acceptance once fixed: parity checklist green vs reference AND GREEN menu+nav AND fps floor, one run.

### Synthetic renderer check

`python private/scratch/diag/synthetic_gs_palette.py private/tools/PS2Recomp-Fixer/build/ps2recomp/ps2xRuntime/Release/pcsx2gs.dll`
opens the same DX11 DLL used by the runtime in a hidden window and reads back pixels from synthetic draws.
It uses generated test data and calls the DLL directly.

| Check | Result | Lesson |
|---|---|---|
| Synthetic DX11 readback | 7/7 passed | The DLL rendered the opaque 4-bit and 8-bit textures with a shared palette address. It rejected the transparent 4-bit draw with alpha testing on and rendered it with alpha testing off. |
| Mutation control | Expected failure | Changing the transparent palette entry to opaque made the transparent-pixel assertion fail. |
| Logical vs raw palette readback | Passed | A generated 64-byte palette matched the logical readback byte for byte while the same bytes at the raw VRAM base were in a different order. The earlier checksum comparison mixed these representations and cannot establish a palette mismatch. |
| Existing Release cache tests | 45/45 passed | CPU backend coverage includes palette reloads, shared contexts, transfer visibility and VRAM addressing. |
| Existing Release runtime suite | 440/464 passed | The libgraph image upload/readback and alpha-test cases passed. The broader suite had 24 failures in the local binary, including GS privileged-register and scheduler cases. |

This check exercised the DLL input and framebuffer readback. The source of the original render failure remains unconfirmed.

### Live draw alpha and GIF differential

`ml_ig9s3fdd` reached `GREEN menu+linecap` at 53.0 median internal fps using the diagnostic DLL in an isolated runtime.
At field 4509, draws 176597 and 176598 both reached the texture-source stage. Estimated effective alpha was
0–128 before and after source lookup, `NOTEQUAL 0` remained enabled, and the framebuffer and depth write masks
stayed zero. The scissor and clipped draw bounds were both 640×448. These results rule out draw-wide cancellation
by the alpha optimizer or write masks. Individual sampled fragments can still fail alpha or depth.

For port GIF fields 4545–4559 and two reference captures (`…231211`, `…231233`), the same logical transfer
payloads had matching 48-bit SHA-256 prefixes for the packed texture transfer and for both palette uploads. The 16-entry
palette contains one zero-alpha entry and 15 entries with alpha 128 in each capture. This supersedes the earlier
upload-vs-raw-VRAM checksum comparison. The GIF differential also found matching XYOFFSET, SCISSOR, TEST and ZBUF
for the selected draws. Both reference captures include a small subset with `TEX0.TFX=DECAL`. The sampled port
fields use `MODULATE` throughout. The recorded vertex bounds also differ before clipping, so these captures do not
establish which difference is causal. Inspect the per-fragment depth outcome and compare vertex data at the same
animation phase before changing default render state.

The temporary instrumentation patch and the draw table remain in the private run directory.

### Depth A/B in the isolated GPU runtime

`ml_5_3p7zi2` reached `GREEN menu+linecap` at 51.2 median internal fps. The first four capture fields used
the original depth test (`GEQUAL`) for both selected draws. The next four set `ALWAYS` for those draws only.
The draw table recorded eight calls in each depth configuration. The 525×110 sample above the menu items was
100% green in the controls and 0% green in the last three override fields. This override produced a flat white
fill with gray menu items. The missing background detail remains absent. The depth override is diagnostic only.

Control screenshot: field 4547. Override screenshot: field 4549. Both use the same alternating render target.
The raw framebuffer PNGs and temporary patch remain under the private run directory.

The follow-up `ml_0xy1yamn` tested two fields for each condition. The sampled region stayed 100% green with
normal depth and with the override on the smaller draw only. With the override on the larger draw only, it
stayed green in the first field and became uniformly white in the second. Both fields with both draws overridden
were uniformly white. The draw table confirms the depth mode for each draw in all four conditions.
Fields 4570 and 4574 show the control and the larger-draw-only override on the same render target. The run
reached `GREEN menu+linecap` at 54.5 median internal fps. The result isolates the source of the white fill under
the depth override. The cause of the missing background detail remains open.

## Separate investigation — black title screen before the menu

Reference evidence: the older screenshot ending in `190303_(2).png` contains the title and the blinking prompt.
A new reference run captured the same title in `title_find/reference_title.gs.zst` and confirmed the logo in
`title_find/reference_title_at_dump.png`. The native `ml_tve54idy` run used the unmodified Release DLL. Six raw
framebuffer samples before the menu were solid RGB black. Each contained one untextured fill. Field 4329 was
captured immediately before the Start that opened the menu. Field 4422 showed the menu with five textured draws.

Logical GIF counts per field, verified over four fields on each side using `title_gif_summary.py`:

| Window | PATH3 packets | 64×64 uploads | IMAGE bytes | TEX0 writes | Vertex kicks |
|---|---:|---:|---:|---:|---:|
| Reference title, fields 0–3 in the dump | 366 | 180 (140 PSM 02, 40 PSM 00) | 1,802,240 | 181 | 372 |
| Native pre-menu capture from `ml_2q2sdsi0`, fields 4328–4331 | 184 | 180 (140 PSM 02, 40 PSM 00) | 1,802,240 | 0 | 2 |

Both windows use PATH3. The upload counts, formats, dimensions and total byte volumes match. In the native
window, the two vertex kicks account for the black fill and none of the reference's texture-bind commands reach
the DLL. This localizes the blank frame to missing textured-draw submission before the renderer. The exact
upstream point remains open. Trace a non-image PATH3 packet from the producing code through GIF DMA submission,
using the post-Start menu packets as the positive control. The protocol summary was checked with split IMAGE
continuation and REGLIST test inputs. All derived data remain private.

### Title fix — DMA scratchpad address

The `ml_x9wa6f27` provenance run observed 180 enabled, unmasked PATH3 chain starts per sampled title field
interleaved with the 180 uploads. The chain walker recorded no corresponding tags before the menu. The sender
passed a CPU scratchpad pointer to `sceDmaSend`. `toDmaPhys()` masked the CPU window from `0x70000000` to
`0x10000000`, outside RAM, so the chain walker discarded the tag before forwarding any draw.

The fix reuses the runtime's scratchpad address detection and normalizes both CPU scratchpad aliases to the
window already supported by the DMA walker. The `PS2Memory` regression feeds a synthetic scratchpad DMA chain
through `sceDmaSend` and checks the payload at the GIF callback. It failed before the fix and passed afterward.
The runtime suite went from 440/465 to 441/465, with the same 24 other failures and no new failing cases.

The fixed executable is installed in the Release directory used by `run_game_gpu.bat`. The previous executable
is saved in `title_find/ps2EntryRunner.before-scratchpad-fix.exe`. The final Release run `title_verify_qolcktl2`
captured the title and Start prompt, recorded 181 textured draws in the title field, opened the menu with Start,
and verified Down to TEAM and Up to ARCADE. The prompt and stable menu row gate input in this probe because
earlier runs sent keys during transitions. The result is `GREEN title+menu+navigation`.

### Playback enabled

`title_verify_qd7x7ea0` ran the same Release executable with `DOD_MUTE` unset and received
`GREEN title+menu+navigation`. The 48 kHz stereo playback stream opened. Output stats reported no underruns
or queue drops. The resampled host queue contained signal at menu entry and during navigation. In the
12-second idle menu sample, 9 of 48 quarter-second windows exceeded RMS 150 and 38 were effectively silent
(RMS at most 1). Continuous BGM is still unverified. These measurements are from the runtime's host queue.

## Ticket 12 — mode screen and the rotating layer (2026-11-26)

### MODE_BLACK was already fixed

With the scratchpad DMA fix (`2d655ad`) installed, Cross on ARCADE PLAY leaves the menu and the
character select screen renders within ~2 s (`mp_pl7zsaix`: lit 0.84 for 30 s; owner confirmed). No
further draw-submission change was needed for the black screen itself. The loop is now tracked as
`tools/runtime/closed_loop.py` with the `MODE_VISIBLE` milestone (3 consecutive lit, colourful,
non-menu captures; the classified frame is saved as `mode_visible.png` in the private run dir).

### The rotating layer: three causes, found in this order

Probe: `private/scratch/i12/gsvert.py` walks GIF state in a PCSX2 `.gs.zst` dump or a DOD `gs.bin`
and prints per-batch vertex ranges (X/Y after XYOFFSET, Z, UV); `--dump TBP PRIM` lists vertices.
Reference = PCSX2 snaps `…231211` (menu) and `…231259` (character select).

| Step | Evidence | Outcome |
|---|---|---|
| Menu layer vertices, port vs reference | reference 3D batch (TBP 0x3580 P_4) Z 0xFFFF8D34–8EDF; port Z 0–0xFFF17D36, a 1008-vertex batch at X=0 with Z 0x80000000 | geometry is wrong before the renderer; the earlier CLUT/alpha hypotheses were downstream |
| Generated projection `0x21F9F0` | its clip test reads the VU0 sticky status flags; stale `src/runner` emits no MAC/status update | nothing ever clipped; behind-camera vertices wrap into 0..4096 |
| Diagnostic: flags added in `0x21F9F0` only | menu turns black, select ring more continuous; all menu layer vertices now clipped to (0,0,0) | clip works, projection itself still wrong |
| Diagnostic: `lqc2 $vf0` in the VU0 context restore `0x103098` ignored | no visible change (scheduler already resets VF0 per slice) | kept: hardware semantics, but not the cause |
| Trace in `0x21F9F0` (`KOF_I12_TRACE`) | matrix w column (0,0,1,0), translation w 0, Q ≈ 1e6 | combined world/view/screen matrix lost the view distance |
| Original `sceVu0MulMatrix` (0x104260) disassembly | loads arg1 rows into VF4..VF7, loops over arg2 rows: out = arg2 · arg1; HLE stub computed arg1 · arg2 | **root cause 1**: HLE operand order |
| MulMatrix fixed | menu emblem/fan and white background appear; menu batches match the reference (decal batch identical, 1008-vertex batch within 1 px, Z band equal) | 3D layer restored |
| Owner: emblem sits at the right edge, mid-height (same as the select-screen "distorted circle") | 24-vertex TRI_STRIP TBP 0x3480: corners off by exactly +255 px for offsets < −128 px | 2D rotated sprites |
| Rotated sprite builder `0x215E50` | rounds each rotated corner through libgcc soft-double (`0x11B238`, `0x11B608`, `0x11BC68`); trace `KOF_I12_TRACE2`: `__adddf3(0.5, −97.66)` returned +158.84 | soft-double add lost the sign |
| `_fpadd_parts` (0x11B3E0) generated code | a branch-likely on the sign of a 64-bit difference emitted as a 32-bit test | **root cause 2**: 32-bit sign branches in stale output |
| `bltzl` fixed (64-bit) | `__adddf3` → −97.16; select rings ("PLEASE SELECT", "PLAYER ONE", "TWO PLAYERS") identical to the reference; menu emblem back in the upper right | 2D layer restored |
| Normalize / CameraMatrix HLE | original `sceVu0Normalize` uses the xyz length and writes w = 0; HLE used xyzw | fixed and tested; no visible change in the menu |

`src/runner` (25,273 files, 2026-11-21) predates the generator fixes for 64-bit sign branches and
VU0 macro flags. `tools/runtime/upgrade_stale_runner.py` applies them keyed on each instruction's
disassembly comment: 2,963 sign branches in 1,946 files, 78 FMAC flag updates, 1 LQC2-to-VF0 load.
Backup of the pre-upgrade tree: `private/scratch/i12/runner_before_upgrade/`.

### Tracked loop and acceptance

`python tools/runtime/closed_loop.py --title-reference private/scratch/diag/title_find/reference_title_at_dump.png`

| Gate | Threshold |
|---|---|
| TITLE | green logo mask IoU ≥ 0.70 against the reference title capture and the Start prompt visible; START retried every 2.5 s while the prompt shows (replaces the attract gate and the 10 s ladder) |
| MENU / NAV | orange header > 2,500 px; highlighted row band > 300 px; an arrow is repeated after 1.5 s on a stable row |
| leave menu | two consecutive captures without the orange header |
| MODE_VISIBLE | 3 consecutive captures: no header, lit (sum > 60) fraction > 0.5, saturated (max−min > 60) fraction > 0.05 |
| FPS | median `[fps]` game frames/s after field 900 ≥ 45 (captures every 0.25 s cost ~9 fps) |

| Run (`private/scratch/i12/`) | Result |
|---|---|
| `loop__h5pza4m` | RED TITLE: relative `--run-root` sent captures to the runner's cwd (fixed: resolved to absolute); fps 59.9 without captures |
| `loop_0htkj8oo` | RED NAV: Up landed during the highlight animation (fixed: repeat on a stable row) |
| `loop_z24v2ziw` | **GREEN title+menu+nav+mode_visible**, fps 50.6, upgraded `src/runner` + libvu0 fixes |
| `loop_gyuyuw8a` | **GREEN title+menu+nav+mode_visible**, fps 50.7, after review fixes (two-capture menu exit, fps floor) |

### Remaining: text ring under the 3D fan (issue #18)

The emblem's text ring (TBP 0x3480 P_8, 1008 vertices) is drawn between the two halves of the fan with
interleaved Z (reference ring 0xFFFF8DA6–8E55, fan 0xFFFF8D34–8EDF, GEQUAL). The DLL draw table reports
the ring at Z 0xFFFF8E00 flat and the fan at 0xFFFF8E00–8F00: 32-bit depth near 2³² is held with float
precision (steps of 256), so ring and fan tie and the later fan half covers the text. The vertex data
matches the reference; this is renderer depth precision, not EE code.

### Pitfalls (this ticket)

17. `DOD_GS_CAPTURE` from an early field slows boot so much that the title may not appear within
    120 s; start the window near the title (title ≈ field 3,300–3,600 in a hands-off boot).
18. Desktop Commander shells are PowerShell 5: `*>` writes UTF-16 logs, and inline `python -c` with
    nested quotes fails to parse. Put scripts in files.
19. The runtime test binary links `ps2_test_lib`; rebuild `ps2xTest/ps2_test_lib` before
    `ps2xTest/ps2x_tests` or the new tests do not run.
20. The 32-bit sign-branch defect only shows where a GPR holds a true 64-bit value (soft-double,
    `ld`/`dsubu` arithmetic); 32-bit results are sign-extended, so most of the 2,963 sites behaved.
