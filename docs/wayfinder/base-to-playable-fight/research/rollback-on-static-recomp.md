# Research: how static recomps can support rollback netplay

Ticket: "Survey how static recomps can support rollback netplay."
Researched: 2026-11-11. Every claim below is tied to a source in the **Sources** list. Where a statement is this note's own inference or arithmetic, it says so. No game data (code, assets, addresses or dumps of *The King of Fighters XI*) appears in this document.

---

## Resumo em português

- **O que é rollback, em uma frase:** cada jogador joga na hora com o próprio controle; quando chega o comando atrasado do adversário, o jogo "volta no tempo" alguns quadros, refaz esses quadros com o comando certo e segue. Para isso o jogo precisa **salvar e carregar o estado inteiro da luta a cada quadro (60 vezes por segundo)** e precisa ser **100% previsível**: os mesmos comandos têm de dar o mesmo resultado, bit a bit, nos dois computadores.
- **Isso já funciona em emuladores e ports:** o Fightcade (FBNeo), o Flycast (que roda Dreamcast/Atomiswave e tem rollback via GGPO), o RetroArch, o Slippi (Melee no Dolphin) e o port nativo de *Street Fighter III: 3rd Strike* (3SX) usam essa técnica. Também já existe pelo menos uma recompilação estática com rollback funcionando (psxrecomp, de PS1), ainda marcada como experimental.
- **A recompilação estática ajuda:** como o código traduzido trabalha numa "RAM emulada" (um bloco de memória) mais um conjunto de registradores, salvar o estado é basicamente copiar memória. Mas não basta copiar a RAM: também entram o estado do chip de vídeo, do áudio, de temporizadores, de leituras de disco em andamento e de qualquer cache do lado do PC.
- **Custo:** copiar a memória inteira a cada quadro custa caro. Medimos ~2,4 ms para o tamanho do Atomiswave e ~4 ms para o tamanho do PS2 numa máquina de nuvem modesta; num rollback de 8 quadros isso estoura o orçamento de 16,7 ms por quadro. Os projetos que funcionam resolvem isso copiando **só as páginas de memória que mudaram**, ou só as regiões que importam.
- **O maior risco é a "imprevisibilidade" (dessincronização):** contas com números decimais (ponto flutuante) podem dar resultados levemente diferentes conforme o compilador, as opções de compilação, o processador e até a biblioteca de matemática do Windows (que escolhe outro algoritmo se o processador tiver uma instrução chamada FMA3). O PS2 tem um jeito próprio, fora do padrão, de fazer essas contas; o Dreamcast tem modos de precisão e de arredondamento que mudam em tempo de execução.
- **Outros riscos:** usar o relógio do PC dentro da lógica do jogo, threads (linhas de execução paralelas) rodando em ordem diferente em cada máquina, memória não inicializada e leituras de disco cujo tempo depende do PC de cada jogador.
- **Bibliotecas prontas:** GGPO (MIT, referência histórica, parado desde 2019), GekkoNet (BSD-2, ativo, usado pelo 3SX e por um emulador de N64), GGRS (Rust, MIT/Apache, ativo), backroll (Rust, ISC, beta parado desde 2022). Todas exigem as mesmas três coisas do jogo: salvar, carregar e avançar um quadro.
- **O que decidir cedo (sem implementar netplay agora):** guardar todo o estado do jogo num lugar só e com tamanho conhecido; ter um "ponto de quadro" bem definido onde salvar/carregar; ler o controle por uma única porta de entrada; separar lógica de desenho/som; fixar as opções de compilação de ponto flutuante; proibir relógio do PC e aleatoriedade do PC na lógica; e criar desde já um teste automático que "volta no tempo e refaz" para detectar dessincronização.

---

## 1. What rollback requires of a game

GGPO's developer guide is the reference contract that later libraries (GGRS, GekkoNet, backroll) follow. Its requirements:

| Requirement | GGPO wording / mechanism |
|---|---|
| Full, serializable state | "The game state must be fully encapsulated and serializable." `save_game_state` must "create a buffer containing enough information to restore the current state of the game"; `load_game_state` must "restore the game state from a previously saved buffer." |
| Determinism | "The game simulation must be fully deterministic." |
| Run a frame without presenting it | The engine must be able to "execute a single simulation frame without rendering the result of that frame"; GGPO "will call your advance frame callback many times during a rollback." |
| Input decoupling | Before each frame the game calls `ggpo_synchronize_input` to get the inputs it must use (Flycast's copy of the callback contract states this explicitly). |
| Separate side effects | Keep rendering out of the state update so rollbacks don't trigger effects or sounds; "your game state should be determined solely by the inputs." |
| Fixed time step | "advance state by a fixed quantum per frame." |
| No wall-clock in state | "The time on two computers or game consoles is almost never in sync." |
| Hidden state | Static/hidden variables must be tracked down and made saveable; pointers must be rebased or stored as base+offset. |
| RNG | Same seed on both sides at frame 0, RNG state inside the saved state. |
| Desync testing | `ggpo_start_synctest`: a single-player session that rolls back every frame and compares checksums; recommended to run "continuously" during development. |

**How often state is saved.** GGPO saves after *every* frame: `Sync::IncrementFrame()` calls `SaveCurrentFrame()`, and during a rollback `Sync::AdjustSimulation` loads the old frame and then calls `advance_frame` once per frame to catch up (each of which saves again). The prediction window is capped at `GGPO_MAX_PREDICTION_FRAMES = 8`, and the ring holds `MAX_PREDICTION_FRAMES + 2` saved frames.

**Worst-case frame budget (inference from the above).** At 60 fps a frame is 16.67 ms. A rollback of *N* frames inside one displayed frame costs roughly: 1 load + (N+1) simulated frames + (N+1) saves. With N up to 8, both the simulation and the save must be far cheaper than one frame.

**Libretro's framing of the same requirements.** RetroArch netplay is "guaranteed" to stay in sync only if "The core is deterministic", the only inputs are pads/sticks, and core and content are identical on both sides. libretro also defines savestate *contexts*: `RETRO_SAVESTATE_CONTEXT_RUNAHEAD_SAME_INSTANCE` is loaded "within the same session, address space, and binary", so "internal pointers to code or data are acceptable" and the code "should be fast"; `RETRO_SAVESTATE_CONTEXT_ROLLBACK_NETPLAY` "Must not contain pointers" because it may be loaded by another binary/device. A core can flag `RETRO_SERIALIZATION_QUIRK_INCOMPLETE` when its state is fine for normal saves "but should not be relied upon for frame-sensitive frontend features such as netplay". The distinction matters for a recomp: rollback snapshots never leave the process, so they may contain host pointers; only spectator/late-join transfer needs a portable format.

---

## 2. How emulators and ports have achieved it

### 2.1 FBNeo in Fightcade (emulator, full savestate per frame)

- Fightcade's FBNeo fork (`fightcadeorg/fightcade-fbneo`) integrates GGPO in `src/burner/win32/fbn_ggpo.cpp` and links a prebuilt `src/dep/ggpo/lib/ggponet.lib`.
- `ggpo_save_game_state_callback` simply runs the emulator's normal savestate walker: `BurnAreaScan(ACB_FULLSCANL | ACB_READ, NULL)` into a static 16 MiB buffer; load runs the same scan with `ACB_WRITE`. The checksum routine is compiled only in debug builds ("Ignore checksums in release builds for now. It takes a while.").
- Lesson: for small arcade boards (a few MiB of state) a full serialize every frame is affordable, and reusing the existing savestate code is the simplest path.

### 2.2 Flycast (Dreamcast / NAOMI / Atomiswave, GGPO with dirty-page deltas)

Directly relevant because the Dreamcast/Atomiswave base candidate is the same hardware family.

- Flycast vendors GGPO (`core/deps/ggpo`) and implements the callbacks in `core/network/ggpo.cpp`. Flycast is GPL-2.0-or-later.
- **Platform sizes** in `core/emulator.cpp`: Atomiswave = 16 MB RAM, 8 MB VRAM, 2 MB AICA (sound) RAM; Dreamcast = 16 MB / 8 MB / 2 MB; NAOMI = 32 / 16 / 8 MB.
- **Snapshot design.** `save_game_state` asserts the SH-4 is not running (`verify(!emu.getSh4Executor()->IsCpuRunning())`), i.e. it saves only at a frame boundary. It serializes the non-RAM machine state with `dc_serialize` in "rollback" mode into a 10 MB (20 MB for NAOMI) buffer (`// TODO this is way too much memory`). The big memories (main RAM, VRAM, AICA RAM, Elan RAM) are **not** copied whole: the `memwatch` module write-protects them, and on the first write to a page per frame it saves that page's old contents. `save_game_state` stores the per-frame delta (`deltaStates[frame - 1]`), and `load_game_state` walks the deltas backwards from the last saved frame, `memcpy`-ing old pages back, then deserializes the rest.
- **Side effects during resimulation.** `advance_frame` sets `settings.aica.muteAudio = true` and `rend_enable_renderer(false)`, runs one frame, then re-enables both. `load_game_state` calls `rend_start_rollback()` / `rend_allow_rollback()` so the renderer can discard work. Audio *emulation* keeps running (it is part of the state); only output is muted.
- **Sync testing.** A compile-time `SYNC_TEST` mode starts `ggpo_start_synctest`, hashes states with XXH3 and verifies that pages saved for frame N-1 match on re-simulation. There is also a `// FIXME dynarecs` note in the load path.
- **Host FP state.** Flycast maps the guest SH-4 `FPSCR.RM` (round-to-nearest vs. round-to-zero) and `FPSCR.DN` (denormals as zero) onto the host FPU control register on every FPSCR change (`setHostRoundingMode`, with a comment "Correct rounding is required by some games").

### 2.3 RetroArch (run-ahead and rollback netplay)

- **Run-ahead** relies on savestates that "need to be clean and fast enough". Single-instance mode disables audio and video, runs and saves frames, then runs the visible frame and loads state, all in RAM. Two-instance mode exists because many cores "do not leave audio emulation in a clean state after loading state, so you would get buzzing".
- **Netplay** "invisibly rewind[s] to the last time they were consistent, replay[s] with the new input", serializes state every frame into a ring, and requires a deterministic core with serialization support.

### 2.4 Dolphin and Slippi

- Mainline Dolphin netplay is **lockstep with an input buffer**, not rollback ("1 pad buffer per 15 ms"). It needs "an identical emulated environment on all PCs" and warns that the x86-64 and AArch64 JITs "can produce very slightly different code which is enough to trip Dolphin's desync detection".
- **Slippi** (Dolphin fork for *Super Smash Bros. Melee*) added rollback in June 2020. Its `SlippiSavestate.cpp` does **not** use Dolphin's full savestate: it copies a hand-picked list of guest memory ranges (data/BSS sections and heap), explicitly **excludes** sound-related ranges, and supports "preserve blocks" that keep their current contents across a load. The full-hardware `DoState` calls are commented out. This works because the save/load is triggered from a fixed point inside the game loop, so CPU registers and hardware state at that point are known to be equivalent.
- Lesson: a **game-aware, partial snapshot** taken at a known point in the frame can be much smaller than a full machine state, at the cost of per-game reverse engineering.

### 2.5 3SX (decompilation-based native port with GekkoNet)

- 3SX is a native port of *Street Fighter III: 3rd Strike* built on the matching PS2 decompilation `3s-decomp`; its README says it "is neither a recomp, nor emulation" and that it "leverages GekkoNet to provide a fast, modern, cross-platform rollback netcode implementation". License: AGPL-3.0.
- State is an explicit C struct (`src/platform/netplay/game_state.h`) listing the game's globals; save is `SDL_memcpy` of a fixed `sizeof(State)`. Rendering is suppressed during resimulation (`advance_game(event, drawing_allowed && !rolling_back)`).
- Desync tooling: GekkoNet `desync_detection = true`, a stress session (`netplay_stress.c`) and a state diff tool (`tools/compare_states.py`). For debug dumps it zeroes pointer fields first (`clean_work_pointers`) so dumps are comparable.
- Lesson: when the game's globals are known (decomp), the state can be tiny and exact. A static recomp has no such list, so it falls back to copying the guest memory images instead.

### 2.6 psxrecomp (static recompiler with working rollback)

This is the closest precedent: a static recompiler (MIPS R3000A to C) with an experimental rollback mode in at least one shipped title (*Battle Arena Toshinden*: "two-player rollback netplay").

- **Runtime model.** Generated C is linked into a runtime that owns "the 2 MB main RAM, scratchpad, BIOS ROM, and MMIO regions" and simulates GPU, DMA, timers, CD-ROM, MDEC, SPU, GTE and interrupts; guest threads run on "a cooperative-thread scheduler on host fibers (Win32 Fibers / POSIX ucontext)".
- **Mode.** "Default match mode for opted-in titles is rollback (GGPO-style tip prediction + resimulation), with delay-sync still available". "Savestate / snapshot rings and AV digests keep peers aligned".
- **What a snapshot holds and costs.** The live ring stores raw `boot_state` of "RAM+VRAM+SPU" (zlib compression was "the live FPS tax"), CPU registers, COP0/GTE, clocks/timers, CD-ROM/MDEC/DMA/SIO state; "raw ring ≈ 3.5 MiB × depth". Live snapshots are rate-limited to every `PSX_NET_SNAP_INTERVAL` ticks (default 16), while resimulation snaps every tick. "Skipping VRAM on live snaps is unsafe for rewind."
- **Where to snapshot.** "Snap PC must be `psx_is_dispatchable`": the snapshot must be taken at an IRQ or basic-block edge from which the runtime can resume, not at an arbitrary point.
- **Rendering split.** For netplay a 1x software rasterizer is the "headless authority" for "Deterministic VRAM / digests / rollback snaps", while OpenGL renders at the player's chosen resolution "for window present quality only". Peers can use different graphics settings "without desyncing the sim".
- **Determinism tooling and findings.** A self-check mode (`PSX_RB_SELFCHECK=1`) snaps, records inputs, then "rewind[s] and resim[s] the window twice from the same snap" and reports per-part divergence. Fixes it found include VBlank-phase restore, clearing interpreter load-delay state, clearing "sticky ... overlay validation memos ... on RAM restore", and auditing "non-deterministic host clocks in sim path". Peers "must run the same bit-identical binary". Digest cost mattered: CRC over 2 MiB RAM plus 1 MiB VRAM on every resimulated tick caused stutter until it was trimmed (measured 3.78 ms to 0.76 ms for the RAM CRC after optimisation).
- **Licensing.** psxrecomp is PolyForm Noncommercial 1.0.0 (with additional permissions in `PERMISSIONS.md`). Its netcode is split into MIT-licensed libraries: `recomp-net` (transport/session; its main-branch README still describes v0.1 as "delay-sync" and says it does "not implement rollback", while psxrecomp pins a rollback-capable commit) and `retcomm-rbengine` ("the offline rollback core ... `snap_ring`: tick-keyed opaque snapshot ring").

### 2.7 Other static recompilers (no rollback found)

- **N64Recomp**: generated functions have the signature `void (uint8_t* rdram, recomp_context* ctx)`; memory access macros index into the `rdram` block, and `recomp_context` holds the 32 GPRs, 32 FPRs, `hi`/`lo`, `status_reg` and `mips3_float_mode`. Its runtime (N64ModernRuntime/ultramodern) runs each guest OS thread on its own `std::thread` (`context->host_thread = std::thread{_thread_func, ...}`). Neither README mentions savestates.
- **XenonRecomp**: "The CPU state is passed as an argument to every PPC function" plus a guest memory base pointer. It tracks FP state in the CPU struct and toggles denormal flushing per instruction because "The FPU expects denormalized numbers to remain unmodified, while VMX instructions always flush them." No savestates mentioned; no runtime provided.
- **PS2Recomp** (GPL-3.0, "Experimental", "many paths are stubbed"): translated code uses `ctx->` register fields and a runtime "Guest memory model and function dispatch table". No savestate support mentioned. It already emulates PS2 float semantics in software (see section 4.1).
- **RMG-K** (an N64 *emulator* fork, not a recomp) added two-player rollback for the whole N64 library in May 2026 on top of GekkoNet (secondary press source).

---

## 3. How a static recomp could snapshot state

### 3.1 Why it is "mostly a memcpy"

In the N64Recomp / XenonRecomp / PS2Recomp style, every translated function receives (a) a pointer to the emulated RAM block and (b) a CPU context struct. Guest data, including the guest stack, lives in that RAM block. So for the CPU side, a snapshot is "copy the RAM block(s) + copy the context struct(s)".

### 3.2 The catch: the host call stack and host threads

This is inference from how these recompilers translate calls, and it is the most important architectural point in this document:

- Static recompilers turn guest `jal` into native C calls ("Direct `jal` instructions become ordinary C function calls"), so **return addresses live on the host stack**, not in guest RAM. A snapshot taken in the middle of a call chain cannot be restored by copying guest RAM alone, because the host stack would not match.
- Runtimes put guest threads on host threads (ultramodern) or host fibers (psxrecomp). Each has its own native stack outside guest RAM.
- Known ways out:
  1. **Snapshot only at a canonical point** (for example the main loop's VSync wait), where every guest thread is parked at a known kernel call. Restoring guest RAM + contexts is then valid as long as each host thread/fiber is parked at the same point. This is what Slippi effectively does inside the game loop, and what Flycast enforces by saving only while the CPU is not running.
  2. **Resumable code**: let the runtime re-enter generated code at any dispatchable address (psxrecomp requires the "Snap PC" to be dispatchable).
  3. **Snapshot fiber stacks too**: because rollback states never leave the process (libretro's same-instance context allows "internal pointers"), fiber stacks allocated at fixed addresses could be copied with the rest. Not seen in a shipped project; listed as an option only.

### 3.3 What else must be captured

| Item | Why | Evidence |
|---|---|---|
| Guest main RAM, scratchpad, sub-CPU RAM (PS2 IOP 2 MB; DC/AW sound CPU RAM) | Game logic state | PCSX2 `MemoryTypes.h`; Flycast `emulator.cpp` |
| CPU contexts (GPR, FPR, HI/LO, FP control/status, COP0) | Resume point | N64Recomp `recomp_context`; psxrecomp digests GPR/COP0/GTE |
| Vector units (PS2 VU0 4 KB data + 4 KB micro; VU1 16 KB + 16 KB) | Micro-programs and data persist between frames | PCSX2 `VUmicro.h` |
| Video memory and GPU registers (PS2 GS 4 MB; AW 8 MB VRAM) | Textures uploaded earlier are reused later; some games read video memory | PCSX2 `GSLocalMemory.h` (`m_vmsize = 1024*1024*4`); psxrecomp: "Skipping VRAM on live snaps is unsafe" |
| Sound RAM and sound-chip state (PS2 SPU2 2 MB; AW AICA 2 MB) | Game may poll voice status; dropping it causes audio glitches after a load | PCSX2 `_spu2mem[0x200000/2]`; RetroArch "buzzing" note; Slippi chose to *exclude* sound ranges instead |
| Timers, interrupt and VSync phase, cycle counters | Game logic timing | psxrecomp "VBlank-phase restore" fix |
| DMA channels and in-flight transfers | Transfers can span the save point | psxrecomp digests DMA |
| Disc/file I/O in progress, FMV/media position | Async reads finish at host-dependent times | psxrecomp `cdrom_resync_deadlines_after_restore`, "FMV / media paths use lockstep-friendly rules" |
| Host-side caches keyed on guest memory (texture caches, decoded overlays, dispatch memos) | Must be invalidated or restored after a load | Flycast `rend_start_rollback`; psxrecomp clears "overlay validation memos ... on RAM restore" |
| Runtime HLE state (kernel objects, semaphores, thread queues, pad/memory-card HLE) | Lives on the host side, not in guest RAM | GGPO "hidden state" tip; psxrecomp plugin profile must "exclude pointers, padding, rendering caches and local-only input state" |

### 3.4 Cost per frame at 60 fps

Measured for this note on a 2-vCPU cloud VM (Intel Xeon @ 2.30 GHz, `gcc -O2`, single thread). Treat as an order of magnitude; a desktop will differ.

| Snapshot size | Full `memcpy` | Simple 64-bit hash of same |
|---|---|---|
| 2 MiB (PS1 main RAM) | 0.17 ms | 0.31 ms |
| 26 MiB (Atomiswave RAM + VRAM + sound RAM) | 2.43 ms | 5.95 ms |
| ~40 MiB (PS2 EE 32 + IOP 2 + GS 4 + SPU2 2) | 4.15 ms | 9.22 ms |
| 64 MiB | 9.51 ms | 18.96 ms |

Arithmetic using GGPO's per-frame saving: a full-copy 8-frame rollback would spend ~9 x 4.15 ≈ 37 ms (PS2) or ~9 x 2.43 ≈ 22 ms (Atomiswave) on saving alone, above the 16.67 ms frame. So **full copies of the whole machine every frame do not fit**. Ways that shipped projects avoid this:

- **Dirty-page deltas** (Flycast `memwatch`: write-protect, copy the page on first write). On Windows, `VirtualAlloc(MEM_WRITE_WATCH)` + `GetWriteWatch` gives the list of written pages without fault handling. A static recomp has a third option: every guest store already goes through a macro (`MEM_W` etc.), so the recompiler could mark a dirty bit per page in software.
- **Region allow-lists** (Slippi: only game data/heap, exclude sound).
- **Snapshot interval** (psxrecomp: live snaps every 16 ticks, every tick only during resimulation).
- **No compression in the live ring** (psxrecomp found zlib too slow).
- **Cheap or periodic checksums** (FBNeo disables them in release; psxrecomp trimmed per-tick CRC work).

Simulation cost matters as much: psxrecomp measured guest frames of 7-29 ms in heavy scenes on its test host, which directly limits how many frames can be re-simulated per displayed frame.

---

## 4. Determinism risks

Rollback needs **peer-to-peer** determinism: both machines must compute the same bits. Hardware accuracy is a separate goal; an inaccurate but identical result does not desync, but an accurate result computed differently on two hosts does.

### 4.1 PS2 floating point (EE FPU and VUs)

- PS2 floats are not IEEE 754. PS2Recomp's runtime summarises the EE FPU / VU0-macro semantics: "no Inf, NaN or denormals"; "exponent 255 is an ordinary exponent, so 0x7F800000 is 2^128 and the largest value is 0x7FFFFFFF"; "exponent 0 is zero whatever the mantissa holds"; overflow "saturates to +-0x7FFFFFFF", underflow becomes ±0; "x/0 gives +-0x7FFFFFFF". It computes rare special cases in `double` and notes one host-dependent gap (tiny operands in ADD/SUB/MUL), "Checked against the hardware results in ps2autotests".
- PCSX2 defaults: the EE FPU and VU host control registers are set to denormals-are-zero + flush-to-zero + `FPRoundMode::ChopZero` (round toward zero); FPU division uses round-to-nearest. PCSX2 exposes clamping modes (`fpuOverflow`, `fpuExtraOverflow`, `fpuFullMode`, and VU equivalents) and per-game fixes such as `FpuMulHack` and `VuAddSubHack` ("requires VU addi opcode to be bit-accurate").
- PCSX2's 2006 blog: "Multiplying two numbers on the FPU, VU, and an x86 processor can give you 3 different results"; "the VUs don't support infinities" and clamp instead.
- Consequence for rollback (inference): whatever emulation policy is chosen (host SSE + clamping, or software PS2-float), it must be the same code path on every peer, and any change to the rounding mode must be applied identically. Host MXCSR state is per thread, so a worker thread with a different rounding mode is a desync source.

### 4.2 SH-4 floating point (Dreamcast / Atomiswave)

- The SH-4 `FPSCR` selects single vs. double precision (`PR`), rounding (`RM`: nearest or zero) and denormal handling (`DN`), and the game can change them at run time. Flycast checks `fpscr.PR` on every FP op and reprograms the host FPU when `RM`/`DN` change.
- Special instructions: `FSCA` (sine/cosine) is implemented in Flycast by a lookup table of hardware results (`fsca-table.h`), with a `NATIVE_FSCA` alternative using `sinf`/`cosf`; `FSRRA` is computed as `1.f / sqrtf(x)`; `FIPR` accumulates in `double`. Any of these computed through host libm or different precision on each peer is a desync risk; a table is deterministic by construction.

### 4.3 Host compiler and runtime

- **MSVC:** default is `/fp:precise`. Since Visual Studio 2022, "Floating-point contractions aren't generated by default under `/fp:precise`"; earlier versions could generate them. `/fp:fast` "may reorder code even if such transformations result in observably different rounding behavior" and enables `/fp:contract`. Under `/fp:precise` the compiler "assumes the floating-point environment isn't accessed or modified", so code that changes rounding modes needs `/fp:strict` or `#pragma fenv_access`; otherwise the compiler "may not honor requested changes".
- **MSVC CRT math:** on x64, "the CRT startup code detects whether the CPU supports FMA3 instructions, and enables or disables the FMA3 implementations"; "Differences may also be observable between computers that do or don't support FMA3." `_set_FMA3_enable(0)` turns this off. This is a concrete cross-machine desync source for any `sinf`/`cosf`/`powf` in the simulation path.
- **GCC:** `-ffp-contract` defaults to `off` only "for C in a standards compliant mode (`-std=c11` or similar)" and to `fast` otherwise, which forms FMAs "if the target has native support for them".
- **Clang:** default `-ffp-model=precise` keeps `-ffp-contract=on` (fusion within one statement); `-ffp-model=strict` disables contractions.
- **x87 vs SSE:** GCC's x86-64 default is SSE; x87 is the default only for non-Darwin 32-bit targets, where "temporary results are computed in 80-bit precision ... resulting in slightly different results". A 64-bit-only build avoids this.
- **Same binary:** psxrecomp requires "the same bit-identical binary" on both peers; Dolphin warns that different JIT back-ends trip desync detection. A practical consequence: Windows-only peers with one official build are easier than mixed compilers or mixed x86-64/ARM64.

### 4.4 Other sources

- **Uninitialized memory and padding.** Guest RAM is initialised by the runtime, but host-side runtime structs can carry garbage or padding into checksums. 3SX zeroes pointer fields before dumping; psxrecomp's mod-state callback must "exclude pointers, padding".
- **Threading.** Preemptive host threads running guest threads in parallel produce host-dependent interleavings. Existing runtimes serialise guest execution: ultramodern runs one thread and blocks the others (`run_next_thread_and_wait`); psxrecomp uses cooperative fibers. Any host worker thread (audio mixing, async file loading, shader compilation) must not write simulation state.
- **Timing-dependent code.** Games that count elapsed VBlanks, poll timers, or wait on DMA/GS/CD completion will behave differently if those events are driven by host time. GGPO: fixed time quantum per frame; psxrecomp fixed "VBlank-phase restore" and audited host clocks.
- **RNG and clocks.** Game RNG state in guest RAM is captured automatically. Seeds taken from host sources (real-time clock, `rand()`, timestamps) must be replaced with agreed values in netplay.
- **Identical inputs and content.** Same disc image/ROM, same save/memory-card data, same settings (Dolphin checksums files and syncs saves; psxrecomp broadcasts the host's memory cards; libretro requires identical content).

---

## 5. Rollback libraries

| Library | Language / API | License | Status (last commit seen) | Notes |
|---|---|---|---|---|
| GGPO (`pond3r/ggpo`) | C++ with C API, callbacks | MIT | 2019-11-07; build documented for Windows/VS2019 only | Reference design; `MAX_PREDICTION_FRAMES 8`; synctest mode. Flycast ships its own vendored copy. |
| GekkoNet (`HeatXD/GekkoNet`) | C/C++ (C API, C++20 to build), event-based | BSD-2-Clause | Active, 2026-11-02 | Online, local, spectator, replay and **stress** sessions; desync detection "Only when limited saving is disabled for now". Fixed `state_size` in `GekkoConfig`. Used by 3SX, RMG-K, bsnes netplay. |
| GGRS (`gschup/ggrs`) | Rust, request-list API | MIT or Apache-2.0 | Active, 2026-10-19; tag v0.13.0 | "fairly stable"; P2P, spectator, sync-test. No C API stated, so C++ use would need an FFI layer. |
| backroll-rs | Rust | ISC | 2022-11-14; "early beta" | Pure-Rust GGPO reimplementation; appears inactive. |
| recomp-net + retcomm-rbengine | C11 | MIT | Active (2026) | Built for recomp runtimes (psxrecomp). Main-branch README is delay-sync v0.1; rollback lives on a branch used by psxrecomp. Young. |

All of these impose the same three callbacks on the game: save, load, advance one frame with given inputs. Choosing a library can be deferred if those three operations exist and are deterministic.

---

## 6. Architectural requirements to lock in early (facts and options, not a decision)

These keep rollback possible later without implementing netplay now. Each item says what the precedent shows and which options exist.

1. **Single owner for all simulation state.** All guest memories, CPU/VU contexts and hardware/HLE state live in one arena (or a fixed list of arenas) owned by the runtime, with no simulation state in host globals scattered across modules. *Options:* one contiguous arena (simplest copy, enables page tracking) vs. a registry of named regions (like FBNeo's `BurnAreaScan`). GekkoNet assumes a fixed `state_size`; GGPO allows variable length.
2. **A defined frame boundary.** One place in the main loop (for example the VSync wait) where the simulation is quiescent, all guest threads are parked and save/load is legal. *Options:* canonical-point snapshots (sec. 3.2 option 1), resumable dispatch (option 2), or fiber-stack capture (option 3). This choice interacts with how the recompiler maps calls and threads, so it is the one to settle earliest.
3. **Deterministic guest scheduling.** Guest threads never run truly in parallel; switching depends only on guest state. *Options:* fibers/coroutines (psxrecomp), host threads with a baton (ultramodern).
4. **Single input entry point.** The controller read path (PS2 pad library via IOP, or Atomiswave/Dreamcast Maple bus) is replaced by one function that returns "the input for frame N", fed by local input now and by the rollback library later. Inputs are a small fixed-size blob per player.
5. **Simulation separated from presentation.** The runtime can run a frame with host rendering and audio output disabled while still updating guest-visible GPU/sound state. Host caches (textures, shaders, decoded overlays) can be invalidated after a load. *Options:* skip host draws during resimulation (Flycast, 3SX) vs. a separate authoritative low-cost renderer plus a presentation renderer (psxrecomp).
6. **Time comes only from the simulation.** VBlank, timers, DMA/GS/CD completion and any RTC are derived from simulated frame/cycle counters, never from host clocks. Disc reads complete on a deterministic schedule.
7. **Pinned floating-point policy.** Decide once how guest float semantics are emulated (PS2: clamping/round-to-zero/software PS2-float; SH-4: honour `PR`/`RM`/`DN`, table-based `FSCA`) and pin the host side: x64 only, no `/fp:fast` or `-ffast-math`, explicit contraction setting (`/fp:precise` on VS2022+ or `/fp:strict`; `-ffp-contract=off` on GCC/Clang), no AVX2/FMA codegen unless every peer runs the same binary, and no CRT transcendental functions in the simulation path (or `_set_FMA3_enable(0)`). If the runtime changes rounding modes, the build needs `fenv_access` semantics.
8. **No host randomness or uninitialised data in the simulation.** Zero-initialise runtime state; keep pointers out of anything hashed; agree on any seeds at session start.
9. **Snapshot API now, even offline.** `save(buf)`, `load(buf)`, `hash()` on the runtime from day one. This also gives savestates, rewind, run-ahead and replay for free.
10. **Determinism test in CI from the start.** A synctest-style harness: run N frames, save, run K frames with recorded inputs, load, re-run, compare hashes (GGPO synctest, GekkoNet stress session, psxrecomp self-check, 3SX stress + state diff). Optionally a "two builds, same inputs" replay comparison.
11. **Measure snapshot and frame cost early.** Track bytes dirtied per frame and simulated-frame time. Full copies of PS2-sized (~40 MiB) or Atomiswave-sized (~26 MiB) state every frame do not fit an 8-frame rollback on modest hardware; dirty tracking or region selection will likely be needed.
12. **License compatibility.** GGPO (MIT), GekkoNet (BSD-2), GGRS (MIT/Apache) and recomp-net (MIT) are permissive. Flycast (GPL-2.0+), PCSX2 and PS2Recomp (GPL-3.0), 3SX (AGPL-3.0) and psxrecomp (PolyForm Noncommercial) carry conditions if their code is reused rather than just studied.

### Base-choice notes (facts only)

- **Atomiswave/Dreamcast:** smaller state (~26 MiB total), a working rollback precedent on the same hardware family (Flycast + GGPO; its code sizes the state buffer for NAOMI vs. the other platforms, but per-game Atomiswave compatibility was not verified here), and an FPU whose modes are explicit in `FPSCR`. The AICA sound CPU (ARM7) is a second processor whose state must be in the snapshot if emulated.
- **PS2:** larger state (~40 MiB plus VU and register files), more processors (EE, VU0, VU1, IOP, SPU2, GS), non-IEEE floats in FPU and VUs, and a precedent only in the decompilation world (3SX), not in a PS2 static recomp.

---

## 7. Gaps and open questions

- No PS2 or SH-4 **static recomp** with rollback was found; the only static-recomp precedent is psxrecomp (PS1), whose rollback is labelled experimental.
- Flycast's GGPO setup guide for players (mizuumi wiki) could not be read (bot protection), so per-game compatibility notes for Atomiswave titles are not covered here.
- PCSX2's 2006 floating-point blog was read via its forum copy; the pcsx2.net page did not load.
- How KOF XI itself uses threads, timers, RNG seeds or floating point is unknown until the chosen binary is analysed. That analysis is out of scope here and must not put game data into the repository.
- The memcpy figures are from one cloud VM; re-measure on target hardware.

---

## Sources

- [GGPO Developer Guide (pond3r/ggpo, doc/DeveloperGuide.md)](https://github.com/pond3r/ggpo/blob/master/doc/DeveloperGuide.md)
- [GGPO repository README (MIT, Windows build)](https://github.com/pond3r/ggpo)
- [GGPO sync.cpp (per-frame save, AdjustSimulation)](https://github.com/pond3r/ggpo/blob/master/src/lib/ggpo/sync.cpp)
- [GGPO ggponet.h (GGPO_MAX_PREDICTION_FRAMES)](https://github.com/pond3r/ggpo/blob/master/src/include/ggponet.h)
- [GekkoNet repository](https://github.com/HeatXD/GekkoNet)
- [GekkoNet public header gekkonet.h](https://github.com/HeatXD/GekkoNet/blob/main/GekkoLib/include/gekkonet.h)
- [GGRS repository](https://github.com/gschup/ggrs)
- [backroll-rs repository](https://github.com/HouraiTeahouse/backroll-rs)
- [Flycast core/network/ggpo.cpp](https://github.com/flyinghead/flycast/blob/master/core/network/ggpo.cpp)
- [Flycast core/hw/mem/mem_watch.h](https://github.com/flyinghead/flycast/blob/master/core/hw/mem/mem_watch.h)
- [Flycast core/emulator.cpp (platform memory sizes)](https://github.com/flyinghead/flycast/blob/master/core/emulator.cpp)
- [Flycast core/hw/sh4/sh4_core_regs.cpp (FPSCR to host rounding)](https://github.com/flyinghead/flycast/blob/master/core/hw/sh4/sh4_core_regs.cpp)
- [Flycast core/hw/sh4/interpr/sh4_fpu.cpp (FSCA/FSRRA/FIPR)](https://github.com/flyinghead/flycast/blob/master/core/hw/sh4/interpr/sh4_fpu.cpp)
- [Fightcade GitHub organisation](https://www.github.com/fightcadeorg)
- [fightcade-fbneo src/burner/win32/fbn_ggpo.cpp](https://github.com/fightcadeorg/fightcade-fbneo/blob/master/src/burner/win32/fbn_ggpo.cpp)
- [Libretro docs: Run Ahead](https://docs.libretro.com/guides/runahead/)
- [Libretro docs: RetroArch Netplay](https://docs.libretro.com/development/retroarch/netplay/)
- [libretro.h (serialization quirks, savestate contexts)](https://github.com/libretro/RetroArch/blob/master/libretro-common/include/libretro.h)
- [Dolphin Netplay Guide](https://dolphin-emu.org/docs/guides/netplay-guide/)
- [Project Slippi (SmashWiki)](https://www.ssbwiki.com/Project_Slippi)
- [Slippi Ishiiruka SlippiSavestate.cpp](https://github.com/project-slippi/Ishiiruka/blob/slippi/Source/Core/Core/Slippi/SlippiSavestate.cpp)
- [3SX repository (crowded-street/3sx)](https://github.com/crowded-street/3sx)
- [3SX src/platform/netplay/netplay.c](https://github.com/crowded-street/3sx/blob/main/src/platform/netplay/netplay.c)
- [3SX src/platform/netplay/game_state.h](https://github.com/crowded-street/3sx/blob/main/src/platform/netplay/game_state.h)
- [psxrecomp repository and README](https://github.com/mstan/psxrecomp)
- [psxrecomp docs/NETPLAY.md](https://github.com/mstan/psxrecomp/blob/master/docs/NETPLAY.md)
- [psxrecomp docs/ROLLBACK_MOTK_HOOKUP.md](https://github.com/mstan/psxrecomp/blob/master/docs/ROLLBACK_MOTK_HOOKUP.md)
- [psxrecomp docs/ARCHITECTURE.md](https://github.com/mstan/psxrecomp/blob/master/docs/ARCHITECTURE.md)
- [recomp-net README](https://github.com/RetroPortingToolKit/recomp-net)
- [retcomm-rbengine README](https://github.com/RetroPortingToolKit/rbengine)
- [N64Recomp repository](https://github.com/N64Recomp/N64Recomp)
- [N64Recomp include/recomp.h](https://github.com/N64Recomp/N64Recomp/blob/main/include/recomp.h)
- [N64ModernRuntime repository](https://github.com/N64Recomp/N64ModernRuntime)
- [N64ModernRuntime ultramodern/src/threads.cpp](https://github.com/N64Recomp/N64ModernRuntime/blob/main/ultramodern/src/threads.cpp)
- [XenonRecomp repository](https://github.com/hedge-dev/XenonRecomp)
- [PS2Recomp repository](https://github.com/ran-j/PS2Recomp)
- [PS2Recomp ps2xRuntime/include/ps2_runtime_macros.h (PS2 float semantics)](https://github.com/ran-j/PS2Recomp/blob/main/ps2xRuntime/include/ps2_runtime_macros.h)
- [PCSX2 pcsx2/FPU.cpp](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/FPU.cpp)
- [PCSX2 pcsx2/Pcsx2Config.cpp (default FPU/VU control registers)](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/Pcsx2Config.cpp)
- [PCSX2 pcsx2/Config.h (clamping options, game fixes)](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/Config.h)
- [PCSX2 pcsx2/MemoryTypes.h](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/MemoryTypes.h)
- [PCSX2 pcsx2/VUmicro.h](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/VUmicro.h)
- [PCSX2 pcsx2/GS/GSLocalMemory.h](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/GS/GSLocalMemory.h)
- [PCSX2 pcsx2/SPU2/defs.h](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/SPU2/defs.h)
- [PCSX2 blog "Nightmare on Floating-Point Street" (forum copy)](https://forums.pcsx2.net/Thread-blog-Nightmare-on-Floating-Point-Street)
- [Microsoft Learn: /fp (Specify floating-point behavior)](https://learn.microsoft.com/en-us/cpp/build/reference/fp-specify-floating-point-behavior)
- [Microsoft Learn: _get_FMA3_enable, _set_FMA3_enable](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/get-fma3-enable-set-fma3-enable)
- [Microsoft Learn: GetWriteWatch](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-getwritewatch)
- [GCC manual: Optimize Options (-ffp-contract)](https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html)
- [GCC manual: x86 Options (-mfpmath)](https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html)
- [Clang User's Manual (-ffp-contract, -ffp-model)](https://clang.llvm.org/docs/UsersManual.html)
- [PC Gamer: N64 emulator RMG-K rollback via GekkoNet (secondary)](https://www.pcgamer.com/software/nintendo-64-emulator-just-implemented-rollback-netcode-for-the-entire-library-it-was-honestly-not-that-hard/)
