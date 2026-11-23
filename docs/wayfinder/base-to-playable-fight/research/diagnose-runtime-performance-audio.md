# Diagnose the runtime's speed and missing audio

_PT-BR: diagnóstico da lentidão e da falta de som do runtime. Cada seção traz o inglês primeiro e o português logo depois._

Measured on 2026-11-22 on the owner's machine (Intel Xeon E5-2640 v3, 8 cores / 16 threads), with the build that reaches the menus: PS2Recomp commit `e563698` plus local changes, Release `-O3` with ThinLTO, clang/MinGW. Counts, addresses and outcomes only; no disassembly, generated code or game data leaves `private/`.

_PT-BR: medido em 22/11/2026 na máquina do dono, com o build que chega aos menus (PS2Recomp `e563698` com mudanças locais, Release `-O3` com ThinLTO). Só contagens, endereços e resultados._

## Feedback loop

The game runs headless for 30 s and the runtime's `[heartbeat]` line gives the emulated vsync count each second; the loop reports the median vsyncs per second once the game has started its five threads. Real speed is 60. The script lives in `private/scratch/diag/run_probe.ps1` (git-ignored) and prints `GREEN` at 57 or more.

_PT-BR: o jogo roda sem janela por 30 s e a linha `[heartbeat]` do runtime dá quantos vsyncs emulados houve em cada segundo; o loop mostra a mediana depois que o jogo cria suas 5 threads. Velocidade real é 60._

## Measurements

| Scenario | Median vsyncs/s |
| --- | --- |
| Boot (one EE thread) | 60 |
| After the game starts its threads, as built | 14–16 |
| Same, with the frame limiter off | 16 |
| IOP fixes simulated (see below) | 25–26 |
| Same, with the frame limiter off | 26 |

- **Everything runs on one host thread.** The recompiled EE code, the IOP interpreter and the GS rasteriser run one after another on the same thread: one core at 100%, the other 15 idle. The GPU only displays the finished picture.
- **Where that thread's time goes, as built** (about 9,000 samples): IOP interpreter about 55–60%, software GS rasteriser (`GSCpuBackend`) about 35%, recompiled game code under 1%. Logging does not appear.

_PT-BR: tudo roda numa única thread do PC (código do jogo, IOP e GS, um depois do outro): um núcleo a 100% e 15 parados; a placa de vídeo só exibe a imagem pronta. Do tempo dessa thread, ~55–60% vão para o IOP interpretado, ~35% para o GS desenhado pela CPU e menos de 1% para o código do jogo. Os logs não aparecem._

## Cause 1: the IOP never idles

The IOP executes one interpreted instruction for every IOP cycle; it is never idle. Two faults, both around the CRI ADX driver (`CRI_ADXI.IRX`, loaded seventh at IOP `0x50E00`):

1. **Error trap.** The driver's stream-output setup (`PSM_Create`) fails at its ring-buffer step (`PSMTBF_Create`). The driver then logs `ioprna_create_rmt: can't create PSM` and enters a deliberate jump-to-self at IOP `0x52104`, which the interpreter spins through until its instruction budget runs out (16 times in 30 s).
2. **SPU2 DMA completes 384 times too early.** With no SPU2, `IopMemory::writeHardware32` completes a sound DMA after `words × 2` IOP cycles; playback at 48 kHz would take `words × 768`. LIBSD's transfer-complete handler (IOP `0x4BDEC`) then runs about 33,000 times per second instead of about 90, and each run wakes the ADX thread, whose 64-channel service routine (IOP `0x571C4`) keeps the IOP busy.

**Experiment:** with the trap ended and sound DMA timed at playback speed (temporary probe, since removed), the IOP went almost idle (under 20 million instructions in a whole 30 s run) and the game rose from about 13 to **25–26 vsyncs/s**.

_PT-BR: o IOP nunca fica ocioso. (1) A criação do buffer de saída do CRI ADX falha (`PSMTBF_Create`), e o driver entra num laço infinito proposital em `0x52104`, que o interpretador executa até esgotar o orçamento. (2) Sem SPU2, a DMA de som é dada como concluída em `palavras × 2` ciclos, em vez de `palavras × 768`; o tratador do LIBSD em `0x4BDEC` roda ~33 mil vezes por segundo em vez de ~90 e mantém a thread do ADX acordada. Com uma sonda temporária que encerrou o laço e pôs a DMA no tempo real, o IOP quase parou e o jogo foi de ~13 para 25–26 vsyncs/s._

## Cause 2: the GS is drawn by the CPU

After the IOP experiment, about 63% of the busy thread's time is `GSCpuBackend` (`WritePixel`, `SampleTexture`, `Submit`) and `GSMem` reads and writes. PS2Recomp at `e563698` has **only** this software backend (`ps2xRuntime/src/lib/gs/gs_cpu_backend.cpp`); there is no Vulkan or Direct3D GS renderer in it.

_PT-BR: depois do experimento do IOP, ~63% do tempo da thread é o `GSCpuBackend` desenhando pixel a pixel. O PS2Recomp no `e563698` só tem esse backend de software; não existe renderizador de GS em Vulkan ou Direct3D nele._

## Audio

- **The SPU2 is not emulated.** `ps2xIOP` stores SPU2 register writes in a table and nothing produces sound from them. The generic LIBSD service only forwards HLE RPCs, and the PS2 Release loads the real `LIBSD.IRX`, `SDRDRV.IRX` and `CRI_ADXI.IRX` instead.
- Other ports on PS2Recomp got CRI ADX audio by adding an SPU2 to the IOP (Persona 3 FES, the PS2Recomp-Fixer fork) or by moving CRI's PCM output to the host (Shinobi).

_PT-BR: o SPU2 não é emulado: as escritas nos registradores só ficam guardadas numa tabela. Outros ports sobre o PS2Recomp só tiveram som de CRI ADX adicionando um SPU2 no IOP ou desviando a saída PCM do CRI para o PC._

## Build settings

Release `-O3` with ThinLTO is correct. Upstream's defaults leave `PS2X_ENABLE_RUNTIME_LOGS`, `PS2X_ENABLE_AGRESSIVE_LOGS`, `PS2X_ENABLE_IOP_RPC_TRACE` and `PS2X_ENABLE_DEBUG_UI` on; they should be off for play builds, but they do not explain the slowness.

_PT-BR: Release `-O3` com ThinLTO está certo. Os logs e a interface de debug vêm ligados por padrão no PS2Recomp; devem ser desligados para jogar, mas não explicam a lentidão._

## Other findings

- **`vfprintf` stub breaks string formatting.** The game function at `0x121580` is replaced by a host `vfprintf` that only accepts host file handles. The game's C library formats strings (`sprintf`-style) through a temporary FILE on the stack, so those calls fail and log `vfprintf error: Invalid file handle` every frame (the handle seen, `0x1F7FD30`, is on thread 1's stack). Likely fix: let the recompiled function run instead of the stub.
- **A second limiter remains.** With the IOP fixed and the limiter off, the game stays at about 26 vsyncs/s while the busy thread waits about 31% of the time, so something besides CPU time holds it back. Unverified suspects: the local `EeScheduler` change that wakes EE thread 1 on every VBlank, and the game's `dbuff err!!` message (about 8 per second).
- **Inputs and memory card are still emulated.** Ticket 17 decided that `PADMAN` and `MCMAN`/`MCSERV` would be native; the runtime loads all three as emulated IRX modules.

_PT-BR: (1) A substituição de `vfprintf` em `0x121580` quebra a formatação de texto do jogo, que usa um FILE temporário na pilha; o erro aparece a cada quadro. (2) Sobra outro limitador: mesmo com o IOP resolvido e sem limitador de FPS, o jogo fica em ~26 com a thread parada ~31% do tempo; suspeitos não verificados: a mudança local no `EeScheduler` que acorda a thread 1 a cada VBlank e a mensagem `dbuff err!!`. (3) Controle e memory card continuam emulados, embora o ticket 17 tenha decidido torná-los nativos._

## Sources

- [PS2Recomp-Fixer](https://github.com/w1284603830/PS2Recomp-Fixer/): fork of `ran-j/PS2Recomp` at `eb8688b` with PCSX2's hardware GS (DX11/12), SPU2, threaded IOP; GPL-3.0.
- [p3fes-recompiled](https://github.com/ppkkkkk/p3fes-recompiled): CRI ADX over an SPU2 added to `ps2xIOP`.
- [Shinobi-PS2-Recomp issue #2](https://github.com/TheRealAfsan/Shinobi-PS2-Recomp/issues/2): CRI RNA output played on the host.
- [holyland issue #6](https://github.com/Voicedrew11/holyland/issues/6): "No audio: SPU2 is not emulated".
- [BT3-Recomp](https://github.com/z3xox/BT3-Recomp): its own OpenGL, Vulkan and paraLLEl-GS renderers on PS2Recomp.
