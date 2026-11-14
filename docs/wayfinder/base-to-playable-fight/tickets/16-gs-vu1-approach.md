---
id: 16
title: Decide how GS and VU1 graphics are reproduced
type: grilling
status: open
assignee:
blocked_by: [06, 14, 15]
---

## Question

How does the port draw the Base Version's graphics? The GS and the VU1 microprograms are the hardest part of the PS2 Release ([Survey graphics and audio reimplementation options and their licenses](02-graphics-audio-options.md)). Options include emulating the GS behind the recompiled code, translating its command stream to a modern graphics API, and interpreting or recompiling the VU1 microprograms. Choose using the measurements in [Measure the PS2 Release's VU1 and GS usage](14-measure-vu1-gs-usage.md), the chosen recompiler, the licence decision, and the first decisive criterion: excellent performance with the NGBC-derived fighters. The renderer must also stay outside the simulation state that rollback saves and restores.

_PT-BR: como o port desenha o gráfico da versão-base? O GS e os microprogramas da VU1 são a parte mais difícil do PS2. Opções: emular o GS por trás do código recompilado, traduzir os comandos dele para uma API gráfica moderna, e interpretar ou recompilar os microprogramas da VU1. Escolher com base nas medições do ticket 14, no recompilador escolhido, na licença e no primeiro critério decisivo: desempenho excelente com os lutadores do NGBC. O desenho também precisa ficar fora do estado que o rollback salva e restaura._

**Input from [Measure the PS2 Release's VU1 and GS usage](14-measure-vu1-gs-usage.md) (2026-11-13):** no VU1 microprograms in anything captured (boot, menus, a 2D fight, fights on two extra 3D stages, the PS2-exclusive fighters and a Leader special), and all GS traffic comes by PATH3 from the main CPU. The VU1 half of this question disappears; what is left is how the GS command stream is drawn, with a small feature set (`Z32`, `CT32`, palette textures, two blend equations, no render-to-texture or readbacks) and heavy per-frame texture uploads in 2D scenes. Consider a guard that logs any VU1 microprogram upload or PATH1/PATH2 packet. / _Do ticket 14: nenhum microprograma de VU1 no que foi capturado; todo o desenho chega pela CPU principal. Isso vale também para os lutadores exclusivos do PS2, duas fases 3D e um especial de líder. A metade "VU1" desta pergunta some; sobra decidir como desenhar os comandos do GS, que usa poucos recursos, mas sobe muita textura por quadro nas cenas 2D._
