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

## Not yet specified

- **Recompiler:** adopt an existing static recompiler for the chosen CPU, extend one, or build our own; how functions and code boundaries are discovered.
- **Host runtime:** language and core libraries for the native side (windowing, input, timing, file access).
- **Graphics, audio and input:** the concrete approach for each once the base version and licence are settled.
- **Reading the disc:** whether the port reads the User-supplied Disc at runtime or extracts it once at setup, and how the disc is validated.
- **Determinism details** for the chosen CPU (floating-point behaviour, compiler flags, sources of non-determinism).
- **Build system and repository layout.**
- **Contributor setup:** how a collaborator goes from a clean checkout plus their own disc to a running build.

_PT-BR: recompilador (usar um existente, estender ou construir); runtime nativo (linguagem e bibliotecas); gráfico, som e entrada; leitura do disco (em tempo de execução ou extração inicial, e validação); detalhes de determinismo; sistema de build e organização do repo; como um colaborador monta o ambiente com o próprio disco._

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
