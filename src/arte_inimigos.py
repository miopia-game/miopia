"""Poses ilustradas e efeitos locais filmados no momento do golpe."""
from functools import lru_cache

from . import pygame_hd as pygame

from .ilustracao import original
from . import movimento_arte

AEREOS = {"morcego", "vespa", "asa-fendida", "coruja"}
SERPENTES = {"cobra", "cobra-dos-bercos"}
TERRESTRES = {"aranha", "carabideo", "caruncho", "sombra"}
RITMO_ASAS = {"morcego": 2.8, "vespa": 3.6, "asa-fendida": 2.15, "coruja": 1.65}
PASSO_RELATIVO = {"aranha": .44, "carabideo": .52, "caruncho": .44, "casco-oco": .40,
                  "sombra": .47, "cobra": .88, "cobra-dos-bercos": .98}
# A segunda família usa um gesto próprio. A técnica vem da mesma IA que
# posiciona o projétil ou resolve o contato.
ESPECIAIS = {
    "morcego": {"eco"},
    "vespa": {"mergulho", "queda", "rasante", "rasante_baixo"},
    "aranha": {"salto", "salto_alto", "pique", "mordida", "rasteira"},
    "sombra": {"orbe", "eco"},
    "carabideo": {"onda", "onda_dupla", "salto"},
    "caruncho": {"onda", "onda_dupla", "salto"},
    "cobra": {"veneno", "ferrao"},
    "cobra-dos-bercos": {"veneno", "ferrao"},
    "tecela": {"chama_ninhada"},
    "casco-oco": {"salto", "salto_casco", "varrida_casco", "varredura"},
    "coruja": {"penas", "sino"},
}


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


def ciclo(ident, fase, tecnica, tempo, passos, w, progresso, duracao=0.):
    p = fracao(progresso)
    folha = ident + ("-especial" if tecnica in ESPECIAIS.get(ident, ()) else "-golpe")
    if fase == "chamado":
        return folha, round(15*p)
    if fase == "preparacao":
        return folha, round(4*p)
    if fase == "ataque":
        # Uma investida longa volta à batida ou passada após o gesto de contato.
        if duracao > .75 and p*duracao > .48 and (ident in AEREOS or ident == "casco-oco"):
            fase = "neutro"
        else:
            contato = min(1., p*duracao/.48) if duracao > .75 else p
            return folha, 5+round(6*contato)
    if fase == "recuo" and not (ident == "tecela" and tecnica == "queda"):
        return folha, 12+round(3*p)
    if fase in {"brecha", "ferido"}:
        return folha, 13
    if fase == "repouso":
        if ident in {"morcego", "asa-fendida"}:
            return ident+"-repouso", movimento_arte.por_tempo(tempo,.65)
        return ident, 0
    if ident in AEREOS:
        return ident, movimento_arte.por_tempo(tempo, RITMO_ASAS[ident])
    if ident == "tecela":
        return ident, movimento_arte.por_tempo(tempo,1.08)
    if passos:
        comprimento = w * PASSO_RELATIVO[ident]
        if ident in SERPENTES:
            return ident, movimento_arte.por_distancia(passos.distancia, comprimento)
        return ident, passos.quadro_passada(comprimento)
    return ident, 0


def corpo(s, ident, fase, x, y, medida, lado, tempo, p, tecnica="", *, centro=False, passos=None, duracao=0.):
    folha, indice = ciclo(ident, fase, tecnica, tempo, passos, medida[0], p, duracao)
    return movimento_arte.desenhar(s, folha, indice, x, y, medida, lado, centro=centro)
