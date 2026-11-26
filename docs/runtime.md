# GPU runtime and reference replays / Runtime GPU e replays de referência

## Run on Windows

| Action | Command |
| --- | --- |
| Play with the installed GPU build | `run_game.bat` |
| Run the local Reference Scenario | `run_replay.bat` |
| Play a specific power-on recording | `run_replay.bat "path\to\recording.p2m2"` |
| Rebuild an already configured GPU checkout | `build_runtime.bat` |

Both launchers use the Release runner under `private/tools/PS2Recomp-Fixer/build/ps2recomp/ps2xRuntime/Release` and read the adjacent `game.ini`. The user's disc, extracted boot ELF, recordings, and logs stay under `private/`. The no-argument replay uses the local `ticket19.p2m2`, or `ticket19_trunc1000.p2m2` if only the short capture exists.

The runtime reads both recorded controller packets at the emulated VSync, including analog axes and pressures. The runner closes at the file's declared length. Savestate-based recordings require emulator state and are rejected. The GPU port and the Reference Emulator start the game through different boot paths. The replay's timing follows the recording tables, and visual or game-state parity needs a separate comparison.

The two interactive batches clear the automated test mute before starting the runner. Their logs are in `private/fixer-port/`.

## Executar no Windows

| Ação | Comando |
| --- | --- |
| Jogar com o build GPU instalado | `run_game.bat` |
| Rodar o Cenário de referência local | `run_replay.bat` |
| Rodar uma gravação específica iniciada do boot | `run_replay.bat "caminho\para\gravacao.p2m2"` |
| Recompilar um checkout GPU já configurado | `build_runtime.bat` |

Os dois launchers usam o runner Release em `private/tools/PS2Recomp-Fixer/build/ps2recomp/ps2xRuntime/Release` e leem o `game.ini` ao lado do executável. O disco do usuário, o ELF extraído, as gravações e os logs ficam em `private/`. O replay sem argumento usa o arquivo local `ticket19.p2m2`, ou `ticket19_trunc1000.p2m2` quando só a gravação curta está disponível.

O runtime lê os pacotes gravados dos dois controles no VSync emulado, incluindo os eixos analógicos e as pressões. O runner encerra na duração declarada no arquivo. Replays iniciados de savestate são rejeitados porque dependem do estado do emulador. O port GPU e o Emulador de referência iniciam o jogo por caminhos diferentes. O replay segue os campos gravados e a equivalência visual ou de estado exige uma comparação à parte.

Os dois batches interativos limpam o mudo dos testes automatizados ao iniciar o runner. Os logs ficam em `private/fixer-port/`.
