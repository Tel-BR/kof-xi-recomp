# KOF XI Recomp

Static recompilation of The King of Fighters XI into a native PC port.

_Recompilação estática de The King of Fighters XI para um port nativo de PC. A versão em português de cada seção vem logo depois da versão em inglês._

## Hard rule: no game data in git

This repository must never contain anything from the games. Users supply their own
disc images. Disc images, generated code and extracted assets live in `private/`,
which is git-ignored. Never `git add -f` anything under `private/`, never commit
disc images, ROMs, executables or extracted assets, and never paste game data into
issues, docs or commit messages.

### Regra obrigatória: nada dos jogos no git

Este repositório nunca pode conter nada dos jogos. Cada usuário fornece as próprias
imagens de disco. Imagens de disco, código gerado e assets extraídos ficam em
`private/`, que o git ignora. Nunca use `git add -f` em nada dentro de `private/`,
nunca faça commit de imagens de disco, ROMs, executáveis ou assets extraídos, e nunca
cole dados dos jogos em issues, documentação ou mensagens de commit.

## Language convention

Human-facing docs (README, `docs/` outside `docs/agents/`, ADRs, glossary) are
bilingual when possible: English first, then Brazilian Portuguese. Issue titles are
in English; issue bodies may be bilingual. Agent-operational files in `docs/agents/`
are English-only so the two versions cannot drift apart.

### Convenção de idioma

A documentação para pessoas (README, `docs/` fora de `docs/agents/`, ADRs, glossário)
é bilíngue sempre que possível: inglês primeiro, depois português do Brasil. Títulos
de issues em inglês; o corpo pode ser bilíngue. Os arquivos operacionais para agentes
em `docs/agents/` ficam só em inglês, para que as duas versões não se desencontrem.

## Agent skills

### Issue tracker

Issues live in GitHub Issues for Tel-BR/kof-xi-recomp, managed with the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default triage labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
