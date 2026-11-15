# What PCSX2 v2.8.2 offers as a Reference Emulator

_PT-BR: o que o PCSX2 v2.8.2 oferece como emulador de referência. Levantamento de fatos para o ticket 07; sem dados do jogo. Itens sem evidência estão marcados "NOT CONFIRMED"._

Facts gathered on 2026-11-15 from the PCSX2 source at tag `v2.8.2` (GitHub) and the official docs. No disc, executable, dump or savestate of the game was read. The local copy in `private/scratch/pcsx2src` holds only five loose files (`GSDump.cpp/.h`, `GSDumpReplayer.cpp`, `GSState.cpp`, `SaveState.cpp`) with no version marker, so it is evidence of formats only.

## Input recording

- File `.p2m2`: 561-byte header (version byte, emulator version, author, game name, total frames, undo count, savestate flag), then 36 bytes per frame (two pads, 18 bytes each). Pad data only.
- Start modes: `POWER_ON` (does a VM reset, not a full boot; the code carries a TODO) or `FROM_SAVESTATE` (loads `<name>_SaveState.p2s` beside the recording).
- While recording, the CDVD real-time clock is pinned to 2020-03-04 00:00:00. Identical replay across runs is **NOT CONFIRMED**; the player only warns when the game differs, and does not compare emulator versions.
- At the end of a recording the VM **pauses**, a natural frame-exact checkpoint.
- No command-line option to record or play: menu only.

## Guest state

- Savestate `.p2s` is a ZIP with `eeMemory.bin`, `iopMemory.bin`, `Scratchpad.bin`, `vu0/vu1Memory.bin`, `vu0/vu1MicroMem.bin`, `eeHwRegs.bin`, `iopHwRegs.bin`, `SPU2.bin`, `GS.bin`, `PAD.bin`, `USB.bin` and `PCSX2 Internal Structures.dat` (CPU registers, own format). Hashable offline. Savestates from another major version are rejected.
- Command line (Qt): `-batch`, `-nogui`, `-statefile`, `-state`, `-disc`, `-bios`, `-fastboot/-slowboot`, `-portable`, `-logfile`, `-testconfig`. **No** exit-after-N-frames, no input-recording options, no dump options.
- PINE (socket, default 28011): read/write RAM (8-64 bit), save/load state by slot, status, title, CRC. No frame advance or pause: NOT CONFIRMED.

## GS dumps

- Hotkeys only: single frame, or multi-frame while held. Formats `.gs`, `.gs.xz`, `.gs.zst` (header, then GIF packets for paths 1/2/3, vsync, registers).
- `pcsx2-gsrunner` replays dumps headless (`-surfaceless`, renderer `sw`/`dx11`/`dx12`/`gl`/`vulkan`) and writes PNGs; it computes no hashes and does not run the game.
- Determinism of the software renderer: NOT CONFIRMED.

## Audio

- A/V capture through FFmpeg (video capture hotkey); audio-only capture NOT CONFIRMED.
- SPU2 logging and wave dumps exist only under `PCSX2_DEVBUILD`, not in the portable release.

## Sources of non-determinism (from code)

- RTC read from the host clock once at reset unless set manually (`ManuallySetRealTimeClock`); fixed while input recording.
- EE timing is cycle-driven, not host-clock-driven; the frame limiter is separate.
- Settings that can change results: MTVU (`vuThread`), `EECycleRate`, `EECycleSkip`, fast boot, EE/VU floating-point rounding and clamping options, BIOS dump. Which combination is reproducible: NOT CONFIRMED.

## Consequence for the ticket

No fully scripted capture exists in the release build: scenarios must be recorded once through the menu, and frame-exact checkpoints need a trick (truncated copies of a recording pause at the chosen frame) that has to be proven in a prototype.

_PT-BR: o release do PCSX2 não tem captura totalmente automatizada (nada de gravar/reproduzir por linha de comando, nem sair após N quadros). Cada cenário é gravado uma vez pelo menu; pontos de checagem exatos dependem de um truque (cópias truncadas do replay, que pausam no quadro escolhido) a ser provado num protótipo._
