# DMA scratchpad fix and rendering follow-up

The GPU runtime was accepting the title screen's texture uploads and dropping its draw packets. The `sceDmaSend` adapter stripped the CPU scratchpad window from the address of the DMA chain, so the chain walker tried to read its first tag outside RAM. The fix preserves that window for both scratchpad aliases.

The regression test injects a synthetic chain through `sceDmaSend` and checks that the GIF callback receives its payload. The test failed before the fix and passed afterward. The broader runtime suite finished with 441 of 465 tests passing and the same 24 pre-existing failures. In the installed GPU build, the title screen rendered with 181 textured draws in the sampled field. The same run verified Start, Down to TEAM, and Up to ARCADE. A run with audio enabled confirmed intermittent output.

Apply [the runtime patch](../../../../tools/runtime/patches/ps2recomp-fixer-dma-scratchpad.patch) from the root of the PS2Recomp-Fixer checkout and rebuild the runtime and test target. The patch was prepared against Fixer `c5a71482dd99f1351bd1ac9d9549098645ddf12c`. Captures and built executables stay in the ignored local workspace.

## Remaining work

- [Issue #18](https://github.com/Tel-BR/kof-xi-recomp/issues/18) stays open for the graphics investigation. Compare the rotating, color-changing background in the main menu with the apparently similar elements in character selection and the fight timer. Check which draw path, texture mode, transforms, blending and depth behavior they share before attributing them to a single defect.
- [Issue #12](https://github.com/Tel-BR/kof-xi-recomp/issues/12) can proceed independently of that investigation.
- The owner reports that the SNK and ADK boot logos render distorted and too low. Track the opening visuals under [issue #14](https://github.com/Tel-BR/kof-xi-recomp/issues/14).
- With audio enabled, output is intermittent. About 9.5 seconds of a 12-second idle-menu sample were effectively silent at the runtime's host queue. Continuous music and clean effects remain open in [issue #15](https://github.com/Tel-BR/kof-xi-recomp/issues/15).

---

# Correção de DMA na scratchpad e investigação gráfica

O runtime GPU recebia as texturas da tela de título, mas descartava os pacotes de desenho. O adaptador `sceDmaSend` removia a faixa de endereços da scratchpad da CPU ao converter o endereço da cadeia DMA. A leitura da primeira tag acabava fora da RAM. A correção preserva essa faixa para os dois endereços equivalentes da scratchpad.

O teste de regressão envia uma cadeia sintética por `sceDmaSend` e confere se o callback do GIF recebe o conteúdo. O teste falhou antes da correção e passou depois. A suíte do runtime terminou com 441 de 465 testes aprovados e as mesmas 24 falhas preexistentes. Na build GPU instalada, o quadro capturado da tela de título teve 181 desenhos com textura. Na mesma execução, Start abriu o menu, ↓ selecionou TEAM e ↑ voltou para ARCADE. Uma execução com áudio habilitado confirmou sinal intermitente.

Aplique [o patch do runtime](../../../../tools/runtime/patches/ps2recomp-fixer-dma-scratchpad.patch) na raiz do checkout do PS2Recomp-Fixer e recompile o runtime e o executável de testes. O patch foi preparado sobre o commit `c5a71482dd99f1351bd1ac9d9549098645ddf12c` do Fixer. As capturas e os executáveis compilados ficam na área local ignorada pelo Git.

## Pendências

- A [issue #18](https://github.com/Tel-BR/kof-xi-recomp/issues/18) continua aberta para a investigação gráfica. Compare o fundo giratório que muda de cor no menu principal com os elementos aparentemente semelhantes da seleção de personagens e do marcador de tempo das lutas. Compare o caminho de desenho, o modo de textura, as transformações, a mistura de cores e a profundidade antes de atribuir os três casos à mesma causa.
- A [issue #12](https://github.com/Tel-BR/kof-xi-recomp/issues/12) pode avançar em paralelo com essa investigação.
- Segundo o mantenedor, os logos SNK e ADK da abertura aparecem distorcidos e abaixo da posição esperada. Acompanhe a abertura na [issue #14](https://github.com/Tel-BR/kof-xi-recomp/issues/14).
- Com áudio habilitado, a saída é intermitente. Cerca de 9,5 dos 12 segundos de menu parado ficaram praticamente silenciosos na fila de áudio do runtime. A música contínua e os efeitos sonoros ainda estão pendentes na [issue #15](https://github.com/Tel-BR/kof-xi-recomp/issues/15).
