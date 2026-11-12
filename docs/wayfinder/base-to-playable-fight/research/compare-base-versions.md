# Compare PS2 and Dreamcast as the base version

Research ticket: "Compare PS2 and Dreamcast as the base version." This file gathers the facts; it does not make the decision. Researched 2026-11-11. No game data (disassembly, extracted assets, disc contents) appears here.

## Resumo em português

- **O "Dreamcast" não é um lançamento oficial.** A SNK nunca lançou KOF XI para Dreamcast. O disco que você tem é quase certamente a conversão caseira de 2020 (feita por "megavolt85") da versão de fliperama **Atomiswave**. Na prática, é o código do fliperama rodando no Dreamcast, que usa o mesmo processador e o mesmo chip gráfico.
- **O PS2 tem mais conteúdo.** Ele traz tudo do fliperama e acrescenta: chefes jogáveis (Shion, Magaki e outros), 7 personagens extras vindos do Neo Geo Battle Coliseum, Challenge Mode, Edit Mode (cores), Team Mode clássico, fases novas e trilha sonora rearranjada.
- **O fliperama/Dreamcast é a versão "original" de torneio.** É a versão que a comunidade joga online hoje, com rollback (GGPO), no emulador Flycast. Os personagens escondidos dela vêm de um sistema de liberação por tempo de uso da máquina.
- **Dificuldade técnica.** O PS2 é bem mais difícil de recompilar: tem vários processadores (EE, VU0/VU1, IOP) e um chip gráfico (GS) muito diferente dos PCs atuais. O Dreamcast é uma máquina mais simples, com um processador principal (SH-4), um gráfico (PowerVR2) e um de som (AICA/ARM7).
- **Ferramentas existentes.** Para PS2 existe o **PS2Recomp**, a ferramenta mais usada da área (GPL-3.0, muito ativa, já com 4 jogos lançados e 5 jogáveis), mas ainda "experimental" e lenta nos gráficos. Para Dreamcast há várias ferramentas novas de 2026 (dream-recomp, dcrecomp, DreamcastRecompiled), todas jovens. Um jogo de luta de Dreamcast (Street Fighter Alpha 3) já foi recompilado e está jogável. Nenhuma delas cita Atomiswave.
- **Risco específico do Dreamcast.** Como o disco é uma conversão caseira, o programa do jogo provavelmente fica dentro de um grande bloco de dados copiado do cartucho (cerca de 232 MB, o que bate com o seu track03 de ~235 MB), e não no formato normal de jogo de Dreamcast. As ferramentas atuais esperam o formato normal, então haverá trabalho extra que ninguém documentou ainda.
- **Rollback (jogo online).** Precisa que o jogo dê sempre o mesmo resultado nas duas máquinas. A matemática de ponto flutuante do PS2 não segue o padrão IEEE-754 dos PCs e precisa ser imitada. A do Dreamcast é mais próxima do padrão, mas também tem detalhes próprios. Os dois lados têm solução conhecida.
- **Personagens do NGBC.** O NGBC existe no Atomiswave, no PS2, no Xbox 360 e no PSN japonês. O KOF XI de PS2 já contém 7 personagens adaptados do NGBC, o que mostra que a própria SNK fez esse transplante naquela plataforma. Não há documentação pública dos formatos de dados de nenhum dos dois jogos.
- **Tela widescreen.** Não existe patch widescreen conhecido para KOF XI em nenhuma das duas versões, nem no PCSX2 nem no Flycast. Seria trabalho novo nos dois casos.

---

## 1. Content differences: PS2 vs Atomiswave/Dreamcast

Release history:

- **Arcade (Atomiswave):** JP 2005-10-26, NA December 2005 ([Wikipedia: KOF XI](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI)). MAME's driver records the KOF XI program build date as "Aug 07 2005" ([MAME dc_atomiswave.cpp](https://github.com/mamedev/mame/blob/master/src/mame/sega/dc_atomiswave.cpp)).
- **PS2:** JP 2006-06-22 (SLPS-25660, with a 2007 "SNK Best Collection" reissue SLPS-25789), PAL 2007-07-06 (SLES-54437), NA 2007-11-13 (SLUS-21687), Korea SLKA-25167 ([Wikipedia](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI); [PCSX2 wiki](https://wiki.pcsx2.net/The_King_of_Fighters_XI)).
- **PSN (PS3, PS2 Classics):** JP only, 2014-12-17 (NPJD-00071). This is the PS2 build ([Wikipedia](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI); [PCSX2 wiki](https://wiki.pcsx2.net/The_King_of_Fighters_XI)).
- **Dreamcast:** no official release. There is a 2020 homebrew conversion of the Atomiswave game (see section 2).

What the PS2 adds over the arcade release, per sources:

| Area | Arcade / Dreamcast conversion | PS2 | Source |
|---|---|---|---|
| Base roster | Arcade teams; Wikipedia gives both "40" and "47 playable" without reconciling them | Arcade roster plus the extras below | [Wikipedia](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI) |
| Mid-bosses | Optional mid-bosses: Gai Tendo and Silber (Buriki One), Sho Hayate and Jyazu (Savage Reign); Wikipedia also cites Kizuna Encounter | Present | [SNK Wiki](https://snk.fandom.com/wiki/The_King_of_Fighters_XI), [Wikipedia](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI) |
| Bosses Shion and Magaki | Bosses. Dream Cancel's boss heading reads "Playable on PS2 Only" | Playable after unlock | [Dream Cancel](https://dreamcancel.com/wiki/The_King_of_Fighters_XI) |
| NGBC-derived characters | Not present | 7 characters "based on their Neo Geo Battle Coliseum incarnation", unlocked in Challenge Mode. Wikipedia names Hotaru Futaba, Tung Fu Rue and NESTS-era Kyo. Dream Cancel's roster also lists Geese Howard (called a PS2/PSN "bonus character"), Mr. Big, Shingo Yabuki and Kasumi Todoh; confirm the exact seven in-game | [Wikipedia](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI), [Dream Cancel roster](https://dreamcancel.com/wiki/The_King_of_Fighters_XI), [Dream Cancel: Geese](https://dreamcancel.com/wiki/Geese_Howard_(KOF:XI)) |
| Modes | Arcade tag-team mode; Time Attack/Survival-type unlocks are not documented | Adds classic (non-tag) Team mode, Challenge Mode and Edit Mode (recolours) | [Wikipedia](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI), [StrategyWiki](https://strategywiki.org/wiki/The_King_of_Fighters_XI) |
| Stages | Ruins, Temple, Alley, Ice Festival, Beach, plus boss stages | Adds Shuttle, Esaka, Wheel and Concert ("available only in PS2 version") | [SNK Wiki](https://snk.fandom.com/wiki/The_King_of_Fighters_XI) |
| Special team endings | n/a | Many PS2 "Special Edit Teams" | [SNK Wiki](https://snk.fandom.com/wiki/The_King_of_Fighters_XI) |
| Controls | Arcade tuning | "Multiple changes were made for the port to make the controls more responsive, based on feedback from the arcade" | [Wikipedia (Kakuge interview)](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI) |
| Audio | Arcade soundtrack | Adds a rearranged soundtrack | [Wikipedia](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI) |
| Video | Arcade: higher-resolution backgrounds with 240p-style sprites; 480p or 15 kHz output | Progressive scan in the NTSC-J build only (NA/PAL lack it) | [Nicole Express](https://nicole.express/2021/sega-sammy-atomiswave.html), [PCSX2 wiki](https://wiki.pcsx2.net/The_King_of_Fighters_XI) |

Hidden characters in the arcade build: the Atomiswave game has a "Time Release" operator menu, hidden by a menu-length limit. That menu "instantly unlocks the various characters that are otherwise only available under certain gameplay conditions or after many hundreds of hours of continual operation" ([Sudden Desu](https://sudden-desu.net/entry/king-of-fighters-xi-time-release-menu/)). The same article reports debug strings in memory that it could not explore, because "the game crashes in MAME before gameplay". Which characters sit behind time release is not stated in the sources read.

PS2 port authorship is murky. Wikipedia's infobox credits SNK Playmore, while the body says "The port was mostly done by Ignition and then reused in other regions" ([Wikipedia](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI)).

## 2. Provenance of the Dreamcast version

- **Not official.** "In 2020, a homebrew conversion was released for the Dreamcast" ([Wikipedia](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI)). SEGAbits (2020-11-07) credits megavolt85 and describes the GDI as a Dreamcast-Talk release of about "150mb", probably the compressed download ([SEGAbits](https://segabits.com/?p=67984)). The Dreamcast Junkyard credits megavolt85, later together with yzb ([DCJY 2020-11](https://www.thedreamcastjunkyard.co.uk/2020/11/atomiswave-games-are-being-ported-to.html), [DCJY follow-up](https://www.thedreamcastjunkyard.co.uk/2020/11/lets-play-some-atomiswave-games-on.html)).
- **The whole Atomiswave library was converted, including NGBC.** ConsoleMods says "all dumped Atomiswave games are playable on stock Dreamcast hardware" and lists both King of Fighters XI and NeoGeo Battle Coliseum ([ConsoleMods](https://consolemods.org/wiki/Dreamcast:Atomiswave_Games)). The best images are "TOSEC-style GDIs that use ISO (2048 bytes/sector) data tracks". Burnable CDIs have "notable performance/compatibility issues". That matches the owner's track01.iso / track02.raw / track03.iso / track04.iso layout.
- **Same CPU, same GPU, same sound chip.** Atomiswave has a Hitachi SH-4 at 200 MHz, a PowerVR2 at 100 MHz, a Yamaha AICA (ARM7) for sound, and 16 MB system / 8 MB video / 2 MB sound RAM ([Wikipedia: Atomiswave](https://en.wikipedia.org/wiki/Atomiswave)). MAME's driver header says: "The Atomiswave System is basically just a Sega Dreamcast using ROM carts" ([MAME](https://github.com/mamedev/mame/blob/master/src/mame/sega/dc_atomiswave.cpp)).
- **What the conversion has to change (partly inference).** On Atomiswave, cartridges "are not exposed to the system's buses directly, and data must be copied into RAM" ([Nicole Express](https://nicole.express/2021/sega-sammy-atomiswave.html)). MAME's KOF XI cart listing is one 8 MB flash plus seven 32 MB mask ROMs, about 232 MiB in total ([MAME](https://github.com/mamedev/mame/blob/master/src/mame/sega/dc_atomiswave.cpp)). That is consistent with the owner's ~235 MB track03.iso, but that match is an inference. The Dreamcast has only 16 MB of RAM, so the conversion must replace the cart-to-RAM copy path with GD-ROM reads, and must map the Atomiswave I/O (5-button JAMMA-style controls) onto Maple controllers. The button mapping is hardcoded: Atomiswave button 3 lands on the Dreamcast stick's C button, and Dreamcast Z is "no function" ([Dreamcast-Talk thread](https://www.dreamcast-talk.com/forum/viewtopic.php?p=145248)). The porters have **not published** their patch method in any source found. SEGAbits only quotes a claim that the ports are "very simple and all you had to do was do a few changes".
- **What this means for recompiling.** The game logic is the Atomiswave arcade program running on SH-4, plus a small set of unknown community patches (cart access, I/O, probably the BIOS/boot path). Existing SH-4 recompilers start from a normal Dreamcast boot executable (`1ST_READ.BIN`) built on Sega's Katana SDK ([dream-recomp README](https://github.com/phobos665/dream-recomp)). On a conversion disc that file is probably a loader, and the real program probably sits inside the cart blob. That is unverified and should be checked first (see risks).
- **Known runtime quirks of the conversions:** optical media can bring "slowdowns and other performance issues" ([ConsoleMods](https://consolemods.org/wiki/Dreamcast:Atomiswave_Games)). KOF XI's prematch scenes load slower from CD-R ([Nicole Express](https://nicole.express/2021/sega-sammy-atomiswave.html)). Some loaders needed tuning to stop freezes in NGBC ([DCJY comments](https://www.thedreamcastjunkyard.co.uk/2020/11/lets-play-some-atomiswave-games-on.html)).
- **Legal note (not legal advice):** the conversion contains third-party patches whose authors publish no licence. Recompiling it means building on unlicensed community code as well as SNK's.

## 3. Target hardware and what it means for recompilation effort

| Subsystem | PS2 | Dreamcast conversion (Atomiswave code) |
|---|---|---|
| Main CPU | MIPS R5900 "Emotion Engine" core at ~294.9 MHz, 128-bit MMI SIMD, 16 KB scratchpad ([Copetti](https://www.copetti.org/writings/consoles/playstation-2)) | Hitachi SH-4 at 200 MHz ([Wikipedia: Atomiswave](https://en.wikipedia.org/wiki/Atomiswave)) |
| FPU | Non-IEEE-754: "lacks support for infinity" ([Copetti](https://www.copetti.org/writings/consoles/playstation-2)); VU math saturates instead of producing inf ([PS2Recomp PR #198](https://github.com/ran-j/PS2Recomp/pull/198)) | Close to IEEE, with quirks: games run round-toward-zero, denormals flush under DN=1, FSCA (sin/cos) uses a hardware table, FTRV/FIPR need specific accumulation ([dream-recomp differential-harness doc](https://github.com/phobos665/dream-recomp/blob/main/docs/differential-harness.md)) |
| Vector units | VU0 (macro mode = COP2, or micro mode) and VU1 (micro mode only, feeds display lists to the GS) ([Copetti](https://www.copetti.org/writings/consoles/playstation-2)) | None (geometry is computed on SH-4 with FTRV/FIPR) |
| Graphics | GS: fixed-function rasteriser, 4 MB eDRAM, no T&L, framebuffer merge tricks ([Copetti](https://www.copetti.org/writings/consoles/playstation-2)) | PowerVR2 tile-based renderer fed by Tile Accelerator display lists ([dream-recomp README](https://github.com/phobos665/dream-recomp)) |
| Audio | SPU2: 48 voices on two cores, 2 MB RAM ([Copetti](https://www.copetti.org/writings/consoles/playstation-2)), driven from the IOP | AICA with an ARM7 running the game's own sound driver ([Wikipedia: Atomiswave](https://en.wikipedia.org/wiki/Atomiswave), [dream-recomp](https://github.com/phobos665/dream-recomp)) |
| I/O processor | IOP: R3000-class at 37.5 MHz running IRX modules (pad, CD, sound, memory card) ([Copetti](https://www.copetti.org/writings/consoles/playstation-2)) | None. Maple bus for controllers; GD-ROM (plus whatever the conversion patched in place of cart DMA) |
| Known emulator behaviour | PCSX2 compat 5 ("perfect") on NA/JP; the only listed fix is `limit24BitDepth: 2` for flicker/missing textures, with no EE/VU float gamefixes ([PCSX2 GameIndex](https://github.com/PCSX2/pcsx2/blob/master/bin/resources/GameIndex.yaml)); the wiki notes missing textures on 3D backgrounds ([PCSX2 wiki](https://wiki.pcsx2.net/The_King_of_Fighters_XI)) | Flycast has a dedicated `kofxi` Atomiswave entry with 5-button input mapping ([Flycast naomi_roms.cpp](https://github.com/flyinghead/flycast/blob/master/core/hw/naomi/naomi_roms.cpp)) |

What this means for effort (analysis, drawn from the tooling docs in section 4):

- **CPU translation:** both are mechanical. R5900 has more exotic instructions (MMI, 128-bit registers, COP2 macro mode). SH-4 has delay slots, banked registers, FPSCR mode bits (PR/SZ) that change the meaning of FPU instructions, and store queues. All of these are already handled by at least one tool on each side.
- **Graphics:** this is the biggest gap. On PS2 the game's VU1 microprograms must be interpreted or translated, and GS behaviour emulated. PS2Recomp says "Performance is very bad for VU and GS" ([PS2Recomp README](https://github.com/ran-j/PS2Recomp)). On Dreamcast, PowerVR2 display lists are decoded and drawn through Vulkan in dream-recomp. Its renderer works well enough to play Crazy Taxi ([dream-recomp](https://github.com/phobos665/dream-recomp)). dcrecomp's OpenGL renderer is "Basic" ([dcrecomp](https://github.com/sp00nznet/dcrecomp)).
- **Audio:** PS2 needs IOP IRX modules plus SPU2. PS2Recomp executes original IRX modules with HLE fallbacks and has `ps2_audio` / VAG code. Dreamcast needs ARM7 plus the AICA mixer. dream-recomp emulates both. dcrecomp's AICA is a stub. chuchu's ARM7 is interpreted but its mixer is missing ([chuchu](https://github.com/sp00nznet/chuchu)).
- **I/O and disc:** PS2 goes through IOP CD/pad modules. The Dreamcast conversion goes through unknown community patches over GD-ROM and Maple. A third path is possible: recompile the Atomiswave program directly from the cart image and write a native "cart read" plus Atomiswave I/O layer. No existing tool does this.

## 4. Static-recompilation tooling

### PS2 (R5900)

| Tool | Licence | Last activity | Maturity / shipped games |
|---|---|---|---|
| [PS2Recomp](https://github.com/ran-j/PS2Recomp) (ran-j) | GPL-3.0 | Commit 2026-10-22 (FPU float emulation landed 2026-10-14) | README title says "Experimental"; ~3.3k stars. Modules: ps2xAnalyzer (Ghidra workflow for stripped games), ps2xRecomp (R5900 + MMI + VU0 macro to C++), ps2xRuntime (memory, syscalls, GS CPU backend, VU1 interpreter, audio, pad), ps2xIOP (runs original IRX). Limits: "Performance is very bad for VU and GS"; "many paths are stubbed". [recomp.fyi](https://recomp.fyi/toolchain/ps2) lists 81 PS2Recomp projects, with **Released**: Battle Stadium D.O.N, Rampage: Total Destruction, The Sims 2; **Playable**: DBZ Budokai 2, DBZ Infinite World, Dynasty Warriors 5 XL, God Hand, Urban Reign. Fighting-game projects include Urban Reign (playable), Ultraman FE3 and Soulcalibur III (in progress or unclaimed) |

recomp.fyi's toolchain index lists PS2Recomp as the only PS2 recompiler ([recomp.fyi toolchains](https://recomp.fyi/toolchains)). Press coverage, Time Extension (January 2026), still called it "in its early days" ([Time Extension](https://www.timeextension.com/news/2026/01/native-pc-ports-of-ps2-games-could-be-on-the-way-thanks-to-new-recompilation-experiment)).

### Dreamcast / SH-4

None of these tools mentions Atomiswave.

| Tool | Licence | Last activity | Maturity / shipped games |
|---|---|---|---|
| [dream-recomp](https://github.com/phobos665/dream-recomp) (phobos665) | GPL-2.0 | 2026-10-29 | CPU compiled to C++. Low-level PowerVR2 via Vulkan, ARM7+AICA emulated, BIOS/GD-ROM replaced by HLE. Has a differential harness against Flycast. Crazy Taxi "plays"; Rez playable to Area 1; others boot. "No title is complete enough to build without" the fallback interpreter. Static discovery finds about 79–90% of code. A fork of its approach is used by [Bomberman Online Recomp](https://github.com/nvd123-YT/BombermanOnlineRecomp) (listed "Released" on [recomp.fyi](https://recomp.fyi/?q=dreamcast)) and Draconus (in progress) |
| [dcrecomp](https://github.com/sp00nznet/dcrecomp) (sp00nznet) | GPL-2.0 (MIT until 2026-10-20) | 2026-10-20 | Alpha with no release. Targets Dreamcast **and NAOMI** (JVS, M4 decryption). SH-4 integer/FPU/MMU/store queues "Full"; OpenGL renderer "Basic"; AICA stub. Crazy Taxi links; Mushiking (NAOMI) runs |
| [DreamcastRecompiled](https://github.com/Duw0ng/DreamcastRecompiled) (Duw0ng) | MIT | 2026-10-18 | D3D11 and Windows only. Self-reports ChuChu Rocket! fully working and three titles to the menus; described as having no oracle-based testing ([dream-recomp review](https://github.com/phobos665/dream-recomp/blob/main/docs/dreamcastrecompiled-review.md)) |
| [Street Alpha 3 Dreamcast Recomp](https://github.com/irnutsmurt/Street-Alpha-3-Dreamcast-Recomp) (custom tool in `tools/recomp/`) | GPL-3.0-or-later | 2026-10-29 | **Playable** 2D fighter on Windows/Linux. Recompiles the main executable plus 111 per-character overlays; Vulkan renderer; delay-based UDP netplay, not rollback. "Built 100% with AI". The closest precedent to KOF XI |
| KatanaRecomp (sonicfreak1337) | unknown | unknown | Called "further along" by the chuchu README, but the repository was not publicly reachable on 2026-11-11 |

## 5. Existing reverse-engineering knowledge for KOF XI and SNK's Atomiswave-era games

Little public reverse-engineering work exists for KOF XI or NGBC:

- No decompilation, symbol map or recomp project for KOF XI, NGBC or any SNK Atomiswave title appears on recomp.fyi's PS2 or Dreamcast listings ([recomp.fyi PS2](https://recomp.fyi/toolchain/ps2), [recomp.fyi Dreamcast search](https://recomp.fyi/?q=dreamcast)).
- **Arcade:** the Sudden Desu "Time Release" write-up (operator menu and debug strings, explored through MAME cheats) ([Sudden Desu](https://sudden-desu.net/entry/king-of-fighters-xi-time-release-menu/)). MAME's driver documents the cart layout and board ([MAME](https://github.com/mamedev/mame/blob/master/src/mame/sega/dc_atomiswave.cpp)). Flycast's `kofxi`/`ngbc` entries define inputs ([Flycast](https://github.com/flyinghead/flycast/blob/master/core/hw/naomi/naomi_roms.cpp)).
- **PS2:** PCSX2 metadata only (serials, CRCs NA `581A4DAA` and JP `E4BB51C1`, the GS fix) ([PCSX2 wiki](https://wiki.pcsx2.net/The_King_of_Fighters_XI), [GameIndex](https://github.com/PCSX2/pcsx2/blob/master/bin/resources/GameIndex.yaml)). There are no KOF XI entries in the [pcsx2_patches](https://github.com/PCSX2/pcsx2_patches) repository (checked 2026-11-11), so no widescreen or 60 fps patches.
- **Sprite/data tools:** none found for KOF XI or NGBC on GitHub searches. Frame data and system mechanics are documented on [Dream Cancel](https://dreamcancel.com/wiki/The_King_of_Fighters_XI), useful later as a behavioural oracle.
- **Shared engine with NGBC:** no source documents a shared engine or data format. The circumstantial evidence: both are 2005 SNK Playmore Atomiswave fighters on the same board, and the PS2 KOF XI ships seven characters rebuilt from their NGBC versions ([Wikipedia](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI)). Dream Cancel notes PS2 Geese's look is "mostly based on" NGBC but his moveset was reworked ([Dream Cancel: Geese](https://dreamcancel.com/wiki/Geese_Howard_(KOF:XI))). That is consistent with a manual port, not a drop-in format.
- Not read: The Cutting Room Floor pages for KOF XI and NGBC (blocked to automated fetch), Hardcore Gaming 101 (site migration), Sega Retro and SRK wiki (bot protection). These may hold more unused-content or version notes and are worth a manual read.

## 6. Considerations for future goals (inputs, not the decision)

**Rollback netplay (determinism)**
- PS2: the EE FPU and VUs are non-IEEE (no infinity; saturation instead) ([Copetti](https://www.copetti.org/writings/consoles/playstation-2), [PS2Recomp PR #198](https://github.com/ran-j/PS2Recomp/pull/198)). PS2Recomp emulates PS2 float semantics for EE FPU results and DIV/RSQRT (commit 2026-10-14). The PR itself lists open gaps: "The denormal band is host-dependent", a max-float stand-in that is "a factor of two low", and a known divergence between the VU1 interpreter and VU0 macro paths. For rollback, both peers must run the same build on the same host float configuration.
- Dreamcast: SH-4 float is IEEE-like, but bit-exact play needs round-toward-zero on the host, a hardware FSCA table, and specific FTRV/FIPR accumulation. dream-recomp found and fixed each of these against Flycast, and runs a "cross-ISA determinism check" ([dream-recomp harness doc](https://github.com/phobos665/dream-recomp/blob/main/docs/differential-harness.md)).
- Prior art: the Atomiswave KOF XI is played online with "Rollback Flycast GGPO" ([Dream Cancel](https://dreamcancel.com/wiki/The_King_of_Fighters_XI)). Flycast ships a GGPO implementation built on whole-machine savestates (`core/network/ggpo.cpp`, GPL-2.0) ([Flycast](https://github.com/flyinghead/flycast)). Flycast Dojo is the Fightcade fork ([flycast-dojo](https://github.com/blueminder/flycast-dojo)). This proves the arcade code is deterministic enough for rollback under emulation. No equivalent PS2 rollback deployment of KOF XI was found.
- State size for rollback snapshots (analysis): Dreamcast/Atomiswave is about 26 MB (16 + 8 + 2). PS2 is larger: 32 MB EE RAM, 4 MB GS, 2 MB IOP and 2 MB SPU2, plus VU memories. A native port would ideally snapshot only game state, which needs RE of the game's state structures on either base.

**Porting NGBC fighters into KOF XI**
- NGBC platforms: Atomiswave (2005), PS2 (JP 2005-12-22, PAL 2006, NA 2007), Xbox Live Arcade (2010-06-09), PSN JP (2015-02-18) ([Wikipedia: NGBC](https://en.wikipedia.org/wiki/Neo_Geo_Battle_Coliseum)). It also has a homebrew Dreamcast conversion ([ConsoleMods](https://consolemods.org/wiki/Dreamcast:Atomiswave_Games)). The Xbox 360 build would be reachable with [XenonRecomp](https://github.com/hedge-dev/XenonRecomp) (MIT, no runtime provided).
- Same-platform pairing is available either way: AW/DC KOF XI with AW/DC NGBC, or PS2 KOF XI with PS2 NGBC.
- PS2 KOF XI already contains seven NGBC-derived characters, which proves SNK moved NGBC characters into the KOF XI engine on that platform. Whether the data formats match is undocumented on both platforms.

**Unlocking hidden characters**
- Arcade/DC: characters are gated by time-release and operator settings, and the menu code still exists ([Sudden Desu](https://sudden-desu.net/entry/king-of-fighters-xi-time-release-menu/)). Bosses are not playable in arcade per Dream Cancel's heading.
- PS2: bosses and the seven NGBC characters unlock through Challenge Mode ([StrategyWiki](https://strategywiki.org/wiki/The_King_of_Fighters_XI)). A native port could expose them with a save-flag change. They are not "hidden data" but shipped content.

**Widescreen**
- No existing patch on either side: no KOF XI in Flycast's widescreen cheat tables ([Flycast cheats.cpp](https://github.com/flyinghead/flycast/blob/master/core/cheats.cpp)) and no KOF XI file in pcsx2_patches.
- Analysis: a 2D fighter needs camera, stage-boundary and background-art changes, not just a projection tweak. The PS2's extra stages and the arcade's high-res backgrounds would both need checking for art beyond 4:3.

## 7. Neutral comparison table

| Criterion | PS2 base | Dreamcast conversion base (Atomiswave code) |
|---|---|---|
| Official release | Yes | No (2020 homebrew conversion of the arcade release) |
| Content | Superset: bosses playable, 7 NGBC-derived characters, Challenge/Edit/Team modes, 4 extra stages, arranged soundtrack, control tweaks | Arcade original; hidden characters behind time-release; no PS2 extras |
| Competitive-community version | Secondary | The version played online (Flycast GGPO) |
| CPU | R5900 (MIPS + MMI) + VU0/VU1 | SH-4 only |
| Graphics effort | High: VU1 microcode + GS emulation; PS2Recomp says perf "very bad" | Moderate: PowerVR2 display lists; Vulkan renderer exists in dream-recomp |
| Audio effort | IOP IRX + SPU2 (PS2Recomp runs IRX) | ARM7 + AICA (emulated in dream-recomp) |
| Mature tool | PS2Recomp: one dominant tool, 81 listed projects, 3 released, 5 playable | Several young tools; 1 released, 2 playable (one a 2D fighter); none support Atomiswave or conversion discs |
| Tool licence | GPL-3.0 | GPL-2.0 (dream-recomp, dcrecomp), MIT (DreamcastRecompiled), GPL-3.0+ (SFA3 tool) |
| Float determinism | Non-IEEE; emulation work in progress | IEEE-like with known, solved quirks |
| Rollback prior art | None found for KOF XI | Flycast GGPO with KOF XI |
| Input image | Retail disc, standard ELF | Community-patched image; program likely inside a ~232 MiB cart blob |
| Region variants | NTSC-J (progressive, original), NA, PAL, KR | Single arcade build plus conversion patches |
| Widescreen prior art | None | None |
| Licence impact on MIT repo (analysis) | Linking PS2Recomp's GPL-3.0 runtime would make distributed binaries GPL-3.0 | Linking a GPL-2.0 runtime (dream-recomp/dcrecomp) makes binaries GPL-2.0; DreamcastRecompiled is MIT |

### Main open risks: PS2

1. VU1 and GS performance and accuracy in PS2Recomp are the weakest areas, and graphics are what a fighting game shows every frame.
2. The non-IEEE float emulation is new (October 2026) and has documented open gaps. That matters for rollback.
3. More subsystems to bring up (EE, VU0, VU1, GS, IOP, SPU2) before a single fight runs.
4. The NA/PAL builds lack progressive scan and were reportedly derived from the PAL build. Which region to recompile is a sub-decision.
5. Whether the ELF has symbols or overlays is not documented anywhere public. Check it on the owner's disc without publishing anything.

### Main open risks: Dreamcast conversion

1. The conversion's patch method is undocumented. Where the real program lives (loader in `1ST_READ.BIN`, program in the cart blob) must be confirmed before any tool choice.
2. No SH-4 recompiler supports Atomiswave or cart-style loading. That layer must be written.
3. It inherits unlicensed third-party patches and a hardcoded button map. Recompiling from the cart program directly would avoid this but needs a separate legal dump of the arcade cart, which the owner does not have.
4. The PS2-only content (bosses, NGBC characters, modes, stages) is absent and would have to be rebuilt or imported.
5. The SH-4 tools are all under a few months old, and the most mature (dream-recomp) still needs its fallback interpreter for every title.

### Suggested low-cost checks before deciding (no data leaves the machine)

- On the Dreamcast image, list the file table of track03 and identify `1ST_READ.BIN`'s size. A small file next to a single huge file would confirm the loader-plus-cart-blob layout.
- On the PS2 disc, check whether `SLUS_216.87` (or the region equivalent) carries a symbol table, and whether there are overlay or IRX files beside it.

## Notes on method

- Primary sources preferred: tool repositories (READMEs, docs, licences, commit dates read via shallow `git clone` on 2026-11-11), the MAME and Flycast sources, and the PCSX2 GameIndex. Community wikis and press are used for content and history.
- One fetched page (nicole.express) contained embedded text asking the reader to edit an instruction file. It was ignored as untrusted content.
- KatanaRecomp, TCRF, HG101, Sega Retro and the SRK wiki could not be read.

## Sources

- [The King of Fighters XI (Wikipedia)](https://en.wikipedia.org/wiki/The_King_of_Fighters_XI)
- [Neo Geo Battle Coliseum (Wikipedia)](https://en.wikipedia.org/wiki/Neo_Geo_Battle_Coliseum)
- [Atomiswave (Wikipedia)](https://en.wikipedia.org/wiki/Atomiswave)
- [The King of Fighters XI (SNK Wiki)](https://snk.fandom.com/wiki/The_King_of_Fighters_XI)
- [The King of Fighters XI (Dream Cancel Wiki)](https://dreamcancel.com/wiki/The_King_of_Fighters_XI)
- [Geese Howard (KOF:XI) (Dream Cancel Wiki)](https://dreamcancel.com/wiki/Geese_Howard_(KOF:XI))
- [NeoGeo Battle Coliseum (Dream Cancel Wiki)](https://dreamcancel.com/wiki/NeoGeo_Battle_Coliseum)
- [The King of Fighters XI (StrategyWiki)](https://strategywiki.org/wiki/The_King_of_Fighters_XI)
- [The King of Fighters XI (PCSX2 Wiki)](https://wiki.pcsx2.net/The_King_of_Fighters_XI)
- [PCSX2 GameIndex.yaml](https://github.com/PCSX2/pcsx2/blob/master/bin/resources/GameIndex.yaml)
- [PCSX2 patches repository](https://github.com/PCSX2/pcsx2_patches)
- [King of Fighters XI Time Release menu (Sudden Desu)](https://sudden-desu.net/entry/king-of-fighters-xi-time-release-menu/)
- [King of Fighters XI Arcade Ported to SEGA Dreamcast (SEGAbits)](https://segabits.com/?p=67984)
- [Atomiswave games are being ported to Dreamcast (The Dreamcast Junkyard)](https://www.thedreamcastjunkyard.co.uk/2020/11/atomiswave-games-are-being-ported-to.html)
- [Let's play some Atomiswave games on Dreamcast (The Dreamcast Junkyard)](https://www.thedreamcastjunkyard.co.uk/2020/11/lets-play-some-atomiswave-games-on.html)
- [Dreamcast: Atomiswave Games (ConsoleMods Wiki)](https://consolemods.org/wiki/Dreamcast:Atomiswave_Games)
- [Issue with Atomiswave fighting game conversions on DC Arcade Stick (Dreamcast-Talk)](https://www.dreamcast-talk.com/forum/viewtopic.php?p=145248)
- [Sega Sammy Atomiswave (Nicole Express)](https://nicole.express/2021/sega-sammy-atomiswave.html)
- [MAME dc_atomiswave.cpp](https://github.com/mamedev/mame/blob/master/src/mame/sega/dc_atomiswave.cpp)
- [Flycast](https://github.com/flyinghead/flycast)
- [Flycast naomi_roms.cpp](https://github.com/flyinghead/flycast/blob/master/core/hw/naomi/naomi_roms.cpp)
- [Flycast cheats.cpp](https://github.com/flyinghead/flycast/blob/master/core/cheats.cpp)
- [Flycast Dojo](https://github.com/blueminder/flycast-dojo)
- [PlayStation 2 Architecture (Rodrigo Copetti)](https://www.copetti.org/writings/consoles/playstation-2)
- [PS2Recomp (ran-j)](https://github.com/ran-j/PS2Recomp)
- [PS2Recomp PR #198: PS2 float semantics](https://github.com/ran-j/PS2Recomp/pull/198)
- [Native PC ports of PS2 games could be on the way (Time Extension)](https://www.timeextension.com/news/2026/01/native-pc-ports-of-ps2-games-could-be-on-the-way-thanks-to-new-recompilation-experiment)
- [recomp.fyi project index](https://recomp.fyi)
- [recomp.fyi toolchains](https://recomp.fyi/toolchains)
- [recomp.fyi PS2 toolchain page](https://recomp.fyi/toolchain/ps2)
- [recomp.fyi Dreamcast search](https://recomp.fyi/?q=dreamcast)
- [dream-recomp (phobos665)](https://github.com/phobos665/dream-recomp)
- [dream-recomp differential harness doc](https://github.com/phobos665/dream-recomp/blob/main/docs/differential-harness.md)
- [dream-recomp review of DreamcastRecompiled](https://github.com/phobos665/dream-recomp/blob/main/docs/dreamcastrecompiled-review.md)
- [dcrecomp (sp00nznet)](https://github.com/sp00nznet/dcrecomp)
- [chuchu (sp00nznet)](https://github.com/sp00nznet/chuchu)
- [DreamcastRecompiled (Duw0ng)](https://github.com/Duw0ng/DreamcastRecompiled)
- [Street Alpha 3 Dreamcast Recomp (irnutsmurt)](https://github.com/irnutsmurt/Street-Alpha-3-Dreamcast-Recomp)
- [Bomberman Online Recomp (nvd123-YT)](https://github.com/nvd123-YT/BombermanOnlineRecomp)
- [XenonRecomp (hedge-dev)](https://github.com/hedge-dev/XenonRecomp)
- [We're finally getting a NAOMI port for Dreamcast (Time Extension)](https://www.timeextension.com/news/2026/07/were-finally-getting-a-naomi-port-for-dreamcast-but-the-monkeys-paw-curls)
