"""A Agulha opcional da campanha usa o perfil medido na Oficina."""
import pygame
import pytest

from src.fases import CHAO
from src.travessia import Comando, Jornada


def tecla(app, key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
    for evento in pygame.event.get():
        app.evento(evento)


def test_entrega_a_mimo_libera_a_troca_e_save_preserva_a_agulha(app):
    app.iniciar('historia')
    app.jogar()
    j = app.jogo
    tecla(app, pygame.K_v)
    assert j.lume.arma.equipamento == 'espinho'

    # Isola a entrega após a rota opcional do Caruncho.
    j.flags.update(('caruncho_vencido', 'ambar_ninho'))
    mimo = next(o for o in j.objetos if o.id == 'abrigo_npc')
    j.recolocar((mimo.x, mimo.y))
    tecla(app, pygame.K_e)
    app.atualizar(1/60)
    assert 'pedido_raizes_entregue' in j.flags
    assert j.bolsa.capacidade_balsamo == 3
    assert 'agulha de taquara' in j.dialogo[1].lower()
    for _ in app.fala_paginas:
        app.atualizar(10)
        tecla(app, pygame.K_RETURN)

    tecla(app, pygame.K_v)
    assert j.lume.arma.equipamento == 'agulha'
    app.iniciar('historia', continuar=True)
    j = app.jogo
    assert j.lume.arma.equipamento == 'agulha'
    j.lume.vida = 0
    app.atualizar(1/60)
    assert app.estado == 'morte'
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert app.estado == 'jogo' and j.lume.arma.equipamento == 'agulha'

    j.entrar(1)
    assert j.lume.arma.equipamento == 'agulha'
    tecla(app, pygame.K_v)
    assert j.lume.arma.equipamento == 'espinho'


def test_save_antigo_libera_a_escolha_so_com_entrega_no_historico():
    j = Jornada(etapa=1)
    j.historico[(0, 0)] = {'pedido_raizes_entregue'}
    dados = j.salvar()
    dados.pop('arma', None)
    novo = Jornada.carregar(dados)
    assert novo.lume.arma.equipamento == 'espinho'
    assert novo.trocar_arma() and novo.lume.arma.equipamento == 'agulha'

    bloqueado = Jornada().salvar()
    bloqueado['arma'] = 'agulha'
    novo = Jornada.carregar(bloqueado)
    assert novo.lume.arma.equipamento == 'espinho' and not novo.trocar_arma()


@pytest.mark.parametrize('agulha,largura,recuperacao', [(False, 84, .24), (True, 118, .35)])
def test_corte_de_luz_tem_alcance_e_tempo_distintos_com_o_mesmo_custo(agulha, largura, recuperacao):
    j = Jornada()
    j.flags.add('pedido_raizes_entregue')
    if agulha:
        assert j.trocar_arma()
    j.recolocar((95, CHAO))
    j.update(.01, Comando(golpe=True, carregado=True))
    assert j.lume.energia == 92
    assert j.lume.arma.perfil.total == recuperacao
    assert not j.trocar_arma()
    for _ in range(10):
        j.update(.01)
    assert j.lume.arma.area(j.lume).width == largura
