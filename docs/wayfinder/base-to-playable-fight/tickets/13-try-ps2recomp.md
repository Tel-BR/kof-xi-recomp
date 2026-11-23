---
id: 13
title: Try PS2Recomp on the PS2 executable
type: task
status: open
assignee: 
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
