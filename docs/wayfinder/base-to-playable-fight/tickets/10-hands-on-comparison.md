---
id: 10
title: Compare both releases hands-on in emulators
type: task
status: closed
assignee: Tel-BR
blocked_by: []
research: ../research/hands-on-checklist.md
---

## Question

What differences between the releases matter to the owner as a player? The owner plays the PS2 Release in PCSX2 and the Arcade Release in Flycast, from his own copies, following a checklist the agent prepares: menus and modes, roster and Hidden Characters, feel of controls and timing, loading, audio, visual quality, and how online rollback behaves in Flycast. The answer records his observations and which differences are must-keeps. HITL: the agent writes the checklist; the owner plays and reports.

_PT-BR: que diferenças entre as versões importam para o dono como jogador? Ele joga a versão de PS2 no PCSX2 e a de arcade no Flycast, a partir das próprias cópias, seguindo um checklist que o agente prepara (menus e modos, elenco e personagens ocultos, sensação dos controles, carregamento, som, imagem, rollback online no Flycast). A resposta registra as observações e o que é indispensável manter._

## Progress

- 2026-11-11: checklist written: [research/hands-on-checklist.md](../research/hands-on-checklist.md). Claimed for the owner (Tel-BR), who plays and reports; the ticket closes when his answers are recorded here as the Resolution.

  _PT-BR: checklist pronto. O ticket fica com o dono, que joga e relata; fecha quando as respostas forem registradas aqui._

## Resolution

The owner played the PS2 Release in PCSX2 and the Arcade Release (his own cartridge dump) in Flycast, and answered the [checklist](../research/hands-on-checklist.md) on 2026-11-11. His answers, in his words where possible:

- **Overall:** prefers the PS2 Release. "The PS2 gameplay is much better tuned than Flycast's; moves come out more easily", possibly an input change, maybe tuned for joysticks. In return, Flycast feels much lighter and runs much better than PCSX2.
- **Controls:** the PS2 Release is more responsive (specials, supers, tag-outs, cancels). This matches the published note that the port's controls were made more responsive based on arcade feedback ([compare-base-versions.md](../research/compare-base-versions.md) §1).
- **PS2-only content, all marked MUST for the final port** (not necessarily the first build): playable bosses and the NGBC-derived fighters; the extra modes (Challenge, Edit, classic Team); the 4 extra stages; the arranged soundtrack.
- **First playable build:** "just the fight is enough". No screens outside round one to the result screen are required, so the glossary's Complete Fight stays as defined.
- **Visuals:** defects only in PCSX2: slowdown, missing textures, and rare, occasional problems with 3D stage elements. No complaints about Flycast.
- **Loading:** the PS2 Release is much slower.
- **Online rollback in Flycast:** tested with another player. A few minor issues, probably emulation (occasional sound flicker), nothing serious; it ran very well most of the time.
- **Rejecting a version:** neither. He leans towards the PS2 Release, but each has strengths, and he will not discard either until the effort is known. **Decisive criteria for the Base Version: excellent performance with the NGBC fighters, and rollback netplay.**

Agent note (interpretation, not the owner's words): PCSX2's slowdown, missing textures and loading times are properties of emulating the PS2, not necessarily of the game; a native port would face the same GS and disc-reading problems in its own way, so they measure the size of that work rather than settle the question.

_PT-BR: o dono prefere o PS2 no geral: a jogabilidade é mais bem ajustada e os golpes saem mais fácil; em troca, o Flycast é bem mais leve e roda melhor que o PCSX2. Tudo o que só o PS2 tem é indispensável no port final (chefes e lutadores do NGBC, modos extras, fases extras, trilha arranjada). Para o primeiro build, "só a luta basta". O PCSX2 teve lentidão, texturas faltando e problemas raros em elementos 3D dos cenários, e carrega bem mais devagar. O rollback do Flycast funcionou bem, com raros chiados de som. Nenhuma versão está descartada; o dono tende ao PS2, e os critérios decisivos são desempenho excelente com os lutadores do NGBC e netplay com rollback._
