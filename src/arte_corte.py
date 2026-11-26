"""Desenho do corte em coordenadas do mundo e mapa local de descoberta."""
from functools import lru_cache
import math

from . import pygame_hd as pygame
from .arte_espinho import desenhar_impactos
from .arte_combate import inimigo, projeteis
from . import arquivo_casca, arte_fio, corte_vertical as corte, fio_corte
from .ilustracao import AMBAR, OSSO, PALIDO, TEAL, brilho, imagem, losango, manivela, original, sprite, texto


@lru_cache(maxsize=1)
def camadas():
    fundo=pygame.transform.smoothscale(original("corte_da_figueira.jpg"), (1144,1670))
    fundo.fill((186,198,199),special_flags=pygame.BLEND_RGB_MULT)
    return fundo,pygame.Surface((960,corte.ALTURA+80)),pygame.Surface((960,540))


LADO_SETOR = 384


@lru_cache(maxsize=16)
def suporte_do_setor(sx, sy):
    """Só a área pintada de cada setor das escoras fica residente em Full HD."""
    tamanho = min(LADO_SETOR, 2432-sx), min(LADO_SETOR, corte.ALTURA-sy)
    out = pygame.Surface(tamanho, pygame.SRCALPHA)

    def pontos(coords):
        return [(x-sx, y-sy) for x,y in coords]

    def linha(cor, a, b, largura):
        pygame.draw.line(out, cor, *pontos((a,b)), largura)

    def linhas(cor, coords, largura):
        pygame.draw.lines(out, cor, False, pontos(coords), largura)

    for centro,ramo in ((370,1),(1224,-1)):
        curva=[(centro+round(math.sin(y*.004)*36),y) for y in range(215,1080,16)]
        margem=[(x-5-int(y*.009),y) for x,y in curva]
        outra=[(x+6+int(y*.008),y) for x,y in curva]
        pygame.draw.polygon(out,(37,46,40,220),pontos(margem+list(reversed(outra))))
        linhas((83,91,73,210),margem,2)
        for tr in corte.terrenos():
            if tr.tipo!="plataforma" or tr.rect.left>=corte.BOCA_LESTE or not 338 < tr.rect.top < 970: continue
            if (tr.rect.centerx<800) != (ramo==1): continue
            h=tr.rect.top
            x=centro+round(math.sin((h+58)*.004)*36)
            destino=tr.rect.centerx
            base=[(x,h+57),(x+ramo*19,h+48),(destino-ramo*33,h+24),(destino,h+9)]
            linhas((52,60,49,235),base,8)
            linhas((98,101,77,230),base,1)
    # A régua de cheia pertence ao poço; marcas e água reaparecem sob o jogador.
    for n in range(10):
        yy=1485-n*9
        linha((127,143,119,220),(814,yy),(814+(10 if n%3==0 else 5),yy-1),2)
    linha((103,114,94,210),(812,1490),(812,1392),3)
    # A oficina e os berços compartilham a mesma armação. As cordas chegam
    # aos apoios reais, assim a descida ainda é legível quando o brilho fecha.
    for x in (1780,2318):
        linhas((51,60,48),[(x-38,1818),(x+4,1428),(x-8,1030),(x,728)],15)
        linha((102,109,81),(x-5,778),(x-29,1792),2)
    linhas((123,111,77),[(1515,970),(1780,723),(2070,741),(2320,708)],5)
    for tr in corte.terrenos():
        if tr.tipo!="plataforma" or tr.rect.left<1590: continue
        x,y=tr.rect.centerx,tr.rect.top
        poste=1780 if x<1970 else 2318
        linha((109,103,79),(poste,y-86),(x,y+4),2)
        linhas((75,85,66),[(x-42,y+5),(x-20,y+25),(x+28,y+21),(x+50,y+5)],4)
        if y>1090:
            # Borda de uma folha dobrada que já serviu de berço.
            pygame.draw.arc(out,(150,147,105),(x-sx-32,y-sy-13,66,21),3.14,6.28,2)
    for x in (1510,1695,1888,2093,2302):
        for y in (1789,1795,1803):
            linha((77,117,115),(x-30,y),(x+53,y-2),1)
    pintado = out.get_bounding_rect()
    if pintado.width:
        return out.subsurface(pintado).copy(), pintado.move(sx, sy)
    return None


def desenhar_suportes(camada, cx, cy):
    visivel = pygame.Rect(cx,cy,960,540).clip(pygame.Rect(0,0,2432,corte.ALTURA))
    for x in range(visivel.left//LADO_SETOR*LADO_SETOR, visivel.right, LADO_SETOR):
        for y in range(visivel.top//LADO_SETOR*LADO_SETOR, visivel.bottom, LADO_SETOR):
            setor = suporte_do_setor(x, y)
            if setor:
                arte, lugar = setor
                camada.blit(arte, (lugar.x-cx, lugar.y))


@lru_cache(maxsize=2)
def janela_arquivo(fechada):
    janela=pygame.Surface((171,111),pygame.SRCALPHA)
    if not fechada:
        pygame.draw.polygon(janela,(224,209,141,70),[(26,24),(44,15),(151,91),(100,103)])
        pygame.draw.line(janela,(243,218,146,90),(41,22),(137,89),2)
    moldura=pygame.Rect(17,13,35,33)
    pygame.draw.rect(janela,(70,52,35),moldura,border_radius=5)
    pygame.draw.rect(janela,(139,114,70),moldura,3,border_radius=5)
    for y in (21,28,35):
        cor=(100,81,52) if fechada else (206,180,118)
        pygame.draw.line(janela,cor,(22,y),(47,y+2),4)
    return janela


def casulo_mola(camada, j, cx):
    x = corte.CASULO.centerx-cx
    y = corte.CASULO.bottom
    pressao = max(0., min(1., (j.lume.arma.rebote-.30)/.16)) if abs(j.lume.rect.centerx-corte.CASULO_X) < 66 else 0.
    topo = y-28+round(9*pressao)
    ramo = [(x-22,corte.NICHO_POCO+12),(x-34,1345),(x-28,1428),(x-17,y-11)]
    pygame.draw.lines(camada, (110, 124, 91), False, ramo, 2)
    pygame.draw.lines(camada, (101, 96, 67), False, [(x-26,y),(x-16,y-8),(x+16,y-8),(x+26,y)], 3)
    pygame.draw.ellipse(camada, (92, 118, 95), (x-20,topo,40,y-topo-1))
    pygame.draw.ellipse(camada, (156, 192, 148), (x-20,topo,40,y-topo-1), 2)
    for faixa in (7, 14):
        yy = min(y-4, topo+faixa)
        pygame.draw.arc(camada, (220, 197, 127), (x-18,yy-4,36,9), math.pi, math.tau, 2)
    pygame.draw.lines(camada, PALIDO, False, [(x-8,topo-7),(x,topo-13),(x+8,topo-7)], 2)


@lru_cache(maxsize=1)
def folha_comporta():
    """Lâmina de casca em coordenadas locais, recortada pelo trilho."""
    w, h = corte.COMPORTA.size
    folha = pygame.Surface((w, h))
    folha.fill((48, 49, 37))
    for n, x in enumerate(range(4, w-3, 7)):
        veta = [(x+round(2*math.sin(y*.085+n)), y) for y in range(0, h+1, 8)]
        pygame.draw.lines(folha, (76+4*(n%3), 69+3*(n%3), 47), False, veta, 6)
        pygame.draw.lines(folha, (117, 103, 67), False, veta, 1)
    for y in (39, 99, h-15):
        pygame.draw.rect(folha, (57, 70, 60), (1, y, w-2, 10), border_radius=2)
        pygame.draw.line(folha, (142, 124, 76), (2, y+1), (w-3, y+1), 2)
        for x in (6, w-7):
            pygame.draw.circle(folha, (157, 143, 93), (x, y+5), 2)
    pygame.draw.line(folha, (188, 159, 99), (1, h-1), (w-2, h-1), 2)
    return folha


def desenhar_comporta(camada, j, cx, roda, t):
    moldura = corte.COMPORTA.move(-cx, 0)
    painel = corte.painel_comporta(j).move(-cx, 0)
    fundo = moldura.bottom
    cabo = ((moldura.centerx, moldura.top-12), (moldura.right+35, moldura.top+20),
            (roda.x-cx, roda.y-32))
    pygame.draw.lines(camada, (47, 53, 43), False, cabo, 4)
    pygame.draw.lines(camada, (131, 117, 75), False, cabo, 1)
    pygame.draw.circle(camada, (147, 124, 73), cabo[0], 8, 2)

    if painel.h:
        folha = folha_comporta()
        camada.blit(folha, painel.topleft,
                    pygame.Rect(0, moldura.h-painel.h, moldura.w, painel.h))
    vao = fundo-painel.bottom
    if vao >= 5:
        largura = moldura.w+40+round(vao*.56)
        inicio = moldura.centerx-largura//2
        for n in range(12):
            x = inicio+largura-(round(t*74)+n*23)%largura
            y = fundo-2-min(vao-2, 3+(n*7)%20)
            pygame.draw.aaline(camada, (72+8*(n%3), 125+8*(n%3), 121+5*(n%3)),
                             (x-15, y), (x+3, y-1))
        if j.comporta_inicio is not None:
            for n in range(5):
                fase = (t*3+n*.21)%1.
                x = moldura.left-round(5+fase*31)
                pygame.draw.circle(camada, (148, 196, 177), (x, fundo-4-round(40*fase*(1.-fase))), 2)

    for x in (moldura.left-2, moldura.right+1):
        pygame.draw.line(camada, (50, 57, 49), (x, moldura.top-4), (x, fundo-2), 5)
        pygame.draw.line(camada, (139, 122, 79), (x, moldura.top), (x, fundo-1), 1)
        for y in (moldura.top+9, fundo-24):
            pygame.draw.circle(camada, (167, 146, 97), (x, y), 2)
        if vao >= 5:
            pygame.draw.lines(camada, (115, 159, 139), False,
                              [(x+2, fundo-33),(x-1, fundo-21),(x+1, fundo-12),(x, fundo-2)], 2)


def desenhar_ponto(camada,o,j,cx):
    x=o.x-cx
    if o.tipo in ("fio_corte", "carretel_fio"):
        arte_fio.objeto(camada, o, j, cx, j.tempo)
        return
    if o.tipo == "pavio_nicho":
        brilho(camada, (x, o.y-12), 15)
        sprite(camada, "item_pavio", x, o.y-2, 31, 25)
        return
    if o.tipo=='lanterna':
        from .encontros import desenhar
        desenhar(camada,o,j,cx);return
    if o.tipo=='sobrevivente':
        from .arte_resgates import pessoa
        pessoa(camada,o,j,cx,j.tempo)
        return
    if o.tipo=='veneziana':
        y=o.y-28
        pygame.draw.line(camada,(94,77,55),(x,o.y),(x,y),3)
        pygame.draw.circle(camada,(170,140,83),(x,y),6,2)
        return
    if o.tipo=='sinal_arquivo':
        y=arquivo_casca.SINAIS[1]
        pygame.draw.rect(camada,(45,58,42),(x-23,y-7,46,14),border_radius=4)
        for inicio,comprimento in ((-18,6),(-6,6),(6,15)):
            pygame.draw.line(camada,(186,237,183),(x+inicio,y),(x+inicio+comprimento,y),3)
        return
    if o.tipo=='atalho_raiz':
        cor=(149,169,108) if corte.RAIZ_DUAS_BOCAS in j.cartografia else (162,122,77)
        if o.id=='raiz_boca_alta':
            pygame.draw.lines(camada,cor,False,[(x-19,o.y-25),(x-13,o.y-14),(x,o.y-6),
                                               (x+13,o.y-14),(x+19,o.y-25)],3)
        else:
            pygame.draw.lines(camada,cor,False,[(x-13,o.y-29),(x-8,o.y-36),(x+8,o.y-36),
                                               (x+13,o.y-29)],2)
            if corte.RAIZ_DUAS_BOCAS not in j.cartografia:
                pygame.draw.rect(camada,cor,(x-11,o.y-34,22,24),3,border_radius=5)
                losango(camada,x,o.y-22,6,AMBAR)
        return
    if o.tipo in ('jardim','orvalho_jardim'):
        from .arte_jardim import objeto
        objeto(camada,o,j,cx)
        return
    if o.tipo=="passagem":
        from .arte_bosque import passagem
        passagem(camada,x,o.y,False)
        return
    if o.tipo=="reliquia":
        from .paisagem import objeto
        objeto(camada,o,j,cx,j.tempo)
        return
    if o.tipo=="elevador":
        if "ralo_aberto" in j.cartografia:
            pygame.draw.lines(camada,(157,129,80),False,[(x-25,o.y),(x-17,o.y+8),(x+20,o.y+8),(x+27,o.y)],4)
            pygame.draw.line(camada,(196,172,117),(x-25,o.y),(x+27,o.y),3)
            pygame.draw.line(camada,(151,129,86),(x,o.y-20),(x,o.y),3)
            losango(camada,x,o.y-11,6,AMBAR,False)
        return
    if o.tipo=="valvula":
        if o.id == "comporta_viveiro":
            sprite(camada, "obj_valvula", x, o.y, 46, 53)
            eixo = round(x), o.y-32
            angulo = -2.5 + math.pi*corte.abertura_comporta(j)
            pino = eixo[0]+round(17*math.cos(angulo)), eixo[1]+round(17*math.sin(angulo))
            pygame.draw.line(camada, (38, 44, 38), eixo, pino, 5)
            pygame.draw.line(camada, AMBAR, eixo, pino, 2)
            pygame.draw.circle(camada, OSSO, pino, 3)
            return
        manivela(camada,x,o.y,46,53,j.manivela_girada(o))
        return
    if o.id == "placa_viveiro":
        arte_fio.berco(camada, o, cx)
    item={"refugio":"refugio", "registro":"registro"}[o.tipo]
    w,h={"refugio":(72,61),"registro":(32,25)}[o.tipo]
    sprite(camada,"obj_"+item,x,o.y,w,h)


def desenhar(s,j,t,nivel_brilho):
    s = pygame.destino(s)
    from . import arte_fagulha
    from .paisagem import lume, terreno, aplicar_nevoa, compor_luz, capturar_fundo
    from .ilustracao import claroes_suaves
    bg, camada, luz=camadas()
    cx,cy=round(j.camera),round(j.camera_y)
    tela=pygame.Rect(0,cy,960,540)
    camada.set_clip(tela)
    recorte=pygame.Rect(round(cx*(bg.get_width()-960)/(corte.LARGURA-960)),
                         round(cy*(bg.get_height()-540)/(corte.ALTURA-540)),960,540)
    camada.blit(bg,(0,cy),recorte)
    fundo_visao=capturar_fundo(camada,cy)
    desenhar_suportes(camada, cx, cy)
    x=corte.RAIZ_X-cx
    alto,baixo=corte.PISO_ARQUIVO,corte.PISO_POCO
    if cy<baixo and cy+540>alto-36 and -24<x<984:
        for lado in (-1,1):
            pontos=[(x+lado*19,alto-35),(x+lado*23,alto+30),
                    (x+lado*20,baixo-45),(x+lado*14,baixo-8)]
            pygame.draw.lines(camada,(64,73,52),False,pontos,7)
            pygame.draw.lines(camada,(105,110,76),False,pontos,2)
        if corte.RAIZ_DUAS_BOCAS in j.cartografia:
            pygame.draw.line(camada,(141,146,85),(x,alto-6),(x,baixo-32),3)
    if cx+960>2432:
        from .arte_jardim import detalhes
        detalhes(camada,j,cx)
    if cy+540>1060 and cy<1260:
        sprite(camada,"obj_refugio",118-cx,1173,77,63)
        if cx<379:
            camada.blit(janela_arquivo(arquivo_casca.FECHADA in j.cartografia),(208-cx,1068))
    if cy+540>1770:
        for n in range(4):
            y=1802+n*6
            pts=[(x-cx,y+math.sin(x*.04+t*1.6+n)*2) for x in range(52,1410,14)]
            pygame.draw.lines(camada,(62+n*3,91+n*3,91+n*3),False,pts,1)
    # A corda percorre várias telas e serve de referência contínua de altura.
    cor=(149,121,81) if "ralo_aberto" in j.cartografia else (75,77,72)
    for x in (1037,1043):
        pygame.draw.line(camada,cor,(x-cx,298),(x-cx,1828),1)
    # Uma polia e a plataforma deixam claro que o cabo é um contrapeso.
    pygame.draw.circle(camada,(90,79,50),(1040-cx,306),11,3)
    if "ralo_aberto" not in j.cartografia:
        pygame.draw.lines(camada,(76,73,54),False,[(1015-cx,1825),(1023-cx,1835),(1061-cx,1835),(1068-cx,1825)],4)
    for tr in j.solidos:
        if tr.rect.bottom+30>=cy and tr.rect.top-18<=cy+540:
            if tr.tipo=="tranca" and tr.rect.topleft == corte.COMPORTA.topleft:
                continue
            i=3 if tr.rect.y>=1200 else 0
            terreno(camada,tr,cx,i)
    if cy-20 < corte.CASULO.bottom < cy+560 and cx-30 < corte.CASULO.centerx < cx+990:
        casulo_mola(camada, j, cx)
    arte_fio.baixo(camada, j, cx, cy, t)
    from .sinalizacao import desenhar as descidas
    descidas(camada,j,cx)
    for o in j.objetos:
        if o.id == "comporta_viveiro" and tela.colliderect(corte.COMPORTA.move(-cx,0).inflate(270,40)):
            desenhar_comporta(camada, j, cx, o, t)
        if cy-10<o.y<cy+630 and cx-60<o.x<cx+1020:
            desenhar_ponto(camada,o,j,cx)
    for n in range(24):
        x=int(n*131+math.sin(t*.4+n)*9)%corte.LARGURA
        y=int((n*83-t*(n%3+1))%corte.ALTURA)
        if cx<x<cx+960 and cy<y<cy+540:
            pygame.draw.circle(camada,(151,153,125),(x-cx,y),1)
    if j.destino_vertical is not None:
        py=j.lume.rect.bottom
        pygame.draw.line(camada,(165,143,103),(1019-cx,py+1),(1061-cx,py+1),4)
    for e in j.inimigos:
        if j.visivel(e.rect.center,18) and cy-50<e.rect.centery<cy+590:
            inimigo(camada,e,cx,j.lume,t)
    from .arte_resgates import luzes
    luzes(camada,j,cx,t)
    from .luzes_mundo import desenhar as globos
    globos(camada,j,cx)
    nivel=min(3,nivel_brilho+int(j.concluida))
    arte_fagulha.iluminar_cenario(camada,j,cx)
    compor_luz(luz,j,cx,cy,nivel)
    aplicar_nevoa(camada,luz,cy,fundo_visao,nivel)
    for v in j.vestigios:
        if v.raio(t)>16:
            if not claroes_suaves():
                brilho(camada,(v.x-cx,v.y),20)
    arte_fagulha.desenhar(camada,j,cx)
    for e in j.inimigos:
        projeteis(camada,e,cx,j.lume,j.raio,j.visivel)
    lume(camada,j.lume,cx,t,j.fagulha_ativa)
    desenhar_impactos(camada,j,cx)
    s.blit(camada,(0,0),tela)
    camada.set_clip(None)


# Os contornos mostram volumes exploráveis e suas ligações. As duas colunas de
# travessia correspondem às plataformas do mundo; o braço oeste contém o arquivo.
SALAS_MAPA = (
    ("copa","Copa do Observatório","Janela alta do Bosque",(155,205,1213,170),(69,82,65)),
    ("galeria","Galeria dos Casulos","Entrada da superfície",(48,816,1316,218),(63,79,75)),
    ("arquivo","Arquivo da Casca","Desvio no oeste",(63,1065,343,217),(92,77,62)),
    ("poco","Poço da Seiva","Marco e régua de cheia",(124,1360,1205,176),(58,72,81)),
    ("cisterna","Cisterna das Duas Margens","Contrapeso e canal",(36,1670,1358,179),(54,76,82)),
    ("estaleiro","Estaleiro das Folhas","Oficina e ponte do Córrego",(1438,734,957,316),(94,90,63)),
    ("viveiro","Viveiro Afundado","Berços e comporta oeste",(1440,1180,950,664),(62,91,88)),
)


def mapa(s,j,rect):
    r=pygame.Rect(rect)
    desenho=pygame.Rect(r.x,r.y,round(r.w*.52),r.h)
    pygame.draw.rect(s,(15,26,33),desenho)
    pygame.draw.rect(s,(57,74,75),desenho,1)
    # Reserva lateral para as entradas da superfície e preserva a altura do corte.
    sy=(desenho.height-18)/corte.ALTURA
    sx=min((desenho.width-32)/corte.LARGURA,sy*1.46)
    ponto_x=desenho.centerx-round(corte.LARGURA*sx/2)
    def tela(x,y):
        return round(ponto_x+x*sx),round(desenho.y+9+y*sy)
    def faixa(x,y,w,h):
        return pygame.Rect(*tela(x,y),max(1,round(w*sx)),max(1,round(h*sy)))

    vistos=j.cartografia
    # Planta do caminho central, do poço oriental e do corredor do arquivo.
    for origem,fim,x,y,w,h in (
        ("copa","galeria",420,360,148,479),("copa","galeria",1002,360,127,479),
        ("galeria","poco",602,990,132,400),("galeria","poco",1001,990,153,400),
        ("arquivo","galeria",389,1107,268,91),("poco","cisterna",550,1464,146,241),
        ("poco","cisterna",1038,1464,147,241),
        ("galeria","estaleiro",1340,928,185,66),
        ("estaleiro","viveiro",2145,1020,110,210)):
        if "viu_"+origem in vistos and "viu_"+fim in vistos:
            pg=faixa(x,y,w,h)
            pygame.draw.rect(s,(49,65,64),pg)
            pygame.draw.rect(s,(105,122,108),pg,1)
    for ident,nome,dica,geo,cor in SALAS_MAPA:
        if "viu_"+ident not in vistos: continue
        pg=faixa(*geo)
        pygame.draw.rect(s,cor,pg)
        pygame.draw.rect(s,tuple(min(255,v+61) for v in cor),pg,1)
    if {"viveiro_aberto","viu_cisterna","viu_viveiro"}<=vistos:
        pygame.draw.rect(s,(130,155,128),faixa(1350,1740,167,76))
    for tr in corte.terrenos("viveiro_aberto" in vistos, passarela_fio=fio_corte.REPARADA in vistos):
        if tr.tipo in ("parede","tranca"): continue
        ident=corte.setor(tr.rect.y,tr.rect.centerx)[0]
        if "viu_"+ident not in vistos: continue
        pygame.draw.line(s,(109,131,117),tela(tr.rect.left,tr.rect.top),tela(tr.rect.right,tr.rect.top),1)
    for o in corte.PONTOS:
        if "viu_"+corte.setor(o.y,o.x)[0] not in vistos: continue
        if o.tipo=="passagem":
            losango(s,*tela(o.x,o.y),4,AMBAR,False)
        elif o.id in ("marco_poco","marco_estaleiro","ralo_cisterna","selo_copa"):
            pygame.draw.circle(s,PALIDO,tela(o.x,o.y),3,1)
    if "ralo_aberto" in vistos:
        cx,_=tela(1040,0)
        for y in range(tela(0,316)[1],tela(0,1828)[1],5):
            pygame.draw.line(s,(168,144,97),(cx,y),(cx,y+2))
    if j.em_vertical:
        losango(s,*tela(*j.lume.rect.center),5,AMBAR)
    tx=desenho.right+16
    passo=max(22,min(43,(r.h-26)//len(SALAS_MAPA)))
    for n,(ident,nome,dica,geo,cor) in enumerate(SALAS_MAPA):
        aberto="viu_"+ident in vistos
        atual=j.em_vertical and nome==j.setor_vertical
        y=r.top+n*passo+1
        texto(s,nome if aberto else "Trecho por descobrir",tx,y,16,
              AMBAR if atual else PALIDO if aberto else (106,124,124),"forte" if atual else "normal")
        if aberto and passo>=35:
            texto(s,dica,tx,y+20,12,TEAL)
    if r.h>=180:
        texto(s,"Losango: passagem   ·   Círculo: marco",tx,r.bottom-22,12,OSSO)
