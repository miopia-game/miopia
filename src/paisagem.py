"""Cenário distante, terreno sólido, criaturas, luz de Lume e HUD."""
import math
import random
import unicodedata
from functools import lru_cache
import pygame
from . import abertura_bosque, arte_bosque, arte_ilustrada, desvios_fagulha, licao_vespera, travessia_fagulha
from . import arte_fagulha
from .arte_arena import sinais_encontro
from .arte_combate import inimigo, projeteis, golpe_lume, tranca
from .arte_lume import desenhar_lume
from .fases import FASES
from .hud_reservas import desenhar as reservas
from .ilustracao import (original, AMBAR, alto_contraste, OSSO, PALIDO, PERIGO, ROMANOS, TEAL, TINTA, brilho, dica_teclado, fonte, imagem,
                         losango, manivela, painel, placa, sprite, tamanho_texto, texto)

CORES = ((77,102,86),(81,119,119),(127,116,72),(97,86,106))
OBJETOS = {"orvalho":("orvalho",21,31), "valvula":("valvula",51,65), "corda":("corda",38,118),
           "peca":("peca",40,30), "no":("raiz",60,52), "brasa":("raiz",40,48),
           "sino":("sino",42,66), "raiz":("raiz",88,91), "registro":("registro",36,26),
           "refugio":("refugio",98,86), "atalho":("porta",61,65),
           "reserva":("registro",38,27)}
NPC_TAM = {"Nira":(61,65),"Casca":(74,60),"Eco":(48,40),"Brasa":(58,52),
           "Mimo":(56,48),"Candeia":(48,40),"Véspera":(58,47),"Fio":(69,43),
           "Risca":(81,48),"Pingo":(56,42),"Nó":(75,55),"Coruja":(96,96)}


def slug(s):
    return unicodedata.normalize("NFKD",s.lower()).encode("ascii","ignore").decode()


def arte_npc(nome):
    if nome == "Coruja":
        return "inimigos-v2/coruja-repouso"
    return "npc_" + slug(nome)


@lru_cache(maxsize=4)
def fundo(i):
    img=imagem(f"fundo_{i}.jpg",1270,714).copy()
    img.fill((158,174,182),special_flags=pygame.BLEND_RGB_MULT)
    return img


@lru_cache(maxsize=4)
def margens(i):
    """Ramos do primeiro plano passam em outra velocidade que o piso."""
    rng=random.Random(35+i)
    surf=pygame.Surface((1200,140),pygame.SRCALPHA)
    for x in range(-15,1200,47):
        h=rng.randrange(14,61)
        if i==2:
            pygame.draw.line(surf,(15,24,23,225),(x,140),(x+20,140-h),4)
            pygame.draw.polygon(surf,(24,34,29,220),[(x+12,118),(x-16,98),(x+7,120)])
        else:
            folha=imagem("obj_folha.png",h*2,h+12,x%2==0).copy()
            folha.fill((30,42,45,210),special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(folha,(x,139-h))
    return surf


@lru_cache(maxsize=1)
def raizes_subsolo():
    # Uma camada larga é recortada pela câmera; não redesenha centenas de
    # segmentos nem aloca uma superfície de fundo a cada quadro.
    sub=pygame.Surface((1280,540));sub.fill((23,29,24))
    for n in range(15):
        x=n*97-30
        pts=[(x+round(math.sin(y*.009+n)*25),y) for y in range(-40,580,12)]
        pygame.draw.lines(sub,(41+n%3*5,41+n%3*4,30),False,pts,13+n%4*5)
        pygame.draw.lines(sub,(60,57,37),False,[(x-4,y) for x,y in pts],1)
    return sub


# Tons do cenário distante, do brilho mínimo ao alto.
TINTAS_NEVOA = ((41,47,62), (70,80,101), (116,136,153), (153,166,184))


@lru_cache(maxsize=2)
def amostra_nevoa(tamanho):
    return pygame.Surface(tuple(max(1, round(lado*2/3)) for lado in tamanho))


@lru_cache(maxsize=1)
def buffers_nevoa():
    tamanho = (960,540)
    nitido, borrado, inversa, fundo = (pygame.Surface(tamanho) for _ in range(4))
    return nitido, borrado, inversa, amostra_nevoa(tamanho), fundo


def capturar_fundo(camada,cy=0):
    fundo=buffers_nevoa()[4]
    fundo.blit(camada,(0,0),pygame.Rect(0,cy,960,540))
    return fundo


def nevoa_distante(fundo, borrado, amostra, nivel, cor=None, nitidez=0.):
    if nitidez >= 1:
        borrado.blit(fundo, (0, 0))
    else:
        pygame.transform.smoothscale(fundo, amostra.get_size(), amostra)
        pygame.transform.smoothscale(amostra, borrado.get_size(), borrado)
    if 0 < nitidez < 1:
        alfa = fundo.get_alpha()
        fundo.set_alpha(round(255 * nitidez))
        borrado.blit(fundo, (0, 0))
        fundo.set_alpha(alfa)
    borrado.fill(TINTAS_NEVOA[nivel] if cor is None else cor, special_flags=pygame.BLEND_RGB_MULT)


def aplicar_nevoa(camada, luz, cy=0, fundo=None, nivel=1, cor=None, nitidez=0.):
    """Fora da luz só existe o fundo distante. Não vaza a silhueta do terreno."""
    area=pygame.Rect(0,cy,960,540)
    nitido,borrado,inversa,pequeno,_=buffers_nevoa()
    nitido.blit(camada,(0,0),area)
    nevoa_distante(fundo if fundo is not None else nitido, borrado, pequeno, nivel, cor, nitidez)
    inversa.fill((255,255,255))
    inversa.blit(luz,(0,0),special_flags=pygame.BLEND_RGB_SUB)
    borrado.blit(inversa,(0,0),special_flags=pygame.BLEND_RGB_MULT)
    nitido.blit(luz,(0,0),special_flags=pygame.BLEND_RGB_MULT)
    borrado.blit(nitido,(0,0),special_flags=pygame.BLEND_RGB_ADD)
    camada.blit(borrado,(0,cy))


@lru_cache(maxsize=16)
def mascara_luz(raio, brilho_mata, forca=255):
    r = max(4, raio)
    tom = (0,0,0)
    surf = pygame.Surface((r*2, r*2))
    surf.fill(tom)
    for n in range(r, 0, -8 if r>=900 else -2):
        v = min(1., (r-n)/100) if r>=900 else min(1., (1 - n / r) * 1.8)
        v = v*v*(3-2*v)
        cor = (round(forca*v),)*3
        pygame.draw.circle(surf, cor, (r,r), n)
        if v>=1:
            break
    return surf


@lru_cache(maxsize=1)
def buffer_luz():
    return pygame.Surface((960,540))


def compor_luz(luz,j,cx,cy,brilho_mata):
    from .visao import fontes
    from .ilustracao import claroes_suaves
    luz.fill((0,0,0))
    from .luzes_mundo import compor_zonas
    compor_zonas(luz,j,cx,cy)
    modo_suave = claroes_suaves()
    def aplicar(x, y, raio, forca=255):
        r=round(raio/8)*8
        if r>=8 and x+r>=cx and x-r<=cx+960 and y+r>=cy and y-r<=cy+540:
            luz.blit(mascara_luz(r,brilho_mata,forca),(round(x-cx)-r,round(y-cy)-r),special_flags=pygame.BLEND_RGB_MAX)
    for x,y,raio in fontes(j, vestigios=not modo_suave):
        aplicar(x,y,raio)
    if modo_suave:
        for v in j.vestigios:
            idade = max(0., j.tempo-v.inicio)
            forca = 70 + round(min(1., idade/.75)*6)*15
            aplicar(v.x, v.y, v.raio(j.tempo), forca)


@lru_cache(maxsize=80)
def rocha_lateral(w, h, tipo, semente):
    # Casca e nós verticais unem a parede de impulso à vegetação. A face útil
    # continua alinhada à colisão; os ramos decorativos não fingem plataformas.
    rng = random.Random(semente + h*5 + w)
    surf = pygame.Surface((w+10,h+4),pygame.SRCALPHA)
    esq = [(rng.randrange(1,6),y) for y in range(0,h,16)] + [(4,h)]
    direita = [(w+rng.randrange(1,6),y) for y in range(0,h,16)] + [(w+5,h)]
    pygame.draw.polygon(surf,(65,51,35),esq + list(reversed(direita)))
    pygame.draw.lines(surf,(133,124,77),False,esq,2)
    pygame.draw.lines(surf,(101,86,59),False,direita,2)
    for x in range(7,w,9):
        curva=[(x+round(math.sin(y*.037+x)*2),y) for y in range(2,h,6)]
        if len(curva)>1:
            pygame.draw.lines(surf,(91,70,44) if x%3 else (42,37,29),False,curva,2)
    for y in range(24,h-11,71):
        x=rng.randint(8,max(8,w-9))
        pygame.draw.ellipse(surf,(36,34,26),(x-5,y-9,11,23),2)
        pygame.draw.ellipse(surf,(120,93,58),(x-3,y-5,7,15),1)
        if tipo=="parede":
            for lado in (3,w+1):
                # Pequenos brotos e casca clara marcam as faces de salto.
                pygame.draw.line(surf,(156,159,101),(lado,y+18),(lado,y+30),2)
                pygame.draw.line(surf,(104,143,80),(lado,y+24),(lado+(-4 if lado==3 else 4),y+20),2)
    return surf


@lru_cache(maxsize=16)
def rocha_de_fundo(bioma, h):
    apoio=imagem("beiral_3.png",h+48,int(h*.76),True).copy()
    apoio.fill((107,128,119,255),special_flags=pygame.BLEND_RGBA_MULT)
    return apoio


def grade(s,r):
    pygame.draw.line(s,(166,158,117),r.topleft,r.topright,2)
    pygame.draw.line(s,(102,105,84),(r.left,r.top+8),(r.right,r.top+8),2)
    for x in range(r.left+3,r.right-7,9):
        pygame.draw.line(s,(147,147,110),(x,r.top+1),(x+7,r.top+8),1)
        pygame.draw.line(s,(85,93,80),(x,r.top+8),(x+7,r.top+1),1)


def sustentar_galho_do_duelo(s,j,cx):
    x,y,w=j.fase.plataformas[0]
    topo=round(x-cx)
    base=j.checkpoint[1]
    # A forquilha fica atrás do patamar e deixa a face de pouso contínua.
    raiz=[(topo+14,base),(topo+40,base-31),(topo+53,y+47),(topo+37,y+9)]
    ponta=[raiz[2],(topo+87,y+32),(topo+w-17,y+9)]
    pygame.draw.lines(s,(51,57,45),False,raiz,13)
    pygame.draw.lines(s,(68,71,54),False,ponta,7)
    pygame.draw.lines(s,(113,105,76),False,[(px-3,py) for px,py in raiz],2)
    for n in (0,1,2):
        px=topo+w-26+n*8
        pygame.draw.lines(s,(93,102,89),False,[(px,y+10),(px+12,y+30-n*4),
                                                (px+29,y+13)],1)


@lru_cache(maxsize=4)
def raiz_da_camara(w,h):
    """Raízes contínuas, sem mosaicos de solo sobre faces verticais estreitas."""
    out=pygame.Surface((w+44,h+20),pygame.SRCALPHA)
    for n in range(3):
        x=23+n*(w-3)/3
        pts=[(x+math.sin(y*.016+n)*4,y+8) for y in range(0,h+1,9)]
        pygame.draw.lines(out,(48,53,35),False,pts,13)
        pygame.draw.lines(out,(112,107,66),False,[(a-2,b) for a,b in pts],3)
        pygame.draw.lines(out,(153,134,83),False,[(a-4,b) for a,b in pts],1)
    for y in range(40,h-30,95):
        lado=-1 if y%2 else 1
        pygame.draw.lines(out,(80,83,47),False,[(22+w/2,y),(22+w/2+lado*17,y+16),(22+w/2+lado*25,y+43)],4)
    return out


def terreno(s,t,camera,i):
    r=t.rect.move(-round(camera),0)
    if r.right<0 or r.left>960 or t.tipo=="arena": return
    cor=CORES[i]
    if t.tipo=="tranca":
        tranca(s,r)
        return
    if t.tipo=="veneziana_sementes":
        from .arte_galeria import veneziana
        veneziana(s,r)
        return
    if t.tipo=="colmos_galeria":
        if r.colliderect(s.get_clip()):
            from .arte_galeria import colmos
            colmos(s,r)
        return
    if t.tipo == "apoio_fagulha":
        arte_bosque.galho(s,r,i,True)
        for x in range(r.left+12,r.right-8,15):
            pygame.draw.circle(s,(161,196,145),(x,r.y-2),2)
        return
    if t.tipo == "plataforma":
        arte_bosque.galho(s, r, i, (t.rect.x // 110) % 2 == 0)
        return
    if t.tipo=='raiz_lisa':
        pygame.draw.rect(s,(52,62,40),r)
        for n in range(3):
            x=r.left+4+n*max(3,(r.w-8)//3)
            pts=[(x+math.sin(y*.018+n)*3,y) for y in range(r.top,r.bottom+1,13)]
            pygame.draw.lines(s,(111,116,74),False,pts,2)
        return
    if t.tipo=='ninho_tranca':
        pygame.draw.rect(s,(60,64,40),r)
        for y in range(r.top+3,r.bottom,16):
            pygame.draw.line(s,(143,127,78),(r.left,y),(r.right,y+6),3)
            pygame.draw.line(s,(90,107,61),(r.left,y+8),(r.right,y-1),2)
        pygame.draw.rect(s,(162,151,96),r,1)
        return
    if t.tipo in ("vedacao","parede"):
        if i==1 and r.w<=40 and r.h>350:
            s.blit(raiz_da_camara(r.w,r.h),(r.x-22,r.y-8))
            return
        s.blit(rocha_lateral(r.w,r.h,t.tipo,t.rect.x),(r.x-4,r.y))
        return
    if t.tipo=="grade":
        grade(s,r)
        if r.w>40:
            pygame.draw.lines(s,(188,186,143),False,[(r.centerx-5,r.top+12),(r.centerx,r.top+16),(r.centerx+5,r.top+12)],2)
        return
    if t.tipo=="porta":
        rng=random.Random(t.rect.x)
        # As raízes de uma comporta descem do dossel e se entrelaçam no chão.
        for n in range(5):
            x=r.left+3+n*max(2,(r.w-6)//4)
            fase=rng.random()*6
            pts=[(x+math.sin(y*.032+fase)*4,y) for y in range(-18,r.bottom+2,9)]
            pygame.draw.lines(s,(53,41,37),False,pts,5)
            pygame.draw.lines(s,(149,115,79),False,pts,1)
        pygame.draw.line(s,(172,141,89),(r.left-2,r.bottom-41),(r.right+3,r.bottom-45),3)
        return
    if t.tipo=="teto":
        # A raiz se apoia na margem de trás. A abertura abaixo permanece legível.
        im=imagem(f"beiral_{i}.png",r.w+12,r.h)
        x,y=r.left,r.bottom
        apoio=rocha_de_fundo(i,r.h)
        s.blit(apoio,(x-apoio.get_width()//2,y-apoio.get_height()+7))
        s.blit(im,(r.left-3,r.top))
        for n in range(3):
            px=r.left+14+n*12
            pygame.draw.aaline(s,(157,148,115),(px,y-3),(px+7,y-4))
        return
    pisos=("chao","galho","bambu","pedra")
    if t.tipo=="chao":
        pygame.draw.rect(s,(24,32,32),r)
        # The same top texture joins continuously over a filled soil cross section.
        passo=157
        start=max(0,(-r.left)//passo)
        for n in range(start,min((r.w+passo-1)//passo,start+8)):
            x=r.left+n*passo
            w=min(passo,r.right-x)
            s.blit(faixa_solo(pisos[i],n%2),(x,r.top),(0,0,w,50))
        for n in range(max(0,(-r.left)//88-1),min((r.w-24)//88+1,max(0,(-r.left)//88)+14)):
            x=r.left+20+n*88+int(math.sin(n*7.1+i)*29)
            if n%4!=2:
                h=12+int(abs(math.sin(n*4.6+i))*19)
                sprite(s,"obj_folha",x,r.top+1,h*2,h,n%2==1)
    else:
        im=imagem("obj_bambu.png",r.w,29)
        s.blit(im,(r.x,r.y-4))
    if t.tipo != "chao" or alto_contraste():
        pygame.draw.line(s,tuple(min(225,v+58) for v in cor),r.topleft,r.topright,2)
    if t.descida and t.tipo!="grade":
        x=r.centerx
        pygame.draw.lines(s,(169,173,139),False,[(x-4,r.top+5),(x,r.top+8),(x+4,r.top+5)],1)


@lru_cache(maxsize=8)
def faixa_solo(tile,espelho):
    im=original("obj_"+tile+".png")
    parte=im.subsurface((im.get_width()//4,im.get_height()//5,
                         im.get_width()//2,im.get_height()*3//5))
    faixa=pygame.transform.smoothscale(parte,(157,50))
    return pygame.transform.flip(faixa,espelho,False)


def rotina(s,nome,x,y,t):
    f=(t*1.18)%1
    if nome in ("Nira","Brasa"):
        pygame.draw.line(s,(190,162,107),(x-20,y-6),(x-27+f*9,y-12),1)
    elif nome in ("Véspera","Coruja"):
        r=4+int(f*10)
        pygame.draw.arc(s,TEAL,(x-24-r,y-29-r,r*2,r*2),2.1,4.1,1)
    elif nome in ("Mimo","Casca","Pingo"):
        pygame.draw.circle(s,(173,183,135),(int(x-21+f*7),int(y-7-math.sin(f*math.pi)*3)),2)
    elif nome=="Fio":
        for n in range(3):
            pygame.draw.aaline(s,PALIDO,(x-17,y-11),(x-38,y-10-n*5+math.sin(t+n)*2))
    else:
        brilho(s,(x+math.sin(t)*7,y-12),14+round(3*math.sin(t*3)))


def mata_reacesa(s,j,cx,t):
    # Nectar attracts three small carriers to each restored section.
    for n in range(15):
        x=(37+n*209+math.sin(t*.8+n)*22)-cx
        if -30<x<990:
            y=421-math.sin(t*1.7+n*4)*17-(n%3)*6
            brilho(s,(x,y),14)
            pygame.draw.circle(s,(195,196,113),(int(x),int(y)),2)
            pygame.draw.aaline(s,TEAL,(x,y-2),(x+4,y-4-math.sin(t*10)*2))



def icone_item(s,item,x,y,w=24,h=24):
    if item in ('globo','semente_luz'):
        centro=(round(x),round(y-h*.5))
        pygame.draw.circle(s,TEAL if item=='globo' else AMBAR,centro,max(3,round(w*.35)),2)
        pygame.draw.circle(s,AMBAR,centro,3)
        return
    if item not in ("tanino","polen"):
        sprite(s,"item_"+item,x,y,w,h)
        return
    rect=pygame.Rect(round(x-w*.35),round(y-h*.85),round(w*.7),round(h*.8))
    cor=(158,105,48) if item=="tanino" else (184,170,82)
    pygame.draw.ellipse(s,cor,rect)
    pygame.draw.line(s,OSSO,(rect.centerx-3,rect.top),(rect.centerx+3,rect.top),3)
    if item=="polen":
        for dx,dy in ((-3,0),(3,3),(0,-4)):
            pygame.draw.circle(s,AMBAR,(rect.centerx+dx,rect.centery+dy),2)
    else:
        pygame.draw.lines(s,AMBAR,False,[(rect.centerx-3,rect.top+5),(rect.centerx+3,rect.centery),(rect.centerx-2,rect.bottom-2)],2)


def objeto(s,o,j,cx,tempo):
    x=o.x-cx
    if not -105<x<1065: return
    if (abertura_bosque.ativa(j) and o.x < abertura_bosque.FIM_TRILHA
            and arte_ilustrada.objeto(s,o,j,x,tempo)):
        if o.tipo == "npc" and abs(o.x-j.lume.rect.centerx)<140:
            altura = arte_ilustrada.PERSONAGENS[o.nome][1]
            texto(s,o.nome,x,o.y-altura-17,14,OSSO,"forte","centerx")
        return
    if o.tipo=='lanterna':
        from .encontros import desenhar
        desenhar(s,o,j,cx);return
    if o.tipo=='sobrevivente':
        from .arte_resgates import pessoa
        pessoa(s,o,j,cx,tempo)
        return
    if o.tipo=="corda_borda":
        from .rotas_borda import desenhar_corda
        desenhar_corda(s,o,cx)
        return
    if o.tipo=='raizes':
        from .arte_raizes import objeto as desenhar_raiz
        desenhar_raiz(s,o,j,cx,tempo)
        return
    if o.tipo=="galeria_sementes":
        from .arte_galeria import objeto as objeto_galeria
        objeto_galeria(s,o,j,cx)
        return
    if o.tipo == "reserva_fagulha":
        desvio = desvios_fagulha.local(j)
        icone_item(s,desvio.item,x,o.y,25,26)
        return
    if o.tipo=='marco':
        sprite(s,"obj_marco",x,o.y,38,57)
        brilho(s,(x+8,o.y-30),18)
        return
    if o.tipo=="encomenda":
        y=o.y
        pygame.draw.polygon(s,(94,119,67),[(x-16,y-2),(x-18,y-21),(x,y-29),(x+18,y-21),(x+14,y-2)])
        pygame.draw.line(s,(206,184,119),(x-17,y-18),(x+16,y-8),2)
        pygame.draw.line(s,(206,184,119),(x+16,y-22),(x-14,y-6),2)
        brilho(s,(x,y-12),13)
        return
    if o.tipo=="pavio_nicho":
        brilho(s,(x,o.y-11),17)
        icone_item(s,"pavio",x,o.y,27,24)
        return
    if o.tipo=="fenda":
        arte_bosque.passagem(s,x,o.y)
        return
    if o.tipo=="pista":
        y=o.y
        pygame.draw.line(s,(96,76,49),(x,y),(x,y-44),4)
        pygame.draw.polygon(s,(72,62,42),[(x-24,y-56),(x+24,y-54),(x+21,y-31),(x-23,y-33)])
        pygame.draw.circle(s,(177,154,104),(round(x-10),y-44),7,2)
        pygame.draw.lines(s,AMBAR,False,[(x+1,y-48),(x+8,y-48),(x+8,y-40),(x+13,y-40),(x+13,y-45)],2)
        pygame.draw.lines(s,PALIDO,False,[(x+17,y-38),(x+21,y-41),(x+17,y-44)],1)
        return
    if o.tipo=="reliquia":
        y=o.y-17+round(math.sin(tempo*2)*2)
        brilho(s,(x,y),25)
        if "asa" in o.id:
            for lado in (-1,1):
                pts=[(x,y+7),(x+lado*23,y-8),(x+lado*17,y-19),(x+lado*5,y-8)]
                pygame.draw.polygon(s,(158,188,151),pts)
                pygame.draw.lines(s,(232,221,168),False,[pts[0],pts[2]],1)
        elif "resina" in o.id:
            pygame.draw.polygon(s,(163,103,39),[(x,y-23),(x-11,y+3),(x-5,y+12),(x+8,y+10),(x+12,y+1)])
            pygame.draw.lines(s,AMBAR,False,[(x-3,y-7),(x-6,y+3),(x-2,y+7)],2)
        else:
            pygame.draw.polygon(s,(124,149,112),[(x-17,y+11),(x+13,y-21),(x+6,y+8)])
            pygame.draw.line(s,OSSO,(x-11,y+8),(x+12,y-19),1)
        return
    if o.tipo=="npc":
        w,h=NPC_TAM[o.nome]
        ond=math.sin(tempo*2+o.x)*1.6
        if o.nome in ("Eco","Pingo","Candeia"): ond-=4
        sprite(s,arte_npc(o.nome),x,o.y+ond,w,h+round(ond/2))
        rotina(s,o.nome,x,o.y+ond,tempo)
        if abs(o.x-j.lume.rect.centerx)<135:
            texto(s,o.nome,x,o.y-h-24,14,OSSO,"forte","centerx")
        return
    if o.tipo in ("saida","voltar"):
        arte_bosque.marco_de_trilha(s, x, o.y, o.tipo == "voltar")
        return
    arte,w,h=OBJETOS[o.tipo]
    if o.tipo=="valvula":
        manivela(s,x,o.y,w,h,j.manivela_girada(o))
        return
    if o.id == "corda":
        arte_ilustrada.cipo(s,x,o.y,tempo)
        return
    if o.tipo=="corda":
        pygame.draw.line(s,(162,134,91),(x,216),(x,o.y-65),3)
        for y in range(219,o.y-64,9): pygame.draw.line(s,(92,75,56),(x-2,y),(x+2,y+3))
    y=o.y
    if o.id=="lingueta":
        w,h=30,14
        if j.visivel((o.x,o.y-8)):
            brilho(s,(x,y-8),18)
            pygame.draw.line(s,AMBAR,(x-6,y-9),(x+5,y-12),2)
    if o.tipo=="reserva":
        especie=("casulo","balsamo","pavio","casulo")[j.etapa]
        brilho(s,(x,y-12),22)
        sprite(s,"item_"+especie,x,y,32,27)
        return
    if o.tipo=="orvalho":
        y+=h//2+round(3*math.sin(tempo*3+o.x))
        brilho(s,(x,y-h//2),25)
    if o.tipo=="raiz" and "raiz" in j.flags or o.tipo=="no" and o.id in j.flags:
        brilho(s,(x,y-25),85)
        for n in range(6):
            pygame.draw.circle(s,(199,209,148),(int(x+math.sin(tempo+n)*44),int(y-16-((tempo*15+n*13)%55))),2)
    sprite(s,"obj_"+arte,x,y,w,h)


def lume(s,l,cx,t,fagulha=None):
    pos=l.pose
    w=58 if pos!="deslize" else 68
    h={"agachar":22,"deslize":19,"pulo":43,"queda":41,"corda":43,"golpe":34}.get(pos,38)
    x=l.rect.centerx-cx
    y=l.rect.bottom
    brilho(s,(x-12*l.face,y-h*.44),55)
    golpe_lume(s,l,cx)
    if l.iframes<=0 or int(t*14)%3!=1:
        desenhar_lume(s, l, x, y+1, (w,h), t, fagulha)
    if l.batida_asa>0:
        # Dois rastros curtos marcam o impulso extra sem iluminar a tela inteira.
        abertura=1-l.batida_asa/.18
        for lado in (-1,1):
            pontos=[(x+lado*7,y-18),(x+lado*(16+10*abertura),y-25+12*abertura),
                    (x+lado*(23+15*abertura),y-20+23*abertura)]
            pygame.draw.lines(s,AMBAR,False,pontos,2)
    if l.slide>0:
        for n in range(4):
            pygame.draw.line(s,AMBAR,(x-l.face*(17+n*8),y-4-n),(x-l.face*(24+n*9),y-4-n),1)


class Paisagem:
    def __init__(self):
        # Decodificar os fundos no início evita o pico de leitura quando
        # Lume já está se movendo e uma região aparece pela primeira vez.
        for i in range(4):fundo(i)
        self.luz=pygame.Surface((960,540))
        self.brilho_mata=1
        self.particulas=[]
        self.ultimo_tempo=None
        self.ultimo_jogo=None
        self.lampejos=()
        self.mundo=pygame.Surface((960,620))

    def ecos(self,s,j,cx):
        # Datas pertencem ao relógio da partida; abrir o diário congela as partículas.
        if j is not self.ultimo_jogo or (self.ultimo_tempo is not None and j.tempo<self.ultimo_tempo):
            self.particulas.clear()
            self.ultimo_tempo=None
            self.ultimo_jogo=j
            self.lampejos=()
        if self.ultimo_tempo!=j.tempo:
            self.ultimo_tempo=j.tempo
            if "resposta_eco" in j.eventos:
                self.lampejos=(j.tempo, 1124, 329)
            paleta={"coleta":AMBAR,"raiz":(160,225,160),"acerto":(229,206,160),
                    "dano":PERIGO,"pouso":(124,147,131),"porta":(194,170,123),
                    "freio_luz":(249,201,117)}
            for ev in set(j.eventos)&paleta.keys():
                quantidade=5 if ev=="pouso" else 13
                for n in range(quantidade):
                    a=n*2.4
                    vel=20+(n*17)%53
                    self.particulas.append((j.tempo,j.lume.rect.centerx,j.lume.rect.bottom-12,
                                            math.cos(a)*vel,-15-abs(math.sin(a))*vel,paleta[ev]))
        if self.lampejos:
            data,x,y=self.lampejos
            idade=j.tempo-data
            for t0 in (.23, .85):
                if t0 <= idade < t0+.33:
                    intensidade=math.sin((idade-t0)/.33*math.pi)
                    brilho(s,(x-cx,y),round(19+40*intensidade))
                    losango(s,round(x-cx),y,round(1+4*intensidade),(218,229,147))
            if idade>1.4:
                self.lampejos=()
        self.particulas=[p for p in self.particulas if 0<=j.tempo-p[0]<.62]
        for inicio,x,y,vx,vy,cor in self.particulas:
            d=j.tempo-inicio
            px,py=x-cx+vx*d,y+vy*d+73*d*d
            pygame.draw.line(s,cor,(round(px),round(py)),(round(px-vx*.025),round(py-vy*.025)),2)

    def desenhar(self,s,j,t):
        if j.em_vertical:
            from .corte_vertical import desenhar_vertical
            desenhar_vertical(s,j,t,self.brilho_mata)
            return
        destino=s
        altura=max(620,getattr(j,"altura_mundo",540)+80)
        if self.mundo.get_height()!=altura:
            self.mundo=pygame.Surface((960,altura))
        s=self.mundo
        cy=round(j.camera_y)
        recorte=pygame.Rect(0,cy,960,540)
        s.set_clip(recorte)
        i,cx=j.etapa,j.camera
        intensidade = abertura_bosque.intensidade(j)
        limite_arte = abertura_bosque.FIM_TRILHA if abertura_bosque.ativa(j) else 0
        s.blit(fundo(i),(-int(cx/max(1,j.fase.width-960)*310),cy-108))
        abertura_bosque.fundo(s,j,cx,cy)
        if cy>60:
            # As raízes cobrem progressivamente o céu ao descer, no mesmo mundo.
            sub=raizes_subsolo()
            alfa=min(255,round((cy-60)*1.1))
            sub.set_alpha(None if alfa==255 else alfa)
            s.blit(sub,(0,cy),pygame.Rect(int(cx*.12)%320,0,960,540))
        for n in range(28):
            x=(n*97-cx*.31+math.sin(n+t*.31)*10)%980-10
            y=cy+70+(n*47+t*(2+n%3))%365
            pygame.draw.circle(s,(146,163,142),(int(x),int(y)),1)
        if i==1:
            nivel=423 if "dreno" in j.flags else 353
            left,right=round(802-cx),round(1349-cx)
            water=placa(547,442-nivel,130).copy()
            water.fill((52,110,117,110))
            s.blit(water,(left,nivel))
            for n in range(4):
                y=nivel+n*10
                pygame.draw.lines(s,(108,154,145),False,[(left+k,y+math.sin(k*.07+t*2)*2) for k in range(0,right-left+1,10)],1)
        fundo_visao=capturar_fundo(s,cy)
        if intensidade:
            arte_ilustrada.sombrear_terreno_fixo(fundo_visao,j,cx,cy,limite_arte,intensidade)
        from . import raizes_bosque
        if raizes_bosque.ativo(j):
            from .arte_raizes import detalhes
            detalhes(s,j,cx)
        if i==1 and not hasattr(j,"sala_id"):
            # O sulco liga a peça desenhada no aviso à boca real do túnel.
            for n in range(18):
                px=807+n*10-cx;py=436+(n%3)-1
                pygame.draw.line(s,(130,137,116),(px,py),(px+6,py-2),1)
            for px in (829,844,1066):
                pygame.draw.lines(s,(120,147,119),False,[(px-cx,440),(px+5-cx,436),(px+9-cx,438)],2)
        if hasattr(j,"sala_id"): sustentar_galho_do_duelo(s,j,cx)
        primeiro = FASES[0].plataformas[0] if i==0 and not hasattr(j,"sala_id") else None
        for tr in j.solidos:
            r = tr.rect
            apoio_inicial = (r.x,r.y,r.w) == primeiro and tr.tipo == "plataforma"
            if tr is abertura_bosque.BROTO or (limite_arte and arte_ilustrada.terreno_fixo(tr, limite_arte)):
                arte_ilustrada.terreno(s,tr,cx)
            elif apoio_inicial:
                arte_bosque.galho(s,r.move(-round(cx),0),i,False,raiz=True)
            else:
                terreno(s,tr,cx,i)
        from .rotas_borda import desenhar as desenhar_passarelas
        desenhar_passarelas(s,j,cx)
        if i == 1:
            from .corrego_historia import desenhar as marcas_do_corrego
            marcas_do_corrego(s,j,cx)
        elif i == 2:
            from .vento_taquaral import desenhar as sementes_ao_vento
            from .arte_galeria import detalhes as detalhes_galeria
            sementes_ao_vento(s,cx,t)
            detalhes_galeria(s,j,cx)
        elif i == 3:
            from .aula_sino import desenhar as sinal_do_sino
            sinal_do_sino(s,j,cx)
        from .sinalizacao import desenhar as descidas
        descidas(s,j,cx)
        if limite_arte:
            arte_ilustrada.vegetacao(s,cx)
        desvios_fagulha.marca(s,j,cx)
        for o in j.objetos:
            if not (abertura_bosque.em_cena(j) and o.tipo == "refugio" and o.x < 100):
                objeto(s,o,j,cx,t)
        if "raiz" in j.flags or "no" in j.flags: mata_reacesa(s,j,cx,t)
        reforcos = j.boss.ninhada.vivos if j.boss and j.boss.ninhada is not None else ()
        criaturas = (*j.inimigos, *reforcos) if reforcos else j.inimigos
        for e in criaturas:
            if j.visivel(e.rect.center,18):
                inimigo(s,e,cx,j.lume,t)
        if j.boss:
            j.boss.desenhar(s,cx)
        # O primeiro plano também faz parte da mata e recebe a mesma sombra.
        if cy<180 and intensidade<1:
            desloc = int(cx*1.16)%1200
            faixas = (recorte,)
            if i == 3:
                from .aula_sino import TRECHO
                esquerda, direita = (round(x-cx) for x in TRECHO)
                faixas = (recorte.clip(pygame.Rect(0,cy,max(0,esquerda),540)),
                          recorte.clip(pygame.Rect(max(0,direita),cy,960,540)))
            for faixa in faixas:
                if faixa.width:
                    s.set_clip(faixa)
                    margem = margens(i)
                    margem.set_alpha(round(255*(1.-intensidade)))
                    for x in (-desloc,1200-desloc):
                        s.blit(margem,(x,414))
            s.set_clip(recorte)
        if i == 1:
            from .corrego_historia import desenhar_agua
            desenhar_agua(s,j,cx)
        from .arte_resgates import luzes
        luzes(s,j,cx,t)
        from .luzes_mundo import desenhar as globos
        globos(s,j,cx)
        nivel=min(3,self.brilho_mata+int(j.concluida))
        arte_fagulha.iluminar_cenario(s,j,cx)
        compor_luz(self.luz,j,cx,cy,nivel)
        cor = abertura_bosque.cor_distante(j,nivel,TINTAS_NEVOA[nivel]) if abertura_bosque.ativa(j) else None
        if intensidade:
            # O fundo frio permanece escuro. Um mínimo de luz revela as silhuetas desenhadas.
            escuro = round((38,52,70,87)[nivel]*intensidade)
            self.luz.fill((escuro,escuro,escuro),special_flags=pygame.BLEND_RGB_MAX)
        aplicar_nevoa(s,self.luz,cy,fundo_visao,nivel,cor,intensidade)
        if limite_arte and cx < limite_arte:
            arte_ilustrada.iluminar_pousos(s,j,cx,nivel,limite_arte)
        if primeiro is not None and abertura_bosque.em_cena(j) and "valvula" not in j.flags:
            x, y, largura = primeiro
            if j.lume.rect.centerx <= x+largura and y-105 <= j.lume.rect.bottom <= y+80:
                x -= round(cx)
                if recorte.collidepoint(x+16,y) and self.luz.get_at((x+16,y-cy)).r < 80:
                    arte_bosque.liquen(s,x,y)
        if abertura_bosque.broto_aceso(j):
            # O bordo bioluminescente continua perceptível fora do halo.
            r = abertura_bosque.BROTO.rect.move(-round(cx), 0)
            for dx, dy in ((11, -3), (28, 0), (46, -4), (58, 0)):
                pygame.draw.circle(s, AMBAR, (r.x+dx, r.y+dy), 1)
        from .ilustracao import claroes_suaves
        for v in j.vestigios:
            if v.raio(j.tempo)>16:
                xy=(round(v.x-cx),round(v.y))
                idade = j.tempo-v.inicio
                if idade<.32 and not claroes_suaves() and not abertura_bosque.em_cena(j):
                    r=max(5,v.raio(j.tempo))
                    area=pygame.Rect(xy[0]-r,xy[1]-r,r*2,r*2)
                    cor=(163,144,107)
                    pygame.draw.arc(s,cor,area,.14,1.54)
                    pygame.draw.arc(s,cor,area,3.68,5.11)
                if not claroes_suaves():
                    brilho(s,xy,min(27,v.raio(j.tempo)//2))
                losango(s,*xy,3,AMBAR,False)
        arte_fagulha.desenhar(s,j,cx)
        for e in criaturas:
            projeteis(s,e,cx,j.lume,j.raio,j.visivel)
        if j.boss: sinais_encontro(s,j.boss,cx,prevista=travessia_fagulha.prever_marca(j))
        lume(s,j.lume,cx,t,j.fagulha_ativa)
        if limite_arte:
            abertura_bosque.desenhar_impacto(s,j,cx)
        licao_vespera.desenhar(s,j,cx)
        self.ecos(s,j,cx)
        abertura_bosque.primeiro_plano(s,j,cx,cy)
        destino.blit(s,(0,0),recorte)
        s.set_clip(None)


def avisar_custo_clarao(s,j,y):
    custo = j.lume.custo_em_vida(j.lume.custo_clarao)
    if custo > 0:
        valor = f'{custo:.2f}'.rstrip('0').rstrip('.').replace('.', ',')
        prefixo = 'K fatal · custa' if custo >= j.lume.vida else 'K custa'
        painel(s,(20,y,223,22),False)
        texto(s,dica_teclado(f'{prefixo} {valor} de vida'),29,y+2,12,PERIGO,'forte')


def hud(s,j):
    if abertura_bosque.em_cena(j) and not j.boss:
        abertura_bosque.hud(s,j)
        if not j.dialogo:
            avisar_custo_clarao(s,j,109)
        return
    from .cartografia import rastro_objetivo, texto_curto
    from .avisos import ocupa_esquerda
    livre=not ocupa_esquerda(j)
    rastro_objetivo(s,j)
    reservas(s,j)
    duelo=hasattr(j,"sala_id")
    if duelo:
        texto(s,f"Avisos {j.inimigos[0].sequencia}",193,105,12,PALIDO,"normal","right")
    avisar_custo_clarao(s,j,155)
    if j.lume.abate_ate>j.tempo and livre:
        hp,br=j.lume.ganho_abate
        texto(s,f'Abate +{hp:g} vida / +{br:g} brilho',22,175,12,TEAL,'forte')
    if j.lume.combo_acertos and livre:
        mult=min(8.,1.25**min(10,j.lume.combo_acertos//3))
        texto(s,f'Sequência {j.lume.combo_acertos} · retorno {mult:.2f}×',22,210,11,TEAL,'forte')
    painel(s,(682,18,259,64))
    if duelo: local=f"ENSAIO    •    SEMENTE {j.semente}"
    else: local="TRAVESSIA   "+ROMANOS[j.etapa]
    texto(s,local,925,24,12,AMBAR,"forte","right")
    from .raizes_bosque import setor
    from .galeria_taquaral import TITULO as GALERIA, dentro
    from . import nicho_taquaral as nicho
    nome = (nicho.TITULO if nicho.dentro(j) else GALERIA) if dentro(j) else setor(j) or j.fase.name
    regiao=j.setor_vertical if j.em_vertical else nome
    tam=20 if fonte(tamanho_texto(20),"titulo").size(regiao)[0]<=237 else 18
    texto(s,texto_curto(regiao,237,tam,"titulo"),925,44,tam,OSSO,"titulo","right")
    texto(s,dica_teclado('M · mapa'),925,68,10,PALIDO,'normal','right')
    if not duelo:
        item=j.bolsa.item
        qtd="ferramenta" if item.permanente and j.bolsa.quantidade else str(j.bolsa.quantidade)
        if item.id=='balsamo':qtd=f'{j.bolsa.quantidade}/{j.bolsa.capacidade_balsamo}'
        painel(s,(19,122,213,32),False)
        icone_item(s,item.id,38,151,24,24)
        reserva=fonte(tamanho_texto(12),"forte").size(qtd)[0]+8
        texto(s,texto_curto(item.nome,160-reserva,13,"forte"),57,124,13,PALIDO,"forte")
        texto(s,qtd,220,124,12,OSSO,"forte","right")
        texto(s,dica_teclado("Q  trocar   F  usar"),57,140,11,PALIDO)
        efeitos = j.bolsa.efeitos_ativos(j.tempo)
        if efeitos and livre:
            texto(s," · ".join(efeitos),22,192,11,AMBAR,"forte")
    if getattr(j, 'ensaio_armas', False) and livre:
        nome = 'Agulha · alcance longo' if j.lume.arma.equipamento=='agulha' else 'Espinho · cortes rápidos'
        painel(s,(19,214,236,44),False)
        texto(s,nome,30,219,14,AMBAR,'forte')
        texto(s,dica_teclado('V trocar arma · E no abrigo recupera reservas'),30,239,10,PALIDO)
    elif getattr(j, 'ensaio_troca_arma', False) and livre:
        nome = 'Agulha · alcance longo' if j.lume.arma.equipamento=='agulha' else 'Espinho · corte rápido'
        texto(s,dica_teclado(f"{nome} · V troca"),22,227,11,PALIDO,"forte")

    if j.boss and not j.boss.vencido:
        chamado = j.boss.estado.startswith('coro_')
        segundo_aviso = j.boss.indice == 1 and j.boss.estado == "aviso"
        painel(s,(258,17,402,101 if segundo_aviso else 79))
        fase=getattr(j.boss,'fase',1)
        nome=j.boss.nome + (' · '+('II' if fase==2 else 'III') if fase>1 else '')
        texto(s,nome,459,22,23,OSSO,"titulo","centerx")
        if chamado:
            for n in range(3):losango(s,421+n*38,60,6,AMBAR,n<j.boss.coro_sinais)
            texto(s,j.boss.dica,459,73,12,PALIDO,'normal','centerx')
        else:
            pygame.draw.rect(s,(53,55,52),(279,62,360,6))
            pygame.draw.rect(s,AMBAR,(279,62,round(360*j.boss.vida/j.boss.vida_max),6))
            estado = j.boss.estado
            aviso = estado in ('aviso','investida','rastro','investida_seiva')
            explicacao = j.boss.pista_fagulha if estado == "busca" else j.boss.dica
            dica = texto_curto(dica_teclado(explicacao),376,12,'forte')
            texto(s,dica,459,73,12,PERIGO if aviso else AMBAR,'forte','centerx')
            if segundo_aviso:
                texto(s,dica_teclado(j.boss.pista_fagulha),459,94,12,AMBAR,'forte','centerx')
    from .avisos import desenhar
    desenhar(s,j)
