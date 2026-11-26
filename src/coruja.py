"""Voo, garras e penas da Coruja; o sino conserva a abertura crítica alcançável."""
from math import hypot, sin
from random import Random
import pygame


def iniciar(e):
    e.fase = 1
    e.tecnica = ''
    e.rng_coruja = Random(731 + e.inicio)
    e.memoria_coruja = []
    e.combo_coruja = 0
    e.penas = []
    e.ouvido_corpo = None


def _escutado(e):
    if e.ouvido_corpo is not None:
        alvo=e.ouvido_corpo
        e.ouvido_corpo=None
        e.x_ouvido=None
        return alvo
    # Sem ruído novo a guardiã cega varre o outro lado, sem consultar a
    # posição atual de Lume. A lembrança é consumida em cada novo plano.
    alvo=pygame.FRect(0,0,24,42)
    alvo.midbottom=(e.esq if e.x>(e.esq+e.dir)/2 else e.dir),e.chao
    return alvo


def preparar(e, corpo, eventos, continuacao=False):
    distancia = abs(e.x - corpo.centerx)
    opcoes = ('rasante', 'garra', 'penas')
    pesos = [1.2, 2.3 if distancia < 180 else .5, 1.8 if distancia > 220 else .45]
    for n, nome in enumerate(opcoes):
        if e.memoria_coruja and e.memoria_coruja[-1] == nome:
            pesos[n] *= .16
    e.tecnica = e.rng_coruja.choices(opcoes, weights=pesos, k=1)[0]
    e.memoria_coruja = (e.memoria_coruja + [e.tecnica])[-3:]
    if not continuacao:
        e.combo_coruja = int(e.fase == 2)
    e.frente = 1 if corpo.centerx >= e.x else -1
    e.destino = max(e.esq, min(e.dir, corpo.centerx + (92 * e.frente if e.tecnica == 'garra' else 0)))
    if e.tecnica == 'penas':
        e.alvo_y = corpo.centery
    else:
        piso = e.chao
        apoio = next((a for a in e.apoios() if a.left <= corpo.centerx < a.right
                      and abs(corpo.bottom - a.top) < 4), None)
        if apoio is not None:
            piso = apoio.top
        e.alvo_y = piso - (18 if e.tecnica == 'garra' else 31 if e.turno % 2 else 12)
    e.impacta = e.atingiu = False
    e._mudar('aviso', .66 if e.fase == 1 else .53)
    eventos.append('aviso')


def atualizar(e, dt, corpo, ruido, eventos, fagulha=None):
    from .chefes import Fio, aproximar
    if (e.alvo_fagulha(fagulha) and not e.sino_soou
            and not (e.tecnica == "sino" and e.estado in ("aviso","investida"))):
        e.ultima_fagulha = fagulha
        e.reacao_fagulha = "sino"
        e.sino_soou = True
        e.onda = 1.
        if e.estado == "busca":
            e.tempo = min(e.tempo,.15)
        eventos.extend(("sino","sino_fagulha"))
    if ruido > .05:
        e.x_ouvido = corpo.centerx
        e.ouvido_corpo = corpo.copy()
    vivos = []
    for p in e.penas:
        p.x += p.vx * dt
        p.y += p.vy * dt
        p.tempo -= dt
        if pygame.FRect(p.x - 7, p.y - 5, 14, 10).colliderect(corpo):
            eventos.append('dano_jogador')
        elif p.tempo > 0 and e.esq - 30 < p.x < e.dir + 30 and e.chao - 300 < p.y < e.chao + 10:
            vivos.append(p)
    e.penas[:] = vivos
    if e.fase == 1 and (e.progresso or e.vida <= 50) and e.estado != 'aberto':
        e.fase = 2
        e.combo_coruja = 0
        e.penas.clear()
        e._mudar('muda_coruja', .95)
        eventos.append('coruja_muda')
    if e.estado == 'muda_coruja':
        e.y = aproximar(e.y, e.chao - 125, dt * 180)
        if e.tempo <= 0:
            e._mudar('busca', .2)
        return
    if e.estado == 'busca':
        e.y = aproximar(e.y, e.chao - 116 + sin(e.relogio * 3) * 8, dt * 160)
        # O voo é deslocamento contínuo, não um salto entre posições.
        ronda = e.esq + 112 if e.turno % 2 else e.dir - 112
        e.x = aproximar(e.x, ronda, dt * 115)
        if e.tempo <= 0:
            e.turno += 1
            if e.sino_soou:
                if abs(e.dir - e.x) < 130:
                    e._mudar('contorna', 1.)
                    return
                e.sino_soou = False
                e.penas.clear()
                e.combo_coruja = 0
                e.tecnica = 'sino'
                e._aviso_investida(e.dir, e.chao - 32, .82, True, eventos)
            else:
                preparar(e, _escutado(e), eventos)
    elif e.estado == 'contorna':
        e.x = aproximar(e.x, e.esq, dt * 380)
        e.frente, e.y = -1, e.chao - 145
        if e.tempo <= 0:
            e._mudar('busca', .12)
    elif e.estado == 'aviso':
        if e.tecnica != 'penas':
            e.y = aproximar(e.y, e.alvo_y, dt * 230)
        if e.tempo <= 0:
            if e.tecnica == 'penas':
                dx, dy = e.destino - e.x, e.alvo_y - e.y
                tamanho = max(1., hypot(dx, dy))
                vx, vy = dx / tamanho * 315, dy / tamanho * 315
                # Ambas as linhas foram mostradas durante todo o aviso.
                for deslocamento in (-.16, .16):
                    e.penas.append(Fio(e.x, e.y, vx - vy * deslocamento, vy + vx * deslocamento))
                e._mudar('recolhe_coruja', .4)
            else:
                e._mudar('investida', 2.1)
    elif e.estado == 'investida':
        if e.tecnica == 'sino':
            e._voar(dt, corpo, eventos, 510)
        else:
            # Diagonal até a faixa anunciada, sem perseguir movimento posterior.
            dx, dy = e.destino - e.x, e.alvo_y - e.y
            distancia = hypot(dx, dy)
            passo = min(distancia, dt * (590 if e.fase == 2 else 515))
            if distancia > .01:
                e.x += dx / distancia * passo
                e.y += dy / distancia * passo
            faixa = pygame.FRect(e.x - 32, e.y - 12, 64, 23 if e.tecnica == 'garra' else 19)
            e._colisao(corpo, faixa, eventos)
            if distancia <= passo + .01 or e.tempo <= 0:
                e._mudar('recolhe_coruja', (.36 if e.combo_coruja else .65)*e.ritmo.recuperacao)
    elif e.estado == 'recolhe_coruja':
        e.y = aproximar(e.y, e.chao - 116, dt * 170)
        if e.tempo <= 0:
            if e.combo_coruja and not e.sino_soou:
                e.combo_coruja -= 1
                preparar(e, _escutado(e), eventos, continuacao=True)
            else:
                e._mudar('busca', .22)
