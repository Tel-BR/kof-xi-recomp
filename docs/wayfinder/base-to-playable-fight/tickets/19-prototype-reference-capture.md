---
id: 19
title: Prototype the reference capture on one scenario
type: task
status: open
assignee:
blocked_by: []
---

## Question

Can the Reference Emulator produce repeatable, frame-exact reference data from one Reference Scenario? The owner records one scenario in PCSX2 (menu to a short fight on a regular 2D stage), then, on the owner's machine, find out: (1) whether playing the same replay twice gives identical memory in the savestate taken at the pause that ends a recording, and which memory areas differ between the two runs (the noise); (2) whether truncated copies of the `.p2m2` file (edited total-frames field) pause at the chosen frame, giving checkpoints at frames of our choosing; (3) whether a GS dump can be tied to a known frame of the replay; (4) whether a different BIOS dump changes any game-owned memory; (5) which settings (real-time clock, MTVU, cycle rate, fast boot, floating-point options) make runs reproducible. Record counts, hashes, setting names and the PCSX2 version only; nothing from the game leaves `private/`. See [reference-emulator-capabilities.md](../research/reference-emulator-capabilities.md) for what PCSX2 does and does not offer.

_PT-BR: o emulador de referência consegue gerar dados de referência repetíveis e exatos por quadro a partir de um cenário? O dono grava um cenário no PCSX2 (menu até uma luta curta numa fase 2D comum); na máquina dele, descobrir: (1) se rodar o mesmo replay duas vezes dá memória idêntica no savestate tirado na pausa do fim da gravação, e quais áreas mudam entre as duas execuções (o ruído); (2) se cópias truncadas do arquivo `.p2m2` pausam no quadro escolhido, dando pontos de checagem onde quisermos; (3) se um dump do GS pode ser amarrado a um quadro conhecido; (4) se outro BIOS muda alguma área de memória do jogo; (5) quais ajustes tornam as execuções reprodutíveis. Só contagens, hashes, nomes de ajustes e a versão do PCSX2; nada do jogo sai de `private/`._
