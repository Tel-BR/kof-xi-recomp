# GS renderer options after the reopening of ticket 16

_PT-BR: opções de renderizador do GS depois da reabertura do ticket 16. Cada seção traz o inglês primeiro e o português logo depois._

Researched on 2026-11-22 for [Decide how GS and VU1 graphics are reproduced](../tickets/16-gs-vu1-approach.md), from shallow clones of each project's default branch. Only public sources, commit ids, licences and line counts; nothing from the game.

_PT-BR: pesquisado em 22/11/2026 para o ticket 16, a partir de clones rasos do branch principal de cada projeto. Só fontes públicas, commits, licenças e contagens de linhas; nada do jogo._

## Starting point

- **Upstream PS2Recomp** (`ran-j/PS2Recomp`, still `e563698` on 2026-11-22): `ps2xRuntime/src/lib/gs/` holds `gs_cpu_backend.cpp`, `gs_frontend.cpp`, `ps2_gif_arbiter.cpp` and `ps2_gs_memory.cpp`. The only renderer is the CPU one.
- **Its cost on the owner's machine** ([diagnose-runtime-performance-audio.md](diagnose-runtime-performance-audio.md)): with the IOP fixed, about 27 ms per vsync against a 16.7 ms budget (87–92% of the one busy thread). Moving it to its own thread alone would still cap the game near 37 vsyncs/s.
- **What the game asks of the GS** ([measure-vu1-gs-usage.md](measure-vu1-gs-usage.md)): PATH3 only, no VU1 microcode, no render-to-texture or readbacks, `Z32`, palette textures, two blend equations, heavy per-frame texture uploads.

_PT-BR: o PS2Recomp oficial continua no `e563698` e só tem o renderizador na CPU. Na máquina do dono, com o IOP corrigido, ele leva ~27 ms por vsync (orçamento de 16,7 ms); só mudá-lo de thread ainda limitaria o jogo a ~37 vsyncs/s. O jogo pede pouco do GS: só PATH3, nenhum microcódigo de VU1, nenhuma leitura de volta, `Z32`, texturas com paleta, duas equações de blend e muito envio de textura por quadro._

## Options

| Option | Source checked | Licence | What it is | Platform |
| --- | --- | --- | --- | --- |
| A. PCSX2's hardware GS | [PS2Recomp-Fixer](https://github.com/w1284603830/PS2Recomp-Fixer/) `c5a7148` (fork of PS2Recomp `eb8688b`); PCSX2 `2954ebe` (2026-10-11) vendored in `third_party/src/pcsx2gs` | GPL-3.0 | PCSX2's hardware renderer built as `pcsx2gs.dll` with a C API (`pcsx2gs_api.h`, version 4): `gif(data, qwc)` takes the merged GIF stream, `vsync(regs)` composes and presents, plus `reset`, `read_fifo`, `save_vram`/`load_vram`, OSD and an in-game menu. The runtime side (`dod_pcsx2_gs.cpp`, ~1,000 lines) feeds it on its own GS thread, with at most two fields in flight | DX11/DX12, Windows; the README requires Visual Studio 2022 (MSVC). PCSX2's Vulkan/OpenGL/Metal backends are absent from the vendored tree (`GS/Renderers/` holds DX11, DX12, HW, Common, Null, SW); the tree keeps PCSX2's layout, so they could be brought in later |
| B. paraLLEl-GS | [Themaister/parallel-gs](https://github.com/Themaister/parallel-gs) `cc6184a` | LGPL-3.0-or-later | A GS emulated from scratch in Vulkan compute shaders; VRAM-exact, supersampling; not PCSX2's code | Vulkan with `descriptorIndexing`, timeline semaphores, 8/16-bit storage and full subgroups. BT3 reports AMD's proprietary driver crashing on Polaris/GCN and ships Mesa lavapipe (software Vulkan) as the Windows fallback; its presentation copies Vulkan frames into OpenGL with one frame of latency |
| C. A renderer of our own | [BT3-Recomp](https://github.com/z3xox/BT3-Recomp) `e22a34b` (OpenGL path) | GPL-3.0 | Translates GS commands to a modern API. BT3's `ps2_gs_gpu.cpp` plus `ps2_gs_gpu_renderer.cpp` are ~25,700 lines and carry a "whole family of render-target aliasing workarounds" that its paraLLEl-GS path does not need | Any |
| D. Engine-level drawing | BT3 "native renderer at the engine seam" (`docs/NATIVE-RENDER-SEAM.md`; `ps2_seam*.cpp`, ~6,300 lines, stage program only, characters not built) | — | Draws from the game's own data before it becomes GS commands. BT3 and the Guitar Hero 2 port found that coverage is incremental: whatever the native path does not cover still goes through an emulated GS into the same frame. BT3 calls it "a capability change, not a rescue" | Any |

**Effort to reach the first fight, roughly:** A is porting ~1,000 lines of glue and building the DLL; B is integrating the library plus moving presentation to Vulkan to avoid the extra frame; C is a renderer of BT3's scale (~25,700 lines); D is A plus reverse engineering of every drawing layer (below).

Other GS renderers seen in other recomps (CoreGS 2.0 Vulkan in GT4, D3D11/Vulkan in GTA VCS and Burnout 3, WebGPU compute in ps2-web) are variants of option C written for other games (source: Fixer's `docs/ECOSYSTEM_SURVEY.md`).

_PT-BR: A) o GS por hardware do PCSX2, empacotado pelo PS2Recomp-Fixer numa DLL com interface em C (recebe o fluxo de comandos do GIF e o fim de quadro), alimentada numa thread própria; DX11/DX12, Windows, o README exige Visual Studio 2022 (MSVC); os backends Vulkan/OpenGL/Metal do PCSX2 não estão na cópia e teriam de ser trazidos depois; GPL-3.0. B) paraLLEl-GS: GS escrito do zero em shaders de computação Vulkan, exato na memória de vídeo; exige Vulkan moderno; no BT3, drivers AMD antigos travam e a apresentação via OpenGL custa 1 quadro de atraso; LGPL-3.0. C) renderizador próprio, como o OpenGL do BT3 (~25,7 mil linhas, com uma família de remendos). D) desenho no nível do jogo, como a "costura" nativa do BT3 (~6,3 mil linhas só para o cenário); a cobertura é por camada e o resto continua passando por um GS emulado no mesmo quadro. Outros renderizadores de recomps (GT4, GTA VCS, Burnout 3, ps2-web) são variações da opção C feitas para outros jogos. Esforço até a primeira luta, por alto: A é trazer ~1.000 linhas de ligação e compilar a DLL; B é integrar a biblioteca e passar a apresentação para Vulkan; C é um renderizador do porte do BT3; D é A mais engenharia reversa de cada camada._

## Rollback

- The game never reads from the GS (ticket 14), so no renderer state belongs to the rollback state, whatever the option.
- Resimulating several frames in one host frame (4–8 in the first resolution) needs the game thread nearly free. With the CPU GS that is impossible (several × 27 ms); with A or B the GS work moves to the GPU and its own thread, and the recompiled game code is light (about 98% of EE cycles pass with every EE thread waiting).
- Frames resimulated without being shown may still upload textures. A and B keep GS memory exactly as the PS2 does, so those uploads can be fed while draws stay suppressed; with C that behaviour would have to be designed.
- **The whole Fixer as a base works against rollback:** VSync and alarms advance in real time (`IMPROVEMENTS.md` §2) and the IOP runs on its own host thread (§7). Both bring host timing into the simulation. The GS DLL alone is one-way and does not.

_PT-BR: o jogo nunca lê do GS, então nenhum estado do renderizador entra no rollback. Refazer vários quadros de uma vez (4 a 8 na primeira resolução) exige a thread do jogo quase livre: impossível com o GS na CPU, possível com A ou B. Quadros refeitos sem aparecer ainda podem enviar texturas; A e B emulam a memória do GS exatamente, então dá para mandar esses envios e continuar sem desenhar. O Fixer inteiro como base vai contra o rollback (VSync e alarmes no relógio real, IOP em thread própria); a DLL do GS sozinha é de mão única e não._

## Effort of option D for KOF XI

- No names anywhere in the executable ([inspect-code-structure.md](inspect-code-structure.md)), and the function list used for recompilation names no Sony graphics library (only kernel DMA and GS calls), so the drawing code is SNK's own and undocumented.
- Many separate layers, each its own seam: fighter sprites (palette textures, up to 14.4 MB uploaded per dump), 2D stage backgrounds, extra 3D stages (60,000–70,000 triangles), menus (~30,000 textured triangles), HUD and fonts, hit effects and super flashes, Leader specials, character select, endings.
- Undocumented data formats (`.UNI`, `.GRC`, `.PAL`); the Mad Gear Edition patch project maps memory, practice-mode data and menus, not the sprite and palette formats.
- The Verification Oracle compares the GS command stream ([ticket 07](../tickets/07-verification-oracle.md)); layers drawn natively bypass it and need another comparison.
- It always needs an emulated GS underneath for whatever it does not cover, so it extends A/B/C rather than replacing them. Its gains are high resolution and widescreen, which this map puts out of scope.

_PT-BR: custo da opção D no KOF XI: nenhum nome no executável e nenhuma biblioteca gráfica da Sony reconhecida, então o desenho é código próprio da SNK; muitas camadas separadas (sprites dos lutadores, cenários 2D, fases 3D, menus, HUD e fontes, efeitos, especiais, seleção, finais); formatos sem documentação (o projeto Mad Gear Edition mapeia memória, dados do modo treino e menus, não os formatos de sprite e paleta); o oráculo do ticket 07 não cobre camadas desenhadas por fora; e sempre precisa de um GS emulado por baixo, então estende A/B/C em vez de substituí-las. O ganho é alta resolução e widescreen, fora do escopo deste mapa._
