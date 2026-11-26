"""Anotações voluntárias, restritas às células que o jogador já descobriu."""
import math
import re
from .descoberta import chave,TAMANHO

LIMITE=32
TIPOS=('voltar','perigo','caminho','segredo')
CORES=((226,183,109),(217,115,102),(137,196,182),(178,152,212))


def carregar(dados,explorado):
    if dados is None:return []
    if not isinstance(dados,list) or len(dados)>LIMITE:raise ValueError('Marcas do mapa inválidas')
    out=[];usadas=set()
    for m in dados:
        if not isinstance(m,dict):raise ValueError('Marca inválida')
        celula,tipo=m.get('celula'),m.get('tipo')
        if (not isinstance(celula,str) or len(celula)>70 or
                not re.fullmatch(r'(?:corte|[0-9]{1,9}:[0-3])/[0-9]{1,4}/[0-9]{1,4}',celula) or
                tipo not in TIPOS or celula not in explorado or celula in usadas):
            raise ValueError('Marca fora do mapa descoberto')
        usadas.add(celula);out.append({'celula':celula,'tipo':tipo})
    return out


def alternar(j,ponto,tipo):
    if tipo not in TIPOS or not all(math.isfinite(v) for v in ponto):return False,'Marca inválida.'
    c=chave(j,*ponto)
    if c not in j.explorado:return False,'Explore e ilumine este trecho antes de marcar.'
    antiga=next((m for m in j.marcas if m['celula']==c),None)
    if antiga is not None:
        j.marcas.remove(antiga)
        return True,'Marca removida.'
    if len(j.marcas)>=LIMITE:return False,f'Limite de {LIMITE} marcas. Remova uma com o botão direito.'
    j.marcas.append({'celula':c,'tipo':tipo})
    return True,'Marca de '+tipo+' guardada.'


def locais(j):
    prefixo=chave(j,0,0).split('/')[0]+'/'
    for m in j.marcas:
        if not m['celula'].startswith(prefixo) or m['celula'] not in j.explorado:continue
        _,x,y=m['celula'].split('/')
        yield (int(x)+.5)*TAMANHO,(int(y)+.5)*TAMANHO,TIPOS.index(m['tipo'])


def desenhar(s,j,ponto,mundo):
    from . import pygame_hd as pygame
    for x,y,t in locais(j):
        if not mundo.collidepoint(x,y):continue
        px,py=ponto(x,y);cor=CORES[t]
        pygame.draw.circle(s,(12,22,24),(px,py),7)
        if t==0:
            pygame.draw.lines(s,cor,False,[(px+3,py-4),(px-4,py),(px+3,py+4)],2)
        elif t==1:
            pygame.draw.polygon(s,cor,[(px,py-5),(px+5,py+4),(px-5,py+4)],1)
            pygame.draw.line(s,cor,(px,py-2),(px,py+1),1)
        elif t==2:pygame.draw.line(s,cor,(px-5,py),(px+5,py),2);pygame.draw.line(s,cor,(px+1,py-4),(px+5,py),2)
        else:pygame.draw.polygon(s,cor,[(px,py-5),(px+5,py),(px,py+5),(px-5,py)],1)
