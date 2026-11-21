---
id: 21
title: Decide which memory regions count as game state
type: grilling
status: closed
assignee: Tel-BR
blocked_by: [15, 19]
---

## Question

Which memory areas does the verification compare, and which does it ignore? The decision in [Decide how correctness is verified against a reference emulator](07-verification-oracle.md) is that only areas that belong to the game count, and BIOS/kernel areas are excluded. Choose the concrete list (main RAM ranges, scratchpad, and whether sound or video memory are in), using the noise map from [Prototype the reference capture on one scenario](19-prototype-reference-capture.md) and the chosen recompiler from [Decide the recompiler](15-decide-recompiler.md). The same list is the starting point for what rollback must save and restore, so it should be reconciled with the rollback requirements in [Survey how static recomps can support rollback netplay](03-rollback-on-static-recomp.md).

_PT-BR: quais áreas de memória a verificação compara e quais ignora? A decisão do ticket 07 é que só contam as áreas do jogo, sem BIOS/kernel. Escolher a lista concreta (faixas da RAM principal, scratchpad, e se memória de som ou de vídeo entram), usando o mapa de ruído do ticket 19 e o recompilador escolhido no ticket 15. A mesma lista é ponto de partida para o que o rollback precisa salvar e restaurar, então deve ser conciliada com os requisitos de rollback do ticket 03._

## Resolution

Decided on 2026-11-21 by the repo owner (Tel-BR).

**Game state is defined as the game's EE RAM segment (`0x100000` to `0x01E2D480`), EE Scratchpad (`0x70000000`), and CPU/VU0 registers; kernel memory, SPU2 sound RAM, and GS VRAM are excluded. Character unlocks reside in EE RAM and synchronize naturally under rollback.**

### Concrete Boundaries

1. **Included Memory Regions (Rollback Savestate & Verification Oracle):**
   - **Game EE RAM:** `0x100000` to `0x01E2D480` (~28.6 MB). This matches the ELF segment boundaries determined in [Inspect the code structure of each candidate release](08-inspect-code-structure.md). It encompasses game variables, fighter positions, hitboxes, frame data counters, animation timers, health bars, and game-mode state.
   - **EE Scratchpad:** `0x70000000` to `0x70003FFF` (16 KB fast on-chip RAM). Used by Metrowerks CodeWarrior routines for scratch calculations during gameplay.
   - **CPU Registers:** EE 128-bit GPRs (`$1`..`$31`), PC, HI/LO, and active VU0 vector registers.

2. **Excluded Regions (Ignored in Diffs and Omitted from Savestates):**
   - **Kernel Memory (`0x000000` to `0x0FFFFF`, bottom 1 MB):** Holds Sony BIOS/kernel exception vectors, OS thread control blocks, heap allocators, and non-deterministic timers identified in [Prototype the reference capture on one scenario](19-prototype-reference-capture.md). Excluded to avoid false desyncs.
   - **SPU2 Audio RAM (2 MB):** Per [Decide how the IOP side is reproduced](17-iop-approach.md) and ADR-0002, audio runs forward asynchronously without rollback to prevent audio pops and stutter.
   - **GS Video Memory (4 MB VRAM):** Per [Decide how GS and VU1 graphics are reproduced](16-gs-vu1-approach.md) and ADR-0001, rendering state lives in host graphics API command buffers outside simulation memory.

3. **Character Unlocks and Recomp Toggle Integration:**
   - The native port includes an "Unlock All Characters" configuration option (enabled by default, with a toggle allowing players to unlock them manually if desired).
   - In the PS2 Release, character unlock flags reside in the game's EE RAM (`0x100000`–`0x01E2D480`).
   - Because this region is captured in the initial frame-0 state and maintained through rollback savestates, both netplay peers synchronize their roster settings deterministically, guaranteeing identical character selection without netplay desync.

---

_PT-BR: decidido em 21/11/2026 pelo dono do repositório (Tel-BR)._

_**O estado do jogo é definido pela faixa de RAM da EE do jogo (`0x100000` a `0x01E2D480`), Scratchpad da EE (`0x70000000`) e registradores da CPU/VU0; memória de kernel, RAM de som do SPU2 e VRAM do GS são excluídas. O desbloqueio de personagens reside na RAM da EE e sincroniza naturalmente no rollback.**_

_Limites concretos:_
1. _**Regiões incluídas (Savestate de Rollback e Verificação):**_
   - _**RAM da EE do jogo:** `0x100000` a `0x01E2D480` (~28.6 MB). Delimitada pelo segmento ELF do jogo (ticket 08). Contém todas as variáveis de luta: posições dos lutadores, barras de vida/especial, hitboxes, contadores de quadros e máquinas de estado._
   - _**Scratchpad da EE:** `0x70000000` a `0x70003FFF` (16 KB). Usado pelo compilador CodeWarrior para cálculos rápidos de física._
   - _**Registradores da CPU:** registradores gerais de 128 bits (`$1`..`$31`), PC, HI/LO e registradores da VU0._
2. _**Regiões excluídas (não entram no rollback nem na comparação):**_
   - _**Memória do Kernel (`0x000000` a `0x0FFFFF`, primeiro 1 MB):** contém vetores de interrupção da Sony, descritores de threads e contadores de relógio que geram ruído não determinístico (ticket 19)._
   - _**RAM de som do SPU2:** o áudio corre sempre para frente e não retrocede no rollback (ticket 17 e ADR-0002)._
   - _**Memória de vídeo do GS (VRAM):** o desenho é traduzido em shaders fora da simulação (ticket 16 e ADR-0001)._
3. _**Desbloqueio de personagens e opção no port:**_
   - _O port trará todos os personagens desbloqueados por padrão, com um seletor na interface permitindo desmarcar caso o jogador prefira desbloquear manualmente._
   - _Como os sinalizadores de desbloqueio ficam guardados na RAM da EE do jogo (`0x100000` a `0x01E2D480`), esse estado faz parte da memória salva e sincronizada pelo rollback, garantindo que ambos os jogadores online compartilhem exatamente os mesmos personagens ativos sem causar desync._
