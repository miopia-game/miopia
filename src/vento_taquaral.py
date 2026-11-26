"""Correntes locais do beiral, com sementes que acompanham a direção do ar."""
from dataclasses import dataclass
import math

from . import pygame_hd as pygame


@dataclass(frozen=True)
class Corrente:
    esquerda: int
    direita: int
    topo: int
    base: int
    deslocamento: int
    subida: int

    def contem(self, x, pe):
        return self.esquerda <= x < self.direita and self.topo <= pe < self.base


ABRIGO = Corrente(224, 320, 108, 396, 0, -158)
EXPOSTA = Corrente(320, 512, 245, 396, 138, 0)
BEIRAL = (108, 213, 105)
ABA = (382, 226, 108, 22)
POUSO = (392, 350, 120, 18)
ALTURA_ENTRADA = ABA[1] + ABA[3] + 33
PAVIO = "pavio_beiral"


def permite_retomar(corrente, pe, velocidade):
    # Na descida do beiral, abrir as asas mantém a trajetória sob a aba.
    return corrente is EXPOSTA and ALTURA_ENTRADA <= pe < POUSO[1] and velocidade > 115


def sobre(x, pe):
    if ABRIGO.contem(x, pe):
        return ABRIGO
    if EXPOSTA.contem(x, pe):
        return EXPOSTA
    return None


def desenhar(s, camera, tempo):
    for corrente in (ABRIGO, EXPOSTA):
        desenhar_corrente(s, camera, tempo, corrente)


def desenhar_corrente(s, camera, tempo, corrente):
    janela = s.get_clip()
    if (camera > corrente.direita or camera + janela.w < corrente.esquerda
            or janela.bottom < corrente.topo-12 or janela.top > corrente.base):
        return
    largura = corrente.direita - corrente.esquerda - 12
    altura = corrente.base - corrente.topo - 14
    for n in range(22):
        oscilacao = math.sin(n * 2.3 + tempo * 3) * 3
        if corrente.subida:
            x = 6 + (n * 31) % largura + oscilacao
            y = (n * 73 - tempo * 86) % altura
            dx, dy = round(oscilacao), 7
        else:
            x = (n * 79 + tempo * 112) % largura
            y = 7 + (n * 19) % altura + oscilacao
            dx, dy = -9, round(oscilacao)
        x = round(corrente.esquerda + x - camera)
        y = round(corrente.topo + y - 12)
        pygame.draw.line(s, (127, 148, 118), (x, y), (x + dx, y + dy))
        pygame.draw.ellipse(s, (203, 202, 146), (x - 2, y - 1, 4, 3))
