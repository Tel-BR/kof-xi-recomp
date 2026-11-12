---
id: 13
title: Try PS2Recomp on the PS2 executable
type: task
status: open
assignee:
blocked_by: []
---

## Question

How far does PS2Recomp get with the Base Version's executable as it stands? The executable has no symbols and was built with Metrowerks CodeWarrior, not GCC ([Inspect the code structure of each candidate release](08-inspect-code-structure.md)), so function and code-boundary discovery is the first unknown. AFK: on the owner's machine, run PS2Recomp's analyzer and recompiler on the US executable (SLUS-21687) and record only counts and outcomes: functions found against the ~1.3 MB of code, instructions or patterns it cannot handle, whether the output compiles, and how far the runtime gets (boots, reaches a menu, crashes, and where by address range). Note the PS2Recomp commit used. No disassembly, generated code or game data leaves `private/`.

_PT-BR: até onde o PS2Recomp chega com o executável da versão-base do jeito que ele é? O executável não tem símbolos e foi compilado com o Metrowerks CodeWarrior, então descobrir onde começa e termina cada função é a primeira incógnita. O agente roda o analisador e o recompilador do PS2Recomp no executável americano, na máquina do dono, e registra só contagens e resultados: funções achadas, instruções que a ferramenta não trata, se o código gerado compila e até onde o runtime chega. Anotar o commit do PS2Recomp usado. Nada de desmontagem, código gerado ou dados do jogo sai da pasta `private/`._
