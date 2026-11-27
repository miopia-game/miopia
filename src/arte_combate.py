"""Silhuetas, rastros e avisos. Os sinais são desenhados no ponto usado pela colisão."""
import math
from . import pygame_hd as pygame
from .ilustracao import AMBAR, OSSO, PALIDO, PERIGO, alto_contraste, brilho, claroes_suaves, losango, texto
from . import arte_golpes_fauna as golpes, arte_inimigos as fauna, movimento_arte
from .fauna_jardim import TEMPO_CACA

CORES = {"fio": (159, 209, 211), "ferrao": (253, 185, 100), "onda": (226, 151, 118), "eco": (153,175,216),"veneno":(163,197,104)}
MEDIDAS = {
    "morcego": (74, 47), "aranha": (72, 51), "vespa": (72, 53),
    "sombra": (64, 56), "carabideo": (79, 55), "cobra": (82, 62),
    "caruncho": (106, 69), "cobra-dos-bercos": (108, 87),
}


def criatura(e):
    if e.tipo == "carabideo" and hasattr(e, "nome"):
        return "caruncho"
    if e.tipo == "cobra" and hasattr(e, "nome"):
        return "cobra-dos-bercos"
    return e.tipo


def fase_da_criatura(e):
    tecnica = getattr(e, "acao_atual", "") or e.tecnica
    if e.estado == "aviso_caca":
        return "preparacao", fauna.fracao(1-e.t/TEMPO_CACA), "bote_caca"
    if e.estado == "aviso":
        duracao = getattr(e, "duracao_aviso", e.ficha.aviso/e.ritmo)
        return "preparacao", fauna.fracao(1-e.t/duracao), tecnica
    if e.estado == "bote_caca":
        return "ataque", fauna.fracao(1-e.t/.31), "bote_caca"
    if e.estado == "investida":
        return "ataque", fauna.fracao(1-e.t/max(e.duracao,.01)), tecnica
    if e.estado == "recuo_caca" and e.t < .55:
        return "neutro", 0., "bote_caca"
    if e.estado in {"recuo", "recuo_caca"}:
        duracao = .74 if e.estado == "recuo_caca" else .65/e.ritmo
        return "recuo", fauna.fracao(1-e.t/duracao), tecnica
    if e.estado == "atordoado":
        return "ferido", 0., tecnica
    if e.estado == "poleiro":
        return "repouso", 0., tecnica
    if e.estado in {"patrulha", "manobra", "investigar"} and criatura(e) in fauna.TERRESTRES:
        return "passos", 0., tecnica
    return "neutro", 0., tecnica


def corpo(s,e,cx,t):
    x, y = e.rect.centerx-cx, e.rect.bottom
    ident = criatura(e)
    fase, p, tecnica = fase_da_criatura(e)
    w, h = MEDIDAS[ident]
    if getattr(e, "grupo", None) == "ninhada":
        w, h = round(w*.76), round(h*.78)
    if e.estado == "poleiro":
        w, h = 26, 35
    if getattr(e,'cego',0)>0:
        for n in range(3):
            ang=t*7+n*2.1
            losango(s,round(x+math.cos(ang)*14),round(e.rect.top-9+math.sin(ang)*4),2,OSSO)
    pe = y+2
    if e.tipo in {"morcego", "vespa"} and e.estado != "poleiro":
        pe = e.rect.centery
    passos = movimento_arte.deslocamento(e, e.rect.centerx, t, e.frente)
    rect = fauna.corpo(s, ident, fase, x, pe, (w,h), e.frente, t, p, tecnica,
                       centro=e.tipo in {"morcego", "vespa"} and e.estado != "poleiro",
                       passos=passos, duracao=e.duracao)
    h = y-rect.top
    if e.estado in ("isca_fagulha","fuga_fagulha"):
        cor = AMBAR if e.estado == "isca_fagulha" else (189,161,213)
        px,py = round(x+e.frente*14),round(y-h-9)
        pygame.draw.lines(s,cor,False,[(px-e.frente*4,py-3),(px,py),(px-e.frente*4,py+3)],2)
    if e.estado == "investigar":
        # Duas marcas claras junto às patas dianteiras acompanham a escuta.
        cor = (153, 195, 186)
        for n in (0, 1):
            px = x + e.frente * (17 + 5*n)
            py = y - h + 3*n
            pygame.draw.aaline(s, cor, (px, py), (px + e.frente*5, py-4))
    if e.flash>0:
        raio = max(4,round(18*e.flash/.20))
        for i in range(4):
            a=i*math.pi/2+.48
            pygame.draw.line(s, OSSO, (x+math.cos(a)*raio,y-h/2+math.sin(a)*raio),
                             (x+math.cos(a)*(raio+5),y-h/2+math.sin(a)*(raio+5)),2)
    if getattr(e,"lentidao",0)>0:
        for n in range(5):
            pygame.draw.circle(s,AMBAR,(round(x+math.sin(t*2+n*1.7)*28),round(y-h/2+math.cos(t*2+n)*19)),2)
    if hasattr(e,'nome'):
        texto(s,e.nome+(' · II' if getattr(e,'fase',1)==2 else ''),x,y-h-43,13,AMBAR,'forte','centerx')
        pygame.draw.line(s,(78,79,52),(x-48,y-h-21),(x+48,y-h-21),4)
        pygame.draw.line(s,AMBAR,(x-48,y-h-21),(x-48+96*max(0,e.vida/e.max_vida),y-h-21),3)
        if getattr(e,'fase',1)==2:
            for n in range(3):
                px=x-14+n*11
                pygame.draw.lines(s,AMBAR,False,[(px-3,y-36),(px+2,y-30),(px-2,y-24)],2)
        if hasattr(e, "exposta") and not e.exposta:
            texto(s,"Escamas fechadas",x,y-h-15,11,PALIDO,"forte","centerx")
    if e.guarda:
        losango(s,x,y-h-17,5,PERIGO,False)
        pygame.draw.line(s,AMBAR,(x-8,y-h-17),(x-4,y-h-17),1)
        pygame.draw.line(s,AMBAR,(x+4,y-h-17),(x+8,y-h-17),1)
    if 0<e.vida<e.max_vida and not hasattr(e,'nome'):
        for n in range(e.max_vida):
            losango(s, x+7*n-(e.max_vida-1)*3.5,y-h-6,2,AMBAR if n<e.vida else (92,96,96))


def inimigo(s,e,cx,lume,t):
    if not -105 < e.rect.centerx-cx < 1065:
        return
    if e.ativo:
        corpo(s,e,cx,t)
        return
    marca = getattr(e, "impacto_corte", None)
    if marca and marca.abate and 0 <= t-marca.inicio < .27:
        p = (t-marca.inicio)/.27
        ident = criatura(e)
        destino = pygame.destino(s)
        cel, _, _ = movimento_arte._quadro(ident+"-golpe", 12+round(3*p), MEDIDAS[ident],
                                            e.frente, 0, destino.escala)
        pose = cel.copy()
        pose.set_alpha(round(225*(1-p)))
        centro = (round(e.rect.centerx-cx+marca.lado*16*p), round(e.rect.centery+26*p*p))
        destino.blit(pose, pose.get_rect(center=centro))

def aviso(s,e,cx):
    if e.estado in {"aviso", "aviso_caca"}:
        x,y=e.rect.centerx-cx,e.rect.top-13
        _, etapa, _ = fase_da_criatura(e)
        cor=(255,197,157) if alto_contraste() else (215,154,120)
        losango(s,x,y,round(3+etapa*3),cor,False)
    elif e.estado == "investida" and e.tecnica == "fenda":
        x,y=e.alvo.x-cx,e.alvo.y
        offsets=(-48,48) if getattr(e,"acao_atual","")=="fenda_dupla" else (0,)
        for dx in offsets:
            if -65<x+dx<1025:
                _, p, _ = fase_da_criatura(e)
                golpes.fenda(s,(x+dx,y),p)



def projeteis(s,e,cx,lume,raio,visivel=None):
    if not e.ativo:
        return
    if getattr(e, "exposta", False) and pygame.Vector2(e.rect.center).distance_to(lume.rect.center) < 260:
        # A brecha permanece legível na penumbra.
        x,y = round(e.rect.centerx-cx),round(e.rect.top-22)
        cor = (168, 231, 192)
        losango(s,x,y,5,cor,False)
        texto(s,"Brecha",x,y-22,12,cor,"forte","centerx")
    if abs(e.rect.centerx-lume.rect.centerx)<350:
        if e.estado in {"aviso", "aviso_caca", "investida"}:
            aviso(s,e,cx)
        if visivel is None or visivel(e.rect.center,18):
            fase, p, tecnica = fase_da_criatura(e)
            escala = 1.24 if hasattr(e, "nome") else 1.
            especie = "cria" if getattr(e,"grupo",None) == "ninhada" else criatura(e)
            golpes.efeito_ataque(s, especie, tecnica, fase, (e.rect.centerx-cx,e.rect.bottom),
                                e.frente, p, escala)
    for p in e.projeteis:
        x,y=p.pos.x-cx,p.pos.y
        perto = p.pos.distance_to(lume.rect.center)<max(raio+70,164)
        if -30<x<990 and (perto or visivel and visivel(p.pos,8)):
            cor=CORES[p.tipo]
            if p.tipo == "eco" and e.tipo == "sombra":
                ponto = round(x),round(y)
                if not claroes_suaves():
                    brilho(s,ponto,19)
                golpes.projetil(s,"orbe",ponto,p.vel,-p.vida,golpes.PALETAS["sombra"])
            else:
                golpes.projetil(s,p.tipo,(x,y),p.vel,-p.vida,cor)

def tranca(s, r):
    """Duas taquaras se curvam a partir do chão; a trança fecha o vão entre elas."""
    terra = r.bottom
    for lado in (-1, 1):
        origem = r.centerx + lado*(r.width//2)
        for n in range(3):
            ramo = [(origem + lado*(10+n*3), terra+3),
                    (origem - lado*3+n, terra-28),
                    (origem - lado*7+n, r.y+85),
                    (r.centerx + lado*(7+n), r.y+15),
                    (r.centerx + lado*11, r.y+2)]
            pygame.draw.lines(s,(45+10*n,47+6*n,38+4*n),False,ramo,8-2*n)
            pygame.draw.lines(s,(126,116,79),False,ramo,1)
    for n in range(7):
        y=terra-13-n*26
        metade=min(15,6+(y-r.top)//10)
        for lado in (-1,1):
            pts=[(r.centerx+lado*metade,y),(r.centerx,y-8),(r.centerx-lado*metade,y-19)]
            pygame.draw.lines(s,(119,91,65),False,pts,3)
            pygame.draw.lines(s,(177,139,91),False,pts,1)
    losango(s,r.centerx,terra-47,9,PERIGO,False)
    losango(s,r.centerx,terra-47,4,AMBAR)
