"""Luz refletida na pintura, filamento em voo e brasa aderida à casca."""
from functools import lru_cache
from math import exp, hypot, sin

import pygame

from .ilustracao import alto_contraste, claroes_suaves


@lru_cache(maxsize=32)
def _luz_refletida(raio, intensidade):
    mascara = pygame.Surface((raio*2, raio*2))
    for r in range(raio, 0, -1):
        v = (1 - (r/raio)**2)**2 * intensidade/8
        pygame.draw.circle(mascara, (round(236*v), round(128*v), round(44*v)), (raio, raio), r)
    return mascara


def iluminar_cenario(s, j, cx):
    f = j.fagulha_ativa
    if f is None:
        return
    agora = j.tempo
    raio = 8 * round(f.raio(agora)/8)
    if raio < 8:
        return
    wx, wy = f.posicao(agora)
    caixa = pygame.Rect(0, 0, 2*raio, 2*raio)
    caixa.center = (round(wx-cx), round(wy))
    area = caixa.clip(s.get_clip())
    if not area:
        return
    # A luz preserva os veios escuros da casca e pega mais nos planos claros.
    reflexo = pygame.transform.grayscale(s.subsurface(area))
    reflexo.fill((51, 51, 51), special_flags=pygame.BLEND_RGB_ADD)
    idade = agora-f.pouso_em
    intensidade = 7 if idade < 0 else 8 if idade < .12 else 5
    if claroes_suaves():
        intensidade = 4
    mascara = _luz_refletida(raio, intensidade)
    recorte = area.move(-caixa.left, -caixa.top)
    reflexo.blit(mascara, (0, 0), recorte, special_flags=pygame.BLEND_RGB_MULT)
    s.blit(reflexo, area, special_flags=pygame.BLEND_RGB_ADD)


def _folha(s, cor, pontos):
    pygame.draw.polygon(s, cor, pontos)
    pygame.draw.aalines(s, cor, True, pontos)


@lru_cache(maxsize=16)
def _aura(raio, suave):
    aura = pygame.Surface((2*raio, 2*raio))
    for r in range(raio, 0, -1):
        v = (1-r/raio)**2 * (.65 if suave else 1)
        pygame.draw.circle(aura, (round(145*v), round(68*v), round(15*v)), (raio, raio), r)
    return aura


def _emissao(s, x, y, raio):
    s.blit(_aura(raio, claroes_suaves()), (round(x)-raio, round(y)-raio),
           special_flags=pygame.BLEND_RGB_ADD)


def desenhar_voo(s, f, agora, cx, escala=1.):
    wx, y = f.posicao(agora)
    x = wx-cx
    dx, dy = f.destino[0]-f.origem[0], f.destino[1]-f.origem[1]
    comprimento = max(1., hypot(dx, dy))
    ux, uy = dx/comprimento, dy/comprimento
    def ponto(alongar, desviar):
        return (x+(alongar*ux-desviar*uy)*escala, y+(alongar*uy+desviar*ux)*escala)

    # Cada segmento existe só depois da passagem da cabeça. A fímbria oscila na esteira.
    cauda = []
    for i in range(9):
        instante = agora-i*.006*escala
        bx, by = f.posicao(max(f.inicio, instante))
        largura = (1-i/9)*2.1*escala
        ondulacao = sin(i*.83 + (agora-f.inicio)*24)*i*.22*escala
        cauda.append((bx-cx, by, largura, ondulacao))
        if instante <= f.inicio:
            break
    if len(cauda) > 1:
        esquerda = [(bx-(w+o)*uy, by+(w+o)*ux) for bx,by,w,o in cauda]
        direita = [(bx+(w-o)*uy, by-(w-o)*ux) for bx,by,w,o in cauda]
        _folha(s, (170, 77, 36), esquerda+direita[::-1])
        pygame.draw.aalines(s, (245, 159, 75), False, esquerda)
        if len(cauda) > 3 and not claroes_suaves():
            pygame.draw.aalines(s, (177, 120, 59), False,
                                [(bx-(o+4)*uy,by+(o+4)*ux) for bx,by,w,o in cauda[2:]])
    _emissao(s, x, y, round(18*escala))
    _folha(s, (236, 142, 66), [ponto(-9,0), ponto(-1,-2.7), ponto(5,-1.6),
                                ponto(8,0), ponto(2,2.5)])
    pygame.draw.aaline(s, (255, 248, 200), ponto(-5,0), ponto(6,0))
    if alto_contraste():
        pygame.draw.circle(s, (255,255,238), (round(x),round(y)), 2)


def _pouso(s, j, cx, f):
    idade = j.tempo-f.pouso_em
    wx, wy = f.destino
    x, y = wx-cx, wy
    vigor = min(1., f.restante(j.tempo)*5)
    if vigor <= .015:
        return
    suave = claroes_suaves()
    golpe = max(0., 1-idade/.36)
    _emissao(s, x, y, max(2, round((17 + golpe*12)*vigor)))
    if golpe:
        # As fibras correm pelo bordo real do apoio. Marcas suspensas não fabricam um chão.
        for apoio in j.solidos:
            r = apoio.rect
            if r.left <= wx < r.right and abs(r.top-wy) <= 10:
                distancia = (1-exp(-idade*15)) * 33
                cor = (round(126+90*golpe),round(77+65*golpe),round(42+32*golpe))
                for lado in (-1,1):
                    fio = []
                    for i, desvio in enumerate((0, -1, 1, 0, 1, 0)):
                        px = min(r.right-1,max(r.left,wx+lado*distancia*i/5))
                        fio.append((px-cx, r.top+desvio))
                    pygame.draw.aalines(s, cor, False, fio)
                break
        for i, (vx, vy) in enumerate(((-71,-43),(45,-74),(-18,-83),(68,-38),(-48,-59),(26,-51))):
            if suave and i > 1:
                break
            tempo = idade* (1+i*.027)
            px, py = x+vx*tempo, y+vy*tempo+91*tempo**2
            pygame.draw.aaline(s, (round(139+107*golpe),round(78+95*golpe),59),
                               (px-vx*.018, py-(vy+182*tempo)*.018), (px, py))
    # Uma semente plantada. A lingueta oscila, a base fica presa à marca.
    oscilacao = sin(idade*8)*vigor
    altura = (7+oscilacao+3*golpe)*vigor
    cor = tuple(round(c*vigor) for c in (246, 159, 74))
    _folha(s, cor, [(x-3*vigor,y),(x-3*vigor,y-altura*.54),(x+oscilacao,y-altura),
                    (x+3*vigor,y-altura*.55),(x+2*vigor,y)])
    pygame.draw.aaline(s, tuple(round(c*vigor) for c in (255,235,168)),
                       (x,y-1), (x+oscilacao,y-altura*.7))


def desenhar(s, j, cx):
    f = j.fagulha_ativa
    if f is None:
        return
    if j.tempo < f.pouso_em:
        desenhar_voo(s, f, j.tempo, cx)
    else:
        _pouso(s, j, cx, f)
