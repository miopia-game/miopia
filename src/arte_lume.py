"""Quadros de Lume desenhados a partir de uma folha de quatro por dois."""
from functools import lru_cache
from math import pi, sin

from . import pygame_hd as pygame

from .ilustracao import original
from . import movimento_arte


POSES = {
    "parado": 0, "pulo": 3, "queda": 3, "planar": 4, "golpe": 5,
    "agachar": 6, "deslize": 6, "dano": 7, "clarao": 0, "corda": 3, "parede": 3,
}
PASSADAS = (1, 2, 1, 0)


@lru_cache(maxsize=1)
def _quadros():
    folha = original("lume_ilustrado_atlas.png")
    largura, altura = folha.get_width() // 4, folha.get_height() // 2
    poses = []
    for indice in range(8):
        linha, coluna = divmod(indice, 4)
        celula = folha.subsurface((coluna*largura, linha*altura, largura, altura))
        recorte = celula.get_bounding_rect(min_alpha=160).inflate(14, 14)
        poses.append(celula.subsurface(recorte.clip(celula.get_rect())).copy())
    return tuple(poses)


@lru_cache(maxsize=64)
def imagem_lume(pose, quadro, largura, altura, espelho=False):
    indice = PASSADAS[quadro] if pose in ("andar", "correr") else POSES[pose]
    imagem = _quadros()[indice]
    if pose == "queda":
        imagem = pygame.transform.rotate(imagem, -42)
    escala = min(largura / imagem.get_width(), altura / imagem.get_height())
    tamanho = round(imagem.get_width()*escala), round(imagem.get_height()*escala)
    imagem = pygame.transform.smoothscale(imagem, tamanho)
    return pygame.transform.flip(imagem, True, False) if espelho else imagem


def desenhar_lume(s, lume, x, pe, medida, tempo, fagulha=None):
    pose = lume.pose
    passos = movimento_arte.deslocamento(lume, lume.rect.centerx, tempo, lume.face)
    if fagulha and pose in {"parado", "andar", "correr", "pulo", "queda", "planar"}:
        fase = (tempo-fagulha.inicio)/.17
        if 0 <= fase < 1:
            recuo = sin(pi*fase**.65)*(1-fase)
            lado = 1 if fagulha.destino[0] >= fagulha.origem[0] else -1
            quadro = round(4+fase*18)
            return movimento_arte.desenhar(s, "lume-voo", quadro, x-lado*4*recuo,
                                          pe-medida[1]/2-2*recuo, medida, lume.face,
                                          centro=True, angulo=round(10*recuo*lado*lume.face))
    if pose in {"andar", "correr"}:
        quadro = movimento_arte.por_distancia(passos.distancia, 55.)
        return movimento_arte.desenhar(s,"lume-andar",quadro,x,pe,medida,lume.face)
    if pose in {"pulo", "queda", "planar"}:
        faixa = "lume-planar" if lume.planando else "lume-voo"
        ritmo = 2.8 if lume.planando else 8. if lume.batida_asa > 0 else 5.5 if lume.vy < 0 else 4.1
        quadro = movimento_arte.por_tempo(tempo, ritmo)
        angulo = -18 if pose == "queda" else 8 if lume.batida_asa > 0 else 0
        return movimento_arte.desenhar(s,faixa,quadro,x,pe-medida[1]/2,medida,lume.face,
                                        centro=True,angulo=angulo)
    quadro = imagem_lume(pose,0,*medida,lume.face < 0)
    caixa = quadro.get_rect(midbottom=(round(x),round(pe)))
    s.blit(quadro,caixa)
    return caixa
