# Graphics and audio reimplementation options, and their licenses

Ticket: *"Survey graphics and audio reimplementation options and their licenses."*
Research date: 2026-11-11. Licenses were read from each repository's LICENSE/COPYING file and per-file SPDX/header comments, not from summaries. This document does **not** pick a base version or a license.

---

## Resumo em português

- **Situação:** o processador principal do jogo vira código C/C++ (recompilação estática). Mas o chip de vídeo e o chip de som do console precisam ser **reimplementados à parte**, e é aí que fica a maior parte do trabalho e o risco de licença.
- **Como os outros fazem:** os projetos de referência (N64, Xbox 360, PS2, Dreamcast) usam três caminhos: (1) imitar o chip de vídeo “de verdade” por software; (2) ler a lista de desenhos que o jogo manda para o chip e redesenhar com Vulkan/DirectX; (3) também recompilar os pequenos programas que rodam nos coprocessadores (os “microprogramas” de vídeo e o “driver” de som).
- **PS2 é mais pesado:** além do chip de vídeo (GS), o jogo usa as unidades vetoriais VU1, que rodam programas próprios para calcular a geometria e também teriam de ser recompilados ou interpretados. O som (SPU2) é controlado por um segundo processador (IOP) que roda módulos do próprio jogo.
- **Atomiswave/Dreamcast é mais enxuto no vídeo:** o processador principal já faz a geometria, e o chip de vídeo (PowerVR2) recebe listas prontas de triângulos. No som, o chip AICA tem um processador ARM7 com driver próprio, que um projeto recente (Street Fighter Alpha 3) recompilou com sucesso.
- **Peças prontas com licença permissiva (permitem manter o MIT):** Play! (emulador de PS2, BSD), SDL3, plume, bgfx, Dawn, RT64 (só serve para N64), Deecy (Dreamcast, MIT, em Zig) e boa parte do antigo reicast (BSD, mas com trechos GPL misturados).
- **Peças mais maduras são GPL:** PCSX2 (GPLv3), Flycast (GPLv2 “ou posterior”), PS2Recomp (GPLv3), DobieStation (GPLv3, parado desde 2021). paraLLEl-GS (vídeo de PS2 por GPU) é LGPLv3.
- **O que muda se virar GPL:** o projeto inteiro passa a ter de ser distribuído sob GPL, com código-fonte; ninguém poderá fechar o código depois; e voltar para MIT exigirá autorização de todos que contribuíram. Já houve um caso igual: o dcrecomp (Dreamcast) era MIT e virou GPL-2.0 em outubro de 2026 por ter aproveitado código do Flycast.
- **Armadilha:** GPLv2 “somente” não se mistura com GPLv3 nem com Apache-2.0. O Flycast é “v2 ou posterior”, então se mistura com GPLv3. Já o dcrecomp diz só “versão 2”.
- **Fato a confirmar:** o KOF XI saiu oficialmente para arcade **Atomiswave** (hardware derivado do Dreamcast) e PS2. A versão “Dreamcast” é uma conversão caseira de 2020, não um lançamento oficial.

---

## 0. Platform facts that frame the question

- KOF XI shipped on **Atomiswave** arcade (Japan, 2005-10-26) and **PlayStation 2** (Japan 2006-06-22; PAL 2007-07-06; NA 2007-11-13). Wikipedia lists no official Dreamcast release. It notes that "a homebrew conversion was released for the Dreamcast" in 2020. [Wikipedia: KOF XI]
- Atomiswave is "based on Sega's Dreamcast": SH-4 at 200 MHz, PowerVR2 at 100 MHz, Yamaha AICA with an ARM7 sound processor. [Wikipedia: Atomiswave] Flycast emulates Dreamcast, Naomi, Naomi 2 and Atomiswave. [Flycast README]
- So the "Dreamcast/Atomiswave" candidate means SH-4 + PowerVR2 (Holly/CLX2) + AICA. The difference between the arcade build and the homebrew conversion matters for I/O and boot code, but not for the GPU and audio chips this ticket covers.

---

## 1. How existing static-recomp projects handle GPU and audio

### 1.1 N64Recomp + RT64 + N64ModernRuntime (Zelda 64: Recompiled)

- **Split licensing.** The N64Recomp tool is **MIT** and RT64 is **MIT**. N64ModernRuntime (ultramodern + librecomp) is **GPLv3**, and so is the game project Zelda64Recomp. [N64Recomp LICENSE] [RT64 LICENSE] [N64ModernRuntime COPYING] [Zelda64Recomp COPYING]
- **Graphics: high-level display-list translation plus an accurate RDP model.** RT64 has per-microcode display-list decoders (`src/gbi/rt64_gbi_f3dex2.cpp`, `..._s2dex.cpp`, etc.). It interprets the game's graphics command lists itself and does not run the RSP graphics microcode. Vertex work by the RSP is "performed by a highly parallel compute shader in the GPU". RDP operations are deferred and RDP behaviour (TMEM loads, framebuffer reinterpretation) is reproduced accurately. Backends are D3D12, Vulkan and Metal, with ubershaders "to guarantee no stutters due to pipeline compilation." [RT64 README] [RT64 src/gbi]
- **Audio: the coprocessor code is recompiled.** The RSP audio microcode is statically recompiled with N64Recomp's `RSPRecomp`. Zelda64Recomp builds `rsp/aspMain.cpp` and `rsp/njpgdspMain.cpp`. ultramodern then passes the PCM output to host callbacks (`queue_audio_buffer`, `audio_callbacks_t`). [N64Recomp README §RSP Microcode Support] [Zelda64Recomp CMakeLists.txt] [N64ModernRuntime ultramodern.hpp]
- **Relevance:** RT64 is specific to N64 (RDP/GBI) and can't render GS or PVR2. Two ideas carry over: its architecture (deferred frames, ubershaders, dual native/high-res renderers), and the pattern of recompiling coprocessor code (RSP microcode → C++), which maps directly onto VU1 microprograms and the AICA ARM7 driver.

### 1.2 XenonRecomp / XenosRecomp / UnleashedRecomp

- **Licensing:** XenonRecomp (PPC → C++) and XenosRecomp (shaders → HLSL) are **MIT**. UnleashedRecomp (the game port) is **GPLv3**. plume, its rendering abstraction layer, is **MIT**. [XenonRecomp LICENSE.md] [XenosRecomp LICENSE.md] [UnleashedRecomp COPYING] [plume LICENSE]
- **Graphics: the game's graphics API is hooked; the GPU is not emulated.** XenosRecomp describes Unleashed as "a recompilation project that implements a translation layer for the renderer rather than emulating the Xbox 360 GPU". In `gpu/video.cpp`, guest D3D device calls (`SetRenderState`, `DrawPrimitive`, …) become host render commands. Xenos shader binaries are converted ahead of time to HLSL, then to DXIL/SPIR-V with DXC. Pipelines are compiled during asset loading, so there are "no stutters during gameplay". [XenosRecomp README] [UnleashedRecomp README] [UnleashedRecomp gpu/video.cpp]
- **Audio:** the game's own XAudio render-driver frames are byte-swapped and submitted through an SDL driver (`apu/driver/sdl2_driver.cpp`). `XMACreateContext`/`XMAReleaseContext` are stubs. XenonRecomp notes that MMIO "typically used for hardware operations such as XMA decoding, is currently unimplemented." [UnleashedRecomp apu/audio.cpp, kernel/imports.cpp] [XenonRecomp README]
- **Relevance:** Xenos is a programmable-shader GPU behind a D3D-like API, so XenosRecomp itself doesn't apply to GS or PVR2, which are fixed-function and have no shaders. The pattern does apply: hook at the game's own render API, if the game has one, and compile pipelines ahead of time.

### 1.3 PS2Recomp (ran-j/PS2Recomp)

- **License: GPLv3 for the whole repository**, including the recompiler, runtime and IOP module. [PS2Recomp LICENSE]
- **What it does today** (commit `e563698`, 2026-10-22):
  - Translates R5900 to C++, including MMI and VU0 macro mode via SSE/AVX. [README] [ps2xRuntime/Readme.md]
  - **GS:** a software GS on the CPU. A `GSRasterBackend` interface (`gs_backend.h`) has one implementation, `gs_cpu_backend.cpp` (~2k lines), plus a GIF arbiter and GS memory/swizzle code. Frames are uploaded to a raylib texture for display. [ps2xRuntime/src/lib/gs/*, ps2_runtime.cpp]
  - **VU1/VIF1:** interpreted (`VU1Interpreter` in `ps2_vu1.h`, `ps2_vif1_interpreter.cpp`). VU1 microcode is **not** statically recompiled. The recompiler has a `gif_dma_kick_analyzer`. [ps2xRuntime/include/runtime/ps2_vu1.h] [ps2xRecomp/include]
  - **IOP/audio:** `ps2xIOP` runs the game's original IRX modules on an R3000A interpreter. Generic HLE services (LIBSD `0x80000701`, MCSERV, DBCMAN) are used when no IRX provides them. Audio decodes VAG/ADPCM transfers and plays samples through raylib (`PS2AudioBackend::onVagTransfer`, `play`). There is no SPU2 voice/mixer model. [ps2xIOP/README.md] [ps2_audio.h]
  - Its own README says: "Performance is very bad for VU and GS" and "Hardware emulation is partial and many paths are stubbed." It cites PCSX2 as the "Reference for runtime". [PS2Recomp README]
- **Summary:** it emulates the GS at a low level in software, interprets VU1, runs the IOP at a low level, and uses high-level emulation for the sound library. It does not translate draw lists into a modern GPU API.

### 1.4 Dreamcast / SH-4 native-port efforts

| Project | License | Graphics | Audio | Status (as read) |
|---|---|---|---|---|
| **SFA3 Native** (Street Fighter Alpha 3 DC) | GPL-3.0-or-later (own code) | Own TA parser (`runtime/ta.c`) decodes the TA parameter stream into vertex/strip lists. Own Vulkan backend (`vk_renderer.c`) draws "decoded PowerVR display lists at a higher internal resolution" | ARM7 sound driver **statically recompiled** (`tools/recomp/arm.py`: "The whole driver becomes one C function, arm_execute(budget)"). Own 64-voice PCM/ADPCM synth in `aica.c`, streamed to SDL3 | Playable, with released setup app; a 2D fighting game, so the closest genre analogue. [SFA3 README] [SFA3 runtime/*] |
| **dcrecomp** (framework) | **GPL-2.0** (NOTICE says "version 2"; "published as MIT until 2026-10-20") | TA FIFO parser + OpenGL 3.3 backend, "Basic (colored triangles, blending)" | "AICA sound: Stub" | Alpha. HAL "derived from" Flycast, which "is why dcrecomp is GPL-2.0". It vendored Flycast code from 2026-03-25 to 2026-08-20. [dcrecomp README] [dcrecomp NOTICE] |
| **chuchu** (ChuChu Rocket!, on dcrecomp) | MIT (repo LICENSE) | Flat-shaded triangles, no textures yet | Real MANATEE.DRV runs on an **interpreted** ARM7; "64-channel mixer is not implemented" | Boots to its main loop, ~28 fps. [chuchu README] |
| **KatanaRecomp** (Sonic Adventure) | not verified | SH-4 → C++ via an IR (per dcrecomp credits) | not verified | Repository not reachable from this session. [dcrecomp README] |

### 1.5 Synthesis: the four approaches

1. **Low-level GPU emulation behind recompiled CPU code.** The GPU's registers, VRAM and rasterizer behaviour are modelled, and the recompiled code writes to them as it did on hardware. Examples: PS2Recomp's CPU GS, dcrecomp's planned Flycast backend.
2. **Command-stream translation.** The stream the CPU feeds the GPU (GIF packets for GS, the TA parameter stream for PVR2, GBI display lists for N64) is decoded and redrawn with Vulkan/D3D12. Examples: RT64, SFA3 Native, Flycast's renderers, Play!'s GS handlers.
3. **Game-API hooking.** The game's own render functions are replaced by host code. Example: UnleashedRecomp. This only works where the game calls a recognisable graphics library.
4. **Coprocessor code recompilation.** The small programs that run on coprocessors are recompiled as well. Examples: N64 RSP audio (`aspMain`), SFA3's AICA ARM7 driver. For the PS2 this would be VU1 microprograms, and the IOP IRX modules or the SPU2 driver.

---

## 2. Reusable components and their licenses

"Keeps MIT?" answers one question: can the component be linked or copied into an MIT project without relicensing that project? Attribution and notice requirements still apply to all of them.

| Component | Platform | License (as read) | Keeps MIT? | Notes |
|---|---|---|---|---|
| PCSX2 GS renderers (DX11/DX12/Metal/OpenGL/Vulkan/SW) and SPU2 | PS2 | **GPL-3.0-or-later** (SPDX `GPL-3.0+` in file headers) | No | Most mature PS2 GS/SPU2; active (commit 2026-11-10). [PCSX2 COPYING.GPLv3, GS/SPU2 headers] |
| Play! (`Source/gs/GSH_Vulkan`, `GSH_OpenGL`; `Iop_Spu2_Core`, `Iop_LibSd`; VU JIT `VuExecutor`) | PS2 | **BSD-2-Clause** (License.txt); its deps Play--Framework and Play--CodeGen are also BSD-2 | Yes | Active (commit 2026-10-24). Per-file headers are absent, so the repo license governs. Other submodules (Nuanceur, libchdr, AltKit, Play-Dependencies) were not audited. [Play! License.txt] [Framework/CodeGen License.txt] |
| libretro Play! core | PS2 | BSD-2 (same license text) | Yes | [libretro/Play- License.txt] |
| DobieStation | PS2 | **GPLv3** | No | Last commit 2021-04-21. [DobieStation LICENSE] |
| paraLLEl-GS (Vulkan compute GS) | PS2 | **LGPL-3.0-or-later**; README: "dual-licensing may be possible"; "External contributions are currently not accepted" | Partly (see §4.4) | Standalone, "does not use GSdx from PCSX2"; supports SSAA. The author's blog notes "some kind of integration into an emulator needs to happen". Its submodule Granite is MIT. [paraLLEl-GS README, COPYING.LGPLv3] [Themaister blog] |
| PS2Recomp runtime (GS CPU backend, VU1/VIF1 interpreters, ps2xIOP) | PS2 | **GPLv3** | No | Experimental. [PS2Recomp LICENSE] |
| Flycast renderers (`core/rend/{gles,gl4,vulkan,dx9,dx11}`), PVR/TA (`core/hw/pvr`), AICA + DSP (`core/hw/aica`), ARM7 interp/JIT (`core/hw/arm7`) | DC/AW | Repository LICENSE is GPLv2 text. 126 files carry "version 2 of the License, or (at your option) any later version"; many files have no header | No | Most mature DC/Atomiswave code; active (commit 2026-11-09). [Flycast LICENSE, file headers] |
| reicast / libswirl | DC/AW | Top-level LICENSE **BSD-3-Clause**; 366 files tagged `#include "license/bsd"`. A `gpl/` tree remains (lxdream `tacore`, vba-arm `arm-new.h`, xbrz), and `hw/arm7/arm7.cpp`, `hw/pvr/pvr_mem.cpp` and `rend/TexCache.cpp` **include those GPL files** | Only after file-by-file audit | EOL ("This project is no longer active"). CONTRIBUTING lists GPL-only portions (nulldc team, contract work, contributors). [reicast LICENSE, docs/CONTRIBUTING.md, libswirl sources] |
| redream | DC | Old GitHub snapshot is **GPLv3** with an ICLA (last commit 2018-04-18). Current releases are closed source ("went closed-source in January 2018"; Lite free, Premium paid) | No (old snapshot GPLv3; current closed) | [redream GitHub LICENSE.txt, README] [Emulation General Wiki] |
| lxdream | DC | **GPLv2** | No | [lxdream COPYING] |
| Deecy | DC | **MIT** ("Rest is MIT"; MAME-derived parts BSD-3) | Yes | Experimental emulator written in Zig; renders through WebGPU (a fork of zig-gamedev `zgpu`). Using it from C/C++ means porting the logic. Its README lists missing PVR features (exclusion modifier volumes, fog LUT mode 2, …). [Deecy README, LICENSE, build.zig.zon] |
| dcrecomp | DC | **GPL-2.0** (MIT until 2026-10-20) | No | [dcrecomp README, NOTICE] |
| SFA3 Native runtime | DC | **GPL-3.0-or-later** | No | [SFA3 README §License] |
| RT64 | N64 only | **MIT** | Yes | Not usable for GS or PVR2; useful as an architecture reference. [RT64 LICENSE] |
| N64ModernRuntime | N64 | **GPLv3** | No | [N64ModernRuntime COPYING] |
| XenonRecomp / XenosRecomp | X360 | **MIT** | Yes | Not applicable to GS or PVR2 (no shaders). [LICENSE.md files] |
| plume (RHI: D3D12, Vulkan; Metal planned) | host | **MIT** | Yes | Used by UnleashedRecomp. [plume LICENSE] [UnleashedRecomp README] |
| SDL3 (incl. SDL GPU: Vulkan, D3D12, Metal) | host | **zlib** | Yes | SDL GPU needs per-backend shader formats; SDL_shadercross (zlib) cross-compiles them. [SDL LICENSE.txt] [SDL wiki CategoryGPU] [SDL_shadercross LICENSE.txt] |
| SDL_mixer | host | zlib | Yes | [SDL_mixer LICENSE.txt] |
| raylib | host | zlib | Yes | Used by PS2Recomp. [raylib LICENSE] |
| bgfx | host | **BSD-2-Clause** | Yes | [bgfx LICENSE] |
| Dawn (WebGPU) | host | **BSD-3-Clause** | Yes | [Dawn LICENSE] |
| wgpu | host | **MIT or Apache-2.0** (dual) | Yes | [wgpu LICENSE.MIT / LICENSE.APACHE] |
| SPIRV-Cross | host tool | **Apache-2.0** | Yes (but see §4.3 for GPLv2) | [SPIRV-Cross LICENSE] |
| DirectXShaderCompiler | host tool | University of Illinois/NCSA (LLVM) | Yes | [DXC LICENSE.TXT] |
| Vulkan-Headers | host | Apache-2.0 for some files (repo states files "fall under one of these licenses") | Yes | [Vulkan-Headers LICENSE.md] |
| libretro API header (`libretro.h`) | host | **MIT** (header only; each core has its own license) | Yes | [libretro.h] |
| xenia | X360 | BSD-3-style | Yes | Reference only. [xenia LICENSE] |

---

## 3. What each platform's GPU and audio reimplementation requires

### 3.1 PS2 (EE + VU0/VU1 + GIF/VIF + GS + IOP/SPU2)

**GS (Graphics Synthesizer)**
- A fixed-function rasterizer with 4 MB embedded VRAM (framebuffer, textures and Z all live there). It does no vertex transform: "The VU1 unit is supposed to do transforms and clipping". It is a "DDA, i.e. a scanline rasterizer" with D3D9-style raster rules. [ps2tek] [Themaister blog] [Copetti PS2]
- It is fed through the **GIF** over three paths: PATH1 (VU1 `XGKICK`, highest priority), PATH2 (VIF1 `DIRECT/DIRECTHL`) and PATH3 (GIF DMA channel 2). [ps2tek]
- A reimplementation needs:
  - GIFtag/packet parsing and the GS register set;
  - VRAM swizzle formats (PSMCT32/16, PSMT8/4, CLUTs; see PS2Recomp's `ps2_gs_psm*.h`);
  - local↔host transfers;
  - the blend/alpha/destination-alpha/Z-test pipeline;
  - CRTC output.
- The hard part is **feedback loops**, where games sample what they just rendered: "the biggest challenge". [Themaister blog]
- There are two broad routes. One is a low-level model of VRAM (software, or compute shaders as in paraLLEl-GS). The other is a "hardware renderer" that maps GS draws to GPU draws with texture-cache heuristics (the PCSX2 HW and Play! GSH_Vulkan/OpenGL style).

**VU1 / VIF1 (geometry)**
- VU1 is a SIMD float processor with its own code and data memory (16 KB each per the ps2tek memory map). It "runs only in Micromode and is often responsible for building Display Lists". VIF1 "decompresses vector data, uploads microprograms to the VUs, and sends graphical data to the GIF." [ps2tek] [Copetti PS2]
- **VU1 microprograms are separate machine code** uploaded by the game at runtime, so the EE recompiler does not cover them. The options are:
  - (a) a static VU1 recompiler, the analogue of N64's RSPRecomp. VU1 is VLIW (upper and lower instruction per cycle) with pipeline-visible timing (Q/P registers, flags), which makes this harder than a scalar ISA;
  - (b) an interpreter (as in PS2Recomp) or a JIT (Play!'s `VuExecutor`, PCSX2 microVU);
  - (c) per-program high-level emulation: hand-write C++ equivalents for each microprogram the game uploads.
- **VU0** in macro mode is COP2 code inside EE functions, which PS2Recomp already translates. VU0 micro mode, if the game uses it, has the same issue as VU1.

**SPU2 / IOP (audio)**
- SPU2 has 48 voices (24 per core) and 2 MB of sound memory. The IOP gives access to it, and its registers sit only in the IOP memory map. [Copetti PS2] [ps2tek]
- Games load their own IRX modules on the IOP and talk to them over SIF RPC. Option (c) below therefore depends on which driver and middleware modules the game loads, which is an open question.
- Options:
  - (a) Low-level: run the game's IRX modules on an R3000A interpreter or recompiler and emulate the SPU2 voices, ADSR, reverb and DMA (PCSX2 SPU2, Play! `Iop_Spu2_Core`).
  - (b) High-level: implement the RPC services the EE calls (for example LIBSD) and decode ADPCM/VAG directly. PS2Recomp does this for LIBSD, and Play! has `Iop_LibSd`.
  - (c) Statically recompile the IRX modules (R3000A) as well.

### 3.2 Atomiswave / Dreamcast (SH-4 + Holly/PowerVR2 + AICA)

**PowerVR2 (CLX2 in Holly)**
- A tile-based deferred renderer. The Tile Accelerator sorts geometry into 32×32 tile bins and "Generates the Display Lists". The hardware sorts translucent primitives automatically. "The GPU only covers the tasks of a rasteriser", so transforms run on the SH-4 in game code, which the CPU recompiler already covers. [Copetti Dreamcast]
- Games build opaque and translucent lists (KallistiOS names `PVR_LIST_OP_POLY` and `PVR_LIST_TR_POLY`). Punch-through lists and modifier volumes exist too; see Deecy's missing-feature list and Flycast's `ta.cpp`. [dreamcast.wiki PowerVR Introduction] [Deecy README]
- The CPU writes the TA parameter stream through store queues or CH2-DMA. [chuchu README]
- A reimplementation needs:
  - a TA parameter decoder: global/polygon/sprite/vertex parameter control words, 18 vertex types (dcrecomp's count), strips;
  - region array and ISP/TSP state;
  - texture formats (twiddled, VQ-compressed, palettes);
  - per-pixel translucency sorting, or an order-independent-transparency approximation (redream needs OpenGL 4.3 for OIT, per Emulation General);
  - modifier volumes (shadows), fog tables and framebuffer write-back.
- Because geometry arrives already transformed, the GPU side is mostly decoding the TA stream and redrawing it. SFA3 Native and Flycast both follow this design.

**AICA (audio)**
- 64 channels with a DSP and mixer, controlled by an ARM7DI that runs a small driver stored in 2 MB of audio SDRAM, "filled by the main CPU using DMA". [Copetti Dreamcast] [Wikipedia: Atomiswave]
- Options:
  - (a) Statically recompile the ARM7 driver, as SFA3 Native does, and implement the 64-voice PCM/ADPCM synthesizer, envelopes, timers and interrupts. The AICA DSP effects are needed only if the game uses them.
  - (b) Interpret the ARM7, as chuchu does, which still needs the mixer.
  - (c) High-level: intercept the SH-4-side sound commands and play samples directly. This is game-specific.

---

## 4. GPL relicensing consequences, in plain terms

This section is not legal advice. It paraphrases the license texts cited.

### 4.1 What changes if KOF XI Recomp becomes GPL to reuse emulator code

- **The whole combined program must be GPL.** GPLv3 §5(c): "You must license the entire work, as a whole, under this License … regardless of how they are packaged." GPLv2 §6: "You may not impose any further restrictions". Permissive parts (MIT/BSD/zlib) can stay in the tree under their own notices, but the distributed program as a whole is GPL. [GPLv3 text] [GPLv2 text]
- **Binaries must come with source.** Anyone who distributes a binary must also provide the "Corresponding Source", which includes build scripts. [GPLv3 §1, §6]
- **Game data is unaffected.** The GPL covers the project's code only. GPLv3 §2: "The output from running a covered work is covered by this License only if the output, given its content, constitutes a covered work." SFA3 Native states the same split explicitly. Generated C from the user's own disc is never distributed under the "no game data" rule in any case. [GPLv3 §2] [SFA3 README]
- **Contributors:**
  - Existing MIT code can be absorbed into a GPL project, because MIT grants the right "to … sublicense". [MIT text in N64Recomp LICENSE]
  - New contributions after the switch are GPL.
  - Going back to MIT later would need every GPL contributor's permission, or a rewrite of their code. reicast's CONTRIBUTING shows this cost in practice ("We'll have to rewrite the parts that we can't get permission for"), and redream used an ICLA to keep that option open. [reicast docs/CONTRIBUTING.md] [redream ICLA.md]
- **No closed or commercial-exclusive fork.** Nobody, including the owner, can ship a proprietary build without first holding all copyrights.
- **Precedent:** dcrecomp moved from MIT to GPL-2.0 on 2026-10-20 because its HAL was derived from Flycast. Its NOTICE also records a period when Flycast code was vendored and later removed. [dcrecomp README, NOTICE]
- **"Reading" versus "copying":** dcrecomp treats code "written from reading Flycast's source" as derived. Projects that want to stay permissive usually rely on hardware documentation (ps2tek, Copetti, KallistiOS, dreamcast.wiki, Neill Corlett's AICA notes) and permissive references (Play!, Deecy) instead.

### 4.2 GPLv2-only vs GPLv3

- "v2 **or later**" code can be used under GPLv3, so it combines with GPLv3 code. GPLv2 §9 and GPLv3 §14 both give that option. [GPLv2 §9] [GPLv3 §14]
- **GPLv2-only** code cannot be combined with GPLv3 code. Each license forbids the extra restrictions the other adds.
- Many Flycast files say "version 2 … or (at your option) any later version", but the top-level file is the GPLv2 text and many files carry no header. Before combining Flycast with GPLv3 code such as PCSX2 or PS2Recomp, audit the files you use. GPLv2 §9 also says that if no version is specified, "you may choose any version ever published".
- dcrecomp's NOTICE says "version 2" with no "or later", so its own code reads as GPLv2-only and cannot be mixed with GPLv3 or LGPLv3 code.

### 4.3 Apache-2.0 and LGPL pitfalls

- **Apache-2.0 + GPLv2:** "the FSF has never considered the Apache License to be compatible with GPL version 2". Apache-2.0 code "can … be included in GPLv3 projects". [Apache GPL-compatibility page]
  - This matters for SPIRV-Cross and for Apache-licensed Vulkan-Headers files in a GPLv2-only build. wgpu avoids the issue through its MIT option.
- **LGPLv3 (paraLLEl-GS) inside an MIT project:** allowed. LGPLv3 §4 ("Combined Works") lets the application keep its own license, provided you:
  - give notice that the library is used, and ship the GPL and LGPL texts;
  - **either** link it as a shared library that users can replace, **or** provide the materials users need to relink the application against a modified version.

  LGPLv3 is **not** compatible with GPLv2-only. [LGPLv3 text]

---

## 5. Neutral option table

Effort scale: **L** = integrate an existing library; **M** = adapt existing code or write a modest subsystem; **H** = write a substantial subsystem; **VH** = new research-grade tooling. "Keeps MIT" assumes the component is used as licensed, without a separate agreement.

| # | Option | Platform | License impact | Effort | Maturity of the reused part |
|---|---|---|---|---|---|
| G1 | Own GS implementation (GIF parser + GS on SDL3 GPU/plume/Vulkan), using docs and BSD Play! as reference | PS2 | Keeps MIT | H | n/a (new code) |
| G2 | Port or adapt Play! GSH_Vulkan/OpenGL | PS2 | Keeps MIT (BSD-2 notice) | M–H | Active emulator (2026-10) |
| G3 | Link paraLLEl-GS | PS2 | MIT app + LGPLv3 library obligations; or GPL; or negotiate dual license | M | Standalone library; external contributions closed |
| G4 | Reuse PCSX2 GS renderers | PS2 | Forces GPLv3+ | M–H (tightly coupled to the emulator) | Most mature PS2 GS |
| G5 | Reuse PS2Recomp CPU GS backend | PS2 | Forces GPLv3 | M | Experimental; "very bad" GS performance per README |
| G6 | Reuse DobieStation GS | PS2 | Forces GPLv3 | M–H | Inactive since 2021 |
| V1 | Static VU1 microprogram recompiler (RSPRecomp-style) | PS2 | Keeps MIT if written fresh | VH | None for PS2 found |
| V2 | VU1 interpreter: own, Play!-derived (BSD) or PS2Recomp (GPLv3) | PS2 | MIT (own or Play!) / GPLv3 (PS2Recomp) | M | PS2Recomp has one (slow); Play! has interpreter and JIT |
| V3 | Per-microprogram high-level C++ replacements | PS2 | Keeps MIT | H (per program, game-specific) | n/a |
| A1 | IRX modules on IOP interpreter + low-level SPU2 (Play! `Iop_Spu2_Core` or own) | PS2 | Keeps MIT (Play!/own) | H | Play! active |
| A2 | Same as A1 using PCSX2 SPU2 or PS2Recomp ps2xIOP | PS2 | Forces GPLv3 | M–H | PCSX2 mature; ps2xIOP experimental |
| A3 | High-level sound-library RPC (LIBSD-style) + ADPCM decode to SDL3 | PS2 | Keeps MIT if own code (Play! `Iop_LibSd` BSD as reference) | M | Pattern exists in PS2Recomp (GPL) and Play! (BSD) |
| D1 | Own TA decoder + PVR2 renderer on SDL3 GPU/plume/Vulkan (SFA3 Native-style design) | DC/AW | Keeps MIT if written fresh; Deecy (MIT) and reicast BSD files usable as reference | M–H | SFA3 Native shows this works (GPLv3 code, so the design is a model, not code to copy) |
| D2 | Reuse Flycast PVR/TA + renderers | DC/AW | Forces GPL (v2+, so GPLv3-combinable after audit) | M | Most mature DC/Atomiswave code |
| D3 | Reuse reicast/libswirl BSD files | DC/AW | Keeps MIT only after excluding the `gpl/` includes (lxdream TA core, vba-arm ARM7, xbrz) | M–H | EOL |
| D4 | Port Deecy renderer logic from Zig | DC/AW | Keeps MIT | M–H | Experimental; listed gaps |
| D5 | Reuse redream 2018 snapshot / lxdream | DC | Forces GPLv3 (redream) / GPLv2 (lxdream) | M–H | Stale |
| S1 | Static ARM7 driver recompile + own 64-voice AICA synth (SFA3 Native-style) | DC/AW | Keeps MIT if written fresh | M–H | Proven in SFA3 Native (GPLv3 code) |
| S2 | Interpreted ARM7 + own AICA mixer | DC/AW | Keeps MIT if own code; Flycast ARM7/AICA forces GPL; reicast ARM7 includes GPL vba-arm | M | chuchu runs the driver but has no mixer |
| S3 | Reuse Flycast AICA + DSP | DC/AW | Forces GPL | M | Mature |
| S4 | High-level sound commands on the SH-4 side | DC/AW | Keeps MIT | M (game-specific) | n/a |
| H1 | Host layer: SDL3 (+SDL GPU), plume, bgfx, Dawn, wgpu, raylib | both | All permissive (zlib/MIT/BSD/MIT-or-Apache) | L | Mature |

---

## Open questions (not resolved here)

1. Which IOP modules the PS2 build loads for sound and streaming, and whether it calls a recognisable Sony or middleware library. This decides between options A1 and A3.
2. How many distinct VU1 microprograms the PS2 build uploads, and whether it uses VU0 micro mode. This sizes V1, V2 and V3.
3. Whether the Atomiswave build uses AICA DSP effects and modifier volumes, which affects the size of D1 and S1.
4. For paraLLEl-GS, whether a dual license is actually available ("may be possible" per its README).
5. KatanaRecomp's license and approach could not be verified, because the repository was unreachable.

---

## Sources

Licenses and source code (repository files read directly):
- [N64Recomp LICENSE (MIT)](https://github.com/N64Recomp/N64Recomp/blob/main/LICENSE) · [N64Recomp README](https://github.com/N64Recomp/N64Recomp/blob/main/README.md)
- [RT64 LICENSE (MIT)](https://github.com/rt64/rt64/blob/main/LICENSE) · [RT64 README](https://github.com/rt64/rt64/blob/main/README.md) · [RT64 src/gbi](https://github.com/rt64/rt64/tree/main/src/gbi)
- [N64ModernRuntime COPYING (GPLv3)](https://github.com/N64Recomp/N64ModernRuntime/blob/main/COPYING) · [N64ModernRuntime README](https://github.com/N64Recomp/N64ModernRuntime/blob/main/README.md)
- [Zelda64Recomp COPYING (GPLv3)](https://github.com/Zelda64Recomp/Zelda64Recomp/blob/dev/COPYING) · [Zelda64Recomp README](https://github.com/Zelda64Recomp/Zelda64Recomp/blob/dev/README.md) · [Zelda64Recomp CMakeLists.txt](https://github.com/Zelda64Recomp/Zelda64Recomp/blob/dev/CMakeLists.txt)
- [XenonRecomp LICENSE.md (MIT)](https://github.com/hedge-dev/XenonRecomp/blob/main/LICENSE.md) · [XenonRecomp README](https://github.com/hedge-dev/XenonRecomp/blob/main/README.md)
- [XenosRecomp LICENSE.md (MIT)](https://github.com/hedge-dev/XenosRecomp/blob/main/LICENSE.md) · [XenosRecomp README](https://github.com/hedge-dev/XenosRecomp/blob/main/README.md)
- [UnleashedRecomp COPYING (GPLv3)](https://github.com/hedge-dev/UnleashedRecomp/blob/main/COPYING) · [UnleashedRecomp README](https://github.com/hedge-dev/UnleashedRecomp/blob/main/README.md) · [UnleashedRecomp gpu/video.cpp](https://github.com/hedge-dev/UnleashedRecomp/blob/main/UnleashedRecomp/gpu/video.cpp) · [UnleashedRecomp apu/audio.cpp](https://github.com/hedge-dev/UnleashedRecomp/blob/main/UnleashedRecomp/apu/audio.cpp) · [UnleashedRecomp kernel/imports.cpp](https://github.com/hedge-dev/UnleashedRecomp/blob/main/UnleashedRecomp/kernel/imports.cpp)
- [plume LICENSE (MIT)](https://github.com/renderbag/plume/blob/main/LICENSE)
- [PS2Recomp LICENSE (GPLv3)](https://github.com/ran-j/PS2Recomp/blob/main/LICENSE) · [PS2Recomp README](https://github.com/ran-j/PS2Recomp/blob/main/README.md) · [ps2xRuntime Readme](https://github.com/ran-j/PS2Recomp/blob/main/ps2xRuntime/Readme.md) · [ps2xRuntime GS sources](https://github.com/ran-j/PS2Recomp/tree/main/ps2xRuntime/src/lib/gs) · [ps2xRuntime VU1 sources](https://github.com/ran-j/PS2Recomp/tree/main/ps2xRuntime/src/lib/vu) · [ps2_audio.h](https://github.com/ran-j/PS2Recomp/blob/main/ps2xRuntime/include/runtime/ps2_audio.h) · [ps2xIOP README](https://github.com/ran-j/PS2Recomp/blob/main/ps2xIOP/README.md)
- [PCSX2 COPYING.GPLv3](https://github.com/PCSX2/pcsx2/blob/master/COPYING.GPLv3) · [PCSX2 GS renderers](https://github.com/PCSX2/pcsx2/tree/master/pcsx2/GS/Renderers) · [PCSX2 SPU2](https://github.com/PCSX2/pcsx2/tree/master/pcsx2/SPU2)
- [Play! License.txt (BSD-2)](https://github.com/jpd002/Play-/blob/master/License.txt) · [Play! README](https://github.com/jpd002/Play-/blob/master/README.md) · [Play! Source/gs](https://github.com/jpd002/Play-/tree/master/Source/gs) · [Play! Source/iop](https://github.com/jpd002/Play-/tree/master/Source/iop) · [Play--Framework License.txt](https://github.com/jpd002/Play--Framework/blob/master/License.txt) · [Play--CodeGen License.txt](https://github.com/jpd002/Play--CodeGen/blob/master/License.txt) · [libretro Play! core License.txt](https://github.com/libretro/Play-/blob/master/License.txt)
- [DobieStation LICENSE (GPLv3)](https://github.com/PSI-Rockin/DobieStation/blob/master/LICENSE) · [DobieStation README](https://github.com/PSI-Rockin/DobieStation/blob/master/README.md)
- [paraLLEl-GS README](https://github.com/Arntzen-Software/parallel-gs/blob/main/README.md) · [paraLLEl-GS COPYING.LGPLv3](https://github.com/Arntzen-Software/parallel-gs/blob/main/COPYING.LGPLv3)
- [Flycast LICENSE (GPLv2 text)](https://github.com/flyinghead/flycast/blob/master/LICENSE) · [Flycast README](https://github.com/flyinghead/flycast/blob/master/README.md) · [Flycast core/hw/pvr](https://github.com/flyinghead/flycast/tree/master/core/hw/pvr) · [Flycast core/hw/aica](https://github.com/flyinghead/flycast/tree/master/core/hw/aica) · [Flycast core/rend](https://github.com/flyinghead/flycast/tree/master/core/rend)
- [reicast LICENSE (BSD-3)](https://github.com/skmp/reicast-emulator/blob/alpha/LICENSE) · [reicast docs/CONTRIBUTING.md](https://github.com/skmp/reicast-emulator/blob/alpha/docs/CONTRIBUTING.md) · [reicast libswirl/gpl](https://github.com/skmp/reicast-emulator/tree/alpha/libswirl/gpl) · [reicast libswirl/hw/arm7/arm7.cpp](https://github.com/skmp/reicast-emulator/blob/alpha/libswirl/hw/arm7/arm7.cpp)
- [redream GitHub LICENSE.txt (GPLv3)](https://github.com/inolen/redream/blob/master/LICENSE.txt) · [redream ICLA.md](https://github.com/inolen/redream/blob/master/ICLA.md) · [redream README](https://github.com/inolen/redream/blob/master/README.md) · [redream.io](https://redream.io/)
- [lxdream COPYING (GPLv2)](https://github.com/lxdream/lxdream/blob/master/COPYING)
- [Deecy README](https://github.com/Senryoku/Deecy/blob/main/README.md) · [Deecy LICENSE (MIT)](https://github.com/Senryoku/Deecy/blob/main/LICENSE) · [Deecy build.zig.zon](https://github.com/Senryoku/Deecy/blob/main/build.zig.zon)
- [dcrecomp README](https://github.com/sp00nznet/dcrecomp/blob/main/README.md) · [dcrecomp NOTICE](https://github.com/sp00nznet/dcrecomp/blob/main/NOTICE) · [dcrecomp LICENSE](https://github.com/sp00nznet/dcrecomp/blob/main/LICENSE)
- [chuchu README](https://github.com/sp00nznet/chuchu/blob/master/README.md) · [chuchu LICENSE (MIT)](https://github.com/sp00nznet/chuchu/blob/master/LICENSE)
- [SFA3 Native README](https://github.com/irnutsmurt/Street-Alpha-3-Dreamcast-Recomp/blob/main/README.md) · [SFA3 Native runtime/](https://github.com/irnutsmurt/Street-Alpha-3-Dreamcast-Recomp/tree/main/runtime) · [SFA3 Native tools/recomp/arm.py](https://github.com/irnutsmurt/Street-Alpha-3-Dreamcast-Recomp/blob/main/tools/recomp/arm.py)
- [SDL LICENSE.txt (zlib)](https://github.com/libsdl-org/SDL/blob/main/LICENSE.txt) · [SDL3 GPU API (CategoryGPU)](https://wiki.libsdl.org/SDL3/CategoryGPU) · [SDL_shadercross LICENSE.txt](https://github.com/libsdl-org/SDL_shadercross/blob/main/LICENSE.txt) · [SDL_mixer LICENSE.txt](https://github.com/libsdl-org/SDL_mixer/blob/main/LICENSE.txt)
- [raylib LICENSE (zlib)](https://github.com/raysan5/raylib/blob/master/LICENSE) · [bgfx LICENSE (BSD-2)](https://github.com/bkaradzic/bgfx/blob/master/LICENSE) · [Dawn LICENSE (BSD-3)](https://github.com/google/dawn/blob/main/LICENSE) · [wgpu LICENSE.MIT](https://github.com/gfx-rs/wgpu/blob/trunk/LICENSE.MIT) · [wgpu LICENSE.APACHE](https://github.com/gfx-rs/wgpu/blob/trunk/LICENSE.APACHE)
- [SPIRV-Cross LICENSE (Apache-2.0)](https://github.com/KhronosGroup/SPIRV-Cross/blob/main/LICENSE) · [DirectXShaderCompiler LICENSE.TXT](https://github.com/microsoft/DirectXShaderCompiler/blob/main/LICENSE.TXT) · [Vulkan-Headers LICENSE.md](https://github.com/KhronosGroup/Vulkan-Headers/blob/main/LICENSE.md)
- [libretro.h (MIT header)](https://github.com/libretro/RetroArch/blob/master/libretro-common/include/libretro.h) · [xenia LICENSE](https://github.com/xenia-project/xenia/blob/master/LICENSE)

License texts and compatibility:
- [GNU GPL v3 text (as shipped in PCSX2)](https://github.com/PCSX2/pcsx2/blob/master/COPYING.GPLv3)
- [GNU GPL v2 text (as shipped in Flycast)](https://github.com/flyinghead/flycast/blob/master/LICENSE)
- [GNU LGPL v3 text (as shipped in paraLLEl-GS)](https://github.com/Arntzen-Software/parallel-gs/blob/main/COPYING.LGPLv3)
- [Apache Software Foundation: Apache License v2.0 and GPL Compatibility](https://www.apache.org/licenses/GPL-compatibility.html)

Hardware documentation and background:
- [ps2tek (PS2 hardware documentation)](https://psi-rockin.github.io/ps2tek/)
- [Themaister: PlayStation 2 GS emulation – the final frontier of Vulkan compute emulation](https://themaister.net/blog/2024/07/03/playstation-2-gs-emulation-the-final-frontier-of-vulkan-compute-emulation)
- [Rodrigo Copetti: PlayStation 2 Architecture](https://www.copetti.org/writings/consoles/playstation-2/)
- [Rodrigo Copetti: Dreamcast Architecture](https://www.copetti.org/writings/consoles/dreamcast/)
- [dreamcast.wiki: PowerVR Introduction](https://dreamcast.wiki/PowerVR_Introduction)
- [Wikipedia: The King of Fighters XI](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI)
- [Wikipedia: Atomiswave](https://en.wikipedia.org/wiki/Atomiswave)
- [Emulation General Wiki: Redream](https://emulation.gametechwiki.com/index.php/Redream) (secondary; used only for redream's closed-source status)

Not retrievable from this session: gnu.org's license-list and GPL FAQ pages (connection refused), so compatibility statements above rely on the license texts and the Apache page. The KatanaRecomp and GitLab redream repositories were also unreachable.
