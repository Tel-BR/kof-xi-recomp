---
id: 13
title: Try PS2Recomp on the PS2 executable
type: task
status: closed
assignee: claude
blocked_by: []
research: ../research/try-ps2recomp.md
---

## Question

How far does PS2Recomp get with the Base Version's executable as it stands? The executable has no symbols and was built with Metrowerks CodeWarrior, not GCC ([Inspect the code structure of each candidate release](08-inspect-code-structure.md)), so function and code-boundary discovery is the first unknown. AFK: on the owner's machine, run PS2Recomp's analyzer and recompiler on the US executable (SLUS-21687) and record only counts and outcomes: functions found against the ~1.3 MB of code, instructions or patterns it cannot handle, whether the output compiles, and how far the runtime gets (boots, reaches a menu, crashes, and where by address range). Note the PS2Recomp commit used. No disassembly, generated code or game data leaves `private/`.

_PT-BR: até onde o PS2Recomp chega com o executável da versão-base do jeito que ele é? O executável não tem símbolos e foi compilado com o Metrowerks CodeWarrior, então descobrir onde começa e termina cada função é a primeira incógnita. O agente roda o analisador e o recompilador do PS2Recomp no executável americano, na máquina do dono, e registra só contagens e resultados: funções achadas, instruções que a ferramenta não trata, se o código gerado compila e até onde o runtime chega. Anotar o commit do PS2Recomp usado. Nada de desmontagem, código gerado ou dados do jogo sai da pasta `private/`._

## Reopened (2026-11-22)

Reopened by the owner after a diagnosis of the build that reaches the menus ([research/diagnose-runtime-performance-audio.md](../research/diagnose-runtime-performance-audio.md)). The measurements below are not wrong, but the scope missed two things that later decisions relied on:

- **Speed was never measured.** The build that reaches the menus runs at 14–16 of 60 vsyncs per second, on one host thread.
- **Audio output was never checked.** "The ADX audio driver starts" means its startup messages appeared, not that sound plays. [Decide how the IOP side is reproduced](17-iop-approach.md) read it as working audio. In fact the SPU2 is not emulated and the ADX driver's output setup fails.

**To re-resolve:** record speed and audio with the feedback loop in the research note, and explain the second limiter it lists (about 26 vsyncs/s with the IOP fixed and the thread idle 31% of the time).

_PT-BR: reaberto pelo dono depois do diagnóstico do build que chega aos menus. As medições abaixo não estão erradas, mas faltaram duas coisas em que decisões posteriores se apoiaram: (1) a velocidade nunca foi medida (o build roda a 14–16 de 60 vsyncs por segundo, numa thread só); (2) a saída de áudio nunca foi conferida ("o driver ADX inicia" quer dizer que as mensagens de início apareceram, não que há som; o ticket 17 leu isso como áudio funcionando, mas o SPU2 não é emulado e a criação da saída do ADX falha). Para resolver de novo: registrar velocidade e áudio com o loop da nota de pesquisa e explicar o segundo limitador (~26 vsyncs/s com o IOP corrigido e a thread parada 31% do tempo)._

## Resolution (2026-11-21, reopened)

Full measurements: [research/try-ps2recomp.md](../research/try-ps2recomp.md). Counts and outcomes only. PS2Recomp commit `e5636981a1c9de368f6b71e819c3dc188dfedbf4` (2026-10-22), analyzer's built-in discovery (JAL scan plus the embedded SDK database); the Ghidra-export path the README recommends was not tried (Ghidra not installed). Built with clang/MinGW, which needed four small local workarounds; MSVC is not on the machine.

- **Functions found:** 3,458, with 3,434 in the code range (~1.5 MB from `0x100008` to `0x280830`); the SDK database recognised 552 library functions. A pointer scan suggests about **5,000 real functions**: of 964 code addresses stored as pointers, **921 (96%) were not found**. The JAL scan misses functions reached only through pointers.
- **Instructions it cannot handle:** 12,769, **all inside 18 "functions" in the data tail** (`0x280830`–`0x2F1400`), which is data decoded as code. **None in the real code**, including all MMI and VU0 macro instructions.
- **Does the output compile:** as is, 110 of 111 units compile with 0 errors, but the unit holding a ~100,000-line data-as-code function did not finish in 60 minutes. With only those 18 entries skipped, **everything compiles and links with 0 errors** in about 5 minutes.
- **How far the runtime gets:** **boots** (7 IOP modules load, the ADX audio driver starts) and drives the GS for about 8 seconds (439 frames), then makes an indirect call to `0x1FB188`, a function start the analyzer never found, and **hangs there**: no crash, **no menu** in 120 s. Without a disc image it stalls earlier, because the game reads raw sectors.
- **Takeaway for [Decide the recompiler](15-decide-recompiler.md):** translation and compilation are not the obstacle; **complete function boundaries and a clean code/data split are**.

_PT-BR: PS2Recomp no commit `e5636981…`, com a descoberta de funções embutida do analisador (a exportação do Ghidra, que o README recomenda, não foi testada). O analisador achou 3.458 funções, mas o executável deve ter umas 5.000: das 964 funções guardadas como ponteiros, 921 (96%) ficaram de fora. As 12.769 instruções não tratadas estão todas em 18 "funções" que são dados lidos como código, no fim da imagem; no código real, nenhuma. Pulando essas 18, tudo compila e linka sem erro. O jogo inicia, carrega os módulos do IOP e o driver de áudio, desenha por uns 8 segundos e então trava numa chamada para uma função que o analisador não achou; não fecha e não chega a menu. Para o ticket 15: o problema não é traduzir nem compilar, é achar todas as funções e separar código de dados._

## Resolution (2026-11-22)

Re-resolved after the reopening. Details: [research/diagnose-runtime-performance-audio.md](../research/diagnose-runtime-performance-audio.md), section "Second pass for ticket 13"; summary added to [research/try-ps2recomp.md](../research/try-ps2recomp.md). Same build as the diagnosis: PS2Recomp `e563698` plus the uncommitted local changes in `private/tools/PS2Recomp` that get it to the menus (EE scheduler and kernel stubs, pad and memory card, and the function table generated from the Ghidra export), Release `-O3` with ThinLTO.

- **Feedback loop, now in the repo:** `tools/runtime/run_native.py --headless --timeout 30 --stdout <file> --stderr <file>` (add `--unthrottled`, or `--exe` for a diagnostic build), then `tools/runtime/speed_report.py <stdout> <stderr>`, which prints the median vsyncs per second, the count of CRI ADX output failures and `GREEN` at 57 or more.
- **Speed:** as built, **17** of 60 vsyncs per second, with the frame limiter on or off. With the IOP's two faults removed in a temporary probe, **31–35** (limiter on or off makes no real difference).
- **Audio:** **none.** The CRI ADX output setup fails 16 times per 30 s run, the host audio backend receives 0 calls, and the SPU2 is not emulated.
- **The second limiter was the old measuring script.** It captured output through PowerShell's `Start-Process` redirection, under which every log write blocked: 30% of the game thread's samples were inside `NtWriteFile`, against 1% when writing straight to files (24 against 34 vsyncs/s on the same probe build). The scheduler itself never waits on host time during play (0% idle wait and 0% frame pacing), so neither suspect (the VBlank wake of EE thread 1, `dbuff err!!`) holds.
- **What is left is the GS.** With the IOP fixed, the software GS takes 87–92% of the busy thread (about 27 ms per vsync, a ceiling near 37 vsyncs/s), the IOP about 3%, the rest 5–9%. The recompiled game code is light: about 98% of EE cycles pass with every EE thread waiting.
- **Inputs for the reopened tickets (not decisions):** for [16](16-gs-vu1-approach.md), the current CPU GS needs about 27 ms per vsync against a 16.7 ms budget; for [17](17-iop-approach.md), sound needs the ADX output fixed, the sound DMA timed correctly and somewhere for the sound to go (an SPU2, or CRI's PCM output played on the host, as other ports did). Play builds should turn the log options off: through a console they may still cost speed (not measured).

_PT-BR: resolvido de novo depois da reabertura. Loop de medição agora no repositório (`run_native.py` gravando a saída em arquivo e `speed_report.py`). Velocidade: 17 de 60 vsyncs por segundo como está; sem os dois defeitos do IOP, 31–35. Áudio: nenhum (a saída do CRI ADX falha, o áudio do PC não recebe nada, o SPU2 não é emulado). O "segundo limitador" era o próprio script de medição antigo: o redirecionamento do `Start-Process` fazia cada escrita de log travar (30% das amostras em `NtWriteFile`, contra 1% gravando direto em arquivo); o escalonador nunca espera tempo real durante o jogo, então nenhum dos suspeitos se confirma. O que sobra é o GS por software: 87–92% da thread, ~27 ms por vsync, teto perto de 37 vsyncs/s; o código do jogo é leve. Dados para os tickets reabertos (não são decisões): no 16, o GS atual leva ~27 ms por vsync para um orçamento de 16,7 ms; no 17, para haver som é preciso corrigir a saída do ADX, acertar o tempo da DMA de som e ter para onde mandar o som (um SPU2, ou o PCM do CRI tocado no PC, como outros ports fizeram). Builds de jogo devem desligar os logs._
