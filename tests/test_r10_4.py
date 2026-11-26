"""Regressões do ataque vertical do carabídeo e do abrigo no Bosque."""
from collections import defaultdict

import pygame
import pytest

from src.combate import Inimigo, segmento_bloqueado
from src.ensaios import ENSAIOS
from src.fases import CHAO, Terreno
from src.taticas import Habitante
from src.travessia import Lume
from tests.auto_qa.test_gameplay_fuzz import quadro, toque


@pytest.mark.parametrize("classe", [Inimigo, Habitante])
def test_carabideo_trava_alvo_acima_e_da_tempo_de_sair(classe):
    piso = Terreno(pygame.Rect(0, CHAO, 800, 100), "chao")
    for esquiva in (False, True):
        besouro = classe("carabideo", 280, CHAO)
        lume = Lume(325, CHAO - 115)
        som = besouro.preparar(lume, (piso,))
        assert som == "aviso_carabideo_4"
        assert besouro.estado == "aviso"
        alvo = besouro.alvo.copy()
        if esquiva:
            lume.rect.centerx += 140
        dano = False
        for _ in range(180):
            _, acertou = besouro.update(1 / 120, lume, 150, False, (piso,))
            dano |= acertou
            assert besouro.alvo == alvo
            if besouro.estado == "recuo":
                break
        assert besouro.estado == "recuo"
        assert dano is not esquiva


@pytest.mark.parametrize("classe", [Inimigo, Habitante])
def test_carabideo_confere_se_o_corpo_cabe_no_arco(classe):
    besouro = classe("carabideo", 280, CHAO)
    lume = Lume(344, CHAO - 86)
    terrenos = (
        Terreno(pygame.Rect(0, CHAO, 800, 100), "chao"),
        Terreno(pygame.Rect(247, 350, 47, 15), "parede"),
    )
    assert not segmento_bloqueado(besouro.rect.center, lume.rect.center, terrenos)
    assert not besouro.preparar(lume, terrenos)
    assert besouro.estado == "patrulha"


def test_carabideo_da_aviso_e_acerta_lume_no_alto_pela_app(app):
    indice = next(i for i, ensaio in enumerate(ENSAIOS) if ensaio.nome == "Pulo entre paredes")
    app.comecar_ensaio(indice)
    jornada = app.jogo
    # A grade real do ramal, diretamente acima do carabídeo do Bosque.
    jornada.recolocar((3190, 307))
    jornada.lume.iframes = 0.
    teclas = defaultdict(bool)
    emitiu_aviso = False
    for _ in range(120):
        quadro(app, teclas)
        emitiu_aviso |= any(nome == "aviso_carabideo_4" for nome, _ in jornada.sons_espaciais)
        if jornada.lume.vida < 100:
            break
    assert emitiu_aviso
    assert jornada.lume.vida < 100


def test_cama_na_abertura_usa_reserva_e_mimo_continua_acessivel(app):
    teclas = defaultdict(bool)
    toque(app, teclas, pygame.K_RETURN)
    assert app.estado == "prologo"
    toque(app, teclas, pygame.K_ESCAPE)
    assert app.estado == "jogo"
    jornada = app.jogo

    toque(app, teclas, pygame.K_k)
    assert jornada.lume.energia < 100
    toque(app, teclas, pygame.K_e)
    assert jornada.lume.energia == 100
    assert "descanso_abrigo" in jornada.flags
    assert jornada.dialogo is None

    quadro(app, teclas, [(pygame.KEYDOWN, pygame.K_d)])
    for _ in range(85):
        quadro(app, teclas)
        if jornada.interacao == "Ouvir Mimo":
            break
    quadro(app, teclas, [(pygame.KEYUP, pygame.K_d)])
    toque(app, teclas, pygame.K_e)
    assert jornada.dialogo[0] == "Mimo"
