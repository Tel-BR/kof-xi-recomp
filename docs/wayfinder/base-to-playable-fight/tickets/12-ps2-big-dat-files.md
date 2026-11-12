---
id: 12
title: Find out what the two big PS2 DAT files hold
type: task
status: open
assignee:
blocked_by: [05]
---

## Question

The PS2 disc has two files, `KOF_0000.DAT` and `KOF_0001.DAT`, of about 630 MB each (52% of the disc). Both look random from first byte to last, share no data with any other file, and are each referenced once by the executable (see [Inspect the code structure of each candidate release](08-inspect-code-structure.md)). Are they filler that pushes the real files to the faster outer part of the DVD, or encrypted or compressed archives the game actually reads? If they are archives, the port must decode them, which adds work to reading the disc. AFK: the agent checks on the owner's machine, for example by watching which files and offsets PCSX2 reads during boot, menus and one fight, and records only file names, offsets and counts. If the Arcade Release is chosen as the Base Version, rule this ticket out of scope.

_PT-BR: o disco de PS2 tem dois arquivos `KOF_000x.DAT` de ~630 MB cada (52% do disco), com aparência aleatória, sem nada em comum com outros arquivos, e citados uma vez cada pelo executável. São só enchimento para empurrar os arquivos de verdade para a parte mais rápida do DVD, ou pacotes criptografados/comprimidos que o jogo lê? Se forem pacotes, o port terá de decodificá-los. O agente confere sozinho, por exemplo observando quais arquivos o PCSX2 lê durante a abertura, os menus e uma luta, e registra só nomes, posições e contagens. Se a versão de arcade for a escolhida, este ticket sai do escopo._
