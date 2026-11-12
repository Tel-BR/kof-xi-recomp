# Identify the exact disc dumps / Identificar exatamente os dumps

_Findings for [Identify the exact disc dumps](../tickets/04-identify-disc-dumps.md). English first, then Brazilian Portuguese. Only hashes and identification fields are recorded here; nothing from inside the games._

_Resultado do ticket. Inglês primeiro, português depois. Só hashes e campos de identificação; nada de dentro dos jogos._

Checked on 2026-11-11 against Redump (PS2 disc 5234) and MAME 0.289 (`kofxi`, `sega/dc_atomiswave.cpp`).

## Summary

| Dump | Identified as | Matches the reference database? |
|---|---|---|
| PS2 image | **PS2 Release, USA/Canada, SLUS-21687, version 1.00** (Redump disc 5234) | **No.** Same size, same volume date, same executable, but the whole-image hash differs from Redump's verified dump. |
| Atomiswave cartridge | **Arcade Release, MAME set `kofxi`** (no clones exist) | **Yes.** All 8 cartridge ROMs match MAME's "good" hashes byte for byte. |
| Dreamcast image | **Dreamcast Conversion by megavolt85**, first released on Dreamcast-Talk on 2020-11-06/07 | No database exists (fan-made); hashes below are the owner's reference. |

## PS2 Release

- Serial from the boot line: `SLUS_216.87` (SLUS-21687), `VER = 1.00`, `VMODE = NTSC`.
- Volume ID `KING_OF_FIGHTERS_XI`, volume created 2007-09-02 22:28:34 (+09:00): same as Redump.
- Boot executable recorded 2007-10-05 (+09:00): same as Redump's EXE date.
- Boot executable PCSX2 game CRC: `581A4DAA`, the CRC the PCSX2 wiki lists for SLUS-21687.

| | Size | CRC32 | MD5 | SHA-1 |
|---|---|---|---|---|
| Owner's image | 2456387584 | `0392eb32` | `badf06edd8c226f9718cb96f724c57f7` | `132c69ad8f8001b6998052ce4201ab65e9d61530` |
| Redump (verified) | 2456387584 | `656bb3dc` | `7a894aecf26968042f333a9732d412b6` | `edf007845af9c744dc24f1781c963bd5773c9c01` |

**What this means.** It is the right release, and its main program looks intact (the executable's CRC matches). But some bytes elsewhere in the image differ from the verified dump. Typical causes are a dump made with a tool or drive that filled unreadable sectors, or an image someone edited. Redump publishes only whole-image hashes for PS2, so the differing sectors cannot be located from here. Consequence: this image is fine for exploring, but it is not a good reference for collaborators, whose correctly dumped discs will hash as Redump's. See [Get a Redump-verified PS2 image](../tickets/11-redump-verified-ps2.md).

## Arcade Release (Atomiswave cartridge)

Container `kofxi.zip`: size 233064957, CRC32 `f06ec8ca`, SHA-1 `60a987829ba699141271726c94b2c0ac2024085b` (the zip itself is not a reference; its contents are).

| File (MAME name) | Size | CRC32 | SHA-1 | MAME |
|---|---|---|---|---|
| ax3201p01.fmem1 | 8388608 | `6dbdd71b` | `cce3897b104f5d923d8136485fc80eb9717ff4b5` | good |
| ax3201m01.mrom1 | 33554432 | `7f9d6af9` | `001064ad1b8c3408efe799dc766c2728dc6512a9` | good |
| ax3202m01.mrom2 | 33554432 | `1ae40afa` | `9ee7957c86cc3a71e6971ddcd906a82c5b1e16f1` | good |
| ax3203m01.mrom3 | 33554432 | `8c5e3bfd` | `b5443e2a1b88642cc57c5287a3122376c2d48de9` | good |
| ax3204m01.mrom4 | 33554432 | `ba97f80c` | `36f672fe833e13f0bab036b02c39123066327e20` | good |
| ax3205m01.mrom5 | 33554432 | `3c747067` | `54b7ff73d618e2e4e40c125c6cfe99016e69ad1a` | good |
| ax3206m01.mrom6 | 33554432 | `cb81e5f5` | `07faee02a58ac9c600ab3cdd525d22c16b35222d` | good |
| ax3207m01.mrom7 | 33554432 | `164f6329` | `a72c8cbe4ac7b98edda3d4434f6c81a370b8c39b` | good |

MD5s are in the owner's local `private/scratch/hashes.json`; MAME does not publish MD5.

**Gap for later tickets:** the Atomiswave BIOS lives on the motherboard, not the cartridge, so it is not in this dump. MAME's `kofxi` needs the `awbios` set (`bios0.ic23`, `bios1.ic23`, `fpr-24363.ic48`) to boot. This matters for the Reference Emulator ([verification oracle](../tickets/07-verification-oracle.md)) if the Arcade Release is chosen.

## Dreamcast Conversion

Identification header of the data track: product `T0001M`, version `V1.000`, date `20051026` (the arcade launch date, kept by the converter), area `J`, boot file `1ST_READ.BIN`, title "King of Fighters XI". GDI with 4 tracks, data tracks stored at 2048 bytes per sector (not Redump's raw format).

| File | Size | CRC32 | MD5 | SHA-1 |
|---|---|---|---|---|
| disc.gdi | 113 | `3a15f95b` | `c527f1ec937b56caa65084d436f8c0a0` | `59d06a3411be8a77cd3643f6ed8b4b6d2acc96c0` |
| track01.iso | 614400 | `39232fac` | `6ffcef32d687a23de0fc44062dd946d5` | `eb1acc6a3155f095ed4890bea2c4ee848e267a77` |
| track02.raw | 1237152 | `bc56e241` | `03c796f60db2e9ef0b65a42a47a9d321` | `1bc5d3822f954a634e1f39584f98da42784e914e` |
| track03.iso | 235511808 | `793e966c` | `880dd98f7dfce81278f66f564c124fff` | `a395a164a05fb839b7f97dd9dda585d45da6b136` |
| track04.iso | 1191936 | `ab50df22` | `fae377a65b3f0f63858603bb8240a238` | `4ffa681acd52c7ccf49f3486041355d690ad7f5b` |

Several builds circulated: the first GDI, later test builds from megavolt85 (for example one for USB-GDROM), and CDI images built by other people. Nobody published hashes, so which build this is cannot be confirmed. The converter also said he did not build the CDI and could not say what it changed, so CDI images should not be treated as equivalent to this GDI.

## Sources

- [Redump: The King of Fighters XI (PS2, USA)](http://redump.org/disc/5234/)
- [PCSX2 Wiki: The King of Fighters XI](https://wiki.pcsx2.net/The_King_of_Fighters_XI)
- [MAME 0.289 machine `kofxi` (spludlow data)](https://mame.spludlow.co.uk/Machine.aspx?name=kofxi)
- [SEGAbits: KOF XI ported to Dreamcast](https://segabits.com/blog/2020/11/07/king-of-fighters-xi-arcade-ported-to-sega-dreamcast-more-atomiswave-arcade-ports-coming/)
- [Dreamcast-Talk: Atomiswave Conversions FAQ](https://www.dreamcast-talk.com/forum/viewtopic.php?t=13621)
- [Dreamcast-Talk: King of Fighters XI thread](https://www.dreamcast-talk.com/forum/viewtopic.php?t=13580&start=170)

---

## Resumo (PT-BR)

- **PS2:** é a versão de PS2 americana/canadense, código SLUS-21687, versão 1.00 (disco 5234 do Redump). Tamanho, data do volume, data e CRC do executável batem. Mas o hash da imagem inteira **não** bate com o dump verificado do Redump. Algum trecho fora do executável principal está diferente. As causas comuns são um dump feito com ferramenta ou leitor que preencheu setores ilegíveis, ou uma imagem editada. Serve para explorar, mas não serve de referência para colaboradores, cujos discos bem extraídos vão dar o hash do Redump. Ver o ticket [Get a Redump-verified PS2 image](../tickets/11-redump-verified-ps2.md).
- **Arcade (cartucho Atomiswave):** os 8 arquivos do cartucho batem byte a byte com o conjunto `kofxi` do MAME 0.289, todos marcados como "good". O BIOS do Atomiswave fica na placa-mãe, não no cartucho, então não está no dump. O MAME precisa do conjunto `awbios` para rodar o jogo, o que pesa no emulador de referência caso a versão de arcade seja escolhida.
- **Dreamcast:** conversão feita por fã (megavolt85), lançada em novembro de 2020 no fórum Dreamcast-Talk, código `T0001M`, versão `V1.000`. Não existe banco de dados para ela, e ninguém publicou hashes; circularam várias builds (GDI inicial, testes posteriores e CDIs montadas por terceiros). Os hashes acima ficam como referência do dono.
