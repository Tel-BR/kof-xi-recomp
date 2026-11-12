---
id: 14
title: Measure the PS2 Release's VU1 and GS usage
type: task
status: open
assignee:
blocked_by: []
---

## Question

How big is the graphics job for the Base Version? AFK: in PCSX2, on the owner's machine, through boot, the menus and one Complete Fight (including one of the extra 3D stages), count the distinct VU1 microprograms the game uploads (by size and hash), whether VU0 runs in micro mode, and which GS features it relies on: render-to-texture or framebuffer feedback, 24-bit depth (the only PCSX2 fix listed for this game), palette formats, blending modes, and anything PCSX2 flags as a hardware-renderer workaround. Record counts, hashes and feature names only. This sizes [Decide how GS and VU1 graphics are reproduced](16-gs-vu1-approach.md).

_PT-BR: qual o tamanho do trabalho gráfico na versão-base? O agente usa o PCSX2 na máquina do dono, da abertura até uma luta completa (incluindo uma das fases 3D extras), e conta quantos microprogramas distintos de VU1 o jogo carrega (tamanho e hash), se a VU0 roda em modo micro e quais recursos do GS o jogo usa (desenhar em textura, profundidade de 24 bits, formatos de paleta, modos de mistura, ajustes que o PCSX2 aplica). Só contagens, hashes e nomes de recursos. Isso dimensiona o ticket 16._
