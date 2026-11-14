# VU1 and GS usage of the PS2 Release / Uso de VU1 e GS na versão de PS2

_Findings for [Measure the PS2 Release's VU1 and GS usage](../tickets/14-measure-vu1-gs-usage.md). English first, then Brazilian Portuguese. Only counts, hashes and feature names are recorded; nothing from inside the game. Measured on 2026-11-13 on the owner's machine with the owner playing, in two sessions (the second with the PS2-exclusive fighters unlocked). The captures, scripts and intermediate files stayed in `private/` (git-ignored)._

_Resultado do ticket. Inglês primeiro, português depois. Só contagens, hashes e nomes de recursos; nada de dentro do jogo. As capturas, os scripts e os arquivos intermediários ficaram em `private/`, que o git ignora._

## Summary

**The PS2 Release does not use VU1 microprograms at all in anything captured, including fights on two extra 3D stages, PS2-exclusive (NGBC-derived) fighters and a Leader special.** Every pixel reaches the GS through PATH3 (GIF DMA from main memory); there is no PATH1 (VU1 `XGKICK`) and no PATH2 (VIF1 `DIRECT`) traffic. VU1 micro memory never changed from its power-on contents between boot and the 3D-stage fight. VU0 is used in macro mode (vector instructions issued by the main CPU), not in micro mode. The graphics job is therefore a **GS-only job**: reproduce the GS command stream the main CPU builds, with a small and conventional feature set.

| Question | Answer |
|---|---|
| Distinct VU1 microprograms uploaded | **0** in 8 savestates and 11 GS dumps (VU1 micro memory identical to its power-on contents in every state, hash `5ff0987e41af` of the fill pattern) |
| Data paths to the GS | PATH3 only: 100% of 86.6 MB of GIF traffic across 11 dumps. PATH1 0 bytes, PATH2 0 bytes |
| VU0 micro mode | Not observed: VU0 micro memory all zero in every state. The executable has **1** `VCALLMSR` call site and **0** `VCALLMS`, plus **305** VU0 macro-mode instructions and **42** `CTC2` |
| Render-to-texture / framebuffer feedback | **None.** Only 2 draw targets per capture (the two display buffers); no texture read from a render target; no GS-to-GS copy; no GS-to-host readback |
| Depth | 32-bit Z (`Z32`) only, as both the stored state and the draws (`GEQUAL` test with writes, plus `ALWAYS` for clears). No `Z24`/`Z16` |
| Colour target | `CT32` only. No `CT24`/`CT16` targets |
| Palette formats | 4-bit and 8-bit indexed textures (`T4`, `T8`) with 32-bit and 16-bit palettes (`CT32`, `CT16`), CLUT storage mode CSM1 only. No `T8H`/`T4HL`/`T4HH` |
| Direct-colour textures | `CT32` and `CT16` |
| Blending | 2 equations: normal alpha blend `(Cs−Cd)·As+Cd` everywhere, and additive `(Cs−0)·As+Cd` on the 3D stages. No `PABE`, no `FBA`, colour clamping on (no wrap), no dithering |
| Tests | Alpha test `NOTEQUAL` with `KEEP` on fail (menus and 3D stages). No destination alpha test (`DATE`). No frame-buffer write masks |
| Texture sampling | `UV` (integer) coordinates only, including the 3D stages (no perspective `STQ`); bilinear filtering on a few dozen vertices per capture; no mipmaps; no region clamp/repeat; texture functions `TFX0` (modulate) and `TFX1` (decal), `TCC1` |
| Primitives | Triangles, triangle strips and sprites. No points, lines or fans |
| Display | Read circuit 2 only (`PMODE EN2`), no merge of two circuits |
| PCSX2 workarounds | GameDB entry: compatibility 5 (perfect); one hardware fix, `limit24BitDepth` mode 2 ("fixes flickering and missing textures"), confirmed applied in the session log. It concerns the host renderer's depth precision for this game's 32-bit depth, not a 24-bit format in the game |

## Captures

PCSX2 v2.8.2 (Windows x64 Qt, archive SHA-256 `7DFC829CA1994CC1045AC49F05E39B6CF968B72E6A374C40E05C2A2B4AC200B4`), portable, hardware renderer (Direct3D 12) with default settings, MTVU on. BIOS: the owner's own SCPH-30004R (PAL) dump. Disc: the owner's SLUS-21687 v1.00 image.

The owner played and, at each point, saved a single-frame GS dump (4 vsyncs each) and a savestate. First session: the main menu (twice), the options screen with the Arranged Option, character select, a fight on a regular stage (two points) and a fight on one extra 3D stage. Second session, with the PS2-exclusive fighters unlocked by a cheat code in PCSX2 (a CodeBreaker code decoded locally with cb2util, MIT; the cheat file stays in `private/`): a fight with PS2-exclusive fighters on another extra 3D stage, and Tung Fu Rue's Leader special in that fight. 11 dumps, 8 savestates.

| Scene class | Vertices per dump | Drawn with | Texture upload per dump |
|---|---|---|---|
| Menus and options (3 dumps) | ~30,200–30,300 | ~29,400 triangles with `T4`/`T8` textures (`CT32` palettes), depth tested; a few hundred strip and sprite vertices | 5.9 MB |
| Character select and regular-stage fights (4 dumps) | ~950–1,140 | Sprites and triangle strips, `CT16`/`CT32` and `T4`/`T8` (`CT16` palettes) textures, alpha blend, no depth test | 4.5–14.4 MB |
| Extra 3D stage fights (2 dumps, one with PS2-exclusive fighters) | ~60,800–69,800 | ~60,000–69,000 depth-tested triangles with `T8` textures (`CT32` palettes), alpha test, alpha blend and additive blend | 7.1–7.8 MB |
| Leader special on an extra 3D stage (2 dumps) | ~850 | Sprites and triangle strips only: the 3D stage is not drawn during the special | 4.3 MB |

The 2D scenes are dominated by **texture uploads**, not geometry: most of the GIF traffic is image data sent from main memory every frame (fighter sprites streamed in), so the renderer's texture upload and cache path will matter more for performance than its triangle throughput.

**Coverage.** The second session added the PS2-exclusive fighters, a second extra 3D stage and a Leader special; none of them brought a new GS feature, a VU1 upload or any PATH1/PATH2 traffic. Not seen: every fighter and stage individually, the other modes (Challenge, Edit, endings and cut-scenes). A VU1 path appearing there is unlikely; the runtime guard suggested below would catch it.

## What this changes for later tickets

- **[Decide how GS and VU1 graphics are reproduced](../tickets/16-gs-vu1-approach.md):** the VU1 half of the question disappears for the captured content. The choice narrows to how the GS command stream is drawn (emulate the GS behind the recompiled code, or translate its stream to a modern API), with a small feature set: no render-to-texture, no feedback, no readbacks, no channel shuffles, no `DATE`, two blend equations, `Z32`, palette textures and heavy per-frame texture uploads. A guard that logs any VU1 microprogram upload or PATH1/PATH2 packet would catch an unseen case.
- **[Decide the recompiler](../tickets/15-decide-recompiler.md):** PS2Recomp's known slow spot is VU1/GS; with no VU1 microcode, what matters is the main-CPU code, including the 305 VU0 macro instructions (vector math done by the main CPU), and the GS path.
- **Rollback:** with no VU1 or VU0 microprograms in use, the state to snapshot loses the VU micro memories as live state, and the renderer can stay a pure consumer of the GS stream, outside the simulation.

## Method

PCSX2's own single-frame GS dumps (format from PCSX2 `GSDump.h`/`GSDump.cpp` and `GSState::Freeze`, v2.8.2) were parsed with a Python script: initial GS registers from the dump's state block, then every GIF packet (PACKED, REGLIST and IMAGE modes, A+D writes, `PRIM`/`PRMODE`, `TEX2` palette updates) with the active context's registers recorded at each vertex kick. Savestates (zip, Zstandard entries decoded with PCSX2's bundled `zstd.dll`) gave VU0/VU1 micro memory and main memory; micro memory was split into routines at end-flag instructions and hashed, and main memory and the executable were scanned for VIF `MPG` commands matching micro memory. The executable was scanned word by word for `VCALLMS`, `VCALLMSR`, `CTC2` and COP2 macro instructions (a count, not a disassembly).

---

## Resumo (PT-BR)

- **A versão de PS2 não usa microprogramas da VU1** em nada do que foi capturado, nem em lutas em duas fases 3D extras, com lutadores exclusivos do PS2 (vindos do NGBC) e um especial de líder. Todo o desenho chega ao GS por um único caminho: a CPU principal monta os comandos e os manda por DMA (PATH3). A memória de programas da VU1 ficou igual à de quando o console liga, da abertura até a luta 3D.
- **A VU0 não roda programas próprios.** Ela é usada como coprocessador da CPU (305 instruções vetoriais no executável, 1 único ponto de chamada de microprograma, que nunca teve programa carregado).
- **O GS usa um conjunto pequeno e comum de recursos:** profundidade de 32 bits, alvo de cor de 32 bits, texturas com paleta de 4 e 8 bits, duas fórmulas de mistura (transparência normal e aditiva), teste de transparência e filtro bilinear em poucos lugares. **Não** desenha em textura, não lê o que já desenhou, não copia dentro da memória de vídeo e não devolve imagens para a CPU.
- **Ajuste do PCSX2:** só um, que limita a profundidade a 24 bits no renderizador do PC; é uma questão de precisão do emulador com a profundidade de 32 bits do jogo.
- **Nas cenas 2D, o peso está em subir texturas** (os sprites dos lutadores vão para a memória de vídeo a cada quadro), e não em desenhar triângulos.
- **Cobertura:** numa segunda sessão, com os lutadores exclusivos do PS2 liberados por um código de trapaça no PCSX2 (o arquivo fica em `private/`), entraram uma segunda fase 3D extra e o especial de líder do Tung Fu Rue. Nada disso trouxe recurso novo do GS nem uso da VU1. Durante o especial, o cenário 3D deixa de ser desenhado. Não foram vistos todos os lutadores e fases um a um, nem os outros modos (Challenge, Edit, finais e cenas animadas).
- **Consequência:** o trabalho gráfico vira "só o GS". O ticket 16 deixa de precisar decidir como reproduzir a VU1 e fica com a escolha de como desenhar os comandos do GS.
