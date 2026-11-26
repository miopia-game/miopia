# Miopia — passagem de trabalho para a equipe

Comece pela branch **main**. Ela reúne a campanha S40 com a revisão de arte, interface, movimento e fagulha que Victor e a equipe vinham testando. Para conhecer a experiência de quem joga pela primeira vez, abra **História**, pule o prólogo se quiser e chegue ao primeiro morcego. Depois use **Campo de testes** para comparar os chefes. [Como instalar e jogar](../../README.md) · [Prévia da abertura](../midia/bosque-em-jogo.mp4)

## O que já está no jogo

| Área | O que mudou e onde experimentar | Por onde continuar no código |
|---|---|---|
| Lume e a mata em seca | O protagonista ganhou ilustração e movimento articulado. A câmera acompanha a exploração vertical, e as camadas de folhagem se deslocam em velocidades diferentes. O clarão revela terreno, e a escuridão varia com a acessibilidade. | [Lume](../../src/arte_lume.py) · [Cenário e iluminação](../../src/paisagem.py) |
| Abertura do Bosque | O primeiro galho se prende ao tronco. O broto iluminado abre uma rota para a mochila de Mimo. Há um cipó escalável, o mapa que Nira pede para ler e o galho de Véspera. A mochila é uma encomenda. Orvalho é coletado à parte, recupera brilho e alimenta a raiz. | [Abertura](../../src/abertura_bosque.py) · [Objetos e apoios](../../src/arte_ilustrada.py) · [Pedidos e diálogo](../../src/narrativa.py) |
| Interface e ensino | Asa, abdômen luminoso e gotas representam vida, brilho e orvalho. No primeiro trecho as dicas aparecem perto da ação. O mapa e o diário guardam informação que pode ser consultada depois. | [HUD](../../src/hud_reservas.py) · [Lição de Véspera](../../src/licao_vespera.py) · [Comandos e remapeamento](../../src/controles.py) |
| Fagulha na campanha | G dispara na direção do olhar. A luz passa pela vegetação, e um estalo espacial marca o contato. Custa 26 de brilho e ilumina por sete segundos após pousar. Ajuda a escolher a travessia, descobrir desvios do Córrego e da Gruta e alterar o comportamento das patrulhas. A marca alcançável dá retorno antes do lançamento. | [Trajetória e reações](../../src/travessia_fagulha.py) · [Desvios e persistência](../../src/desvios_fagulha.py) · [Vídeo da mecânica](../midia/fagulha-combate.mp4) |
| Inimigos e animação | Doze modelos redesenhados em 36 poses-base. Os pacotes de movimento da fauna têm 60 quadros por ciclo. A cria da Tecelã compartilha a arte da aranha em outra escala. Na coruja, as duas asas articulam e a cabeça conserva a forma. As cobras ondulam e os insetos terrestres alternam apoios. As patrulhas antecipam os ataques pela postura e pelos efeitos, sem desenhar o caminho da investida. | [Elenco lado a lado](../midia/elenco-no-render-do-jogo.png) · [Animação na partida](../../src/movimento_arte.py) · [Arte de ataque](../../src/arte_inimigos.py) |
| Exploração, campanha e saves | Bosque, Córrego, Taquaral e Gruta ligam raízes, sobreviventes, desvios e o desfecho. Checkpoints, descobertas e preferências usam armazenamento local. O Campo de testes permite repetir um trecho isolado. | [Fases](../../src/fases.py) · [Jornada](../../src/travessia.py) · [Persistência](../../src/memoria.py) · [Ensaios](../../src/ensaios.py) |

## O que observar nas lutas

| Guardião | Uso da fagulha | Registro da luta |
|---|---|---|
| Asa Fendida | Ilumine um patamar de resina e saia da faixa de voo. Ao atacar a isca, ela expõe o dorso, que Lume alcança pelo patamar. | [Vídeo](../midia/asa-luta-inteira.mp4) |
| Tecelã do Vão | Ilumine a seda marcada e atraia o fio para a luz. A seda queima e a Tecelã desce ao alcance do corte. | [Vídeo](../midia/tecela-luta-inteira.mp4) |
| Casco Oco | Aqueça a marca de seiva no centro e faça a carga atravessá-la. Use a abertura para saltar e golpear. | [Vídeo](../midia/casco-luta-inteira.mp4) |
| A Coruja | Mova o sino com E e use a marca para tocá-lo de longe. A Coruja segue o som. O clarão perto da face exposta completa o crítico. | [Vídeo](../midia/coruja-luta-inteira.mp4) |

As quatro gravações individuais e a rota até a Asa são registros das iterações de mecânica. A gravação em 17 capítulos mostra o elenco redesenhado, a cria e quatro variações da campanha. As métricas registram condições reproduzidas por um piloto automatizado. [Abertura até a Asa Fendida](../midia/bosque-ate-asa-fendida.mp4) · [Elenco atual em movimento](../midia/fauna-1080p60.mp4) · [Métricas dos guardiões](../midia/metricas-guardioes.json)

## Assumindo a próxima rodada

1. **Observe um primeiro contato.** Entregue o teclado a alguém que ainda não jogou. Peça para atravessar o Bosque e vencer o morcego. Anote o primeiro ponto em que a pessoa para, a ação que tentou e se percebeu o primeiro acerto. Faça perguntas depois da tentativa.
2. **Observe a esquiva e o contra-ataque.** No chão, Shift com Lume parado inicia um deslize na direção do olhar. Veja como a pessoa reage ao rasante e ao mergulho e em que momento tenta o primeiro corte. O combate guarda o próximo toque de J por até 0,22 segundo. [Fila de golpes](../../src/combate.py)
3. **Compare o cenário na partida.** Jogue a abertura em 1920 × 1080. Anote onde a pessoa reconhece o primeiro galho, o pouso da fagulha e as asas do morcego. Os vídeos mostram a mesma rota antes e depois da troca de pintura. [Abertura anterior](https://github.com/miopia-game/miopia/blob/49c06f1eed2e95edfd6bba050869bfaa09df330e/docs/midia/bosque-em-jogo.mp4) · [Abertura atual](../midia/bosque-em-jogo.mp4)
4. **Registre um resultado reproduzível.** Guarde o trecho, dificuldade, entrada usada e uma captura do mesmo instante. Rode o teste focal e a suíte. Em alterações de persistência, reabra um save e volte a um marco. Depois peça à mesma pessoa para repetir e a uma pessoa nova para experimentar sem instruções.

Para gerar uma prévia igual à desta entrega, use o comando do [guia de bibliotecas](BIBLIOTECAS.md). Para propor mudanças, abra sua branch a partir da main. As avaliações de clareza, sensação de combate e direção de arte ficam com a equipe. [Fila de trabalho](PLANO.md) · [Critérios de validação](VALIDACAO.md)
