---
id: 17
title: Decide how the IOP side is reproduced
type: grilling
status: open
assignee:
blocked_by: [06, 15]
---

## Question

How does the port handle what the PS2 Release does on its I/O processor: sound (SPU2 and the CRI ADX middleware), controller input and disc reads? The disc carries 7 IOP modules (Sony SDK libraries plus CRI ADX) and Sony's IOP replacement image ([Inspect the code structure of each candidate release](08-inspect-code-structure.md)). Choose between running the original modules under emulation (as PS2Recomp does, with fallbacks) and replacing them with native code on the PC side (for example an ADX decoder and host audio, and host controller input), module by module. Weigh the chosen recompiler, the licence decision, and the rollback requirements: one input entry point, and no host time leaking into the simulation.

_PT-BR: como o port trata o que a versão de PS2 faz no processador de entrada e saída (IOP): som (SPU2 e o middleware CRI ADX), controle e leitura do disco? O disco tem 7 módulos de IOP (bibliotecas da Sony e o CRI ADX). Escolher, módulo a módulo, entre rodar os módulos originais emulados (como o PS2Recomp faz) e substituí-los por código nativo no PC (por exemplo, um decodificador de ADX e o controle do próprio PC). Pesar o recompilador escolhido, a licença e os requisitos de rollback: um único ponto de entrada dos controles e nenhum relógio do PC vazando para a simulação._
