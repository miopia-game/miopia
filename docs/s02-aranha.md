# S02 • Aranha contextual

O S02 aplica à aranha da campanha e da Galeria da Seda uma escolha entre ações que cabem no espaço. As demais espécies conservam seus seletores. A avaliação de dificuldade e leitura pelo jogador continua pendente.

## Entrega dos cartões

| Cartão | Implementação | Evidência |
|---|---|---|
| T02.1 | Fio exige visão do alvo e linha desobstruída até a mira antecipada. Salto verifica teto, paredes e dois pontos de apoio no pouso. Sem opção, espera e tenta reposicionar. | Cem sementes com parede, teto baixo e borda sem piso. Nenhum ataque inelegível foi escolhido. |
| T02.2 | Distância pondera fio e salto, usando as afinidades do atlas. O sorteio ocorre uma vez ao começar o aviso. | Dez mil escolhas por contexto, três contextos. Diferença inferior a dois pontos percentuais em cada um. |
| T02.3 | A repetição recebe fator 0,45. Depois de duas escolhas consecutivas recebe 0,20. A única ação possível mantém seu peso. | Repetições continuam presentes. Pesos zero nunca são sorteados. Reiniciar reproduz a sequência. |
| T02.4 | Mira usa posição e velocidade observadas. Técnica e alvo ficam fixos até o fim do ataque. | Mudar posição e velocidade durante o aviso não altera a mira. O jogador pode sair da trajetória. |
| T02.5 | As entradas do S01 foram executadas novamente, com comparação de sequência. | Registro abaixo, reprodução de três sementes e referências de vespa e morcego preservadas nos testes. |

O gerador de cada aranha é separado do gerador global. A campanha deriva sua semente da posição inicial e dificuldade; o duelo inclui a semente escolhida no menu. Reiniciar recria o gerador e a memória. Música, desenho e chamadas aleatórias de apresentação não alteram suas decisões.

O arco do salto é o mesmo na verificação e na execução, com elevação de 49 px. A checagem usa 32 segmentos e expande os obstáculos pelo tamanho do corpo, impedindo que um teto fino seja ignorado. A recuperação respeita bordas, inclusive depois de um salto.

## Modelo utilizado

Para distância horizontal `d`, o peso do fio é `max(0, 1 − |d−150|/160)`, elegível entre 65 e 260 px. O salto usa `0,95 × max(0, 1 − |d−65|/95)`, elegível até 150 px, com alvo numa altura compatível e arco livre. Depois da memória, cada peso é dividido pela soma dos pesos positivos.

Esta implementação normaliza somente **fio e salto**. O simulador do atlas inclui também um recuo sorteado; aqui o recuo continua sendo parte da recuperação, e o deslocamento para reposicionar ocorre na patrulha. Essa adaptação evita anunciar como ataque um movimento que não causa dano.

Medição fixa de 110 px, semente individual 20261106, dez mil escolhas independentes por linha. A memória foi fixada antes de cada amostra, sem acumular os sorteios como ataques executados.

| Memória fixa | Chance teórica de fio | Fio observado | Salto observado |
|---|---:|---:|---:|
| Nenhuma | 60,00% | 60,44% | 39,56% |
| Último ataque foi fio | 40,30% | 39,79% | 60,21% |
| Dois últimos foram fio | 23,08% | 22,85% | 77,15% |

## Comparação com o S01

Amostra da Galeria da Seda, dificuldade normal, semente 1701, 300 passos de 1/60 s. Direita nos quadros 1–124. No percurso exposto, salto no quadro 35, mantido até o 82. Os quadros desta tabela começam em 1.

| Percurso | S01 | S02 |
|---|---|---|
| Caminhar até a pedra, sem saltar | Nenhuma decisão, nenhum dano | Nenhuma decisão, nenhum dano |
| Passar por cima da pedra | Fio 68, salto 168, salto 280 | Fio 68, salto 168, fio 264 |
| Primeiro dano no percurso exposto | Quadro 113 | Quadro 113 |

É uma comparação das mesmas entradas em versões diferentes. Não se deve abrir um JSON antigo como se suas regras fossem as atuais. O replay rejeita assinaturas incompatíveis. Tentativas novas são reproduzíveis na versão que as gravou.

Como controle, uma vespa e um morcego receberam o mesmo alvo parado durante 600 quadros. Mantiveram os mesmos instantes, técnicas e posições de mira da referência anterior. Asserções com esses valores estão no teste S02.

## F02 • Dificuldade relatada no teste

Foi reproduzido um problema além da seleção. Cada corte leve reiniciava atordoamento, recuperação e espera. Uma aranha podia morrer sem chegar a anunciar ataque.

* A aranha normal passou de 4 para **6 PV**. Fácil usa 5 e difícil usa 7. O aviso normal continua em **0,60 s**. Os demais níveis mantêm seus multiplicadores anteriores.
* Cortes leves ainda causam dano e feedback de impacto, mas preservam um aviso ou uma investida já iniciada. Na patrulha, uma interrupção leve abre resistência de 0,95 s a novas interrupções leves.
* Terceiro corte, golpe descendente e clarão continuam interrompendo. A relíquia de dano multiplica os cortes por 1,25; o clarão conserva dano 2.
* Após uma interrupção, a aranha tenta recuar até 200 px para longe do atacante, dentro de seu território e sem passar por paredes ou bordas. A evasão dura até 0,38 s, não causa dano e permite uma decisão nova sem espera extra de patrulha. Cortes leves não reiniciam esse movimento enquanto durar a resistência.

Uma aproximação reproduzível distingue as respostas. Na semente 1701, caminhar à direita por 94 quadros e saltar no quadro 35 coloca Lume diante do primeiro ataque. A partir daí, aproximar e apertar J a cada 17 quadros vence em cerca de 1,3 s, recebendo um dano. Recuar durante aviso/investida e atacar na recuperação vence em cerca de 3,5 s, sem dano. A aranha inicia duas decisões nos dois percursos. O teste usa somente comandos normais de movimento, salto e golpe.

Outro ensaio isola a repetição de J a cada 17 quadros. Lume começa a 50 px da aranha na Galeria, em chão livre verificado. No S01, ficar parado atacando a derrotava em 40 quadros, antes de qualquer decisão. No S02, ela recua, mantém 5 PV e anuncia três fios em seis segundos. Persegui-la ativamente permite vencer em 78 quadros, mas agora ela inicia duas decisões. As espadas podem interceptar os fios; causar dano inevitável não é o objetivo dessa mudança.

**Limite observado.** Uma aranha comum isolada ainda pode ser dominada por aproximação e combos bem encaixados. O teste não demonstra que a campanha inteira já tenha a dificuldade desejada. Novas técnicas, organização dos encontros e janelas de recuperação de chefes continuam precisando de cartões próprios e avaliação humana. Os valores novos de vida, resistência e recuo são hipóteses de balanceamento, sem aceite de Thierry.

## Como retestar

Abra **Campo de testes → Duelo da aranha**, mantenha a semente 1701 e atravesse a pedra. Compare avançar atacando com recuar após o aviso. Use **V** no Campo de testes para assistir à última tentativa. Repita com 1702 e 1703. Observe se o fio e o salto são distinguíveis antes do dano, se o recuo permite responder e se o aumento de vida torna o encontro interessante.

Verificação técnica específica na raiz do projeto com pygame-ce instalado:

```sh
python -m unittest tests.test_s02_aranha tests.test_combate tests.test_s01_sala tests.test_s01_replay tests.test_s01_app -v
```

Os treze testes novos incluem geometria, probabilidades, repetição, mira fixa, independência do desenho, retorno pela borda, dano da relíquia, interrupções, evasão após golpes e o percurso sem dano. Nenhum asset externo ou dependência nova foi adicionado pelo S02.

## Revisão da integração e custo de desenho

Foram capturadas e inspecionadas três telas da versão integrada, com o brilho padrão Noturno e recursos já presentes no projeto. A primeira mostra a roda da ponte e o clarão; a segunda, a câmara inferior com a membrana; a terceira, o mapa completo do Córrego com o mesmo desvio. As capturas posicionam Lume para ilustrar a entrega. A validação do trajeto por controles normais é separada, em `tests/test_feedback_s02.py`.

* [Ponte e clarão](../capturas/s02_ponte_clarao.png)
* [Subsolo e relíquia](../capturas/s02_subsolo_reliquia.png)
* [Mapa completo](../capturas/s02_mapa_completo.png)

O recorte vertical do cenário e a máscara usam a mesma `camera_y`. Lume, projéteis e efeitos são desenhados nas coordenadas do mundo antes do recorte; o HUD e a indicação de rumo usam coordenadas da tela. A planagem de dez segundos, as três relíquias e o retorno do subsolo estão cobertos pelos testes de integração.

| Cena, 960 × 540 | Mediana do desenho | Percentil 95 |
|---|---:|---:|
| Superfície do Córrego | 1,184 ms | 2,617 ms |
| Câmara inferior do Córrego | 5,532 ms | 6,333 ms |

Esta amostra usa o backend SDL `dummy`, vinte desenhos para aquecer caches e trezentos desenhos medidos por cena, incluindo HUD. O relógio de animação avança 1/60 s entre amostras. Simulação, áudio, espera por quadro e apresentação na tela (`flip`) ficam fora do intervalo medido. Nesta execução o subsolo teve mediana aproximadamente 4,7 vezes maior. Os valores medem este processo local e não são uma promessa de taxa de quadros ou desempenho em outro computador.
