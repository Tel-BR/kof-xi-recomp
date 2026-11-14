---
id: 14
title: Measure the PS2 Release's VU1 and GS usage
type: task
status: closed
assignee: claude
blocked_by: []
research: ../research/measure-vu1-gs-usage.md
---

## Question

How big is the graphics job for the Base Version? AFK: in PCSX2, on the owner's machine, through boot, the menus and one Complete Fight (including one of the extra 3D stages), count the distinct VU1 microprograms the game uploads (by size and hash), whether VU0 runs in micro mode, and which GS features it relies on: render-to-texture or framebuffer feedback, 24-bit depth (the only PCSX2 fix listed for this game), palette formats, blending modes, and anything PCSX2 flags as a hardware-renderer workaround. Record counts, hashes and feature names only. This sizes [Decide how GS and VU1 graphics are reproduced](16-gs-vu1-approach.md).

_PT-BR: qual o tamanho do trabalho gráfico na versão-base? O agente usa o PCSX2 na máquina do dono, da abertura até uma luta completa (incluindo uma das fases 3D extras), e conta quantos microprogramas distintos de VU1 o jogo carrega (tamanho e hash), se a VU0 roda em modo micro e quais recursos do GS o jogo usa (desenhar em textura, profundidade de 24 bits, formatos de paleta, modos de mistura, ajustes que o PCSX2 aplica). Só contagens, hashes e nomes de recursos. Isso dimensiona o ticket 16._

## Resolution

Done on 2026-11-13 in PCSX2 v2.8.2 with the owner playing (menus, the Arranged Option screen, character select, a regular-stage fight, a fight on one extra 3D stage and, with the PS2-exclusive fighters unlocked by a cheat code, a fight on a second extra 3D stage including Tung Fu Rue's Leader special): 11 single-frame GS dumps and 8 savestates. Full findings: [measure-vu1-gs-usage.md](../research/measure-vu1-gs-usage.md).

- **VU1 microprograms: 0.** VU1 micro memory never left its power-on contents from boot to the 3D-stage fight, and all GS traffic is PATH3 (GIF DMA from main memory): no PATH1, no PATH2.
- **VU0: macro mode only.** Micro memory empty in every state; the executable has 1 `VCALLMSR` site, 305 VU0 macro instructions and 42 `CTC2`.
- **GS features:** `Z32` depth and `CT32` targets only; `T4`/`T8` textures with `CT32`/`CT16` palettes (CSM1) plus `CT32`/`CT16` direct textures; two blend equations (normal alpha, additive); alpha test `NOTEQUAL`; `UV` coordinates only; a little bilinear filtering; triangles, strips and sprites. **No** render-to-texture, framebuffer feedback, GS-to-GS copies, readbacks, `DATE`, write masks, fog, mipmaps or two-circuit merge.
- **PCSX2 workarounds:** only `limit24BitDepth` (mode 2), a host-precision fix for the game's 32-bit depth.
- **Performance shape:** 2D scenes draw ~1,000 vertices per dump but upload 4.5–14.4 MB of textures; the 3D stages draw ~60,000–69,000 triangles, and are not drawn during a Leader special.
- **Coverage:** the PS2-exclusive fighters, two extra 3D stages and a Leader special brought no new GS feature and no VU1 use. Not seen: every fighter and stage one by one, and the other modes (Challenge, Edit, endings, cut-scenes).

Consequence: the graphics job is GS-only. [Decide how GS and VU1 graphics are reproduced](16-gs-vu1-approach.md) and [Decide the recompiler](15-decide-recompiler.md) received a note.

_PT-BR: feito em 13/11/2026 no PCSX2 v2.8.2, com o dono jogando (menus, a tela da opção Arranged, seleção de personagens, uma luta em fase comum, uma luta numa fase 3D extra e, com os lutadores exclusivos do PS2 liberados por trapaça, uma luta em outra fase 3D extra com o especial de líder do Tung Fu Rue): 11 capturas de quadro e 8 estados salvos. **A VU1 não roda nenhum microprograma**: a memória de programas dela ficou como no boot do console do começo ao fim, e todo o desenho chega ao GS por DMA vindo da CPU principal. **A VU0 só é usada como coprocessador da CPU**, sem programas próprios. **O GS usa poucos recursos e comuns**: profundidade de 32 bits, texturas com paleta de 4 e 8 bits, transparência normal e aditiva, teste de transparência; nada de desenhar em textura, ler o que foi desenhado, copiar dentro da memória de vídeo ou devolver imagens à CPU. O único ajuste do PCSX2 é de precisão da profundidade no PC. Nas cenas 2D o peso está em subir texturas a cada quadro, não em desenhar triângulos. Os lutadores exclusivos do PS2, duas fases 3D e um especial de líder não trouxeram nada novo; não foram vistos todos os lutadores e fases um a um, nem os outros modos. Consequência: o trabalho gráfico é "só o GS"; os tickets 15 e 16 receberam uma nota._
