"""Correntes e pingos desenhados no espaço da pintura, antes da névoa e do terreno."""

from math import cos, pi, sin

import pygame as sdl
from pygame import gfxdraw

# Pontos na composição 960 × 540. Cada canal liga o veio pintado à sua poça.
QUEDAS = (
    ((105, 171), (129, 188), (138, 225), (148, 239), (158, 270), (161, 301)),
    ((129, 324), (153, 334), (164, 365), (173, 377), (185, 411), (190, 446)),
)
CORRENTEZAS = (
    (542, 269, -16, 4, 7),
    (521, 282, -25, 5, 9),
    (509, 299, 27, 5, 10),
    (565, 314, 10, 5, 8),
    (458, 390, -36, 4, 12),
    (478, 407, -50, 4, 16),
    (323, 449, -48, 9, 24),
    (397, 431, -58, 4, 22),
    (355, 476, -65, 8, 24),
    (231, 466, -35, 2, 13),
    (314, 500, -29, 5, 18),
)
# x, ponta da raiz, nível da poça, duração do ciclo, defasagem, tamanho.
GOTEIRAS = (
    (418, 288, 484, 2.53, 0.25, 1.10),
    (488, 192, 431, 3.37, 1.65, 0.98),
    (653, 226, 376, 2.77, 0.91, 0.80),
    (638, 180, 351, 4.14, 2.86, 0.62),
    (744, 182, 414, 3.09, 2.02, 0.90),
)
# Pigmentos já na mesma luz fria aplicada ao panorama.
BRUMA = (104, 151, 129)
ESPUMA = (147, 183, 159)
FUNDO_QUEDA = (49, 103, 99)
CORRENTE = (69, 125, 123)
GOTA = (125, 150, 172)
AGUA_GRUTA = (89, 106, 141)


class Pincel:
    def __init__(self, superficie, origem):
        self.tela = superficie.pixels
        self.escala = superficie.escala * 4 / 3
        self.x, self.y = (round(v * superficie.escala) for v in origem)

    def ponto(self, x, y):
        return (self.x + round(self.escala * x), self.y + round(self.escala * y))

    def mancha(self, cor, pontos):
        vertices = [self.ponto(x, y) for x, y in pontos]
        sdl.draw.polygon(self.tela, cor, vertices)
        gfxdraw.aapolygon(self.tela, vertices, cor)

    def borda(self, cor, pontos):
        sdl.draw.aalines(self.tela, cor, False, [self.ponto(x, y) for x, y in pontos])


def anel(p, x, y, raio, altura, cor, abertura=0.0):
    # Duas pinceladas deixam as pontas se perderem na superfície.
    for inicio, fim in (
        (0.14 + abertura, 2.76 - abertura),
        (3.39 + abertura, 5.94 - abertura),
    ):
        p.borda(
            cor,
            [
                (
                    x + raio * cos(inicio + (fim - inicio) * i / 12),
                    y + altura * sin(inicio + (fim - inicio) * i / 12),
                )
                for i in range(13)
            ],
        )


def fio(canal, fracao):
    posicao = min(1.0, max(0.0, fracao)) * (len(canal) - 1)
    n = min(int(posicao), len(canal) - 2)
    a, b = canal[n : n + 2]
    u = posicao - n
    return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u


def corrego(s, origem, tempo):
    p = Pincel(s, origem)
    for i, canal in enumerate(QUEDAS):
        for k in range(7):
            u = (tempo * (0.75 + i * 0.14) + k / 7 + i * 0.31) % 1
            # O filete aparece no lábio da queda e se estica com a aceleração.
            a, b, c = (
                fio(canal, v)
                for v in (u**1.25, (u + 0.048) ** 1.25, (u + 0.126) ** 1.25)
            )
            lado = (-2.8, 1.3, 3.7)[k % 3]
            largura = (0.85 + u * 1.65) * min(1, u * 12, (1 - u) * 14)
            p.mancha(
                (FUNDO_QUEDA, ESPUMA, BRUMA)[k % 3],
                [
                    (a[0] + lado, a[1]),
                    (b[0] + lado + largura, b[1]),
                    (c[0] + lado, c[1]),
                    (b[0] + lado - largura * 0.45, b[1]),
                ],
            )
        x, y = canal[-1]
        # A espuma se abre lateralmente quando os filetes chegam à pedra.
        pulso = sin(tempo * 7.1 + i)
        p.mancha(
            BRUMA,
            [
                (x - 11, y + 1),
                (x - 6, y - 1),
                (x - 7 - pulso, y - 4 + pulso),
                (x - 2, y - 2),
                (x + 0.6, y - 5.5 - pulso),
                (x + 3, y - 2),
                (x + 8 - pulso, y - 4.3 - pulso),
                (x + 7, y - 0.5),
                (x + 14, y + 0.5),
                (x + 2, y + 2),
            ],
        )
        for k in range(2):
            u = (tempo * (1.05 + i * 0.11) + k * 0.5) % 1
            anel(
                p,
                x + u * 3,
                y + 1 + u * 1.4,
                2 + 20 * u,
                0.6 + 2.1 * u,
                BRUMA if u < 0.57 else CORRENTE,
                u * 0.62,
            )
        for k in range(4):
            u = (tempo * (1.56 + k * 0.08) + k * 0.28) % 1
            dx = (k - 1.5) * 4 * u
            px, py = x + dx, y - 1 - (3 + k % 2) * 4 * u * (1 - u)
            p.borda(BRUMA, [(px, py), (px + 0.45, py + 0.75)])
    for k, (x, y, dx, dy, tamanho) in enumerate(CORRENTEZAS):
        u = (tempo * (0.38 + k % 3 * 0.06) + k * 0.37) % 1
        px, py = x + u * dx, y + u * dy
        comprimento = tamanho * sin(pi * u)
        # Reflexos finos se alongam, acompanham a curva e se apagam.
        p.mancha(
            CORRENTE if k % 4 else BRUMA,
            [
                (px - comprimento, py + 0.7),
                (px, py - 0.35),
                (px + comprimento * 0.33, py - 0.45),
                (px + 2, py + 0.6),
            ],
        )


def gruta(s, origem, tempo):
    p = Pincel(s, origem)
    for x, teto, agua, periodo, atraso, tam in GOTEIRAS:
        fase = (tempo + atraso) % periodo
        formacao = 0.70
        queda = ((agua - teto) / 540) ** 0.5
        if fase < formacao:
            r = tam * (fase / formacao) ** 1.4
            if r < 0.18:
                continue
            p.mancha(
                GOTA,
                [
                    (x, teto - 1),
                    (x + 1.5 * r, teto + 2.7 * r),
                    (x, teto + 4 * r),
                    (x - 1.5 * r, teto + 2.7 * r),
                ],
            )
        elif fase < formacao + queda:
            u = (fase - formacao) / queda
            y = teto + 4 * tam + (agua - teto - 4 * tam) * u * u
            r = tam * (1.48 - 0.49 * u)
            cauda = tam * (3 + 8 * u)
            p.mancha(
                GOTA, [(x, y - cauda), (x + r, y - 0.7), (x, y + 1), (x - r, y - 0.7)]
            )
            p.borda(
                (155, 168, 184),
                [(x - 0.35 * r, y - 0.8), (x - 0.35 * r, y - 2.5 * tam)],
            )
        else:
            idade = fase - formacao - queda
            for atraso_anel in (0.0, 0.16):
                u = (idade - atraso_anel) / 0.89
                if 0 < u < 1:
                    anel(
                        p,
                        x,
                        agua,
                        (2 + 19 * u) * tam,
                        (0.6 + 2.5 * u) * tam,
                        GOTA if u < 0.32 and not atraso_anel else AGUA_GRUTA,
                        u * 0.92,
                    )
            if idade < 0.22:
                u = idade / 0.22
                for lado in (-1, 1):
                    px, py = x + lado * 5 * u * tam, agua - 3.2 * tam * 4 * u * (1 - u)
                    p.borda(GOTA, [(px, py), (px - lado * 0.6, py + 0.8)])
