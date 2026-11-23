# IOP Subsystem Rollback Contract: Forward Audio, Native Input, Cached Disc

**Status: under review (2026-11-22).** The emulated sound modules cannot produce audio because the SPU2 is not emulated, and native input was not carried out. The rollback contract itself (audio forward only, one input entry point, cached disc) still stands. See [ticket 17](../wayfinder/base-to-playable-fight/tickets/17-iop-approach.md).

_PT-BR: **Situação: em revisão (22/11/2026).** Os módulos de som emulados não têm como gerar áudio porque o SPU2 não é emulado, e o controle nativo não foi implementado. O contrato de rollback em si (áudio só para frente, um ponto de entrada de controle, disco em cache) continua valendo. Ver o ticket 17._

To satisfy rollback netplay determinism without audio distortion or I/O hitches, controller input (`PADMAN`) is replaced with a single native frame-boundary input injection point, disc reads are served synchronously from memory/RAM cache, and emulated IOP sound modules (`CRI_ADX`/`LIBSD`) run forward asynchronously without rollback. Rewinding audio state during frame predictions would cause audible pops and stutter, so audio commands are dispatched only on final displayed frames.

_PT-BR: Para garantir determinismo de rollback netplay sem distorção sonora ou travamentos de disco, a leitura de controles (`PADMAN`) é substituída por um ponto único de injeção nativa na fronteira de cada quadro, leituras de disco são atendidas em cache na memória RAM e o som emulado no IOP (`CRI_ADX`/`LIBSD`) corre sempre para frente sem retroceder no rollback. Rebobinar áudio geraria estalos e ruídos, portanto comandos sonoros só são disparados no quadro final exibido._
