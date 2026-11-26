"""Poses de vento das folhas, em coordenadas da composição de 960 × 540."""

from functools import lru_cache
from math import sin
from pathlib import Path
from struct import unpack_from
from zipfile import ZipFile

import pygame as sdl

PASTA = Path(__file__).resolve().parents[1] / "assets" / "arte" / "panoramas"
ESCALA = 8 / 3  # A pintura física mede 2560 × 1440.
PASSOS = 16
# Nome, retângulo, velocidade angular e atraso. Cada recorte volta à pose de repouso
# nas bordas; as coordenadas são múltiplos de 3 para alinhar os pixels da pintura.
PLANTAS = {
    "bosque": (
        ("fronde_central", (300, 267, 558, 507), 1.62, 0.8),
        ("fronde_alta", (594, 9, 948, 246), 1.39, 1.2),
        ("fronde_baixa", (558, 249, 861, 477), 1.52, 1.6),
    ),
    "taquaral": (
        ("colmos", (0, 0, 306, 438), 1.16, 0.3),
        ("ramagem", (306, 0, 747, 300), 1.32, 0.7),
        ("touceira", (747, 24, 960, 345), 1.24, 1.3),
    ),
}


@lru_cache(maxsize=2)
def _arquivo(bioma):
    # O índice do pacote cabe em memória. As poses são lidas sob demanda.
    return ZipFile(PASTA / f"vento_{bioma}.atlas")


@lru_cache(maxsize=6)
def _cores(bioma, nome):
    cores = _arquivo(bioma).read(f"{nome}/cores")
    return tuple(zip(cores[::3], cores[1::3], cores[2::3]))


@lru_cache(maxsize=36)
def _pose(bioma, nome, passo):
    dados = _arquivo(bioma).read(f"{nome}/{passo:+d}")
    x, y, w, h = unpack_from("<4H", dados)
    im = sdl.image.frombuffer(memoryview(dados)[8:], (w, h), "P")
    im.set_palette(_cores(bioma, nome))
    im.set_colorkey(0, sdl.RLEACCEL)
    return im, x, y


def folhagem(s, bioma, origem, tempo):
    ox, oy = (round(v * s.escala) for v in origem)
    for nome, (x, y, direita, baixo), velocidade, atraso in PLANTAS[bioma]:
        # A rajada passa de uma planta à seguinte; a folha continua oscilando entre rajadas.
        vento = (
            0.62 * sin(tempo * velocidade - atraso)
            + 0.27 * sin(tempo * 2.13 - atraso * 1.7)
            + 0.11 * sin(tempo * 3.07 + atraso)
        )
        passo = round(PASSOS * vento)
        if passo == 0:
            continue  # O panorama já contém exatamente a pose central.
        pos = (ox + round(x * ESCALA), oy + round(y * ESCALA))
        area = sdl.Rect(
            pos, (round((direita - x) * ESCALA), round((baixo - y) * ESCALA))
        )
        if s.pixels.get_clip().colliderect(area):
            imagem, x_local, y_local = _pose(bioma, nome, passo)
            s.pixels.blit(imagem, (pos[0] + x_local, pos[1] + y_local))
