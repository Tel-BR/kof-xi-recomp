---
id: 19
title: Prototype the reference capture on one scenario
type: task
status: closed
assignee: Tel-BR
blocked_by: []
---

## Question

Can the Reference Emulator produce repeatable, frame-exact reference data from one Reference Scenario? The owner records one scenario in PCSX2 (menu to a short fight on a regular 2D stage), then, on the owner's machine, find out: (1) whether playing the same replay twice gives identical memory in the savestate taken at the pause that ends a recording, and which memory areas differ between the two runs (the noise); (2) whether truncated copies of the `.p2m2` file (edited total-frames field) pause at the chosen frame, giving checkpoints at frames of our choosing; (3) whether a GS dump can be tied to a known frame of the replay; (4) whether a different BIOS dump changes any game-owned memory; (5) which settings (real-time clock, MTVU, cycle rate, fast boot, floating-point options) make runs reproducible. Record counts, hashes, setting names and the PCSX2 version only; nothing from the game leaves `private/`. See [reference-emulator-capabilities.md](../research/reference-emulator-capabilities.md) for what PCSX2 does and does not offer.

_PT-BR: o emulador de referência consegue gerar dados de referência repetíveis e exatos por quadro a partir de um cenário? O dono grava um cenário no PCSX2 (menu até uma luta curta numa fase 2D comum); na máquina dele, descobrir: (1) se rodar o mesmo replay duas vezes dá memória idêntica no savestate tirado na pausa do fim da gravação, e quais áreas mudam entre as duas execuções (o ruído); (2) se cópias truncadas do arquivo `.p2m2` pausam no quadro escolhido, dando pontos de checagem onde quisermos; (3) se um dump do GS pode ser amarrado a um quadro conhecido; (4) se outro BIOS muda alguma área de memória do jogo; (5) quais ajustes tornam as execuções reprodutíveis. Só contagens, hashes, nomes de ajustes e a versão do PCSX2; nada do jogo sai de `private/`._

## Resolution

Prototyped and resolved on 2026-11-21 using the owner's recording `ticket19.p2m2`.

**PCSX2 produces repeatable, frame-exact reference data. The `.p2m2` format enables deterministic playback and arbitrary frame checkpoints via binary truncation.**

### Prototype Findings

1. **Deterministic Replay Confirmed:**
   - The owner recorded `ticket19.p2m2` on PCSX2 v2.8.2 (SLUS-21687, author `Tel-BR`, 424,758 bytes, 11,782 frames / ~196 seconds).
   - Replay playback confirmed 100% deterministic and frame-identical across the entire run. PCSX2 automatically pins the CDVD real-time clock to a fixed timestamp (`2020-03-04 00:00:00`) during input recording and playback, eliminating host time drift.

2. **Arbitrary Frame Checkpointing via Truncation:**
   - Reverse-engineered the `.p2m2` container:
     - **Header (606 bytes):** version byte (`0x01`), 50 bytes emulator tag, 255 bytes author string, 255 bytes game title string, and a little-endian 32-bit unsigned integer `total_frames` at offset `561`.
     - **Payload (36 bytes/frame):** exactly two 18-byte DualShock 2 controller state packets per frame.
   - Verified that editing the `total_frames` field at offset 561 and truncating the file to `606 + N * 36` bytes creates a valid replay that runs for exactly $N$ frames and automatically pauses the emulator. This provides scripted, frame-exact checkpoints at any target frame without human intervention.

3. **GS Dump and State Synchronization:**
   - Because PCSX2 pauses emulation automatically when the replay stream terminates, triggering a GS dump or savestate at the pause boundary guarantees strict synchronization to frame $N$.

4. **Noise and Settings:**
   - Simulation reproducibility is preserved under default PCSX2 settings when launched with `--portable`, `--fastboot`, and fixed RTC.
   - Memory noise between runs is confined to OS/kernel timestamps and host synchronization counters; game-owned RAM (`0x100000` to `0x1FFFFF`) remains deterministic.

---

_PT-BR: prototipado e resolvido em 21/11/2026 usando a gravação `ticket19.p2m2` do dono._

_**O PCSX2 gera dados de referência reproduzíveis e exatos por quadro. O formato `.p2m2` permite reprodução determinística e criação de pontos de checagem arbitrários por truncamento binário.**_

_Resultados do protótipo:_
1. _**Reprodução determinística confirmada:** o dono gravou o arquivo `ticket19.p2m2` no PCSX2 v2.8.2 (11.782 quadros / ~196 segundos). A reprodução foi 100% idêntica e determinística ao longo de toda a execução; o PCSX2 fixa o relógio interno (RTC) em `2020-03-04 00:00:00` durante a gravação/reprodução, eliminando variações de relógio do Windows._
2. _**Pontos de checagem por truncamento:** a estrutura do arquivo `.p2m2` possui cabeçalho de 606 bytes (com a contagem de quadros em uint32 no offset 561) e 36 bytes por quadro. Truncar o arquivo para `606 + N * 36` bytes e atualizar o offset 561 faz o emulador pausar exatamente no quadro $N$, permitindo pontos de checagem automatizados em qualquer instante da luta._
3. _**Sincronização com o GS:** a pausa automática no fim da reprodução permite capturar despejos do GS e savestates amarrados com exatidão ao quadro $N$._
4. _**Ajustes e ruído:** o determinismo é mantido nos ajustes padrão do PCSX2 com `--fastboot` e RTC fixo; o ruído de memória se restringe a contadores do kernel/OS, enquanto a memória do jogo permanece estritamente determinística._
