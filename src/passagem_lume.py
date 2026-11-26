"""Ar deslocado pelo corpo de Lume, guardado brevemente em coordenadas do mundo."""

from collections import deque
from math import cos, exp


class Passagem:
    def __init__(self):
        self.amostras = deque()

    def mover(self, tempo, antes, depois):
        while self.amostras and tempo - self.amostras[0][0] >= 1.15:
            self.amostras.popleft()
        dx, dy = depois[0] - antes[0], depois[1] - antes[1]
        if abs(dx) + abs(dy) < 0.001:
            return
        # Soma o caminho percorrido a cada 1/30 s mesmo com subpassos menores.
        if self.amostras and int(tempo * 30) == int(self.amostras[-1][0] * 30):
            _, _, _, anterior_x, anterior_y = self.amostras.pop()
            dx, dy = dx + anterior_x, dy + anterior_y
        self.amostras.append((tempo, *depois, dx, dy))

    def flexao(self, x, y, tempo, *, bambu=False, alcance=48):
        total = 0.0
        for instante, px, py, dx, dy in self.amostras:
            idade = tempo - instante
            distancia = ((x - px) / alcance) ** 2 + ((y - py) / (alcance * 0.92)) ** 2
            if distancia >= 1 or not 0 <= idade < 1.15:
                continue
            # Uma passagem vertical afasta o ramo para o lado de fora do corpo.
            sopro = dx + abs(dy) * (0.52 if x >= px else -0.52)
            amortecimento, frequencia = (3.5, 6.6) if bambu else (5.4, 8.8)
            total += (
                sopro
                * (1 - distancia) ** 1.4
                * exp(-amortecimento * idade)
                * cos(frequencia * idade)
            )
        return max(-1.0, min(1.0, total / 32))
