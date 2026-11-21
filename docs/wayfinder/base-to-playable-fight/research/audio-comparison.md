# Audio comparison against the Reference Emulator / Comparação de áudio contra o emulador de referência

_Findings for [Survey how to compare audio against the Reference Emulator](../tickets/20-audio-comparison.md). English first, then Brazilian Portuguese. Researched 2026-11-21. Facts and comparative analysis only; no game assets, audio files, or code are stored here. Audio captures, scripts, and intermediate recordings stay in `private/` (git-ignored)._

_Resultado do levantamento para o ticket 20. Inglês primeiro, português do Brasil depois. Apenas fatos e análise comparativa; nenhum asset do jogo, arquivo de áudio ou código entra aqui. Capturas de áudio, scripts e gravações intermediárias ficam em `private/` (ignorado pelo git)._

---

## Resumo em português

- **O problema:** no Ticket 07, o PCSX2 foi escolhido como emulador de referência e o áudio foi incluído como meta da suíte de verificação, com a audição humana como plano B. No entanto, o build de release do PCSX2 não exporta dumps isolados dos comandos do chip de som (SPU2) nem arquivos de onda separados (recursos restritos a builds de desenvolvimento), e sua captura padrão (FFmpeg) grava áudio misturado com vídeo. Além disso, áudio é contínuo e assíncrono: mesmo uma diferença de 1 amostra de atraso, interpolação ou arredondamento de ponto flutuante no reverb quebra totalmente hashes exatos (como SHA-256), tornando a comparação direta de bytes inviável.
- **As 4 opções analisadas:**
  1. **Build de desenvolvimento do PCSX2 local (GPL, ferramenta interna):** compilar o PCSX2 localmente com `PCSX2_DEVBUILD` para usar o dump de ondas do SPU2 e logs internos. *Esforço médio-alto (M–L)* pela manutenção do ambiente de build e sincronia com releases. *Prova fidelidade acústica*, mas não garante hashes exatos entre o port e o emulador. *Licença:* 100% limpa, pois o emulador é usado apenas como ferramenta de bancada privada e nada é distribuído ou incorporado ao port.
  2. **Registro de comandos enviados pelo IOP ao SPU2 (e chamadas RPC/ADX):** registrar a sequência de comandos que a CPU/IOP emite para o subsistema de áudio (alocação de vozes, notas, volume, pitch e streaming ADX). *Esforço baixo-médio (S–M)*. *Prova correção lógica e funcional exata por quadro* (o jogo dispara o som certo no quadro certo com parâmetros certos). Não prova a fidelidade do sintetizador/mixer no PC hospedeiro. *Licença limpa* e determinística: cabe em tabelas de referência versionadas no git.
  3. **Comparação de formas de onda gravadas com tolerância (DSP):** gravar o áudio mixado do PCSX2 (extraído do vídeo via FFmpeg) e do port, alinhando com correlação cruzada (*cross-correlation*) e comparando envelopes espectrais (STFT/MFCC) ou *Dynamic Time Warping* (DTW) com margem de tolerância. *Esforço médio (M)*. *Prova fidelidade acústica perceptual*, detectando canais mudos, pitch distorcido ou vozes ausentes. Sensível ao ajuste de limiares. Arquivos ficam em `private/`.
  4. **Audição humana como plano B:** o desenvolvedor escuta os 4 cenários lado a lado. *Esforço de implementação zero*, mas alto custo manual recorrente. *Prova correção subjetiva e experiência de jogo*. Não automatizável.
- **Recomendação estratégica (Arquitetura em Camadas):**
  - **Camada 1 (Regressão Contínua / Diária):** Opção 2 (Registro de comandos IOP/SPU2). Determinística, exata por quadro e hashable em tabelas no git, idêntica ao modelo adotado para comandos GS e estado de RAM.
  - **Camada 2 (Validação do Motor de Áudio em Marcos):** Opção 3 (Comparação DSP de formas de onda com tolerância). Valida o sintetizador, decodificador ADPCM e streaming ADX do runtime do port contra gravações de referência.
  - **Camada 3 (Diagnóstico Avançado):** Opção 1 (Build dev do PCSX2 local). Mantido como recurso pontual para investigar bugs complexos de DSP do SPU2 ou isolar canais de voz.
  - **Camada 4 (Aceite Final do Marco):** Opção 4 (Audição humana). Validação final pelo dono nos 4 Cenários de Referência.

---

## 1. Context and Problem Statement

Ticket 07 ([verification-oracle.md](../tickets/07-verification-oracle.md)) established PCSX2 (latest release) as the project's Reference Emulator. The verification model relies on:
- Game state in memory at marked frames;
- Command streams sent to the Graphics Synthesizer (GS) per frame;
- Input replays (`.p2m2`) driving deterministic execution across four Reference Scenarios.

Audio was explicitly marked as a goal, but the method of comparison remained open, with human listening designated as the fallback. 

Checking audio output introduces fundamental differences compared to checking memory or graphics commands:
1. **Tooling limitation in PCSX2 release builds:** The official portable release of PCSX2 does not provide command-level dumping for the audio processor (SPU2) or isolated waveform dumping. Its built-in recording facility (FFmpeg) records multiplexed audio and video containers (MP4/MKV). SPU2 logging macros and voice/core wave dumps are compiled only when `PCSX2_DEVBUILD` is enabled.
2. **Asynchrony and clock drift:** Video frames in KOF XI are discrete (VSYNC-locked at ~59.94 Hz). Audio synthesis, however, runs continuously at 44.1 kHz (CDVD/IOP/ADX) and 48 kHz (SPU2 core rate). Slight buffer scheduling variations or host audio device resampling mean that two runs can have identical game logic but sub-millisecond phase offsets.
3. **Impossibility of byte-level sample hashing:** A single-sample phase shift, slight differences in ADPCM decoding filters, or floating-point approximations in SPU2 reverb algorithms cause raw waveform hashes (`SHA-256`) to diverge completely, producing 100% false-negative test failures despite the audio sounding acoustically indistinguishable.

This survey evaluates four concrete paths to compare audio against PCSX2 across effort, proof value, licensing, and fit within the project's Reference Scenarios.

---

## 2. KOF XI Audio Architecture on PS2

Understanding what to compare requires identifying how KOF XI drives sound on the PlayStation 2:

```
[EE (Main CPU)]
       │
       │ SIF RPC (Sound Requests / ADX commands)
       ▼
[IOP (I/O Processor)] ─── Loads 7 IRX modules:
       │                   - LIBSD.IRX & SDRDRV.IRX (Sony Sound Drivers)
       │                   - CRI_ADXI.IRX (CRI ADX Audio Middleware)
       │
       ├─── SPU2 MMIO Registers (Voice allocation, Pitch, ADSR, Reverb, Volume)
       └─── SPU2 DMA (Ch 4: Core 0, Ch 8: Core 1) ──► Uploads ADPCM / Streams PCM
                                                              │
                                                              ▼
                                                   [SPU2 Hardware (2 MB SSRAM)]
                                                   - Core 0: SFX / Voices (4-bit VAG)
                                                   - Core 1: BGM Streams / Ambient
                                                   - Hardware Mixer & Reverb DSP
```

1. **Sound Effects and Voices (SFX):** Managed through Sony's standard SDK modules (`LIBSD.IRX` and `SDRDRV.IRX`). The main game engine on the EE issues high-level SIF RPC calls requesting sound playback. The IOP driver assigns SPU2 voices, configures pitch, ADSR volume envelopes, and triggers Key-ON (`KON`). Sample data lives in SPU2 sound memory (2 MB SSRAM) as 4-bit Sony ADPCM (VAG).
2. **Music (BGM):** Managed through CRI Middleware (`CRI_ADXI.IRX`). Music tracks are stored in an AFS container (`KOFXI.AFS`) on the disc as compressed ADX streams. The IOP reads raw disc sectors, decompresses or buffers the ADX packets, and feeds them into the SPU2 via DMA for streaming playback.

Any audio verification must account for both paths: discrete, event-driven sound effects and continuous, streamed background music.

---

## 3. Evaluation of the Four Comparison Options

### 3.1 Option A: Locally Built PCSX2 Development Build (Internal Developer Tool)

- **Description:** Build a customized PCSX2 binary from source with `PCSX2_DEVBUILD` defined. In development builds, PCSX2 exposes SPU2 debug facilities, including raw WAV dumping per SPU2 core or per voice (`SPU2_LOG_ENABLE`), bypassing host audio drivers and video multiplexing. Custom command-line flags or patch hooks can be inserted to automatically dump audio when a replay terminates.
- **Effort required: Medium to High (M–L).**
  - Requires setting up a Windows MSVC/CMake C++20 build environment with all PCSX2 dependencies.
  - Requires continuous maintenance: Ticket 07 established that the Reference Emulator is "always the latest release". Tracking upstream requires rebuilding, rebasing custom dump hooks, or maintaining a local fork.
  - Recomp runtime contributors would need the devbuild binary locally, creating an additional build prerequisite.
- **What it proves:**
  - Proves high-fidelity emulation output from the reference core before host OS mixing.
  - Can dump isolated audio stems (e.g., Core 0 SFX without BGM, or individual voices).
  - **Does NOT prove cycle-exact sample matching with the recomp port:** Even with raw WAV dumps from PCSX2, the port's audio backend would need an identical SPU2 emulation core with identical fixed-point DSP math and identical clock alignment to achieve bitwise sample equality.
- **License consequences: Clean (Tool-only use).**
  - PCSX2 is licensed under **GPL-3.0-or-later**.
  - Using a locally compiled GPL program as a development tool (generating reference audio or traces kept in `private/`) does not trigger copyleft obligations on the recompiled game port or its runtime. Under copyright and GPL guidelines, the output of a compiler, emulator, or debug tool is not a derivative work of the tool itself.
  - No PCSX2 code is vendored into or linked with the recomp repository.
- **Fit into Reference Scenarios:**
  - Fits Scenarios 1–4: Any recorded `.p2m2` input replay can be played in the devbuild to generate reference WAV files.
  - Provides clean stem separation (isolating Tung Fu Rue's special voice clip in Scenario 3, or separating BGM from combat SFX in Scenario 1 and 2).

### 3.2 Option B: Logging What the IOP Sends to the SPU2 (Command-Stream Logging)

- **Description:** Capture the audio command stream at the control interface rather than the resulting acoustic waveform. This can be captured at two levels:
  1. *Hardware MMIO / DMA boundary:* Intercepting register writes to SPU2 (`VMAX`, `PITCH`, `ADSR`, `ENVX`, `KON`, `KOFF`, `ENDX`, Reverb) and DMA channel 4/8 buffer transfers.
  2. *High-level RPC boundary:* Intercepting EE-to-IOP SIF RPC calls directed to `LIBSD` (voice trigger, sample ID, volume, pan) and CRI ADX commands (`adx_play_bgm(track_id)`).
- **Effort required: Low to Medium (S–M).**
  - In the recomp port, adding a logging interceptor to SPU2 MMIO writes or IOP HLE functions requires minimal code (~100–200 lines).
  - In PCSX2, logging this command stream requires either a lightweight hook in a dev build (linking with Option A) or memory snooping via savestates/PINE.
  - Output is formatted as structured event logs (e.g., JSON or binary event records: `{frame, voice_id, event, pitch, volume}`).
- **What it proves:**
  - **Deterministic functional correctness:** Proves 100% that the recompiled game logic executed the exact right audio triggers at the exact right simulation frames.
  - Proves that hit sounds, character voice lines, announcer calls, and BGM track switches occur without lag, skips, or omissions.
  - **Does NOT prove host acoustic rendering:** It does not prove that the host audio device or software mixer correctly plays the sound without buffer underruns, crackling, or distortion.
- **License consequences: Completely clean (MIT / Permissive).**
  - The logging hooks and event stream schemas are native project implementations.
  - No external GPL code is required. Event log hashes can be stored directly in git-tracked Reference Tables alongside GS command hashes.
- **Fit into Reference Scenarios:**
  - **Ideal fit.** Replays in `.p2m2` yield completely deterministic event streams:
    - *Scenario 1 (2D stage short fight):* Frame-exact log of menu confirmation sounds, announcer "Round 1... Fight!", punch/kick contact sounds, and stage BGM start.
    - *Scenario 2 (3D stage):* Correct 3D stage BGM stream packet dispatch.
    - *Scenario 3 (PS2-exclusive fighter + Leader special):* Frame-exact verification of Leader Super activation sound effects and exclusive character voice triggers.
    - *Scenario 4 (Complete Fight):* Verifies the entire sequence across rounds, KO voice lines, victory quotes, and result screen music transition.

### 3.3 Option C: Comparing Recorded Audio Waveforms with a Tolerance (DSP Analysis)

- **Description:** Record master audio output from PCSX2 (demuxed from FFmpeg capture via `ffmpeg -i capture.mp4 -vn -acodec pcm_s16le ref.wav`) and from the recomp port. Run an automated Python DSP evaluation script using standard signal processing techniques:
  1. *Cross-Correlation ($R_{xy}(\tau)$):* Compute time-domain sliding dot product to identify global latency offset ($\tau$) and synchronize the two tracks.
  2. *Dynamic Time Warping (DTW):* Align localized tempo fluctuations, minor buffer jitter, or frame-limiter drifts.
  3. *Spectral Envelope / STFT Comparison:* Compute Short-Time Fourier Transform magnitude distances or Mel-Frequency Cepstral Coefficients (MFCC) cosine distances. Measure spectral similarity within a defined tolerance band ($\epsilon$).
  4. *Transient / Event Peak Detection:* Verify that energy peaks (hits, explosions, snare hits) align within a temporal window (e.g., $\pm 2$ frames / $\pm 33$ ms).
- **Effort required: Medium (M).**
  - Developing a standalone Python analysis script using `numpy`, `scipy.signal`, or `librosa`.
  - Demuxing PCSX2 video recordings with `ffmpeg` in a pre-test step.
  - Calibration effort: Tuning acceptance thresholds ($\epsilon$) to avoid false negatives caused by SPU2 reverb tail approximations or resampling filters, while reliably detecting missing sound channels or wrong pitches.
- **What it proves:**
  - **Acoustic and perceptual correctness:** Proves that the actual sound emitted into the player's speakers closely matches the reference hardware in volume, frequency spectrum, timing, and pitch.
  - Catches runtime audio bugs: missing audio channels, sample playback speed errors, inverted stereo channels, broken ADPCM decoders, or clipped audio buffers.
  - Does NOT prove bitwise sample equality.
- **License consequences: Completely clean.**
  - Standalone script using standard open-source tools (FFmpeg CLI, NumPy, SciPy under BSD/Apache).
  - WAV files and analysis cache remain strictly inside `private/`.
- **Fit into Reference Scenarios:**
  - *Scenarios 1, 2, and 3 (Short clips, 10–30 s):* Excellent fit. Small audio file size (~2–5 MB uncompressed), fast processing (< 2 seconds per test), distinct transient peaks (hits, special moves) that make cross-correlation alignment trivial.
  - *Scenario 4 (Complete Fight, 2–3 min):* Requires windowed/chunked analysis. Over several minutes, microscopic clock drift between host audio buffer timers and emulated PS2 hardware timers accumulates. Windowing into 5–10 second slices or round boundaries resolves this.

### 3.4 Option D: Human Listening as the Fallback

- **Description:** The developer or owner listens to side-by-side playback of the port and PCSX2, or conducts playtesting while validating audio cues against memory.
- **Effort required: Zero implementation effort; high recurring manual effort.**
  - No scripting or toolchain needed.
  - Requires 5 to 10 minutes of active human listening per verification cycle across the four scenarios.
- **What it proves:**
  - **Subjective player experience:** Confirms that the game feels authentic, the soundtrack loops seamlessly, voices are clear, and effects have punch.
  - Human hearing effortlessly detects gross defects (glitches, popping, missing BGM, silence, wrong voices) that might slip past loose numerical thresholds.
  - **Does NOT provide automated regression protection:** Cannot run unattended, cannot catch regressions during automated developer workflows, and cannot provide machine-readable hashes.
- **License consequences: None.**
- **Fit into Reference Scenarios:**
  - Fits all 4 scenarios as the final human sign-off milestone.

---

## 4. Comparative Synthesis Matrix

| Criterion | Option A: PCSX2 Devbuild Tool | Option B: Command-Stream Logging | Option C: DSP Waveform Comparison | Option D: Human Listening Fallback |
|---|---|---|---|---|
| **Implementation Effort** | Medium–High (M–L) | Low–Medium (S–M) | Medium (M) | None (0) |
| **Recurring Maintenance** | High (syncing with PCSX2 releases) | Low (stable once hooked) | Low–Medium (threshold tuning) | High (manual listening per run) |
| **Automation Feasibility** | Moderate (requires devbuild harness) | **Full (unattended, CLI)** | **Full (unattended, CLI)** | None (manual only) |
| **Determinism & Hashing** | Medium (WAV hashes diverge) | **Exact (integer frame & event hashes)** | Tolerance-based score ($\epsilon$) | None |
| **What it Proves** | Reference emulation accuracy | Game logic audio correctness | Acoustic & perceptual fidelity | Subjective player experience |
| **What it Misses** | Host playback flaws | Synthesizer/mixer backend bugs | Microscopic sub-sample timing | Subtle timing drift, quiet layers |
| **License Risk** | Clean (internal tool only) | Clean (native format) | Clean (independent DSP script) | None |
| **Git Tracking** | None (WAV in `private/`) | **Yes (hashes in Reference Tables)** | Test metric scores in `private/` | None |
| **Scenario 1 (2D Stage)** | Good (clean WAV stem) | Excellent (menu + combat events) | Fast & reliable alignment | Natural check |
| **Scenario 2 (3D Stage)** | Good | Excellent (3D BGM stream check) | Fast & reliable alignment | Natural check |
| **Scenario 3 (Leader Special)**| Good (isolated voice) | Excellent (Leader SFX + voice ID) | Distinct transient signature | High value (voice check) |
| **Scenario 4 (Complete Fight)** | Heavy (large WAV dump) | Excellent (full match event log) | Needs windowing due to drift | Good final milestone check |

---

## 5. Recommended Strategy: Tiered Verification Architecture

A single comparison method cannot satisfy both deterministic regression testing and acoustic fidelity validation. The recommended architecture combines the options into a multi-tiered pipeline:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 1: Command-Stream Logging (Option B)                               │
│ - Runs on every automated test pass and milestone                       │
│ - Compares frame-exact IOP/SPU2 command events against Reference Tables │
│ - Proves: Game simulation drives audio identically to the original      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 2: Automated DSP Waveform Comparison (Option C)                    │
│ - Runs on audio-backend milestones and subsystem refactors              │
│ - Compares rendered port WAV against demuxed PCSX2 reference WAV        │
│ - Cross-correlation alignment + STFT spectral tolerance check          │
│ - Proves: Synthesizer, ADPCM decoder, and mixer produce correct sound   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ TIER 3: Human Listening Sign-Off (Option D)                             │
│ - Final qualitative acceptance test before closing a milestone          │
│ - Owner listens across the 4 Reference Scenarios                        │
│ - Proves: Game sounds satisfying and authentic to the player            │
└─────────────────────────────────────────────────────────────────────────┘
  [Diagnostic Reserve: Option A (Locally built PCSX2 devbuild)]
  - Used only when debugging deep SPU2 DSP anomalies or voice register bugs.
```

### Why this structure fits the project rules:
1. **Zero game data in git:** Reference Tables store only text hashes of the command event streams. All audio recordings, demuxed WAVs, and analysis plots reside in `private/`.
2. **License integrity:** No GPL code is introduced into the recompiled runtime. Option A is relegated to an optional local developer diagnostic aid.
3. **Seamless fit with Ticket 07:** Option B matches the exact structure of GS command stream and memory verification already established for the four Reference Scenarios.

---

## 6. Brazilian Portuguese Translation / Tradução em Português do Brasil

### 6.1 Contexto e Formulação do Problema

O Ticket 07 ([verification-oracle.md](../tickets/07-verification-oracle.md)) definiu o PCSX2 (sempre a versão de release mais recente) como o Emulador de Referência do projeto. O modelo de verificação adotado baseia-se em:
- Estado da memória do jogo em quadros pré-determinados;
- Fluxo de comandos enviados ao Graphics Synthesizer (GS) a cada quadro;
- Replays de comandos de botões (`.p2m2`) executados deterministicamente nos quatro Cenários de Referência.

O áudio foi estabelecido como meta, mas o método exato de comparação permaneceu em aberto, com a audição humana definida como plano de contingência (*fallback*).

A validação de áudio apresenta desafios substancialmente diferentes da comparação de memória ou gráficos:
1. **Limitação de ferramentas no release do PCSX2:** A versão de distribuição padrão do PCSX2 não disponibiliza dumps isolados de comandos do SPU2 nem a gravação de arquivos de áudio independentes. O recurso de captura integrado (baseado em FFmpeg) gera contêineres de vídeo com áudio multiplexado (MP4/MKV). Dumps de ondas sonoras e logs do SPU2 só são compilados quando a flag `PCSX2_DEVBUILD` está ativada.
2. **Assincronia e flutuação de relógio (*clock drift*):** Os quadros de vídeo no KOF XI são discretos (sincronizados com o VSYNC em ~59,94 Hz). A síntese de áudio, por outro lado, é contínua e opera a 44,1 kHz (CDVD/IOP/ADX) e 48 kHz (SPU2). Pequenas variações de agendamento de buffers ou de reamostragem do sistema operacional fazem com que execuções com lógica idêntica apresentem diferenças de fase de frações de milissegundo.
3. **Inviabilidade de hashes exatos de amostras:** Uma variação de uma única amostra, divergências mínimas nos filtros de interpolação ADPCM ou aproximações de ponto flutuante nos algoritmos de reverberação fazem com que hashes binários tradicionais (`SHA-256`) falhem completamente, gerando falsos negativos mesmo quando o som é indistinguível aos ouvidos humanos.

### 6.2 Arquitetura de Áudio do KOF XI no PS2

O som do jogo no PlayStation 2 funciona em dois fluxos bem demarcados:
1. **Efeitos Sonoros e Vozes (SFX):** Controlados pelos módulos oficiais da Sony (`LIBSD.IRX` e `SDRDRV.IRX`). O processador principal (EE) emite chamadas SIF RPC ao processador de E/S (IOP). O driver no IOP gerencia as vozes do SPU2, configura pitch, curvas de envelope ADSR, volume e ativa o gatilho de execução (*Key-ON*). As amostras residem na memória do SPU2 (2 MB SSRAM) no formato Sony ADPCM de 4 bits (VAG).
2. **Música (BGM):** Gerenciada pelo middleware da CRI (`CRI_ADXI.IRX`). As faixas musicais ficam armazenadas no arquivo `KOFXI.AFS` no DVD como streams comprimidos em formato ADX. O IOP faz a leitura direta dos setores do disco, decodifica os pacotes e os transfere via DMA para os canais de reprodução do SPU2.

A verificação de áudio precisa cobrir esses dois lados: os eventos pontuais de efeitos sonoros e o fluxo contínuo da trilha sonora.

### 6.3 Avaliação Detalhada das Quatro Opções

#### Opção A: Build de Desenvolvimento do PCSX2 Local (Ferramenta Interna de Desenvolvimento)
- **Descrição:** Compilar o PCSX2 localmente com a flag `PCSX2_DEVBUILD` ativa. Nesse modo, o emulador expõe recursos avançados de diagnóstico do SPU2, permitindo gerar dumps diretos de áudio WAV por núcleo ou por voz individual (`SPU2_LOG_ENABLE`), contornando o mixer do sistema operacional e a multiplexação de vídeo.
- **Esforço:** Médio a Alto (M–L). Exige manter o ambiente de compilação em C++20 configurado no Windows e acompanhar as atualizações contínuas do PCSX2 (já que o projeto adota o release mais novo).
- **O que prova:** Prova com máxima fidelidade o áudio gerado pelo emulador de referência. Não garante, contudo, que o port recompilado consiga produzir hashes de amostras idênticos byte a byte, devido a diferenças inevitáveis de ponto flutuante e DSP.
- **Licença:** Totalmente segura. O PCSX2 é GPLv3, mas usá-lo privadamente no computador do desenvolvedor como ferramenta de teste/geração de artefatos não contamina o código do port. Nenhum código do PCSX2 é incluído no repositório.
- **Cenários de Referência:** Aplica-se aos Cenários 1 a 4 com os replays `.p2m2`. Útil para isolar canais específicos (como a voz de um especial de líder no Cenário 3).

#### Opção B: Registro de Comandos Enviados pelo IOP ao SPU2 (Command-Stream Logging)
- **Descrição:** Registrar os comandos de controle na fronteira entre a lógica e o sintetizador de áudio:
  1. *Nível de Hardware/MMIO:* Gravações nos registradores do SPU2 (alocação de voz, volume, pitch, ADSR, reverb) e transferências de DMA (canais 4 e 8).
  2. *Nível de RPC de Alto Nível:* Chamadas de função de áudio enviadas pela CPU ao IOP (`LIBSD`) e requisições do CRI ADX (`adx_play_bgm`).
- **Esforço:** Baixo a Médio (S–M). Implementar ganchos de log na camada de emulação do IOP/SPU2 do port é direto e conciso.
- **O que prova:** Prova **correção funcional determinística**. Garante com precisão de quadro que o jogo disparou o som correto, no momento exato e com os parâmetros adequados. Não prova que o mixer do PC hospedeiro está livre de ruídos ou falhas acústicas.
- **Licença:** Limpa (MIT/permissiva). Formato estruturado próprio (JSON ou registros binários). As tabelas de hash podem ser versionadas diretamente no git.
- **Cenários de Referência:** Encaixe perfeito para todos os 4 cenários:
  - *Cenário 1 (Fase 2D curta):* Confere cliques de menu, vozes do anunciador ("Round 1... Fight!"), golpes e início da BGM.
  - *Cenário 2 (Fase 3D):* Confere o disparo da música de fundo específica da fase 3D.
  - *Cenário 3 (Lutador exclusivo + Especial de Líder):* Confere o som de ativação do golpe e os clipes de voz exclusivos do PS2.
  - *Cenário 4 (Luta Completa):* Confere a sequência completa da luta, falas de vitória e transição para a tela de resultados.

#### Opção C: Comparação de Formas de Onda Gravadas com Tolerância (Análise DSP)
- **Descrição:** Gravar o áudio final gerado pelo PCSX2 (extraído do vídeo via FFmpeg) e pelo port nativo. Um script em Python executa a validação por processamento digital de sinais:
  1. *Correlação Cruzada:* Identifica a latência global ($\tau$) entre as duas gravações e alinha os pontos de início.
  2. *Dynamic Time Warping (DTW):* Compensa variações microscópicas de ritmo ou oscilações de buffer.
  3. *Comparação Espectral (STFT / MFCC):* Mede a distância espectral de frequências com base em uma margem de tolerância definida ($\epsilon$).
  4. *Detecção de Picos e Transientes:* Garante que eventos percussivos e impactos ocorram dentro de uma janela temporal aceitável ($\pm 2$ quadros).
- **Esforço:** Médio (M). Demanda construir o script de DSP em Python (`scipy`, `numpy`) e calibrar os limiares de tolerância para evitar falsos positivos sem deixar passar anomalias reais.
- **O que prova:** Prova **fidelidade acústica e perceptual**. Confirma que o som gerado reproduz as frequências, timbres, volumes e balanço estéreo esperados.
- **Licença:** Totalmente limpa. Scripts independentes com bibliotecas de código aberto permissivas; áudios ficam em `private/`.
- **Cenários de Referência:**
  - *Cenários 1, 2 e 3 (Trechos curtos, 10–30 s):* Excelente. Arquivos leves (~2 a 5 MB), alinhamento rápido e confiável.
  - *Cenário 4 (Luta Completa, 2–3 min):* Exige divisão do áudio em blocos temporais (janelas de 5 a 10 segundos ou por round) para evitar o acúmulo de *clock drift*.

#### Opção D: Audição Humana como Plano B
- **Descrição:** O desenvolvedor ou o dono escuta as gravações ou joga as partidas prestando atenção à autenticidade e sincronia do áudio.
- **Esforço:** Zero esforço de código; alto custo manual recorrente (5 a 10 minutos por rodada de testes).
- **O que prova:** Prova a **experiência subjetiva do jogador**. O ouvido humano detecta com extrema rapidez anomalias grosseiras (sons estourados, chiados, silêncio, canais ausentes ou músicas fora de tom). Não serve para automação de testes nem detecção de regressões em commits.
- **Licença:** Sem impacto.
- **Cenários de Referência:** Aplica-se a todos os 4 cenários como validação de entrega nos marcos principais.

### 6.4 Matriz Síntese Comparativa

| Critério | Opção A: Build Dev PCSX2 | Opção B: Registro de Comandos IOP/SPU2 | Opção C: Comparação DSP com Tolerância | Opção D: Audição Humana |
|---|---|---|---|---|
| **Esforço de Implementação** | Médio–Alto (M–L) | Baixo–Médio (S–M) | Médio (M) | Zero (0) |
| **Manutenção Contínua** | Alta (atualizações do PCSX2) | Baixa (estável após ganchos) | Baixa–Média (ajuste de limiares) | Alta (escuta manual repetitiva) |
| **Automação de Testes** | Razoável (com harness) | **Total (CLI, silencioso)** | **Total (CLI, silencioso)** | Nula (manual) |
| **Determinismo e Hash** | Médio (WAVs divergem) | **Exato (quadro e eventos)** | Pontuação por margem ($\epsilon$) | Inexistente |
| **O que Prova** | Precisão do emulador de ref. | Correção lógica do jogo | Fidelidade acústica real | Sensação geral de jogo |
| **O que Deixa Passar** | Falhas do mixer do PC | Erros acústicos do backend | Timing exato em sub-amostras | Desvios sutis de volume/reverb |
| **Risco de Licença** | Seguro (ferramenta local) | Seguro (formato nativo) | Seguro (script independente) | Inexistente |
| **Armazenamento no Git** | Nenhum (WAV em `private/`) | **Sim (hashes em tabelas)** | Métricas locais em `private/` | Nenhum |
| **Cenário 1 (Fase 2D)** | Bom | Excelente (menus e golpes) | Alinhamento ágil | Avaliação natural |
| **Cenário 2 (Fase 3D)** | Bom | Excelente (stream da BGM) | Alinhamento ágil | Avaliação natural |
| **Cenário 3 (Especial Líder)** | Bom (voz isolada) | Excelente (ID de voz e FX) | Assinatura clara de pico | Alto valor (avaliação de voz) |
| **Cenário 4 (Luta Completa)** | Pesado (WAV grande) | Excelente (partida inteira) | Exige divisão em blocos | Bom fechamento de marco |

### 6.5 Recomendação Estratégica: Arquitetura em Camadas

A recomendação definitiva do levantamento é estruturar a verificação de áudio em camadas complementares:

1. **Camada 1 (Regressão Contínua / Diária): Opção B (Registro de Comandos IOP/SPU2)**
   - Integra-se diretamente ao modelo de Tabelas de Referência do Ticket 07.
   - Fornece hashes exatos por quadro no git sem armazenar nenhum byte de som do jogo.
   - Garante que nenhuma alteração de código faça o jogo esquecer de tocar um golpe, voz ou música.
2. **Camada 2 (Validação do Motor de Áudio em Marcos): Opção C (Comparação DSP de Formas de Onda)**
   - Executada ao desenvolver ou alterar o backend de áudio do port nativo (decodificador ADPCM, sintetizador SPU2 e streaming ADX).
   - Extrai o áudio do PCSX2 via FFmpeg e compara os espectrogramas e picos contra a saída do port com tolerância matemática.
3. **Camada 3 (Diagnóstico Avançado de Erros): Opção A (Build Dev do PCSX2)**
   - Mantida na bancada como ferramenta de suporte para casos em que haja discrepâncias complexas de DSP ou necessidade de extrair canais de voz isolados.
4. **Camada 4 (Homologação Final): Opção D (Audição Humana)**
   - Avaliação qualitativa do dono do projeto ao final de cada marco de luta jogável nos 4 Cenários de Referência.
