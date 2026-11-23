# Diagnose the runtime's speed and missing audio

_PT-BR: diagnóstico da lentidão e da falta de som do runtime. Cada seção traz o inglês primeiro e o português logo depois._

Measured on 2026-11-22 on the owner's machine (Intel Xeon E5-2640 v3, 8 cores / 16 threads), with the build that reaches the menus: PS2Recomp commit `e563698` plus local changes, Release `-O3` with ThinLTO, clang/MinGW. Counts, addresses and outcomes only; no disassembly, generated code or game data leaves `private/`.

_PT-BR: medido em 22/11/2026 na máquina do dono, com o build que chega aos menus (PS2Recomp `e563698` com mudanças locais, Release `-O3` com ThinLTO). Só contagens, endereços e resultados._

## Feedback loop

The game runs headless for 30 s and the runtime's `[heartbeat]` line gives the emulated vsync count each second; the loop reports the median vsyncs per second once the game has started its five threads. Real speed is 60. The script lives in `private/scratch/diag/run_probe.ps1` (git-ignored) and prints `GREEN` at 57 or more.

**Corrected in the second pass (below):** that script captured the game's output through PowerShell's `Start-Process` redirection, which made every log write block and, with the IOP fixed, cost about 30% of the speed. The loop is now in the repo and writes the output straight to files:

```
python tools/runtime/run_native.py --headless --timeout 30 --stdout private/scratch/run_out.txt --stderr private/scratch/run_err.txt
python tools/runtime/speed_report.py private/scratch/run_out.txt private/scratch/run_err.txt
```

Add `--unthrottled` to turn the frame limiter off and `--exe <path>` to measure a diagnostic build. The report gives the median vsyncs per second, the count of CRI ADX output failures (the audio signal) and `GREEN` at 57 or more.

_PT-BR: o jogo roda sem janela por 30 s e a linha `[heartbeat]` do runtime dá quantos vsyncs emulados houve em cada segundo; o loop mostra a mediana depois que o jogo cria suas 5 threads. Velocidade real é 60._

_**Corrigido na segunda passada (abaixo):** aquele script capturava a saída do jogo pelo redirecionamento do `Start-Process` do PowerShell, que fazia cada escrita de log travar e, com o IOP corrigido, custava cerca de 30% da velocidade. O loop agora está no repositório e grava a saída direto em arquivo: `tools/runtime/run_native.py --headless --timeout 30 --stdout … --stderr …` e depois `tools/runtime/speed_report.py` com os dois arquivos. `--unthrottled` desliga o limitador de quadros e `--exe` mede um build de diagnóstico. O relatório dá a mediana de vsyncs por segundo, quantas vezes a saída do CRI ADX falhou (o sinal de áudio) e `GREEN` a partir de 57._

## Measurements

| Scenario | Median vsyncs/s |
| --- | --- |
| Boot (one EE thread) | 60 |
| After the game starts its threads, as built | 14–16 |
| Same, with the frame limiter off | 16 |
| IOP fixes simulated (see below) | 25–26 |
| Same, with the frame limiter off | 26 |

- **Everything runs on one host thread.** The recompiled EE code, the IOP interpreter and the GS rasteriser run one after another on the same thread: one core at 100%, the other 15 idle. The GPU only displays the finished picture.
- **Where that thread's time goes, as built** (about 9,000 samples): IOP interpreter about 55–60%, software GS rasteriser (`GSCpuBackend`) about 35%, recompiled game code under 1%. Logging does not appear among the program's own functions, but see the second pass: those samples were taken with the old loop, whose log writes were counted as waiting. Its cost was measured on the IOP probe (30% of the thread); as built it matters less, because the IOP dominates.

_PT-BR: tudo roda numa única thread do PC (código do jogo, IOP e GS, um depois do outro): um núcleo a 100% e 15 parados; a placa de vídeo só exibe a imagem pronta. Do tempo dessa thread, ~55–60% vão para o IOP interpretado, ~35% para o GS desenhado pela CPU e menos de 1% para o código do jogo. Os logs não aparecem entre as funções do programa, mas veja a segunda passada: essas amostras foram tiradas com o loop antigo, cujas escritas de log contavam como espera. O custo foi medido na sonda do IOP (30% da thread); como está, pesa menos, porque o IOP domina._

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

Release `-O3` with ThinLTO is correct. Upstream's defaults leave `PS2X_ENABLE_RUNTIME_LOGS`, `PS2X_ENABLE_AGRESSIVE_LOGS`, `PS2X_ENABLE_IOP_RPC_TRACE` and `PS2X_ENABLE_DEBUG_UI` on; they should be off for play builds. With output written straight to a file they cost little (about 1% of the thread); through a pipe or a console they can cost much more (see the second pass).

_PT-BR: Release `-O3` com ThinLTO está certo. Os logs e a interface de debug vêm ligados por padrão no PS2Recomp; devem ser desligados para jogar. Gravando direto em arquivo custam pouco (~1% da thread); por um pipe ou pelo console podem custar bem mais (veja a segunda passada)._

## Other findings

- **`vfprintf` stub breaks string formatting.** The game function at `0x121580` is replaced by a host `vfprintf` that only accepts host file handles. The game's C library formats strings (`sprintf`-style) through a temporary FILE on the stack, so those calls fail and log `vfprintf error: Invalid file handle` every frame (the handle seen, `0x1F7FD30`, is on thread 1's stack). Likely fix: let the recompiled function run instead of the stub.
- **A second limiter remains.** With the IOP fixed and the limiter off, the game stays at about 26 vsyncs/s while the busy thread waits about 31% of the time, so something besides CPU time holds it back. Unverified suspects: the local `EeScheduler` change that wakes EE thread 1 on every VBlank, and the game's `dbuff err!!` message (about 8 per second). **Explained in the second pass:** the wait was the thread writing logs through the old loop's redirection, not the scheduler.
- **Inputs and memory card are still emulated.** Ticket 17 decided that `PADMAN` and `MCMAN`/`MCSERV` would be native; the runtime loads all three as emulated IRX modules.

_PT-BR: (1) A substituição de `vfprintf` em `0x121580` quebra a formatação de texto do jogo, que usa um FILE temporário na pilha; o erro aparece a cada quadro. (2) Sobra outro limitador: mesmo com o IOP resolvido e sem limitador de FPS, o jogo fica em ~26 com a thread parada ~31% do tempo; suspeitos não verificados: a mudança local no `EeScheduler` que acorda a thread 1 a cada VBlank e a mensagem `dbuff err!!`. **Explicado na segunda passada:** a espera era a thread gravando logs pelo redirecionamento do loop antigo, não o escalonador. (3) Controle e memory card continuam emulados, embora o ticket 17 tenha decidido torná-los nativos._

## Second pass for ticket 13 (2026-11-22)

Same machine and day, same PS2Recomp tree, re-measured with the corrected loop above. The IOP fixes were applied again as a temporary probe (end the jump-to-self at IOP `0x52104`; time sound DMA at `words × 768`), together with temporary counters: host time spent in the scheduler's waits (idle and frame pacing), in the IOP interpreter, in the GS reached through the GIF path and in VU1, plus calls into the host audio backend. All of it was removed afterwards; the PS2Recomp sources are back as they were.

_PT-BR: mesma máquina, mesmo dia, mesma árvore do PS2Recomp, medido de novo com o loop corrigido. As correções do IOP voltaram como sonda temporária (encerrar o laço infinito em `0x52104`; DMA de som em `palavras × 768`), junto com contadores temporários de tempo nas esperas do escalonador, no IOP, no GS e no VU1, e de chamadas ao áudio do PC. Tudo foi removido depois; o PS2Recomp voltou ao que era._

### Speed

| Build | Old loop (`Start-Process`) | Corrected loop (files) |
| --- | --- | --- |
| As built, limiter on | 14–16 | **17** |
| As built, limiter off | 16 | **17** |
| IOP probe, limiter on | 24–26 | **33–35** |
| IOP probe, limiter off | 26 | **31–33** |

Median vsyncs per second once the game's five threads exist; real speed is 60. As built, the IOP still dominates, so the loop changes little; with the IOP fixed, the old loop alone cost about 30% (24 against 34 on the same build, measured back to back). Removing 30% of blocking time from 24 predicts 34, which is what the corrected loop gives. Limiter on or off makes no real difference: frame pacing never waits (below), and 31–35 is the spread between runs.

_PT-BR: mediana de vsyncs por segundo depois que o jogo cria as 5 threads (60 é a velocidade real). Como está, o IOP ainda domina e o loop muda pouco; com o IOP corrigido, só o loop antigo custava ~30% (24 contra 34 no mesmo build, medidos em seguida), exatamente o que se espera tirando 30% de tempo travado. Ligar ou desligar o limitador não muda nada de fato: ele nunca espera, e 31–35 é a variação entre rodadas._

### The second limiter, explained

- **The 31% "wait" was log writing.** Sampling the game thread with the old loop put **30% of its samples inside `NtWriteFile`**, the Windows call that writes to a file or pipe; earlier profiles grouped it as waiting because it is outside the program's own code. With the corrected loop the same probe spends **1%** there. The output is small (about 100 lines per second, mostly `[sceSifSetDma]` traces on stderr, `[run:tick]` and GS traces, the `vfprintf error` line and `dbuff err!!`), but every write blocked under the old redirection.
- **The scheduler never waits on host time in game.** The counters gave 0% for both the idle wait and frame pacing during play, with the limiter on or off. So neither suspect holds: the `EeScheduler` change that wakes thread 1 on every VBlank adds no waiting, and `dbuff err!!` (about 4 per second in these runs, against about 8 counted in the first pass) is just one of the log lines; what it means for the game is still unknown.
- **The game itself is light.** By the runtime's own cycle accounting, about 160 million EE cycles pass per real second at ~33 vsyncs/s, and about 98% of them are skipped forward while every EE thread waits. The recompiled game code is not what limits speed.
- **What is left is the GS.** With the IOP fixed and the corrected loop, the software GS reached through the GIF path takes **87–92%** of the busy thread, the IOP interpreter about **3%**, everything else about 5–9% (VU1: 0%, matching ticket 14). That is about 27 ms of GS work per vsync against a 16.7 ms budget: the GS alone caps the game at about 37 vsyncs/s. There is no other limiter.
- **Smaller costs worth knowing.** About 13% of the busy thread's samples are in Windows lock routines (`AcquireSRWLockExclusive`/`ReleaseSRWLockExclusive`, the body of `std::mutex`) and about 5% in `QueryPerformanceCounter` (clock reads). These samples fall inside the buckets above (most likely the GS, which dominates), not on top of them; which code calls them was not traced. They are worth checking when the GS is replaced, but they are not a separate limiter.
- **Interactive play may still pay for logs.** `run_game.bat` starts `run_native.py` without `--stdout`, so the logs go to a console window, which is usually slower than a file. Not measured; turning the log options off in play builds removes the risk.

_PT-BR: (1) A "espera" de 31% era escrita de log: com o loop antigo, 30% das amostras da thread estavam em `NtWriteFile`, a chamada do Windows que grava em arquivo ou pipe; com o loop corrigido, 1%. A saída é pequena (~100 linhas por segundo), mas cada escrita travava com aquele redirecionamento. (2) O escalonador nunca espera tempo real durante o jogo (0% nas duas esperas), então nenhum dos dois suspeitos se confirma: acordar a thread 1 a cada VBlank não cria espera, e o `dbuff err!!` (~4 por segundo) é só mais uma linha de log, cujo significado para o jogo continua desconhecido. (3) O jogo em si é leve: ~98% dos ciclos da EE passam com todas as threads esperando. (4) O que sobra é o GS: com o IOP corrigido, o GS por software leva 87–92% da thread, o IOP ~3% e o resto 5–9% (VU1 0%). São ~27 ms de GS por vsync para um orçamento de 16,7 ms; só o GS já limita o jogo a ~37 vsyncs/s. Não há outro limitador. (5) Custos menores: ~13% das amostras em travas do Windows (o `std::mutex`) e ~5% lendo o relógio; essas amostras estão dentro das parcelas acima (provavelmente no GS), não somadas a elas; quem chama não foi rastreado. (6) Jogando pelo `run_game.bat`, os logs vão para a janela de console, que costuma ser mais lenta que arquivo; não medido, e desligar os logs no build de jogo elimina o risco._

### Audio

- **No sound.** In every 30 s run (as built and with the probe) the CRI ADX driver logs its output-setup failure (`can't create PSM`) **16 times**, and the host audio backend received **0 calls** and played **0 sounds**: with the real `LIBSD.IRX` loaded, nothing reaches it. The SPU2 is still not emulated, so even a working ADX driver would have nowhere to send sound.
- In these automated headless runs raylib also failed to open the playback device (`Failed to initialize playback device`) although the machine has working audio devices; whether it opens in an interactive run was not checked. It does not change the result, since nothing is sent to it.

_PT-BR: sem som. Em toda rodada de 30 s (como está e com a sonda) o driver CRI ADX registra 16 vezes a falha ao criar sua saída, e o áudio do PC recebeu 0 chamadas e tocou 0 sons: com o `LIBSD.IRX` real carregado, nada chega até ele. O SPU2 continua sem emulação, então mesmo um driver ADX funcionando não teria para onde mandar o som. Nestas rodadas automáticas sem janela o raylib também não conseguiu abrir o dispositivo de áudio, embora a máquina tenha placas de som funcionando; numa rodada interativa não foi conferido. Isso não muda o resultado, porque nada é enviado a ele._

## Sources

- [PS2Recomp-Fixer](https://github.com/w1284603830/PS2Recomp-Fixer/): fork of `ran-j/PS2Recomp` at `eb8688b` with PCSX2's hardware GS (DX11/12), SPU2, threaded IOP; GPL-3.0.
- [p3fes-recompiled](https://github.com/ppkkkkk/p3fes-recompiled): CRI ADX over an SPU2 added to `ps2xIOP`.
- [Shinobi-PS2-Recomp issue #2](https://github.com/TheRealAfsan/Shinobi-PS2-Recomp/issues/2): CRI RNA output played on the host.
- [holyland issue #6](https://github.com/Voicedrew11/holyland/issues/6): "No audio: SPU2 is not emulated".
- [BT3-Recomp](https://github.com/z3xox/BT3-Recomp): its own OpenGL, Vulkan and paraLLEl-GS renderers on PS2Recomp.
