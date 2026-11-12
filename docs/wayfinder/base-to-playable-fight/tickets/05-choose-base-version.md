---
id: 05
title: Choose the base version
type: grilling
status: open
assignee:
blocked_by: [01, 04, 08, 09, 10]
---

## Question

Which code does the project recompile: the PS2 Release, or the Arcade Release's code (taken either from an Atomiswave cartridge dump or from the Dreamcast Conversion)? The goal is the best of both releases for the least effort. Weigh the comparison in ticket 01, the exact dumps from ticket 04, the code structure from ticket 08, the cost of carrying content across releases from ticket 09, and the owner's hands-on comparison from ticket 10. Record the reasons, and what the choice gives up.

Owner input to weigh:
- The PS2 Release's extra fighters were adapted from Neo Geo Battle Coliseum. Having them in the base is a strong head start for the future NGBC-porting map, because SNK's own adaptations show the pattern to follow.
- The PS2 Release has more modes and menu options.
- The Arcade Release has more ready-made tooling on PC (Flycast, including online rollback that already works).
- After playing both (ticket 10): the PS2 controls feel more responsive and all PS2-only content is a must for the final port, but neither release is discarded until the effort is known. **Decisive criteria: excellent performance with the NGBC fighters, and rollback netplay.**

Fact to confirm with the owner first (from ticket 09): does turning Arrange off in the PS2 options give the original arcade balance?

_PT-BR: que código o projeto recompila: a versão de PS2 ou o código da versão de arcade (vindo de um dump do cartucho Atomiswave ou da conversão para Dreamcast)? O objetivo é o melhor das duas versões com o menor esforço. Pesar os tickets 01, 04, 08, 09 e 10. Pontos do dono: os lutadores extras do PS2 vieram do NGBC e são uma vantagem forte para o futuro port de lutadores do NGBC; o PS2 tem mais modos e menus; a versão de arcade tem mais ferramentas prontas no PC (Flycast, com rollback online funcionando). Depois de jogar as duas (ticket 10): os controles do PS2 respondem melhor e todo o conteúdo exclusivo do PS2 é indispensável no port final, mas nenhuma versão está descartada até se conhecer o esforço. **Critérios decisivos: desempenho excelente com os lutadores do NGBC e netplay com rollback.**_
