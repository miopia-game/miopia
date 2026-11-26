"""Luz permanente criada pelo jogador e clareiras conquistadas em desafios."""
import math,re
from . import pygame_hd as pygame
from functools import lru_cache

RAIO_GLOBO=440
MAX_GLOBOS=24


def regiao(j):return 'corte' if j.em_vertical else f'{j.volta}:{j.etapa}'


def carregar(dados):
    if dados is None:return []
    if not isinstance(dados,list) or len(dados)>MAX_GLOBOS:raise ValueError('Globos inválidos')
    out=[]
    for d in dados:
        if (not isinstance(d,dict) or not isinstance(d.get('regiao'),str) or
            not re.fullmatch(r'(?:corte|[0-9]{1,9}:[0-3])',d['regiao']) or
            any(type(d.get(k)) not in (int,float) or not math.isfinite(d[k]) for k in ('x','y')) or
            not 0<=d['x']<=5000 or not 0<=d['y']<=2000):raise ValueError('Globo fora do mundo')
        out.append({'regiao':d['regiao'],'x':d['x'],'y':d['y']})
    return out


def colocar(j):
    if j.modo!='historia' or hasattr(j,'sala_id') or getattr(j,'ensaio_armas',False):
        j.notificar('Globos são usados nas trilhas da História.');return False
    if len(j.globos)>=MAX_GLOBOS:j.notificar('Já há 24 globos nesta campanha.');return False
    x,y=j.lume.rect.center
    if any(math.dist((x,y),(g['x'],g['y']))<120 for g in j.globos if g['regiao']==regiao(j)):
        j.notificar('Já há um globo próximo. Guarde este para outra parte da trilha.');return False
    j.globos.append({'regiao':regiao(j),'x':x,'y':y})
    j.eventos.append('resgate');j.notificar('Globo fixado: esta região continua iluminada após morrer, sair e carregar.',6.)
    return True


def fontes(j):
    return [(g['x'],g['y'],RAIO_GLOBO) for g in j.globos if g['regiao']==regiao(j)]


def zonas(j):
    from .encontros import CLAREIRAS
    from . import galeria_taquaral
    atual = regiao(j)
    return ([pygame.Rect(c.area) for c in CLAREIRAS if c.regiao == atual and c.id in j.tochas]
            + list(galeria_taquaral.zonas(j)))


def pontos_claros(j, pontos):
    from .resgates import fontes as resgatados
    areas = zonas(j)
    focos = fontes(j) + resgatados(j)
    focos.extend((v.x, v.y, v.raio(j.tempo)) for v in j.vestigios)
    return tuple(any(z.collidepoint(ponto) for z in areas)
                 or any(math.dist(ponto, (x, y)) < r*.65 for x, y, r in focos)
                 for ponto in pontos)


def claro(j, ponto):
    return pontos_claros(j, (ponto,))[0]


def desenhar(s,j,cx):
    from .ilustracao import AMBAR,brilho
    for x,y,r in fontes(j):
        if not cx-30<x<cx+990:continue
        x-=cx
        pygame.draw.circle(s,(129,173,139),(round(x),round(y)),12,2)
        pygame.draw.circle(s,AMBAR,(round(x),round(y)),5)
        brilho(s,(x,y),24)


@lru_cache(maxsize=4)
def mascara_zona(w,h):
    s=pygame.Surface((w,h));s.fill((0,0,0))
    for n in range(0,73,2):
        u=n/72;v=round(255*u*u*(3-2*u))
        pygame.draw.rect(s,(v,v,v),(n,n,w-2*n,h-2*n),border_radius=max(4,100-n))
    return s


def compor_zonas(s,j,cx,cy):
    for z in zonas(j):
        if z.colliderect(pygame.Rect(cx,cy,960,540)):
            s.blit(mascara_zona(z.w,z.h),(z.x-cx,z.y-cy),special_flags=pygame.BLEND_RGB_MAX)
