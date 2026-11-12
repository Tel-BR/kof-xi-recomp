---
label: wayfinder:map
title: "Map: from disc to a playable fight / Do disco a uma luta jogável"
status: open
---

# Map: from disc to a playable fight

_Mapa: do disco a uma luta jogável. Cada seção traz o inglês primeiro e o português logo depois._

Tickets live in [`tickets/`](./tickets/), one file per ticket; research findings live in [`research/`](./research/). See "Local wayfinding" in `docs/agents/issue-tracker.md` for how to query the frontier, claim, and resolve.

## Destination

A decided, written plan for a native Windows build of KOF XI that plays **one Complete Fight** (two local players, with graphics, sound, music and controller input) from a **User-supplied Disc**, built on an architecture that is **ready for rollback netplay** (the whole game state can be saved and restored every frame, and the simulation is deterministic). The map is done when nothing is left to decide before building starts.

_PT-BR: um plano decidido e escrito para um build nativo de Windows do KOF XI que joga **uma luta completa** (dois jogadores no mesmo PC, com gráfico, som, música e controle) a partir do **disco do próprio usuário**, sobre uma arquitetura **pronta para netplay com rollback** (o estado inteiro do jogo pode ser salvo e restaurado a cada quadro, e a simulação é determinística). O mapa termina quando não sobrar nada a decidir antes de começar a construir._

## Notes

- **Decider:** the repo owner (Tel-BR) answers every HITL ticket; collaborators comment. The owner is not a systems programmer: every option must be presented with its causes and consequences in plain language, and questions use the interactive question tool.
- **Skills:** grilling tickets call `grilling` + `domain-modeling`; research tickets call `research`. Use the vocabulary in [`GLOSSARY.md`](../../../GLOSSARY.md).
- **Hard rule:** no game data anywhere: not in tickets, research notes or commits (see `AGENTS.md`). Disc hashes are fine; disassembly and assets are not.
- **Language:** ticket titles in English; bodies bilingual (English, then Brazilian Portuguese).
- **Platform:** Windows first, using cross-platform libraries so Linux/Mac stay possible later at no cost now.
- **Licence:** currently MIT. The owner is willing to relicense to GPL if reusing emulator code pays off (see the relicensing ticket).
- **Planning only:** this map produces decisions, not code.

_PT-BR: o dono do repositório (Tel-BR) responde todos os tickets de conversa; colaboradores comentam. Cada opção vem com causas e consequências em linguagem simples, e as perguntas usam a ferramenta interativa. Nada dos jogos em lugar nenhum (hashes de disco podem). Títulos em inglês, corpo bilíngue. Windows primeiro, com bibliotecas multiplataforma. Licença MIT hoje, aceitando GPL se reaproveitar código de emulador compensar. Este mapa produz decisões, não código._

## Decisions so far

<!-- one line per closed ticket: [title](tickets/NN-slug.md): one-line gist -->

- [Identify the exact disc dumps](tickets/04-identify-disc-dumps.md): PS2 is SLUS-21687 v1.00 but does not match Redump's verified image (executable does); arcade cartridge matches MAME `kofxi` exactly, BIOS not included; Dreamcast is megavolt85's 2020 conversion, no database.
- [Compare PS2 and Dreamcast as the base version](tickets/01-compare-base-versions.md): PS2 has more content (bosses, 7 NGBC-derived fighters, extra modes and stages) but far more hardware to rebuild and one experimental GPL-3.0 recompiler; the arcade code is simpler hardware with young SH-4 tools and proven rollback in Flycast.
- [Survey graphics and audio reimplementation options and their licenses](tickets/02-graphics-audio-options.md): PS2 needs GS + VU1 microprograms + IOP/SPU2; arcade needs a PowerVR2 display-list renderer + AICA/ARM7 (done before by the SFA3 recomp); the most mature reusable parts are GPL, permissive ones exist but are less mature.
- [Survey how static recomps can support rollback netplay](tickets/03-rollback-on-static-recomp.md): needs save/load/advance plus determinism; snapshot at one fixed frame point and copy only changed pages; pin floating point and keep host time out; permissive libraries (GekkoNet, GGPO); 12 early architecture requirements listed.
- [Inspect the code structure of each candidate release](tickets/08-inspect-code-structure.md): no symbols anywhere; PS2 is one 2 MB CodeWarrior ELF with no overlays; the arcade cart is encrypted (MAME's BSD-3 cipher decrypts it) and holds a 1.19 MB SH-4 program; the Dreamcast disc is that same program with 754 bytes patched plus the cart data byte-identical.
- [Compare both releases hands-on in emulators](tickets/10-hands-on-comparison.md): owner prefers the PS2 Release (more responsive controls; all PS2-only content is a must for the final port) but discards neither; decisive criteria are excellent performance with the NGBC fighters and rollback netplay; first build needs only the fight itself.
- [Assess carrying content across releases](tickets/09-carry-content-across-releases.md): content flows one way (the PS2 has all the arcade content, reportedly even its balance with Arrange off); the arcade's strengths are technical and cannot be carried; rebuilding the PS2 content on the arcade code is large (modes rewritten, fighters and stages need undocumented formats and converters).

## Not yet specified

- **Recompiler:** adopt an existing static recompiler for the chosen CPU, extend one, or build our own; how functions and code boundaries are discovered (no release has symbols; the PS2 program is CodeWarrior-built, the arcade program is a raw SH-4 image).
- **Host runtime:** language and core libraries for the native side (windowing, input, timing, file access).
- **Graphics, audio and input:** the concrete approach for each once the base version and licence are settled. Sizing questions still open: how many VU1 microprograms the PS2 build uploads; whether the arcade build uses AICA DSP effects and PowerVR2 modifier volumes.
- **Reading the disc:** whether the port reads the User-supplied Disc at runtime or extracts it once at setup, and how the disc is validated. For the arcade code this includes decrypting the user's cart dump (MAME's cipher is BSD-3) and replacing the cart file-read interface.
- **Rollback-ready runtime contract:** which of the 12 early requirements in the rollback findings become binding, and how snapshots meet the frame boundary, once the recompiler and runtime are known.
- **Determinism details** for the chosen CPU (floating-point behaviour, compiler flags, sources of non-determinism).
- **Build system and repository layout.**
- **Contributor setup:** how a collaborator goes from a clean checkout plus their own disc to a running build.

_PT-BR: recompilador (usar um existente, estender ou construir; nenhuma versão tem símbolos); runtime nativo (linguagem e bibliotecas); gráfico, som e entrada (falta medir quantos microprogramas de VU1 o PS2 usa, e se o arcade usa efeitos de DSP do AICA e volumes modificadores do PowerVR2); leitura do disco (em tempo de execução ou extração inicial, e validação; no arcade, inclui descriptografar o dump do cartucho); contrato do runtime pronto para rollback (quais dos 12 requisitos viram regra); detalhes de determinismo; sistema de build e organização do repo; como um colaborador monta o ambiente com o próprio disco._

## Out of scope

Ruled beyond this map's destination; each may become its own future map. / _Fora do destino deste mapa; cada item pode virar um mapa futuro._

- Online netplay implementation (only the rollback-ready architecture is in scope) / _netplay online implementado_
- High resolution and widescreen / _alta resolução e widescreen_
- Modern controls and menus / _controles e menus modernos_
- Playable Hidden Characters and New Characters / _personagens ocultos jogáveis e personagens novos_
- Color edit, missions, practice mode, frame data display / _color edit, missões, modo treino, frame data_
- Porting Neo Geo Battle Coliseum fighters, including documenting how SNK adapted NGBC fighters for the PS2 Release (groundwork for that future map; study the NGBC release that matches the chosen Base Version) / _lutadores do NGBC, incluindo documentar como a SNK adaptou os lutadores do NGBC para a versão de PS2 (base para esse mapa futuro; estudar o NGBC da mesma plataforma da versão-base)_
- Linux and macOS builds / _builds para Linux e Mac_
- Arcade mode and every other mode beyond one Complete Fight / _modo arcade e outros modos além de uma luta completa_
