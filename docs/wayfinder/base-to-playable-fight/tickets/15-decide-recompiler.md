---
id: 15
title: Decide the recompiler
type: grilling
status: open
assignee:
blocked_by: [13]
---

## Question

Which static recompiler turns the Base Version's R5900 code into native code: adopt PS2Recomp as it is, build on a fork of it, or write the project's own? Weigh what [Try PS2Recomp on the PS2 executable](13-try-ps2recomp.md) found, PS2Recomp's GPL-3.0 licence (adopting it makes the distributed port GPL-3.0), its float emulation and its runtime against the rollback requirements in [Survey how static recomps can support rollback netplay](03-rollback-on-static-recomp.md), and how function discovery will work on an executable without symbols.

_PT-BR: qual recompilador estático transforma o código R5900 da versão-base em código nativo: usar o PS2Recomp como está, partir de um fork dele ou escrever um próprio? Pesar o resultado do ticket 13, a licença GPL-3.0 do PS2Recomp (adotá-lo torna o port distribuído GPL-3.0), a emulação de ponto flutuante e o runtime dele diante dos requisitos de rollback do ticket 03, e como descobrir as funções num executável sem símbolos._
