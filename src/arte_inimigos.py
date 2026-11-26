"""Poses ilustradas e efeitos locais filmados no momento do golpe."""
from functools import lru_cache
from math import pi, sin

from . import pygame_hd as pygame

from .ilustracao import original
from . import movimento_arte

AEREOS = {"morcego", "vespa", "asa-fendida", "coruja"}
SERPENTES = {"cobra", "cobra-dos-bercos"}
TECELOES = {"aranha", "tecela"}
TERRESTRES = {"aranha", "carabideo", "caruncho", "sombra"}
RITMO_ASAS = {"morcego": 4.6, "vespa": 8.3, "asa-fendida": 3.7, "coruja": 3.2}
PERCURSO = TERRESTRES | SERPENTES | {"casco-oco", "tecela"}
PASSO_RELATIVO = {"aranha": .44, "carabideo": .52, "caruncho": .44, "casco-oco": .40,
                  "sombra": .47, "cobra": .88, "cobra-dos-bercos": .98}
IMPACTOS_MOVEIS = {"rasteira", "mordida", "carga", "pique", "bote_caca", "retorno",
                   "investida_seiva", "varrida_casco", "varredura", "salto", "salto_alto"}

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
            return "coruja-impulso", movimento_arte.por_tempo(tempo, RITMO_ASAS[ident])
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
    if fase == "preparacao" and ident not in SERPENTES:
        return ident+"-arma", quadro_acao
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
    sy, angulo = 1., 0
    pose = "repouso"
    if fase in {"neutro", "passos"}:
        if ident in {"morcego", "asa-fendida", "vespa"}:
            # Pequeno deslocamento do tórax acompanha a força da batida.
            y += .021*h*sin(2*pi*RITMO_ASAS[ident]*tempo-.48)
    elif fase == "preparacao":
        pose = "preparacao"
        if ident in AEREOS:
            angulo = round((-12 if tecnica in {"mergulho", "garra", "queda"} else 9) * p)
        x -= lado * round(4*p)
    elif fase == "ataque":
        pose = "ataque"
        impulso = sin(pi * p)
        # A extensão já está na articulação pintada. Mantém crânio e quitina rígidos.
        if tecnica in {"mergulho", "garra", "queda"}:
            angulo = round(-10-11*impulso)
        elif tecnica in {"rasante", "rasante_baixo", "fagulha", "sino", "coro_investida"}:
            angulo = -6
        elif tecnica in DISPAROS:
            x -= lado * round(7*(1-p))
    elif fase == "recuo":
        pose = "preparacao" if ident in AEREOS or ident in TECELOES else "repouso"
        sy -= .035 * (1-p)
        angulo = 6 if ident in AEREOS else 0
    elif fase == "ferido":
        pose = "preparacao"
        angulo = 8
    elif fase == "brecha":
        pose = "preparacao" if ident in AEREOS else "repouso"
        angulo = 3
    if ident == "coruja":
        sy = 1.
    animacao = ciclo(ident, fase, tecnica, tempo, passos, w, p)
    h = round(h*sy)
    if animacao:
        faixa, quadro_atual = animacao
        return movimento_arte.desenhar(s, faixa, quadro_atual, x, y, (w,h), lado,
                                       centro=centro, angulo=angulo if centro else 0)
    imagem = quadro(ident, pose, w, h, lado, angulo)
    ancora = {"center" if centro else "midbottom": (round(x), round(y))}
    rect = imagem.get_rect(**ancora)
    s.blit(imagem, rect)
    return rect
