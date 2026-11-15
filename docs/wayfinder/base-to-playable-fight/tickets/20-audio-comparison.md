---
id: 20
title: Survey how to compare audio against the Reference Emulator
type: research
status: open
assignee:
blocked_by: []
---

## Question

How can the port's audio be checked against PCSX2? The owner wants audio in the verification suite, but the PCSX2 release has no dump of the sound chip's commands (SPU2 logging and wave dumps exist only in development builds) and its audio capture is mixed with video. Survey the options: a locally built PCSX2 development build used only as a tool (GPL, never distributed), logging what the IOP sends to the SPU2, comparing recorded waveforms with a tolerance, or human listening as the fallback. For each: effort, what it proves, licence consequences and how it fits the Reference Scenarios. Findings only; no code.

_PT-BR: como conferir o áudio do port contra o PCSX2? O dono quer áudio na suíte, mas o release do PCSX2 não tem dump dos comandos do chip de som (registro e dump do SPU2 só existem em builds de desenvolvimento) e a captura de áudio sai misturada com o vídeo. Levantar as opções: um build de desenvolvimento do PCSX2 compilado localmente só como ferramenta (GPL, nunca distribuído), registrar o que o IOP manda ao SPU2, comparar formas de onda com tolerância, ou audição humana como plano B. Para cada uma: esforço, o que prova, consequências de licença e como se encaixa nos cenários de referência. Só achados, sem código._
