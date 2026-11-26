"""Vida, brilho e progresso da raiz, com os mesmos sinais em cada bioma."""
from functools import lru_cache
from math import pi

from . import pygame_hd as pygame

from .ilustracao import AMBAR, OSSO, PALIDO, alto_contraste, imagem, numeros_hud, sprite, texto

ORVALHO = (160, 218, 204)


@lru_cache(maxsize=2)
def _fundo(contraste):
    s = pygame.Surface((202, 72), pygame.SRCALPHA)
    for x in range(s.get_width()):
        opacidade = round((235 if contraste else 167)*(1-(x/s.get_width())**3))
        pygame.draw.line(s, (9, 13, 26, opacidade), (x,0), (x,71))
    return s


@lru_cache(maxsize=4)
def _gota(cheia, contraste):
    s = pygame.Surface((32, 38), pygame.SRCALPHA)
    pontos = [(16, 2), (23, 13), (28, 22), (28, 27), (24, 33),
              (16, 36), (8, 33), (4, 27), (4, 22), (9, 13)]
    borda = ORVALHO if cheia or contraste else (112, 151, 142)
    pygame.draw.polygon(s, (49, 114, 105) if cheia else (17, 25, 23), pontos)
    pygame.draw.polygon(s, borda, pontos, 3)
    if cheia:
        pygame.draw.ellipse(s, (219, 251, 235), (9, 20, 6, 10))
    return pygame.transform.smoothscale(s, (11, 13))


@lru_cache(maxsize=1)
def _abdomen():
    aceso = imagem("hud_abdomen.png",22,35).copy()
    escuro = aceso.copy()
    escuro.fill((122,116,146),special_flags=pygame.BLEND_RGB_MULT)
    luz = aceso.copy()
    luz.fill((144,84,12),special_flags=pygame.BLEND_RGB_ADD)
    return escuro, luz


def desenhar(s, j):
    s = pygame.destino(s)
    contraste = alto_contraste()
    s.blit(_fundo(contraste),(17,13))
    vida = j.lume.vida
    asa = "hud_asa" if vida > 64 else "hud_asa_ferida" if vida > 30 else "hud_asa_critica"
    sprite(s,asa,44,50,35,29)
    escuro, luz = _abdomen()
    s.blit(escuro,(83,15))
    cheio = round(28*max(0.,min(100.,j.lume.energia))/100)
    if cheio:
        y = 33-cheio
        s.blit(luz,(83,15+y),(0,y,22,cheio))

    if j.fagulha_ativa:
        r = j.fagulha_ativa.restante(j.tempo)
        sprite(s,"hud_fagulha",119,35,12,13)
        pygame.draw.arc(s,AMBAR,(108,18,22,22),pi/2,pi/2+2*pi*r,2)

    sprite(s,"hud_folha",157,50,47,30)
    gotas = min(j.orvalhos,3)
    for i in range(3):
        s.blit(_gota(i < gotas, contraste),(140+i*12,30))
    precisao = numeros_hud()
    for nome, valor, x in (("Vida", round(vida), 44), ("Brilho", round(j.lume.energia), 94),
                            ("Orvalho", f"{gotas}/3", 157)):
        rotulo = f"{nome} {valor}" if precisao else nome
        texto(s,rotulo,x,52,11,OSSO,alinhar="centerx")
    texto(s,f"Tentativas {j.lume.vidas}",24,69,10,PALIDO)
