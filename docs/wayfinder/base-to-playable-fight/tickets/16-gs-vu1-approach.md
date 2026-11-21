---
id: 16
title: Decide how GS and VU1 graphics are reproduced
type: grilling
status: closed
assignee: Tel-BR
blocked_by: [06, 14, 15]
---

## Question

How does the port draw the Base Version's graphics? The GS and the VU1 microprograms are the hardest part of the PS2 Release ([Survey graphics and audio reimplementation options and their licenses](02-graphics-audio-options.md)). Options include emulating the GS behind the recompiled code, translating its command stream to a modern graphics API, and interpreting or recompiling the VU1 microprograms. Choose using the measurements in [Measure the PS2 Release's VU1 and GS usage](14-measure-vu1-gs-usage.md), the chosen recompiler, the licence decision, and the first decisive criterion: excellent performance with the NGBC-derived fighters. The renderer must also stay outside the simulation state that rollback saves and restores.

_PT-BR: como o port desenha o gráfico da versão-base? O GS e os microprogramas da VU1 são a parte mais difícil do PS2. Opções: emular o GS por trás do código recompilado, traduzir os comandos dele para uma API gráfica moderna, e interpretar ou recompilar os microprogramas da VU1. Escolher com base nas medições do ticket 14, no recompilador escolhido, na licença e no primeiro critério decisivo: desempenho excelente com os lutadores do NGBC. O desenho também precisa ficar fora do estado que o rollback salva e restaura._

## Resolution

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
