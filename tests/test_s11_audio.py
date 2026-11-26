"""A trilha da revisão acadêmica usa o mixer real e a App normal."""
import pygame
import pytest

from src.chefes import Encontro
from src.ensaios import ENSAIOS
from src.fases import ARENA, CHAO


TRILHAS = (
    "menu", "historia", "bosque", "corrego", "taquaral", "gruta", "jardim", "retorno",
    "chefe_0", "chefe_1", "chefe_2", "chefe_3", "chefe_final", "chefe_caruncho",
)


@pytest.mark.parametrize("tema", TRILHAS)
def test_trilha_nova_faz_streaming_no_mixer(app, tema):
    faixa = app.audio.trilhas.get(tema)
    assert faixa is not None and faixa.suffix == ".ogg"
    if tema == app.audio.atual:
        app.musica("creditos")
    app.musica(tema)
    assert app.audio.atual == tema
    assert pygame.mixer.music.get_busy()


def test_minichefe_tem_trilha_propria_do_inicio_ao_fim(app):
    indice = next(i for i, ensaio in enumerate(ENSAIOS) if ensaio.nome == "Caruncho do Viveiro")
    app.comecar_ensaio(indice)
    app.jogo.recolocar((1870,1282))
    caruncho = app.jogo.minichefe
    assert caruncho is not None
    app.mix(1/60)
    assert app.audio.atual == "chefe_caruncho"
    caruncho.ativo = False
    app.mix(1/60)
    assert app.audio.atual == "bosque"


def test_retomar_boss_nao_recarrega_musica(app, monkeypatch):
    app.iniciar("historia")
    app.jogo.boss = Encontro(0, ARENA, CHAO)
    app.jogar()
    app.mix(1/60)
    assert app.audio.atual == "chefe_0"
    original = pygame.mixer.music.load
    carregamentos = []

    def observar(caminho):
        carregamentos.append(caminho)
        return original(caminho)

    monkeypatch.setattr(pygame.mixer.music, "load", observar)
    for tecla in (pygame.K_p, pygame.K_p):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=tecla))
        for evento in pygame.event.get():
            app.evento(evento)
        app.mix(1/60)
    assert app.estado == "jogo" and app.audio.atual == "chefe_0"
    assert not carregamentos


def test_guardioes_biomas_e_fase_final_trocam_de_faixa(app):
    app.iniciar("historia")
    for i, bioma in enumerate(("bosque", "corrego", "taquaral", "gruta")):
        j = app.jogo
        j.entrar(i)
        app.jogar()
        assert app.audio.atual == bioma
        j.boss = Encontro(i, ARENA, CHAO)
        app.mix(1/60)
        assert app.audio.atual == f"chefe_{i}"
        if i == 3:
            j.boss.coro_iniciado = True
            app.mix(1/60)
            assert app.audio.atual == "chefe_final"
        j.boss.vencido = True
        app.mix(1/60)
        assert app.audio.atual == bioma
