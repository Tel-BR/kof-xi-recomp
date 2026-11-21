---
id: 12
title: Find out what the two big PS2 DAT files hold
type: task
status: closed
assignee: Tel-BR
blocked_by: [05]
research: ../research/ps2-big-dat-files.md
---

## Question

The PS2 disc has two files, `KOF_0000.DAT` and `KOF_0001.DAT`, of about 630 MB each (52% of the disc). Both look random from first byte to last, share no data with any other file, and are each referenced once by the executable (see [Inspect the code structure of each candidate release](08-inspect-code-structure.md)). Are they filler that pushes the real files to the faster outer part of the DVD, or encrypted or compressed archives the game actually reads? If they are archives, the port must decode them, which adds work to reading the disc. AFK: the agent checks on the owner's machine, for example by watching which files and offsets PCSX2 reads during boot, menus and one fight, and records only file names, offsets and counts. If the Arcade Release is chosen as the Base Version, rule this ticket out of scope.

_PT-BR: o disco de PS2 tem dois arquivos `KOF_000x.DAT` de ~630 MB cada (52% do disco), com aparência aleatória, sem nada em comum com outros arquivos, e citados uma vez cada pelo executável. São só enchimento para empurrar os arquivos de verdade para a parte mais rápida do DVD, ou pacotes criptografados/comprimidos que o jogo lê? Se forem pacotes, o port terá de decodificá-los. O agente confere sozinho, por exemplo observando quais arquivos o PCSX2 lê durante a abertura, os menus e uma luta, e registra só nomes, posições e contagens. Se a versão de arcade for a escolhida, este ticket sai do escopo._

## Resolution

Full measurements and analysis: [research/ps2-big-dat-files.md](../research/ps2-big-dat-files.md). Counts, offsets, and outcomes only.

- **Outcome:** `KOF_0000.DAT` and `KOF_0001.DAT` (~630 MB each, 1.26 GB combined, or 52% of the disc) are **pure dummy padding/filler**. They are not archives, contain no game assets, and the game executable never reads, opens, or accesses them.
- **Table analysis:** The executable contains a static master table of all 685 DVD files at `0x28E8D0`. The two DAT files sit at the end of the disc (outer sectors 574,123..1,189,163; table indices 683 and 684).
- **Executable code exclusion:** All five file lookup functions in `SLUS_216.87` (`0x1D7F70`, `0x1D8180`, `0x1D83F0`, `0x1D8660`, `0x1D87B0`) scan the table with an explicit loop bound `slti v0, index, 684`, completely excluding `KOF_0001.DAT` (index 684) by design. Furthermore, all searches prepend `\DATA\%s;1`, which never matches root paths `\KOF_0000.DAT;1` or `\KOF_0001.DAT;1`. Zero instructions load their names or table pointers, and no `sceCdRead` calls target their LBA range.
- **Live memory verification:** Memory dumps (32 MB EE RAM, 2 MB IOP RAM) from 7 PCSX2 savestates across boot, menus, and battles contain zero blocks from either DAT file.
- **Impact on the port:** The PC port can completely ignore both DAT files; real game assets occupy only ~1.17 GB (LBA 1,089..574,122). Additionally, the zeroed-out sectors in `KOF_0001.DAT` responsible for the Redump hash mismatch in [Get a Redump-verified PS2 image](11-redump-verified-ps2.md) do not affect game data in any way.

_PT-BR: Análise completa em [research/ps2-big-dat-files.md](../research/ps2-big-dat-files.md). Os dois arquivos DAT (~630 MB cada, somando 1,26 GB ou 52% do disco) são puramente enchimento (dummy padding) para atingir a especificação mínima de prensagem do DVD de PS2. Não são arquivos comprimidos/criptografados e nunca são lidos pelo jogo. Todas as funções de busca de arquivos do executável limitam a busca com `slti reg, 684` (excluindo o índice 684 do `KOF_0001.DAT`) e buscam apenas dentro de `\DATA\`. Não há referências a eles no código nem chamadas de leitura para seus setores no disco, e a memória do PCSX2 (EE e IOP) em 7 savestates não contém nenhum dado deles. O port de PC pode ignorar totalmente ambos os arquivos (os dados reais têm ~1,17 GB). Além disso, os setores com falha de leitura no dump do dono em `KOF_0001.DAT` (Ticket 11) não afetam nenhum asset ou código do jogo._
