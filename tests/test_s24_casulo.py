"""O golpe de queda vira um impulso ambiental no Poço da Seiva."""
import pygame

from src.travessia import Jornada
from tests.test_s20_raiz import esperar_piso, ir, passo, preparar_poco, tecla


CENTRO = 947
FUNDO = 1492
NICHO = 1270
PREMIO = "pavio_casulo_poco"


def alinhar_no_casulo(app):
    ir(app, CENTRO-15)
    for _ in range(18):
        passo(app)
    assert abs(app.jogo.lume.rect.centerx-CENTRO) < 5


def saltar(app, quadros):
    tecla(app, pygame.K_SPACE)
    for _ in range(quadros):
        passo(app, pygame.K_SPACE)


def quicar(app, tecla_ataque=pygame.K_j, dt=1/60):
    saltar(app, 23)
    tecla(app, tecla_ataque)
    for _ in range(28):
        passo(app, pygame.K_s, dt=dt)
        if "rebote_casulo" in app.jogo.eventos:
            return
    raise AssertionError("O golpe não atingiu o casulo.")


def test_rebote_pela_app_alcanca_nicho_sem_luz_e_entrega_pavio_unico(app):
    preparar_poco(app)
    j = app.jogo
    alinhar_no_casulo(app)
    j.lume.energia = 0
    assert j.ensino_id == "casulo_impulso"
    assert j.lume.rect.bottom == FUNDO
    quicar(app)
    assert j.lume.vy < -600
    assert "praticado_casulo_impulso" in j.tutorial
    assert j.lume.combo_acertos == 0
    esperar_piso(app, NICHO)
    assert j.proximo().id == PREMIO
    antes = j.bolsa.estoque["pavio"]
    tecla(app, pygame.K_e)
    passo(app)
    assert j.bolsa.estoque["pavio"] == antes+1 and PREMIO in j.cartografia
    assert (j.lume.vida, j.lume.energia) == (100, 0)
    tecla(app, pygame.K_e)
    passo(app)
    assert j.bolsa.estoque["pavio"] == antes+1
    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_s)
    esperar_piso(app, FUNDO)
    app.salvar_campanha()
    app.iniciar("historia", continuar=True)
    assert PREMIO in app.jogo.cartografia
    assert app.jogo.bolsa.estoque["pavio"] == antes+1
    assert all(o.id != PREMIO for o in app.jogo.objetos)


def test_passar_pelo_casulo_pular_e_bater_no_chao_nao_lancam_lume(app):
    preparar_poco(app)
    alinhar_no_casulo(app)
    j = app.jogo
    tecla(app, pygame.K_j)
    for _ in range(40):
        passo(app, pygame.K_s)
        assert j.lume.chao and "rebote_casulo" not in j.eventos
    saltar(app, 24)
    passo(app)
    saltar(app, 24)
    for _ in range(110):
        if j.lume.rect.bottom < NICHO+48:
            tecla(app, pygame.K_e)
        passo(app)
        assert PREMIO not in j.cartografia and "rebote_casulo" not in j.eventos
        assert j.lume.rect.bottom > NICHO
        if j.lume.chao:
            break
    assert j.lume.rect.bottom == FUNDO


def test_rebote_com_l_e_retomada_apos_morte(app):
    preparar_poco(app)
    app.salvar_campanha()
    salvo = app.jogo.salvar()
    salvo["corte"]["memoria"] = ["viu_poco"]
    j = app.jogo = Jornada.carregar(salvo)
    assert any(o.id == PREMIO for o in j.objetos)
    alinhar_no_casulo(app)
    quicar(app, pygame.K_l, dt=.05)
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and j.lume.rect.midbottom == j.checkpoint
    assert j.lume.arma.rebote == 0 and PREMIO not in j.cartografia
    alinhar_no_casulo(app)
    quicar(app, pygame.K_l)
    esperar_piso(app, NICHO)
    assert j.proximo().id == PREMIO


def test_rota_pela_fenda_do_bosque_e_pavio_em_uso(app):
    app.iniciar("historia")
    app.jogar()
    j = app.jogo
    ir(app, 630)
    tecla(app, pygame.K_e)
    passo(app)
    assert j.em_vertical
    ir(app, 690)
    for piso in (1072, 1156, 1240, 1324, 1408, FUNDO):
        tecla(app, pygame.K_SPACE)
        passo(app, pygame.K_s)
        esperar_piso(app, piso)
    alinhar_no_casulo(app)
    quicar(app)
    esperar_piso(app, NICHO)
    tecla(app, pygame.K_e)
    passo(app)
    assert j.bolsa.estoque["pavio"] == 1
    for _ in range(12):
        if j.bolsa.equipado == "pavio":
            break
        tecla(app, pygame.K_q)
        passo(app)
    tecla(app, pygame.K_f)
    passo(app)
    assert j.bolsa.estoque["pavio"] == 0 and j.bolsa.luz_ate > j.tempo
    assert PREMIO in j.cartografia
