---
id: 08
title: Inspect the code structure of each candidate release
type: task
status: open
assignee:
blocked_by: []
---

## Question

What does the code of each candidate look like from a recompiler's point of view? For the PS2 disc, the Dreamcast Conversion disc and the owner's Atomiswave cartridge dump (the owner has the cartridge; the dump goes in `private/arcade/`), record structural facts only: executable format and size; whether symbols or debug info are present; how much is code versus data; how many separately loaded code modules or overlays exist; where fighter and mode data live. For the Dreamcast Conversion, confirm or refute that it is a small loader plus the arcade cartridge data, and whether the arcade code inside matches the cartridge dump. AFK: the agent runs this on the owner's machine. Never record disassembly, assets or any other game content: sizes, counts, formats and hashes only.

_PT-BR: como é o código de cada candidato, do ponto de vista de um recompilador? Registrar só fatos estruturais (formato e tamanho do executável, se há símbolos, quanto é código ou dados, quantos módulos de código, onde ficam os dados de lutadores e modos) para o disco de PS2, o disco de Dreamcast e o dump do cartucho Atomiswave do dono (em `private/arcade/`); na conversão de Dreamcast, confirmar se é um carregador mais os dados do cartucho e se o código bate com o dump do cartucho. O agente faz sozinho; nada de conteúdo do jogo, só tamanhos, contagens, formatos e hashes._
