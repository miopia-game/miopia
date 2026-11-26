# S01 • Ficha de produção do Duelo da aranha

Esta ficha compara uma sala privada do Campo de testes com a distribuição Linux entregue antes do S01. O ponto de partida foi inventariado em 06/11/2026 às 20h56, horário de Brasília.

| Referência anterior ao sprint | Medição |
|---|---:|
| Download Linux compactado | 51.560.558 bytes |
| Instalação, soma dos tamanhos lógicos dos 965 arquivos | 81.396.393 bytes |
| Arte e folhas de chefes | 5.749.745 bytes |
| Áudio | 24.241.500 bytes |
| Fontes e seus avisos | 480.487 bytes |
| Código executado em `src`, 20 arquivos | 225.425 bytes |

SHA-256 do download anterior: `94a7b2ab4f2ae4565a6ff54538ab644c7a4709b7d5941c0e42b1abdd2a306b66`. Os tamanhos de categorias são partes da instalação e o tamanho do download é uma medida separada.

Uma extração limpa do pacote S01, sem caches locais de Python, tem **81.911.982 bytes** em 971 arquivos (+515.589 bytes). O download tem **52.045.398 bytes** (+484.840). Essa diferença inclui também a captura da sala, a interface, o gravador e os testes. A arte, os sons e as fontes distribuídos como assets mantiveram o mesmo tamanho. SHA-256 do pacote validado: `55914fe9e652df0f971f494e12bb28f13e5a5b21c6b8f621637703868c663eec`.

## O que a sala consumiu

Abrimos duas jornadas novas em `bosque.galeria_da_seda.v1` com a mesma semente. Em um processo limpo, desenhamos a sala, Lume, a aranha e a interface a cada passo, usando vídeo e áudio simulados do SDL. Contamos pelo caminho cada imagem que o pygame realmente abriu nessas duas rotas. Para áudio, contamos os arquivos correspondentes aos avisos espaciais emitidos. A ambiência e os efeitos normais do jogador continuam compartilhados com o Bosque.

| Componente observado | Resultado | Interpretação |
|---|---:|---|
| Imagens solicitadas | 14 arquivos, 618.824 bytes | Fundo do Bosque, chão, folha, abrigo, sete poses de Lume, duas poses da aranha e fio. Já acompanhavam a distribuição. A medição final usa o HUD da sala, sem inventário de campanha. |
| Sons espaciais emitidos | 3 arquivos, 107.736 bytes | Pés da aranha, disparo do fio e rasgo do salto. Já acompanhavam a distribuição. |
| Sala e ligação com o Campo de testes | +3.808 bytes de código-fonte | O módulo da sala usa 3.445 bytes e a lista de ensaios cresceu 363 bytes sobre a referência. Esses números medem o custo direto do cenário na árvore de trabalho e excluem o gravador, a interface, os testes e o instalador. |
| Mídia adicionada pela sala | 0 arquivos, 0 bytes | Os grupos de arte e áudio foram confrontados com o inventário anterior, usando caminho e SHA-256 dos 145 arquivos de assets. |
| Sessão de autoria da primeira sala | Cerca de 6 min | O responsável situou leitura e implementação entre 20h55 e 20h59 e verificação da sala entre 20h59 e 21h01. São intervalos locais de relógio arredondados, sem soma com atividades paralelas de integração e replay. |
| Orçamento de planejamento de T01.2 / T01.5 / T01.6 | 60 / 45 / 25 min | Previsões de capacidade do quadro. O tempo de uma sessão humana futura será medido à parte. |

## Dois percursos comparáveis

Ambos começam no marco em x = 160. A cobertura sólida ocupa x = 335–405. A semente **1701**, em dificuldade normal, posiciona a aranha em x = 563. As duas amostras têm 270 passos de simulação de 1/60 s, equivalentes a 4,5 s. Os números de quadro abaixo começam em 1. Todos os comandos não mencionados permanecem soltos.

| Percurso | Entrada de Lume | Resultado observado |
|---|---|---|
| Atrás da raiz | Direita nos quadros 1–47. Depois, aguardar. | O centro de Lume para em x = 323. A raiz bloqueia a linha até a aranha, que continua patrulhando. Zero decisões de ataque e zero danos. |
| Por cima da raiz | Direita nos quadros 1–100. Apertar salto no 43, mantê-lo até o 78. Depois, aguardar. | A aranha prepara fio no quadro 75 e salto no 176. O primeiro dano a Lume ocorre no 220. No primeiro aviso, Lume está em x = 380,42 e o alvo antecipado do fio em x = 419,94. |

O seletor continua fazendo as escolhas usadas na campanha. Na verificação direta, vinte chamadas a 103 px selecionaram salto e vinte a 104 px selecionaram fio, em ambos os sentidos. Essa medição de código é distinta da avaliação do aviso por um jogador.

**Reexecução.** Gravamos os dois trajetos em arquivos JSON separados e conferimos pelo módulo de replay em processos novos. O primeiro reproduziu os 270 quadros e zero decisões. O segundo reproduziu os 270 quadros e duas decisões. Os registros de 4,5 s ocuparam 1.112 e 2.517 bytes na amostra medida às 21h02. Esses arquivos pertencem ao perfil de teste e ficam fora do instalador. Para conferir uma tentativa própria, execute na raiz do projeto com o ambiente de desenvolvimento: `python -m src.replay_aranha "/caminho/da/tentativa.json"`.

**Isolamento da apresentação.** Repetimos o percurso de travessia com as sementes 1701, 1702 e 1703, primeiro sem desenho, depois desenhando os 270 quadros com brilho alto e chamadas ao gerador aleatório global. Em cada par, a origem da aranha, os eventos e o estado final coincidiram. O poleiro ficou em x = 563, 598 e 586, respectivamente. O primeiro dano ocorreu nos quadros 220, 241 e 239. Confirmar pela interface e em hardware real continua fazendo parte da rodada humana.

## Fechamento após a sessão humana

Quando a sala receber avaliação, completar os campos abaixo e reaproveitar a ficha no cartão T08.4, ao produzir a segunda sala. Medir a diferença contra a versão de partida usando a mesma plataforma, o mesmo empacotador e tamanhos lógicos de arquivos. Recursos que já acompanham o jogo entram como reutilização. Registrar a revisão separadamente para que um segundo passe de arte ou de áudio possa ser comparado ao primeiro.

| Campo para a próxima rodada | Situação |
|---|---|
| Aceite da leitura da sala por Thierry | Pendente |
| Minutos de retrabalho após feedback humano | Pendente |
| Decisão da equipe sobre produzir a próxima sala | Pendente |
