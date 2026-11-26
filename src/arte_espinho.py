"""Lâmina de quitina, rastro do corte e lascas no contato com o alvo."""
from math import cos, hypot, pi, sin

from . import pygame_hd as pygame
from .ilustracao import alto_contraste, claroes_suaves

AMBAR = ((89,47,42),(209,105,48),(255,189,89),(255,242,191))
SEIVA = ((35,61,65),(47,145,139),(119,224,199),(232,255,222))


def _forma(s, cor, pontos):
    pygame.draw.polygon(s,cor,pontos)
    pygame.draw.aalines(s,cor,True,pontos)


def _lamina(s, mao, ponta, face, estreita, cores):
    x,y = mao
    dx,dy = ponta[0]-x,ponta[1]-y
    comprimento=max(1.,hypot(dx,dy))
    nx,ny = -dy*face/comprimento,dx*face/comprimento
    def ponto(u,v):
        return (x+u*dx+v*nx,y+u*dy+v*ny)
    largura = 2.7 if estreita else 4.8
    # Duas facetas e um entalhe na base conservam o espinho legível sobre uma raiz clara.
    _forma(s,cores[0],[ponto(-.10,0),ponto(.10,-largura),ponto(.32,-largura*.70),
                       ponto(.66,-largura*.5),ponta,ponto(.45,largura*.7),ponto(.19,largura),
                       ponto(.23,largura*.38),ponto(.03,largura*.5)])
    _forma(s,cores[2],[ponto(.11,-largura*.61),ponto(.54,-largura*.47),ponta,
                       ponto(.44,.3),ponto(.17,largura*.37)])
    pygame.draw.aaline(s,cores[3],ponto(.20,-largura*.64),ponta)


def desenhar(s, lume, mao, x, pe):
    ataque = lume.arma
    perfil = ataque.perfil
    face = ataque.face
    forte = ataque.tipo in ("pesado","quebra","corte3","aurora")
    estocada = ataque.equipamento == "agulha" or ataque.tipo == "avanco"
    queda = ataque.tipo == "queda"
    sobe = ataque.tipo in ("corte2","retorno","aurora")
    cores = SEIVA if ataque.luminoso else AMBAR
    cy = pe-lume.rect.h*.5
    alcance = perfil.alcance - (7 if queda else 5)
    sinal = -1 if sobe else 1
    def curso(p):
        if queda:
            return (x+face*(12*(1-p)-3), pe-5+alcance*(.18+.82*p))
        if estocada:
            return (x+face*alcance*(.45+.55*sin(p*pi*.74)),cy+3-12*p)
        angulo = -1.08 + 2.05*p
        return (x+face*alcance*cos(angulo),cy+sinal*(25 if forte else 21)*sin(angulo))
    decorrido = ataque.tempo-perfil.espera
    if decorrido < 0:
        t=1+decorrido/perfil.espera
        px,py=curso(0)
        pronto = (mao[0]+face*12,mao[1]+(18 if sobe else -18))
        ponta=(pronto[0]+(px-pronto[0])*t,pronto[1]+(py-pronto[1])*t)
        _lamina(s,mao,ponta,face,estocada,cores)
        return
    progresso=min(1., decorrido/perfil.ativo)
    cauda=max(0.,1-max(0.,decorrido-perfil.ativo)/.085)
    ponta=curso(progresso)
    if cauda > 0:
        suave = claroes_suaves()
        espessura = (4 if estocada or queda else 10 if forte else 7.5)*cauda*(.68 if suave else 1.)
        frente,atras=[],[]
        inicio = max(0.,progresso-.60*cauda)
        for i in range(15):
            u=i/14
            p=inicio+(progresso-inicio)*u
            px,py=curso(p)
            qx,qy=curso(p+.008)
            dx,dy=qx-px,qy-py
            norma=max(.001,hypot(dx,dy))
            nx,ny=-dy/norma,dx/norma
            peso=espessura*sin(pi*u)**.72*min(1.,progresso*7)
            frente.append((px+nx*peso*.54,py+ny*peso*.54))
            atras.append((px-nx*peso,py-ny*peso))
        if progresso>0 and inicio<progresso:
            _forma(s,cores[1],frente+atras[::-1])
            meio=[((a[0]+b[0])*.5,(a[1]+b[1])*.5) for a,b in zip(frente,atras)]
            _forma(s,cores[2],frente+meio[::-1])
            if not suave or alto_contraste():
                pygame.draw.aalines(s,cores[3],False,frente[3:])
    # A lâmina volta à mão depois da passagem. O rastro acaba antes da recuperação.
    recuperar=max(0.,min(1.,(decorrido-perfil.ativo)/(perfil.total-perfil.espera-perfil.ativo)))
    pronto=(mao[0]+face*10,mao[1]-12)
    ponta=tuple(a+(b-a)*recuperar for a,b in zip(ponta,pronto))
    _lamina(s,mao,ponta,face,estocada,cores)


def desenhar_impactos(s,j,cx):
    for marca in j.impactos_corte:
        idade=j.tempo-marca.inicio
        duracao=.34 if marca.abate else .24
        if not 0<=idade<duracao or not j.visivel(marca.ponto,18):
            continue
        x,y=marca.ponto
        x-=cx
        cores=SEIVA if marca.luminoso else AMBAR
        p=idade/duracao
        suave=claroes_suaves()
        if p<.40:
            r=(1-p/.40)*(5 if suave else 11)
            _forma(s,cores[3],[(x-r,y+2),(x-2,y-1),(x+2,y-r),(x+3,y-2),
                                (x+r*.8,y+1),(x+1,y+2),(x-2,y+r*.5)])
        vetores=((88,-34),(66,-80),(111,17),(-56,-42),(40,53),(-70,15))
        for vx,vy in vetores[:3 if suave else 6]:
            dx=marca.lado*vx
            px=x+dx*idade
            py=y+vy*idade+105*idade**2
            base=(px-dx*.051*(1-p),py-(vy+210*idade)*.051*(1-p))
            _forma(s,cores[2],[base,(px-1,py-1),(px+2,py),(px,py+1)])
