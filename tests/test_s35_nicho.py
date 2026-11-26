"""Desvio opcional de Risca, luta e recompensa no Taquaral."""
import pygame
import pytest

from src.ensaios import ENSAIOS
from src.luzes_mundo import claro
from tests.test_s20_raiz import ir, passo, tecla
from tests.test_s30_galeria import FUNDO, passar_pela_raiz, pela_grade, ramal, recolher_cavilha


def usar(app):
    tecla(app, pygame.K_e)
    passo(app)


def test_o_reparo_revela_o_deposito_e_permite_ir_e_voltar_pelo_mesmo_piso(app):
    j = ramal(app)
    assert not any(o.id == "tranca_bercos" for o in j.objetos)
    pela_grade(app)
    recolher_cavilha(app)
    ir(app, 2180)
    passar_pela_raiz(app)
    usar(app)
    passar_pela_raiz(app, voltar=True)
    ir(app, 1700)
    assert j.proximo().id == "tranca_bercos"
    usar(app)
    assert "nicho_bercos_aberto" in j.flags
    ir(app, 1510)
    assert j.lume.rect.bottom == FUNDO and j.lume.rect.centerx < 1640
    ir(app, 1700)
    assert j.lume.rect.bottom == FUNDO and j.lume.rect.centerx > 1670


def abrir_ensaio(app, dificuldade="normal"):
    i = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == "Nicho dos Berços")
    app.comecar_ensaio(i, dificuldade)
    j = app.jogo
    assert j.proximo().id == "tranca_bercos"
    usar(app)
    cobra = next(e for e in j.inimigos if getattr(e, "nome", "") == "Cobra dos Berços")
    return j, cobra


@pytest.mark.parametrize("sequencia", [0, 1])
def test_cobra_anuncia_e_lanca_dois_projeteis_na_segunda_fase(app, sequencia):
    j, cobra = abrir_ensaio(app)
    j.recolocar((1560, FUNDO))
    cobra.sequencia = sequencia
    cobra.vida = cobra.max_vida/2
    for _ in range(180):
        passo(app)
        if cobra.estado == "aviso" and cobra.acao_atual == "veneno":
            break
    assert cobra.fase == 2 and cobra.angulo_veneno
    assert cobra.estado == "aviso" and not cobra.projeteis
    for _ in range(90):
        passo(app)
        if cobra.projeteis:
            break
    assert len(cobra.projeteis) == 2
    a, b = cobra.projeteis
    assert a.tipo == b.tipo == "veneno" and a.vel.y != b.vel.y
    tecla(app, pygame.K_k)
    passo(app)
    assert not cobra.projeteis


def test_cortes_leves_seguidos_nao_renovam_o_atordoamento(app):
    j, cobra = abrir_ensaio(app)
    j.recolocar((1432, FUNDO))
    arma = j.lume.arma
    arma.tipo, arma.serie = "corte1", 1
    assert cobra.acertar(arma, cobra.rect, False, j.lume) == "acerto"
    assert cobra.estado == "atordoado"
    cobra.t = .05  # Próximo ao fim da reação do primeiro corte.
    arma.tipo, arma.serie = "corte2", 2
    assert cobra.acertar(arma, cobra.rect, False, j.lume) == "acerto"
    assert cobra.t == .05
    arma.tipo, arma.serie = "pesado", 3
    assert cobra.acertar(arma, cobra.rect, False, j.lume) == "acerto"
    assert cobra.t > .05


def vencer(app, cobra):
    j = app.jogo
    for n in range(850):
        if not cobra.ativo:
            return
        assert app.estado == "jogo"
        l = j.lume
        dx = cobra.rect.centerx-l.rect.centerx
        lado = 1 if dx >= 0 else -1
        if cobra.estado in ("aviso", "investida") and cobra.tecnica == "rasteira" and abs(dx) < 112 and l.chao:
            tecla(app, pygame.K_SPACE)
        if n%15 == 0 and abs(dx) < 96:
            tecla(app, pygame.K_l if n%45 == 0 else pygame.K_j)
        if cobra.angulo_veneno and (cobra.estado == "aviso" or cobra.projeteis) and abs(dx) < 186 and l.energia >= 22:
            tecla(app, pygame.K_k)
        if abs(dx) > 57 or l.face != lado:
            passo(app, pygame.K_d if lado > 0 else pygame.K_a)
        else:
            passo(app)
    raise AssertionError(f"A cobra ainda vive com {cobra.vida:g} PV.")


def test_vitoria_e_cofre_na_historia_persistem_com_luz_e_recompensa(app):
    j = ramal(app)
    j.flags.update(("cavilha_sementes", "veneziana_sementes_aberta",
                    "inimigo_1910", "inimigo_2087"))
    j.entrar(2)
    j.reiniciar()
    pela_grade(app)
    ir(app, 1700)
    usar(app)
    cobra = next(e for e in j.inimigos if getattr(e, "nome", "") == "Cobra dos Berços")
    ir(app, 1510)
    assert not claro(j, (1330, 900))
    vencer(app, cobra)
    assert j.lume.vida > 0 and "inimigo_1388" in j.flags
    ir(app, 1274)
    usar(app)
    usar(app)
    assert claro(j, (1330, 900)) and j.bolsa.estoque["casulo"] == 2
    app.menu()
    tecla(app, pygame.K_RETURN)
    novo = app.jogo
    assert novo is not j and claro(novo, (1330, 900))
    assert novo.bolsa.estoque["casulo"] == 2
    assert all(getattr(e, "nome", "") != "Cobra dos Berços" for e in novo.inimigos)


def test_morte_recompoe_cobra_viva_e_preserva_a_tranca(app):
    j = ramal(app)
    j.flags.update(("cavilha_sementes", "veneziana_sementes_aberta"))
    pela_grade(app)
    ir(app, 1700)
    usar(app)
    cobra = next(e for e in j.inimigos if getattr(e, "nome", "") == "Cobra dos Berços")
    cobra.vida -= 7
    cobra.rect.centerx += 45
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.5)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and "nicho_bercos_aberto" in j.flags
    assert cobra.vida == cobra.max_vida and cobra.rect.midbottom == cobra.origem
