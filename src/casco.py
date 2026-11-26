"""Casco Oco: compromissos de mira, combos curtos e saltos físicos sobre a arena."""
from dataclasses import dataclass
from math import sin, pi
import pygame


@dataclass
class Onda:
    x: float
    y: float
    vx: float
    tempo: float = 1.35
    tocada: bool = False


def iniciar(e):
    e.fase = 1
    e.tecnica = ''
    e.combo_restante = 0
    e.alto_t = 0.
    e.ondas = []
    e.origem_salto = (e.x, e.y)
    e.voo_t = 0.
    e.ultimo_casco = ''


def preparar(e, corpo, eventos, continuacao=False):
    """Reavalia entre golpes; dentro de um aviso a mira fica imutável."""
    if not continuacao:
        e.combo_restante = 1 if e.fase == 2 else 0
    distancia = abs(corpo.centerx - e.x)
    # Alternar famílias impede a sequência degenerada de saltos repetidos.
    salto = e.ultimo_casco != 'salto' and (e.alto_t > .6 or (continuacao and distancia < 155))
    e.tecnica = 'salto' if salto else 'varrida' if distancia < 104 else 'retorno' if continuacao else 'carga'
    e.ultimo_casco = e.tecnica
    e.frente = 1 if corpo.centerx >= e.x else -1
    if salto:
        e.destino = max(e.esq, min(e.dir, corpo.centerx))
        e.alvo_y = e.chao - 35.
        duracao = .63 if e.fase == 1 else .54
    elif e.tecnica == 'varrida':
        e.destino = e.x + e.frente * 113
        e.alvo_y = e.chao - 44.
        duracao = .55 if e.fase == 1 else .47
    else:
        e.destino = max(e.esq, min(e.dir, corpo.centerx + e.frente * 142))
        e.alvo_y = e.chao - 35.
        duracao = .62 if e.fase == 1 else .5
    e.atingiu = False
    e._mudar('aviso', duracao)
    eventos.append('aviso')


def _terminar(e, eventos):
    # Uma janela sem contato existe mesmo entre os dois golpes da segunda fase.
    e._mudar('freio_casco', (.30 if e.combo_restante else .76)*e.ritmo.recuperacao)


def _tabua(e, eventos):
    if not e.tabua_quebrada and abs(e.x - e.inicio - e.largura / 2) < 70:
        e.tabua_quebrada = True
        eventos.append('impacto')


def _empurrar(e, dt, corpo, direcao, eventos):
    from .chefes import aproximar
    if not e.engatado:
        return
    if e._perto(corpo, e.barrel_x, 95):
        if direcao:
            desejado = corpo.centerx + direcao * 27
            e.barrel_x = max(e.esq, min(e.dir, aproximar(e.barrel_x, desejado, dt * 295)))
    else:
        e.engatado = False
    if abs(e.barrel_x - e.entalhe) < 24:
        e.barrel_x = e.entalhe
        e.assentado, e.engatado = True, False
        eventos.append('impacto')


def ponto_salto(origem, destino, alvo_y, p):
    """Alcança a coluna antes de cair: pune quem permanece no apoio alto."""
    ox, oy = origem
    return (ox + (destino - ox) * min(1., p / .68),
            oy + (alvo_y - oy) * p - 155 * sin(pi * p))


def atualizar(e, dt, corpo, direcao, eventos, fagulha=None):
    from .chefes import aproximar
    _empurrar(e, dt, corpo, direcao, eventos)
    e.alto_t = e.alto_t + dt if corpo.bottom < e.chao - 48 else max(0., e.alto_t - dt * 2)
    for o in e.ondas:
        o.x += o.vx * dt
        o.tempo -= dt
        if not o.tocada and pygame.FRect(o.x - 17, o.y - 16, 34, 16).colliderect(corpo):
            o.tocada = True
            eventos.append('dano_jogador')
    e.ondas[:] = [o for o in e.ondas if o.tempo > 0 and e.esq - 30 < o.x < e.dir + 30]

    if e.fase == 1 and (e.progresso or e.vida <= 50) and e.estado not in ('aberto', 'flor', 'rastro', 'investida_seiva'):
        e.fase = 2
        e.combo_restante = 0
        e.ondas.clear()
        e._mudar('muda_casco', 1.05)
        eventos.append('casco_muda')
    if e.estado == 'muda_casco':
        e.y = aproximar(e.y, e.chao - 35., dt * 220)
        if e.tempo <= 0:
            preparar(e, corpo, eventos)
        return

    if e.estado == 'rastro':
        e.ondas.clear()
        if e.tempo <= 0:
            e._mudar('investida_seiva', 3.)
        return
    if e.estado == 'investida_seiva':
        e.x = aproximar(e.x, e.destino, dt * 450)
        e.y = aproximar(e.y, e.chao - 35., dt * 260)
        e._colisao(corpo, pygame.FRect(e.x - 36, e.y - 17, 72, 52), eventos)
        _tabua(e, eventos)
        if abs(e.x - e.destino) < .01:
            e.onda = 1.
            e._mudar('flor', .50)
            eventos.append('impacto')
        return
    if e.estado == 'flor':
        e.y = aproximar(e.y, e.chao - (45 if e.progresso == 0 else 70), dt * 150)
        if e.tempo <= 0:
            e._abrir(2.5 if e.progresso else 3.1, eventos)
        return
    if e.estado == 'busca':
        e.y = aproximar(e.y, e.chao - 35., dt * 200)
        if e.tempo <= 0:
            preparar(e, corpo, eventos)
    elif e.estado == 'aviso' and e.tempo <= 0:
        if e.tecnica == 'salto':
            e.origem_salto = e.x, e.y
            e.voo_t = 0.
            e._mudar('salto_casco', .76)
        elif e.tecnica == 'varrida':
            e._mudar('varrida_casco', .18)
        else:
            e._mudar('investida', 2.)
    elif e.estado == 'investida':
        e.y = e.chao - 35.
        anterior = e.x
        e.x = aproximar(e.x, e.destino, dt * (590 if e.fase == 2 else 510))
        _tabua(e,eventos)
        e._colisao(corpo,pygame.FRect(e.x-42,e.chao-53,84,52),eventos)
        marca = e.alvo_fagulha(fagulha)
        if marca and min(anterior,e.x) <= marca[0] <= max(anterior,e.x):
            e.ultima_fagulha = fagulha
            e.reacao_fagulha = "seiva"
            e.combo_restante = 0
            e._abrir(2.8,eventos)
            eventos.append("casco_presaseiva")
            return
        if e.tempo <= 0 or abs(e.x-e.destino)<.01:
            _terminar(e,eventos)
    elif e.estado == 'varrida_casco':
        area = pygame.FRect(0, e.chao - 72, 113, 71)
        area.left = e.x if e.frente > 0 else e.x - 113
        e._colisao(corpo, area, eventos)
        if e.tempo <= 0:
            _terminar(e, eventos)
    elif e.estado == 'salto_casco':
        e.voo_t = min(.76, e.voo_t + dt)
        p = e.voo_t / .76
        e.x, e.y = ponto_salto(e.origem_salto,e.destino,e.alvo_y,p)
        e._colisao(corpo, pygame.FRect(e.x - 33, e.y - 20, 66, 52), eventos)
        if p >= 1:
            e.y = e.chao - 35.
            e.ondas.extend(Onda(e.x, e.chao, lado * 255) for lado in (-1, 1))
            eventos.append('impacto')
            _terminar(e, eventos)
    elif e.estado == 'freio_casco' and e.tempo <= 0:
        if e.combo_restante:
            e.combo_restante -= 1
            preparar(e, corpo, eventos, continuacao=True)
        else:
            e._mudar('busca', .22)
