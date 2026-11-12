---
id: 04
title: Identify the exact disc dumps
type: task
status: closed
assignee: claude
blocked_by: []
research: ../research/identify-disc-dumps.md
---

## Question

Which exact releases are the owner's dumps (region, serial, revision)? Compute hashes (CRC32, MD5, SHA-1) of each track of the PS2 and Dreamcast images and of each file of the Atomiswave cartridge dump in `private/`, match them against Redump, MAME's software lists or another dump database (the Dreamcast Conversion, being fan-made, may only match community release notes), and record only the hashes and identification, never any disc content. AFK: the agent can do this alone on the owner's machine.

_PT-BR: quais são exatamente as versões dos dois discos do dono (região, código, revisão)? Calcular os hashes de cada trilha das imagens e de cada arquivo do dump do cartucho em `private/`, comparar com o Redump e com as listas do MAME e registrar só os hashes e a identificação, nunca conteúdo do disco. O agente faz sozinho._

## Resolution

Full hashes and sources: [research/identify-disc-dumps.md](../research/identify-disc-dumps.md).

- **PS2 Release:** USA/Canada, SLUS-21687, version 1.00 (Redump disc 5234). Size, volume date, executable date and the executable's PCSX2 CRC (`581A4DAA`) all match, but the whole-image hash does **not** match Redump's verified dump, so some bytes outside the main program differ. Usable for exploration, not as a reference image. New ticket: [Get a Redump-verified PS2 image](11-redump-verified-ps2.md).
- **Arcade Release:** all 8 cartridge ROMs match MAME 0.289's `kofxi` set (all "good"; the set has no clones). The Atomiswave BIOS (`awbios`) is on the motherboard, not in the dump; a Reference Emulator for this release needs it.
- **Dreamcast Conversion:** megavolt85's conversion, released November 2020 (product `T0001M`, `V1.000`). No dump database covers it and no build hashes were published, so the exact build cannot be confirmed; the owner's hashes are recorded as the local reference.

_PT-BR: o PS2 é o SLUS-21687 versão 1.00 (EUA/Canadá), mas a imagem não bate com o dump verificado do Redump, embora o executável principal bata; serve para explorar, não de referência (novo ticket para refazer o dump). O cartucho de arcade bate 100% com o conjunto `kofxi` do MAME; o BIOS do Atomiswave não faz parte do dump e será necessário para o emulador de referência. A conversão de Dreamcast é a do megavolt85 (nov/2020); sem banco de dados, os hashes do dono ficam como referência._
