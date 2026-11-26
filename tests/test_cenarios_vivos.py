import pygame
import pytest

from src import paisagem
from src import pygame_hd as hd


# Os centros são da composição 960 × 540. A comparação usa um recorte interno
# de 192 × 192 pixels físicos para excluir o limite de desenho da superfície.
@pytest.mark.parametrize(
    "etapa,centro,instantes",
    [
        (0, (625, 381), (0.4, 2.8)),  # ponta da samambaia
        (1, (157, 260), (0.05, 0.63)),  # veio claro da primeira queda
        (2, (479, 169), (0.4, 2.8)),  # ramo de bambu
        (3, (488, 431), (0.10, 1.36)),  # anel e intervalo seco da mesma goteira
    ],
)
def test_movimento_local_segue_pintura_e_reproduz_pose(etapa, centro, instantes):
    ox, oy = (80 - x * 4 / 3 for x in centro)

    def pintar(t, deslocamento=0):
        quadro = hd.Surface((160 + deslocamento, 160))
        paisagem.desenhar_panorama(quadro, etapa, (ox + deslocamento, oy), t)
        return pygame.image.tobytes(
            quadro.pixels.subsurface((64 + 2 * deslocamento, 64, 192, 192)), "RGB"
        )

    primeiro = pintar(instantes[0])
    assert primeiro != pintar(instantes[1])
    assert primeiro == pintar(instantes[0], deslocamento=13)
    assert primeiro == pintar(instantes[0])


def test_fundo_de_repouso_continua_integro(app):
    original = paisagem.fundo(0)
    area = pygame.Rect(1590, 970, 120, 120)
    antes = pygame.image.tobytes(original.pixels.subsurface(area), "RGB")
    app.iniciar("historia")
    app.jogar()
    j = app.jogo
    j.recolocar((2944, 370))
    for _ in range(4):
        app.atualizar(1 / 60)
        app.desenhar()
    assert antes == pygame.image.tobytes(original.pixels.subsurface(area), "RGB")
