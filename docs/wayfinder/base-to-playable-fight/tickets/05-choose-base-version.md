---
id: 05
title: Choose the base version
type: grilling
status: closed
assignee: Tel-BR
blocked_by: [01, 04, 08, 09, 10]
---

## Question

Which code does the project recompile: the PS2 Release, or the Arcade Release's code (taken either from an Atomiswave cartridge dump or from the Dreamcast Conversion)? The goal is the best of both releases for the least effort. Weigh the comparison in ticket 01, the exact dumps from ticket 04, the code structure from ticket 08, the cost of carrying content across releases from ticket 09, and the owner's hands-on comparison from ticket 10. Record the reasons, and what the choice gives up.

Owner input to weigh:
- The PS2 Release's extra fighters were adapted from Neo Geo Battle Coliseum. Having them in the base is a strong head start for the future NGBC-porting map, because SNK's own adaptations show the pattern to follow.
- The PS2 Release has more modes and menu options.
- The Arcade Release has more ready-made tooling on PC (Flycast, including online rollback that already works).
- After playing both (ticket 10): the PS2 controls feel more responsive and all PS2-only content is a must for the final port, but neither release is discarded until the effort is known. **Decisive criteria: excellent performance with the NGBC fighters, and rollback netplay.**

Confirmed by the owner (2026-11-11, from ticket 09): on the PS2, "Arranged" is an option. On: new stages, modified music and rebalancing across the whole game. Off: the arcade balance, with the PS2-exclusive fighters and Color Edit still available. / _Confirmado pelo dono: no PS2, "Arranged" é uma opção. Ligada: fases novas, músicas modificadas e balanceamento novo no jogo inteiro. Desligada: balanceamento do arcade, com os lutadores exclusivos do PS2 e o Color Edit ainda disponíveis._

_PT-BR: que código o projeto recompila: a versão de PS2 ou o código da versão de arcade (vindo de um dump do cartucho Atomiswave ou da conversão para Dreamcast)? O objetivo é o melhor das duas versões com o menor esforço. Pesar os tickets 01, 04, 08, 09 e 10. Pontos do dono: os lutadores extras do PS2 vieram do NGBC e são uma vantagem forte para o futuro port de lutadores do NGBC; o PS2 tem mais modos e menus; a versão de arcade tem mais ferramentas prontas no PC (Flycast, com rollback online funcionando). Depois de jogar as duas (ticket 10): os controles do PS2 respondem melhor e todo o conteúdo exclusivo do PS2 é indispensável no port final, mas nenhuma versão está descartada até se conhecer o esforço. **Critérios decisivos: desempenho excelente com os lutadores do NGBC e netplay com rollback.**_

## Resolution

Decided by the owner on 2026-11-12.

**The Base Version is the PS2 Release, US edition: SLUS-21687, version 1.00 (Redump disc 5234).**

Why:

- **It holds all the content the owner requires.** The NGBC-derived fighters, the playable bosses, the Challenge, Edit and classic Team modes, the 4 extra stages and the arranged soundtrack are already in its code and data. Content flows one way ([Assess carrying content across releases](09-carry-content-across-releases.md)): with the Arranged Option off, the PS2 Release plays with the arcade balance, so the Arcade Release has no content the PS2 Release lacks.
- **It serves the first decisive criterion directly.** The NGBC-derived fighters run on the same engine as the rest of the game, so their performance is the port's performance, with no data converter in between. On the arcade code they would first have to be rebuilt from undocumented formats on both sides.
- **The owner prefers its controls** ([Compare both releases hands-on in emulators](10-hands-on-comparison.md)).
- **The arcade's strengths are technical and cannot be carried** to the PS2 Release, while the PS2 Release's content could only reach the arcade code through a large reverse-engineering and rewriting effort. The PS2 base costs more up front; the arcade base costs more in total for the owner's final goal.
- **US edition:** it is the owner's disc, already identified and inspected ([Identify the exact disc dumps](04-identify-disc-dumps.md), [Inspect the code structure of each candidate release](08-inspect-code-structure.md)), it is in English, and it is easy for collaborators in the Americas to buy. The Japanese edition's progressive scan does not matter to a native port.

What the choice gives up:

- **Simpler hardware.** The PS2 has more processors. Reproducing the GS and the VU1 microprograms is the hardest part of the port, and the only PS2 recompiler today (PS2Recomp) is slow exactly there.
- **Proven rollback.** Flycast already runs rollback with the arcade code; nobody has done it for the PS2 Release. The PS2 float unit is not IEEE-754, and the state to snapshot is larger (~40 MiB against ~26 MiB). The second decisive criterion, rollback netplay, becomes engineering risk to manage rather than a precedent to rely on.
- **A shorter path to the first Complete Fight**, and the young SH-4 tools with the Street Fighter Alpha 3 recomp as a close precedent.
- **Licence freedom, probably.** Building on PS2Recomp would make the distributed port GPL-3.0; that is decided in [Decide whether to relicense to GPL](06-gpl-relicense.md).
- **Other PS2 editions.** The Japanese (the original release), European and Korean editions are not supported by this map; a user needs the US disc. Ruled out of scope on the map.
- **The tournament original.** The PS2 Release with the Arranged Option off has the arcade balance, but adds fighters, Color Edit and the PS2's control tuning, so it is not an exact copy of the Arcade Release.

Consequences on the map: [Get a Redump-verified PS2 image](11-redump-verified-ps2.md) and [Find out what the two big PS2 DAT files hold](12-ps2-big-dat-files.md) stay in scope. The arcade-only fog (cart decryption, AICA DSP, PowerVR2 modifier volumes) is dropped. New tickets: [Try PS2Recomp on the PS2 executable](13-try-ps2recomp.md), [Measure the PS2 Release's VU1 and GS usage](14-measure-vu1-gs-usage.md), [Decide the recompiler](15-decide-recompiler.md), [Decide how GS and VU1 graphics are reproduced](16-gs-vu1-approach.md), [Decide how the IOP side is reproduced](17-iop-approach.md) and [Decide how the port reads the User-supplied Disc](18-read-user-disc.md).

_PT-BR: decidido pelo dono em 12/11/2026. **A versão-base é a versão de PS2, edição americana SLUS-21687 v1.00 (disco 5234 do Redump).** Por quê: ela já tem todo o conteúdo obrigatório (lutadores do NGBC, chefes, modos, fases e trilha); com a opção "Arranged" desligada ela usa o balanceamento do arcade, então o arcade não tem conteúdo que falte; os lutadores do NGBC rodam no mesmo motor do resto do jogo, sem conversor, o que atende direto ao primeiro critério decisivo; o dono prefere os controles do PS2; as vantagens do arcade são técnicas e não se transportam, enquanto levar o conteúdo do PS2 para o arcade seria um trabalho enorme. Edição americana: é o disco do dono, já medido, em inglês e fácil de comprar. Do que abre mão: hardware mais simples (GS e VU1 são a parte mais difícil, e o PS2Recomp é lento justamente aí); rollback já provado (o Flycast já faz com o código do arcade; no PS2 ninguém fez, o ponto flutuante é fora do padrão e o estado é maior), então o rollback vira risco de engenharia a administrar; um caminho mais curto até a primeira luta e as ferramentas de SH-4; provavelmente a licença MIT, se usarmos o PS2Recomp (ticket 06); as outras edições de PS2 (japonesa, europeia, coreana), que ficam fora do escopo; e a versão exata de torneio (com "Arranged" desligado o balanceamento é o do arcade, mas há lutadores a mais, Color Edit e o ajuste de controles do PS2). Os tickets 11 e 12 continuam valendo; a névoa só do arcade sai do mapa; seis tickets novos foram criados._
