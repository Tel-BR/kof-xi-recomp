# The rotating layer: root cause and fix (issue #12)

The main menu, the character select screen and the fight timer share a "rotating layer": 3D geometry projected by the game (the menu's emblem fan) and 2D sprites rotated around a pivot (the menu emblem, the select-screen rings). In the GPU build these elements were missing, sat in the wrong place or broke into fragments. Three runtime defects caused this. None of them was in the renderer.

1. **The `sceVu0MulMatrix` HLE multiplied in the wrong order.** The game's own routine loads its first matrix into VF4–VF7 and runs the VMULA/VMADD loop over the rows of the second, so the result is `second · first`. The runtime's replacement computed `first · second`. The SDK composes world, view and screen matrices with this call, so every combined matrix lost the view distance from the projected w. Q exploded and the clip test rejected the whole layer.
2. **The stale generated code tested sign branches on 32 bits.** On the R5900, BLTZ, BGEZ, BLEZ and BGTZ test the whole 64-bit register. The compiled `src/runner` came from an older recompiler that tested only the low 32 bits. libgcc's software `double` addition, which the game uses to round every rotated sprite corner, then missed a negative 64-bit mantissa difference. Corners more than about 128 px left of or above their pivot moved 255 px.
3. **The stale generated code did not update the VU0 flags.** The projection's clip test reads the sticky sign and zero flags after two VSUBs; the old output never set them. A VU0 context restore could also reload VF0, which the hardware keeps at (0,0,0,1).

The current PS2Recomp-Fixer generator already handled 2 and 3 except the LQC2 case. The fix has three parts:

- A runtime and generator patch, [`ps2recomp-fixer-libvu0-matrix-and-vf0.patch`](../../../../tools/runtime/patches/ps2recomp-fixer-libvu0-matrix-and-vf0.patch). It corrects MulMatrix's operand order and makes Normalize and CameraMatrix use the xyz length with w = 0, as the original does. It also makes the generator ignore LQC2 to VF0. Each change has a test that failed before the fix.
- [`upgrade_stale_runner.py`](../../../../tools/runtime/upgrade_stale_runner.py), which applies the generator's rules to the already-generated sources. It is keyed on each instruction's disassembly comment and is idempotent. On this game it changed 2,963 sign branches in 1,946 files, added 78 flag updates and dropped 1 LQC2 to VF0.
- [`closed_loop.py`](../../../../tools/runtime/closed_loop.py), which promotes the keyboard probe to tracked tooling. It adds the `MODE_VISIBLE` milestone for the screen after ARCADE PLAY. That screen already renders since the scratchpad DMA fix (`2d655ad`).

Evidence: after the fix, the menu's 3D batches match the PCSX2 reference. The decal batch is identical, the 1008-vertex batch is within 1 px, and the depth band is the same. The select-screen rings and the menu emblem are in the reference positions. The run log is in [`docs/agents/menu-input-loop.md`](../../../agents/menu-input-loop.md). Counts, addresses and outcomes only; captures stay in `private/`.

Still open: the palette phase (blue versus lime) needs a same-moment comparison, and the fight timer has not been checked by a run yet. Other generator fixes that the stale output lacks, such as VDIV by zero and quadword address alignment, were not applied.

---

# A camada giratória: causa raiz e correção (issue #12)

O menu principal, a seleção de personagens e o marcador de tempo das lutas compartilham uma "camada giratória": geometria 3D projetada pelo jogo (o leque do emblema do menu) e sprites 2D girados em torno de um pivô (o emblema do menu e os anéis da seleção). Na build GPU, esses elementos sumiam, apareciam fora do lugar ou se partiam em fragmentos. A causa foram três defeitos do runtime, nenhum deles no renderizador.

1. **A HLE de `sceVu0MulMatrix` multiplicava na ordem errada.** A rotina original do jogo carrega a primeira matriz em VF4–VF7 e percorre as linhas da segunda com VMULA/VMADD, então o resultado é `segunda · primeira`. A substituta do runtime calculava `primeira · segunda`. O SDK compõe as matrizes de mundo, câmera e tela com essa chamada, então toda matriz combinada perdia a distância da câmera no w projetado. O Q explodia e o teste de recorte descartava a camada inteira.
2. **O código gerado antigo testava desvios de sinal em 32 bits.** No R5900, BLTZ, BGEZ, BLEZ e BGTZ testam o registrador inteiro de 64 bits. O `src/runner` compilado veio de um recompilador mais antigo, que olhava só os 32 bits baixos. A soma de `double` por software da libgcc, que o jogo usa para arredondar cada canto de sprite girado, deixava então de ver uma diferença de mantissas negativa em 64 bits. Cantos a mais de ~128 px à esquerda ou acima do pivô andavam 255 px.
3. **O código gerado antigo não atualizava as flags do VU0.** O teste de recorte da projeção lê as flags acumuladas de sinal e de zero depois de dois VSUB, e o código antigo nunca as ligava. Além disso, a restauração de contexto do VU0 podia recarregar VF0, que no hardware é fixo em (0,0,0,1).

O gerador atual do PS2Recomp-Fixer já tratava os itens 2 e 3, menos o caso do LQC2. A correção tem três partes:

- Um patch do runtime e do gerador, [`ps2recomp-fixer-libvu0-matrix-and-vf0.patch`](../../../../tools/runtime/patches/ps2recomp-fixer-libvu0-matrix-and-vf0.patch). Ele corrige a ordem da MulMatrix e faz Normalize e CameraMatrix usarem o comprimento de xyz com w = 0, como o original. Também faz o gerador ignorar LQC2 para VF0. Cada mudança tem um teste que falhava antes da correção.
- O [`upgrade_stale_runner.py`](../../../../tools/runtime/upgrade_stale_runner.py), que aplica as regras do gerador ao código já gerado. Ele se guia pelo comentário de desmontagem de cada instrução e pode rodar de novo sem efeito. Neste jogo, mudou 2.963 desvios de sinal em 1.946 arquivos, acrescentou 78 atualizações de flags e removeu 1 LQC2 para VF0.
- O [`closed_loop.py`](../../../../tools/runtime/closed_loop.py), que promove a sonda de teclado a ferramenta versionada. Ele acrescenta o marco `MODE_VISIBLE` para a tela que vem depois do ARCADE PLAY. Essa tela já aparece desde a correção do DMA da scratchpad (`2d655ad`).

Evidência: depois da correção, os lotes 3D do menu batem com a referência do PCSX2. O lote decal é idêntico, o lote de 1008 vértices fica a menos de 1 px e a faixa de profundidade é a mesma. Os anéis da seleção e o emblema do menu ficam nas posições da referência. O registro das execuções está em [`docs/agents/menu-input-loop.md`](../../../agents/menu-input-loop.md). O texto traz só contagens, endereços e resultados; as capturas ficam em `private/`.

Ainda em aberto: a fase da paleta (azul contra verde-limão) precisa de uma comparação no mesmo instante, e o marcador de tempo das lutas ainda não foi conferido numa execução. Outras correções do gerador que faltam ao código antigo, como VDIV por zero e alinhamento de endereços de quadword, não foram aplicadas.
