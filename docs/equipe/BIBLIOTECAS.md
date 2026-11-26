# Bibliotecas e ferramentas do Miopia

Para jogar, instale Python e as dependências de `requirements.txt`. As figuras já estão recortadas, as animações estão em PNG e os sons vêm prontos. As outras instalações abaixo dependem do trabalho que você assumir.

| Componente | Papel no projeto | Onde conferir |
|---|---|---|
| Python (3.10–3.14 nos lançadores) | Linguagem da campanha e das ferramentas. `sqlite3` grava progresso e preferências. `wave` e `array` geram áudio nos scripts que usam a biblioteca padrão. | [Python](https://www.python.org/) · [Persistência](../../src/memoria.py) |
| Pygame CE 2.5.8 | Única dependência externa da partida. Abre a janela SDL, lê teclado/controle, toca o áudio e desenha cenário, máscaras de luz, sprites e HUD. | [Pygame CE](https://pyga.me/) · [App](../../src/main.py) · [Versão fixada](../../requirements.txt) |
| pytest 9.2.0 | Exercita campanha, combates, movimento, menus, saves e ferramentas. | [pytest](https://docs.pytest.org/) · [Suíte](../../tests) |
| Pillow 13.0.0 no ambiente de revisão | Recorta as folhas transparentes, articula membros e exporta os quadros das animações. No código os imports usam `PIL`. | [Pillow](https://pillow.readthedocs.io/) · [Recorte](../../tools/recortar_elenco.py) · [Movimento](../../tools/gerar_movimento.py) |
| imageio-ffmpeg 0.8.1 e FFmpeg | O pacote fornece o executável que recebe os quadros RGB da App e codifica o MP4 H.264. A simulação roda a 60 passos/s e a gravação captura um quadro a cada dois passos. | [imageio-ffmpeg](https://pypi.org/project/imageio-ffmpeg/) · [FFmpeg](https://ffmpeg.org/) · [Gravador do Bosque](../../tools/gravar_bosque.py) |
| NumPy | Dependência opcional do gerador de áudio antigo. Necessária apenas para regenerar aquele material. | [NumPy](https://numpy.org/) · [Gerador que o importa](../../tools/gerar_audio.py) |
| Tiled 1.12.2 e PyTMX 3.32 | No estudo de ferramentas, o Tiled exportou uma camada de objetos e o PyTMX leu um mapa TMX. A geometria usada pela campanha continua definida em Python. | [Tiled](https://www.mapeditor.org/) · [PyTMX](https://pytmx.readthedocs.io/) · [Geometria das fases](../../src/fases.py) |
| ModernGL 5.13.0 | O protótipo verificou um desenho em framebuffer OpenGL no Mac. O renderizador da campanha usa superfícies e máscaras do Pygame CE. | [ModernGL](https://moderngl.readthedocs.io/) · [Renderizador atual](../../src/paisagem.py) |
| Aseprite 1.3.18.6 no Mac de produção | Editor instalado e testado com leitura de folha e exportação de PNG RGBA. As folhas reproduzíveis desta versão são geradas pelo script com Pillow. | [Aseprite](https://www.aseprite.org/) · [Registro das ferramentas](S40.md) |
| OpenAI ImageGen | Ferramenta de produção dos desenhos e folhas-base. A partida usa os arquivos locais. | [Fontes da arte](../arte/ORIGEM.md) · [Prompts da fauna](../arte/prompts-fauna.md) |

## Instalar conforme a tarefa

Em um ambiente virtual ativado, use um dos comandos abaixo na raiz do projeto.

```sh
# Jogar
python -m pip install -r requirements.txt

# Desenvolver e testar
python -m pip install -r requirements-dev.txt

# Trabalhar com os sprites e gravar o playtest
python -m pip install -r requirements-dev.txt -r requirements-arte.txt

# Repetir os experimentos de mapa e OpenGL
python -m pip install PyTMX==3.32 ModernGL==5.13.0

# Regenerar o áudio histórico
python -m pip install numpy
```

O Tiled e o Aseprite são aplicativos de desktop. Quem for repetir os experimentos pode obter os editores pelos sites da tabela. As dependências transitivas, como `glcontext` para ModernGL, são resolvidas pelo instalador.

## Refazer as animações ou a gravação

Execute na raiz do projeto, em uma branch de trabalho. Os dois primeiros comandos sobrescrevem os PNGs derivados. Revise o diff antes de guardar o resultado.

```sh
python tools/recortar_elenco.py docs/arte/fontes assets/arte/inimigos-v2
python tools/gerar_movimento.py
python -m tools.gravar_bosque --saida work/entrega/previa
```

O gravador começa pela História com um perfil descartável, verifica o pouso da fagulha e o abate, grava a imagem em 960 × 540 e decodifica o vídeo para conferir o arquivo. O MP4 é silencioso. Para avaliar som e tempo de reação com controle físico, abra a partida normalmente.
