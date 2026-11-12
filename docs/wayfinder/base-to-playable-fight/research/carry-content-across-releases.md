# Carrying content across releases / Levar conteúdo de uma versão para a outra

_Findings for [Assess carrying content across releases](../tickets/09-carry-content-across-releases.md). English first, then Brazilian Portuguese. Researched 2026-11-11. Facts and rough effort only; the choice belongs to [Choose the base version](../tickets/05-choose-base-version.md). No game content appears here: the local measurements below are counts and percentages, and their scripts stayed in `private/scratch/`._

## Resumo em português

- **O conteúdo corre num sentido só.** Tudo o que a versão de arcade tem de conteúdo o PS2 também tem. O dono confirmou: no PS2, "Arranged" é uma opção. Ligada, traz as fases novas, as músicas modificadas e o balanceamento novo no jogo inteiro; desligada, o jogo fica com o balanceamento do arcade. Mesmo desligada, os lutadores exclusivos do PS2 e o Color Edit continuam disponíveis. O que o arcade tem de melhor é **técnico** (hardware mais simples, rollback que já funciona no Flycast), não conteúdo.
- **Base PS2 + vantagens do arcade:** quase nada a transportar. As vantagens do arcade não são arquivos que se copiam; são propriedades do port nativo, que precisam ser construídas de qualquer jeito. O custo está no próprio PS2, que é a base mais difícil de recompilar (tickets 01–03).
- **Base arcade + conteúdo do PS2:** esforço **muito alto**. Os processadores são diferentes, então nenhum código do PS2 pode ser reaproveitado. Os modos Challenge, Edit e Team teriam de ser reescritos. Os lutadores extras, as fases 3D novas e os finais exigem entender formatos de dados não documentados dos dois lados e escrever conversores. Além disso, o ajuste dos controles do PS2, que você preferiu, se perderia.
- **Medição local:** cerca de 1/6 dos trechos dos arquivos de lutadores do PS2 aparece idêntico, byte a byte, nos dados do cartucho, mas em pedaços pequenos e espalhados. As paletas de cor são ~90% idênticas. Cenários, menus e galeria: praticamente nada em comum. Conclusão: os mesmos materiais de origem, reembalados de outro jeito. Copiar não basta; é preciso converter.
- **Conhecimento público:** praticamente nenhum. Não há documentação de formato nem ferramenta de modding para o KOF XI em nenhuma das versões.

---

## 1. What "the best of both" contains

From [compare-base-versions.md](compare-base-versions.md), the owner's hands-on comparison ([ticket 10](../tickets/10-hands-on-comparison.md)) and the sources below:

| Strength | Where it lives | Kind |
|---|---|---|
| Playable bosses, 7 NGBC-derived fighters (all must-keeps for the owner) | PS2 only | Content: fighter data + roster/unlock code |
| Challenge, Edit and classic Team modes | PS2 only | Content: **game code** + menus + data |
| 4 extra stages ("several new 3D backgrounds", per HG101) | PS2 only, active when the Arranged option is on | Content: stage data + stage code |
| Arranged soundtrack | PS2 only, active when the Arranged option is on | Content: audio (CRI ADX in AFS) |
| Extra endings | PS2 only | Content: scenes |
| More responsive controls (owner's experience; the port's controls "were made more responsive, based on feedback from the arcade", per Wikipedia) | PS2 only | Code (input handling and/or move data) |
| "Arranged" balance changes | PS2 only, applied to the whole game when the Arranged option is on | Code + data |
| Original arcade balance | Arcade; **also in the PS2 Release** with the Arranged option off (TV Tropes: the PS2 version offers "an option to turn off the Arrange Mode"; confirmed by the owner) | Code + data |
| Simpler hardware, lighter to run | Arcade | Technical, not content |
| Working online rollback (Flycast GGPO; the owner tested it) | Arcade, under emulation | Technical, not content |
| Hidden characters behind the time-release menu | Arcade | Same fighters the PS2 unlocks through play |

**Confirmed by the owner (2026-11-11):** on the PS2, "Arranged" is an option. When on, it brings the new stages, the modified music and the rebalancing to the whole game. When off, the game has the arcade balance. Even with it off, the PS2-exclusive fighters and Color Edit stay available. So the PS2 with Arranged off is the arcade balance with a larger roster and Color Edit, not an exact copy of the Arcade Release.

## 2. What differs between the two releases' engines and data

- **CPU and code.** The PS2 program is MIPS R5900 code built with Metrowerks CodeWarrior; the arcade program is SH-4 code ([inspect-code-structure.md](inspect-code-structure.md)). No code can be moved between them. Any PS2-only feature that is code (modes, Arrange balance logic, input changes, roster and unlock handling) would have to be rewritten for the arcade base, either as new SH-4 code or as native C++ hooked into the recompiled game.
- **Containers.** The PS2 keeps data in 685 named files with game-specific formats (`.UNI`, `.GRC`, `.LZ`, `.BCC`, `.PK`, …). The arcade keeps it in an unnamed cartridge file system across 7 mask ROMs. Neither format is publicly documented.
- **Graphics.** Each release stores graphics for its own chip: the PS2 for the GS (textures and colour tables in GS formats, 3D drawn through VU1), the arcade for the PowerVR2 (textures in its own layouts, display lists built by the SH-4). The PS2's 4 extra stages use 3D backgrounds made for that path.
- **Audio.** The PS2 plays music through CRI ADX streams in an AFS archive (open-source decoders exist). The arcade drives the AICA chip through its ARM7 driver. In a native port the music is played by the host either way, so audio is the cheapest content to carry.
- **NGBC-derived fighters.** Their PS2 versions "are the same versions as found in Neo Geo Battle Coliseum" (HG101) and "mostly recycle their graphics from NeoGeo Battle Coliseum" (TV Tropes), but at least one moveset was reworked for KOF XI (Dream Cancel on Geese). The Atomiswave NGBC exists and would carry the same graphics in arcade-side formats, but the owner has no NGBC dump, and the fighters would still need KOF XI's movesets, roster slots and unlock logic.

### Local measurement: how much raw data the two releases share

Method: every 256th 16-byte window of the PS2's uncompressed data files (compressed `.LZ`, the music archive, cut-scenes and the two big DAT files excluded) was looked up at every byte offset of the decrypted arcade cartridge. Windows made of one repeated byte were skipped. A control run kept only "rich" windows (8 or more distinct byte values), which are unlikely to repeat by chance. Byte-level only: data converted to another layout will not match even if it is the same picture.

| PS2 data | Rich windows found in the arcade cart | Notes |
|---|---|---|
| Fighter folders `/DATA/PL`, `PL2`, `PLA`, `PLA2` | 16.4%, 12.6%, 18.5%, 13.8% | Every one of the 100 `.UNI` files shares some data (9% to 49% of all its windows); none shares more than half. Matches land almost entirely in `mrom1`–`mrom2` |
| Palettes `/DATA/PAL`, `PAL2` (all windows) | 91.1%, 67.1% | Colour data largely identical |
| Small tables (ranking, continue, misc.; all windows) | 99.6–100% | Tiny files |
| Main program (ELF; all windows) | 2.2% | Matches land in the arcade **program**: some data tables are shared |
| Stages `/DATA/BG` | 1.1% | Mostly different |
| Stage binaries, menus, missions, logo, gallery, `/DATA/PLUS` | 0.0% | Nothing in common |

**Shape of the shared data.** Matched windows are scattered, not long blocks: a run of consecutive matches has a median length of one sample (256 bytes) and a maximum of 108 samples (~27 KB). So the fighter files and the cart share pieces of the same source data in the same encoding, packed differently. Carrying a fighter across therefore needs a converter that understands both containers. A plain copy will not work.

## 3. What is publicly known

Almost nothing usable:

- No format documentation, decompilation or modding tool for KOF XI or NGBC on either platform was found (see also [compare-base-versions.md](compare-base-versions.md) §5).
- The MUGEN community has a KOF XI downloads category and sprite discussions, which shows sprites have been extracted somehow, but no tool or method was published in the sources found.
- No arcade hack that adds PS2 content, and no PS2 hack that restores arcade-only behaviour, was found.
- Not readable from this session: the SRK wiki (bot protection), The Cutting Room Floor, Sega Retro. Character-level version differences may be documented there.

## 4. Rough effort in each direction

Scale: **S** small (days), **M** medium (weeks), **L** large (months), **XL** research-grade (months, with uncertain outcome). Each estimate is relative and assumes a working native port of the chosen base already exists.

### A. PS2 Release as the base, adding the arcade's strengths

| Item | Effort | Why |
|---|---|---|
| Arcade content | none | Already in the PS2 Release (Arranged option off; confirmed by the owner) |
| Lighter to run | n/a | Not transferable: a native port is fast or slow on its own merits. The cost sits in the PS2 base itself (GS, VU1, IOP; tickets 01–02) |
| Rollback | n/a | Not transferable: must be built into the port in either case (ticket 03). The arcade's head start is a working emulator precedent, not reusable code (Flycast is GPL) |

### B. Arcade Release as the base, adding the PS2's content

| Item | Effort | Why |
|---|---|---|
| Arranged soundtrack | S–M | Decode ADX on the host, then hook the arcade's music calls |
| Palettes / Edit Mode colours | M | Palettes largely identical; Edit Mode itself is new code (UI + saving) |
| Each extra fighter (NGBC-derived, bosses) | L each, XL for the first | Reverse-engineer both releases' fighter formats and the arcade's roster/loading tables, write a converter, and re-create the PS2 movesets. No public groundwork |
| Challenge, classic Team, Endless modes | L | Rewrite the mode logic, menus and unlock rules; the PS2 code cannot be reused |
| 4 extra stages | L | 3D backgrounds built for GS/VU1 must be rebuilt for the PowerVR2 path, plus stage code |
| Arrange balance and the PS2's control feel | L–XL | Spread through the PS2's code and move data; would have to be identified and re-applied |
| Endings and cut-scenes | M | Data conversion plus scene code |

### Summary

Content moves one way: from the PS2 Release to the arcade code, at a cost that adds up to more than porting a whole release, item by item, on undocumented formats. The other direction carries no content; what the arcade offers is cheaper hardware to recompile and a rollback precedent, and neither can be "carried": they only show up by choosing the arcade as the base. So the real trade-off for [Choose the base version](../tickets/05-choose-base-version.md) is: **a harder base that already has everything (PS2)** versus **an easier base that would then need most of the PS2's content rebuilt (arcade)**.

## Sources

- [The King of Fighters XI (Hardcore Gaming 101)](https://www.hardcoregaming101.net/king-of-fighters-xi/): PS2 extras, Arrange (described there as a mode; the owner confirmed it is an option), NGBC versions, loading
- [The King of Fighters XI (TV Tropes)](https://www.tvtropes.org/pmwiki/pmwiki.php/VideoGame/TheKingOfFightersXI): Arrange option and balance changes, recycled NGBC graphics, unlocks
- [The King of Fighters XI (Wikipedia)](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI): control changes in the port
- [The King of Fighters XI (StrategyWiki)](https://strategywiki.org/wiki/The_King_of_Fighters_XI): PS2 modes
- [The King of Fighters XI (Dream Cancel Wiki)](https://dreamcancel.com/wiki/The_King_of_Fighters_XI) and [Geese Howard (KOF:XI)](https://dreamcancel.com/wiki/Geese_Howard_(KOF:XI)): PS2-only bosses, reworked moveset
- [King of Fighters XI downloads (The MUGEN Archive)](https://mugenarchive.com/forums/downloads.php?do=cat&id=59-king-of-fighters-xi): evidence of extracted sprites
- Local measurements: [inspect-code-structure.md](inspect-code-structure.md) for the dumps and the cart decryption
