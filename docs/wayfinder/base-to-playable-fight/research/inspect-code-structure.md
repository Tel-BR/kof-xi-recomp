# Code structure of each candidate release / Estrutura do código de cada candidato

_Findings for [Inspect the code structure of each candidate release](../tickets/08-inspect-code-structure.md). English first, then Brazilian Portuguese. Only sizes, counts, formats, offsets and hashes are recorded; nothing from inside the games. Measured on 2026-11-11 on the owner's machine, against the dumps identified in [identify-disc-dumps.md](identify-disc-dumps.md). The scripts and any intermediate files stayed in `private/scratch/` (git-ignored)._

_Resultado do ticket. Inglês primeiro, português depois. Só tamanhos, contagens, formatos, posições e hashes; nada de dentro dos jogos. Os scripts e arquivos intermediários ficaram em `private/scratch/`, que o git ignora._

## Summary

| | PS2 Release (SLUS-21687) | Arcade Release (Atomiswave cart `kofxi`) | Dreamcast Conversion |
|---|---|---|---|
| Main program format | Standard PS2 ELF (MIPS R5900), 2,037,464 bytes | Raw SH-4 binary in the cart's flash ROM, after a 256-byte cart header; **encrypted** on the cart | Raw SH-4 binary `1ST_READ.BIN`, 1,189,920 bytes, unencrypted |
| Program size | 2,036,736 bytes loaded, plus ~28.6 MB zero-initialised memory reserved | 1,189,920 bytes | 1,189,920 bytes |
| Symbols / debug info | None (symbol table empty, section names stripped) | None (no container at all) | None |
| Compiler | Metrowerks CodeWarrior for PS2 (`MW MIPS C Compiler 2.4.1.01`, from the ELF's comment section) | Not identified | Same as arcade |
| Code vs data (heuristic) | About 66% of the loaded image looks like code (~1.3 MB code, ~0.7 MB data) | About 88% looks like code (~1.05 MB) | Same as arcade |
| Separately loaded code | No overlays found. Only the 7 IOP modules plus one IOP replacement image are separate code | No SH-4 overlays found in the mask ROMs. An ARM7 code block (presumably the sound driver) sits inside the program image | Same as arcade |
| Game data | ~2.4 GB in 685 files (see below) | 7 mask ROMs (224 MiB), encrypted, holding a cartridge file system | The same 7 mask ROMs, **decrypted**, stored as one raw block in track 3 |

**Answer to the Dreamcast question.** The hypothesis "small loader plus the arcade cartridge data" is only half right. There is no separate loader: `1ST_READ.BIN` **is** the arcade program, taken from the cart's flash ROM and decrypted, with **754 bytes changed in 28 places** (the converter's patches; the largest change is 314 bytes). The cart's mask-ROM data is stored decrypted and **byte-identical** to the owner's cartridge dump. So the arcade code inside the conversion matches the owner's cartridge, except for those patches.

## PS2 Release

**Disc layout.** 685 files, 2,432,567,552 bytes. The ISO file table and the boot line were read; no file content was kept.

| Where | Files | Size | What it is (from names and formats only) |
|---|---|---|---|
| `/SLUS_216.87` | 1 | 2.0 MB | Main program (ELF) |
| `/MODULES/` | 8 | 0.56 MB | IOP side: `IOPRP310.IMG` (Sony IOP replacement image), `SIO2MAN`, `PADMAN`, `MCMAN`, `MCSERV`, `LIBSD`, `SDRDRV` (Sony SDK modules) and `CRI_ADXI` (CRI ADX audio middleware) |
| `/KOF_0000.DAT`, `/KOF_0001.DAT` | 2 | 1.26 GB (52% of the disc) | See "The two big DAT files" below |
| `/DATA/ZDX/` | 2 | 522 MB | Music, in one CRI AFS archive |
| `/DATA/DEMO/` (+ 4 subfolders) | 80 | 353 MB | Cut-scenes and endings |
| `/DATA/PL`, `/DATA/PL2`, `/DATA/PLA`, `/DATA/PLA2` | 100 | 116 MB | Per-fighter data, in four sibling folders of 24–26 files each |
| `/DATA/PAL`, `/DATA/PAL2` | 50 | 0.3 MB | Colour palettes |
| `/DATA/BG*`, `/DATA/WIN/*`, `/DATA/GALLERY/*`, `/DATA/MENU`, `/DATA/MISSION0`, `/DATA/MISSION1`, `/DATA/RANKING`, others | ~440 | ~0.2 GB | Stages, win screens, gallery, menus and mode data |

File formats by extension: `.LZ` 180 files (compressed; entropy 6.4 bits/byte median), `.GRC` 151, `.BIN` 103, `.UNI` 100, `.PAL` 50, `.DAT` 29, `.RAW` 22, `.BCC` 19, `.PK` 9, `.IRX` 7, `.MDP` 6, `.AFS` 1. None of these formats is publicly documented for this game, except AFS and ADX, which are CRI middleware formats with open-source readers.

**Main program (ELF).** Type executable, machine MIPS, R5900 flags, entry point 8 bytes into the load segment.

- Program headers: one loadable read-write-execute segment at `0x100000` (2,036,736 bytes in the file, 30,594,176 bytes in memory, so about 28.6 MB of the 32 MB main RAM is reserved as zero-initialised memory); an empty segment; and a 6,624-byte segment at `0x70000000` (the scratchpad).
- Sections: the code and data sections are merged and their names stripped. `.symtab` and `.strtab` exist but are **empty**. There is no debug section (no `.debug_*`, no `.mdebug`).
- The executable refers to `cdrom0:` paths and to all the file types above, including both big DAT files.
- Searching every disc file for the ELF signature and for MIPS function returns finds code only in the main program and in the IOP modules. Compressed `.LZ` files cannot be checked without knowing their format, so a compressed overlay cannot be ruled out, but nothing points to one.

**The two big DAT files.** Both have near-maximum entropy (7.9 bits/byte) from their first sector to their last, share no 2 KB block with any other file, and are each referenced once by the executable. That fits either encrypted or compressed archives, or filler data placed to push the real files to the faster outer part of the DVD. Which one it is remains open; it matters, because an encrypted archive would have to be decoded by the port.

**Likely cause of the Redump mismatch** (relevant to [Get a Redump-verified PS2 image](../tickets/11-redump-verified-ps2.md)). `KOF_0001.DAT` contains **42 runs of all-zero sectors (800 sectors in total)**, each 16 or 32 sectors long and aligned to 16 sectors, inside otherwise high-entropy data, near the outer edge of the disc (sectors ~1.09 to ~1.17 million). A DVD error-correction block is 16 sectors. This is the usual signature of unreadable blocks that the dumping tool filled with zeros. `KOF_0000.DAT` has none.

## Arcade Release (Atomiswave cartridge)

- **The cartridge dump is encrypted.** The raw flash and mask ROMs show 8.0 bits/byte of entropy everywhere. MAME's `aw_rom_board` (file `src/mame/sega/awboard.cpp`, **BSD-3-Clause**) documents the cipher and MAME's driver gives this game's key. Applying them locally produced the standard Atomiswave cart header and a program that matches the Dreamcast Conversion (below), which confirms the decryption.
- **Flash ROM (`fmem1`, 8 MiB):** a 256-byte cart header, then the program (1,189,920 bytes), then erased flash. The header's data offset says the mask-ROM area starts at cart address `0x2000000`.
- **Mask ROMs (`mrom1`–`mrom7`, 7 × 32 MiB):** game data in a cartridge file system, organised in three banks (`mrom1`–`3`, `mrom4`–`6`, `mrom7`), each starting with a header. The record format is visible only through MAME's access code; files were not counted. Only the last 2.4 MiB of `mrom7` is unused.
- **Code inside the data:** a scan for SH-4 code found only scattered 4 KB windows in the mask ROMs (179 of 57,344, with no run of 64 KB or more), consistent with data, not overlays. An ARM7 block with 214 ARM return instructions sits inside the program image, and a block with the same count sits in `mrom6`: most likely the AICA sound driver, uploaded to the sound CPU by the main program.
- **Where fighter and mode data live:** inside the mask-ROM file system. Unlike the PS2 disc, there are no file names, so locating a fighter's data needs the file-system records and the program's loading code.

## Dreamcast Conversion

- **Tracks:** the GDI lists track 1 (data, LBA 0), track 2 (audio, LBA 450), track 3 (data, LBA 45000) and track 4 (data, LBA 450000).
- **File system:** only **2 files**: `1ST_READ.BIN` (1,189,920 bytes, stored in track 4; SHA-1 `97fdf421562441108af76694b583ffbfafb5cd1c`) and `0GDTEX.PVR` (131,104 bytes, the disc's boot-menu art). The volume label names a different Atomiswave game, a leftover from the converter's template.
- **Track 3 beyond the file table:** at byte 614,400 (LBA 45300) start the 7 mask ROMs, decrypted and concatenated in order, **all 57,344 pages of 4 KB identical** to the decrypted cartridge dump. A 16 KB block, almost all zeros, follows them.
- **Program:** `1ST_READ.BIN` equals the decrypted flash program (from cart offset `0x100`) except for 754 bytes in 28 runs. These patches presumably replace the cart reads and the arcade I/O (see [compare-base-versions.md](compare-base-versions.md) §2); their content is not recorded here.

## What this changes for later tickets

- **Choose the base version:** the Arcade Release's code can be taken cleanly from the owner's own cartridge (decrypt with MAME's BSD-3 algorithm and key), with no community patches. The Dreamcast Conversion is the same code plus 754 bytes of patches. Starting from the cart, the port must provide the cart's file-read interface and the Atomiswave I/O natively; starting from the conversion, it must provide the GD-ROM and controller paths the patches switched to.
- **Recompiler:** neither release has symbols or debug info; function discovery must come from code analysis. The PS2 program is compiled with Metrowerks CodeWarrior, not GCC, which matters for tools that rely on GCC prologue patterns. The arcade program is about 1.19 MB of SH-4 code with no container format.
- **Graphics and audio:** the PS2 build plays music through CRI ADX/AFS and uses Sony's `LIBSD`/`SDRDRV` modules, recognisable libraries that make the high-level audio option (A3) plausible in [graphics-audio-options.md](graphics-audio-options.md). The number of VU1 microprograms was not measured.
- **Carry content across releases:** the PS2 fighters live in named per-fighter folders with undocumented formats; the arcade data lives in an unnamed cartridge file system. Neither format is documented.

## Method

Python scripts on the owner's machine: ISO 9660 parsing of the PS2 image and of the Dreamcast data tracks; ELF header, program-header and section-header parsing; Shannon entropy per sector and per MiB; search for the ELF signature, MIPS `jr ra`, SH-4 `rts`/`nop` and ARM `mov pc, lr` patterns per 4 KB window (a heuristic, not a disassembly); 2 KB and 4 KB block hashing and page-by-page comparison between the decrypted cart and the Dreamcast image.

Sources: [MAME `awboard.cpp`](https://github.com/mamedev/mame/blob/master/src/mame/sega/awboard.cpp) (cart cipher and layout, BSD-3-Clause); [MAME `dc_atomiswave.cpp`](https://github.com/mamedev/mame/blob/master/src/mame/sega/dc_atomiswave.cpp) (`kofxi` ROM map and key).

---

## Resumo (PT-BR)

- **PS2:** o programa principal é um ELF padrão de 2 MB, **sem símbolos nem informação de depuração**, compilado com o Metrowerks CodeWarrior (não o GCC). Cerca de dois terços é código. Não há overlays: o único código separado são os 7 módulos do processador de E/S (IOP), quase todos bibliotecas da Sony, mais o middleware de som CRI ADX. Os dados ocupam 685 arquivos; os lutadores ficam em quatro pastas irmãs (`/DATA/PL*`), a música num arquivo AFS da CRI, e dois arquivos `KOF_000x.DAT` de 630 MB cada (52% do disco) parecem aleatórios: podem ser pacotes criptografados ou só enchimento. Isso fica em aberto.
- **Pista para o Redump:** o `KOF_0001.DAT` tem 42 trechos zerados, em blocos de 16 setores (o tamanho do bloco de correção de erro do DVD), perto da borda do disco. É a marca típica de setores que o leitor não conseguiu ler e a ferramenta preencheu com zeros. Provavelmente é por isso que o hash não bate.
- **Arcade (cartucho):** o dump do cartucho é **criptografado**. O MAME documenta a cifra (licença BSD-3, compatível com MIT) e a chave do jogo; aplicando-as localmente, sai o programa: 1,19 MB de código SH-4, sem símbolos. Os dados ficam em 7 ROMs de 32 MB, num sistema de arquivos do cartucho, sem nomes de arquivo. Não há overlays de código; há um bloco ARM7, quase certamente o driver de som.
- **Dreamcast:** **não** é "um carregador mais os dados". O `1ST_READ.BIN` **é** o programa do arcade, descriptografado, com **754 bytes alterados em 28 pontos** (os patches do conversor). Os dados das 7 ROMs estão gravados descriptografados na trilha 3 e são **idênticos byte a byte** ao dump do seu cartucho.
- **Consequência:** o código de arcade pode vir limpo do seu próprio cartucho, sem patches de terceiros. A conversão de Dreamcast é o mesmo código com 754 bytes de remendo.
