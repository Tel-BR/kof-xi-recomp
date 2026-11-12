---
id: 18
title: Decide how the port reads the User-supplied Disc
type: grilling
status: open
assignee:
blocked_by: [11, 12]
---

## Question

Does the port read the User-supplied Disc at runtime, or extract what it needs once at setup? How does it check that the user's image is the US edition (SLUS-21687 v1.00), given that a dump with read errors can still carry a correct executable ([Get a Redump-verified PS2 image](11-redump-verified-ps2.md))? And what happens to the two 630 MB `KOF_000x.DAT` files, depending on what [Find out what the two big PS2 DAT files hold](12-ps2-big-dat-files.md) finds? Disc reads must also be replayable for rollback (no host timing in the simulation).

_PT-BR: o port lê o disco do usuário enquanto roda, ou extrai o que precisa uma única vez na instalação? Como confere que a imagem é a edição americana v1.00, já que um dump com erros de leitura pode ter o executável correto (ticket 11)? E o que fazer com os dois arquivos `KOF_000x.DAT` de 630 MB, conforme o que o ticket 12 descobrir? As leituras do disco também precisam ser reproduzíveis para o rollback (nada de tempo do PC na simulação)._
