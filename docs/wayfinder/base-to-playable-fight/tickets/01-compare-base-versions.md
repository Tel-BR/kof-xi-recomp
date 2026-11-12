---
id: 01
title: Compare PS2 and Dreamcast as the base version
type: research
status: closed
assignee: claude
blocked_by: []
research: ../research/compare-base-versions.md
---

## Question

What are the facts the owner needs to choose the Base Version? Compare the PS2 release and the Dreamcast disc on: content (roster, Hidden Characters, modes); provenance of the Dreamcast version (official or a conversion of the Atomiswave arcade code); the CPU and hardware to recompile (PS2: EE + VU + GS + IOP/SPU2; Dreamcast: SH-4 + PowerVR2 + AICA); existing static-recompilation tooling for each CPU; existing reverse-engineering knowledge of KOF XI and its engine. Also note how each option weighs on out-of-scope future goals (rollback determinism, porting NGBC fighters, Hidden Characters, widescreen) without deciding.

_PT-BR: quais fatos o dono precisa para escolher a versão-base? Comparar PS2 e Dreamcast em conteúdo, origem da versão Dreamcast, processador e hardware a recompilar, ferramentas de recompilação existentes e conhecimento já publicado sobre o jogo; anotar como cada opção pesa nas metas futuras (rollback, lutadores do NGBC, personagens ocultos, widescreen), sem decidir._

## Resolution

Full findings: [research/compare-base-versions.md](../research/compare-base-versions.md). Facts only; the choice is [Choose the base version](05-choose-base-version.md).

- **Content:** the PS2 Release is a superset of the arcade game: playable bosses, 7 fighters rebuilt from Neo Geo Battle Coliseum, Challenge, Edit and classic Team modes, 4 extra stages, an arranged soundtrack and control tweaks. The Arcade Release is the tournament original; its hidden characters sit behind an operator time-release menu.
- **Dreamcast provenance:** not an official release. It is megavolt85's 2020 conversion of the Arcade Release, so it is the arcade code on the same CPU and graphics chip. [Inspect the code structure of each candidate release](08-inspect-code-structure.md) later showed it is the cart's own program with 754 bytes patched, plus the cart data decrypted.
- **Hardware to recompile:** PS2 means EE (MIPS R5900) + VU0/VU1 + GS + IOP + SPU2. Arcade means SH-4 + PowerVR2 + AICA (ARM7). The PS2 has more processors and a graphics path (VU1 microprograms + GS) that is much harder to reproduce.
- **Tooling:** PS2 has one dominant recompiler, PS2Recomp (GPL-3.0, 3 games released, still experimental, slow GS/VU). SH-4 has several young recompilers (dream-recomp and dcrecomp GPL-2.0, DreamcastRecompiled MIT, plus the Street Fighter Alpha 3 recomp, a playable 2D fighter); none supports Atomiswave carts or conversion discs.
- **Existing knowledge of KOF XI:** almost none in public: no decompilation, symbol map or data-format documentation for either release; no widescreen patch for either.
- **Future goals:** rollback has working precedent only on the arcade code (Flycast GGPO); the PS2 float unit is non-IEEE. The PS2 Release already proves SNK moved NGBC fighters into this engine on that platform.

_PT-BR: só fatos; a escolha fica para o ticket 05. O PS2 tem mais conteúdo (chefes jogáveis, 7 lutadores vindos do NGBC, modos e fases extras, trilha arranjada). O "Dreamcast" é a conversão de 2020 da versão de arcade, ou seja, o mesmo código de arcade (o ticket 08 confirmou: é o programa do cartucho com 754 bytes alterados). O PS2 tem mais processadores e um caminho gráfico bem mais difícil; tem uma ferramenta dominante (PS2Recomp, GPL-3.0, experimental). O lado SH-4 tem várias ferramentas jovens, nenhuma pronta para cartucho Atomiswave. Quase nada público sobre o KOF XI em nenhuma das versões. Rollback já funciona no código de arcade (Flycast); o PS2 tem ponto flutuante fora do padrão._
