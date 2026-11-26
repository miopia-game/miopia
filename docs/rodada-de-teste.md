# Rodada de teste com Thierry

Abra **Miopia** e escolha **Campo de testes**. A opção Mundo vertical abre o acesso a um corte de múltiplas telas. Os ensaios usam uma jornada separada da campanha e dos recordes. O Duelo da aranha também registra suas entradas em um histórico local próprio. Na pausa, escolha **Voltar ao campo de testes** para ir direto ao próximo trecho.

## S02 • Orientação e aranha

Esta rodada corrige o retorno relatado no Córrego. Na campanha, Tab abre a planta local com o destino, e K aponta seu rumo. O fundo e o terreno ficam escuros fora da luz. A planagem continua enquanto Espaço estiver pressionado durante a queda.

Em **Raízes do Córrego**, use S + Espaço para descer no mesmo mapa. Recolha com E a membrana no fundo e volte pelos galhos da direita. A primeira subida pede salto duplo. Em **Duelo da aranha**, compare a aproximação pelo chão e pelo galho. O seletor usa distância, obstáculos, viabilidade do salto e memória dos últimos ataques. [Mudanças e pendências](s02-feedback.md) · [Medições do combate](s02-aranha.md).

1. Selecione **Duelo da aranha**, deixe a semente em **1701** e pressione **Enter**. Caminhe até a pedra e pare. Depois, salte a cobertura e aproxime-se pelo chão ou pelo galho. **Tab** mostra o traçado da sala; **E** no abrigo recupera luz.
2. Após uma vitória, morte ou saída pela pausa, a tentativa fica disponível no histórico local. Para repetir do início, use a mesma semente. Na pausa, **R** pede confirmação e registra o trecho jogado antes de começar outro.
3. Volte ao Campo de testes, destaque o duelo e pressione **V**. **Espaço** pausa ou continua a reprodução. **Esc** retorna ao campo. As setas ou os botões ao lado da semente mudam o próximo encontro, independentemente do replay que você está assistindo.
4. Na sessão seguinte, um JSON anterior pode ser aberto com o executável: `./Miopia --reproduzir "/caminho/da/tentativa-01.json"`. No Linux, o histórico usa `$XDG_DATA_HOME/miopia/ensaios/aranha` ou `~/.local/share/miopia/ensaios/aranha`, salvo se `MIOPIA_DADOS` apontar para outra pasta. O histórico guarda até 32 arquivos sem sobrescrever os anteriores; copie ou mova os que quiser guardar. Se faltar espaço, ainda é possível assistir à última tentativa daquela sessão. Cada gravação aceita até 18 mil entradas de simulação ou ações instantâneas. Uma tentativa mais longa guarda o trecho inicial.

Arquivos de replay verificam a versão das regras que os produziu. Tentativas do S01 ficam preservadas e precisam da distribuição S01 para reproduzir exatamente. Grave novas tentativas para avaliar o S02.

**Pergunta de jogo:** mantendo a mesma semente, quando a aranha começou a se preparar para o golpe? O que mudou quando você passou por cima da pedra? O replay reexecuta as entradas e verifica a versão das regras, os avisos, o primeiro impacto e o resultado. O jogador continua livre para avaliar a dificuldade e a leitura dos ataques.

**Revisão do retorno de T00.5.** Comece em **Estaleiro das Folhas**. Pressione **E** na fenda, caminhe à direita do marco até a grade e use **S + Espaço**. Siga os berços até a roda no fundo. Depois de girá-la, caminhe para oeste e consulte o mapa com **Tab**. Em **Mundo vertical**, há outro acesso à mesma oficina: siga para leste pela galeria e use o salto duplo para alcançar o primeiro beiral alto. O parecer sobre a duração e a verticalidade das demais regiões continua aberto.

| Trecho corrigido | O que experimentar | O que registrar |
|---|---|---|
| Galhos do Bosque | Na História, ache o galho acima de Nira. Salte, solte Espaço, aperte novamente no ar e pouse na varanda de orvalho. | Se o segundo impulso saiu no toque esperado e se ficou claro qual piso deixa atravessar. |
| Manivelas | No Bosque, salte contra o aro e pressione E. Na cisterna, use K e E juntos perto do ralo. | Nome da roda e aviso exibido se alguma ainda não responder. |
| Asa Fendida | Passe a primeira investida. Na fase seguinte, observe a altura anunciada e escolha sua esquiva. | Se a nova postura permite decidir sem decorar o turno. |
| Tecelã do Vão | Compare as marcas no ar antes e depois do primeiro acerto. Observe o que muda ao abrir a cortina de água. | Se os dois fios deixam espaço legível para agir. |
| Áudio no Bosque | Corra, salte e escute o inimigo com o mesmo volume usado antes. Em Ajustes, Ambiência e Efeitos têm controles separados. | Qual som ainda incomoda e se foi possível localizar o ataque. |

| Trecho | Experimento | O que observar | Avaliação de Thierry |
|---|---|---|---|
| Mundo vertical | E na fenda do Bosque → visite a galeria, suba até a copa, desça ao poço e retorne por outra boca. Abra o mapa com Tab. | Consegue dizer o que está acima e abaixo e escolher uma volta diferente? | Em aberto |
| Combate no Bosque | Escute de que lado vem o morcego. Toque J três vezes em cadência; salte e use S + J sobre ele. | Dá para reconhecer o acerto, o terceiro corte e o rebote? | Em aberto |
| Túnel do Córrego | Use K, deslize para a direita com Shift e use E sob a raiz. | A raiz da captura faz sentido? A área iluminada permanece onde você a deixou? | Em aberto |
| Pulo entre paredes | Salte contra a face riscada, pressione Espaço no contato e alterne as paredes até a cunha. | A janela de impulso parece justa? É fácil identificar as faces? | Em aberto |
| Descida pela grade | Segure S e aperte Espaço; depois faça o mesmo sobre a terra no fundo. | A grade deixa descer e o chão segura? | Em aberto |
| Planeio no Taquaral | Corra para a direita, salte da ponta e segure Espaço na descida. Solte para cair mais rápido. | A sustentação continua enquanto segura a tecla e o pouso é controlável? | Em aberto |
| Raízes do Córrego | Desça sem portal, pegue a membrana e suba por outra grade. | O mapa, o objetivo e a recompensa tornam a exploração compreensível? | Em aberto |
| Sentinela do Taquaral | Enfrente o carabídeo. Observe a carapaça, salte sobre ele e procure um flanco. | O perigo é claro antes do ataque? A dificuldade ficou adequada? | Em aberto |
| História e itens | Na História, converse com Nira, procure o mapa e leve-o a Véspera. Use Q para escolher um item e F para usá-lo. | O pedido dá motivo para voltar? O item recebido ajuda na travessia? | Em aberto |
| Morte e retorno | Caia num vão. Leia **Você morreu** e confirme o retorno. | O último marco, os itens e as portas conquistadas continuam claros? | Em aberto |

Para registrar a rodada, basta dizer **trecho**, **o que fez**, **o que aconteceu** e **aprovar / ajustar**. Pode escolher apenas uma linha. Os testes automatizados verificam as regras; a marca de aprovação desta tabela é do jogador.

## Prompt auxiliar para o próximo ciclo

> Continue a revisão de Miopia na pasta do projeto. Leia este caderno, o README e o último feedback do jogador. Identifique os trechos aprovados por Thierry e preserve seu comportamento. Reproduza o problema pelo Campo de testes ou pelos comandos normais da História. Mude apenas o necessário para o feedback desta rodada. Confira os testes da campanha, o caminho de volta ao marco e os saves anteriores. Atualize o executável no mesmo lugar e registre um trecho curto que Thierry possa abrir para julgar a mudança. Mantenha em aberto tudo que ele ainda não experimentou.

## Guias consultados

A coleção **GameDev Agent Skills** apresentava cerca de 7,1 mil estrelas no GitHub na consulta. O projeto tem um validador de estrutura e testes desse validador. Para Miopia, a verificação de comportamento foi feita separadamente no pygame-ce com movimentos e combates reais. [Repositório e validação](https://github.com/gamedev-skills/awesome-gamedev-agent-skills).

- **Platformer** orientou o uso de margem no contato com a parede, a distinção entre piso sólido e plataforma de passagem e a medição do alcance do salto em salas jogáveis. [Guia de plataforma](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/genres/platformer/SKILL.md).
- **Game AI** e **Game Feel** orientaram a separação entre perceber, escolher um ataque, avisar e se recuperar. Em Miopia os acertos têm efeitos diferentes e uma breve pausa visual. [IA de jogo](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/disciplines/game-ai/SKILL.md) · [Resposta dos controles e impactos](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/disciplines/game-feel/SKILL.md).
- **Audio Design** orientou a separação entre ambiência e avisos e a redução do fundo sob sons importantes. Também foi consultado o material público de agentes de jogos da Hugging Face. A IA de Miopia roda localmente no pygame, com regras em Python. [Guia de áudio](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/main/skills/disciplines/audio-design/SKILL.md) · [Hugging Face, agentes em jogos](https://huggingface.co/learn/deep-rl-course/en/unitbonus1/how-huggy-works).
