---
id: 18
title: Decide how the port reads the User-supplied Disc
type: grilling
status: closed
assignee: Tel-BR
blocked_by: [11, 12]
---

## Question

Does the port read the User-supplied Disc at runtime, or extract what it needs once at setup? How does it check that the user's image is the US edition (SLUS-21687 v1.00), given that a dump with read errors can still carry a correct executable ([Get a Redump-verified PS2 image](11-redump-verified-ps2.md))? And what happens to the two 630 MB `KOF_000x.DAT` files, depending on what [Find out what the two big PS2 DAT files hold](12-ps2-big-dat-files.md) finds? Disc reads must also be replayable for rollback (no host timing in the simulation).

_PT-BR: o port lê o disco do usuário enquanto roda, ou extrai o que precisa uma única vez na instalação? Como confere que a imagem é a edição americana v1.00, já que um dump com erros de leitura pode ter o executável correto (ticket 11)? E o que fazer com os dois arquivos `KOF_000x.DAT` de 630 MB, conforme o que o ticket 12 descobrir? As leituras do disco também precisam ser reproduzíveis para o rollback (nada de tempo do PC na simulação)._

## Resolution

Decided on 2026-11-21 by the repo owner (Tel-BR).

**Extract assets once at setup from a user-supplied ISO, verifying the executable hash and discarding the dummy DAT files.**

### Concrete Decisions

1. **Input Format (User-supplied Disc):**
   - End users provide a standard PS2 ISO disc image (`.iso`) dumped from their own copy. Physical optical drive reading is omitted.

2. **Extraction Strategy (One-time Setup):**
   - A dedicated setup/installer tool extracts all required game assets once from the user's ISO into an extracted directory or optimized game pack.
   - **Omitting Dummy DAT Files:** The two ~630 MB `KOF_0000.DAT` and `KOF_0001.DAT` files (1.26 GB, 52% of the disc) are completely skipped during extraction based on findings from [Find out what the two big PS2 DAT files hold](12-ps2-big-dat-files.md). The extracted footprint is only **~1.17 GB**, saving 1.26 GB of local storage.

3. **Edition & Integrity Verification:**
   - The setup tool verifies that the user's ISO is the US release (SLUS-21687 v1.00) by computing the **SHA-1 / CRC32 of the extracted executable (`SLUS_216.87`)** rather than hashing the whole disc image.
   - This ensures full compatibility even if a user's disc dump contains unreadable zeroed sectors inside the outer dummy padding (as analyzed in [Get a Redump-verified PS2 image](11-redump-verified-ps2.md)).

4. **Rollback Predictability:**
   - At runtime, the port loads game files directly from local SSD or memory cache with 0 ms read latency. No ISO parsing or virtual drive seeking occurs during match simulation, guaranteeing determinism for rollback frame advances.

---

_PT-BR: decidido em 21/11/2026 pelo dono do repositório (Tel-BR)._

_**Extrair os assets uma única vez na instalação a partir de uma ISO do usuário, validando o hash do executável e descartando os arquivos DAT de preenchimento.**_

_Decisões concretas:_
1. _**Formato de entrada:** o usuário fornece uma imagem de disco comum (`.iso`) extraída da própria mídia física. Suporte a leitura direta de drive óptico físico é dispensado._
2. _**Estratégia de extração:** uma ferramenta de setup extrai todos os dados necessários uma única vez para uma pasta local ou pacote otimizado._
   - _**Descarte dos arquivos DAT:** os dois arquivos `KOF_0000.DAT` e `KOF_0001.DAT` (~630 MB cada, 52% do disco) são ignorados na extração com base no ticket 12. O tamanho final dos dados do jogo é de apenas **~1.17 GB**, economizando 1.26 GB de espaço em disco no PC._
3. _**Verificação de integridade e versão:** o instalador valida que a imagem é a edição americana (SLUS-21687 v1.00) conferindo o **SHA-1 / CRC32 do executável extraído (`SLUS_216.87`)** em vez do hash da ISO completa. Isso garante que o instalador aceite imagens de usuários que contenham setores ilegíveis no preenchimento descartável (conforme analisado nos tickets 11 e 12)._
4. _**Determinismo para Rollback:** o jogo carrega os arquivos diretamente do SSD ou cache de memória com latência zero, sem buscar setores virtuais de ISO durante a luta, garantindo previsibilidade total no rollback._
