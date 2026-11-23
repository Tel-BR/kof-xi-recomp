---
id: 17
title: Decide how the IOP side is reproduced
type: grilling
status: closed
assignee: Tel-BR
blocked_by: [06, 15]
research: ../research/iop-audio-options.md
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

## Resolution (2026-11-23)

Re-decided on 2026-11-23 by the repo owner (Tel-BR), with rollback netplay as the focus. Evidence: [research/iop-audio-options.md](../research/iop-audio-options.md).

**PCSX2-matched SPU2 from the PS2Recomp-Fixer fork inside our `ps2xIOP`, with the original sound modules, clocked by emulated IOP time and running on the game thread. Controller and memory card stay native on the EE side; the controller is read once per frame for both ports.**

1. **Sound: the Fixer's SPU2 as a single piece** (`iop_spu2.{h,cpp}`, `iop_spu2_gauss.h`, ~2,000 lines, GPL-3.0; based on upstream [PR #308](https://github.com/ran-j/PS2Recomp/pull/308)) brought into our fork of `e563698`, without its diagnostic hooks, together with its wiring in `iop_memory`, `iop_emulator` and the IOP host output hook. The original `LIBSD`, `SDRDRV` and `CRI_ADXI` keep running on the emulated IOP and produce music, voices and sound effects as on the PS2, with PCSX2's sound behaviour, which also serves the audio comparison of [ticket 20](20-audio-comparison.md).
2. **Following from item 1, the Fixer's IOP fixes that this sound path needs:** AutoDMA completes at playback speed (fault 2), IOP sysclib's `look_ctype_table` returns real flags (a candidate cause of fault 1, the failed ADX output setup: in the Fixer it made `CRI_ADXI` ignore its start arguments; to be confirmed when it lands), no DMA completion or thread switch inside `CpuSuspendIntr` sections, same-priority IOP threads not preempting each other, and `sceSifGetOtherData`.
3. **Following from item 1, sound effects reach the IOP:** the EE's `sceSdRemote`, `sceSdRemoteInit` and `sceSdTransToIOP` stop being replaced by host stubs, so the recompiled library sends its commands to `SDRDRV.IRX`.
4. **Clock and host output:** the SPU2 advances by IOP cycles (768 per 48 kHz sample), which follow the EE's emulated cycles; nothing in the IOP reads host time. The host plays a one-way queue and may resample or drop audio to follow the sound card without touching the simulation. Upstream PR #307 (IOP time following the host clock) and the Fixer's real-time IOP baseline are not taken.
5. **IOP thread: the game thread.** With both faults fixed the IOP measured about 3% of the thread, a lower bound: that probe had no SPU2 mixing and no ADX streaming; a thread of its own would add locks and let the EE see the IOP at points that vary from run to run. To revisit only if a measurement shows the game thread is short of time once the GS has its own thread.
6. **Controller: native, read once per frame.** The game's `scePad*` functions stay host stubs. The runtime takes one snapshot of both ports per frame at the frame boundary and every `scePadRead` in that frame returns it, by port (players 1 and 2 separate). This is the single input entry point rollback needs. `SIO2MAN` and `PADMAN` are no longer loaded into the IOP. Vibration is left for later.
7. **Memory card: native folders, as today.** The game's `sceMc*` functions stay host stubs writing into `mc0/` and `mc1/`. `MCMAN` and `MCSERV` are no longer loaded into the IOP.
8. **Disc reads:** unchanged from the first resolution and [ticket 18](18-read-user-disc.md): served from the extracted files, never blocking a simulated frame.

**Consequences and follow-ups (not separate decisions):**

- Audio stays outside the rollback state and runs forward only ([ticket 21](21-game-state-regions.md)). The first resolution's rule carries over: sound requests made by resimulated frames are not sent to the IOP, and the IOP does not advance with the EE cycles of resimulated frames (otherwise it would run twice). Those frames still read IOP replies (ADX status, RPC results) and must see what the game saw the first time; how that is done (for example, recording the replies per frame and replaying them) belongs to the rollback-ready runtime contract.
- No real-time catch-up: because the SPU2 only follows emulated time, sound plays slow and breaks up whenever the game runs below real speed (about 33–37 of 60 vsyncs per second today, before the PCSX2 GS lands). This is accepted; the Fixer's real-time IOP baseline would hide it by putting host time in the simulation.
- To verify when the pieces land: speed with `tools/runtime/speed_report.py` and the IOP's share of the thread (3% was measured without sound; real mixing and streaming cost more), the CRI ADX output failures at 0 in the report, sound heard in an interactive run, and two controllers moving the two fighters separately.

**Rejected:** CRI's PCM played on the host as in Shinobi (each PS2RNA function must be found in an executable with no names, it leaves `sceSdRemote` sound effects silent, and ADX's clock would follow the host's sound card, putting host time in the simulation); the whole Fixer as a base (already rejected in [ticket 16](16-gs-vu1-approach.md): real-time VSync and alarms, IOP thread, IOP clock following real time); an IOP thread of its own (small gain, run-to-run variation); controller emulated through the Fixer's SIO2 and DualShock 2 with the original `PADMAN` (vibration, but input would pass through the IOP, which rollback does not restore); a PCSX2-format `.ps2` memory card file (format work for portability nobody needs yet; unlocks are covered by ticket 21's "Unlock All Characters" toggle).

---

_PT-BR: decidido de novo em 23/11/2026 pelo dono do repositório (Tel-BR), com o netplay com rollback como foco._

_**SPU2 do fork PS2Recomp-Fixer, conferido com o PCSX2, dentro do nosso `ps2xIOP`, com os módulos de som originais, movido pelo tempo emulado do IOP e rodando na thread do jogo. Controle e memory card continuam nativos do lado da EE; o controle é lido uma vez por quadro, nas duas portas.**_

1. _**Som: o SPU2 do Fixer como peça única** (~2.000 linhas, GPL-3.0, baseado no PR #308 do PS2Recomp oficial), trazido para o nosso fork do `e563698` sem os ganchos de diagnóstico, junto com a ligação dele em `iop_memory`, `iop_emulator` e no gancho de saída do IOP para o PC. Os `LIBSD`, `SDRDRV` e `CRI_ADXI` originais continuam no IOP emulado e geram música, vozes e efeitos como no PS2, com o comportamento de som do PCSX2, o que também serve à comparação de áudio do ticket 20._
2. _**Como consequência do item 1, as correções de IOP do Fixer que esse caminho exige:** AutoDMA terminando na velocidade de reprodução (falha 2), `look_ctype_table` do sysclib com os valores certos (candidata a causa da falha 1, a criação da saída do ADX: no Fixer, sem ela o `CRI_ADXI` ignorava seus argumentos; a confirmar quando entrar), nada de fim de DMA ou troca de thread dentro de `CpuSuspendIntr`, threads do IOP de mesma prioridade sem se interromper, e o `sceSifGetOtherData`._
3. _**Como consequência do item 1, os efeitos sonoros chegam ao IOP:** `sceSdRemote`, `sceSdRemoteInit` e `sceSdTransToIOP` da EE deixam de ser trocados por stubs do PC, e a biblioteca recompilada manda os comandos ao `SDRDRV.IRX`._
4. _**Relógio e saída no PC:** o SPU2 avança pelos ciclos do IOP (768 por amostra a 48 kHz), que seguem os ciclos emulados da EE; nada no IOP lê o relógio do PC. O PC toca uma fila de mão única e pode reamostrar ou descartar áudio para acompanhar a placa de som sem mexer na simulação. O PR #307 (tempo do IOP preso ao relógio do PC) e a linha de base em tempo real do IOP do Fixer não entram._
5. _**Thread do IOP: a do jogo.** Sem as duas falhas o IOP mediu ~3% da thread, um piso: aquela sonda não tinha mistura do SPU2 nem streaming do ADX; uma thread própria traria travas e faria a EE ver o IOP em pontos diferentes a cada rodada. Rever só se uma medição mostrar falta de tempo na thread do jogo depois que o GS ganhar a dele._
6. _**Controle: nativo, lido uma vez por quadro.** As funções `scePad*` do jogo continuam stubs do PC. O runtime tira uma foto das duas portas por quadro, na fronteira do quadro, e todo `scePadRead` daquele quadro devolve essa foto, por porta (jogadores 1 e 2 separados). É o ponto único de entrada que o rollback exige. `SIO2MAN` e `PADMAN` deixam de ser carregados no IOP. Vibração fica para depois._
7. _**Memory card: pastas no PC, como hoje.** As funções `sceMc*` do jogo continuam stubs do PC gravando em `mc0/` e `mc1/`. `MCMAN` e `MCSERV` deixam de ser carregados no IOP._
8. _**Leitura do disco:** igual à primeira resolução e ao ticket 18: servida dos arquivos extraídos, sem nunca travar um quadro simulado._

_**Consequências e próximos passos (não são decisões à parte):** o áudio fica fora do estado do rollback e só anda para frente (ticket 21). Continua a regra da primeira resolução: pedidos de som feitos em quadros refeitos não vão ao IOP, e o IOP não avança com os ciclos da EE desses quadros (senão rodaria duas vezes). Esses quadros ainda leem respostas do IOP (estado do ADX, resultados de RPC) e precisam ver o mesmo que o jogo viu da primeira vez; como fazer isso (por exemplo, gravar as respostas por quadro e repeti-las) fica para o contrato do runtime pronto para rollback. Sem compensação em tempo real: como o SPU2 só segue o tempo emulado, o som fica lento e picotado enquanto o jogo rodar abaixo da velocidade real (hoje ~33–37 de 60 vsyncs por segundo, antes do GS do PCSX2). Isso é aceito; a linha de base em tempo real do Fixer esconderia o problema pondo o relógio do PC na simulação. Verificar quando as peças entrarem: velocidade com o `speed_report.py` e a parcela do IOP na thread (os 3% foram medidos sem som; mistura e streaming de verdade custam mais), falhas de saída do CRI ADX em 0 no relatório, som ouvido numa rodada interativa e dois controles movendo os dois lutadores separadamente._

_**Descartados:** PCM do CRI tocado no PC como no Shinobi (cada função PS2RNA teria de ser achada num executável sem nomes, os efeitos do `sceSdRemote` ficariam mudos e o relógio do ADX seguiria a placa de som do PC, pondo tempo do PC na simulação); o Fixer inteiro como base (já descartado no ticket 16: VSync e alarmes em tempo real, IOP em thread, relógio do IOP seguindo o tempo real); IOP em thread própria (ganho pequeno, variação entre rodadas); controle emulado pelo SIO2 e DualShock 2 do Fixer com o `PADMAN` original (vibração, mas a entrada passaria pelo IOP, que o rollback não restaura); arquivo de memory card `.ps2` do PCSX2 (trabalho de formato para uma portabilidade que ninguém precisa ainda; os desbloqueios já têm a opção "liberar todos" do ticket 21)._
