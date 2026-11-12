---
id: 03
title: Survey how static recomps can support rollback netplay
type: research
status: closed
assignee: claude
blocked_by: []
research: ../research/rollback-on-static-recomp.md
---

## Question

What must a static recomp guarantee so rollback netplay can be added later? Survey what rollback requires (per-frame save/restore of the full simulation state, determinism, input decoupling), how emulators and ports achieved it (FBNeo/Fightcade, Flycast GGPO, RetroArch, decomps), how a recomp can snapshot its state, the determinism risks for each candidate CPU (notably the PS2 FPU, which is not IEEE-754), and the available rollback libraries and licences.

_PT-BR: o que uma recompilação estática precisa garantir para que o netplay com rollback possa ser adicionado depois? Levantar requisitos do rollback, como emuladores e ports conseguiram, como salvar o estado de uma recompilação, riscos de determinismo de cada processador e bibliotecas de rollback disponíveis._

## Resolution

Full findings: [research/rollback-on-static-recomp.md](../research/rollback-on-static-recomp.md).

- **What rollback needs from the game:** three operations (save the state, load the state, advance one frame with given inputs) and full determinism: the same inputs give the same bits on both PCs.
- **Precedent:** emulators do it with whole-machine savestates (FBNeo/Fightcade, Flycast GGPO, which already runs KOF XI's arcade code, RetroArch, Slippi). One static recomp has working, still experimental, rollback (psxrecomp, PS1); none exists yet for PS2 or SH-4.
- **Snapshotting a recomp:** mostly copying the emulated memory and CPU registers, plus video, sound, timer, DMA, disc and host-cache state. The catch is that recompiled code keeps return addresses on the PC's own stack, so snapshots must be taken at one defined point in the frame where all game threads are parked.
- **Cost:** a full copy every frame (~26 MiB arcade, ~40 MiB PS2) is too slow for an 8-frame rollback; shipped projects copy only the memory pages that changed, or only the regions that matter.
- **Determinism risks:** floating point (PS2 is non-IEEE; SH-4 switches precision and rounding at run time), compiler options, the Windows maths library's FMA3 switch, host clocks, threads and uninitialised memory.
- **Libraries:** GekkoNet (BSD-2, active), GGPO (MIT, inactive since 2019), GGRS (Rust, MIT/Apache); all are permissive.
- **Early architecture requirements:** the findings list 12, including one owner for all simulation state, a defined frame boundary, deterministic scheduling, a single input entry point, simulation separated from presentation, time only from the simulation, a pinned floating-point policy, a save/load/hash API from day one, and an automatic "rewind and replay" test. Which become binding depends on the recompiler and runtime (still in the fog).

_PT-BR: o rollback exige do jogo três operações (salvar, carregar e avançar um quadro) e determinismo total. Emuladores já fazem isso, inclusive o Flycast com o código de arcade do KOF XI; só uma recompilação estática (de PS1) tem rollback, ainda experimental. Salvar o estado de uma recompilação é quase só copiar memória, mas tem de ser num ponto fixo do quadro, e copiar tudo a cada quadro é lento demais: os projetos copiam só as páginas que mudaram. Os maiores riscos são o ponto flutuante, as opções do compilador, o relógio do PC e as threads. As bibliotecas são todas permissivas (GekkoNet, GGPO, GGRS). A pesquisa lista 12 requisitos de arquitetura para fixar cedo; quais viram regra depende do recompilador e do runtime, ainda na névoa._
