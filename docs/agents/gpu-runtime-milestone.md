# GPU runtime milestone · 2026-11-26

The owner confirmed working graphics, keyboard controls and audible playback from the GPU runner. This branch records the launchers, runtime patches and generated-source repair tools. Private inputs, private build state and captures are intentionally local.

## Local rebuild

The installed build uses PS2Recomp-Fixer at `c5a71482dd99f1351bd1ac9d9549098645ddf12c`. Given the configured private checkout, keep `game.ini` alongside the Release runner and build `ps2EntryRunner` with `build_runtime.bat`.

For a new checkout, use the normal Fixer port setup with the user's own disc. Use the upstream `examples/generic_runner/main.cpp` as `third_party/src/PS2Recomp/ps2xRuntime/src/runner/main.cpp`. Apply the runtime patches from `tools/runtime/patches/` to the Fixer root. Apply `ps2recomp-fixer-gpu-port.patch` before `ps2recomp-fixer-replay.patch`. The GPU patch carries the GS changes and the opt-in scheduler workaround. The replay patch carries the runner's keyboard configuration, the .p2m2 reader, the VSync execution limit, and replay input for both libpad and SIO2. The two existing DMA and VU patches are independent of the replay.

Keep generated code, function registration tables and the revision-specific profile under `private/`. The installed milestone was built incrementally. A from-scratch game rebuild is still a separate verification step.

## Audio from local generation

- Configure the generator with the local symbol boundaries. Remove stubs for `sceSdRemoteInit`, `sceSdTransToIOP` and `sceSdRemote` so the EE SDK can bind and call the actual SDRDRV IOP service. When updating an older generated runner incrementally, install all three regenerated bodies and check that the scheduler continuation at `0x112320` is registered.
- Keep `sceSifAllocIopHeap` and `sceSifFreeIopHeap` paired through the host stub allocator. Remove confirmed speculative analyzer NOP patches for real data stores. In the installed build the CRI reply destination store at `0x201474`, work-size store at `0x1fcf48`, and teardown store at `0x1fd574` were restored. The latter must be restored in all generated copies. `tools/runtime/restore_ee_stores.py ELF RUNNER 0x201474 0x1fcf48 0x1fd574` reads the store encodings from the user's local ELF when repairing stale generated output.
- The current generator reads the correct COP1 `SQRT.S` source. Run `tools/runtime/upgrade_stale_runner.py` after importing older generated code. This fixes the wrong floating-point operand that destabilized the ADX predictor.

The corrected streaming PCM reached a raw correlation above 0.999999 on two channels against an independent ADX decode. The early track in the final mixer correlated at 0.985–0.990 across four measured stereo segments against the PCSX2 recording. The closed-loop mixer measured 47/47 active seconds against the 85% gate. The actual launcher cleared inherited mute and delivered 12 consecutive seconds to the Windows session before the owner confirmed listening.

## Replay integration evidence

The first replay implementation reached the requested end field but supplied input only to SIO2. The active KOF XI build uses the EE `scePadRead` stub and the native pad backend. The installed replay source supplies the same packets to that backend as well. The runtime trace records the emulated field used when each controller word changes. The main-menu, character-selection and fight checks use private presentation captures. The 1,000-field replay is an input and end-of-file smoke test. It ends early in boot.

The full Reference Scenario reached a fight and completed at VSync 11,782. All 726 controller-word transitions emitted in the trace matched the recording at their logged field and port. A late portion of the run logged guest `vfprintf` warnings. No full state-hash or frame-exact comparison with the Reference Emulator was performed. Four malformed or incompatible replay headers were rejected before opening a game window.

`build_runtime.bat` rebuilt the configured GPU checkout. The short replay finished at VSync 1,000 when launched through `run_replay.bat`. A synthetic two-port recording verified independent buttons, pressure values, a disconnected packet and end-of-file. The consolidated `run_game.bat` cleared an inherited mute and produced 12 consecutive seconds of Windows audio with a lowest one-second median of 0.215. The Python suite passed all 52 tests. All four runtime patches were applied to source copies from the pinned Fixer revision for a patch consistency check.
