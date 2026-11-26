"""Mapa jogável e rumo do clarão, ambos derivados da geometria e do objetivo atual."""
import math
from itertools import chain

from . import pygame_hd as pygame

from . import aula_sino
from .ilustracao import AMBAR, OSSO, PALIDO, TEAL, fonte, losango, painel, tamanho_texto, texto


def texto_curto(msg, largura, tamanho=14, estilo="normal"):
    medida = fonte(tamanho_texto(tamanho),estilo)
    if medida.size(msg)[0]<=largura:
        return msg
    while msg and medida.size(msg+"…")[0]>largura:
        msg=msg[:-1]
    return msg.rstrip()+"…"


def dimensoes(j):
    if j.em_vertical:
        from .corte_vertical import LARGURA, ALTURA
        return LARGURA,ALTURA
    return j.fase.width,getattr(j,"altura_mundo",540)


def alvo_local(j):
    from .orientacao import objetivo_atual
    alvo=objetivo_atual(j)
    if alvo is not None and alvo.regiao==("corte" if j.em_vertical else "superficie"):
        return alvo
    return None


def janela(j,compacto):
    w,h=dimensoes(j)
    if not compacto:
        return pygame.Rect(0,0,w,h)
    largura,altura=min(1800,w),min(760,h)
    x=max(0,min(w-largura,j.lume.rect.centerx-largura//2))
    y=max(0,min(h-altura,j.lume.rect.centery-altura//2))
    return pygame.Rect(x,y,largura,altura)


def mapa_local(s,j,rect,compacto=False,*,janela_mundo=None):
    """A planta usa os sólidos reais, inclusive grades e o novo subsolo contínuo."""
    r=pygame.Rect(rect)
    mundo=janela(j,compacto) if janela_mundo is None else pygame.FRect(janela_mundo)
    sx,sy=r.w/mundo.w,r.h/mundo.h
    def ponto(x,y):
        return round(r.x+(x-mundo.x)*sx),round(r.y+(y-mundo.y)*sy)
    clip=s.get_clip()
    s.set_clip(r.clip(clip))
    pygame.draw.rect(s,(12,22,24),r)
    if j.em_vertical:
        from .corte_vertical import setor
    for tr in j.solidos:
        if tr.tipo=="arena" or not tr.rect.colliderect(mundo):
            continue
        x,y=ponto(tr.rect.left,tr.rect.top)
        w,h=max(1,round(tr.rect.w*sx)),max(1,round(tr.rect.h*sy))
        cor=(69,95,81) if tr.atravessavel else (45,62,52)
        pygame.draw.rect(s,cor,(x,y,w,h))
        pygame.draw.line(s,(126,154,125) if tr.descida else (88,119,102),(x,y),(x+w,y),1)
    cam=pygame.Rect(round(r.x+(j.camera-mundo.x)*sx),
                    round(r.y+(j.camera_y-mundo.y)*sy),round(960*sx),round(540*sy))
    if not getattr(j,'_mapa_sem_lume',False):pygame.draw.rect(s,(64,81,77),cam,1)
    for o in j.objetos:
        if o.tipo not in ("refugio","marco","fenda","passagem","valvula","saida","voltar","corda_borda",'lanterna') and not o.id.startswith("borda_"):
            continue
        if not mundo.collidepoint(o.x,o.y-8):
            continue
        px,py=ponto(o.x,o.y-12)
        if o.tipo=='lanterna':
            pygame.draw.circle(s,AMBAR,(px,py),4,1)
        elif o.tipo in ('refugio','marco'):
            pygame.draw.circle(s,PALIDO,(px,py),2 if compacto else 4,1)
        elif o.tipo=="valvula":
            pygame.draw.circle(s,(94,143,139),(px,py),1 if compacto else 3)
        else:
            losango(s,px,py,2 if compacto else 4,TEAL,False)
    alvo=alvo_local(j)
    from .descoberta import chave, conhecida, TAMANHO
    # Apaga somente trechos ainda não percorridos, inclusive partes de uma
    # plataforma longa que continua para dentro de uma sala desconhecida.
    largura,altura=dimensoes(j)
    colunas=range(max(0,math.floor(mundo.left/TAMANHO)),
                  min(math.ceil(largura/TAMANHO),math.ceil(mundo.right/TAMANHO)))
    linhas=range(max(0,math.floor(mundo.top/TAMANHO)),
                 min(math.ceil(altura/TAMANHO),math.ceil(mundo.bottom/TAMANHO)))
    for gx in colunas:
        prefixo=chave(j,gx*TAMANHO,0).removesuffix('0')
        descobertas=(gy for gy in linhas if prefixo+str(gy) in j.explorado)
        inicio=linhas.start
        # Cada célula descoberta encerra uma faixa de células ocultas.
        for gy in chain(descobertas,(linhas.stop,)):
            if inicio<gy:
                x,y=ponto(gx*TAMANHO,inicio*TAMANHO)
                x2,y2=ponto((gx+1)*TAMANHO,gy*TAMANHO)
                pygame.draw.rect(s,(12,22,24),(x,y,x2-x+1,y2-y+1))
            inicio=gy+1
    if aula_sino.ativa(j):
        for volta, coluna, y in j.pisadas_escuta:
            x = coluna*TAMANHO + TAMANHO//2
            if volta == j.volta and mundo.collidepoint(x,y):
                px,py = ponto(x,y)
                meia = max(1, round(TAMANHO*sx*.36))
                pygame.draw.line(s,aula_sino.COR_PISADA,(px-meia,py-2),(px+meia,py-2),2)
        x,y = aula_sino.SAIDA
        if mundo.collidepoint(x,y-34) and conhecida(j,x,y-34):
            px,py = ponto(x,y-34)
            pygame.draw.lines(s,TEAL,False,[(px-4,py+2),(px,py-2),(px+4,py+2)],1)
    if alvo and mundo.collidepoint(alvo.x,alvo.y-20) and conhecida(j,alvo.x,alvo.y-20):
        px,py=ponto(alvo.x,alvo.y-20)
        px=max(r.left+6,min(r.right-7,px))
        py=max(r.top+6,min(r.bottom-7,py))
        pygame.draw.circle(s,(162,230,198),(px,py),4 if compacto else 7,1)
        pygame.draw.line(s,(162,230,198),(px-6,py),(px+6,py),1)
        pygame.draw.line(s,(162,230,198),(px,py-6),(px,py+6),1)
        if not compacto:
            label=texto_curto(alvo.nome,min(200,r.w-14),14,"forte")
            largura=fonte(tamanho_texto(14),"forte").size(label)[0]
            tx=max(r.left+4,min(r.right-largura-4,px+12))
            ty=max(r.top+2,min(r.bottom-19,py-24))
            painel(s,(tx-3,ty-1,largura+6,21),False)
            texto(s,label,tx,ty,14,OSSO,"forte")
    if not compacto:
        from .raizes_bosque import ativo
        if ativo(j):
            from .arte_raizes import nomes_mapa
            nomes_mapa(s,j,r,ponto,conhecida)
    from .marcas_mapa import desenhar as desenhar_marcas
    from .sinalizacao import descidas
    for rampa in descidas(j):
        x,y=rampa.centerx,rampa.top+20
        if mundo.collidepoint(x,y) and conhecida(j,x,y):
            px,py=ponto(x,y)
            pygame.draw.lines(s,AMBAR,False,[(px-3,py-2),(px,py+2),(px+3,py-2)],1)
    from .luzes_mundo import fontes as globos
    for x,y,raio in globos(j):
        if mundo.collidepoint(x,y) and conhecida(j,x,y):
            px,py=ponto(x,y);pygame.draw.circle(s,AMBAR,(px,py),4,1)
            pygame.draw.circle(s,TEAL,(px,py),1)
    desenhar_marcas(s,j,ponto,mundo)
    if not getattr(j,'_mapa_sem_lume',False):
        px,py=ponto(*j.lume.rect.center)
        if r.collidepoint(px,py):losango(s,px,py,4 if compacto else 6,AMBAR)
    s.set_clip(clip)
    pygame.draw.rect(s,(62,85,80),r,1)


def minimapa(s,j):
    chefe=j.boss and not j.boss.vencido
    y=88 if chefe else 18
    r=pygame.Rect(250,y,416,88)
    painel(s,r)
    texto(s,"TRILHA LOCAL",261,y+4,10,PALIDO,"forte")
    texto(s,"TAB  mapa completo",655,y+4,10,PALIDO,"normal","right")
    mapa_local(s,j,(261,y+21,394,43),True)
    alvo=alvo_local(j)
    legenda=("Desvio · " if alvo and alvo.opcional else "Destino · ")+(alvo.nome if alvo else j.fase.name)
    texto(s,texto_curto(legenda,389,12,"forte"),261,y+68,12,(162,230,198),"forte")


def rastro_objetivo(s,j):
    """O clarão aponta o rumo por 2,8 s; não afirma que a reta seja caminhável."""
    if hasattr(j,"sala_id") or not j.vestigios:
        return
    idade=j.tempo-j.vestigios[-1].inicio
    if not 0<=idade<2.8:
        return
    alvo=alvo_local(j)
    if alvo is None:
        return
    from .descoberta import conhecida
    if not conhecida(j,alvo.x,alvo.y-20):
        return
    px,py=j.lume.rect.center
    dx,dy=alvo.x-px,alvo.y-20-py
    dist=math.hypot(dx,dy)
    if dist<34:
        return
    dx,dy=dx/dist,dy/dist
    x,y=px-j.camera,py-j.camera_y
    fase=1-min(1,max(0,(idade-1.6)/1.2))
    cor=tuple(round(c*fase) for c in (162,230,198))
    alcance=min(100.,dist-12.)
    inicio=min(30.,alcance*.35)
    for n in range(5):
        d=inicio+(alcance-8-inicio)*n/4
        pygame.draw.circle(s,cor,(round(x+dx*d),round(y+dy*d)),max(1,3-n//2))
    tx,ty=x+dx*alcance,y+dy*alcance
    pygame.draw.lines(s,cor,False,[(tx-dx*9-dy*5,ty-dy*9+dx*5),(tx,ty),
                                  (tx-dx*9+dy*5,ty-dy*9-dx*5)],2)
