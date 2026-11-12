---
id: 02
title: Survey graphics and audio reimplementation options and their licenses
type: research
status: closed
assignee: claude
blocked_by: []
research: ../research/graphics-audio-options.md
---

## Question

For each candidate Base Version, how can the console's graphics and audio be reproduced natively, and under which licences? Survey how existing static recomps handle the GPU and sound (e.g. RT64, XenonRecomp/UnleashedRecomp, PS2Recomp), which reusable emulator components exist (PCSX2, Play!, Flycast, libretro cores, permissive libraries) and their licences, and what relicensing from MIT to GPL would mean in practice.

_PT-BR: para cada versão candidata, como reproduzir gráfico e som de forma nativa, e sob quais licenças? Levantar como as recompilações existentes resolvem isso, quais componentes de emuladores podem ser reaproveitados e com que licença, e o que significaria na prática trocar MIT por GPL._

## Resolution

Full findings: [research/graphics-audio-options.md](../research/graphics-audio-options.md). Facts only; the licence choice is [Decide whether to relicense to GPL](06-gpl-relicense.md).

- **How recomps do it:** four patterns: emulate the chip at a low level behind the recompiled CPU code; translate the command stream the CPU sends the chip into Vulkan/Direct3D draws; hook the game's own render API; and recompile the small programs that run on coprocessors too.
- **PS2:** three hard pieces: the GS (fixed-function rasteriser with tricky feedback effects), the VU1 microprograms (separate code, not covered by the CPU recompiler) and sound on the IOP + SPU2. PS2Recomp today emulates the GS in software and interprets VU1, and is slow at both.
- **Arcade/Dreamcast:** lighter: geometry is already computed by the SH-4, so graphics means decoding the PowerVR2 display lists and redrawing them; sound means the AICA chip plus its ARM7 driver. The Street Fighter Alpha 3 recomp does exactly this (own display-list decoder + Vulkan, ARM7 driver statically recompiled).
- **Licences:** the most mature reusable parts are GPL (PCSX2 GPLv3, Flycast GPLv2-or-later, PS2Recomp GPLv3). Permissive options that keep MIT exist on both sides but are less mature: Play! (BSD-2) for PS2, Deecy (MIT) or code written fresh from hardware docs for Dreamcast; the host layer (SDL3, plume, bgfx, wgpu) is permissive either way.
- **What GPL would mean:** the whole distributed program becomes GPL with source; nobody can ship a closed fork; going back to MIT needs every contributor's permission. GPLv2-only code cannot be mixed with GPLv3 code.

_PT-BR: só fatos; a licença se decide no ticket 06. No PS2 há três peças difíceis (o chip gráfico GS, os microprogramas da VU1 e o som no IOP/SPU2). No arcade/Dreamcast é mais leve: o processador já calcula a geometria, então o gráfico é ler as listas de desenho e redesenhar; o som é o chip AICA com seu driver ARM7 (o recomp do Street Fighter Alpha 3 já fez isso). As peças mais maduras são GPL (PCSX2, Flycast, PS2Recomp); há opções permissivas, menos maduras, que mantêm o MIT. Virar GPL obriga o programa inteiro a ser GPL, com código aberto, e voltar para MIT exige autorização de todos os colaboradores._
