---
id: 03
title: Survey how static recomps can support rollback netplay
type: research
status: open
assignee:
blocked_by: []
research: ../research/rollback-on-static-recomp.md
---

## Question

What must a static recomp guarantee so rollback netplay can be added later? Survey what rollback requires (per-frame save/restore of the full simulation state, determinism, input decoupling), how emulators and ports achieved it (FBNeo/Fightcade, Flycast GGPO, RetroArch, decomps), how a recomp can snapshot its state, the determinism risks for each candidate CPU (notably the PS2 FPU, which is not IEEE-754), and the available rollback libraries and licences.

_PT-BR: o que uma recompilação estática precisa garantir para que o netplay com rollback possa ser adicionado depois? Levantar requisitos do rollback, como emuladores e ports conseguiram, como salvar o estado de uma recompilação, riscos de determinismo de cada processador e bibliotecas de rollback disponíveis._
