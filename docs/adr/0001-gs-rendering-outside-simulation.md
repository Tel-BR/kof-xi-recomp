# GS Rendering Kept Outside Simulation State

The port translates the PS2 Graphics Synthesizer (GS) PATH3 command stream into modern graphics API calls (Vulkan/Direct3D) using PS2Recomp's shader backend, keeping all GPU and renderer state completely outside the savestate buffer that rollback netplay serializes. This enables fast frame rewinding with suppressed draw calls during rollback prediction catch-up, while an assertion guard logs if any unobserved VU1 microcode is ever transmitted.

_PT-BR: O port traduz o fluxo de comandos PATH3 do Graphics Synthesizer (GS) para chamadas de APIs gráficas modernas (Vulkan/Direct3D) através do backend de shaders do PS2Recomp, mantendo todo o estado de renderização e da GPU fora do buffer de memória que o rollback salva. Isso permite avanço rápido de quadros sem desenhar na tela durante correções de rede, enquanto uma guarda de log alerta caso qualquer microcódigo de VU1 inesperado seja enviado._
