"""O mapa e o rastro de K apontam ao mesmo ninho usado no último chamado."""
import pygame
import pytest

from src.cartografia import alvo_local
from src.ensaios import ENSAIOS
from src.ultimo_chamado import alvo as ninho


@pytest.mark.parametrize('aliados', [0, 3])
def test_alvo_acompanha_os_tres_sinais_e_prioriza_o_climax(app, aliados):
    indice = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == 'Último chamado')
    app.comecar_ensaio(indice)
    j = app.jogo
    e = j.boss
    e.aliados = aliados
    j.sobreviventes = dict(list(j.sobreviventes.items())[:aliados])
    j.missao = 'resgates' if aliados == 0 else 'principal'

    for sinal in range(3):
        x, _ = ninho(e)
        assert alvo_local(j).x == x
        assert alvo_local(j).id == f'ninho_chamado_{sinal}'
        j.recolocar((x, e.chao))
        # A física/arena é real. Posicionamos Lume para verificar cada ninho.
        j.lume.pulso_cd = 0
        j.lume.energia = 0
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        for evento in pygame.event.get(): app.evento(evento)
        app.atualizar(1/60)
        assert not e.coro_gota and j.lume.energia >= 32
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_k))
        for evento in pygame.event.get(): app.evento(evento)
        app.atualizar(1/60)
        assert e.coro_sinais == sinal+1

    assert e.vencido and 'chefe' in j.flags
    assert alvo_local(j).id.startswith('ninho_chamado_') is False
