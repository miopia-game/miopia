"""A escolha do resgate explica o efeito e parte do trabalho em curso."""
from unittest.mock import patch

import pygame

from src import resgates, telas
from src.ensaios import ENSAIOS


def tecla(app, key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
    for evento in pygame.event.get():
        app.evento(evento)


def falar(app):
    tecla(app, pygame.K_e)
    app.atualizar(1/60)
    assert app.jogo.escolha_resgate == 'tila'
    for _ in app.fala_paginas[:-1]:
        app.atualizar(10)
        tecla(app, pygame.K_RETURN)
    app.atualizar(10)


def rotulos(app):
    with patch.object(telas, 'opcoes', wraps=telas.opcoes) as desenhar:
        app.desenhar()
    return desenhar.call_args.args[2]


def test_resgate_exibe_local_e_item_antes_de_escolher(app):
    indice = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == 'Resgate no berçário')
    app.comecar_ensaio(indice)
    falar(app)

    trilha, abrigo = rotulos(app)
    assert 'grade' in trilha and 'forquilha' in trilha and 'luz' in trilha
    assert '1 Pavio de pólen' in abrigo and '12 s' in abrigo
    assert app.jogo.sobreviventes['tila']['oficio'] == 'aguardando'
    assert app.jogo.bolsa.estoque['pavio'] == 0

    tecla(app, pygame.K_ESCAPE)
    assert app.jogo.sobreviventes['tila']['oficio'] == 'aguardando'
    assert app.jogo.dialogo is None


def test_retornar_a_tila_carrega_trabalho_salvo_e_nao_duplica_pavio(app):
    app.iniciar('historia')
    app.jogar()
    app.jogo.flags.update(('pino_ninho', 'porta_ninho', 'caruncho_vencido'))
    app.jogo.recolocar(resgates.POR_ID['tila'].ponto)
    falar(app)
    tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    assert app.jogo.bolsa.estoque['pavio'] == 1

    app.iniciar('historia', continuar=True)
    j = app.jogo
    j.recolocar(resgates.POR_ID['tila'].abrigo)
    falar(app)
    assert j.sobreviventes['tila'] == {'oficio': 'abrigo', 'premio': True}
    assert app.selecao == 1
    assert 'pavio já recebido' in rotulos(app)[1]
    tecla(app, pygame.K_RETURN)
    assert j.sobreviventes['tila']['oficio'] == 'abrigo'
    assert j.bolsa.estoque['pavio'] == 1

    falar(app)
    tecla(app, pygame.K_UP)
    tecla(app, pygame.K_RETURN)
    assert j.sobreviventes['tila']['oficio'] == 'trilha'
    j.recolocar((1640, 442))
    j.camera = 1200
    assert (1640, 415, 150) in resgates.fontes(j)
    assert j.bolsa.estoque['pavio'] == 1
