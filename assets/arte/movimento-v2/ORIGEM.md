# Movimento da fauna

Os 12 modelos usam 37 sequências com 16 desenhos completos em cada uma. Cada folha em PNG foi ilustrada com OpenAI ImageGen a partir das pinturas destes personagens de Miopia. As criaturas da ponte, da galeria e da ninhada compartilham o modelo da espécie. [Folhas originais e registro dos recortes](../../../docs/arte/fontes/fauna-quadros)

O registro descreve o retângulo de cada desenho, sua posição na célula e uma escala uniforme para a folha inteira. A Coruja usa as duas asas e a cabeça da mesma pintura. As patas e o ventre encostam no piso, enquanto os morcegos em repouso se prendem pelo alto. Para reconstruir os pacotes com Pillow, execute `.venv/bin/python tools/gerar_movimento.py` na raiz do projeto. [Empacotador](../../../tools/gerar_movimento.py)

O jogo escolhe a passada pelo deslocamento, a batida de asas pelo tempo e o desenho do ataque pelo estado da IA. Lê um quadro RGBA por vez do ZIP. Os avisos, a seda, o ferrão, a onda, o veneno e as penas continuam ligados ao combate. [Seleção das poses](../../../src/arte_inimigos.py) · [Leitura das células](../../../src/movimento_arte.py) · [Efeitos](../../../src/arte_golpes_fauna.py)
