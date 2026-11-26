"""O pedido de Fio conecta o Estaleiro, os berços e a margem da cisterna."""
import pygame

from src import corte_vertical, missoes
from src.descoberta import conhecida
from src.ensaios import ENSAIOS
from src.fases import CHAO
from src.orientacao import objetivo_atual
from src.travessia import Jornada
from tests.test_s20_raiz import esperar_piso, ir, passo, tecla
from tests.test_s21_arquivo import fechar_fala
from tests.test_s26_comporta import abrir, painel


PEDIDO = "pedido_fio"
ACEITO = "fio_cheia_conhecida"
CARRETEL = "carretel_fio"
CONCLUIDO = "passarela_fio"
OFICINA = (1834, 790)
MARGEM = (1310, 1828)


def usar(app):
    tecla(app, pygame.K_e)
    passo(app)


def descer(app, x, piso):
    ir(app, x)
    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_s)
    esperar_piso(app, piso)


def estaleiro(app):
    indice = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == "Estaleiro das Folhas")
    app.comecar_ensaio(indice)
    usar(app)
    assert app.jogo.setor_vertical == "Estaleiro das Folhas"
    return app.jogo


def teste_rotina_com_fio_na_oficina_e_depois_na_cisterna(app):
    j = estaleiro(app)
    bancos = [o for o in j.objetos if o.id == "fio_corte"]
    assert [(o.x, o.y) for o in bancos] == [OFICINA]
    ir(app, OFICINA[0])
    usar(app)
    assert j.dialogo[0] == "Fio" and "casulos" in j.dialogo[1]
    fechar_fala(app)

    j.recolocar((1554, 1828))
    abrir(app)
    assert painel(j) is not None
    assert [(o.x, o.y) for o in j.objetos if o.id == "fio_corte"] == [OFICINA]
    for _ in range(63):
        passo(app)
    assert [(o.x, o.y) for o in j.objetos if o.id == "fio_corte"] == [MARGEM]
    ir(app, MARGEM[0])
    usar(app)
    assert j.dialogo[0] == "Fio" and "margem" in j.dialogo[1]


def teste_percurso_completo_pela_app_com_rastreio_e_passarela(app):
    j = estaleiro(app)
    ir(app, OFICINA[0])
    usar(app)
    fechar_fala(app)
    assert ACEITO in j.cartografia
    tecla(app, pygame.K_m)
    tecla(app, pygame.K_RIGHT)
    lista = missoes.conhecidas(j)
    indice = next(i for i, pedido in enumerate(lista) if pedido.id == PEDIDO)
    for _ in range(len(lista)):
        if app.pedido_cursor == indice:
            break
        tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    assert j.missao == PEDIDO and objetivo_atual(j).id == "grade_viveiro"
    assert not conhecida(j, 1176, 1556)
    tecla(app, pygame.K_m)

    for x, piso in ((2215, 886), (2215, 982), (2195, 1078), (2195, 1174), (2085, 1270)):
        descer(app, x, piso)
    assert objetivo_atual(j).id == "placa_viveiro"
    ir(app, 1982)
    usar(app)
    fechar_fala(app)
    assert "leu_placa_viveiro" in j.cartografia and objetivo_atual(j).id == "comporta_viveiro"
    for x, piso in ((1950, 1366), (1787, 1462), (1715, 1558),
                    (1690, 1654), (1690, 1744), (1690, 1828)):
        descer(app, x, piso)
    ir(app, 1554)
    abrir(app)
    ir(app, 1115)
    assert objetivo_atual(j).id == CARRETEL
    for piso in (1744, 1660, 1576):
        tecla(app, pygame.K_SPACE)
        for _ in range(32):
            passo(app, pygame.K_SPACE)
        esperar_piso(app, piso)
    ir(app, 1160)
    usar(app)
    assert CARRETEL in j.cartografia and objetivo_atual(j).id == "fio_corte"
    for piso in (1660, 1744, 1828):
        descer(app, 1120, piso)
    ir(app, MARGEM[0])
    usar(app)
    assert CONCLUIDO in j.cartografia and j.bolsa.estoque["globo"] == 1
    assert any(m.id == PEDIDO and m.estado == "Concluída" for m in missoes.conhecidas(j))
    fechar_fala(app)
    usar(app)
    fechar_fala(app)
    assert j.bolsa.estoque["globo"] == 1 and sum(t == "O fio da cheia" for t, _ in j.diario) == 1
    ir(app, 895)
    assert j.lume.chao and j.lume.rect.bottom == 1828 and j.lume.vida == 100
    ir(app, 1110)
    assert j.lume.rect.bottom == 1828
    restaurado = Jornada.carregar(j.salvar())
    restaurado.recolocar((1110, 1828))
    corte_vertical.camera(restaurado)
    restaurado.lume.energia = 0
    app.jogo = restaurado
    assert restaurado.visivel((963, 1796))
    ir(app, 895)
    assert restaurado.lume.chao and restaurado.lume.rect.bottom == 1828
    assert restaurado.bolsa.estoque["globo"] == 1
    for _ in restaurado.bolsa.estoque:
        if restaurado.bolsa.equipado == "globo":
            break
        tecla(app, pygame.K_q)
    tecla(app, pygame.K_f)
    assert restaurado.bolsa.estoque["globo"] == 0 and len(restaurado.globos) == 1


def teste_save_antigo_e_carretel_recolhido_antes_de_falar(app):
    app.iniciar("historia")
    app.jogar()
    j = app.jogo
    corte_vertical.entrar(j, "cisterna")
    antigo = j.salvar()
    j = app.jogo = Jornada.carregar(antigo)
    assert PEDIDO not in {m.id for m in missoes.conhecidas(j)}
    assert not any(t.tipo == "ponte" and t.rect.x == 930 for t in j.solidos)
    j.recolocar((1176, 1576))
    usar(app)
    assert CARRETEL in j.cartografia and ACEITO in j.cartografia
    assert missoes.selecionar(j, PEDIDO)
    app.salvar_campanha()
    app.iniciar("historia", continuar=True)
    j = app.jogo
    assert j.missao == PEDIDO and CARRETEL in j.cartografia
    assert not any(o.id == CARRETEL for o in j.objetos)
    assert "viveiro_aberto" not in j.cartografia and objetivo_atual(j).id == "ralo_cisterna"
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert CARRETEL in app.jogo.cartografia and CONCLUIDO not in app.jogo.cartografia
    j = app.jogo
    j.entrar(1)
    j.flags.add("ponte")
    assert objetivo_atual(j).id == "corte_estaleiro"
    j.recolocar((1944, CHAO))
    usar(app)
    assert j.em_vertical and objetivo_atual(j).id == "grade_viveiro"
    j.recolocar((1982, 1270))
    usar(app)
    fechar_fala(app)
    j.recolocar((1554, 1828))
    abrir(app)
    ir(app, MARGEM[0])
    usar(app)
    assert CONCLUIDO in j.cartografia and j.bolsa.estoque["globo"] == 1


def teste_fio_da_superficie_preserva_pedido_de_casca():
    j = Jornada(etapa=1)
    j.flags.update(("ponte", "registro"))
    fio = next(o for o in j.objetos if o.id == "fio")
    assert fio.x == 1567 and fio.y == CHAO
    j.interagir(fio)
    assert "pedido_entregue" in j.flags and j.bolsa.estoque["concha"] == 1
    assert ACEITO not in j.cartografia
