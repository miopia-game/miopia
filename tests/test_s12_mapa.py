"""O mapa panorâmico conserva a máscara de descoberta com poucos desenhos."""
import math
from unittest.mock import patch

import pygame

from src.corte_vertical import entrar
from src.descoberta import TAMANHO, chave
from src.mapa_visor import QUADRO


def test_arrastar_mapa_parcial_preserva_mascara_em_faixas(app):
    app.iniciar('historia')
    app.jogar()
    j = app.jogo
    entrar(j, 'jardim')
    # Intervalos separados de descoberta na mesma coluna e em outra região.
    j.explorado.update(chave(j, x, y) for x in range(2400, 2640, TAMANHO)
                       for y in (576, 600, 744, 768, 792))
    j.explorado.add('0:0/100/28')
    antes = j.salvar()

    centro = QUADRO.center
    for evento in (
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_m),
        pygame.event.Event(pygame.MOUSEWHEEL, y=-3, pos=centro),
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=centro),
        pygame.event.Event(pygame.MOUSEMOTION, pos=(centro[0], centro[1]-31), rel=(0, -31)),
        pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=centro),
    ):
        pygame.event.post(evento)
    for evento in pygame.event.get():
        app.evento(evento)
    assert app.estado == 'diario'

    # Captura somente as operações que apagam terreno desconhecido.
    cor = (12, 22, 24)
    mascara = pygame.Surface(QUADRO.size)
    desenhar_rect = pygame.draw.rect
    operacoes = 0

    def contar(tela, cor_rect, rect, *args, **kwargs):
        nonlocal operacoes
        if tela is app.mapa_visor.camada and cor_rect == cor and rect != tela.get_rect():
            operacoes += 1
            desenhar_rect(mascara, cor, rect)
        return desenhar_rect(tela, cor_rect, rect, *args, **kwargs)

    with patch.object(pygame.draw, 'rect', side_effect=contar):
        app.desenhar()

    from src.cartografia import dimensoes
    mundo = app.mapa_visor.janela(j)
    largura, altura = dimensoes(j)
    esperado = pygame.Surface(QUADRO.size)
    for x in range(0, largura, TAMANHO):
        for y in range(0, altura, TAMANHO):
            if (x >= mundo.right or y >= mundo.bottom
                    or x+TAMANHO <= mundo.left or y+TAMANHO <= mundo.top
                    or chave(j, x, y) in j.explorado):
                continue
            left = round((x-mundo.x) * (QUADRO.w/mundo.w))
            right = round((x+TAMANHO-mundo.x) * (QUADRO.w/mundo.w))
            top = round((y-mundo.y) * (QUADRO.h/mundo.h))
            bottom = round((y+TAMANHO-mundo.y) * (QUADRO.h/mundo.h))
            desenhar_rect(esperado, cor, (left, top, right-left+1, bottom-top+1))
    assert pygame.image.tobytes(mascara, 'RGB') == pygame.image.tobytes(esperado, 'RGB')
    assert j.salvar() == antes
    assert operacoes <= math.ceil(largura/TAMANHO) + len(j.explorado)
