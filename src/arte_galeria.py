"""Tabuletas, berços e mecanismos da Galeria das Sementes."""
import math
from . import pygame_hd as pygame

from . import galeria_taquaral as galeria
from . import nicho_taquaral as nicho
from .fases import CHAO
from .ilustracao import AMBAR, OSSO, PALIDO, brilho
from .vento_taquaral import desenhar_corrente


def colmos(s, r):
    pygame.draw.rect(s, (44, 50, 35), r, border_radius=8)
    for n, x in enumerate(range(r.left+7, r.right-2, 8)):
        caminho = [(x + math.sin(n+y*.035)*2, y) for y in range(r.top+4, r.bottom-1, 8)]
        pygame.draw.lines(s, (71+n%2*17, 80+n%2*12, 49), False, caminho, 7)
        pygame.draw.lines(s, (121, 121, 70), False, caminho, 1)
        for y in range(r.top+16+n*9, r.bottom-1, 34):
            pygame.draw.line(s, (134, 124, 77), (x-4,y+1), (x+4,y-1), 2)
    for x in range(r.left+5, r.right-3, 11):
        pygame.draw.line(s, (112, 116, 65), (x,r.bottom-3), (x+4,r.bottom-6), 2)


def veneziana(s, r):
    pygame.draw.rect(s, (71, 63, 42), r, border_radius=3)
    pygame.draw.rect(s, (154, 139, 90), r, 2, border_radius=3)
    for x in range(r.left+5, r.right-8, 11):
        pygame.draw.line(s, (173, 147, 91), (x,r.bottom-4), (x+6,r.y+3), 2)


def detalhes(s, j, cx):
    view = s.get_clip()
    if cx > galeria.DIREITA or cx+s.get_width() < galeria.ESQUERDA or view.bottom < CHAO:
        return
    x = round(galeria.CIPO.x-cx)
    pts = [(x + (y//15 % 3 - 1)*2, y) for y in range(CHAO+10, galeria.FUNDO, 7)]
    pygame.draw.lines(s, (74, 92, 59), False, pts, 6)
    pygame.draw.lines(s, (150, 136, 86), False, pts, 2)
    pygame.draw.circle(s, (170, 152, 89), (x, galeria.FUNDO-36), 5, 2)
    # Linhas de cheia e cestaria repetem as alturas dos berços.
    for base in (1745, 1798, 1861, 1932):
        x = round(base-cx)
        y = galeria.FUNDO
        pygame.draw.arc(s, (151, 135, 80), (x-20,y-42,40,43), 3.2, 6.2, 3)
        pygame.draw.line(s, (121, 109, 65), (x-20,y-18), (x+20,y-18), 4)
        for dx in (-12, 0, 12):
            pygame.draw.line(s, (98, 102, 58), (x+dx,y-16), (x+dx//2,y-2))
    x = round(galeria.VENEZIANA.x-cx)
    topo = galeria.BOCA_VENEZIANA.centery
    pygame.draw.line(s, (94, 112, 70), (x, topo), (x, galeria.FUNDO-46), 3)
    for y in range(topo+24, galeria.FUNDO-40, 34):
        pygame.draw.line(s, (140, 136, 82), (x-2,y), (x+3,y-4))
    if galeria.abertura(j) == 1.:
        eixo = galeria.CHAMINE
        for deslocamento in (12, 26, 48):
            px = round(eixo.esquerda-cx+deslocamento)
            pygame.draw.line(s, (55, 77, 58), (px+20,CHAO+9), (px,galeria.FUNDO-4))
        desenhar_corrente(s, cx, j.tempo, eixo)
    if nicho.ABERTO in j.flags and view.bottom > 810:
        for base in range(1240, 1635, 49):
            px = round(base-cx)
            y = nicho.FUNDO
            pygame.draw.lines(s, (63, 78, 57), False, [(px-8,y),(px+3,y-102),(px+13,y-148)], 8)
            pygame.draw.lines(s, (119, 125, 78), False, [(px-5,y),(px+6,y-103),(px+16,y-147)], 2)
            for descer in (27, 73, 119):
                x = px+descer//8-8
                pygame.draw.line(s, (127,128,83), (x-5,y-descer), (x+6,y-descer-2), 2)
        x = round(nicho.LESTE-cx)
        veneziana(s, pygame.Rect(x, nicho.SOLEIRA-12, 30, 12))


def objeto(s, o, j, cx):
    x, y = round(o.x-cx), o.y
    if o.id == nicho.TRANCA.id:
        pygame.draw.lines(s, (117, 116, 69), False, [(x-52,y-109),(x-5,y-39),(x,y-21)], 3)
        pygame.draw.circle(s, PALIDO, (x,y-22), 10, 2)
        if nicho.ABERTO not in j.flags:
            pygame.draw.lines(s, AMBAR, False, [(x-15,y-54),(x,y-65),(x+15,y-54)], 2)
    elif o.id == nicho.LAMPADA.id:
        acesa = nicho.ACESO in j.flags
        if acesa:
            brilho(s, (x,y-53), 38)
        pygame.draw.line(s, (114, 93, 61), (x,y), (x,y-62), 4)
        pygame.draw.ellipse(s, AMBAR if acesa else (101, 112, 78), (x-12,y-65,24,17), 2)
        pygame.draw.circle(s, AMBAR if acesa else (84, 92, 69), (x,y-57), 5)
        pygame.draw.rect(s, (115, 88, 55), (x-23,y-19,46,19), border_radius=4)
        for dx in (-15,-5,5,15):
            pygame.draw.line(s, (159, 142, 92), (x+dx,y-16), (x+dx+4,y-3), 2)
    elif o.id == galeria.PLACA.id:
        pygame.draw.line(s, (104, 84, 54), (x,y), (x,y-47), 5)
        pygame.draw.polygon(s, (87, 74, 50), [(x-20,y-50),(x+25,y-47),(x+18,y-25),(x-23,y-29)])
        for n in range(2):
            px = x+n*14-7
            pygame.draw.lines(s, OSSO, False, [(px-4,y-40),(px,y-44),(px+4,y-40)], 2)
        pygame.draw.line(s, (164, 150, 103), (x-12,y-33), (x+16,y-31))
    elif o.id == galeria.CAVILHA.id:
        brilho(s, (x,y-13), 16)
        pygame.draw.polygon(s, (160, 124, 68), [(x-14,y-13),(x+10,y-18),(x+16,y-11),(x-8,y-7)])
        pygame.draw.line(s, AMBAR, (x-10,y-15), (x+10,y-18), 2)
        pygame.draw.circle(s, OSSO, (x+5,y-14), 2, 1)
    elif o.id == galeria.VENEZIANA.id:
        centro = (x,y-36)
        pygame.draw.line(s, (113, 97, 61), (x-15,y), centro, 5)
        pygame.draw.line(s, (113, 97, 61), (x+15,y), centro, 5)
        pygame.draw.circle(s, (171, 151, 97), centro, 19, 3)
        for dx, dy in ((-13,0),(0,-13),(13,0),(0,13)):
            pygame.draw.line(s, PALIDO, centro, (x+dx,y-36+dy), 2)
        if galeria.ABERTA in j.flags:
            pygame.draw.circle(s, AMBAR, centro, 5)
        else:
            pygame.draw.rect(s, (38, 44, 33), (x-5,y-40,10,7))
