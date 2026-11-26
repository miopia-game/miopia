"""Marcas de movimento no corpo, na superfície atingida e nos projéteis em voo."""
from math import cos, hypot, pi, sin, tau

from . import pygame_hd as pygame
from .ilustracao import alto_contraste, claroes_suaves

PALETAS = {
    "morcego": (220,145,95), "asa-fendida": (234,116,139),
    "vespa": (243,201,83), "aranha": (223,195,160), "tecela": (164,217,197),
    "carabideo": (122,201,165), "caruncho": (218,164,91), "casco-oco": (251,176,65),
    "sombra": (174,145,228), "cobra": (169,208,112), "cobra-dos-bercos": (197,205,126),
    "coruja": (221,216,181), "cria": (177,205,173),
}
MARFIM = (251,237,201)


def tinta(cor, luz):
    return tuple(min(255,round(c*luz)) for c in cor)


def forma(s, cor, pontos):
    pygame.draw.polygon(s,cor,pontos)
    pygame.draw.aalines(s,cor,True,pontos)


def fita(s, pontos, largura, cor):
    """As bordas se encontram nas pontas. O veio claro revela o sentido da curva."""
    cima,baixo=[],[]
    for i,(x,y) in enumerate(pontos):
        a,b=pontos[max(0,i-1)],pontos[min(i+1,len(pontos)-1)]
        dx,dy=b[0]-a[0],b[1]-a[1]
        r=largura*sin(pi*i/(len(pontos)-1))**.8/max(.001,hypot(dx,dy))
        cima.append((x-dy*r,y+dx*r))
        baixo.append((x+dy*r,y-dx*r))
    forma(s,tinta(cor,.66),cima+baixo[::-1])
    forma(s,cor,cima+pontos[::-1])
    if not claroes_suaves() or alto_contraste():
        pygame.draw.aalines(s,MARFIM,False,cima[len(cima)//2:])


def lascas(s, ponto, p, cor, peso=1., quantidade=7):
    """Grãos lançados da origem descrevem arcos diferentes e caem por gravidade."""
    for i in range(0,quantidade,2 if claroes_suaves() else 1):
        t=(p-.047*(i%4))/.81
        if not 0<t<1:
            continue
        x=-(9+i*3)*t
        y=-(23+i%3*10)*t + 37*t*t
        r=(1-t)*peso*(1.4+i%3)
        forma(s,tinta(cor,.92-.25*t),[ponto(x-r,y),ponto(x,y-r*1.6),
                                      ponto(x+r*1.3,y-.4*r),ponto(x+.3*r,y+r)])


def gumes(s, ponto, p, cor, garras):
    # Cada garra descreve só a porção que já passou pelo arco.
    inicio=max(0.,p-.44)
    for n in range(garras):
        pontos=[]
        for i in range(12):
            u=inicio+(p-inicio)*i/11
            a=-1.3+2.65*u
            pontos.append(ponto(12+n*4+(18+n)*cos(a),-18+13*sin(a)+n*4))
        fita(s,pontos,(1.25+n*.23)*sin(pi*p),cor)


def onda(s, pos, frente, p, cor, escala=1.):
    # Uma frente de terra ativa, com espículas que se levantam e quebram na cauda.
    x,y=pos
    def pt(u,v): return x+frente*u*escala,y+v*escala
    for i in range(4):
        u=9-i*7
        altura=(10+i%2*3)*(1-i*.16)*(1+.24*sin(tau*p+i))
        forma(s,tinta(cor,.47),[pt(u-7,1),pt(u-2,-altura*.72),pt(u+3,-altura),pt(u+5,1)])
        forma(s,cor,[pt(u-3,-1),pt(u+3,-altura),pt(u+1,-2)])
    lascas(s,pt,p,cor,.75,5)


def fenda(s,pos,p):
    x,y=pos
    for lado in (-1,1):
        def pt(u,v):return x+lado*u,y+v
        for n in range(3):
            u=4+n*7
            h=(26-5*n)*sin(pi*min(1.,max(0.,p*1.28-.1*n)))**.8
            forma(s,(74,49,99),[pt(u-4,0),pt(u-1,-h*.6),pt(u+6,-h),pt(u+3,-3)])
            pygame.draw.aaline(s,PALETAS["sombra"],pt(u+6,-h),pt(u+3,-3))
        lascas(s,pt,p,PALETAS["sombra"],.8,4)


def efeito_ataque(s,ident,tecnica,fase,ponto,lado,p,escala=1.):
    if fase not in ("ataque","recuo"):
        return
    x,y=ponto
    cor=PALETAS[ident]
    def pt(u,v):
        return x+lado*u*escala,y+v*escala
    def atras(u,v):
        return pt(u-9,v)
    cascos=ident in ("carabideo","caruncho","casco-oco")
    if fase=="recuo":
        if cascos or tecnica in ("salto","salto_alto","queda"):
            lascas(s,atras,p,cor,.78,4)
        return
    if not 0<p<1:
        return
    forca=sin(pi*p)
    if ident in ("morcego","asa-fendida"):
        # A membrana arrasta o ar atrás do ombro. A asa rasgada solta duas fitas.
        for n in range(3 if ident=="asa-fendida" else 2):
            curva=[pt(-9-32*u,-17+n*7-7*sin(pi*(u+p))*(1-u)-6*u*u)
                   for u in (i/12 for i in range(13))]
            fita(s,curva,(1.8+n*.48)*escala*forca,cor)
        if ident=="asa-fendida":
            gumes(s,pt,p,cor,2)
    elif ident in ("aranha","cria","tecela"):
        if ident=="tecela" or tecnica in ("fio","leque_fio","fio_duplo"):
            # Laçadas de seda se desenrolam das fiandeiras ao soltar o fio.
            for n in range(2):
                curva=[pt(-9+16*u+(5-3*p)*sin(u*tau+p*3+n),-12+n*4-7*cos(u*tau+p*3+n)*forca)
                       for u in (i/14 for i in range(15))]
                fita(s,curva,.83*escala,cor)
        elif ident=="cria":
            lascas(s,atras,p,cor,.59,5)
            gumes(s,pt,p,cor,1)
        else:
            for sinal in (-1,1):
                curva=[pt(12+13*u,-12+sinal*(2+8*(1-p)*(1-u)+4*sin(pi*u)))
                       for u in (i/10 for i in range(11))]
                fita(s,curva,1.4*forca,cor)
    elif cascos:
        lascas(s,atras,p,cor,1.25 if ident=="casco-oco" else .9)
        if ident=="carabideo" and tecnica=="carga":
            # Reflexo de atrito percorre o corno, com faíscas voltadas para o corpo.
            curva=[pt(10+16*u,-10-7*u*u-3*p) for u in (i/10 for i in range(11))]
            fita(s,curva,1.7*escala*forca,cor)
        if ident=="casco-oco" or tecnica in ("varrida","varredura","varrida_casco"):
            gumes(s,pt,p,cor,1)
        if ident=="caruncho" and tecnica in ("onda_dupla","onda"):
            onda(s,pt(14,-1),lado,p,cor,escala*.64)
    elif ident=="sombra":
        for n in range(3):
            curva=[pt(-6-25*u,-14+4*n-7*sin(pi*u+p*3+n)*u) for u in (i/12 for i in range(13))]
            fita(s,curva,escala*(1.8-.3*n)*forca,cor)
    elif ident in ("cobra","cobra-dos-bercos"):
        for n in range(2 if ident=="cobra" else 4):
            t=(p-n*.065)/.8
            if 0<t<1:
                a,b=pt(18+(7+n*2)*t,-12-(9+n)*t+23*t*t)
                r=(1-t)*(2.6 if ident=="cobra-dos-bercos" else 1.8)*escala
                forma(s,cor,[(a-r,b),(a,b-r*1.7),(a+r,b),(a,b+r)])
    elif ident=="vespa":
        # O ferrão vibra no abdômen e o pólen se desprende atrás.
        curva=[pt(9+17*u,-11+2*sin(tau*(u+p))*u) for u in (i/10 for i in range(11))]
        fita(s,curva,1.9*forca,cor)
        lascas(s,atras,p,cor,.55,5)
    else:
        gumes(s,pt,p,cor,3)
        for n in range(3):
            u=p*(16+5*n)
            px,py=pt(-7-u,-20+4*n+16*p*p)
            pena(s,(px,py),(-lado,.5+sin(p*3+n)),cor,.46*escala*(1-.5*p))


def pena(s,pos,vel,cor,escala=1.):
    x,y=pos
    dx,dy=vel
    norma=max(.001,hypot(dx,dy))
    dx,dy=dx/norma,dy/norma
    def pt(u,v):return x+escala*(dx*u-dy*v),y+escala*(dy*u+dx*v)
    forma(s,tinta(cor,.58),[pt(8,0),pt(-3,3.6),pt(-7,2),pt(-10,3),pt(-8,-1),pt(-3,-3)])
    forma(s,cor,[pt(8,0),pt(-2,-2.8),pt(-8,-1),pt(-4,0)])
    pygame.draw.aaline(s,MARFIM,pt(-11,0),pt(7,0))


def projetil(s,tipo,pos,vel,tempo,cor):
    x,y=pos
    dx,dy=vel
    norma=max(.001,hypot(dx,dy))
    dx,dy=dx/norma,dy/norma
    def pt(u,v):return x+dx*u-dy*v,y+dy*u+dx*v
    if tipo=="onda":
        onda(s,pos,1 if dx>=0 else -1,(tempo*3)%1,cor)
    elif tipo=="pena":
        pena(s,pos,vel,cor,1.25)
    elif tipo=="fio":
        for n in range(2):
            curva=[pt(-20+22*u,(1-u)*3*sin(tau*u+tempo*14+n*pi)) for u in (i/10 for i in range(11))]
            pygame.draw.aalines(s,cor,False,curva)
        forma(s,MARFIM,[pt(4,0),pt(-1,-2.8),pt(-4,0),pt(-1,2.8)])
    elif tipo=="ferrao":
        forma(s,tinta(cor,.58),[pt(10,0),pt(-4,3.8),pt(-2,1),pt(-10,1.9),pt(-6,-2.4)])
        forma(s,cor,[pt(10,0),pt(-4,-2.2),pt(-6,-.4)])
        pygame.draw.aaline(s,MARFIM,pt(-1,-1.1),pt(10,0))
    elif tipo=="orbe":
        pygame.draw.circle(s,(66,39,89),pos,7)
        for n in range(2):
            curva=[]
            for i in range(13):
                a=tempo*7+n*pi+i*.13
                curva.append(pt(7*cos(a),6*sin(a)))
            fita(s,curva,1.4,cor)
        forma(s,MARFIM,[pt(-2,0),pt(0,-2.6),pt(2,0),pt(0,2.6)])
    elif tipo=="veneno":
        curva=[pt(-15+14*u,2*sin(u*pi+tempo*10)*(1-u)) for u in (i/10 for i in range(11))]
        fita(s,curva,1.6,cor)
        pygame.draw.circle(s,tinta(cor,.43),pos,6)
        pygame.draw.circle(s,cor,pt(1,0),4)
        pygame.draw.circle(s,MARFIM,pt(1,-2),1)
    else:
        for n in range(2):
            curva=[pt(-7*n+5*cos(a),7*sin(a)) for a in (-1.2+i*.20 for i in range(13))]
            fita(s,curva,1.1,cor)
