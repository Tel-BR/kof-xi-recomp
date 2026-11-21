---
id: 06
title: Decide whether to relicense to GPL
type: grilling
status: closed
assignee: Tel-BR
blocked_by: [02, 05, 15]
---

## Question

For the chosen Base Version, does reusing GPL emulator code (graphics, audio or other components) save enough work to justify relicensing the project from MIT to GPL? If yes, which GPL version, and what changes for contributors and users?

_PT-BR: para a versão escolhida, reaproveitar código GPL de emuladores economiza trabalho suficiente para justificar trocar a licença de MIT para GPL? Se sim, qual versão da GPL, e o que muda para colaboradores e usuários?_

## Notes

- 2026-11-12, from [Choose the base version](05-choose-base-version.md): the Base Version is the PS2 Release, so this ticket now also waits for [Decide the recompiler](15-decide-recompiler.md). If that ticket adopts PS2Recomp, GPL-3.0 follows from it, and this ticket only confirms the version and records what changes for contributors and users.

  _PT-BR: a versão-base é o PS2, então este ticket agora espera também o ticket 15. Se o 15 adotar o PS2Recomp, a GPL-3.0 vem junto, e aqui só se confirma a versão e o que muda para colaboradores e usuários._

## Resolution

Decided on 2026-11-21 by the repo owner (Tel-BR).

**Relicense the project to GNU General Public License v3.0 (GPL-3.0).**

### Rationale

1. **Mandated by the Recompiler Decision:** [Decide the recompiler](15-decide-recompiler.md) decided to build the port on a fork of `ran-j/PS2Recomp`, which is licensed under GPL-3.0. Distributing the recompiled port linked against PS2Recomp's runtime legally requires the entire combined work to be GPL-3.0.
2. **Reusing Proven Emulator Components:** Reusing GPL-licensed components from the PS2 emulation ecosystem (such as mature GS rendering pipelines, SPU2 audio processing, and IOP emulation logic from PCSX2/PS2Recomp) saves months or years of redundant engineering. Permissive alternatives either do not exist or are immature for the Emotion Engine and GS.
3. **No Trade-off Disadvantage:** Because this is an open-source non-commercial fan recreation where users supply their own disc images, copyleft licensing perfectly matches the project goals: keeping all code open and community-owned.

### What Changes for Contributors and Users

- **For Contributors:**
  - All source code contributions to the repository will be licensed under GPL-3.0.
  - Permissively licensed third-party code (MIT, BSD, Apache 2.0, zlib/libpng) may still be incorporated, but proprietary closed-source contributions cannot.
  - Forks and derivative distributions must keep the source code public under GPL-3.0.
- **For Users:**
  - Full rights under the GPL-3.0 to inspect, modify, compile, and distribute the port source code.
  - The project still adheres strictly to the hard rule: no game data, disc images, or copyrighted assets are distributed. Users supply their own discs locally.

---

_PT-BR: decidido em 21/11/2026 pelo dono do repositório (Tel-BR)._

_**Trocar a licença do projeto para GNU General Public License v3.0 (GPL-3.0).**_

_Motivação:_
1. _**Consequência direta da escolha do recompilador:** o ticket 15 ([Decidir o recompilador](15-decide-recompiler.md)) decidiu construir o projeto sobre um fork do `ran-j/PS2Recomp`, licenciado sob GPL-3.0. Distribuir o port com o runtime do PS2Recomp exige legalmente que a obra combinada seja GPL-3.0._
2. _**Reaproveitamento de componentes maduros de emulação:** poder reaproveitar componentes sob GPL do ecossistema de PS2 (como o pipeline do GS, áudio SPU2 e IOP do PCSX2/PS2Recomp) economiza meses ou anos de desenvolvimento redundante. Não existem alternativas permissivas maduras para a arquitetura de Emotion Engine e GS._
3. _**Alinhamento de objetivos:** por ser um projeto aberto e não comercial onde cada usuário fornece sua própria cópia do disco, a licença copyleft garante que o código permaneça sempre livre, aberto e compartilhado pela comunidade._

_O que muda para colaboradores e usuários:_
- _**Para colaboradores:** contribuições ao repositório passam a ser licenciadas sob GPL-3.0. Bibliotecas permissivas (MIT, BSD, Apache 2.0) continuam compatíveis e utilizáveis, mas código proprietário fechado não é permitido. Qualquer fork distribuído deve disponibilizar o código-fonte sob GPL-3.0._
- _**Para usuários:** garantia das quatro liberdades essenciais da GPL-3.0 (estudar, modificar, executar e redistribuir o código). A regra obrigatória do repositório permanece intacta: nada dos jogos é distribuído pelo projeto; cada usuário fornece seus próprios arquivos extraídos do disco localmente._
