# Arte da revisão jogável

A versão do protagonista com máscara de semente, antenas de folha e lenço vermelho foi ilustrada com OpenAI ImageGen a partir de Mimo, Nira e Véspera do próprio jogo. As fontes são a [guarda](fontes/lume/guarda.png) e as [quatro poses de ação](fontes/lume/acoes.png). O gerador articula as botas, desenha as duas membranas de voo e conserva a posição do âmbar em cada quadro. Com as dependências de arte instaladas, rode `.venv/bin/python tools/animar_lume.py` a partir da raiz. [Gerador](../../tools/animar_lume.py) · [Uso no jogo](../../src/arte_lume.py)

As margens de mata, pedra molhada, bambu e xisto foram ilustradas com OpenAI ImageGen a partir da paleta das quatro pinturas locais. A preparação alinha a borda jogável, une a faixa de solo e conserva as duas extremidades dos patamares. Rode `.venv/bin/python tools/preparar_margens.py` para regenerar os oito recortes. [Pintura em faixas](fontes/panoramas/margens.png) · [Preparação](../../tools/preparar_margens.py)

Lume, Mimo, Nira, Véspera, o HUD e os objetos da abertura foram ilustrados para Miopia com OpenAI ImageGen. Os atlases em `assets/arte/` guardam as folhas. A composição, as colisões, a orientação, a máscara de luz e os efeitos são montados no jogo com Pygame CE. [Acervo do jogo](../../assets/arte) · [Composição do Bosque](../../src/arte_ilustrada.py)

As pinturas do Bosque, Córrego, Taquaral e Gruta foram recompostas com OpenAI ImageGen usando o elenco e as paisagens anteriores como referências. As formas coloridas foram vetorizadas com VTracer e exportadas separadamente para a câmera e o prólogo. [Fontes editáveis, referências e prompts](PINTURAS_DOS_BIOMAS.md)

Os 12 modelos da fauna foram redesenhados a partir do elenco do projeto. As três folhas de produção têm quatro criaturas e três poses cada. Os desenhos da Coruja em voo e das cobras em percurso complementam as articulações. A criação e o recorte são etapas de desenvolvimento e os PNGs gerados acompanham a versão jogável. [Folhas e guia de cor](fontes) · [Prompts](prompts-fauna.md) · [Fontes de movimento](../../tools/fontes) · [Como regenerar](../equipe/BIBLIOTECAS.md)

Os seis integrantes aparecem nos [créditos do jogo](../../src/telas.py). O registro de origens da equipe documenta também os recursos herdados da base acadêmica e os itens pendentes de avaliação para outros usos. Os avisos de fontes acompanham os arquivos distribuídos. [Registro da base acadêmica](../s00-origens.md) · [Licenças das fontes](../../assets/fontes)

O rastro de voo, a luz refletida e os veios acesos no pouso da fagulha são desenhados em Pygame sobre as pinturas da equipe. Os sons de disparo e de contato são sínteses originais com osciladores e ruído de semente fixa. [Arte da fagulha](../../src/arte_fagulha.py) · [Gerador dos dois sons](../../tools/gerar_sons_fagulha.py)
