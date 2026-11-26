"""Janelas e ataques dos guardiões continuam legíveis em cada dificuldade."""
import pygame

from src.chefes import Encontro
from src.fases import CHAO
from src.ensaios import ENSAIOS
from tests.test_s20_raiz import passo, tecla


def test_guardioes_exigem_mais_preparo_conforme_a_dificuldade():
    for indice in range(4):
        facil = Encontro(indice, 0, CHAO, dificuldade="fácil")
        normal = Encontro(indice, 0, CHAO)
        dificil = Encontro(indice, 0, CHAO, dificuldade="difícil")
        assert facil.vida_max == normal.vida_max == dificil.vida_max
        assert (facil.meta, normal.meta, dificil.meta) == (2, 3, 3)
        for e in (facil, normal, dificil):
            e._abrir(3., [])
        assert facil.tempo > normal.tempo > dificil.tempo
        jogador = pygame.FRect(20, CHAO-42, 24, 42)
        for e in (facil, normal, dificil):
            e._fechar()
            eventos = e.update(1/120, jogador, golpe=pygame.Rect(0, 0, 760, CHAO), serie=1)
            assert "acerto" in eventos and e.progresso == 0
        assert facil.vida < normal.vida < dificil.vida < dificil.vida_max


def chamar_na_app(app, dificuldade="normal"):
    i = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == "Tecelã do Vão")
    app.comecar_ensaio(i, dificuldade)
    j = app.jogo
    for _ in range(31):
        passo(app, pygame.K_d)
    e = j.boss
    assert e and e.indice == 1
    e.vida = 66  # Isola a troca de fase. O percurso integral chega por golpes.
    for _ in range(120):
        passo(app)
        if e.estado == "chama_ninhada":
            break
    assert e.estado == "chama_ninhada"
    return j, e


def test_tecela_avisa_de_onde_vem_a_ninhada_e_recomeca_limpa(app):
    j, e = chamar_na_app(app)
    assert not e.ninhada.vivos
    pontos = e.ninhada.cascas
    assert pontos
    tecla(app, pygame.K_ESCAPE)
    app.atualizar(.5)
    assert e.ninhada.cascas == pontos and not e.ninhada.vivos
    tecla(app, pygame.K_ESCAPE)
    for _ in range(70):
        passo(app)
        if e.ninhada.vivos:
            break
    assert tuple(a.origem for a in e.ninhada.vivos) == tuple((x, CHAO) for x in pontos)
    assert all(a.estado == "patrulha" for a in e.ninhada.vivos)
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte" and not e.ninhada.vivos and not e.ninhada.cascas
    app.atualizar(.5)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and app.jogo.boss is None


def test_agua_interrompe_reforco_proximo_e_abate_nao_marca_o_save(app):
    j, e = chamar_na_app(app, "difícil")
    for _ in range(60):
        passo(app)
        if e.ninhada.vivos:
            break
    assert len(e.ninhada.vivos) == 2
    atacando = e.ninhada.vivos[0]
    atacando.rect.midbottom = e.cortina, CHAO
    atacando.estado, atacando.t = "aviso", .6
    j.recolocar((e.valvula, CHAO))
    tecla(app, pygame.K_e)
    passo(app)
    assert e.agua > 0 and atacando.estado == "recuo" and atacando.lentidao > 0
    j.recolocar((atacando.rect.centerx-18, CHAO))
    j.lume.face = 1
    tecla(app, pygame.K_l)
    for _ in range(34):
        passo(app, pygame.K_LCTRL)
        if not atacando.ativo:
            break
    assert not atacando.ativo and f"inimigo_{atacando.origem[0]}" not in j.flags
    e._resolver([])
    assert not e.ninhada.vivos and not e.ninhada.cascas


def test_duas_levas_trocam_pressao_com_a_tecela_sem_encher_a_arena(app):
    j, e = chamar_na_app(app, "difícil")
    j.lume.iframes = 50
    viu_cria = viu_tecela = False
    for _ in range(1900):
        if e.ninhada.levas == 1 and e.ninhada.vivos:
            e.vida = 32
        passo(app)
        criaturas = [c for c in e.ninhada.vivos if c.ativo]
        assert len(criaturas) <= 2 and e.ninhada.levas <= 2
        tecela = e.estado == "aviso" or bool(e.fios)
        ataques = sum(bool(c.estado in ("aviso", "investida") or c.projeteis) for c in criaturas)
        assert ataques + int(tecela) <= 1
        viu_cria |= ataques > 0
        viu_tecela |= tecela
    assert viu_cria and viu_tecela
    assert e.ninhada.levas == 2 and not e.ninhada.vivos and not e.ninhada.cascas
