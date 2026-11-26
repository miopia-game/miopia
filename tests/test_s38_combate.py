"""A esquiva, a carga e os itens oferecem respostas diferentes no S38."""
import pygame
import pytest

from src import encontros
from src.ensaios import ENSAIOS
from src.fases import CHAO
from src.narrativa import Bolsa
from tests.test_s20_raiz import passo, tecla
from tests.test_s35_nicho import FUNDO, abrir_ensaio


def aguardar(app, condicao, quadros=140, seguradas=()):
    for _ in range(quadros):
        passo(app, *seguradas)
        if condicao():
            return
    raise AssertionError("O estado esperado não ocorreu no combate.")


@pytest.mark.parametrize("carregado,esperado", [(False, .5), (True, 2.)])
def test_corte_em_escamas_fechadas_respeita_a_carga(app, carregado, esperado):
    j, cobra = abrir_ensaio(app)
    j.recolocar((1453, FUNDO))
    j.lume.face = -1
    antes = cobra.vida
    tecla(app, pygame.K_j)
    aguardar(app, lambda: cobra.vida < antes, 20, (pygame.K_LCTRL,) if carregado else ())
    assert antes-cobra.vida == pytest.approx(esperado)
    assert j.lume.energia == pytest.approx(92.35 if carregado else 100.)


def test_salto_sobre_rasteira_abre_brecha_para_contra_ataque(app):
    j, cobra = abrir_ensaio(app)
    j.recolocar((1455, FUNDO))
    cobra.plano = [0]  # Isola a rasteira. O aviso e a investida usam a simulação real.
    aguardar(app, lambda: cobra.estado == "aviso")
    assert cobra.acao_atual == "rasteira"
    aguardar(app, lambda: cobra.t <= .16)
    tecla(app, pygame.K_SPACE)
    aguardar(app, lambda: cobra.estado == "investida", seguradas=(pygame.K_SPACE,))
    aguardar(app, lambda: cobra.estado == "recuo")
    assert j.lume.vida == 100 and cobra.exposta
    assert cobra.t >= .7
    tecla(app, pygame.K_F10)
    app.desenhar()
    x = round(cobra.rect.centerx-j.camera)
    y = round(cobra.rect.top-22)-round(j.camera_y)
    assert app.tela.get_at((x, y-5))[:3] == (168, 231, 192)
    segurada = pygame.K_d if cobra.rect.centerx > j.lume.rect.centerx else pygame.K_a
    aguardar(app, lambda: abs(cobra.rect.centerx-j.lume.rect.centerx) <= 68, 30, (segurada,))
    antes = cobra.vida
    tecla(app, pygame.K_j)
    aguardar(app, lambda: cobra.vida < antes, 12)
    assert antes-cobra.vida == pytest.approx(2.)
    assert j.lume.energia == 100


def dupla(app):
    indice = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == "Patrulha em dupla")
    app.comecar_ensaio(indice)
    j = app.jogo
    grupo = [e for e in j.inimigos if e.origem[0] in encontros.CLAREIRAS[0].membros]
    return j, grupo


@pytest.mark.parametrize("carregado", [False, True])
def test_dupla_aceita_as_duas_armas_e_so_a_carga_interrompe_o_aviso(app, carregado):
    j, grupo = dupla(app)
    assert len(grupo) == 2
    assert {e.tipo for e in grupo} == {"morcego", "aranha"}
    tecla(app, pygame.K_v)
    assert j.lume.arma.equipamento == "agulha"
    aranha = next(e for e in grupo if e.tipo == "aranha")
    j.recolocar((1575, CHAO))
    aranha.plano = [3]
    aguardar(app, lambda: aranha.estado == "aviso")
    antes = aranha.vida
    tecla(app, pygame.K_j)
    aguardar(app, lambda: aranha.vida < antes, 18, (pygame.K_LCTRL,) if carregado else ())
    assert (aranha.estado == "atordoado") is carregado
    assert antes-aranha.vida == (4 if carregado else 2)
    assert j.lume.energia == pytest.approx(92.35 if carregado else 100.)


def equipar(app, item):
    for _ in app.jogo.bolsa.estoque:
        if app.jogo.bolsa.equipado == item:
            return
        tecla(app, pygame.K_q)
    raise AssertionError(f"Item {item} indisponível no ensaio.")


def test_polen_serve_para_asa_e_preserva_segunda_carga_sem_novo_alvo(app):
    j, grupo = dupla(app)
    morcego = next(e for e in grupo if e.tipo == "morcego")
    j.recolocar((1500, CHAO))
    j.lume.face = 1
    equipar(app, "polen")
    tecla(app, pygame.K_f)
    assert j.bolsa.estoque["polen"] == 1 and morcego.lentidao == 6.
    tecla(app, pygame.K_f)
    assert j.bolsa.estoque["polen"] == 1
    assert morcego.lentidao == 6. and "6 s" in j.bolsa.item.descricao


@pytest.mark.parametrize("agulha", [False, True])
def test_agulha_alcanca_escamas_alem_do_espinho(app, agulha):
    j, cobra = abrir_ensaio(app)
    j.recolocar((1515, FUNDO))
    j.lume.face = -1
    if agulha:
        tecla(app, pygame.K_v)
    antes = cobra.vida
    tecla(app, pygame.K_j)
    for _ in range(15):
        passo(app)
    assert antes-cobra.vida == int(agulha)
    assert j.lume.energia == 100.


def test_pavio_indica_tempo_e_mantem_o_clarao_mais_longo(app):
    j, _ = dupla(app)
    j.lume.energia = 80.
    alcance = j.raio
    equipar(app, "pavio")
    tecla(app, pygame.K_f)
    assert j.bolsa.efeitos_ativos(j.tempo) == ["Pavio 12 s"]
    assert j.raio == pytest.approx(alcance+65.)
    tecla(app, pygame.K_k)
    passo(app)
    assert j.lume.energia == 58. and j.vestigios[-1].duracao == 9.
    tempo = j.tempo
    bolsa = Bolsa.carregar(j.salvar()["bolsa"], tempo)
    assert bolsa.efeitos_ativos(tempo+2) == ["Pavio 10 s"]
    assert not bolsa.efeitos_ativos(tempo+12.)


def test_polen_da_bolsa_desfaz_so_o_leque_sem_gastar_brilho(app):
    j, cobra = abrir_ensaio(app)
    j.recolocar((1560, FUNDO))
    j.lume.face = -1
    cobra.vida = cobra.max_vida/2
    aguardar(app, lambda: len(cobra.projeteis) == 2)
    equipar(app, "polen")
    tecla(app, pygame.K_f)
    assert not cobra.projeteis and j.lume.energia == 100.
    assert j.bolsa.estoque["polen"] == 1
    assert j.aviso == "Pólen · 2 projéteis desfeitos"


def test_casulo_consumido_em_um_bote_avisa_no_hud(app):
    j, cobra = abrir_ensaio(app)
    j.recolocar((1448, FUNDO))
    cobra.plano = [3]
    equipar(app, "casulo")
    tecla(app, pygame.K_f)
    assert j.bolsa.efeitos_ativos(j.tempo) == ["Casulo armado"]
    aguardar(app, lambda: cobra.estado == "aviso")
    aguardar(app, lambda: not j.bolsa.escudo)
    assert j.lume.vida == 100. and j.bolsa.estoque["casulo"] == 0
    assert not j.bolsa.efeitos_ativos(j.tempo)


def test_aviso_da_sombra_nao_revela_a_fenda_antes_do_golpe(app):
    from src.arte_combate import projeteis
    from src.taticas import Habitante
    from src.travessia import Lume

    sombra = Habitante("sombra", 190, 170)
    lume = Lume(200, 170)
    sombra.estado, sombra.t = "aviso", .32
    sombra.tecnica = "fenda"
    s = pygame.Surface((560, 200), pygame.SRCALPHA)
    marcas = []
    for alvo_x in (320, 490):
        s.fill((0, 0, 0, 0))
        sombra.alvo.update(alvo_x, 170)
        projeteis(s, sombra, 0, lume, 150)
        marcas.append(pygame.image.tobytes(s, "RGBA"))
        assert s.get_bounding_rect().right < 208
    assert marcas[0] == marcas[1]

    sombra.estado, sombra.duracao, sombra.t = "investida", .24, .12
    s.fill((0, 0, 0, 0))
    projeteis(s, sombra, 0, lume, 150)
    assert s.get_bounding_rect().right > 490
