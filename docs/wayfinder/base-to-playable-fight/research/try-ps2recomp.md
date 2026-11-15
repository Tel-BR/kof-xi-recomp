# PS2Recomp on the PS2 executable / O PS2Recomp no executável do PS2

_Findings for [Try PS2Recomp on the PS2 executable](../tickets/13-try-ps2recomp.md). English first, then Brazilian Portuguese. Only counts, outcomes, tool versions and address ranges are recorded; no disassembly, generated code, screenshots or game data. Measured on 2026-11-15 on the owner's machine (Windows 11, x64, 16 threads). Everything the run produced (the extracted ELF and disc files, the TOML configs, ~110 MB of generated C++, logs, the build) stayed in `private/` (git-ignored)._

_Resultado do ticket. Inglês primeiro, português depois. Só contagens, resultados, versões e faixas de endereço; nada de desmontagem, código gerado, capturas de tela ou dados do jogo. Tudo o que a execução produziu ficou em `private/`, que o git ignora._

## Setup

- **PS2Recomp:** `ran-j/PS2Recomp` at commit `e5636981a1c9de368f6b71e819c3dc188dfedbf4` (2026-10-22, "GIF: treat FLG=3 like IMAGE everywhere a GIFtag is parsed (#384)").
- **Input:** `SLUS_216.87` from the owner's US disc (2,037,464 bytes, SHA-1 `133f8c56283f0e255be995e894a3a7e6fe0c7b24`, the executable that matches Redump per [identify-disc-dumps.md](identify-disc-dumps.md)).
- **Function discovery:** the analyzer's built-in path (JAL scan plus the embedded SCE SDK signature database). The README's preferred path for stripped retail games is a Ghidra export; Ghidra is not installed on this machine, so that path was **not** tried.
- **Compiler:** clang 22 targeting MinGW (the machine's only C++ toolchain), Release, Ninja. PS2Recomp is tested mainly with MSVC, which is not installed. Four small local changes were needed, none in the recompiler or in the generated code:
  1. `-Wl,--allow-multiple-definition`: raylib's `CloseWindow`/`ShowCursor` collide with MinGW's `user32` import library.
  2. `-I` on the generated-code folder: generated files include their own headers with `<...>`, which only MSVC resolves from the file's folder.
  3. `-msse4.1`: generated code uses an SSE4.1 intrinsic for VU0 macro and MMI operations; MSVC does not need the flag, clang does.
  4. A 6-line hook in the runner's `main.cpp` reading a `PS2X_CD_IMAGE` environment variable: the runtime can read a disc image, but the stock runner never sets one.

## Results

| Stage | Outcome |
|---|---|
| Analyzer | **3,458 functions** from the JAL scan, 0 symbols. The SDK database matched 552 library functions (named 360 already found, added 192 more for classification). The recompiler, reading the generated TOML, emitted the same 3,458 functions. 245 functions bound to runtime stubs, 285 library-like functions without a runtime handler, 36 instruction patches, 9 jump tables. 678 "unknown MMI function" notices (30 distinct sub-opcodes), all from the data tail (none once it is skipped) |
| Coverage | 3,434 function starts fall in the code range (`0x100008`–`0x280830`, ~1.5 MB); the other 24 sit in the data tail |
| Recompiler, as is | Completes. **12,769 unhandled instructions**, **all inside 18 "functions" in the data tail** (`0x280830`–`0x2F1400`): data decoded as code (opcode, SPECIAL, COP0, FPU, MMI and COP2 "instructions" that are not real code). Those 18 make 27.7 MB of the 110 MB of generated C++. 390 control-flow warnings (unresolved `JR`/`JALR`, given a runtime fallback). **Zero unhandled instructions in the real code**, including every MMI and VU0 macro instruction |
| Build, as is | 110 of 111 compilation units build with **0 errors**. The unit that holds the largest data-as-code "function" (~100,000 lines in one function) was still compiling after **60 minutes** at `-O3` and was stopped |
| Recompiler, second run | Same config with only those 18 tail entries listed in `skip`: 0 unhandled instructions, 364 control-flow warnings |
| Build, second run | **Compiles and links with 0 errors** in about 5 minutes (51 MB executable) |
| Runtime without a disc image | Boots: loads the 7 IOP modules, the CRI ADX driver initialises, the GS receives draws. Then loops on 26,247 failed raw-sector disc reads (the game reads by sector number, not by file name) |
| Runtime with the disc image | Boots and **drives the GS for about 8 seconds** (~480 runtime ticks, 862 DMA/GIF transfers, 439 frames uploaded at 640×448). Then the main thread makes an **indirect call (`JALR`) to `0x1FB188`, an address the analyzer never found as a function start**, and stays there: no more DMA, the picture freezes, no crash, no menu reached in the 120 s run. What was on screen during those 8 seconds was not checked by eye; it fits the boot sequence |

## Function discovery is the real blocker

The stall is the symptom of a gap the analyzer cannot see on this executable. A heuristic scan (counts only) of the loaded image:

- **964** distinct code addresses are stored as pointers somewhere in the image and land on a stack-frame prologue; **921** of them (96%) are **not** among the discovered functions. The JAL scan only finds functions that are called directly; functions reached only through pointers (callback tables, state machines, C++-style dispatch, which CodeWarrior code uses heavily) are missed.
- **4,470** stack-frame prologues exist in the code range; **1,589** are not at a discovered start. Not every prologue is a function start, so this is an upper bound, but it suggests the true count is **somewhere around 5,000 functions**, of which the analyzer found about two-thirds.
- The stall target itself is not a stack-frame prologue and is not stored as a plain pointer: likely a leaf function whose address is computed or loaded from a structure. Pointer scans alone will not find all of these.

So, for [Decide the recompiler](../tickets/15-decide-recompiler.md): the instruction translation is not the problem (all real code translates, and the output compiles), and neither is the toolchain (four small MinGW workarounds). What decides how far PS2Recomp gets is **getting complete function boundaries**: a Ghidra export (the path the README recommends and this run did not try), a CodeWarrior-aware boundary pass, or both, plus a clean cut between code and data so the 18 data-tail entries never reach the recompiler.

## PT-BR

- **Montagem:** PS2Recomp no commit `e5636981…` (22/10/2026). Executável americano do disco do dono. Descoberta de funções pelo caminho embutido do analisador (varredura de `JAL` mais o banco de assinaturas do SDK da Sony); o caminho recomendado para jogos sem símbolos, exportar do Ghidra, **não** foi testado porque o Ghidra não está instalado. Compilado com clang (MinGW), já que o MSVC não está na máquina; foram precisos quatro ajustes locais pequenos (conflito de nomes entre raylib e Windows, caminho de include, opção SSE4.1, e um gancho de 6 linhas para indicar a imagem do disco), nenhum no recompilador nem no código gerado.
- **Analisador:** 3.458 funções pela varredura; o banco do SDK reconheceu 552 funções de biblioteca (deu nome a 360 já achadas e acrescentou 192 para classificação). 9 tabelas de salto, 36 patches.
- **Recompilador como está:** termina, com 12.769 instruções não tratadas, **todas dentro de 18 "funções" no fim da imagem, que na verdade são dados lidos como código**. No código real, **zero** instruções não tratadas, incluindo todas as MMI e as instruções vetoriais da VU0.
- **Compilação como está:** 110 de 111 unidades compilam sem erro; a que contém a maior "função" de dados (~100 mil linhas) passou de 60 minutos e foi interrompida. **Pulando só essas 18 entradas, tudo compila e linka sem erro** em uns 5 minutos.
- **Execução:** sem a imagem do disco, o jogo inicia mas trava pedindo setores do disco. Com a imagem, **inicia e desenha por uns 8 segundos** (módulos do IOP carregados, driver de áudio ADX iniciado, 439 quadros enviados); depois faz uma chamada indireta para um endereço que o analisador nunca reconheceu como função e fica parado ali. Não fecha, não chega a menu nenhum em 120 s.
- **Conclusão para o ticket 15:** traduzir instruções e compilar não é o problema. O que trava é **achar todas as funções**: das 964 funções que o executável guarda como ponteiros, 921 (96%) não foram achadas, e a estimativa é de umas 5.000 funções no total, das quais o analisador achou cerca de dois terços. O caminho é uma lista de funções completa (exportação do Ghidra, que esta rodada não testou, ou uma passada que entenda o padrão do CodeWarrior) e um corte limpo entre código e dados.
