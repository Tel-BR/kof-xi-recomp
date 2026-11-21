---
id: 20
title: Survey how to compare audio against the Reference Emulator
type: research
status: closed
assignee:
blocked_by: []
research: ../research/audio-comparison.md
---

## Question

How can the port's audio be checked against PCSX2? The owner wants audio in the verification suite, but the PCSX2 release has no dump of the sound chip's commands (SPU2 logging and wave dumps exist only in development builds) and its audio capture is mixed with video. Survey the options: a locally built PCSX2 development build used only as a tool (GPL, never distributed), logging what the IOP sends to the SPU2, comparing recorded waveforms with a tolerance, or human listening as the fallback. For each: effort, what it proves, licence consequences and how it fits the Reference Scenarios. Findings only; no code.

_PT-BR: como conferir o áudio do port contra o PCSX2? O dono quer áudio na suíte, mas o release do PCSX2 não tem dump dos comandos do chip de som (registro e dump do SPU2 só existem em builds de desenvolvimento) e a captura de áudio sai misturada com o vídeo. Levantar as opções: um build de desenvolvimento do PCSX2 compilado localmente só como ferramenta (GPL, nunca distribuído), registrar o que o IOP manda ao SPU2, comparar formas de onda com tolerância, ou audição humana como plano B. Para cada uma: esforço, o que prova, consequências de licença e como se encaixa nos cenários de referência. Só achados, sem código._

## Resolution

Survey completed on 2026-11-21. Full survey and evaluation: [audio-comparison.md](../research/audio-comparison.md).

The release build of PCSX2 does not dump SPU2 command streams and mixes audio into FFmpeg video captures. Furthermore, raw audio waveforms suffer from clock drift, sub-millisecond phase jitter, and floating-point DSP differences, making sample-exact hashing (`SHA-256`) impractical for verification.

Four options were surveyed:
1. **Locally built PCSX2 devbuild (GPL internal tool):** Medium–High effort. Enables internal SPU2 logging and WAV dumps. Proves emulator output fidelity, but does not guarantee sample-exact matching against the port. License is clean because it is an internal developer tool never distributed. Fits all scenarios, but has high maintenance tracking upstream releases.
2. **Logging IOP-to-SPU2 commands and RPC/ADX calls:** Low–Medium effort. Captures SPU2 register writes/DMA and `LIBSD`/`CRI ADX` requests. Proves 100% deterministic functional game-logic correctness at exact frames. Clean MIT license; hashes fit directly into git Reference Tables. Fits all 4 scenarios perfectly.
3. **Comparing recorded waveforms with tolerance (DSP):** Medium effort. Extracts audio from PCSX2 FFmpeg video and compares against port audio using cross-correlation alignment and STFT/MFCC spectral envelope distance. Proves acoustic and perceptual correctness (catches missing channels, wrong pitches, clipping). Clean license, data stays in `private/`. Fits Scenarios 1–3 directly; Scenario 4 requires windowed chunking to avoid clock drift.
4. **Human listening fallback:** Zero implementation effort, but recurring manual effort. Proves qualitative player experience and catches gross bugs effortlessly, but cannot be automated.

**Recommended Strategy (Tiered Verification):**
- **Tier 1 (Automated Regression):** Option 2 (Command-stream logging) as the primary automated test on every run, storing deterministic event hashes in git Reference Tables.
- **Tier 2 (Audio Engine Validation):** Option 3 (DSP waveform comparison with tolerance) on audio backend milestones to verify acoustic output against demuxed PCSX2 reference recordings.
- **Tier 3 (Diagnostic Deep Dive):** Option 1 (PCSX2 devbuild) kept in reserve for isolating elusive SPU2 hardware/DSP register bugs.
- **Tier 4 (Milestone Sign-Off):** Option 4 (Human listening) across the 4 Reference Scenarios for final playable fight milestone releases.

_PT-BR: levantamento concluído em 21/11/2026. Estudo completo e avaliação: [audio-comparison.md](../research/audio-comparison.md). O release do PCSX2 não extrai comandos do SPU2 e grava áudio misturado ao vídeo; além disso, formas de onda brutas sofrem com drift de relógio, jitter de fase e arredondamento de DSP, tornando hashes exatos de amostras (como SHA-256) inviáveis para verificação. As quatro opções foram levantadas: (1) build dev do PCSX2 local como ferramenta interna (esforço M–L, prova fidelidade do emulador mas não garante hash idêntico, licença limpa como ferramenta privada, manutenção contínua); (2) registro de comandos do IOP para o SPU2 e chamadas RPC/ADX (esforço S–M, prova 100% de correção lógica determinística por quadro, licença limpa, hashes cabem nas Tabelas de Referência no git, encaixe ideal nos 4 cenários); (3) comparação DSP de formas de onda com tolerância (esforço M, alinhamento por correlação cruzada e distância espectral STFT/MFCC, prova fidelidade acústica perceptual, arquivos em private/, exige divisão em blocos no Cenário 4); (4) audição humana como plano B (esforço zero de código, custo manual recorrente, validação qualitativa indispensável mas não automatizável). Estratégia recomendada em camadas: Camada 1 (regressão diária por registro de comandos IOP/SPU2 com hashes no git); Camada 2 (validação acústica do motor de áudio em marcos por comparação DSP com tolerância); Camada 3 (build dev do PCSX2 de reserva para depuração pontual de registradores SPU2); Camada 4 (homologação final por audição humana nos 4 cenários de referência ao fechar marcos jogáveis)._
