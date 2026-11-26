"""As faixas avisadas pela Coruja governam os golpes do Último Chamado."""
import pygame
import pytest

from src.ensaios import ENSAIOS
from src.ultimo_chamado import alvo, perto
from tests.test_s20_raiz import passo, tecla


def iniciar_chamado(app, aliados=0, dificuldade="normal"):
    indice = next(i for i, ensaio in enumerate(ENSAIOS) if ensaio.nome == "Último chamado")
    app.comecar_ensaio(indice, dificuldade)
    j = app.jogo
    j.sobreviventes = dict(list(j.sobreviventes.items())[:aliados])
    j.boss.aliados = aliados
    return j, j.boss


def devolver(app, e):
    j = app.jogo
    j.recolocar((alvo(e)[0], e.chao))
    tecla(app, pygame.K_e)
    passo(app)
    j.lume.pulso_cd = 0
    tecla(app, pygame.K_k)
    passo(app)


def esperar_aviso(app, e):
    for _ in range(180):
        passo(app)
        if e.estado == "coro_aviso":
            return
    raise AssertionError("A Coruja não anunciou o golpe")


@pytest.mark.parametrize("esquiva", [False, True])
def test_queda_de_penas_mantem_o_alvo_e_distingue_esquiva_de_contato(app, esquiva):
    j, e = iniciar_chamado(app)
    devolver(app, e)
    j.recolocar((4020, e.chao))
    esperar_aviso(app, e)
    assert e.som_aviso == "coruja_penas"
    assert e.coro_faixas == (4020,)
    vida = j.lume.vida
    for _ in range(100):
        mover = esquiva and j.lume.rect.centerx < 4110
        passo(app, pygame.K_d) if mover else passo(app)
        if e.estado in ("coro_aviso", "coro_queda"):
            assert e.coro_faixas == (4020,)
        else:
            break
    assert e.estado == "coro_busca" and not e.coro_faixas
    assert (j.lume.vida == vida) == esquiva


def test_ultimo_ninho_anuncia_duas_faixas_e_limpa_ao_responder(app):
    j, e = iniciar_chamado(app)
    devolver(app, e)
    devolver(app, e)
    j.recolocar((3890, e.chao))
    esperar_aviso(app, e)
    assert len(e.coro_faixas) == 2 and e.coro_faixas[0] == 3890
    assert e.coro_faixas[1] > 3890
    devolver(app, e)
    assert e.vencido and not e.coro_faixas and "chefe" in j.flags


@pytest.mark.parametrize("aliados,dificuldade", [(0, "normal"), (3, "normal"), (0, "difícil")])
def test_os_tres_ninhos_sao_alcancaveis_pela_app(app, aliados, dificuldade):
    from tests.test_s31_historia import CampanhaPelaApp, resolver_arena

    j, e = iniciar_chamado(app, aliados, dificuldade)
    p = CampanhaPelaApp(app)
    resolver_arena(p)
    assert e.vencido and e.coro_sinais == 3 and j.lume.vida > 0


def test_pausa_morte_e_retorno_esvaziam_o_golpe_da_tentativa(app):
    j, e = iniciar_chamado(app, 3)
    devolver(app, e)
    j.recolocar((4020, e.chao))
    esperar_aviso(app, e)
    marcas = e.coro_faixas
    tempo = e.tempo
    tecla(app, pygame.K_ESCAPE)
    app.atualizar(.75)
    assert app.estado == "pausa" and e.coro_faixas == marcas and e.tempo == tempo
    tecla(app, pygame.K_ESCAPE)
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.5)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and app.jogo is not j
    assert not app.jogo.boss.coro_faixas and app.jogo.boss.coro_sinais == 0


def test_um_ou_dois_resgates_ja_dao_tempo_e_alcance(app):
    duracoes = []
    for aliados in range(4):
        j, e = iniciar_chamado(app, aliados)
        x, y = alvo(e)
        borda = pygame.FRect(x+95, y-10, 20, 20)
        assert perto(e, borda) == (aliados >= 2)
        esperar_aviso(app, e)
        assert not e.coro_faixas and e.som_aviso == "coruja_eco"
        duracoes.append(e.tempo)
    assert all(a < b for a, b in zip(duracoes, duracoes[1:]))
