---
id: 15
title: Decide the recompiler
type: grilling
status: closed
assignee: Tel-BR
blocked_by: [13]
---

## Question

Which static recompiler turns the Base Version's R5900 code into native code: adopt PS2Recomp as it is, build on a fork of it, or write the project's own? Weigh what [Try PS2Recomp on the PS2 executable](13-try-ps2recomp.md) found, PS2Recomp's GPL-3.0 licence (adopting it makes the distributed port GPL-3.0), its float emulation and its runtime against the rollback requirements in [Survey how static recomps can support rollback netplay](03-rollback-on-static-recomp.md), and how function discovery will work on an executable without symbols.

_PT-BR: qual recompilador estático transforma o código R5900 da versão-base em código nativo: usar o PS2Recomp como está, partir de um fork dele ou escrever um próprio? Pesar o resultado do ticket 13, a licença GPL-3.0 do PS2Recomp (adotá-lo torna o port distribuído GPL-3.0), a emulação de ponto flutuante e o runtime dele diante dos requisitos de rollback do ticket 03, e como descobrir as funções num executável sem símbolos._

**Input from [Measure the PS2 Release's VU1 and GS usage](14-measure-vu1-gs-usage.md) (2026-11-13):** the game runs no VU1 or VU0 microprograms in anything captured, so PS2Recomp's known weakness with VU1 matters less; what matters is the main-CPU code, including 305 VU0 macro instructions (vector math issued by the main CPU), and the GS path. / _Do ticket 14: o jogo não roda microprogramas de VU1 nem de VU0 no que foi capturado; a fraqueza do PS2Recomp com a VU1 pesa menos, e o que importa é o código da CPU principal (com 305 instruções vetoriais da VU0) e o caminho até o GS._

## Resolution

Decided on 2026-11-21.

**Build on a fork of PS2Recomp (`ran-j/PS2Recomp`).**

### Evaluation of Options

1. **Option A: Adopt PS2Recomp upstream directly (Rejected).**
   - Upstream PS2Recomp is built for single-player console recompilation, not rollback netplay. It has no API or abstraction to snapshot and restore the simulation state (the ~32 MiB EE memory and registers) at 60 Hz.
   - It lacks a designated frame-boundary synchronization point where all EE threads are safely parked for snapshotting.
   - Host OS clocks and timers leak directly into emulated timing and thread scheduling, violating the determinism required by rollback.
   - The stock runner lacks CLI/environment configuration for User-supplied Disc images (required a local patch in Ticket 13), and needs small build tweaks for MinGW/clang toolchains.
   - Keeping upstream as an unmodified dependency prevents implementing the architecture required by [Survey how static recomps can support rollback netplay](03-rollback-on-static-recomp.md).

2. **Option C: Write a custom static recompiler from scratch (Rejected).**
   - Writing an R5900 recompiler from scratch would be massive, unnecessary overhead. The Emotion Engine is complex: MIPS III/IV base instructions, 128-bit MMI SIMD instructions, non-standard non-IEEE-754 truncated/clamped float arithmetic, and 305 VU0 macro instructions (`CTC2`, `CFC2`, `QMFC2`, `QMTC2`, `VADD`, `VMUL`, etc.).
   - [Try PS2Recomp on the PS2 executable](13-try-ps2recomp.md) proved that PS2Recomp already translates 100% of KOF XI's real code with **0 unhandled instructions**, compiles with 0 errors, and boots the game (loading 7 IOP modules, initializing CRI ADX, and driving the GS for 439 frames).
   - Rebuilding an instruction recompiler and an EE kernel/DMAC runtime from scratch would delay the first playable fight by months or years for no functional benefit.

3. **Option B: Build on a fork of PS2Recomp (Decided).**
   - **Proven translation:** Preserves PS2Recomp's complete, verified instruction translation for R5900 MMI and VU0 macro instructions.
   - **Freedom to implement rollback:** A fork allows adding the state-snapshotting abstractions:
     - Introducing an explicit frame-boundary hook where EE threads park and state is captured.
     - Implementing differential/dirty-page tracking for the ~32 MiB memory space so rollback save/restore takes <1 ms rather than copying 32 MiB every frame.
     - Decoupling the simulation state from host presentation and replacing real-time host clocks with deterministic, input-driven tick stepping.
   - **Toolchain maintenance:** Incorporates the MinGW/clang build adjustments (SSE4.1 flags, raylib header namespace fixes, include paths) and CLI disc path loading directly.

### Function Discovery Strategy

The stall observed in Ticket 13 (an indirect `JALR` jump to `0x1FB188`) was caused by the analyzer's built-in JAL scanner missing ~921 pointer-dispatched functions (96% of function pointers in the binary).

- The project will use PS2Recomp's official Ghidra export pipeline (`ExportSymbols.py`).
- Ghidra with the R5900 Emotion Engine module is already set up in `private/tools/ghidra`.
- Headless Ghidra analysis of `SLUS_216.87` identifies all function entries (including indirect callback tables, jump tables, and leaf functions) and generates a complete `symbols.csv` / TOML configuration.
- It also cleanly defines the code boundaries (`0x100008`–`0x280830`), ensuring the 18 data-tail pseudo-functions (`0x280830`–`0x2F1400`) are excluded from recompiler input.

### Consequences

- **Licence:** PS2Recomp is licensed under GPL-3.0. Forking and distributing the native PC port makes the port GPL-3.0. This resolves the question for [Decide whether to relicense to GPL](06-gpl-relicense.md).
- **Downstream Tickets:**
  - Unblocks [Decide whether to relicense to GPL](06-gpl-relicense.md) to formalize GPL-3.0.
  - Unblocks [Decide how GS and VU1 graphics are reproduced](16-gs-vu1-approach.md) and [Decide how the IOP side is reproduced](17-iop-approach.md), which will build upon the PS2Recomp fork runtime.
- **Hard Rule Compliance:** The fork contains only recompiler and runtime source code. Discs, extracted assets, symbols, and generated C++ remain strictly inside `private/`.

---

_PT-BR: decidido em 21/11/2026. **Construir sobre um fork do PS2Recomp (`ran-j/PS2Recomp`).**_

_Avaliação das opções:_
- _**Opção A: Adotar o PS2Recomp upstream diretamente (Rejeitada).** O upstream foi feito para jogos solo no console e não tem suporte a rollback: não tem ganchos de sincronização na fronteira de quadros quando as threads da EE estão estacionadas, não tem API de snapshot diferencial para salvar/restaurar ~32 MiB a 60 Hz e faz o relógio do sistema operacional vazar para o escalonador e temporizadores, quebrando o determinismo. Também exige ajustes locais para carregar imagens de disco e compilar no MinGW/clang._
- _**Opção C: Escrever um recompilador estático próprio do zero (Rejeitada).** Seria um retrabalho enorme e desnecessário. O conjunto de instruções do R5900 (MIPS III/IV, MMI de 128 bits, ponto flutuante truncado/não IEEE-754 e 305 instruções vetoriais da VU0) já foi 100% traduzido pelo PS2Recomp sem nenhuma instrução não tratada no código real, compilando com 0 erros e rodando 439 quadros do GS. Fazer do zero adiaria o projeto por meses ou anos sem ganho funcional._
- _**Opção B: Partir de um fork do PS2Recomp (Decidida).** Aproveita a tradução completa e testada de instruções e dá controle total para implementar a arquitetura de rollback: gancho de fronteira de quadro, salvamento diferencial de páginas modificadas para snapshot em <1 ms, desacoplamento da simulação em relação à apresentação e avanço por ticks determinísticos sem relógio do host._

_Descoberta de funções:_
- _O travamento no ticket 13 (chamada indireta para `0x1FB188`) ocorreu porque a varredura embutida de JAL perdeu 921 funções chamadas por ponteiro (96% dos ponteiros de função)._
- _A solução será usar o fluxo oficial de exportação do Ghidra do PS2Recomp (`ExportSymbols.py`). O Ghidra com o módulo da Emotion Engine (R5900) já está disponível em `private/tools/ghidra`._
- _A análise headless do Ghidra no `SLUS_216.87` descobre todos os pontos de entrada de funções (tabelas de callback, saltos indiretos e funções-folha) e define o corte exato de código (`0x100008`–`0x280830`), eliminando as 18 pseudo-funções de dados no final da imagem._

_Consequências:_
- _**Licença:** o PS2Recomp é GPL-3.0. Fazer um fork e distribuir o port torna o projeto GPL-3.0, resolvendo a direção do ticket 06 ([Decidir sobre relicenciamento para GPL](06-gpl-relicense.md))._
- _**Próximos tickets:** desbloqueia o ticket 06 para formalizar a GPL-3.0, e os tickets 16 (GS/VU1) e 17 (IOP), que partem do runtime do fork do PS2Recomp._
- _**Regra obrigatória:** o fork conterá apenas código-fonte do recompilador e do runtime; discos, assets extraídos e código gerado permanecem estritamente em `private/`._
