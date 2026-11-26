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
