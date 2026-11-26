"""A veneziana permite ler o código e levar a descoberta a Véspera."""
import pygame

from src import corte_vertical
from src.visao import ponto_visivel
from tests.test_s20_raiz import ir, passo, tecla, cortar_no_poco, esperar_piso
from tests.test_travessia import Percurso


OESTE, LESTE, SINAIS = 224, 365, 328
FECHADA = 'veneziana_arquivo_fechada'
LIDOS = 'arquivo_sinais_lidos'
CONFIRMADOS = 'arquivo_sinais_confirmados'
ENTREGUES = 'arquivo_sinais_entregues'


def usar(app):
    tecla(app, pygame.K_e)
    passo(app)


def fechar_fala(app):
    for _ in app.fala_paginas:
        app.atualizar(10)
        tecla(app, pygame.K_RETURN)


def preparar_corte(app):
    app.iniciar('historia')
    app.jogar()
    corte_vertical.entrar(app.jogo, 'poco')
    corte_vertical.camera(app.jogo)


def test_veneziana_alterna_pelos_dois_lados_sem_gastar_luz(app):
    preparar_corte(app)
    j = app.jogo
    j.recolocar((OESTE, 1173))
    j.lume.energia = 0
    app.audio.mudo = True
    app.paisagem.brilho_mata = 3
    assert not any(o.id == 'sinais_arquivo' for o in j.objetos)
    for _ in range(5):
        assert j.proximo().id == 'veneziana_oeste'
        usar(app)
        assert FECHADA in j.cartografia
        assert any(o.id == 'sinais_arquivo' for o in j.objetos)
        assert ponto_visivel(j, (SINAIS, 1148))
        ir(app, LESTE)
        assert j.proximo().id == 'veneziana_leste'
        usar(app)
        assert FECHADA not in j.cartografia
        assert not any(o.id == 'sinais_arquivo' for o in j.objetos)
        ir(app, OESTE)
    assert j.lume.energia == 0 and j.lume.vida == 100
    assert not {LIDOS, CONFIRMADOS, ENTREGUES} & j.cartografia

    # A janela fechada permite voltar ao poço pelo caminho original.
    usar(app)
    p = Percurso()
    p.jogo, p.lume = j, j.lume
    p.ir(339)
    p.ir(474, pular=True)
    p.ir(690)
    for _ in range(4):
        p.tick(baixo=True, salto=True)
        p.esperar(60)
    p.ir(286)
    assert j.lume.rect.bottom == 1492 and FECHADA in j.cartografia


def test_luz_dos_sinais_pertence_ao_arquivo_e_nao_ao_poco(app):
    preparar_corte(app)
    j = app.jogo
    j.recolocar((OESTE, 1173))
    usar(app)
    j.lume.energia = 0
    assert ponto_visivel(j, (SINAIS, 1148))
    j.recolocar((328, 1253))
    assert not ponto_visivel(j, (SINAIS, 1148))


def test_ler_pelo_atalho_reabrir_e_entregar_pista_uma_vez(app):
    preparar_corte(app)
    j = app.jogo
    cortar_no_poco(app)
    ir(app, 138)
    usar(app)
    esperar_piso(app, 1173)
    ir(app, OESTE)
    usar(app)
    ir(app, SINAIS)
    usar(app)
    assert LIDOS in j.cartografia
    assert j.dialogo and 'dois traços curtos' in j.dialogo[1].lower()
    fechar_fala(app)
    ir(app, LESTE)
    usar(app)
    assert {LIDOS, CONFIRMADOS} <= j.cartografia and FECHADA not in j.cartografia

    # A entrega é na Véspera já existente. Isola o diálogo na plataforma real.
    j.entrar(0)
    vespera = next(o for o in j.objetos if o.id == 'vespera')
    j.recolocar((vespera.x, vespera.y))
    inicial = j.bolsa.estoque['casulo']
    usar(app)
    assert ENTREGUES in j.cartografia and 'Fio' in j.dialogo[1]
    assert j.bolsa.estoque['casulo'] == inicial+1
    assert 'pedido_entregue' not in j.flags
    fechar_fala(app)
    app.salvar_campanha()
    app.iniciar('historia', continuar=True)
    j = app.jogo
    j.recolocar((vespera.x, vespera.y))
    usar(app)
    assert ENTREGUES in j.cartografia and j.bolsa.estoque['casulo'] == inicial+1


def test_morte_e_retorno_preservam_a_pista_antes_de_reabrir(app):
    preparar_corte(app)
    j = app.jogo
    j.recolocar((OESTE, 1173))
    usar(app)
    ir(app, SINAIS)
    usar(app)
    fechar_fala(app)
    assert {LIDOS, FECHADA} <= j.cartografia and CONFIRMADOS not in j.cartografia

    j.lume.vida = 0
    passo(app)
    assert app.estado == 'morte'
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert app.estado == 'jogo' and j.lume.rect.midbottom == (286, 1492)
    app.iniciar('historia', continuar=True)
    assert {LIDOS, FECHADA} <= app.jogo.cartografia
    assert CONFIRMADOS not in app.jogo.cartografia
    cortar_no_poco(app)
    ir(app, 138)
    usar(app)
    esperar_piso(app, 1173)
    ir(app, OESTE)
    usar(app)
    assert CONFIRMADOS in app.jogo.cartografia
