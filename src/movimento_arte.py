"""Folhas de animação com âncoras estáveis e cadência separada da física."""
from dataclasses import dataclass
from functools import lru_cache
from math import floor
import json
from weakref import WeakKeyDictionary

import pygame

from .ilustracao import ARTE, original

N_QUADROS = 24
COLUNAS = 4


@dataclass
class Passos:
    x: float
    tempo: float
    distancia: float = 0.
    velocidade: float = 0.
    tempo_passada: float | None = None
    amostra_distancia: float = 0.
    fase_passada: float = 0.

    def quadro_passada(self, comprimento):
        if self.tempo_passada is None:
            self.fase_passada = self.distancia/comprimento
        else:
            delta = self.distancia-self.amostra_distancia
            dt = self.tempo-self.tempo_passada
            if delta:
                self.fase_passada += delta/comprimento
            elif dt > 0:
                # Termina o apoio em até meia passada, conservando a fase
                # atingida como ponto de partida quando o animal volta a andar.
                contato = round(self.fase_passada*2)/2
                falta = contato-self.fase_passada
                self.fase_passada += max(-dt*1.65,min(dt*1.65,falta))
        self.tempo_passada = self.tempo
        self.amostra_distancia = self.distancia
        return round(self.fase_passada*N_QUADROS) % N_QUADROS


_passos = WeakKeyDictionary()


def deslocamento(ator, x, tempo, frente=1):
    """A câmera, a pausa e o número de desenhos no mesmo quadro não contam como passos."""
    passos = _passos.get(ator)
    if passos is None or tempo < passos.tempo:
        passos = _passos[ator] = Passos(x, tempo)
    dt = tempo - passos.tempo
    if dt > 0:
        dx = x - passos.x
        if dt > .24 or abs(dx) > 175:
            # Retornos ao marco e troca de área não fazem a pose avançar.
            passos.distancia = passos.velocidade = 0.
            passos.tempo_passada = None
        else:
            passos.distancia += dx * frente
            passos.velocidade = abs(dx) / dt
        passos.x, passos.tempo = x, tempo
    return passos


def por_distancia(distancia, comprimento):
    return floor(distancia * N_QUADROS / comprimento) % N_QUADROS


def por_tempo(tempo, ciclos):
    return int(tempo * ciclos * N_QUADROS) % N_QUADROS


@lru_cache(maxsize=1)
def _medidas():
    return json.loads((ARTE / "movimento-v2" / "folhas.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=32)
def _folha(nome):
    return original(f"movimento-v2/{nome}.png")


@lru_cache(maxsize=512)
def _quadro(nome, indice, medida, lado, angulo):
    fonte = _folha(nome)
    w, h, margem = _medidas()[nome]
    linha, coluna = divmod(indice, COLUNAS)
    largura, altura = w+2*margem, h+2*margem
    celula = fonte.subsurface((coluna*largura, linha*altura, largura, altura))
    escala = min(medida[0]/w, medida[1]/h)
    quadro = pygame.transform.smoothscale(celula, (round(largura*escala), round(altura*escala)))
    if lado < 0:
        quadro = pygame.transform.flip(quadro, True, False)
    if angulo:
        quadro = pygame.transform.rotate(quadro, angulo*lado)
    return quadro, quadro.get_bounding_rect(min_alpha=70), round(margem*escala)


def desenhar(s, nome, indice, x, y, medida, lado, *, centro=False, angulo=0):
    quadro, pigmento, margem = _quadro(nome, indice % N_QUADROS, medida, lado, angulo)
    ponto = round(x), round(y)
    if centro:
        caixa = quadro.get_rect(center=ponto)
    else:
        caixa = quadro.get_rect(midbottom=(ponto[0], ponto[1]+margem))
    s.blit(quadro, caixa)
    return pigmento.move(caixa.topleft)
