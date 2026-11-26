"""Ilustrações de casca compartilhadas pelo terreno e pelas passagens."""
from functools import lru_cache

from . import arte_margens
from . import pygame_hd as pygame

from .ilustracao import AMBAR, alto_contraste, imagem, sprite

def galho(s, r, bioma, variante, *, raiz=False):
    if raiz:
        s.blit(imagem("galho_enraizado.png", r.w+28, 96), (r.x-23, r.y-31))
    else:
        arte_margens.patamar(s, r, bioma, variante)
    if alto_contraste():
        pygame.draw.line(s, (213, 199, 156), (r.x+2, r.y), (r.right-3, r.y), 2)


@lru_cache(maxsize=1)
def _liquen():
    trecho = imagem("galho_enraizado.png", 158, 96).subsurface((25, 29, 40, 15)).copy()
    s = pygame.Surface(trecho.get_size(), pygame.SRCALPHA)
    for x in range(s.get_width()):
        alfa = min(135, x*35, (s.get_width()-1-x)*23)
        pygame.draw.line(s, (255, 255, 255, alfa), (x, 0), (x, 14))
    trecho.blit(s, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return trecho


def liquen(s, x, y):
    s.blit(_liquen(), (x+2, y-2))
    pygame.draw.lines(s, (158, 143, 100), False,
                      [(x+8, y+2), (x+13, y), (x+24, y), (x+31, y+1)])


def broto(s, r):
    s.blit(imagem("galho_broto.png", r.w+8, 25), (r.x-4, r.y-10))


def passagem(s, x, y, subterranea=True):
    """A mesma boca de raiz marca as duas pontas do desvio."""
    sprite(s, "passagem_raizes", x, y+4, 174, 66, not subterranea)


def marco_de_trilha(s, x, y, retorno):
    x, y = round(x), round(y)
    sprite(s, "obj_marco", x, y, 29, 48, retorno)
    d = -1 if retorno else 1
    xx, yy = x+d*6, y-25
    pygame.draw.lines(s, (37, 32, 23), False,
                      [(xx-5*d, yy-5), (xx+3*d, yy), (xx-5*d, yy+5)], 4)
    pygame.draw.lines(s, AMBAR, False,
                      [(xx-5*d, yy-5), (xx+3*d, yy), (xx-5*d, yy+5)], 2)
