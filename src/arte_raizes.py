"""Sinais e encaixes da raiz: tudo usa as coordenadas físicas da região."""
import math
from . import pygame_hd as pygame
from .ilustracao import AMBAR, OSSO, PALIDO, brilho, texto
from . import raizes_bosque as r


def objeto(s,o,j,cx,t):
    x,y=o.x-cx,o.y
    if o.id=='cipos_baixo':
        topo=442 if 'cipo_estendido' in j.flags else 842
        pts=[(x+math.sin(h*.025)*2,h) for h in range(topo-16,y+1,12)]
        pygame.draw.lines(s,(73,94,51),False,pts,7)
        pygame.draw.lines(s,(165,155,97),False,pts,2)
        for h in range(topo+14,y,31):
            pygame.draw.line(s,(190,171,113),(x-7,h-2),(x+7,h+2),3)
        pygame.draw.ellipse(s,AMBAR,(x-10,y-20,20,10),2)
    elif o.id=='pino_ninho':
        pygame.draw.line(s,OSSO,(x-14,y-9),(x+14,y-14),4)
        pygame.draw.lines(s,AMBAR,False,[(x-10,y-15),(x-10,y-5),(x-4,y-5)],3)
        brilho(s,(x,y-11),16)
    elif o.id=='ambar_ninho':
        dy=math.sin(t*3)*2
        pygame.draw.polygon(s,(153,99,37),[(x,y-37+dy),(x-15,y-11+dy),(x-8,y-2+dy),(x+12,y-6+dy),(x+16,y-20+dy)])
        pygame.draw.lines(s,AMBAR,False,[(x-4,y-23+dy),(x+5,y-17+dy),(x,y-8+dy)],2)
        brilho(s,(x,y-19),20)
    elif o.id=='porta_ninho':
        px=2095-cx
        pygame.draw.circle(s,(115,125,83),(round(px),y-41),12,2)
        pygame.draw.line(s,OSSO,(px-7,y-42),(px+7,y-42),3)
        pygame.draw.line(s,(103,108,72),(x,y),(px,y-36),3)
    elif o.id=='trava_cipo':
        pygame.draw.line(s,(114,133,80),(x,y-42),(x,y-7),5)
        pygame.draw.ellipse(s,AMBAR,(x-10,y-45,20,19),2)
        for n in range(3):
            pygame.draw.line(s,(139,122,78),(x-12,y-19+n*5),(x+12,y-16+n*5),2)
    elif o.id=='pista_pino':
        pygame.draw.ellipse(s,(69,82,49),(x-22,y-28,44,26))
        for dx in (-8,8):
            pygame.draw.lines(s,AMBAR,False,[(x+dx-4,y-11),(x+dx,y-20),(x+dx+4,y-11)],2)
        pygame.draw.line(s,OSSO,(x-10,y-5),(x+11,y-9),2)
    else:
        pygame.draw.line(s,(105,117,72),(x,y),(x,y-57),4)
        pygame.draw.ellipse(s,(56,66,45),(x-24,y-66,49,29))
        for n in range(3):
            yy=y-59+n*7
            pygame.draw.line(s,PALIDO,(x-13,yy),(x+11,yy),2)
            pygame.draw.circle(s,AMBAR,(round(x-16+n*12),yy),2)


def detalhes(s,j,cx):
    # Sulcos que descem da grade: pistas locais, também cobertas pela neblina.
    for x in (1586,1640,1712):
        pontos=[(x-cx,442),(x-cx-13,484),(x-cx+9,535)]
        pygame.draw.lines(s,(100,114,69),False,pontos,3)
    for x in range(1500,2080,92):
        y=827
        pygame.draw.arc(s,(106,119,76),(x-cx,y-24,43,31),0,math.pi,2)
        pygame.draw.line(s,(64,81,51),(x-cx+22,y+6),(x-cx+14,y+21),2)
    pygame.draw.lines(s,(157,138,86),False,[(1880-cx,829),(1900-cx,792),(1940-cx,748),(1929-cx,702),(1940-cx,648)],2)
    # Suporte sob os galhos é uma raiz fina; não usa um tronco de pé como chão.
    for x,y,w in ((1580,542,140),(1560,642,340),(1570,742,210),(1860,742,165),(1830,642,130)):
        pygame.draw.lines(s,(76,87,54),False,[(x-cx+12,y+12),(x-cx+30,y+27),(x-cx+w-15,y+13)],4)
    for x in range(1500,2040,93):
        pygame.draw.ellipse(s,(61,68,43),(x-cx,1207,58,66),3)
        pygame.draw.lines(s,(102,108,67),False,[(x-cx+8,1218),(x-cx+31,1203),(x-cx+54,1220)],2)


def nomes_mapa(s,j,rct,ponto,conhecida):
    for ident,nome,sala in r.SALAS:
        if 'viu_raizes_'+ident not in j.flags:continue
        x,y=sala.left+70,sala.bottom-45
        if not conhecida(j,x,y):continue
        px,py=ponto(x,y)
        curto={'galeria':'Galeria','poco':'Poço','camara':'Câmara'}[ident]
        texto(s,curto,px,py,11,PALIDO)
