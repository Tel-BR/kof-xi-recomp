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

## Reopened (2026-11-22)

Reopened by the owner: the audio decision rests on a false premise, and the input and memory card decisions were not carried out ([research/diagnose-runtime-performance-audio.md](../research/diagnose-runtime-performance-audio.md)).

- **There was no audio output to rely on.** [Try PS2Recomp on the PS2 executable](13-try-ps2recomp.md) only saw the ADX driver start. The SPU2 is not emulated, so the original sound modules cannot make sound however they run.
- **The ADX driver fails to set up its output** (`PSM_Create` fails at `PSMTBF_Create`) and falls into a deliberate endless loop that the IOP interpreter keeps executing.
- **Sound DMA finishes 384 times too early** without an SPU2, so LIBSD's transfer-complete handler runs about 33,000 times per second instead of about 90. With both faults, the IOP takes about 55–60% of the one host thread; removing them in a probe raised the game from about 13 to 25–26 vsyncs per second.
- **`PADMAN`, `MCMAN` and `MCSERV` are still emulated IRX modules**, not the native replacements decided below.

**To re-decide:** how sound is produced, for example PCSX2's SPU2 inside `ps2xIOP` (as Persona 3 FES and the PS2Recomp-Fixer fork do), CRI's PCM output played on the host (as Shinobi does), or adopting the fork; and whether the IOP runs on its own thread. The rollback requirements stay: audio runs forward only, one input entry point, no host time in the simulation.

_PT-BR: reaberto pelo dono: a decisão de áudio parte de uma premissa falsa, e as decisões de controle e memory card não foram executadas. O ticket 13 só viu o driver ADX iniciar; o SPU2 não é emulado, então os módulos originais não têm como gerar som. A criação da saída do ADX falha e o driver entra num laço infinito proposital, que o IOP interpretado segue executando. Sem SPU2, a DMA de som termina 384 vezes cedo demais e o tratador do LIBSD roda ~33 mil vezes por segundo em vez de ~90. Juntas, essas falhas ocupam ~55–60% da única thread; removê-las numa sonda levou o jogo de ~13 para 25–26 vsyncs por segundo. `PADMAN`, `MCMAN` e `MCSERV` continuam emulados. A decidir de novo: como o som é produzido (o SPU2 do PCSX2 dentro do `ps2xIOP`, a saída PCM do CRI tocada no PC, ou adotar o fork) e se o IOP ganha thread própria. Os requisitos de rollback continuam: áudio só para frente, um único ponto de entrada de controle, nenhum relógio do PC na simulação._

## Resolution (2026-11-21, reopened)

Decided on 2026-11-21 by the repo owner (Tel-BR).

**Hybrid approach: native deterministic input and cached disc reads on the host, with emulated IOP audio running forward asynchronously outside the rollback state.**

### Concrete Decisions by Subsystem

1. **Controller Input (`PADMAN.IRX` / `SIO2MAN.IRX`): Replaced by Native Host Input.**
   - **Rollback Requirement:** Must adhere strictly to GGPO's single input entry point contract. Real-time controller polling or emulating the PS2 pad bus directly would break rollback resimulation by leaking host OS timing or reading uncoordinated button states during frame rewinds.
   - **Design:** `PADMAN` is replaced with a clean host bridge. The simulation receives exactly one immutable input structure per frame before simulation advances, enabling deterministic replay and seamless integration with rollback libraries (GGPO / GekkoNet) as well as modern PC inputs (XInput, DirectInput, SDL3).

2. **Audio Subsystem (`CRI_ADXI.IRX` / `LIBSD.IRX` / `SDRDRV.IRX` / SPU2): Emulated IOP Running Forward.**
   - **Rollback Requirement:** Audio must never be rewound or restored during rollback frame resimulations (rewinding audio produces audible pops, clicks, distortion, and stuttering).
   - **Design:** The project keeps the original audio modules (`CRI_ADXI` and Sony sound drivers) running inside the PS2Recomp emulated IOP core (which already demonstrated successful boot and audio output in [Try PS2Recomp on the PS2 executable](13-try-ps2recomp.md)).
   - Sound trigger commands from the main EE CPU to the IOP are queued during the presentation frame only; during rollback catch-up resimulation, audio command triggers are discarded so sound playback continues smoothly forward.

3. **Disc I/O (`CDVD` / `KOF_000x.DAT`): Intercepted and Served Deterministically from RAM/Cache.**
   - **Rollback Requirement:** A file read must never block or yield to asynchronous optical/disk hardware during a rollback prediction frame.
   - **Design:** As established in [Find out what the two big PS2 DAT files hold](12-ps2-big-dat-files.md), the real game data occupies only ~1.17 GB, while the two 630 MB DAT files are dead padding and completely ignored.
   - The port maps all required disc assets directly into a memory cache or fast synchronous host file lookup, ensuring 0 ms read latency during simulation frames.

4. **Memory Card & System Modules (`MCMAN.IRX` / `MCSERV.IRX`): Native Host Stubs.**
   - Memory card operations are handled via native filesystem directory or local `.bin` container stubs on the host, avoiding emulated flash access timing quirks.

5. **Monitoring & Fallback Strategy:**
   - Per the owner's direction: observe runtime behavior during milestone scenarios. If emulated IOP thread timing drifts from the EE simulation, isolate the RPC boundary and evaluate native HLE decoding for CRI ADX.

---

_PT-BR: decidido em 21/11/2026 pelo dono do repositório (Tel-BR)._

_**Abordagem híbrida: entrada de controle nativa e leitura de disco em cache na máquina local, com áudio do IOP emulado correndo sempre para a frente fora do estado de rollback.**_

_Decisões concretas por subsistema:_
1. _**Controles (`PADMAN.IRX` / `SIO2MAN.IRX`): substituído nativamente no PC.** Exigência central do rollback: a entrada de controles deve vir de um único ponto determinístico por quadro. Emular o circuito do controle do PS2 quebraria o rollback ao ler controles do Windows de forma assíncrona durante a rebobinagem. O `PADMAN` é substituído por uma ponte nativa que injeta exatamente 1 estrutura de botões por quadro antes da simulação, compatível com GGPO, teclados e controles modernos (XInput/SDL3)._
2. _**Áudio (`CRI_ADXI.IRX`, `LIBSD.IRX`, `SDRDRV.IRX`, SPU2): IOP emulado correndo para a frente.** O áudio nunca deve retroceder no rollback para evitar estalos, ruídos e gagueira de som. Os módulos rodam no núcleo emulado de IOP do PS2Recomp (que já funcionou no ticket 13). Comandos de som são enfileirados apenas no quadro final exibido; durante a re-simulação rápida de rollback, chamadas de áudio repetidas são descartadas e a música continua tocando suave para frente._
3. _**Leitura de disco (`CDVD`): interceptada e servida em memória (RAM/SSD).** Nenhuma leitura de disco pode travar a simulação durante um quadro recalculado. Comprovado no ticket 12 que os dados reais têm ~1.17 GB e os arquivos DAT são dispensáveis, todos os arquivos da luta ficam pré-carregados em cache de memória com latência zero e determinismo total._
4. _**Memory Card (`MCMAN` / `MCSERV`): stubs nativos no PC.** Salva dados em arquivos comuns no PC sem emular circuitos de cartão de memória._
5. _**Monitoramento e contingência:** conforme orientação do dono, o comportamento em jogo será monitorado; caso surjam problemas de sincronia entre EE e IOP, avalia-se a substituição do CRI ADX por um decodificador nativo no PC._
