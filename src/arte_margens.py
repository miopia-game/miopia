"""Margens pintadas para os quatro biomas, ancoradas na superfície de pouso."""
from functools import lru_cache

from . import pygame_hd as pygame
from .ilustracao import imagem, original

# Mesma tinta da borda inferior da pintura de cada solo.
SUBSOLO = ((32, 30, 39), (30, 38, 45), (48, 37, 36), (39, 29, 44))
LARGURA = 820
ALTURA = 61


@lru_cache(maxsize=4)
def _faixa(bioma):
    # A terra é sólida. Uma superfície RGB mantém a oclusão após a redução do PNG.
    opaca = pygame.Surface((LARGURA, ALTURA))
    opaca.blit(imagem(f"margens/solo-{bioma}.png", LARGURA, ALTURA), (0, 0))
    return opaca


def preparar(bioma):
    _faixa(bioma)
    original(f"margens/patamar-{bioma}.png")
    original(f"beiral_{bioma}.png")


def chao(s, r, bioma):
    """Recorta a faixa na câmera e mantém a emenda fixa no espaço do mundo."""
    s = pygame.destino(s)
    area = s.get_clip().clip(r)
    if not area.width or not area.height:
        return
    s.fill(SUBSOLO[bioma], area)
    if area.top >= r.y + ALTURA:
        return
    primeira = (area.left - r.x) // LARGURA
    ultima = (area.right - 1 - r.x) // LARGURA
    trecho = _faixa(bioma)
    for indice in range(primeira, ultima + 1):
        x = r.x + indice * LARGURA
        largura = min(LARGURA, r.right - x)
        s.blit(trecho, (x, r.y), (0, 0, largura, min(r.h, ALTURA)))


def patamar(s, r, bioma, espelho):
    altura = max(19, min(48, round(r.w * .18)))
    arte = imagem(f"margens/patamar-{bioma}.png", r.w + 6, altura, espelho)
    # A linha de apoio da arte está a 12% da altura; pontas irregulares passam da caixa.
    pygame.blit(s, arte, (r.x - 3, r.y - round(altura * .12)))
