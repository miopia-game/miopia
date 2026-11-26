"""Calhas, berços e polias originais, desenhados nas coordenadas do Jardim."""
import math
from . import pygame_hd as pygame
from .ilustracao import AMBAR,OSSO,brilho
from .fauna_jardim import FLOR, PLACA


def objeto(s,o,j,cx):
    x,y=o.x-cx,o.y
    i=o.id;c=j.cartografia
    if i.startswith('jardim_cipo_'):
        pygame.draw.line(s,(95,118,64),(x,774),(x,y-4),5)
        for h in range(790,y,29):pygame.draw.line(s,(178,163,102),(x-5,h),(x+5,h+3),2)
        pygame.draw.ellipse(s,AMBAR,(x-11,y-20,22,11),2)
    elif i.startswith('jardim_gota_') or i=='jardim_orvalho':
        pygame.draw.polygon(s,(149,186,177),[(x,y-30),(x-9,y-9),(x,y-3),(x+9,y-9)])
        pygame.draw.line(s,OSSO,(x-3,y-17),(x-4,y-10),2)
        brilho(s,(x,y-13),17)
    elif i=='jardim_brotos':
        pygame.draw.ellipse(s,(96,128,68),(x-20,y-31,40,25))
        for d in (-9,0,9):pygame.draw.line(s,(191,181,117),(x+d,y-6),(x+d+3,y-24),2)
        if 'vigia_4350' not in c:pygame.draw.line(s,(145,128,90),(4350-cx,y-8),(x,y-12),2)
    elif i=='jardim_lente':
        pygame.draw.circle(s,(146,184,164),(round(x),y-14),12,2)
        pygame.draw.line(s,OSSO,(x-5,y-21),(x+4,y-25),2)
        brilho(s,(x,y-14),16)
    elif i=='jardim_memoria':
        pygame.draw.polygon(s,(139,152,100),[(x-16,y-25),(x+19,y-22),(x+13,y-3),(x-17,y-7)])
        for n in range(3):pygame.draw.line(s,(70,94,62),(x-9,y-20+n*5),(x+8,y-17+n*5),1)
    elif i == PLACA:
        pygame.draw.line(s,(104,92,64),(x,y),(x-3,y-38),4)
        pygame.draw.polygon(s,(83,71,53),[(x-20,y-39),(x+15,y-41),(x+20,y-22),(x-16,y-21)])
        pygame.draw.line(s,AMBAR,(x-10,y-34),(x-3,y-28),2)
        pygame.draw.lines(s,OSSO,False,[(x-7,y-26),(x,y-30),(x+8,y-25),(x+13,y-29)],1)
    elif i=='jardim_entrada':
        pygame.draw.line(s,(105,123,79),(x,y),(x,y-58),4)
        for n in range(3):
            pygame.draw.circle(s,AMBAR if n<len(j.sobreviventes) else (81,95,67),(round(x-13+n*13),y-49),5,2)
    elif i=='jardim_polia':
        pygame.draw.lines(s,(121,104,67),False,[(x-12,y-46),(x-10,y-6),(x+14,y-6),(x+18,y-46)],3)
        if 'jardim_comporta' in c:pygame.draw.rect(s,(109,162,164),(x-7,y-30,18,21))
        pygame.draw.lines(s,(160,141,91),False,[(x+4,y-47),(x+4,y-132),(3968-cx,y-132),(3968-cx,y-18)],2)
        pygame.draw.circle(s,AMBAR,(round(x+4),y-132),8,2)
    elif i=='jardim_calha':
        pygame.draw.line(s,(104,130,104),(x-28,y-12),(x+30,y-12),8)
        pygame.draw.circle(s,(161,150,100),(round(x),y-24),11,2)
        pygame.draw.line(s,AMBAR,(x-7,y-24),(x+7,y-24),2)
    elif i=='jardim_plantar':
        pygame.draw.ellipse(s,(78,92,51),(x-31,y-10,62,10))
        altura=49 if 'jardim_plantado' in c else 16
        pygame.draw.line(s,(119,155,79),(x,y-6),(x+3,y-altura),4)
        for lado in (-1,1):
            pygame.draw.ellipse(s,(132,162,87),(x+lado*4-12,y-altura+7,24,9),2)
        if 'jardim_plantado' in c:brilho(s,(x,y-altura),30)
    else:
        pygame.draw.line(s,(105,128,73),(x,y),(x,y-47),4)
        pygame.draw.circle(s,AMBAR,(round(x),y-48),8,2)


def detalhes(s,j,cx):
    for x in range(2470,4580,220):
        if not cx-80<x<cx+1040:continue
        pts=[(x-cx+math.sin(y*.008+x)*19,y) for y in range(225,1908,24)]
        pygame.draw.lines(s,(57,76,48),False,pts,12)
        pygame.draw.lines(s,(104,114,70),False,[(a-3,b) for a,b in pts],1)
    for x,y in ((2730,790),(3020,790),(3510,790),(4320,790),(3960,1462),(3020,1828)):
        for n in (-1,0,1):
            px=x-cx+n*30
            pygame.draw.arc(s,(106,120,75),(px-15,y-35,30,34),0,math.pi,2)
    x, y = FLOR[0]-cx, FLOR[1]
    if -45 < x < 1005 and 'jardim_aberto' in j.cartografia:
        pygame.draw.lines(s,(111,130,81),False,[(x-5,y+32),(x+4,y+18),(x,y+3)],4)
        for face in (-1,1):
            pygame.draw.polygon(s,(98,123,73),[(x,y+22),(x+face*19,y+14),(x+face*24,y+17),(x,y+29)])
            pygame.draw.lines(s,(194,162,112),False,[(x,y+4),(x+face*14,y-9),(x+face*18,y-2),(x+face*11,y+6)],3)
        pygame.draw.ellipse(s,(160,111,77),(x-10,y-2,20,9))
        pygame.draw.circle(s,AMBAR,(x,y+1),3)
        brilho(s,(x,y+1),18)
    if 'jardim_calha' in j.cartografia:
        for n in range(6):
            yy=1480+n*5
            pygame.draw.line(s,(90,144,144),(3530-cx,yy),(4165-cx,yy-13),1)
