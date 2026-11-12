# Hands-on comparison checklist / Checklist da comparação na prática

_For [Compare both releases hands-on in emulators](../tickets/10-hands-on-comparison.md). The owner plays; the agent records his answers on the ticket. Each item is in English, then Portuguese. Answer in either language; short notes are enough._

_O dono joga; o agente registra as respostas no ticket. Responda em qualquer idioma; anotações curtas bastam._

**How to mark each difference / Como marcar cada diferença:** **MUST** = must keep in the port / _indispensável no port_; **NICE** = nice to have / _bom ter_; **NO** = don't care / _tanto faz_.

## 0. Setup / Preparação

- **PS2 Release:** PCSX2 (current stable), your own PS2 BIOS dumped from your console, and `private/ps2/` image (SLUS-21687). Start at native resolution (1x) so both versions are compared fairly; upscale later only if you want to.
  _PCSX2 atual, o BIOS do seu próprio PS2 e a imagem em `private/ps2/`. Comece na resolução nativa (1x) para comparar de forma justa._
- **Arcade Release:** Flycast (current), loading `private/arcade/kofxi.zip` (your cartridge, MAME `kofxi` set). Flycast can run Atomiswave without the `awbios` file (it emulates the BIOS); note it if something looks wrong. Map the 5 arcade buttons, plus Service and Test.
  _Flycast atual com o `kofxi.zip` do seu cartucho. O Flycast roda Atomiswave sem o arquivo de BIOS; anote se algo parecer errado. Mapeie os 5 botões, mais Service e Test._
- **Optional:** the Dreamcast Conversion GDI in Flycast. It is the same arcade code with 754 bytes patched, so only note anything that differs from the cartridge version.
  _Opcional: a conversão de Dreamcast no Flycast. É o mesmo código de arcade com remendos; anote só o que for diferente do cartucho._
- Use the **same controller, screen and V-Sync setting** for both. / _Mesmo controle, mesma tela e mesma configuração de V-Sync nas duas._

## 1. One Complete Fight, screen by screen / Uma luta completa, tela a tela

The map's destination is one Complete Fight, which the [glossary](../../../../GLOSSARY.md) currently defines as "from the start of round one to the result screen". In each version, play one fight from the title screen and **list every screen in order** (for example: title, mode select, character/team select, order select, loading, stage intro, rounds, win screen, continue or results, back to menu). Then say which screens outside "round one to result" you would also want in the first playable build.

_O destino do mapa é uma luta completa, que o glossário hoje define como "do início do primeiro round até a tela de resultado". Em cada versão, jogue uma luta a partir da tela de título e **liste cada tela, em ordem**. Depois diga quais telas fora desse trecho você também quer no primeiro build jogável._

| | PS2 | Arcade |
|---|---|---|
| Screens in order / telas em ordem | | |
| Missing or extra / falta ou sobra | | |

## 2. Menus and modes / Menus e modos

- Which modes and menu options exist out of the box? List them; don't unlock anything yet.
  _Quais modos e opções existem logo de início? Liste; não desbloqueie nada ainda._
- Which options would you want in a two-player fight (time, rounds, handicap, button config, sound test, and so on)?
  _Quais opções você quer numa luta de dois jogadores (tempo, rounds, handicap, configuração de botões etc.)?_

## 3. Roster and Hidden Characters / Elenco e personagens ocultos

- How many fighters are selectable at the start in each? / _Quantos lutadores dá para escolher logo de início em cada uma?_
- Arcade: open the Test menu and note which settings affect characters (do not look for hidden menus). / _Arcade: abra o menu de Test e anote quais ajustes afetam personagens (sem procurar menus escondidos)._
- Which fighters that exist only in one version matter to you? / _Quais lutadores exclusivos de uma versão importam para você?_

## 4. Controls and feel / Controles e sensação

Play the same three matchups in both versions. / _Jogue os mesmos três confrontos nas duas versões._

- Button layout and which actions need a button combination. / _Layout dos botões e quais ações exigem combinação._
- Do specials, supers, tag-outs and cancels come out equally easily? Any input feeling late or dropped?
  _Especiais, supers, trocas e cancelamentos saem com a mesma facilidade? Algum comando parece atrasado ou ignorado?_
- Does the game speed feel the same? Any slowdown? / _A velocidade do jogo parece igual? Alguma lentidão?_

## 5. Loading / Carregamento

- Roughly how long from character select to the fight, and between rounds? / _Mais ou menos quanto tempo da escolha do personagem até a luta, e entre rounds?_

## 6. Audio / Som

- Music: original or arranged, and can you choose? Voices and effects: any difference in quality or balance?
  _Música: original ou arranjada, dá para escolher? Vozes e efeitos: diferença de qualidade ou volume?_

## 7. Visuals / Imagem

- Sprites, backgrounds, effects, flicker or missing textures; progressive or interlaced output; any stage that exists in only one version.
  _Sprites, cenários, efeitos, tremulação ou texturas faltando; imagem progressiva ou entrelaçada; fases exclusivas de uma versão._

## 8. Online rollback in Flycast (optional) / Rollback online no Flycast (opcional)

Only if a partner is available (Flycast's GGPO option or Fightcade): how does it feel at your usual ping, and do you see rollback glitches (teleporting, repeated sounds)?

_Só se houver um parceiro (opção GGPO do Flycast ou Fightcade): como fica no seu ping habitual, e aparecem defeitos de rollback (personagem "teleportando", sons repetidos)?_

## 9. Verdict / Conclusão

- Top five differences, each marked MUST / NICE / NO. / _As cinco maiores diferenças, cada uma marcada MUST / NICE / NO._
- Is there anything that would make you reject a version outright? / _Existe algo que faria você descartar uma versão de vez?_
