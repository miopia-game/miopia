from types import SimpleNamespace

import pygame
import pytest

from src import arte_fagulha
from src.ilustracao import estilo
from src.travessia_fagulha import Fagulha


@pytest.mark.parametrize("suave", [False, True])
def test_reflexo_segue_luz_e_respeita_valor_da_pintura(suave):
    f = Fagulha(0, (40,85), (320,85))
    j = SimpleNamespace(fagulha_ativa=f, tempo=f.duracao_voo*.54)
    x, _ = f.posicao(j.tempo)
    cx = 13
    centro = round(x-cx)
    tela = pygame.Surface((370,180))
    tela.fill((60,60,60))
    tela.fill((12,12,12), (0,85,370,95))
    with estilo(dict(claroes_suaves=suave)):
        arte_fagulha.iluminar_cenario(tela, j, cx)
    claro = tela.get_at((centro,81))
    escuro = tela.get_at((centro,89))
    assert claro.r - 60 > escuro.r - 12 > 0
    assert claro.r > claro.g > claro.b
    assert tela.get_at((centro+36,80)).r > 60
    assert tela.get_at((320-cx,83))[:3] == (60,60,60)
    assert tela.get_at((40-cx,83))[:3] == (60,60,60)


def test_cauda_fica_atras_e_pouso_preserva_camera_vertical():
    f = Fagulha(20, (360,690), (120,690))
    instante = f.inicio + f.duracao_voo*.6
    tela = pygame.Surface((400,790))
    tela.set_clip((0,550,400,230))
    arte_fagulha.desenhar_voo(tela, f, instante, 10)
    x = round(f.posicao(instante)[0])-10
    assert sum(tela.get_at((x+20,690))[:3]) > 0
    assert tela.get_at((x-21,690))[:3] == (0,0,0)
    tela.fill((35,35,35))
    j = SimpleNamespace(fagulha_ativa=f, tempo=f.pouso_em+.09,
                        solidos=[SimpleNamespace(rect=pygame.Rect(84,694,160,20))])
    arte_fagulha.iluminar_cenario(tela,j,10)
    arte_fagulha.desenhar(tela,j,10)
    assert tela.get_at((110,688)).r > 150
    assert tela.get_at((110,150)).r == 0
