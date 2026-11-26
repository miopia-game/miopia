"""Arte do começo do Bosque em camadas de tinta e contornos."""
from functools import lru_cache
from math import sin

import pygame

from .fases import CHAO
from .ilustracao import alto_contraste, imagem, original, sprite

BORDA = (238, 184, 112)
SOMBRA = (29, 19, 37)
PERSONAGENS = {
    "Mimo": ("pintado_mimo", 59),
    "Nira": ("pintado_nira", 73),
    "Véspera": ("pintado_vespera", 63),
}

FUNCOES = {
    "Mimo": ("Erveiro do abrigo", (158,194,148)),
    "Nira": ("Cartógrafa do Bosque", (171,188,208)),
    "Véspera": ("Vigia dos ninhos", (238,173,101)),
}


def vegetacao(s,cx):
    for mundo, pe, largura, altura, nome, espelho in (
        (107,CHAO,77,39,"bosque_fungos",False),
        (455,CHAO,93,56,"bosque_juncos",True),
        (810,CHAO,101,67,"bosque_samambaias",False),
        (1181,CHAO,98,49,"bosque_sarcas",True),
    ):
        x = mundo-cx
        if -100 < x < 1060:
            sprite(s,nome,x,pe,largura,altura,espelho)


def cipo(s, x, pe, tempo):
    """O cipó abraça a forquilha e cai junto à faixa que Lume pode escalar."""
    x = round(x)
    topo = 240
    trama = [(x+30,topo+9),(x+23,topo-2),(x+14,topo-4),(x+5,topo+3),(x+1,topo+15)]
    for y in range(topo+18,pe-4,7):
        v = (y-topo)/(pe-topo)
        dx = round(sin(y*.058+tempo*.9)*(1.8+v*3.1))
        trama.append((x+dx,y))
    trama.append((x+3,pe-5))
    pygame.draw.lines(s,SOMBRA,False,trama,8)
    pygame.draw.lines(s,(82,96,47),False,trama,5)
    pygame.draw.aalines(s,(183,168,98),False,[(a-1,b) for a,b in trama])
    for i in (5, 11, 19, 27):
        a,b = trama[i]
        lado = -1 if i in (5,19) else 1
        pygame.draw.polygon(s,(35,39,28),[(a,b+2),(a+lado*9,b-7),(a+lado*19,b-6),(a+lado*10,b+5)])
        pygame.draw.polygon(s,(115,130,69),[(a+lado*2,b),(a+lado*8,b-5),
                                            (a+lado*16,b-5),(a+lado*9,b+3)])
    pygame.draw.arc(s,(105,112,61),(x-5,pe-15,13,14),.4,3.8,2)


def _borda(s, r, cor=BORDA):
    esquerda, direita = r.x+1, r.right-2
    pygame.draw.line(s, SOMBRA, (esquerda, r.y-1), (direita, r.y-1), 3)
    pygame.draw.line(s, cor, (esquerda, r.y), (direita, r.y), 2+int(alto_contraste()))


def terreno(s, r, tipo, primeiro=False):
    if tipo == "chao":
        _solo(s,r)
    elif primeiro:
        s.blit(imagem("pintado_raiz.png", r.w+24, 88), (r.x-18,r.y-20))
        _borda(s,r)
    else:
        broto = tipo == "broto"
        nome = "pintado_broto.png" if broto else "pintado_galho.png"
        altura = max(21, min(38, round(r.w*.22)))
        s.blit(imagem(nome, r.w+8, altura), (r.x-4,r.y-(7 if broto else 2)))
        _borda(s,r,(239, 211, 123) if broto else BORDA)


@lru_cache(maxsize=2)
def _azulejo(espelho):
    faixa = imagem("pintado_solo.png", 248, 66, espelho)
    return faixa.subsurface((12,0,224,66)).copy()


def _solo(s, r):
    area = s.get_clip().clip(r)
    if not area.width:
        return
    pygame.draw.rect(s,(24,20,38),area)
    for n in range((area.left-r.left)//224,(area.right-1-r.left)//224+1):
        x = r.x+n*224
        largura = min(224,r.right-x)
        s.blit(_azulejo(n%2==0),(x,r.y),(0,0,largura,66))
    _borda(s,pygame.Rect(area.x,r.y,area.w,area.h))


def iluminar_pousos(s, j, cx, nivel, fim):
    """Desenha a borda útil dos apoios sem revelar objetos atrás deles."""
    for t in j.solidos:
        if t.tipo not in ("plataforma","apoio") or t.rect.x >= fim:
            continue
        r = t.rect.move(-round(cx),0)
        if not s.get_clip().colliderect(r):
            continue
        perto = min(1., abs(t.rect.centerx-j.lume.rect.centerx)/480)
        fator = max(.44, 1.-perto*.56) + nivel*.05
        tom = tuple(round(c*min(1.,fator)) for c in BORDA)
        x, y = r.x, r.y
        pontos = [(x+3,y+1),(x+max(7,r.w//8),y),(r.right-8,y),(r.right-3,y+1)]
        pygame.draw.lines(s,SOMBRA,False,pontos,3)
        pygame.draw.aalines(s,tom,False,pontos)


def objeto(s,o,j,x,tempo):
    """Retorna se o objeto tem ilustração específica para esta cena."""
    if o.tipo == "npc" and o.nome in PERSONAGENS:
        _, altura = PERSONAGENS[o.nome]
        personagem(s,o.nome,x,o.y,altura,80)
    elif o.tipo == "registro":
        sprite(s,"pintado_registro",x,o.y,44,26)
    elif o.tipo == "encomenda":
        sprite(s,"mochila_bosque",x,o.y,37,29)
    elif o.tipo == "fenda":
        sprite(s,"pintado_passagem",x,o.y+3,128,72)
    elif o.tipo == "orvalho":
        sprite(s,"pintado_orvalho",x,o.y+10+round(2*sin(tempo*3+o.x)),14,22)
    else:
        return False
    return True


def personagem(s,pessoa,x,y,altura,limite):
    nome = PERSONAGENS[pessoa][0]
    arte = original(nome + ".png")
    escala = min(altura/arte.get_height(),limite/arte.get_width())
    sprite(s,nome,x,y,round(arte.get_width()*escala),round(arte.get_height()*escala))
