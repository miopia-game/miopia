"""O Campo de testes reabre cenas sem carregar o progresso da tentativa."""
import pygame
import pytest

from src.encontros import CLAREIRAS
from src.ensaios import ENSAIOS


VIGILIA = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == 'Clareira da Vigília')


def evento(app, tipo, **dados):
    pygame.event.post(pygame.event.Event(tipo, **dados))
    for e in pygame.event.get():
        app.evento(e)


def tecla(app, key):
    evento(app, pygame.KEYDOWN, key=key)


def abrir_vigilia(app):
    for _ in range(app.menu_nomes().index('Campo de testes')):
        tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    for _ in range(app.selecao - VIGILIA):
        tecla(app, pygame.K_UP)
    tecla(app, pygame.K_RETURN)
    assert app.ensaio == VIGILIA


def guardas(jogo):
    return [e for e in jogo.inimigos if e.origem[0] in CLAREIRAS[0].membros]


@pytest.mark.parametrize('com_mouse', [False, True])
def test_repetir_vigilia_da_pausa_carrega_o_estado_inicial(app, com_mouse):
    app.iniciar('historia')
    app.jogar()
    app.menu()
    campanha = app.mem.ler('campanha')
    abrir_vigilia(app)
    primeira = app.jogo
    inicio = primeira.salvar()
    posicao = primeira.lume.rect.midbottom
    inicial = [(e.origem, e.vida) for e in guardas(primeira)]
    assert len(inicial) == 3

    # Reproduz o estado deixado por um abate e consumo de recursos.
    abatido, ferido, _ = guardas(primeira)
    abatido.ativo = False
    abatido.vida = 0
    primeira.flags.add(f'inimigo_{abatido.origem[0]}')
    ferido.rect.x += 90
    ferido.vida -= 4
    primeira.bolsa.estoque['balsamo'] = 0
    primeira.lume.energia = 33
    primeira.tempo = 5
    app.mem.prefs['dificuldade'] = 'difícil'

    tecla(app, pygame.K_ESCAPE)
    tecla(app, pygame.K_r)
    tecla(app, pygame.K_RETURN)  # Cancelar preserva o andamento do ensaio.
    assert app.estado == 'pausa' and app.jogo is primeira
    assert not guardas(primeira)[0].ativo

    if com_mouse:
        app.desenhar()
        evento(app, pygame.MOUSEBUTTONDOWN, button=1, pos=app.alvos[3].center)
        app.desenhar()
        evento(app, pygame.MOUSEBUTTONDOWN, button=1, pos=app.alvos[1].center)
    else:
        tecla(app, pygame.K_r)
        tecla(app, pygame.K_DOWN)
        tecla(app, pygame.K_RETURN)

    atual = app.jogo
    assert app.estado == 'jogo' and app.ensaio == VIGILIA
    assert all(e.ativo and e.rect.midbottom == e.origem for e in guardas(atual))
    assert [(e.origem, e.vida) for e in guardas(atual)] == inicial
    assert atual.lume.rect.midbottom == posicao
    assert atual.salvar() == inicio and atual.tempo == 0
    assert atual.dificuldade == primeira.dificuldade
    assert app.mem.ler('campanha') == campanha


def test_sair_da_morte_retorna_ao_ensaio_selecionado(app):
    abrir_vigilia(app)
    app.jogo.lume.vida = 0
    app.atualizar(1/60)
    assert app.estado == 'morte'
    app.atualizar(.4)
    tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    assert app.estado == 'ensaios' and app.selecao == VIGILIA
    assert app.mem.ler('campanha') is None

    tecla(app, pygame.K_RETURN)
    assert app.estado == 'jogo' and app.ensaio == VIGILIA
    assert all(e.ativo and e.vida == e.max_vida for e in guardas(app.jogo))
