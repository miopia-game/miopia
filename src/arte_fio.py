"""Berços, régua e reparos de Fio desenhados na própria figueira."""
import math

from . import pygame_hd as pygame

from . import fio_corte
from .ilustracao import AMBAR, OSSO, brilho, losango, sprite, texto


def objeto(s, o, j, cx, t):
    x, y = o.x-cx, o.y
    if o.tipo == "carretel_fio":
        semente = pygame.Rect(x-13, y-20, 26, 15)
        pygame.draw.rect(s, (86, 72, 51), semente, border_radius=5)
        for dx in (-11, 9):
            pygame.draw.ellipse(s, (145, 115, 73), (x+dx-3, y-24, 6, 21))
        for n in range(4):
            pygame.draw.aaline(s, (200, 190, 144), (x-8, y-9-n*3), (x+8, y-14-n*2))
        pygame.draw.lines(s, (137, 188, 163), False, [(x+8,y-16),(x+16,y-11),(x+20,y-14)], 2)
        return
    na_oficina = o.y == fio_corte.OFICINA[1]
    from .paisagem import rotina
    barra = x-40
    pygame.draw.lines(s, (94, 87, 58), False, [(barra-10,y),(barra-5,y-27),(barra+12,y-27),(barra+18,y)], 4)
    if na_oficina:
        for n in range(5):
            py = y-26+n*4
            pygame.draw.aaline(s, (145, 146, 105), (barra-4,py),(barra+6+n%2,py))
    else:
        f = math.sin(t*2.4)
        pygame.draw.lines(s, (183, 172, 123), False,
                          [(barra-5,y-23),(barra+7,y-27),(x-19,y-11+f)], 2)
    sprite(s, "npc_fio", x, y, 69, 43)
    rotina(s, "Fio", x, y, t)
    if abs(o.x-j.lume.rect.centerx) < 132:
        texto(s, "Fio", x, y-60, 14, OSSO, "forte", "centerx")


def berco(s, o, cx):
    x, y = o.x-cx, o.y
    perfil = [(x-66,y-124),(x-70,y-87),(x-60,y-52),(x-63,y-12)]
    pygame.draw.lines(s, (64, 63, 46), False, perfil, 9)
    pygame.draw.lines(s, (107, 101, 69), False, perfil, 2)
    # A chuva deixou uma linha acima do depósito seco da noite anterior.
    pygame.draw.lines(s, (140, 176, 146), False, [(x-72,y-93),(x-52,y-95),(x-42,y-92)], 3)
    pygame.draw.line(s, (170, 129, 84), (x-67,y-54), (x-44,y-54), 2)
    for dx, altura in ((-44, y-63), (-21, y-52)):
        centro = x+dx
        pygame.draw.line(s, (105, 107, 77), (centro-8, altura+13), (centro-14, y-91), 2)
        pygame.draw.line(s, (105, 107, 77), (centro+8, altura+13), (centro+10, y-91), 2)
        pygame.draw.arc(s, (177, 160, 111), (centro-13, altura, 26, 25), math.pi, math.tau, 3)
        pygame.draw.line(s, (97, 125, 104), (centro-11, altura+12), (centro+10, altura+12), 1)


def baixo(s, j, cx, cy, t):
    x, fundo, largura, _ = fio_corte.PASSARELA
    if cy+540 < fundo-42 or cx > 1920 or cx+960 < x-30:
        return
    if "viveiro_aberto" in j.cartografia:
        from .corte_vertical import abertura_comporta
        abertura = abertura_comporta(j)
        # A vazante chega às duas margens na proporção em que o vão abre.
        for inicio, fim, y in ((997,1393,fundo-9),(1440,1910,fundo-14)):
            alcance = round((fim-inicio)*abertura)
            if alcance < 18 or fim < cx or inicio > cx+960:
                continue
            margem = fim if fim < 1440 else inicio+alcance
            for n in range(16):
                px = margem-cx-(round(t*53)+n*31)%alcance
                py = y+round(4*math.sin(t*2+n*.67))
                pygame.draw.aaline(s, (76+n%3*12, 117+n%3*8, 105+n%3*7), (px-13, py+1), (px+3, py))
    if cx > x+largura+12 or cx+960 < x-12:
        return

    inicio, fim = x-cx, x+largura-cx
    for ponta in (inicio-2, fim+2):
        pygame.draw.line(s, (69, 69, 52), (ponta, fundo+4), (ponta, fundo-17), 6)
        pygame.draw.line(s, (155, 133, 86), (ponta+2, fundo-17), (ponta+2, fundo+1), 2)
    if fio_corte.REPARADA in j.cartografia:
        for y in (fundo+2, fundo+10):
            pygame.draw.line(s, (170, 150, 99), (inicio, y), (fim, y), 2)
        for px in range(inicio+6, fim, 9):
            pygame.draw.line(s, (99, 123, 84), (px, fundo+1), (px-3, fundo+11), 2)
        poste = inicio+largura//2
        pygame.draw.line(s, (134, 130, 82), (poste, fundo+2), (poste, fundo-31), 3)
        brilho(s, (poste, fundo-32), 20)
        losango(s, poste, fundo-32, 4, AMBAR)
    else:
        pygame.draw.lines(s, (124, 107, 72), False,
                          [(fim+2,fundo-6),(fim-10,fundo+12),(fim-3,fundo+26)], 2)
