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


@pytest.mark.parametrize("visibilidade, foco, esperados", [
    ([True, False, False, True], [True] * 4, [10, 40]),
    # O compositor ainda informa "visível" durante a saída da Mesa.
    ([True] * 5, [True, False, False, False, True], [10, 20, 50]),
    # A pausa se reapresenta ao voltar para a Mesa ainda sem foco.
    ([True, True, False, True, True, True], [True, False, False, False, False, True], [10, 20, 40, 60]),
])
def test_janela_reapresenta_o_quadro_atual_ao_voltar(visibilidade, foco, esperados):
    from unittest.mock import Mock

    janela = Janela.__new__(Janela)
    janela.nativa = SimpleNamespace(handle=7)
    janela.renderer = Mock()
    janela.renderer.get_viewport.return_value = pygame.Rect((0, 0), QUADRO)
    janela.textura = Mock()
    janela._visivel = Mock(side_effect=visibilidade)
    janela._apresentou_sem_foco = False
    quadro = pygame.Surface(QUADRO, depth=32)
    cores = []
    janela.textura.update.side_effect = lambda pixels: cores.append(pixels.get_at((0, 0)).r)

    enviados = []
    for i, em_foco in enumerate(foco, start=1):
        janela.nativa.focused = em_foco
        vermelho = i * 10
        quadro.set_at((0, 0), (vermelho, 0, 0))
        enviados.append(janela.apresentar(quadro))

    assert enviados == [i * 10 in esperados for i in range(1, len(foco) + 1)]
    assert cores == esperados
    assert janela.renderer.present.call_count == janela.textura.draw.call_count == len(esperados)
