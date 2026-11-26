# As quatro guardiãs da mata

Cada arena ocupa 760 px. O ponto de retorno fica antes da entrada. As posições nesta ficha são relativas ao limite esquerdo. As colisões dos apoios são fornecidas por `Encontro.apoios()`. A camada de desenho lê esses mesmos contornos. Os retratos RGBA em `assets/arte/chefe_*.png` ganham respiração, espelhamento e movimentos diferentes na vigília, no aviso, na ação e no repouso. As pequenas gravuras de entrada vêm das folhas em `assets/chefes/`, desenhadas pelo gerador `tools/desenhar_guardioes.py`.

## Regras atuais desde o S32

No Último Chamado da História, a Coruja anuncia rasantes horizontais
e, a partir do primeiro sinal, quedas verticais de penas. A marca da
queda fica no lugar até o impacto. Atravesse fora das faixas e use E
para recuperar brilho no ninho âmbar, seguido de K para responder.
Cada sobrevivente resgatado amplia em 6 px o alcance da resposta e
em 0,04 s o aviso. [Detalhes e evidências do S34](equipe/S34.md).

| Dificuldade | Dano crítico em 100 PV | Janela de abertura | Dano comum |
|---|---:|---:|---:|
| Fácil | 50 PV | 100% da duração original | 100% |
| Normal | 34 PV | 86% da duração original | 58% |
| Difícil | 34 PV | 72% da duração original | 44% |

O dano comum contribui para que a vitória possa chegar antes da última
abertura. Os avisos conservam o tempo de resposta. A recuperação entre
ataques encurta no Normal e no Difícil. O Casco e a Coruja podem entrar
na segunda fase após o primeiro crítico. A Coruja ainda pede três sinais
no Último Chamado da História.

A Tecelã chama crias dos casulos marcados por luz e som. No Fácil nasce
uma aranha. No Normal a primeira leva traz uma e a segunda, duas. No
Difícil podem nascer duas por leva. O ataque revezado dá à Tecelã tempo
para disparar e às crias tempo para alcançar Lume. A cortina de água
interrompe as crias próximas e as desacelera. As que sobrevivem voltam
aos casulos ou saem ao fim da leva. Morrer ou terminar a luta encerra
todos os reforços. [Encontros e verificação](equipe/S32.md).

## Mecanismos das arenas e notas de origem

### Asa Fendida · os ninhos sem luz

O morcego procura o brilho dos ninhos vazios. Uma cicatriz nas raízes de cada extremo indica as batidas anteriores. Há um patamar a 66 px de altura junto a cada parede, com outro a 120 px. A peça da corda permite entrar. Quando levanta as asas, a direção da investida fica assinalada. Perto da parede, Lume pode se agachar para deixar a asa passar acima. Longe das marcas, o morcego freia antes de bater. A colisão com a raiz prende a asa e revela o dorso. Suba e acerte a marca nas aberturas. Quando a criatura repousa no berçário, a passagem se abre.

### Tecelã do Vão · o fio da correnteza

Esta aranha reparava as margens. O Breu amarrou seus fios ao teto. O encaixe de Casca permite operar a válvula a oeste. A aranha mira um fio, projeta uma linha no instante do aviso e lança o fio pelo espaço livre. Os fios que erram Lume deixam tramas temporárias, ora altas, ora rente ao solo. Os patamares e o espaço de agachamento permitem cruzá-las. Girar a válvula interrompe os fios no ar. A cortina de água força a Tecelã a descer num ponto próximo da válvula. Na descida, o ventre fica apoiado no leito e pode receber um golpe curto. Repita a manobra para expor o ventre de novo.

### Casco Oco · a vigília dos bambus

O guardião patrulha o que resta da borda. Um aviso precede sua marcha pelo chão. O contato quebra o estrado central de bambu. Uma semente de seiva pode ser empurrada a partir do lado oeste. Apertar E junto dela engata o carrinho, que acompanha o deslocamento de Lume até o entalhe iluminado. E junto à fonte de brasa então acende a seiva por magia. O guardião segue esse brilho até o fruto e cruza o espaço de Lume. Quando alcança o entalhe, a casca se abre e revela uma marca elevada para um golpe. Na segunda fase, o entalhe fica mais adiante e a marca sobe. A fonte oferece outra semente a cada tentativa de expor o casco.

### Coruja · o ouvido da figueira (descrição histórica)

A tempestade feriu seus olhos. Ela se orienta pelos sons da mata. Ao ouvir passos, pousos ou deslizes, memoriza o lugar. Em silêncio ela busca às cegas, alternando varreduras altas e baixas. Os arcos de escuta e a linha de ataque permitem antecipar a trajetória. A válvula a oeste move o sino até a marca da parede a leste; E na mesma corda o faz soar. A Coruja dirige a investida até o som. Subir pela gradação de apoios e usar o clarão perto de sua face enquanto descansa quebra parte do transe. Repetir o chamado a acalma. Desde o S03, cortes também causam dano comum; o crítico continua exigindo K na face exposta. Ela fica viva, junto da raiz.

### Revisão histórica S05

A revisão está detalhada em equipe/S05.md. Casco tem carga/retorno, varrida,
salto com ondas e fase II, preservando seiva/brasa para o crítico. Coruja voa,
usa garras, rasantes e pares de penas, com segunda fase. O sino abre a face
por 2,8 s. Crítico de 50 PV e corte comum uma vez por arco. Mira fixa após
aviso e efeitos desenhados nas coordenadas físicas. Novos ensaios de ambos
estão no Campo de testes. O clímax com resgates depende do S07.

### Tentativas

A Asa Fendida segue a altura de Lume na busca desde o início. No aviso, fixa a linha de voo na altura do patamar ou de Lume no ar. Na segunda fase, também pode dar rasantes baixos nos apoios e no chão. Um risco baixo levanta folhas e pede salto. A investida à altura do peito permite agachar. Ao marcar Lume no ar, ela anuncia a linha de que ele precisa sair. A abertura após bater na raiz passa de 3,8 s na primeira rodada a 2,1 s na segunda. A Tecelã abre os fios em duas trajetórias anunciadas na fase seguinte, e o ventre fica exposto por 2,85 s após a segunda cortina. Os dois duelos podem ser repetidos pelo Campo de testes.

Cada acerto abre uma janela diferente da próxima. O brilho âmbar marca o alvo durante a abertura. O aviso de ataque usa ferrugem, som e mudança de postura. A recomposição do encontro renova barril, sino, apoios, válvula e chefes. Um alvo ameaçador acerta no máximo uma vez por investida; a invulnerabilidade após dano é resolvida pelo modelo de travessia.
