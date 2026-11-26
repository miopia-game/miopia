"""Grades abertas, folhas pendentes e câmera que deixa enxergar a descida."""
import math
from . import pygame_hd as pygame


def descidas(j):
    solidos=j.solidos
    for t in solidos:
        if t.tipo!='grade':continue
        r=t.rect
        if any(not outro.atravessavel and outro.rect.collidepoint(r.centerx,r.bottom+24) for outro in solidos):continue
        yield r


def camera_vertical(j,altura,dt=None,*,enquadrar=False):
    l=j.lume.rect
    acompanhar = enquadrar or l.bottom > 474 or any(
        r.left-24 <= l.centerx <= r.right+24 and abs(l.bottom-r.top) < 65 for r in descidas(j))
    alvo = max(0., min(altura-540., l.centery-300.)) if acompanhar else 0.
    if dt is None:j.camera_y=alvo
    else:j.camera_y+=(alvo-j.camera_y)*(1.-math.exp(-8.5*dt))


def desenhar(s,j,cx):
    for r in descidas(j):
        if r.right<cx or r.left>cx+960 or not j.visivel((r.centerx,r.top-4)):continue
        x,y=r.centerx-cx,r.top
        for lado in (-1,1):
            pygame.draw.lines(s,(104,129,79),False,[(x+lado*22,y+4),(x+lado*19,y+16),(x+lado*25,y+30)],2)
            pygame.draw.ellipse(s,(164,166,106),(x+lado*22-4,y+13,8,13),1)
        for n in range(2):
            yy=y+19+n*14;v=round(155+35*math.sin(j.tempo*2-n*.8))
            pygame.draw.lines(s,(v,min(220,v+18),117),False,[(x-6,yy),(x,yy+5),(x+6,yy)],2)
