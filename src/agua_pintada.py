"""Correntes e pingos desenhados no espaço da pintura, antes da névoa e do terreno."""

from dataclasses import dataclass
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


@dataclass(frozen=True)
class LuzNaAgua:
    x: float
    y: float
    raio: float
    intensidade: float

    def na_pintura(self, origem):
        return LuzNaAgua(
            (self.x - origem[0]) * 0.75,
            (self.y - origem[1]) * 0.75,
            self.raio * 0.75,
            self.intensidade,
        )

    def incide(self, x, y):
        distancia = ((x - self.x) / self.raio) ** 2 + ((y - self.y) / self.raio) ** 2
        return self.intensidade * max(0.0, 1 - distancia) ** 1.5


def luz_da_fagulha(j, camera):
    from .ilustracao import claroes_suaves

    f = j.fagulha_ativa
    if f is None:
        return None
    x, y = f.posicao(j.tempo)
    raio = f.raio(j.tempo)
    if raio <= 0:
        return None
    forca = min(1.0, f.restante(j.tempo) * 5) * (0.62 if claroes_suaves() else 1.0)
    return LuzNaAgua(x - camera, y, raio, forca)


def aquecer(cor, forca, tom=(255, 196, 101)):
    return tuple(round(a + (b - a) * forca) for a, b in zip(cor, tom))


# Margens do remanso na pintura. A coluna de luz se parte nas ondulações
# e termina quando encontra pedra ou raiz.
MARGENS = (
    (376, 430, 563),
    (383, 423, 556),
    (396, 405, 545),
    (407, 364, 523),
    (416, 325, 505),
    (430, 287, 474),
    (440, 229, 451),
    (451, 154, 407),
    (463, 159, 400),
    (476, 208, 350),
    (490, 235, 325),
    (499, 271, 312),
)


def _lamina(p, luz, y, esquerda, direita, tempo, indice, largura):
    tremor = sin(tempo * 3.4 + indice * 1.9)
    x = luz.x + tremor * (2.2 + indice % 3)
    perto = max(esquerda, min(direita, x))
    forca = luz.incide(perto, y)
    if forca < 0.035:
        return
    w = largura * forca * (0.77 + 0.23 * cos(indice * 2.76 + tempo * 2.2))
    a, b = max(esquerda, x - w), min(direita, x + w)
    if b - a < 1.2:
        return
    centro = (a + b) * 0.5
    h = (0.38 + forca * 1.2) * min(1.0, (b - a) / 5.0)
    # Lê o pigmento molhado situado debaixo da pincelada.
    pos = p.ponto(centro, y)
    if not p.tela.get_clip().collidepoint(pos):
        return
    tinta = p.tela.get_at(pos)[:3]
    p.mancha(
        aquecer(tinta, forca * 0.81, (234, 151, 66)),
        [(a, y), (centro, y - h), (b, y - 0.18), (centro + (b - a) * 0.065, y + h)],
    )
    if forca > 0.30 and b - a > 5:
        p.borda(
            aquecer(tinta, forca, (255, 220, 149)),
            [(centro - (b - a) * 0.21, y), (centro + (b - a) * 0.14, y - 0.25)],
        )


def reflexo_remanso(p, luz, tempo):
    for i, (inicio, fim) in enumerate(zip(MARGENS, MARGENS[1:])):
        y, a, b = inicio
        _lamina(p, luz, y, a, b, tempo, 2 * i, 25 + i * 0.85)
        _lamina(
            p,
            luz,
            (y + fim[0]) * 0.5,
            (a + fim[1]) * 0.5,
            (b + fim[2]) * 0.5,
            tempo,
            2 * i + 1,
            14 + i * 0.63,
        )


def reflexo_canal(s, luz, camera, nivel, tempo):
    if luz is None:
        return
    # O canal jogável está no plano de Lume. A mesma função respeita o desnível
    # depois de drenar e a borda de cada margem.
    p = Pincel(s, (0, 0), escala=1.0)
    for i in range(10):
        y = nivel + 2.5 + i * 3.1
        if y + 2 >= 442:
            break
        _lamina(p, luz, y, 804 - camera, 1347 - camera, tempo, i, 32 + i * 0.9)


class Pincel:
    def __init__(self, superficie, origem, escala=4 / 3):
        self.tela = superficie.pixels
        self.escala = superficie.escala * escala
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


def corrego(s, origem, tempo, luz=None):
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
            cor = (FUNDO_QUEDA, ESPUMA, BRUMA)[k % 3]
            if luz:
                cor = aquecer(cor, luz.incide(b[0] + lado, b[1]) * 0.90)
            p.mancha(
                cor,
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

    if luz:
        reflexo_remanso(p, luz, tempo)


def _brilho_gota(p, luz, x, y, r):
    forca = luz.incide(x, y) if luz else 0.0
    if forca <= 0.05:
        return
    # A face voltada para a fagulha fica âmbar; a borda oposta guarda o azul da gruta.
    lado = 1 if luz.x >= x else -1
    h = r * (1.7 + forca)
    w = r * (1.2 + 0.65 * forca)

    def face(dx, dy):
        return x + lado * w * dx, y + h * dy

    p.mancha(
        aquecer(GOTA, forca * 0.78, (243, 181, 95)),
        [
            face(0, -1.3),
            face(0.70, -0.57),
            face(1, -0.09),
            face(0.87, 0.42),
            face(0.38, 0.73),
            face(-0.36, 0.76),
            face(-0.86, 0.46),
            face(-1, 0.01),
            face(-0.69, -0.63),
        ],
    )
    p.borda(
        aquecer(GOTA, forca, (255, 240, 190)),
        [face(0.41, -0.74), face(0.78, -0.34), face(0.81, 0.01)],
    )
    p.borda(
        aquecer(GOTA, forca * 0.43, (154, 174, 192)),
        [face(-0.79, 0.26), face(-0.41, 0.60), face(0, 0.68)],
    )


def gruta(s, origem, tempo, luz=None):
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
                aquecer(GOTA, luz.incide(x, teto)) if luz else GOTA,
                [
                    (x, teto - 1),
                    (x + 1.5 * r, teto + 2.7 * r),
                    (x, teto + 4 * r),
                    (x - 1.5 * r, teto + 2.7 * r),
                ],
            )
            _brilho_gota(p, luz, x, teto + 2.8 * r, r)
        elif fase < formacao + queda:
            u = (fase - formacao) / queda
            y = teto + 4 * tam + (agua - teto - 4 * tam) * u * u
            r = tam * (1.48 - 0.49 * u)
            cauda = tam * (3 + 8 * u)
            p.mancha(
                aquecer(GOTA, luz.incide(x, y) * 0.68) if luz else GOTA,
                [(x, y - cauda), (x + r, y - 0.7), (x, y + 1), (x - r, y - 0.7)],
            )
            p.borda(
                aquecer((155, 168, 184), luz.incide(x, y), (255, 228, 166))
                if luz
                else (155, 168, 184),
                [(x - 0.35 * r, y - 0.8), (x - 0.35 * r, y - 2.5 * tam)],
            )
            _brilho_gota(p, luz, x, y - r, r)
        else:
            idade = fase - formacao - queda
            for atraso_anel in (0.0, 0.16):
                u = (idade - atraso_anel) / 0.89
                if 0 < u < 1:
                    cor = GOTA if u < 0.32 and not atraso_anel else AGUA_GRUTA
                    if luz:
                        cor = aquecer(cor, luz.incide(x, agua) * (1 - u * 0.56))
                    anel(
                        p,
                        x,
                        agua,
                        (2 + 19 * u) * tam,
                        (0.6 + 2.5 * u) * tam,
                        cor,
                        u * 0.92,
                    )
                    if luz:
                        forca = luz.incide(x, agua) * (1 - u)
                        if forca > 0.13:
                            lado = 1 if luz.x >= x else -1
                            raio = (2 + 19 * u) * tam
                            cx = x + lado * raio * 0.50
                            py = agua + (0.6 + 2.5 * u) * tam * 0.85
                            meio = raio * 0.37
                            p.mancha(
                                aquecer(cor, forca, (255, 217, 142)),
                                [
                                    (cx - meio, py),
                                    (cx, py - forca * 0.52),
                                    (cx + meio, py - 0.42),
                                    (cx, py + forca * 0.83),
                                ],
                            )
            if idade < 0.22:
                u = idade / 0.22
                for lado in (-1, 1):
                    px, py = x + lado * 5 * u * tam, agua - 3.2 * tam * 4 * u * (1 - u)
                    p.borda(GOTA, [(px, py), (px - lado * 0.6, py + 0.8)])
