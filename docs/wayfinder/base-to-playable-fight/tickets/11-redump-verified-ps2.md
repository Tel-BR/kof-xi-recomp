---
id: 11
title: Get a Redump-verified PS2 image
type: task
status: open
assignee:
blocked_by: [05]
---

## Question

The owner's PS2 image is the right release (SLUS-21687, version 1.00) but its whole-image hash does not match Redump's verified dump (see [Identify the exact disc dumps](04-identify-disc-dumps.md)). If the PS2 Release becomes the Base Version, the project needs the owner to hold an image that hashes exactly as Redump's, so that what the owner tests is byte-identical to what collaborators dump from their own discs. HITL: the owner re-dumps his own physical disc with a Redump-compatible method (a PC DVD drive and a dumping tool that reports read errors instead of filling them silently), then the agent re-hashes it. Done when the new image's CRC32, MD5 and SHA-1 match Redump disc 5234, or when it is clear they cannot, and why. If the Arcade Release is chosen instead, rule this ticket out of scope.

_PT-BR: a imagem de PS2 do dono é a versão certa, mas o hash da imagem inteira não bate com o dump verificado do Redump. Se a versão de PS2 virar a versão-base, o dono precisa de uma imagem idêntica à do Redump, para que o que ele testa seja igual, byte a byte, ao que os colaboradores extraem dos próprios discos. O dono refaz o dump do próprio disco num leitor de DVD de PC, com uma ferramenta que avisa dos erros de leitura em vez de preenchê-los em silêncio, e o agente confere os hashes de novo. Termina quando os hashes baterem com o disco 5234 do Redump, ou quando ficar claro que não vão bater, e por quê. Se a versão de arcade for a escolhida, este ticket sai do escopo._

## Notes

- 2026-11-11, from [Inspect the code structure of each candidate release](08-inspect-code-structure.md): the likely cause of the mismatch is read errors. `KOF_0001.DAT`, otherwise high-entropy from start to end, contains 42 runs of all-zero sectors (800 sectors), each 16 or 32 sectors long and aligned to 16 sectors, between sectors ~1.09 and ~1.17 million, near the outer edge. A DVD error-correction block is 16 sectors, so this is the usual mark of unreadable blocks that the dumping tool filled with zeros. When re-dumping, watch that area: clean the disc and use a tool that reports read errors. The main program is not affected (its CRC matches PCSX2's).

  _PT-BR: a causa provável são erros de leitura: o `KOF_0001.DAT` tem 42 trechos zerados em blocos de 16 setores (o bloco de correção de erro do DVD), perto da borda do disco. Ao refazer o dump, atenção a essa região: limpar o disco e usar uma ferramenta que avise dos erros. O programa principal não foi afetado._
