"""Percurso, luz e chegada usam o mesmo disparo simulado pela campanha."""
import pygame
import pytest

from src.combate import segmento_bloqueado
from src.desvios_fagulha import DESVIOS
from src.fases import Terreno
from src.travessia import Comando, Jornada
from src.travessia_fagulha import CHEGADA, CUSTO, DURACAO, Fagulha, prever_marca
from src.visao import fontes


@pytest.mark.parametrize("destino", [(300., 140.), (300., 187.), (20., 97.)])
def test_disparo_segue_a_linha_da_mira_ate_o_pouso(destino):
    origem = pygame.Vector2(110., 140.)
    f = Fagulha(8., tuple(origem), destino)
    direcao = pygame.Vector2(destino) - origem
    assert f.posicao(7.) == tuple(origem)
    anterior = 0.
    for n in range(1, 11):
        pos = pygame.Vector2(f.posicao(8. + n*f.duracao_voo/10))
        deslocamento = pos-origem
        assert abs(deslocamento.cross(direcao)) < .001
        assert anterior < deslocamento.length() <= direcao.length() + .001
        anterior = deslocamento.length()
    assert f.posicao(f.pouso_em) == f.posicao(12.) == destino
    assert f.progresso(f.pouso_em) == 1.
    assert f.restante(f.pouso_em + DURACAO) == 0.


def test_origem_luz_movimento_e_som_espacial_coincidem():
    j = Jornada()
    j.recolocar((799, 248))
    j.lume.face = 1
    antes = j.lume.energia
    j.update(1/60, Comando(fagulha=True))
    f = j.fagulha_ativa
    assert f.destino == CHEGADA and f.origem[0] < j.lume.rect.centerx
    assert j.lume.energia == antes-CUSTO
    assert .18 < f.duracao_voo < .28
    assert Fagulha(0., (0.,0.), (85.,0.)).duracao_voo < f.duracao_voo
    pousos = []
    for dt in (.102, .134, .15, .15):
        j.update(dt)
        pontos = [x for x in j.sons_espaciais if x[0] == "pouso_fagulha"]
        if pontos:
            assert j.tempo >= f.pouso_em
        pousos.extend(pontos)
        assert (*f.posicao(j.tempo),f.raio(j.tempo)) in fontes(j)
        if j.tempo < f.pouso_em:
            assert f.raio(j.tempo) >= 90 and f.posicao(j.tempo) != CHEGADA
    assert pousos == [("pouso_fagulha", CHEGADA[0])]


@pytest.mark.parametrize("etapa,desvio", DESVIOS.items())
def test_marca_aceita_um_voo_reto_de_toda_a_borda_do_desvio(etapa, desvio):
    j = Jornada(etapa=etapa)
    j.flags.add(desvio.requisito)
    x, y = desvio.partida
    for partida in range(x-57, x+58):
        j.recolocar((partida, y))
        j.lume.face = 1
        j.lume.energia = 100.
        j.fagulha = None
        j.update(1/60, Comando(fagulha=True))
        f = j.fagulha_ativa
        assert f and f.destino == desvio.marca, partida
        assert not segmento_bloqueado(f.origem, f.destino, j.solidos)


@pytest.mark.parametrize("altura,tipo,bloqueado", [(220,"teto",True), (182,"teto",False),
                                                  (220,"plataforma",False)])
def test_previsao_e_disparo_respeitam_o_mesmo_obstaculo(monkeypatch, altura, tipo, bloqueado):
    j = Jornada()
    j.recolocar((799, 248))
    j.lume.face = 1
    obstaculo = Terreno(pygame.Rect(908, altura, 9, 22), tipo)
    solidos = [*j.solidos, obstaculo]
    monkeypatch.setattr(Jornada, "solidos", property(lambda _: solidos))
    antes = j.lume.energia
    assert prever_marca(j) == (None if bloqueado else CHEGADA)
    j.update(1/60, Comando(fagulha=True))
    if bloqueado:
        assert j.fagulha_ativa is None and j.lume.energia == antes
        assert "parede" in j.aviso
    else:
        assert j.fagulha_ativa.destino == CHEGADA and j.lume.energia == antes-CUSTO
