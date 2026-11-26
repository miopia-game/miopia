# S02 e correções do teste da campanha

O teste de Thierry identificou orientação insuficiente, combate fraco, cenário claro demais, planeio curto e desvios sem recompensa. Esta rodada entrega correções jogáveis junto do seletor contextual da aranha. O parecer humano continua aberto.

## Ponte do Córrego

A roda da ponte já existia no Córrego, depois de Fio, em x1295. O salto duplo permitia passar pelo vão sem acioná-la. O ralo posterior exigia a ponte e respondia com uma instrução genérica. Além disso, o registro narrativo sobrescrevia o aviso que explicava o mecanismo.

Agora o próximo objetivo segue a primeira pendência real. Primeiro vem a roda elevada do dreno, depois a lingueta sob a raiz baixa, depois a roda da ponte e finalmente o ralo sob a grade. O ralo bloqueado informa onde voltar. Casca e Fio dão a mesma orientação que o mapa, e o descanso informa o próximo passo junto da recuperação da luz. Os IDs dos mecanismos e as flags dos saves foram preservados.

## Mapa e luz

O minimapa fica no alto, ao centro. Mostra Lume em âmbar, o destino em verde e os marcos em círculos. Tab abre diretamente a planta da região com o nome e a instrução do objetivo. Dentro do Corte, o mapa preserva a descoberta dos setores. Os demais locais mostram sua geometria, inclusive o novo subsolo do Córrego.

K ainda custa 22 de luz e ilumina uma região fixa por 6,5 segundos, fechando gradualmente. Durante os primeiros 2,8 segundos também surge um rastro que aponta o rumo do objetivo atual. A seta indica a direção do destino. A geometria do mapa explica a rota necessária para chegar lá.

O cenário inteiro recebe escuridão, incluindo terra, vegetação e fundo. O ajuste Noturno agora conserva cerca de 1–3% da intensidade dos canais RGB fora da luz. Os ajustes Médio e Alto continuam disponíveis. As entradas do Corte têm escadas escavadas na casca. Paredes de impulso usam desenho de troncos. O elevador de cipó apresenta estrado e polia e explica o bloqueio antes da abertura do ralo.

## Planagem e exploração contínua

Segurar Espaço durante a queda mantém a planagem enquanto houver espaço para descer. Não existe mais limite de 1,12 segundo nem consumo adicional por planar. Soltar Espaço ou segurar baixo volta à queda normal. O consumo passivo da luz e o risco de cair em um vão continuam existindo.

Depois do ralo do Córrego, a grade entre x2520 e x2680 dá acesso às Raízes Inferiores. Use S + Espaço. O chão do fundo fica em y1102, 660 px abaixo da superfície, dentro do mesmo mundo físico. A descida passa por sete patamares. Uma segunda coluna de galhos permite voltar pela grade de x2980 a x3095. Não há troca de região ao atravessar essas grades. A câmera acompanha o percurso.

No Campo de testes, **Raízes do Córrego** começa sobre a primeira grade. A membrana no fundo passa a ser o objetivo local. Após recolhê-la, o mapa indica a saída superior. Morrer retorna ao marco anterior e conserva a relíquia. O desvio é opcional e mantém as exigências da história principal.

## Recompensas dos desvios

As três relíquias funcionam automaticamente ao recolher com E e permanecem após morte e reabertura do save. Seus efeitos aparecem no mapa. Q e F continuam reservados às ferramentas e aos consumíveis.

| Relíquia | Local | Efeito |
|---|---|---|
| Espinho de acácia | Arquivo da Casca, ao lado do armário | +25% ao dano dos cortes contra criaturas comuns. Os chefes mantêm seus mecanismos próprios de exposição. |
| Membrana de libélula | Fundo das Raízes Inferiores do Córrego | +12% à velocidade horizontal ao andar e no ar. |
| Resina de âmbar | Patamar da placa dos berços, no Viveiro Afundado | −35% no consumo passivo da luz. Clarão e danos recebidos mantêm seus custos. |

## Como avaliar esta entrega

1. Feche a versão que está aberta e abra novamente o executável. Na campanha, vá ao Córrego. Confira se Tab e K permitem localizar a primeira pendência sem sair do bioma.
2. No Campo de testes, abra Raízes do Córrego. Desça pela grade, pegue a membrana e tente voltar pelos galhos da direita. No salto inicial da subida, use a segunda batida de asas.
3. Abra Duelo da aranha. Compare aproximação por cima da pedra, pelo chão e pelo galho. Mantenha a mesma semente para repetir as condições. V permite rever a última tentativa.

O [relatório do combate](s02-aranha.md) separa medições automáticas da avaliação humana. A planilha mantém os aceites de Thierry abertos.

## Trabalho que continua necessário

Esta rodada amplia a verticalidade contínua em um trecho do Córrego. O restante dos quatro biomas ainda precisa de desenho de mundo mais extenso, retornos e conexões naturais. O Corte continua sendo uma região opcional conectada por entradas. A qualidade visual dos cenários exige outra rodada de composição e animação.

A aranha recebeu mudanças de decisão e resistência. Os demais inimigos e os quatro chefes ainda precisam de rodadas próprias de variedade, dificuldade e comportamento. O S03 planeja aprofundar a leitura dos ataques. O balanceamento só será aceito depois de jogar.

Não foram adicionadas músicas, imagens ou bibliotecas externas nesta rodada. Os desenhos novos usam código local e recursos já presentes. As pendências de autoria e licença herdadas permanecem no quadro de direitos.
