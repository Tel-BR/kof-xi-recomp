---
id: 08
title: Inspect the code structure of each candidate release
type: task
status: closed
assignee: claude
blocked_by: []
research: ../research/inspect-code-structure.md
---

## Question

What does the code of each candidate look like from a recompiler's point of view? For the PS2 disc, the Dreamcast Conversion disc and the owner's Atomiswave cartridge dump (the owner has the cartridge; the dump goes in `private/arcade/`), record structural facts only: executable format and size; whether symbols or debug info are present; how much is code versus data; how many separately loaded code modules or overlays exist; where fighter and mode data live. For the Dreamcast Conversion, confirm or refute that it is a small loader plus the arcade cartridge data, and whether the arcade code inside matches the cartridge dump. AFK: the agent runs this on the owner's machine. Never record disassembly, assets or any other game content: sizes, counts, formats and hashes only.

_PT-BR: como é o código de cada candidato, do ponto de vista de um recompilador? Registrar só fatos estruturais (formato e tamanho do executável, se há símbolos, quanto é código ou dados, quantos módulos de código, onde ficam os dados de lutadores e modos) para o disco de PS2, o disco de Dreamcast e o dump do cartucho Atomiswave do dono (em `private/arcade/`); na conversão de Dreamcast, confirmar se é um carregador mais os dados do cartucho e se o código bate com o dump do cartucho. O agente faz sozinho; nada de conteúdo do jogo, só tamanhos, contagens, formatos e hashes._

## Resolution

Full measurements: [research/inspect-code-structure.md](../research/inspect-code-structure.md). Sizes, counts, formats and hashes only.

- **PS2 Release:** one standard ELF, 2.0 MB, with **no symbols and no debug info**, built with Metrowerks CodeWarrior (not GCC). About two-thirds is code (~1.3 MB). **No overlays**: the only other code is 7 IOP modules (Sony SDK libraries plus the CRI ADX audio middleware) and Sony's IOP replacement image. Data is 685 files: per-fighter data in four sibling folders under `/DATA/PL*`, music in one CRI AFS archive, and two 630 MB high-entropy `KOF_000x.DAT` files (52% of the disc) whose role (encrypted archive or filler) is still open.
- **Arcade Release:** the cartridge dump is **encrypted**; MAME documents the cipher (BSD-3-Clause) and this game's key, and decrypting locally works. The program is a raw SH-4 binary of 1.19 MB (~88% code) after a 256-byte cart header, **no symbols**. Data is 7 × 32 MiB mask ROMs in an unnamed cartridge file system. No SH-4 overlays; an ARM7 block (the sound driver, most likely) sits inside the program.
- **Dreamcast Conversion:** **not** a small loader plus cart data. `1ST_READ.BIN` *is* the arcade program, decrypted, with **754 bytes changed in 28 places**; the 7 mask ROMs are stored decrypted in track 3 and are **byte-identical** to the owner's cartridge. So the arcade code inside the conversion matches the cartridge dump, apart from the converter's patches.
- **Side finding for [Get a Redump-verified PS2 image](11-redump-verified-ps2.md):** `KOF_0001.DAT` has 42 zero-filled runs aligned to 16-sector DVD error-correction blocks near the disc edge, the usual mark of unreadable blocks. Recorded on that ticket.

_PT-BR: no PS2, um ELF de 2 MB sem símbolos, compilado com Metrowerks; sem overlays; lutadores em quatro pastas `/DATA/PL*`; dois arquivos de 630 MB com aparência aleatória, papel ainda em aberto. No arcade, o dump do cartucho é criptografado (o MAME documenta a cifra, em licença BSD-3, e a chave); o programa tem 1,19 MB de SH-4, sem símbolos; dados em 7 ROMs com um sistema de arquivos sem nomes. O Dreamcast não é "carregador + dados": o `1ST_READ.BIN` é o próprio programa do arcade com 754 bytes alterados em 28 pontos, e os dados das ROMs são idênticos byte a byte ao dump do cartucho do dono. De quebra: o `KOF_0001.DAT` tem trechos zerados no padrão de setores ilegíveis, o que explica o hash do PS2 (anotado no ticket 11)._
