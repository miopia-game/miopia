"""Poses ilustradas e efeitos locais filmados no momento do golpe."""
from functools import lru_cache
from math import cos, pi, sin

import pygame

from .ilustracao import OSSO, brilho, claroes_suaves, original
from . import movimento_arte

AEREOS = {"morcego", "vespa", "asa-fendida", "coruja"}
CASCO = {"carabideo", "caruncho", "casco-oco"}
SERPENTES = {"cobra", "cobra-dos-bercos"}
TECELOES = {"aranha", "tecela"}
TERRESTRES = {"aranha", "carabideo", "caruncho", "sombra"}
RITMO_ASAS = {"morcego": 4.6, "vespa": 8.3, "asa-fendida": 3.7, "coruja": 3.2}
PERCURSO = TERRESTRES | SERPENTES | {"casco-oco", "tecela"}
PASSO_RELATIVO = {"aranha": .44, "carabideo": .52, "caruncho": .44, "casco-oco": .40,
                  "sombra": .47, "cobra": .88, "cobra-dos-bercos": .98}
IMPACTOS_MOVEIS = {"rasteira", "mordida", "carga", "pique", "bote_caca", "retorno",
                   "investida_seiva", "varrida_casco", "varredura", "salto", "salto_alto"}

PALETAS = {
    "morcego": (220, 145, 95), "asa-fendida": (223, 113, 130),
    "vespa": (243, 201, 83), "aranha": (237, 204, 171), "tecela": (189, 214, 159),
    "carabideo": (125, 207, 163), "caruncho": (218, 164, 91), "casco-oco": (251, 176, 65),
    "sombra": (174, 158, 237), "cobra": (169, 208, 112), "cobra-dos-bercos": (197, 205, 126),
    "coruja": (221, 216, 181),
}
DISPAROS = {"fio", "ferrao", "eco", "onda", "orbe", "veneno", "leque_fio", "leque_ferrao",
            "onda_dupla", "penas", "fio_duplo", "trama_alta", "trama_baixa", "chama_ninhada"}


def fracao(valor):
    return min(1., max(0., valor))


@lru_cache(maxsize=420)
def quadro(ident, pose, largura, altura, lado, angulo=0):
    base = original(f"inimigos-v2/{ident}-{pose}.png")
    escala = min(largura / base.get_width(), altura / base.get_height())
    imagem = pygame.transform.smoothscale(base, (round(base.get_width()*escala),
                                                 round(base.get_height()*escala)))
    if lado < 0:
        imagem = pygame.transform.flip(imagem, True, False)
    if angulo:
        imagem = pygame.transform.rotate(imagem, angulo * lado)
    return imagem


def ciclo(ident, fase, tecnica, tempo, passos, w, progresso):
    n = movimento_arte.N_QUADROS
    quadro_acao = round(fracao(progresso)*(n-1))
    if ident == "coruja":
        if fase == "preparacao":
            # Abre as asas e as ergue para a arrancada.
            return ident, (n//2 + round(n/2*fracao(progresso*1.25))) % n
        if fase in {"ferido", "brecha"}:
            return ident, n//2
        if fase == "ataque" and tecnica in {"garra", "coro_queda", "coro_investida", "rasante"}:
            return "coruja-impulso", round(quadro_acao*.375)
        if fase == "neutro" and passos and passos.velocidade > 60:
            # Após duas batidas, segura a pose de asa aberta num breve planeio.
            batida = int(tempo * RITMO_ASAS[ident] * n) % (3*n)
            return ident, (n//4 + min(batida, 2*n)) % n
    if ident in AEREOS and fase in {"neutro", "ataque", "recuo", "preparacao"}:
        ativo = fase == "ataque"
        nome = ident+"-impulso" if ativo and ident in {"vespa", "coruja"} else ident
        # Um único relógio por espécie preserva a fase das asas ao trocar de ação.
        fr = movimento_arte.por_tempo(tempo, RITMO_ASAS[ident])
        return nome, fr
    if ident not in PERCURSO:
        return None
    if ident == "tecela":
        if fase == "ataque":
            return "tecela-gesto", quadro_acao
        if fase in {"neutro","recuo","preparacao"}:
            return ident, movimento_arte.por_tempo(tempo,1.08)
        return None
    if ident in SERPENTES and fase == "preparacao":
        return ident+"-recolher", quadro_acao
    if fase == "ataque":
        if ident in SERPENTES:
            return ident+"-impulso", quadro_acao
        salto_aranha = ident == "aranha" and tecnica in {"salto","salto_alto"}
        if tecnica not in IMPACTOS_MOVEIS or salto_aranha:
            return ident+"-gesto", quadro_acao
        if passos and passos.velocidade > 1:
            return ident+"-impulso", passos.quadro_passada(w*PASSO_RELATIVO[ident])
        return ident+"-impulso", quadro_acao
    if passos and fase in {"passos", "neutro", "recuo"}:
        comprimento = w*PASSO_RELATIVO[ident]
        if ident in SERPENTES:
            return ident, movimento_arte.por_distancia(passos.distancia, comprimento)
        if passos.velocidade > 1 or passos.tempo_passada is not None:
            return ident, passos.quadro_passada(comprimento)
    return None


def corpo(s, ident, fase, x, y, medida, lado, tempo, p, tecnica="", *, centro=False, passos=None):
    w, h = medida
    sx, sy, angulo = 1., 1., 0
    pose = "repouso"
    if fase in {"neutro", "passos"}:
        if ident in {"morcego", "asa-fendida", "vespa"}:
            # Pequeno deslocamento do tórax acompanha a força da batida.
            y += .021*h*sin(2*pi*RITMO_ASAS[ident]*tempo-.48)
    elif fase == "preparacao":
        pose = "preparacao"
        if ident in AEREOS:
            angulo = round((-12 if tecnica in {"mergulho", "garra", "queda"} else 9) * p)
        elif ident not in SERPENTES:
            sx += .08 * p
            sy -= .15 * p
        x -= lado * round(4*p)
    elif fase == "ataque":
        pose = "ataque"
        impulso = sin(pi * p)
        sx += (.22 if ident in CASCO or ident in SERPENTES else .11) * impulso
        if tecnica in {"mergulho", "garra", "queda"}:
            angulo = -21
        elif tecnica in {"rasante", "rasante_baixo", "fagulha", "sino", "coro_investida"}:
            angulo = -6
        elif tecnica in DISPAROS:
            x -= lado * round(7*(1-p))
        if ident in CASCO and tecnica in {"carga", "retorno", "investida_seiva"}:
            sy -= .11
        if ident in TECELOES and tecnica not in DISPAROS:
            sy -= .13 * impulso
    elif fase == "recuo":
        pose = "preparacao" if ident in AEREOS or ident in TECELOES else "repouso"
        sy -= .16 * (1-p)
        angulo = 6 if ident in AEREOS else 0
    elif fase == "ferido":
        pose = "preparacao"
        sx, sy, angulo = .9, .83, 8
    elif fase == "brecha":
        pose = "preparacao" if ident in AEREOS else "repouso"
        sx, sy = 1.04, .78
    if ident == "coruja":
        sx = sy = 1.
    animacao = ciclo(ident, fase, tecnica, tempo, passos, w, p)
    w, h = round(w*sx), round(h*sy)
    if animacao:
        faixa, quadro_atual = animacao
        return movimento_arte.desenhar(s, faixa, quadro_atual, x, y, (w,h), lado,
                                       centro=centro, angulo=angulo if centro else 0)
    imagem = quadro(ident, pose, w, h, lado, angulo)
    ancora = {"center" if centro else "midbottom": (round(x), round(y))}
    rect = imagem.get_rect(**ancora)
    s.blit(imagem, rect)
    return rect


def particulas(s, x, y, lado, p, cor, *, poeira=False, quantidade=7):
    """Fragmentos curtos partem do corpo ou do ponto de contato já ocorrido."""
    for n in range(quantidade):
        a = (n - (quantidade-1)/2) * (.22 if poeira else .42)
        dx = (8 + n%4*4 + 21*p) * cos(a)
        dy = -(5 + n%3*4)*sin(pi*p) if poeira else (7 + 26*p)*sin(a)
        px, py = round(x + lado*dx), round(y + dy)
        tam = 1 + int(p < .58)
        tom = tuple(round(c*(.86-.46*p)) for c in cor)
        pygame.draw.polygon(s, tom, [(px-tam,py+1),(px+lado*2,py-tam),
                                      (px+tam+1,py+1),(px,py+tam+1)])


def efeito_ataque(s, ident, tecnica, fase, ponto, lado, p, escala=1.):
    """Efeitos respeitam a fase ativa, sem consultar alvos ou trajetórias futuras."""
    cor = PALETAS[ident]
    x, y = ponto
    if fase == "recuo":
        if p < .48 and (ident in CASCO or tecnica in {"salto", "salto_alto", "queda", "salto_casco"}):
            particulas(s, x, y, -lado, p, cor, poeira=True)
        return
    if fase != "ataque":
        return

    if tecnica in DISPAROS or tecnica in {"fenda", "fenda_dupla", "coro_queda"}:
        if p < .6:
            ponto_local = (round(x+lado*12*escala), round(y-14*escala))
            if not claroes_suaves():
                brilho(s, ponto_local, round((1-p)*18*escala))
            particulas(s, *ponto_local, lado, p, cor, quantidade=6)
            pygame.draw.circle(s, OSSO, ponto_local, max(1, round(3*(1-p)*escala)))
    elif ident == "sombra":
        particulas(s, x, y-13*escala, -lado, p, cor, quantidade=10)
        particulas(s, x, y-4*escala, -lado, p, (103, 70, 154), quantidade=6)
    elif ident in CASCO and tecnica not in {"varredura", "varrida", "varrida_casco"}:
        particulas(s, x-lado*13*escala, y, -lado, p, cor, poeira=True, quantidade=9)
    elif ident in TECELOES:
        # Duas mandíbulas fecham de lados opostos no mesmo golpe.
        frente = x + lado*(18+12*p)*escala
        meio = y-14*escala
        abertura = (13-8*p)*escala
        for sinal in (-1,1):
            pontos = [(frente-lado*11*escala, meio+sinal*abertura),
                      (frente+lado*9*escala, meio+sinal*(abertura-1)),
                      (frente+lado*3*escala, meio+sinal*2*escala)]
            pygame.draw.polygon(s, cor, pontos)
            pygame.draw.aaline(s, OSSO, pontos[1], pontos[2])
    elif ident in SERPENTES:
        # O gancho claro acompanha os dentes no bote; verde só fica no veneno.
        frente = x + lado*25*escala
        meio = y-14*escala
        for n in range(2):
            px = frente+lado*n*6*escala
            pygame.draw.polygon(s, OSSO, [(px-lado*3*escala,meio-6*escala),
                                (px+lado*3*escala,meio-5*escala),
                                (px+lado*5*escala,meio+3*escala)])
        particulas(s,frente,meio,-lado,p,cor,quantidade=4)
    elif ident in CASCO:
        # Um golpe de chifre raspa a terra, soltando lascas pesadas na borda.
        frente = x+lado*(23+11*sin(pi*p))*escala
        pygame.draw.polygon(s, cor, [(x,y-4*escala),
                            (frente+lado*13*escala,y-21*escala),
                            (frente,y-8*escala),(x,y+1)])
        particulas(s, frente, y-2, lado, p, cor, poeira=True, quantidade=9)
    elif ident == "coruja":
        # As garras rasgam para baixo, enquanto fragmentos de pena ficam atrás.
        for n in range(3):
            px = x+lado*(16+7*n)*escala
            py = y-(25+5*n)*escala
            pygame.draw.polygon(s, OSSO if n==1 else cor,
                                [(px,py),(px+lado*9*escala,py+9*escala),
                                 (px+lado*5*escala,py+17*escala),
                                 (px+lado*5*escala,py+10*escala)])
        particulas(s,x-lado*8*escala,y-16*escala,-lado,p,cor,quantidade=7)
    elif ident == "vespa":
        frente = x+lado*(18+13*p)*escala
        meio = y-12*escala
        pygame.draw.polygon(s, cor, [(frente-lado*10*escala,meio-5*escala),
                            (frente+lado*14*escala,meio),
                            (frente-lado*7*escala,meio+5*escala),
                            (frente-lado*3*escala,meio)])
        particulas(s,x,y-12*escala,-lado,p,cor,quantidade=4)
    else:
        # A asa deixa duas curvas junto do corpo, já durante o rasante.
        for n in range(2):
            w, h = round((24+5*n)*escala), round((24+7*n)*escala)
            px = x+lado*(18+4*n)*escala
            py = y-(17+3*n)*escala
            a = -.9 if lado > 0 else pi-.9
            pygame.draw.arc(s, cor if n else OSSO, (round(px-w/2),round(py-h/2),w,h), a,a+1.8,2)
        particulas(s, x, y-10*escala, -lado, p, cor, quantidade=4)
