"""Arte do começo do Bosque em camadas de tinta e contornos."""
from functools import lru_cache
from math import sin

from . import pygame_hd as pygame

from .fases import CHAO, FASES, GALHO_DO_MORCEGO, Terreno
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


def _modelo_apoio(t):
    r = t.rect
    if (r.x, r.y, r.w) == FASES[0].plataformas[0]:
        return "raiz", r.w, False
    if t.tipo == "apoio":
        return "broto", r.w, False
    return "galho", r.w, (r.x // 110) % 2 == 0


@lru_cache(maxsize=32)
def _pintura(tipo, largura, espelho):
    if tipo == "raiz":
        w, h = round(largura*1.23), 86
        dx, dy = largura-w, -18
    elif tipo == "broto":
        w, h = largura+3, max(22, round(largura*.32))
        dx, dy = -2, -round(h*.43)
    else:
        w, h = largura+4, max(29, min(62, round(largura*.30)))
        dx, dy = -2, -round(h*.055)
    return imagem("pintado_" + tipo + ".png", w, h, espelho), dx, dy


@lru_cache(maxsize=32)
def _musgo(tipo, largura, espelho):
    arte, dx, dy = _pintura(tipo, largura, espelho)
    topo = max(0, -dy-3)
    faixa = arte.subsurface((0, topo, arte.get_width(), 12)).copy()
    # Recupera a luz nas folhas da borda e deixa a casca voltar à sombra.
    for y in range(6, 12):
        faixa.fill((255, 255, 255, round(255*(11-y)/6)), (0,y,faixa.get_width(),1),
                   special_flags=pygame.BLEND_RGBA_MULT)
    return faixa, dx, topo+dy


def terreno(s, t, camera):
    r = t.rect.move(-round(camera), 0)
    if t.tipo == "chao":
        _solo(s, r)
        return
    if (t.rect.x, t.rect.y, t.rect.w) == GALHO_DO_MORCEGO:
        tronco = _tronco_poleiro()
        s.blit(tronco, tronco.get_rect(bottomright=(r.right+7, CHAO+2)))
    arte, dx, dy = _pintura(*_modelo_apoio(t))
    s.blit(arte, (r.x+dx, r.y+dy))


@lru_cache(maxsize=1)
def _tronco_poleiro():
    # A madeira do suporte recua um plano em relação à borda jogável.
    tronco = imagem("pintado_raiz.png", 218, 251, True).copy()
    tronco.fill((121, 140, 155), special_flags=pygame.BLEND_RGB_MULT)
    return tronco


def terreno_fixo(t, fim):
    if t.tipo == "chao":
        return t.rect.x < FASES[0].pisos[0][1]
    return t.tipo == "plataforma" and t.rect.x < fim


@lru_cache(maxsize=4)
def _silhueta_terreno(geometria, contraste):
    largura = max(x+w for x,y,w,h,tipo in geometria) + 16
    altura = max(y+h for x,y,w,h,tipo in geometria)
    camada = pygame.Surface((largura, altura), pygame.SRCALPHA)
    for x, y, w, h, tipo in geometria:
        terreno(camada, Terreno(pygame.Rect(x, y, w, h), tipo), 0)
    camada.fill((87, 99, 115, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return camada


def sombrear_terreno_fixo(fundo, j, cx, cy, fim, intensidade):
    """A madeira e a terra opacas ocultam a floresta também fora do halo."""
    geometria = tuple((*t.rect, t.tipo) for t in j.solidos if terreno_fixo(t, fim))
    if geometria:
        camada = _silhueta_terreno(geometria, alto_contraste())
        camada.set_alpha(round(255 * intensidade))
        fundo.blit(camada, (-round(cx), -cy))


@lru_cache(maxsize=3)
def _leito(largura, altura):
    """Monta a margem com cortes em várias escalas da pintura de terra."""
    margem = pygame.Surface((largura, altura), pygame.SRCALPHA)
    margem.fill((24,20,38), (0,3,largura,altura-3))
    trechos = ((402,149,13,369,False), (375,134,41,312,False),
               (451,158,35,391,True), (337,135,11,307,False))
    x = 0
    n = 0
    while x < largura:
        w, h, inicio, corte, espelho = trechos[n % len(trechos)]
        terra = imagem("pintado_solo.png", w, h, espelho)
        camada = terra.subsurface((inicio, 3, corte, min(h-3, altura))).copy()
        # Uma transição curta entre bordas de terra evita a costura espelhada.
        sobreposicao = 18 if n else 0
        for coluna in range(sobreposicao):
            camada.fill((255,255,255,round(255*coluna/sobreposicao)), (coluna,0,1,altura),
                         special_flags=pygame.BLEND_RGBA_MULT)
        x -= sobreposicao
        margem.blit(camada, (x, 0))
        x += corte
        n += 1
    for y in range(altura):
        profundidade = min(1., max(0., (y-10)/max(1, altura-25)))
        tinta = tuple(255-round(atenuacao*profundidade) for atenuacao in (83,77,60))
        margem.fill((*tinta,255), (0,y,largura,1), special_flags=pygame.BLEND_RGBA_MULT)
    return margem


def _solo(s, r):
    area = s.get_clip().clip(r)
    if not area.width:
        return
    s.blit(_leito(r.w, r.h), r.topleft)
    if alto_contraste():
        pygame.draw.line(s, BORDA, (area.left, r.y), (area.right-1, r.y), 3)


def iluminar_pousos(s, j, cx, nivel, fim):
    """Desenha a borda útil dos apoios sem revelar objetos atrás deles."""
    s = pygame.destino(s)
    for t in j.solidos:
        if t.tipo not in ("plataforma","apoio") or t.rect.x >= fim:
            continue
        r = t.rect.move(-round(cx),0)
        if not s.get_clip().colliderect(r):
            continue
        faixa, dx, dy = _musgo(*_modelo_apoio(t))
        distancia = min(1., abs(t.rect.centerx-j.lume.rect.centerx)/480)
        faixa.set_alpha(round(193 - 112*distancia + 8*nivel))
        s.blit(faixa, (r.x+dx, r.y+dy))
        if alto_contraste():
            esquerda, direita = (r.left, r.y), (r.right-1, r.y)
            pygame.draw.line(s, SOMBRA, esquerda, direita, 5)
            pygame.draw.line(s, (244, 225, 166), esquerda, direita, 3)


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
