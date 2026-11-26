"""Apresentação e pistas do começo do Bosque na cópia de experiência."""
from functools import lru_cache
from math import dist, sin

import pygame

from .avisos import pista_interacao
from .fases import Terreno
from .hud_reservas import desenhar as reservas
from .ilustracao import OSSO, PALIDO, dica_local, imagem, placa, texto
from .travessia_fagulha import (CHEGADA, CORTE_PRATICADO, CUSTO, FORA_DA_MARCA,
                                MorcegoDoGalho, na_borda)

FIM_HUD = 1350
FIM_TRILHA = 1650
BROTO = Terreno(pygame.Rect(248,306,64,9), "apoio")


def ativa(j):
    return (j.etapa == 0 and j.modo == "historia" and not j.em_vertical
            and not getattr(j, "campo_testes", False) and not hasattr(j, "sala_id"))


def em_cena(j):
    return ativa(j) and j.lume.rect.centerx < FIM_HUD


def intensidade(j):
    return max(0, min(1, (FIM_TRILHA-j.lume.rect.centerx)/300)) if ativa(j) else 0


@lru_cache(maxsize=2)
def fundo_sombrio(largura, altura):
    arte = imagem("bosque_figueira_tinta.png", largura, altura).copy()
    arte.fill((180,192,201), special_flags=pygame.BLEND_RGB_MULT)
    return arte


def fundo(s, j, cx, cy):
    opacidade = round(255 * intensidade(j))
    if not opacidade:
        return
    arte = fundo_sombrio(1850, 925)
    arte.set_alpha(opacidade)
    s.blit(arte, (-round(cx*.54), cy-196))


def cor_distante(j, nivel, normal):
    local = ((133,143,171),(174,184,215),(211,220,241),(253,253,255))[nivel]
    a = intensidade(j)
    return tuple(round(origem+(alvo-origem)*a) for origem, alvo in zip(normal,local))


def primeiro_plano(s,j,cx,cy):
    a = intensidade(j)
    if not a:
        return
    folhagem = (
        (8, 188, 111, "bosque_samambaias.png", False),
        (284, 138, 60, "bosque_sarcas.png", False),
        (614, 176, 76, "bosque_juncos.png", True),
        (986, 210, 108, "bosque_sarcas.png", True),
        (1320, 164, 82, "bosque_samambaias.png", True),
    )
    for mundo, largura, altura, nome, espelho in folhagem:
        x = mundo-round(cx*1.26)
        if -110 < x < 1070:
            planta = imagem(nome,largura,altura,espelho)
            planta.set_alpha(round(227*a))
            pe = cy+563+round(2*sin(j.tempo*1.4+mundo))
            s.blit(planta,planta.get_rect(midbottom=(x,pe)))


def broto_aceso(j):
    return em_cena(j) and any(v.raio(j.tempo) > dist((v.x,v.y), BROTO.rect.midtop)+15
                             for v in j.vestigios)


def pista_combate(j):
    lume = j.lume
    if CORTE_PRATICADO in j.tutorial or lume.arma.tipo or lume.impacto > 0 or lume.em_corda:
        return None
    area = lume.arma.area_corte_rapido(lume)
    for e in j.inimigos:
        if not isinstance(e, MorcegoDoGalho) or not e.ativo or not j.visivel(e.rect.center):
            continue
        if e.estado == "aviso":
            if (lume.chao and abs(e.rect.centerx - lume.rect.centerx) <= 175
                    and abs(e.rect.centery - lume.rect.centery) < 100):
                tecla, verbo = ("S", "Abaixar") if e.tecnica == "rasante" else ("A / D", "Sair do mergulho")
                return tecla, verbo, lume.rect.midtop
        elif e.estado not in ("poleiro", "investida") and area.colliderect(e.rect):
            return "J", "Cortar", lume.rect.midtop
    return None


def corte_praticavel(j):
    dica = pista_combate(j)
    return dica is not None and dica[0] == "J"


def pista(j):
    lume = j.lume
    ponto = lume.rect.midtop
    x = lume.rect.centerx
    if lume.em_corda or lume.arma.tipo or lume.impacto > 0:
        return None
    if na_borda(j):
        if j.aviso_t > 0 and j.aviso == FORA_DA_MARCA:
            return "", "Vire à direita", ponto
        if j.fagulha_ativa and j.fagulha_ativa.destino == CHEGADA:
            if j.fagulha_ativa.progresso(j.tempo) >= 1 and lume.chao:
                return "Espaço", "Cruzar", (x + 62, ponto[1])
            return None
        if j.fagulha_ativa:
            return "", "Espere a fagulha apagar", ponto
        if lume.energia < CUSTO:
            return "", "Orvalho e cipó no chão à direita", ponto
        if lume.face < 0:
            return "", "Vire para a marca", ponto
        return None
    combate = pista_combate(j)
    if combate:
        return combate

    interacao = j.interacao
    if interacao and ("reserva" not in interacao or min(lume.vida, lume.energia) < 100):
        return pista_interacao(j, interacao)

    if x < 105 and "praticado_primeiros_passos" not in j.tutorial:
        return "A / D", "Andar", ponto
    if x < 302 and "praticado_clarao_bosque" not in j.tutorial:
        return "K", "Clarear", ponto
    if BROTO.rect.left <= x <= BROTO.rect.right and abs(lume.rect.bottom - BROTO.rect.top) < 2:
        return "Espaço", "Saltar até a mochila", ponto
    if x < 313 and lume.chao:
        return "Espaço", "Saltar", ponto
    if 313 <= x < 438 and 350 <= lume.rect.bottom <= 377 and "encomenda_recolhida" not in j.flags:
        if broto_aceso(j):
            return "Espaço", "Saltar para o broto", ponto
        return "K", "Revelar o broto", ponto
    if 313 <= x < 475 and not lume.chao and lume.asa_disponivel and "praticado_salto_duplo" not in j.tutorial:
        return "Espaço", "Saltar de novo", ponto
    if 920 <= x < 1040 and j.ensino_id == "mapa" and j.ensino_ate > j.tempo and "praticado_mapa" not in j.tutorial:
        return "M", "Abrir mapa", ponto
    if j.aviso_t > 0 and j.aviso.startswith("Mochila de ervas recolhida."):
        return "", "Leve a mochila a Mimo", ponto
    return None


def hud(s, j):
    reservas(s, j)
    if j.tempo < 3.2:
        texto(s, "Bosque das Samambaias", 928, 24, 27, OSSO, "titulo", "right")
    if j.dialogo:
        return
    acao = pista(j)
    if acao:
        tecla, rotulo, (x, y) = acao
        dica_local(s, tecla, rotulo, (x - j.camera, y - j.camera_y))


def pausa(a,s):
    from .telas import opcoes

    s.blit(placa(960,540,75),(0,0))
    s.blit(placa(364,408,237),(26,66))
    texto(s,"Pausa",58,86,48,OSSO,"titulo")
    pygame.draw.line(s,(125,105,69),(58,157),(354,157))
    nomes=a.pausa_nomes.copy()
    if a.ensaio is not None:
        nomes[3:]=["Repetir o ensaio","Voltar ao campo de testes"]
    opcoes(a,s,nomes,50,179,322,40)
    rodape = "R · Repetir o ensaio" if a.ensaio is not None else f"Dificuldade · {a.jogo.dificuldade.capitalize()}"
    texto(s,rodape,58,420,13,PALIDO)
    if a.jogo.dificuldade_pendente:
        texto(s,f"{a.jogo.dificuldade_pendente.capitalize()} no próximo marco",58,442,12,PALIDO)
