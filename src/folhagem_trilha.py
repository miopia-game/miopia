"""Vegetação enraizada no chão e nos galhos, ao alcance do corpo de Lume."""

from functools import lru_cache
from math import sin

from . import pygame_hd as pg
from .ilustracao import imagem

# Pé de cada touceira (mundo) e altura. A planta de x=810 já compõe a abertura.
TOUCEIRAS = {
    0: (
        (174, 442, 49),
        (396, 376, 42),
        (810, 442, 67),
        (1302, 372, 48),
        (1852, 442, 55),
        (2478, 291, 43),
        (3014, 442, 62),
        (3092, 369, 43),
        (3290, 442, 50),
        (3660, 442, 57),
    ),
    2: (
        (176, 442, 82),
        (375, 377, 67),
        (592, 310, 74),
        (845, 442, 87),
        (1368, 375, 71),
        (1864, 442, 79),
        (2128, 371, 68),
        (2920, 374, 74),
        (3278, 442, 85),
        (3610, 442, 77),
    ),
}


@lru_cache(maxsize=16)
def _bambus(altura, espelho):
    largura = round(altura * 1.13)
    s = pg.Surface((largura, altura), pg.SRCALPHA)

    def ponto(x, y):
        return ((1 - x if espelho else x) * largura, y * altura)

    def tinta(cor, *coords):
        vertices = [ponto(x, y) for x, y in coords]
        pg.draw.polygon(s, cor, vertices)
        pg.draw.aalines(s, cor, True, vertices)

    # Três colmos em profundidades distintas. O entrenó recebe sombra e borda de palha.
    for base, inclinacao, topo, cor, luz in (
        (0.48, -0.26, 0.16, (76, 70, 51), (127, 113, 69)),
        (0.55, 0.27, 0.23, (85, 77, 49), (155, 134, 77)),
        (0.48, 0.03, 0.045, (111, 92, 54), (184, 151, 82)),
    ):

        def eixo(y):
            return base + inclinacao * ((1 - y) / (1 - topo)) ** 1.32

        pontos = [(eixo(y), y) for y in (1, 0.77, 0.55, 0.34, topo)]
        tinta(
            (39, 34, 36),
            *((x - 0.022, y) for x, y in pontos),
            *((x + 0.022, y) for x, y in reversed(pontos)),
        )
        for (x, y), (xx, yy) in zip(pontos, pontos[1:]):
            tinta(
                cor, (x - 0.012, y), (x + 0.014, y), (xx + 0.01, yy), (xx - 0.015, yy)
            )
            tinta(
                luz, (xx - 0.015, yy), (xx - 0.006, yy + 0.005), (x - 0.007, y - 0.015)
            )
            tinta(
                (53, 49, 40),
                (xx - 0.025, yy + 0.015),
                (xx + 0.024, yy + 0.006),
                (xx + 0.024, yy - 0.009),
                (xx - 0.024, yy),
            )
            tinta(
                luz,
                (xx - 0.024, yy),
                (xx + 0.024, yy - 0.009),
                (xx + 0.018, yy - 0.016),
                (xx - 0.019, yy - 0.011),
            )
        for k, (y, lado) in enumerate(((0.60, -1), (0.41, 1), (0.29, -1))):
            x = eixo(y)
            alcance = (0.18 + 0.026 * (k % 2)) * lado
            for v in range(3):
                u = (v + 1) / 3
                px = x + alcance * u
                py = y - 0.082 * u
                pg.draw.aaline(s, luz, ponto(x, y), ponto(px, py))
                sinal = 1 if v % 2 else -1
                ponta = (
                    px + lado * (0.09 + 0.022 * v),
                    py + sinal * (0.08 + 0.018 * v),
                )
                tinta(
                    (79, 84, 53) if v % 2 else (104, 108, 63),
                    (px, py),
                    (px + lado * 0.074, py + sinal * 0.018 - 0.018),
                    ponta,
                    (px + lado * 0.061, py + sinal * 0.033 + 0.014),
                )
                pg.draw.aaline(
                    s,
                    (145, 137, 77),
                    ponto(px, py),
                    ponto((px + ponta[0]) / 2, (py + ponta[1]) / 2),
                )
    return s


def curvar(s, planta, x, pe, amplitude):
    """Translada fileiras de pixels nativos. O deslocamento zera na raiz."""
    pixels = planta.pixels
    largura, altura = pixels.get_size()
    escala = s.escala
    esquerda = round(x * escala) - largura // 2
    topo = round(pe * escala) - altura
    if abs(amplitude) * escala < 0.5:
        s.pixels.blit(pixels, (esquerda, topo))
        return
    # Agrupa as fileiras que teriam o mesmo deslocamento físico.
    inicio = 0
    anterior = round(amplitude * escala)
    retalhos = []
    for y in range(1, altura + 1):
        desloc = round(amplitude * escala * (1 - y / altura) ** 1.65)
        if desloc != anterior or y == altura:
            retalhos.append(
                (
                    pixels,
                    (esquerda + anterior, topo + inicio),
                    (0, inicio, largura, y - inicio),
                )
            )
            inicio, anterior = y, desloc
    s.pixels.blits(retalhos, doreturn=False)


def desenhar(s, j, cx):
    if hasattr(j, "sala_id") or getattr(j, "campo_testes", False):
        return
    bambu = j.etapa == 2
    for i, (x, pe, h) in enumerate(TOUCEIRAS.get(j.etapa, ())):
        if not -120 < x - cx < 1080:
            continue
        planta = (
            _bambus(h, i % 2 == 1)
            if bambu
            else imagem("bosque_samambaias.png", round(h * 1.51), h, i % 2 == 1)
        )
        flexao = j.passagem.flexao(
            x, pe - h * 0.47, j.tempo, bambu=bambu, alcance=h * 0.65 + 15
        )
        brisa = sin(j.tempo * (1.35 if bambu else 1.68) + x * 0.013) * h * 0.033
        curvar(
            s, planta, x - cx, pe + 2, brisa + flexao * h * (0.46 if bambu else 0.62)
        )
