# Draft: native experience and customization

Approved on 2026-11-26 and published as GitHub issue #19, complementary to the existing project spec #1; its complete-fight and rollback goals remain in force. The ticket proposal below is retained as the review record; issue #10 carries the joystick slice, and the other slices were published as #20–#28.

## Problem Statement

The native port can launch a GPU build, but its startup presentation still needs comparison against the PS2 Release, and players do not have a launcher for configuring the native experience. Players want to use a keyboard or joystick, avoid an unnecessary memory-card notice, select unlock behavior, fill widescreen margins and explore externally supplied character customizations. Existing game data must remain locally supplied by each player.

## Solution

Provide correct startup logos and a launcher that starts the installed native port with player-selected options. Maintain the game's save behavior, 4:3 image and rollback constraints. Investigate Color Edit before specifying or implementing an external customization format. Support joystick play through a Complete Fight.

## User Stories

1. As a player, I want the SNK logo to appear correctly, so that startup matches the PS2 Release.
2. As a player, I want the ADK logo to follow correctly, so that startup preserves the original sequence.
3. As a player, I want a launcher, so that I can start the game and configure its native options.
4. As a player, I want settings to persist, so that I do not repeat setup every launch.
5. As a player, I want to configure keyboard controls, so that I can choose comfortable inputs.
6. As a player, I want to configure a joystick, so that I can use my preferred controller.
7. As a player, I want distinct player assignments, so that two people can play independently.
8. As a player, I want to complete a fight with a joystick, so that its use is verified in play.
9. As a player, I want the memory-card notice skipped by default, so that startup is quicker.
10. As a player, I want to turn the skip off, so that I can see the original notice.
11. As a player, I want my save loaded when skipping the notice, so that my progress remains available.
12. As a player, I want save errors reported, so that skipping a notice does not conceal a failed load.
13. As a player, I want an unlock-all cheat option, so that I can select locked characters.
14. As a player, I want the unlock cheat switchable off, so that ordinary progression remains available.
15. As a player, I want unlocked state handled consistently during rollback, so that resimulation remains deterministic.
16. As a player, I want a soft gradient beside the 4:3 image, so that widescreen margins are intentional.
17. As a player, I want to turn side decoration off, so that I can use plain margins.
18. As a player, I want to use artwork from my own disc later, so that the sides can show game gallery art.
19. As a player, I want the game image to retain its aspect ratio, so that characters are not stretched.
20. As a player, I want the pre-fight transition to match the PS2's duration, so that its pacing feels right.
21. As a player, I want to skip that transition with a button, so that I can get to the fight sooner.
22. As a player, I want Color Edit investigated, so that externally supplied character customizations become possible.
23. As a player, I want malformed or incompatible customization files rejected clearly, so that my saves are not damaged.
24. As a player, I want supported customizations to appear on the selected fighter and in a fight, so that I can use them in play.
25. As a player, I want the expected persistence of customizations documented and verified, so that I know what survives restart.
26. As a contributor, I want game-derived files to stay private, so that the repository and release do not distribute game data.

## Implementation Decisions

- Preserve the existing User-supplied Disc workflow; never commit or distribute extracted assets, captures, generated game code, saves or images of game data.
- Retain the existing native input and save interfaces where feasible. Keyboard and joystick input must remain compatible with the single frame input seam intended for rollback.
- The autosave notice skip is configurable and enabled by default. Prefer not displaying the notice, but do not bypass save initialization or hide errors.
- Use a switchable unlock cheat consistent with the current rollback-state ADR; verify the real unlock mechanism before treating it as implemented.
- Preserve 4:3 presentation. Start with a soft gradient; later gallery art is locally extracted from each player's own disc and remains private. Gallery support is separate from the initial gradient.
- Measure pre-fight transition timing against the Reference Emulator before implementing the skippable equivalent.
- Investigate Color Edit's edit, save, selection and rendering lifecycle first. External format, import seam, persistence and the extent beyond palettes remain undecided until the investigation produces evidence.
- Capture and compare both the actual native window and the Reference Emulator for the boot logos. A 640×224 diagnostic capture alone does not prove the visible window is clipped or establish the cause.

## Testing Decisions

- Prefer the highest existing end-to-end seam: start the native build, observe presentation and use real input and save behavior. Extend the existing closed-loop runtime verification where practical, rather than creating competing end-to-end harnesses.
- Compare boot logos and pre-fight transition against the Reference Emulator with the same disc. Keep captures private. Verify the actual window as well as diagnostic capture output.
- Exercise launcher settings through launching the runtime: keyboard and joystick assignment, persistence, notice on/off, real save loading and errors, unlock on/off, and widescreen appearance. Demonstrate a Complete Fight with a physical joystick; automated synthetic input supplements but does not replace that observation.
- For external customization, prove a controlled change in character selection and fight and test persistence and invalid files against copies of saves. Confirm rollback behavior if the chosen seam changes simulation state.
- Good tests assert observable behavior and use synthetic input where possible. Existing runtime closed-loop checks, replay tooling and parser tests provide prior art; no proprietary screenshots or fixtures enter git.

## Out of Scope

- Distributing game files or captures; other base versions; matchmaking or online transport.
- Replacing the game renderer with a new high-resolution renderer.
- Assuming a specific Color Edit file format or promising broader asset replacement before investigation.
- Declaring audio, keyboard fight certification or full reference parity achieved merely because the owner elected to close earlier issues.

## Further Notes

The precise launcher design and Color Edit customization scope remain open. Consult the live issue tracker for the current status and dependencies.

## Existing issue reconciliation proposal

- #1: retain its complete-fight and rollback goals; make this proposal a complementary spec linked to #1, rather than silently rewriting the parent. Reconcile stale architectural claims separately.
- #2, #3, #12: retain closed; validate #3's export in the clean build.
- #4, #5: reopen for a clean GPU rebuild and current-runtime Reference Emulator comparison, respectively, per owner decision.
- #6: retain rollback/synctest and unlock requirements. The launcher unlock slice below should refer to #6 and avoid duplicating the rollback engine.
- #7: investigate current applicability. #8 and #9: reconcile acceptance criteria with the adopted runtime. #10: retain its two-player input and memory-card checks, and add physical-joystick Complete Fight verification instead of creating an overlapping input issue.
- #11: update to request a new current-build replay and check whether the formatting warnings reproduce; keep the earlier replay private and do not delete it automatically.
- #13, #14, #15, #17: close per owner's decision, explicitly recording that this is scope acceptance, not new proof that every historical acceptance criterion was met. Track joystick verification under #10.
- #16: retain the integrated gate. Reconcile its visual/audio requirements with the owner's decision to close #14 and #15, rather than asserting that those older checks were proven. Track the transition separately.
- #18: retain and update with the user's report that the circular text should appear above the emblem; verify the actual cause and result.

## Proposed ticket slices

Titles below are proposed English GitHub issue titles. Blocking edges describe completion gates, not a mandatory work order. Existing #10 and #6 are amended or linked as described above, rather than duplicated.

### A. Restore the SNK and ADK startup logos

**Blocked by:** None.

**What to build:** Both startup screens render in sequence like the PS2 Release.

- [ ] Compare actual native-window presentation against the Reference Emulator for both screens and reproduce the defect.
- [ ] Correct confirmed differences and verify both screens plus subsequent startup without distributing captures.

### B. Launch the native game with persistent keyboard settings

**Blocked by:** None.

**What to build:** A player can open the launcher, configure keyboard controls, save them and start the native game with those bindings.

- [ ] Settings persist across launcher restarts and affect gameplay through the existing input path.
- [ ] Report an unavailable runtime or invalid settings clearly; do not claim unsupported settings work.

### C. Configure and verify joystick play

**Blocked by:** B for launcher integration; the gameplay and device investigation can start independently. Reconcile with existing #10 rather than duplicate it.

**What to build:** A player configures a joystick in the launcher and completes a fight with it; two-player input remains independent.

- [ ] Demonstrate a Complete Fight with a physical joystick, with observable input and a result screen.
- [ ] Verify two-player assignments and the existing memory-card criteria in #10.

### D. Skip the memory-card notice while loading saves

**Blocked by:** B for the launcher option; save-path investigation can start independently.

**What to build:** The configurable skip defaults on, preferably without showing the notice, and the player's saved progress still loads.

- [ ] On/off behavior persists; disabled mode shows the original notice.
- [ ] Existing, absent and invalid saves behave correctly, with errors surfaced and no loss of progress.

### E. Select the unlock-all cheat from the launcher

**Blocked by:** B for the launcher option; coordinate with #6 for unlock state and rollback.

**What to build:** The player can enable or disable the cheat and select supported locked fighters.

- [ ] Verify enabled and disabled behavior and preserve ordinary progression.
- [ ] Verify state handling is compatible with rollback requirements.

### F. Fill widescreen margins with a soft gradient

**Blocked by:** B for the launcher option.

**What to build:** The player can enable or disable a soft gradient around the undistorted 4:3 game image.

- [ ] Verify multiple widescreen sizes and 4:3 without stretching or obscuring the game.
- [ ] Verify the selected setting persists.

### G. Use local gallery art in widescreen margins

**Blocked by:** F.

**What to build:** A player can use gallery art from their own disc in place of the initial gradient.

- [ ] Extract and load locally; no game data enters git or the distributed product.
- [ ] Missing art has a clear fallback and the game image stays 4:3.

### H. Match and allow skipping the pre-fight transition

**Blocked by:** None.

**What to build:** The transition after order selection matches reference timing and can be skipped with a button.

- [ ] Measure against the Reference Emulator; verify automatic completion and player-triggered skip.
- [ ] Both paths reach the fight reliably; preserve the integrated gate in #16.

### I. Investigate Color Edit and external customization

**Blocked by:** None.

**What to build:** A reproducible investigation identifies how an edit is created, saved, selected and displayed, and evaluates safe external import seams.

- [ ] Demonstrate a controlled edit across save/restart, character selection and fight using private copies.
- [ ] Document observed limits, candidate formats and persistence/rollback tradeoffs without publishing game data.

### J. Import a verified external character customization

**Blocked by:** I.

**What to build:** A player imports a supported external customization and sees it on the intended character in selection and a fight.

- [ ] Document the supported format and verify intended persistence after restart.
- [ ] Reject malformed or incompatible files clearly without corrupting existing saves; validate rollback implications for the chosen seam.
