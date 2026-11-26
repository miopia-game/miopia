# Movimento da fauna

As 35 sequências contêm 60 quadros cada. O gerador em Pillow articula as pinturas originais de Miopia. As patas de apoio, o ventre das serpentes e os dois ombros da Coruja têm referências próprias. Nas criaturas grandes, o preparo conserva o dobro da resolução da fonte de movimento anterior. As três folhas PNG antigas de Lume permanecem no acervo. O protagonista jogável usa os atlas em `assets/arte/lume/`.

O jogo localiza cada quadro RGBA por índice dentro do pacote ZIP da sequência. Dessa forma o primeiro golpe de um guardião pode ler apenas sua pose atual. A descompressão usa a biblioteca padrão de Python. As formas dos efeitos, a cor e a duração dos rastros são calculadas no Pygame CE. [Gerador](../../../tools/gerar_movimento.py) · [Leitura no jogo](../../../src/movimento_arte.py) · [Efeitos](../../../src/arte_golpes_fauna.py)

As poses-base vieram das pinturas de fauna do projeto. As peças da Coruja e as serpentes em percurso vieram das ilustrações geradas com ImageGen para as rodadas anteriores. [Origem e prompts](../../../docs/arte/prompts-fauna.md) · [Fontes de movimento](../../../tools/fontes)
