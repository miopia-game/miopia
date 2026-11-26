"""Conversão dos pontos do mouse para o jogo em monitores 1× e Retina."""
from types import SimpleNamespace

import pygame
import pytest

from src.janela_hd import QUADRO, Janela, area_de_jogo


@pytest.mark.parametrize('pontos,pixels,centro,origem', [
    ((1920,1080), (1920,1080), (960,540), (0,0)),
    ((960,540), (1920,1080), (480,270), (0,0)),
    ((1920,1200), (1920,1200), (960,600), (0,60)),
    ((720,540), (720,540), (360,271), (0,68)),
    ((1512,982), (3024,1964), (756,491), (276,221)),
])
def test_regiao_visivel_e_coordenadas_do_ponteiro(pontos,pixels,centro,origem,monkeypatch):
    janela=Janela.__new__(Janela)
    janela.nativa=SimpleNamespace(size=pontos)
    janela.renderer=SimpleNamespace(get_viewport=lambda:pygame.Rect((0,0),pixels))
    area=area_de_jogo(pixels)
    assert area.w <= QUADRO[0] and area.h <= QUADRO[1]
    assert janela._posicao_logica(centro) == (480,270)
    assert janela._posicao_logica(origem) == (0,0)
    assert janela._posicao_logica((origem[0]-2,origem[1]-2))[0] < 0
    wheel=pygame.event.Event(pygame.MOUSEWHEEL, x=0,y=1,mouse_x=centro[0],mouse_y=centro[1])
    convertido=janela.evento_logico(wheel)
    assert convertido.pos == (480,270) and convertido.y == 1
    assert not hasattr(wheel, 'pos')
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda:centro)
    roda_sem_pos=pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=1, pos=None)
    assert janela.evento_logico(roda_sem_pos).pos == (480,270)
    assert janela.evento_logico(pygame.event.Event(pygame.WINDOWCLOSE)).type == pygame.QUIT
