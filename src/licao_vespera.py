"""A vigia aponta a marca. O jogador decide se ilumina e atravessa."""
from . import pygame_hd as pygame

from .arte_fagulha import desenhar_voo
from .ilustracao import AMBAR, brilho, claroes_suaves, dica_local
from .travessia_fagulha import CHEGADA, Fagulha, prever_marca

POSTO = (755, 248)
PRATICADO = "praticado_fagulha_vespera"


def perto(j):
    x,y = j.lume.rect.midbottom
    return (j.etapa == 0 and not j.em_vertical and "raiz" not in j.flags
            and not getattr(j,"campo_testes",False) and not hasattr(j,"sala_id")
            and POSTO[0]-55 <= x <= POSTO[0]+58 and abs(y-POSTO[1]) <= 9)


def atualizar(j):
    f = j.fagulha_ativa
    if f and f.destino == CHEGADA and f.progresso(j.tempo) >= 1:
        j.tutorial.add(PRATICADO)
    if perto(j) and j.vespera_sinal is None and PRATICADO not in j.tutorial:
        j.vespera_sinal = j.tempo


def desenhar(s,j,cx):
    if j.dialogo or not perto(j):
        return
    mx,my = round(CHEGADA[0]-cx),CHEGADA[1]
    px = round(POSTO[0]-cx)
    idade = j.tempo-j.vespera_sinal if j.vespera_sinal is not None else 99
    f = j.fagulha_ativa
    iluminou = f and f.destino == CHEGADA and f.progresso(j.tempo) >= 1

    # O lampejo da vigia indica a posição da marca. Só a luz de Lume ilumina o pouso.
    if PRATICADO not in j.tutorial and not f and .28 < idade < 1.2:
        sinal = Fagulha(.28, (POSTO[0]+17, POSTO[1]-50), CHEGADA)
        if idade < sinal.pouso_em:
            desenhar_voo(s, sinal, idade, cx, .68)
        else:
            raio = max(1, round(3*(1.2-idade)/(1.2-sinal.pouso_em)))
            pygame.draw.circle(s, AMBAR, (mx,my), raio)
    if iluminou:
        return
    if prever_marca(j) == CHEGADA:
        if not claroes_suaves():
            brilho(s,(mx,my+2),24)
        pygame.draw.ellipse(s,AMBAR,(mx-20,my+1,40,11),2)
        dica_local(s, "G", "Lançar fagulha", (mx, my))
    elif PRATICADO not in j.tutorial and 1.2 <= idade < 3.0:
        pygame.draw.ellipse(s,AMBAR,(mx-14,my+2,28,8),1)
        if not j.interacao and j.lume.face > 0:
            dica_local(s, "", "Chegue à ponta do galho", (px, POSTO[1] - 62))
