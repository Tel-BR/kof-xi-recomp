# Native launcher and boot requirements

Owner request, 2026-11-26. This is a work plan, not a description of features already implemented.

## Boot logos

The SNK and ADK startup screens should appear in sequence, with the same framing and behavior as the PS2 Release. Compare both with the Reference Emulator using the same user-supplied disc. Keep all game-derived captures under `private/`.

On the current installed GPU build, an unattended run through field 1200 produced both logo images and the autosave notice. The GPU frame captures of the logo screens were 640×224, while the autosave capture was 640×448. The logo images are cut off in those captures. A capture-path or presentation discrepancy has not been excluded; the images alone do not establish what the application window presents, or the underlying cause. Existing `closed_loop.py` starts its visual checks at the title screen and does not validate either boot logo. Obtain matching PS2 reference and actual window presentation captures, then build a repeatable check specific to the defect before diagnosing or changing rendering.

Local reproduction (PowerShell; captures remain private):

```powershell
$env:DOD_WINDOW_UNFOCUSED = '1'
$env:DOD_FRAME_CAPTURE_DIR = (Join-Path (Get-Location) 'private/scratch/diag/boot_review')
$env:DOD_FRAME_CAPTURE_EVERY = '0.5'
python tools/runtime/run_native.py --max-frames 1200 --timeout 40 --stdout private/scratch/diag/boot_review/out.txt --stderr private/scratch/diag/boot_review/err.txt
```

This command captures the observed behavior; it is not yet a pass/fail comparison against the PS2.

## Launcher

The owner wants a native-port launcher with room for additional options. The current `run_game.bat` launches the configured GPU runner; it is not a graphical settings launcher. The current GPU runner reads keyboard overrides from its adjacent `game.ini`; keyboard and controller configuration need to be exposed and validated, including gameplay with an actual joystick.

- **Controls:** let players configure keyboard or joystick input. Define player assignment, device handling and the supported mapping interface against the current runtime; retain the single per-frame input seam needed for rollback.
- **Autosave notice:** offer a configurable automatic skip, enabled by default, preferably without displaying the PS2 memory-card notice, while preserving actual save loading and error handling. Verify existing, missing and invalid saves; do not assume hiding the picture also completes save initialization.
- **Unlocks:** offer an optional cheat to enable all locked characters. Verify which unlock flags are supported, that disabling it preserves ordinary progression, and that the setting is represented in synchronized simulation state as required by ADR 0004. The mechanism remains to be established; do not ship game-derived data.
- **Side art:** initially use a subtle color gradient in the unused area beside the 4:3 image on widescreen displays. Later, allow gallery artwork extracted locally from the user's disc. Preserve the game's aspect ratio and allow the player to disable the art. Extracted artwork remains under `private/` and must never be committed or distributed with the project.

Settings should only be presented as working once connected to the runtime and verified.

## Color Edit and external customizations

The owner also wants the PS2 Release's Color Edit behavior investigated so character customizations can eventually be injected from external files. This is a research goal; neither external-file support nor the Color Edit data format has been established.

The project already records that Color Edit is available with Arranged on or off and that fighter rendering uses palette textures. Those facts do not establish where an edit is stored, how it is applied, or whether every desired customization can be represented as a palette.

- In the Reference Emulator, create a controlled edit for one character and compare behavior before and after saving, restarting, selecting the character, and entering a fight. Repeat with a separate save to establish persistence and selection behavior without risking the player's original save.
- Trace the edit from its saved representation to the active character and renderer. Determine supported editable regions, color representation, limits and how multiple characters or players interact; distinguish observed behavior from assumptions.
- Evaluate import through the game's normal save/load path versus a runtime override. Choose a seam only after testing persistence, character selection, existing saves and rollback determinism; do not assume either approach is safe or sufficient in advance.
- Propose a documented, validated external format and an import workflow, including clear errors, backups or reversible operation, and handling for incompatible files. Keep the intended scope open: confirm whether external customizations mean Color Edit palettes only or broader visual modifications.
- Validate a known user-created customization in the selection screen and in a fight, then restart and check the intended persistence. Test malformed and incompatible inputs and confirm they do not corrupt existing saves.

Use the user's own disc and local copies of saves. Game-derived assets, dumps and captures stay under `private/`; synthetic examples and independently created format tooling can be tracked only if they contain no game data.
