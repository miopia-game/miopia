"""A comporta do Viveiro abre no mundo e deixa uma passagem persistente."""
import pygame

from src import corte_vertical
from src.ensaios import ENSAIOS
from src.travessia import Jornada
from tests.test_s20_raiz import esperar_piso, ir, passo, tecla


PISO = 1828
X_RODA = 1554
X_PAINEL = 1394
ABERTA = "viveiro_aberto"
NOTA = "A água encontra a cisterna"


def painel(jogo):
    return next((t.rect for t in jogo.solidos if t.tipo == "tranca" and t.rect.left == X_PAINEL), None)


def preparar_fundo(app):
    app.iniciar("historia")
    app.jogar()
    corte_vertical.entrar(app.jogo, "estaleiro")
    app.jogo.recolocar((X_RODA, PISO))
    return app.jogo


def abrir(app, *seguradas, dt=1/60):
    assert app.jogo.proximo().id == "comporta_viveiro"
    tecla(app, pygame.K_e)
    passo(app, *seguradas, dt=dt)


def test_roda_e_travessia_pelo_estaleiro_na_app(app):
    indice = next(n for n, cena in enumerate(ENSAIOS) if cena.nome == "Estaleiro das Folhas")
    app.comecar_ensaio(indice)
    tecla(app, pygame.K_e)
    passo(app)
    j = app.jogo
    assert j.em_vertical and j.setor_vertical == "Estaleiro das Folhas"
    for x, piso in ((2215, 886), (2215, 982), (2195, 1078), (2195, 1174),
                    (2085, 1270), (1950, 1366), (1787, 1462), (1715, 1558),
                    (1690, 1654), (1690, 1744), (1690, PISO)):
        ir(app, x)
        tecla(app, pygame.K_SPACE)
        passo(app, pygame.K_s)
        esperar_piso(app, piso)
    ir(app, X_RODA)
    assert painel(j).bottom == PISO
    abrir(app)
    assert ABERTA in j.cartografia and j.dialogo is None
    assert j.eventos.count("agua") == 1
    assert sum(titulo == NOTA for titulo, _ in j.diario) == 1
    for _ in range(24):
        passo(app, pygame.K_a)
    assert painel(j) is not None and painel(j).bottom < PISO
    ir(app, 1225)
    assert j.setor_vertical == "Cisterna das Duas Margens" and painel(j) is None
    ir(app, X_RODA)
    assert j.setor_vertical == "Viveiro Afundado"
    abrir(app)
    assert j.dialogo[0] == NOTA and painel(j) is None
    assert "agua" not in j.eventos and sum(titulo == NOTA for titulo, _ in j.diario) == 1


def test_subida_respeita_colisao_e_pausa_sem_repetir_som(app):
    j = preparar_fundo(app)
    j.recolocar((1512, PISO))
    abrir(app)
    assert painel(j) and j.dialogo is None
    altura = painel(j).h
    tecla(app, pygame.K_ESCAPE)
    assert app.estado == "pausa"
    for _ in range(30):
        passo(app)
        assert painel(j).h == altura
    tecla(app, pygame.K_ESCAPE)
    tecla(app, pygame.K_e)
    tecla(app, pygame.K_LSHIFT)
    encostou = False
    alturas = []
    for _ in range(74):
        passo(app, pygame.K_a, pygame.K_LSHIFT)
        folha = painel(j)
        alturas.append(folha.h if folha else 0)
        assert not folha or not folha.colliderect(j.lume.rect)
        if folha and PISO-folha.bottom < j.lume.rect.h and abs(j.lume.rect.left-folha.right) < .5:
            encostou = True
        assert "agua" not in j.eventos and j.dialogo is None
    assert encostou and alturas == sorted(alturas, reverse=True)
    assert painel(j) is None and j.lume.rect.centerx < X_PAINEL


def test_save_em_qualquer_fase_da_abertura_conserva_o_estado(app):
    j = preparar_fundo(app)
    antigo = j.salvar()
    assert painel(Jornada.carregar(antigo)).bottom == PISO
    abrir(app)
    assert painel(j)
    app.salvar_campanha()
    app.iniciar("historia", continuar=True)
    novo = app.jogo
    assert novo.em_vertical and painel(novo) is None
    assert ABERTA in novo.cartografia and sum(titulo == NOTA for titulo, _ in novo.diario) == 1
    novo.recolocar((X_RODA, PISO))
    abrir(app)
    assert novo.dialogo[0] == NOTA and "agua" not in novo.eventos


def test_morte_enquanto_a_lamina_sobe_mantem_passagem_aberta(app):
    j = preparar_fundo(app)
    abrir(app)
    assert painel(j) and ABERTA in j.cartografia
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and app.jogo.lume.rect.midbottom == corte_vertical.MARCOS["estaleiro"]
    assert painel(app.jogo) is None and ABERTA in app.jogo.cartografia
