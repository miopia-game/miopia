import pygame
import pytest

from src import paisagem
from src.fases import CHAO
from src.ilustracao import original


@pytest.mark.parametrize("etapa", range(4))
def test_quatro_pinturas_entram_na_campanha_sem_reduzir_a_resolucao(
    app, monkeypatch, etapa
):
    assert original(f"fundo_{etapa}.jpg").get_size() == (1920, 1080)
    panorama = paisagem.fundo(etapa)
    assert panorama.pixels.get_size() == (2560, 1440)
    # Confere uma porção do raster usado pela câmera contra os pixels do arquivo.
    nome = paisagem.PANORAMAS[etapa]
    arte = original(f"panoramas/{nome}.jpg")
    area = pygame.Rect(785, 345, 77, 39)
    esperado = arte.subsurface(area).copy()
    esperado.fill((191, 202, 211), special_flags=pygame.BLEND_RGB_MULT)
    assert pygame.image.tobytes(esperado, "RGB") == pygame.image.tobytes(
        panorama.pixels.subsurface(area), "RGB"
    )
    app.iniciar("historia")
    app.jogar()
    app.jogo.entrar(etapa)
    app.jogo.recolocar((2944 if etapa == 0 else 650, CHAO))
    opcoes = []
    nevoa = paisagem.nevoa_distante

    def observar(fundo, saida, amostra, nivel, cor=None, nitidez=0.0):
        opcoes.append((fundo.pixels.get_size(), nitidez))
        nevoa(fundo, saida, amostra, nivel, cor, nitidez)

    monkeypatch.setattr(paisagem, "nevoa_distante", observar)
    app.desenhar()
    assert opcoes == [((1920, 1080), 1.0)]


def test_composicao_hd_no_mundo_equivale_a_mascara_com_buffers(app):
    from src import pygame_hd as hd

    app.iniciar("historia")
    app.jogar()
    mundo = hd.Surface((960, 600))
    mundo.fill((173, 49, 213))
    fundo = hd.Surface((960, 540))
    fundo.fill((30, 190, 83))
    pygame.draw.circle(fundo.pixels, (170, 18, 240), (441, 558), 180)
    luz = hd.Surface((960, 540))
    referencia_luz = luz.copy()
    paisagem.compor_luz(referencia_luz, app.jogo, 0, 39, 1)
    referencia_luz.fill((46,) * 3, special_flags=pygame.BLEND_RGB_MAX)
    paisagem.compor_luz(luz, app.jogo, 0, 39, 1, minimo=46)
    assert pygame.image.tobytes(luz.pixels, "RGB") == pygame.image.tobytes(referencia_luz.pixels, "RGB")

    esperado = mundo.pixels.copy()
    area = pygame.Rect(0, 78, 1920, 1080)
    claro = esperado.subsurface(area).copy()
    inversa = pygame.Surface(area.size)
    inversa.fill("white")
    inversa.blit(luz.pixels, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
    distante = fundo.pixels.copy()
    distante.fill(paisagem.TINTAS_NEVOA[1], special_flags=pygame.BLEND_RGB_MULT)
    distante.blit(inversa, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    claro.blit(luz.pixels, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    claro.blit(distante, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    esperado.blit(claro, area)
    paisagem.aplicar_nevoa(mundo, luz, 39, fundo, nitidez=1., consumir_fundo=True)
    assert pygame.image.tobytes(esperado, "RGB") == pygame.image.tobytes(mundo.pixels, "RGB")
