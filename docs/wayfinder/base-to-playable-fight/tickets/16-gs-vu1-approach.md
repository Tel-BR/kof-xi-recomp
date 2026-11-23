---
id: 16
title: Decide how GS and VU1 graphics are reproduced
type: grilling
status: closed
assignee: Tel-BR
blocked_by: [06, 14, 15]
research: ../research/gs-renderer-options.md
---

## Question

How does the port draw the Base Version's graphics? The GS and the VU1 microprograms are the hardest part of the PS2 Release ([Survey graphics and audio reimplementation options and their licenses](02-graphics-audio-options.md)). Options include emulating the GS behind the recompiled code, translating its command stream to a modern graphics API, and interpreting or recompiling the VU1 microprograms. Choose using the measurements in [Measure the PS2 Release's VU1 and GS usage](14-measure-vu1-gs-usage.md), the chosen recompiler, the licence decision, and the first decisive criterion: excellent performance with the NGBC-derived fighters. The renderer must also stay outside the simulation state that rollback saves and restores.

_PT-BR: como o port desenha o gráfico da versão-base? O GS e os microprogramas da VU1 são a parte mais difícil do PS2. Opções: emular o GS por trás do código recompilado, traduzir os comandos dele para uma API gráfica moderna, e interpretar ou recompilar os microprogramas da VU1. Escolher com base nas medições do ticket 14, no recompilador escolhido, na licença e no primeiro critério decisivo: desempenho excelente com os lutadores do NGBC. O desenho também precisa ficar fora do estado que o rollback salva e restaura._

## Reopened (2026-11-22)

Reopened by the owner: the decision rests on a false premise ([research/diagnose-runtime-performance-audio.md](../research/diagnose-runtime-performance-audio.md)).

- **PS2Recomp has no shader GS backend.** At `e563698` its only GS renderer is `GSCpuBackend`, which draws every pixel on the CPU; the GPU only displays the finished picture.
- **The software GS is now the main cost.** With the IOP faults removed, it takes about 63% of the one busy host thread, and the game stays near 25 of 60 vsyncs per second on the owner's machine.
- **What still holds:** zero VU1 microcode (ticket 14), the small GS feature set, and the requirement that renderer state stays outside rollback state with draws suppressed during resimulation.

**To re-decide:** how GS commands reach the GPU, for example PCSX2's hardware GS as the [PS2Recomp-Fixer](https://github.com/w1284603830/PS2Recomp-Fixer/) fork does (DX11/12, own thread, GPL-3.0), a renderer of our own as [BT3-Recomp](https://github.com/z3xox/BT3-Recomp) built (OpenGL/Vulkan), or paraLLEl-GS. Each option must be presented with its causes and consequences.

_PT-BR: reaberto pelo dono porque a decisão parte de uma premissa falsa: o PS2Recomp não tem backend de GS com shaders. No `e563698` o único renderizador é o `GSCpuBackend`, que desenha cada pixel na CPU; a placa de vídeo só mostra a imagem pronta. Sem as falhas do IOP, ele consome ~63% da única thread ocupada e o jogo fica perto de 25 de 60 vsyncs por segundo. Continua valendo: nenhum microcódigo de VU1, o conjunto pequeno de recursos do GS e o estado do renderizador fora do rollback. A decidir de novo: como os comandos do GS chegam à placa de vídeo (por exemplo, o GS por hardware do PCSX2 como no fork PS2Recomp-Fixer, um renderizador próprio como no BT3-Recomp, ou o paraLLEl-GS), com causas e consequências de cada opção._

## Resolution (2026-11-21, reopened)

Decided on 2026-11-21 by the repo owner (Tel-BR).

**Command-stream translation via the PS2Recomp shader backend (Vulkan/Direct3D), decoupled from simulation state, with an assertion guard for VU1.**

### Concrete Decisions

1. **GS Rendering Approach:**
   - The port translates the GS PATH3 command stream (GIF packets) into modern graphics API draw calls using PS2Recomp's shader-based GS renderer (under the GPL-3.0 license decided in [Decide whether to relicense to GPL](06-gpl-relicense.md)).
   - The PS2 Release uses a small and conventional GS feature set (`Z32` depth, `CT32` color targets, `T4`/`T8` palette textures in CSM1, and two blend equations: standard alpha and additive) with heavy 2D texture streaming (up to 14.4 MB/dump), perfectly matching a modern shader backend with texture cache.
   - Reusing the PS2Recomp renderer guarantees high performance for both regular 2D stages and extra 3D stages with NGBC-derived fighters.

2. **Decoupled from Rollback Simulation State:**
   - The renderer lives entirely outside the rollback state buffer. GS registers and GPU buffers are never serialized into frame savestates.
   - During rollback prediction resimulation (e.g. resimulating 4–8 frames to reconcile network input), the engine invokes the advance frame callback with **host draw calls suppressed**, rendering only the final displayed frame to the screen.

3. **Zero VU1 Microcode & Runtime Assertion Guard:**
   - As measured in [Measure the PS2 Release's VU1 and GS usage](14-measure-vu1-gs-usage.md), KOF XI runs zero VU1 microprograms across menus, 2D stages, 3D stages, and NGBC fighters; all drawing reaches the GS via PATH3 from the main EE CPU.
   - VU1 emulation is omitted entirely from the active build and rollback state.
   - A lightweight assertion/logging guard is placed on VIF1/VU1 DMA channels to immediately log and halt if an unobserved mode (e.g. gallery cutscenes or challenge modes) ever attempts to upload a VU1 microprogram or transmit PATH1/PATH2 packets.

4. **Fallback Strategy:**
   - Per the owner's direction: monitor visual output during milestone verification against the Reference Emulator (PCSX2). If specific rendering artifacts appear (e.g. depth fighting on 3D stages or palette indexing quirks), address them via targeted shader fixes or explore the PCSX2 `limit24BitDepth` workaround before evaluating alternative backends.

---

_PT-BR: decidido em 21/11/2026 pelo dono do repositório (Tel-BR)._

_**Tradução de comandos do GS via backend de shaders do PS2Recomp (Vulkan/Direct3D), desacoplado do estado de simulação, com guarda de log para a VU1.**_

_Decisões concretas:_
1. _**Abordagem do GS:** o port traduz o fluxo de comandos PATH3 do GS (pacotes GIF) para chamadas de APIs gráficas modernas aproveitando o renderizador do PS2Recomp (sob GPL-3.0, conforme o ticket 06). O jogo usa um conjunto simples de recursos do GS (`Z32`, texturas indexadas `T4`/`T8` e duas equações de blend) com envio pesado de texturas 2D (até 14.4 MB por despejo), cenário ideal para o backend de shaders com cache de texturas, garantindo 60 FPS cravados com os lutadores do NGBC e nas fases 3D._
2. _**Desacoplamento do Rollback:** o renderizador fica 100% fora da memória salva pelo rollback. Durante correções de rede (onde a física avança 4 a 8 quadros em fração de milissegundo), as chamadas de desenho na GPU são suprimidas, desenhando apenas o último quadro corrigido na tela._
3. _**Sem microcódigo na VU1 e guarda de execução:** o ticket 14 provou que o jogo não usa microprogramas de VU1. A emulação da VU1 foi totalmente removida do estado ativo e dos savestates. Uma guarda de log no DMA da VU1 alertará imediatamente caso algum modo ainda não testado tente enviar microcódigo inesperado._
4. _**Estratégia de contingência:** conforme orientação do dono, o comportamento visual será monitorado contra o emulador de referência (PCSX2); se surgirem falhas gráficas pontuais, serão corrigidas via ajustes nos shaders ou na precisão de profundidade (`limit24BitDepth`)._

## Resolution (2026-11-22)

Re-decided on 2026-11-22 by the repo owner (Tel-BR), with rollback netplay as the focus and performance as the decisive criterion. The owner leaned toward engine-level drawing (option D) for what it could open later (new options, New Characters, high resolution), then chose to start from option A once its effort was weighed: D needs an emulated GS underneath anyway, and new options and New Characters depend on understanding the game's data and logic, not on how GS commands reach the GPU. The owner's test machine has an NVIDIA GTX/RTX GPU. Evidence: [research/gs-renderer-options.md](../research/gs-renderer-options.md).

**PCSX2's hardware GS, taken as a single piece from the PS2Recomp-Fixer fork into our PS2Recomp fork, fed on its own thread and kept outside the rollback state. Engine-level drawing is a future direction on top of it, not part of this map.**

1. **Renderer:** `pcsx2gs.dll` (PCSX2's hardware renderer, DX11/DX12, GPL-3.0) from [PS2Recomp-Fixer](https://github.com/w1284603830/PS2Recomp-Fixer/), behind its C API: the runtime hands it the merged GIF stream and the end of each field. It draws with the same code as the Reference Emulator, runs on almost any DirectX 11 GPU, and takes the GS work off the game thread.
2. **Only that piece, not the Fixer as a base.** [Decide the recompiler](15-decide-recompiler.md) stands: we keep our fork of upstream `e563698` and port the GS glue (`dod_pcsx2_gs.cpp`, ~1,000 lines) into it. The Fixer's real-time VSync and alarms and its IOP thread bring host time into the simulation, which rollback forbids; its SPU2 may be weighed as a separate piece in [Decide how the IOP side is reproduced](17-iop-approach.md).
3. **Rollback:** renderer state stays outside the rollback state (the game never reads from the GS), and draws stay suppressed during resimulation: frames resimulated during rollback are neither drawn nor presented. Whether their texture uploads are still fed to the GS or the renderer is resynchronised another way belongs to the rollback-ready runtime contract.
4. **VU1:** unchanged from the first resolution. No VU1 emulation in the active build, and a guard that logs and stops on any VU1 microprogram upload or PATH1/PATH2 packet.
5. **Engine-level drawing (option D):** drawing selected layers (fighter sprites first) from the game's own data, layer by layer, with the PCSX2 GS drawing everything not yet covered. It belongs to the future high-resolution/widescreen map. Studying the sprite and palette formats it needs also serves New Characters.

**Consequences and follow-ups (not separate decisions):**

- The Fixer's README requires Visual Studio 2022 (MSVC) for the DLL; our runtime builds with clang/MinGW, and the DLL's C API lets the two meet. Windows first; PCSX2's Vulkan/OpenGL/Metal backends are absent from the vendored tree and would be brought in from PCSX2 for Linux and macOS (the tree keeps PCSX2's layout).
- To verify when the piece lands: speed with `tools/runtime/speed_report.py` on the owner's machine (GREEN at 57 vsyncs/s or more), and input latency with the GS thread's queue kept at the minimum for play.

**Rejected:** paraLLEl-GS (it would run on the owner's NVIDIA GPU, but online players use GPUs of every kind and it needs modern Vulkan, with known crashes on older AMD drivers; presentation through our OpenGL window adds a frame of latency; not the Reference Emulator's code); a renderer of our own (the most work and the most visual differences from the Reference Emulator); engine-level drawing as the base (it needs an emulated GS underneath anyway and reverse engineering of every drawing layer); keeping the CPU GS on its own thread (still about 27 ms per vsync).

_PT-BR: decidido de novo em 22/11/2026 pelo dono do repositório (Tel-BR), com o netplay com rollback como foco e o desempenho como critério decisivo. O dono se inclinou para o desenho no nível do jogo (opção D) pelo que ela poderia abrir depois (opções novas, personagens novos, alta resolução) e escolheu começar pela opção A depois de pesar o esforço: a D precisa de um GS emulado por baixo de qualquer jeito, e opções e personagens novos dependem de entender os dados e a lógica do jogo, não de como os comandos do GS chegam à placa de vídeo. A máquina de testes do dono tem placa NVIDIA GTX/RTX._

_**GS por hardware do PCSX2, trazido como peça única do fork PS2Recomp-Fixer para o nosso fork do PS2Recomp, alimentado numa thread própria e fora do estado do rollback. O desenho no nível do jogo fica como direção futura por cima dele, fora deste mapa.**_

1. _**Renderizador:** a `pcsx2gs.dll` (renderizador por hardware do PCSX2, DX11/DX12, GPL-3.0) do PS2Recomp-Fixer, pela interface em C dela: o runtime entrega o fluxo de comandos do GIF e o fim de cada campo. Desenha com o mesmo código do emulador de referência, roda em quase qualquer placa com DirectX 11 e tira o GS da thread do jogo._
2. _**Só essa peça, não o Fixer como base.** O ticket 15 continua valendo: seguimos no nosso fork do `e563698` e trazemos para ele o código de ligação (~1.000 linhas). O VSync e os alarmes em tempo real e o IOP em thread própria do Fixer põem o relógio do PC na simulação, o que o rollback proíbe; o SPU2 dele pode ser avaliado como peça separada no ticket 17._
3. _**Rollback:** o estado do renderizador fica fora do estado do rollback (o jogo nunca lê do GS), e o desenho continua suprimido na ressimulação: quadros refeitos durante o rollback não são desenhados nem mostrados. Se as texturas enviadas neles ainda vão para o GS ou se o renderizador é ressincronizado de outro jeito fica para o contrato do runtime pronto para rollback._
4. _**VU1:** igual à primeira resolução: sem emulação da VU1 no build e uma guarda que registra e para em qualquer envio de microprograma da VU1 ou pacote PATH1/PATH2._
5. _**Desenho no nível do jogo (opção D):** desenhar camadas escolhidas (primeiro os sprites dos lutadores) a partir dos dados do próprio jogo, camada por camada, com o GS do PCSX2 desenhando o que ainda não estiver coberto. Fica para o mapa futuro de alta resolução e widescreen. Estudar os formatos de sprite e paleta que ela exige também serve para personagens novos._

_**Consequências e próximos passos (não são decisões à parte):** o README do Fixer exige o Visual Studio 2022 (MSVC) para a DLL; nosso runtime usa clang/MinGW, e a interface em C da DLL permite juntar os dois. Windows primeiro; os backends Vulkan/OpenGL/Metal do PCSX2 não estão na cópia do Fixer e teriam de ser trazidos do PCSX2 para Linux e Mac (a cópia mantém a organização de pastas do PCSX2). Verificar quando a peça entrar: velocidade com o `speed_report.py` na máquina do dono (GREEN a partir de 57 vsyncs/s) e atraso de controle com a fila da thread do GS no mínimo para jogar._

_**Descartados:** paraLLEl-GS (rodaria na NVIDIA do dono, mas quem joga online usa placas de todo tipo, e ele exige Vulkan moderno, com travamentos conhecidos em drivers AMD antigos; a apresentação pela nossa janela OpenGL acrescenta um quadro de atraso, não é o código do emulador de referência); renderizador próprio (mais trabalho e mais diferenças em relação ao emulador de referência); desenho no nível do jogo como base (precisa de um GS emulado por baixo de qualquer jeito e de engenharia reversa de cada camada); manter o GS na CPU numa thread separada (continua ~27 ms por vsync)._
