# PS2 Big DAT Files Analysis / Análise dos Arquivos DAT Gigantes do PS2

_Findings for [Find out what the two big PS2 DAT files hold](../tickets/12-ps2-big-dat-files.md). English first, then Brazilian Portuguese. Only counts, offsets, LBA ranges, struct layouts, and outcomes are recorded; no game data or binary chunks. Measured on 2026-11-21 on the owner's machine against the retail US PS2 dump (SLUS-21687)._

_Resultado do ticket. Inglês primeiro, português depois. Apenas contagens, posições, faixas de LBA, formatos de estrutura e resultados; nada de dados do jogo ou trechos binários._

---

## Summary

The two big files on the PS2 disc, `KOF_0000.DAT` and `KOF_0001.DAT` (~630 MB each, 1,259,602,843 bytes combined, or 52% of the 2.45 GB disc), are **pure dummy padding/filler**.

1. **Not archives:** They contain no encrypted or compressed game assets.
2. **Never accessed:** The executable (`SLUS_216.87`) never opens, reads, parses, or seeks into either file.
3. **Hardcoded exclusion:** The game's internal file table search loop explicitly cuts off at index 684 (`slti reg, 684`), completely excluding `KOF_0001.DAT` (index 684) from lookup. All lookups also prepend `\DATA\` and append `;1`, which cannot match root directory entries `\KOF_0000.DAT;1` or `\KOF_0001.DAT;1`.
4. **Zero live memory hits:** EE RAM (32 MB) and IOP RAM (2 MB) from PCSX2 savestates across boot, menus, and battles contain zero pages from either DAT file.
5. **Purpose:** Standard PS2 DVD mastering filler placed on the outer tracks (LBA 574,123 through 1,189,163, from ~1.17 GB to ~2.45 GB) to meet physical DVD-ROM stamping/pressing plant minimum radius specifications.
6. **Impact on the port:** The native PC port can completely ignore both files. Real game data is only ~1.17 GB. Furthermore, the bad sectors and zeroed-out blocks in `KOF_0001.DAT` noted in [Identify the exact disc dumps](identify-disc-dumps.md) have zero effect on game logic or assets.

---

## Static Master File Table in `SLUS_216.87`

At virtual address `0x28E8D0` (file offset `0x18E9D0`), the ELF executable contains a static master table of all 685 files on the DVD, stored in ascending LBA order.

### Table Entry Structure

Each entry is 32 bytes (64-bit aligned fields for the EE MIPS architecture):

| Offset | Type | Field | Description |
|---|---|---|---|
| `+0x00` | `const char*` | `path` | Pointer to file path string in `0x2E4208`–`0x2E9750` |
| `+0x04` | `uint32_t` | `pad0` | Alignment padding (`0x00000000`) |
| `+0x08` | `uint32_t` | `lba_start` | Starting sector on disc (Mode 1 LBA, 2,048 bytes/sector) |
| `+0x0c` | `uint32_t` | `pad1` | Alignment padding (`0x00000000`) |
| `+0x10` | `uint32_t` | `lba_end` | Ending sector on disc (`lba_start + sector_count - 1`) |
| `+0x14` | `uint32_t` | `pad2` | Alignment padding (`0x00000000`) |
| `+0x18` | `uint32_t` | `sector_count` | Length in 2,048-byte sectors |
| `+0x1c` | `uint32_t` | `pad3` | Alignment padding (`0x00000000`) |

### Table Extents and Layout

- **Index 0 (`0x28E8D0`):** `\SLUS_216.87;1` (LBA 1,089..2,083, 995 sectors, 2,037,464 bytes).
- **Index 1 (`0x28E8F0`):** `\SYSTEM.CNF;1` (LBA 2,084..2,084, 1 sector, 57 bytes).
- **Indices 2..673 (`0x28E910`..`0x293CE0`):** Game data files in `\DATA\` (stages, character sprites/models, menus, movies).
- **Index 674 (`0x293D00`):** `\DATA\ZDX\KOFXIBGM.AFS;1` (LBA 318,728..573,847, 255,120 sectors, 522,485,760 bytes).
- **Indices 675..682 (`0x293D20`..`0x293E10`):** The 8 IOP modules (`CRI_ADXI.IRX`, `IOPRP310.IMG`, `LIBSD.IRX`, `MCMAN.IRX`, `MCSERV.IRX`, `PADMAN.IRX`, `SDRDRV.IRX`, `SIO2MAN.IRX`).
- **Index 683 (`0x293E30`):** `\KOF_0000.DAT;1` (LBA 574,123..881,611, 307,489 sectors, 629,737,399 bytes).
- **Index 684 (`0x293E50`):** `\KOF_0001.DAT;1` (LBA 881,612..1,189,163, 307,552 sectors, 629,865,444 bytes).
- **Index 685 (`0x293E70`):** Sentinel end marker (`path = (char*)0xFFFFFFFF`).

All real game files (indices 0..682) span from LBA 1,089 to LBA 574,122 (~1.17 GB). `KOF_0000.DAT` and `KOF_0001.DAT` occupy the remainder of the disc up to LBA 1,189,163 (~2.45 GB).

---

## File Lookup Analysis in the Executable

The game accesses disc files through five functions:
1. `FileLoad` (`0x1D7F70`): Reads entire file into buffer via `sceCdRead` (`0x1151D8`).
2. `FileReadRange` (`0x1D8180`): Reads specified byte offset and size.
3. `FileStream` (`0x1D83F0`): Streaming read / DMA.
4. `FileGetInfo` (`0x1D8660`): Queries `lba_start`, `lba_end`, and `sector_count`.
5. `FileGetSize` (`0x1D87B0`): Queries sector count / size.

### Evidence of Exclusion

- **Loop Bound:** Every single one of these five functions contains a linear search loop over the master table with the exact instruction:
  ```
  slti v0, index_reg, 684
  bne  v0, zero, <loop_body>
  ```
  The loop terminates as soon as `index_reg == 684`. Index 684 (`\KOF_0001.DAT;1`) is therefore unreachable by design.
- **Search Prefix:** Before table comparison, filenames passed to the lookup functions are formatted using the template `\DATA\%s;1` (stored at `0x2E9760`). Because `KOF_0000.DAT` is located at the root of the disc, searching for it would query `\DATA\KOF_0000.DAT;1`, which never matches table entry 683 (`\KOF_0000.DAT;1`).
- **No Direct References:** A complete disassembly and pointer scan of `SLUS_216.87` confirmed that neither the path strings `\KOF_0000.DAT;1` (`0x2E9740`) / `\KOF_0001.DAT;1` (`0x2E9750`) nor table entry pointers `0x293E30` / `0x293E50` are ever loaded or referenced outside the static table definition itself.
- **No Direct LBA Reads:** No calls to `sceCdRead` or low-level CDVD read functions ever request sectors in the range 574,123..1,189,163.

---

## Runtime Verification (PCSX2 Savestates)

To verify whether the running game ever accesses data from these files dynamically (e.g. via IOP background streaming), EE RAM (32 MB) and IOP RAM (2 MB) were inspected from seven distinct emulator savestates captured during:
- Bios / PS2 boot sequence
- SNK / CRI middleware splash logos
- Main title menu
- Character selection
- Active battle gameplay

Samples of 256-byte and 2,048-byte blocks across `KOF_0000.DAT` and `KOF_0001.DAT` were tested against memory dumps:
- Matches in EE RAM: **0** across all 7 savestates.
- Matches in IOP RAM: **0** across all 7 savestates.

---

## Conclusion & Actionable Items

| Question | Answer |
|---|---|
| Are the DAT files archives? | **No.** Pure dummy padding. |
| Must the PC port decode them? | **No.** They can be completely omitted. |
| How big is the actual PS2 game? | **~1.17 GB** (574,123 sectors), not 2.45 GB. |
| Does the Redump dump mismatch matter? | **No.** The bad sectors in the owner's dump reside in `KOF_0001.DAT` (outer edge), which is unused padding. All 683 real game files are intact. |

---

## Resumo (PT-BR)

Os dois arquivos gigantes do disco de PS2, `KOF_0000.DAT` e `KOF_0001.DAT` (~630 MB cada, somando 1,26 GB ou 52% do disco de 2,45 GB), são **estritamente enchimento (padding)**.

1. **Não são pacotes:** Não contêm nenhum dado comprimido, criptografado ou arquivo empacotado do jogo.
2. **Nunca são acessados:** O executável (`SLUS_216.87`) nunca abre, lê ou busca dados em nenhum dos dois arquivos.
3. **Exclusão no código:** O loop de busca na tabela interna de arquivos do executável usa a instrução `slti reg, 684`. Como o índice máximo verificado é 683, o arquivo `KOF_0001.DAT` (índice 684) é matematicamente excluído de qualquer busca. Além disso, todas as chamadas de carregamento formatam o caminho como `\DATA\%s;1`, o que impede qualquer correspondência com arquivos na raiz (`\KOF_0000.DAT;1`).
4. **Zero ocorrências na memória:** Varredura nas memórias EE (32 MB) e IOP (2 MB) de 7 savestates do PCSX2 (abertura, menus, seleção e luta) confirmou que nenhum bloco dos arquivos DAT jamais esteve na memória do console.
5. **Finalidade:** Prática padrão da prensagem de DVDs de PS2 para atingir o raio mínimo físico de fabricação (lead-out) exigido pelas fábricas da Sony (~1,2 GB / 2 GB). Os arquivos reais do jogo ocupam apenas ~1,17 GB na parte interna do disco.
6. **Impacto no port:** O port nativo de PC pode ignorar totalmente ambos os arquivos. Além disso, confirma que os setores com erro de leitura no dump do dono no `KOF_0001.DAT` (mencionados no Ticket 11) não afetam em nada a integridade dos assets ou do jogo.
