# GS Rendering Kept Outside Simulation State

**Status: under review (2026-11-22).** Its premise is false: PS2Recomp has no shader GS backend, only a CPU rasteriser. Keeping renderer state outside rollback still stands. See [ticket 16](../wayfinder/base-to-playable-fight/tickets/16-gs-vu1-approach.md).

_PT-BR: **Situação: em revisão (22/11/2026).** A premissa é falsa: o PS2Recomp não tem backend de GS com shaders, só um rasterizador na CPU. Manter o estado do renderizador fora do rollback continua valendo. Ver o ticket 16._

The port translates the PS2 Graphics Synthesizer (GS) PATH3 command stream into modern graphics API calls (Vulkan/Direct3D) using PS2Recomp's shader backend, keeping all GPU and renderer state completely outside the savestate buffer that rollback netplay serializes. This enables fast frame rewinding with suppressed draw calls during rollback prediction catch-up, while an assertion guard logs if any unobserved VU1 microcode is ever transmitted.

_PT-BR: O port traduz o fluxo de comandos PATH3 do Graphics Synthesizer (GS) para chamadas de APIs gráficas modernas (Vulkan/Direct3D) através do backend de shaders do PS2Recomp, mantendo todo o estado de renderização e da GPU fora do buffer de memória que o rollback salva. Isso permite avanço rápido de quadros sem desenhar na tela durante correções de rede, enquanto uma guarda de log alerta caso qualquer microcódigo de VU1 inesperado seja enviado._
