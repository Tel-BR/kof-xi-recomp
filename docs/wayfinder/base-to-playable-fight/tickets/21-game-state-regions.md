---
id: 21
title: Decide which memory regions count as game state
type: grilling
status: open
assignee:
blocked_by: [15, 19]
---

## Question

Which memory areas does the verification compare, and which does it ignore? The decision in [Decide how correctness is verified against a reference emulator](07-verification-oracle.md) is that only areas that belong to the game count, and BIOS/kernel areas are excluded. Choose the concrete list (main RAM ranges, scratchpad, and whether sound or video memory are in), using the noise map from [Prototype the reference capture on one scenario](19-prototype-reference-capture.md) and the chosen recompiler from [Decide the recompiler](15-decide-recompiler.md). The same list is the starting point for what rollback must save and restore, so it should be reconciled with the rollback requirements in [Survey how static recomps can support rollback netplay](03-rollback-on-static-recomp.md).

_PT-BR: quais áreas de memória a verificação compara e quais ignora? A decisão do ticket 07 é que só contam as áreas do jogo, sem BIOS/kernel. Escolher a lista concreta (faixas da RAM principal, scratchpad, e se memória de som ou de vídeo entram), usando o mapa de ruído do ticket 19 e o recompilador escolhido no ticket 15. A mesma lista é ponto de partida para o que o rollback precisa salvar e restaurar, então deve ser conciliada com os requisitos de rollback do ticket 03._
