---
id: 07
title: Decide how correctness is verified against a reference emulator
type: grilling
status: closed
assignee: Tel-BR
blocked_by: [05]
research: ../research/reference-emulator-capabilities.md
---

## Question

How will contributors check that the port behaves like the original? Choose the Reference Emulator for the chosen Base Version, what gets compared (frames, audio, RAM and CPU state at given frames, input replays), and how often, so collaborators and agents can validate work without the owner playing every build.

_PT-BR: como os colaboradores vão conferir que o port se comporta como o original? Escolher o emulador de referência, o que comparar (imagens, áudio, estado da memória, replays de entrada) e com que frequência, para validar sem depender de o dono jogar cada build._

## Resolution

Decided with the owner on 2026-11-15. Capabilities and limits of the emulator: [reference-emulator-capabilities.md](../research/reference-emulator-capabilities.md).

- **Reference Emulator:** PCSX2, always the latest release (the owner's choice over pinning 2.8.2). Adopting a new release follows a drift check: run the existing suite on the new version first; identical hashes mean adopt it, different hashes mean investigate who is right (new emulator or old reference) before regenerating. Every Reference Table records the PCSX2 version and the BIOS used.
- **What goes in git:** scripts, button-only replays and Reference Tables (hashes, no game bytes). Memory dumps, images and audio stay in `private/`. Each collaborator brings their own disc (and, to regenerate references, their own BIOS).
- **Reference Scenarios (the owner records each once, in PCSX2's menu):** (1) menu to a short fight on a regular 2D stage; (2) a fight on one extra 3D stage; (3) a PS2-exclusive fighter with a Leader special; (4) one Complete Fight to the result screen. Same coverage as [Measure the PS2 Release's VU1 and GS usage](14-measure-vu1-gs-usage.md).
- **What is compared:** (a) game state in memory at marked frames and (b) the command stream sent to the GS per frame, both automatic; (c) audio is a goal, but how to compare it is open (human listening is the fallback); (d) side-by-side screenshots are visual aid only, never part of the suite.
- **"Game state" means only the memory areas that belong to the game;** BIOS/kernel areas are excluded. Noise is found by playing the same replay twice in PCSX2 and diffing the results.
- **Frequency:** a quick suite (a few hundred frames) on every change to the runtime, the full suite (one Complete Fight) at each milestone, always run locally; no cloud CI, because it cannot hold the owner's disc.
- **Open points turned into tickets:** [Prototype the reference capture on one scenario](19-prototype-reference-capture.md), [Survey how to compare audio against the Reference Emulator](20-audio-comparison.md), [Decide which memory regions count as game state](21-game-state-regions.md).

_PT-BR: decidido com o dono em 15/11/2026. Emulador de referência: PCSX2, sempre o release mais novo; ao atualizar, rodamos antes a suíte antiga na versão nova (hashes iguais = adota; diferentes = investigar antes de regravar), e toda tabela anota a versão do PCSX2 e o BIOS. No git entram scripts, replays de botões e tabelas de hash; dumps, imagens e áudio ficam em `private/`. O dono grava uma vez quatro cenários (luta curta numa fase 2D, fase 3D extra, lutador exclusivo do PS2 com especial de líder, Luta completa). Confere-se o estado do jogo na memória e os comandos de desenho ao GS (automáticos); áudio é meta com método em aberto (audição humana como plano B); prints lado a lado só como apoio. "Estado do jogo" são só as áreas de memória do jogo, sem BIOS/kernel; o ruído se acha rodando o mesmo replay duas vezes. Suíte rápida a cada mudança no runtime e completa a cada marco, sempre local, sem CI na nuvem. Pontos em aberto viraram os tickets 19, 20 e 21._
