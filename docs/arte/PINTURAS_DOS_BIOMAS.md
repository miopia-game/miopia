# As quatro pinturas da campanha

No Bosque, a luz da lua recorta as frondes contra a figueira oca. No Córrego, os fios de água clara separam as raízes do barranco. No Taquaral, os colmos inclinados e as folhas em lâmina fecham o caminho. Na Gruta, a abertura azul ilumina a abóbada violeta. O elenco serviu de referência para a espessura dos contornos, as pontas de pincel e as sombras em áreas de cor. O âmbar mais luminoso continua reservado para a ação. [Folha do elenco](../../assets/arte/bosque_elenco_atlas.png)

| Cenário | Pintura de tela, 1920 × 1080 | Panorama de câmera, 2560 × 1440 | Mestre editável | Caminhos vetoriais |
|---|---|---|---|---:|
| Bosque das Samambaias | [JPG](../../assets/arte/fundo_0.jpg) | [JPG](../../assets/arte/panoramas/bosque.jpg) | [SVGZ](fontes/panoramas/bosque.svgz) | 3.800 |
| Córrego Fundo | [JPG](../../assets/arte/fundo_1.jpg) | [JPG](../../assets/arte/panoramas/corrego.jpg) | [SVGZ](fontes/panoramas/corrego.svgz) | 4.085 |
| Taquaral | [JPG](../../assets/arte/fundo_2.jpg) | [JPG](../../assets/arte/panoramas/taquaral.jpg) | [SVGZ](fontes/panoramas/taquaral.svgz) | 7.341 |
| Gruta da Figueira | [JPG](../../assets/arte/fundo_3.jpg) | [JPG](../../assets/arte/panoramas/gruta.jpg) | [SVGZ](fontes/panoramas/gruta.svgz) | 2.652 |

## Da composição à tela

As quatro composições foram geradas com OpenAI ImageGen. Cada chamada recebeu a folha do elenco e a pintura do bioma na revisão `206a09b` como referências. As imagens iniciais vieram em 1672 × 941. Para manter as bordas limpas nas duas saídas, os planos de cor foram convertidos em caminhos de Bézier com VTracer 0.6.15. Os quatro SVGZ contêm os caminhos editáveis, e cada JPG é rasterizado diretamente do seu mestre com resvg-py. O exportador usa JPEG 96 sem subamostragem de cor. [Exportador](../../tools/exportar_pinturas.py)

A campanha mostra uma janela de 1920 × 1080 do panorama com margem para a câmera. O terreno e Lume passam mais rápido que o fundo. A máscara de luz continua a ocultar o que Lume ainda não iluminou. Na pintura distante, a névoa altera a cor e a luminosidade preservando os contornos. A abertura de Véspera e as salas verticais têm composições próprias. [Compositor da campanha](../../src/paisagem.py)

## Repetir o playtest

A gravação abre uma partida descartável por bioma. Os quatro pontos iniciais são preparados e a câmera se estabiliza. Daí em diante, o piloto envia os comandos de andar, pular, lançar a fagulha, golpear e acionar o clarão. Cada capítulo dura oito segundos. O arquivo de cada fase inclui o trajeto e quatro quadros integrais em PNG. O comparativo usa recortes em escala 1:1 do mesmo quadro da base e da nova versão, com os mesmos comandos e brilho. [Vídeo com quatro capítulos](../midia/quatro-pinturas-em-jogo.mp4) · [Antes e depois](../midia/quatro-pinturas-antes-e-depois.png)

Na raiz do projeto, com o ambiente virtual ativado, execute os comandos abaixo. O primeiro instala apenas as ferramentas para trabalhar na arte. O segundo recria os oito JPGs e o terceiro reproduz a gravação.

```sh
python -m pip install -r requirements.txt -r requirements-arte.txt
python tools/exportar_pinturas.py
python -m tools.gravar_pinturas --saida work/quatro-pinturas
```

## Prompts de produção

A instrução comum foi enviada junto com o trecho do bioma correspondente.

### Direção comum

Create one new, finished continuous widescreen environmental background painting, 16:9 landscape, 3072×1728 or larger high-resolution master for a 1920×1080 scrolling 2D platform game. Stylized-concept environmental animation layout art for the original game Miopia. Reference #1 is ONLY the project's own style model sheet: reproduce its purposeful irregular dark plum ink outlines, tapered strokes, sharp angular shadows, restrained opaque gouache color planes and sparse small hand-painted cuts. Do not paint any of the characters or objects in the sheet. Reference #2 is ONLY for the identity/geography of this biome; fully REPAINT in the sharper animation style, do not reproduce its engraving, speckle, airbrushed distance, noise or low-resolution texture. Brazilian Atlantic forest seen at a firefly's scale. A full-bleed continuous piece with a left, middle and right landmark that can be seen as the side camera tracks. Keep the center and lower-middle legible behind the action, interesting details in the flanks and silhouette, crisp clean gradients of VALUE by depth, hard well-designed edges even at distance. Clear open negative space, high craft. Muted midvalues that survive the game's own night lighting; the playable characters and amber sparks remain the brightest elements. Distant implied forms, no horizontal walkable-looking ledges in foreground, no game platforms, no characters/animals, no floating lights, no text/logos/UI, no borders, no panels. Classic hand-inked animation matte painting; absolutely no depth-of-field blur/bloom, woodcut crosshatching or noise.

### Bosque das Samambaias

BOSQUE DAS SAMAMBAIAS. An intimate green-blue fern ravine at nightfall. Leaning old fig tree with braided fluting and a few warm-copper scars on the far left, luminous negative space of a moonlit turquoise notch among distant crowns off-centre, distinct crowns of giant sharply serrated ferns at right. Show leaflets as tapered grouped shapes with elegant engraved central veins, an occasional hanging root, moss on bark planes, hints of dry bronze curled fern fronds around the edges. Cool deep pine, oxidized teal, muted sage mids and sparse parchment accents. Lateral view, crown opening in middle upper third, subtle overlap echoing the colors of the mossy cloaked NPC.

### Córrego Fundo

CÓRREGO FUNDO. A drought-stricken forest stream gorge after dusk, as seen from the side. Split runnels plunge as two thin stylized pale celadon waterfalls down stepped slate in the left half; dark exposed waterlines on rust-red basalt, a still blue-green pool catching broken sharp horizontal reflections through the center. An old tree gripping the right bank with distinct thick interlaced roots over damp rock. Retreating water has left seams of mineral color. Distinct silhouettes and shapes; make the eyes follow a lazy S with the stream. Color deep petrol, washed jade, peacock teal and mineral blue; tiny ochre touches matching the character model. Falling waters are broken ink-edged ribbons with clear planes, no white glare, fog or mist.

### Taquaral

TAQUARAL. A wind-leaning thicket of Brazilian native bamboo in the dry season, warm and uneasy. Chunky jointed olive-and-ochre culms rake diagonally from the lower left toward the upper middle. A broken hollow culm and curled parchment sheaths tucked at far left. An open amber/copper atmospheric clearing in the center with two gently rising distant ridges. Taller slimmer bamboo recedes off to the right, where sprays of spear-shaped leaves are silhouetted against a muted golden sky. Make every node and the alternating leaf clusters intentional. Color deep plum shadows, muted olive greens, bronze, mustard ochre and toasted maize. Cel-painted light on one side of each cane. No temple structures or Asian garden motifs.

### Gruta da Figueira

GRUTA DA FIGUEIRA. Underground cave hollowed between the buttress roots of an ancient fig. A long descending arched vault of violet slate and dark folded roots. Massive pale-plum twisted root buttresses with angular bark facets on the far left, a still black-violet pool leading toward an offset cold mineral-blue aperture in the middle-right, toothlike hanging rootlets tracing the ceiling at right. Echo the shapes of the moth's cloak in the curved rock planes, drawing the ribbed roots as overlapping ink shapes and the reflection as broken quiet bands. Palette deep aubergine and mulberry, muted lilac mineral planes, restrained cool turquoise at the distant cleft. No bright crystals, torches, architecture, vapor, monsters or skulls.
