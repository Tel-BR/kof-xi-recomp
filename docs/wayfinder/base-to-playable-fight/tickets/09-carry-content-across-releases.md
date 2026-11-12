---
id: 09
title: Assess carrying content across releases
type: research
status: closed
assignee: claude
blocked_by: [08]
research: ../research/carry-content-across-releases.md
---

## Question

How much effort would it take to get the best of both releases on a single base? In each direction (the PS2 Release's extra fighters, modes and menus moved onto the Arcade Release's code, or arcade-only strengths moved onto the PS2 code), what differs between the two releases' engines and data formats, what is publicly known about those differences, and what would the transfer roughly involve? Use the structural facts from ticket 08; no game content in the findings.

_PT-BR: quanto esforço daria juntar o melhor das duas versões numa base só? Em cada direção (lutadores extras, modos e menus do PS2 levados para o código de arcade, ou o contrário), o que muda entre os motores e os formatos de dados, o que já se sabe publicamente e o que a transferência envolveria, por alto._

## Resolution

Full findings: [research/carry-content-across-releases.md](../research/carry-content-across-releases.md).

- **Content flows one way.** Every piece of arcade content is also in the PS2 Release, including the original arcade balance: with the Arranged option off, the whole game uses the arcade balance (confirmed by the owner; the PS2-exclusive fighters and Color Edit stay available). The arcade's strengths are technical: simpler hardware and a working rollback precedent. They cannot be carried; they only come with choosing the arcade as the base.
- **PS2 base + arcade strengths:** nothing to transfer. The cost is the PS2 base itself.
- **Arcade base + PS2 content:** large. No code can move between MIPS and SH-4, so the Challenge, Edit and Team modes, the Arrange balance and the PS2's control feel would be rewritten. Each extra fighter, the 4 extra stages (3D backgrounds) and the endings need undocumented formats reverse-engineered on both sides plus converters. Only the music is cheap.
- **Measured locally:** about 13–18% of distinctive data in the PS2 fighter files appears byte-identical in the arcade cart, in short scattered pieces; palettes ~70–90% identical; stages ~1%; menus, missions and gallery 0%. The two releases share source assets but repack them, so a converter is needed, not a copy.
- **Public knowledge:** no format docs, decompilation or modding tools for KOF XI or NGBC.
- **Confirmed by the owner (2026-11-11):** on the PS2, "Arranged" is an option. On: new stages, modified music and rebalancing across the whole game. Off: the arcade balance, with the PS2-exclusive fighters and Color Edit still available.

_PT-BR: o conteúdo só anda num sentido: tudo o que o arcade tem o PS2 também tem, inclusive o balanceamento original: com a opção "Arranged" desligada, o jogo inteiro usa o balanceamento do arcade (confirmado pelo dono; os lutadores exclusivos do PS2 e o Color Edit continuam disponíveis). Ligada, ela traz as fases novas, as músicas modificadas e o balanceamento novo. O que o arcade tem de melhor é técnico e não se transporta; só vem escolhendo o arcade como base. Base PS2: nada a transportar; o custo é o próprio PS2. Base arcade: trazer o conteúdo do PS2 é trabalho grande (modos reescritos, lutadores, fases e finais com formatos não documentados e conversores); só a música é barata. Na medição local, os arquivos de lutadores compartilham pedaços pequenos com o cartucho: mesma origem, embalagem diferente._
