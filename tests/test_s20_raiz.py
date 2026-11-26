"""A raiz liga duas alturas do Corte por uma rota física persistente."""
from collections import defaultdict

import pygame

from src import corte_vertical
from src.descoberta import conhecida
from src.travessia import Jornada
from tests import test_corte_vertical


FLAG = 'raiz_duas_bocas'
BOCA_X = 138
ARQUIVO_Y = 1173
POCO_Y = 1492


def tecla(app, key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
    for evento in pygame.event.get():
        app.evento(evento)


def passo(app, *seguradas, dt=1/60):
    teclado = defaultdict(bool, {k: True for k in seguradas})
    app.atualizar(dt, presso=teclado)


def ir(app, x):
    for _ in range(180):
        dx = x-app.jogo.lume.rect.centerx
        if abs(dx) < 4:
            passo(app)
            return
        tecla_mover = pygame.K_d if dx > 0 else pygame.K_a
        passo(app, tecla_mover)
    raise AssertionError(f'Lume não alcançou x={x}')


def esperar_piso(app, y):
    for _ in range(180):
        passo(app)
        lume = app.jogo.lume
        if lume.chao and lume.rect.bottom == y:
            return
    raise AssertionError(f'Lume não alcançou o piso y={y}')


def preparar_poco(app):
    app.iniciar('historia')
    app.jogar()
    corte_vertical.entrar(app.jogo, 'poco')


def cortar_no_poco(app):
    ir(app, 176)
    assert app.jogo.lume.face == -1
    tecla(app, pygame.K_j)
    for _ in range(28):
        passo(app)
    assert FLAG in app.jogo.cartografia


def test_chegar_pelo_arquivo_mostra_a_trava_e_preserva_a_trilha_antiga():
    corte = test_corte_vertical.CorteTest()
    p = corte.entrar()
    p.ir(690)
    corte.descer(p, 2)
    p.ir(BOCA_X)
    assert p.lume.rect.bottom == ARQUIVO_Y
    assert p.jogo.proximo().id == 'raiz_boca_alta'
    p.usar()
    assert 'por baixo' in p.jogo.aviso
    p.tick(baixo=True, salto=True)
    p.esperar(60)
    assert p.lume.rect.bottom == ARQUIVO_Y and FLAG not in p.jogo.cartografia
    p.ir(339)
    p.ir(474, pular=True)
    p.ir(690)
    corte.descer(p, 4)
    p.ir(286)
    assert p.lume.rect.bottom == POCO_Y and FLAG not in p.jogo.cartografia


def test_corte_sem_brilho_abre_atualiza_o_save_e_permite_os_dois_sentidos(app):
    preparar_poco(app)
    j = app.jogo
    j.lume.energia = 0
    cortar_no_poco(app)
    assert j.lume.vida == 100 and j.lume.energia == 0
    assert not conhecida(j, BOCA_X, ARQUIVO_Y-10)
    assert any(t.descida and t.rect.collidepoint(BOCA_X, ARQUIVO_Y) for t in j.solidos)
    assert sum(t == 'O reparo de Fio' for t, _ in j.diario) == 1
    tecla(app, pygame.K_j)
    for _ in range(25): passo(app)
    assert sum(t == 'O reparo de Fio' for t, _ in j.diario) == 1

    # Recarrega no marco do poço, como numa História normal.
    app.salvar_campanha()
    app.iniciar('historia', continuar=True)
    j = app.jogo
    assert FLAG in j.cartografia and j.lume.rect.midbottom == (286, POCO_Y)
    ir(app, BOCA_X)
    tecla(app, pygame.K_e)
    passo(app)
    assert j.lume.em_corda and ARQUIVO_Y < j.lume.rect.bottom < POCO_Y
    esperar_piso(app, ARQUIVO_Y)
    assert j.em_vertical and j.setor_vertical == 'Arquivo da Casca'

    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_s, pygame.K_SPACE)
    assert j.lume.rect.bottom > ARQUIVO_Y
    esperar_piso(app, POCO_Y)
    assert j.em_vertical and j.setor_vertical == 'Poço da Seiva'


def test_morte_no_cipo_retorna_ao_marco_e_preserva_a_abertura(app):
    preparar_poco(app)
    j = app.jogo
    cortar_no_poco(app)
    ir(app, BOCA_X)
    tecla(app, pygame.K_e)
    passo(app, dt=.09)
    assert j.lume.em_corda and j.lume.rect.bottom < POCO_Y
    j.lume.vida = 0
    passo(app)
    assert app.estado == 'morte'
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert app.estado == 'jogo' and not j.lume.em_corda
    assert j.lume.rect.midbottom == (286, POCO_Y)
    assert FLAG in j.cartografia and FLAG in Jornada.carregar(j.salvar()).cartografia
