"""Rotas da borda antes e depois de restaurar as raízes."""
import pygame

from src.fases import CHAO, RAIZ, SAIDA
from src.missoes import conhecidas
from src.orientacao import objetivo_atual
from tests.test_s20_raiz import passo, tecla
from tests.test_s21_arquivo import fechar_fala
from tests.test_s31_historia import CampanhaPelaApp, iniciar


def restaurar(app):
    j = app.jogo
    # Isolamos a consequência da interação. O percurso integral enfrenta
    # as guardiãs e coleta o orvalho no teste da campanha.
    j.flags.update(("chefe", "gota_0", "gota_1", "gota_2"))
    j.recolocar((RAIZ, CHAO))
    tecla(app, pygame.K_e)
    passo(app)
    assert "raiz" in j.flags


def test_bosque_molhado_tem_ponte_fisica_e_vespera_no_posto(app):
    j = iniciar(app)
    assert next(o for o in j.objetos if o.id == "vespera").x == 755
    assert not any(t.rect.collidepoint(1430, CHAO) for t in j.solidos)
    restaurar(app)
    posto = next(o for o in j.objetos if o.id == "vespera")
    assert posto.x == 1322
    assert any(t.rect.collidepoint(1430, CHAO) for t in j.solidos)
    trocar_de_regiao(app, SAIDA)
    assert j.etapa == 1
    trocar_de_regiao(app, 34)
    assert j.etapa == 0 and "raiz" in j.flags

    j.recolocar((1364, CHAO))
    p = CampanhaPelaApp(app)
    p.ir(1502)
    p.ir(1364)
    tecla(app, pygame.K_e)
    passo(app)
    assert j.dialogo[0] == "Véspera" and "amarra" in j.dialogo[1]
    fechar_fala(app)


def test_corrego_restaurado_da_passagem_alta_e_mantem_o_ralo(app):
    j = iniciar(app)
    j.historico[0, 1] = {"inimigo_2590"}
    j.entrar(1)
    j.flags.update(("dreno", "lingueta", "ponte", "ralo", "meio"))
    assert any(t.tipo == "vedacao" and t.rect.x == 2150 for t in j.solidos)
    restaurar(app)
    assert not any(t.tipo == "vedacao" and t.rect.x == 2150 for t in j.solidos)
    j.recolocar((2100, CHAO))
    p = CampanhaPelaApp(app)
    p.ir(2228, pular=True)
    p.ir(2316)
    assert p.lume.rect.bottom == 426
    p.tick(baixo=True, salto=True)
    p.esperar(30)
    assert p.lume.rect.bottom == 470 and j.proximo().id == "ralo"
    p.ir(2316, pular=True)
    p.ir(2468)
    p.ir(2260, pular=True)
    assert p.lume.vida == 100 and p.lume.rect.bottom == 426


def falar_resgate(app):
    tecla(app, pygame.K_e)
    passo(app)
    assert app.jogo.escolha_resgate
    for _ in app.fala_paginas[:-1]:
        app.atualizar(10)
        tecla(app, pygame.K_RETURN)
    app.atualizar(10)


def usar(app):
    tecla(app, pygame.K_e)
    passo(app)


def trocar_de_regiao(app, x):
    p = CampanhaPelaApp(app)
    p.ir(x)
    usar(app)
    assert app.estado == "capitulo"
    tecla(app, pygame.K_RETURN)


def rastrear(app, ident, alvo=None):
    tecla(app, pygame.K_m)
    tecla(app, pygame.K_RIGHT)
    assert app.estado == "diario" and app.pagina == 1
    pedidos = conhecidas(app.jogo)
    for _ in pedidos:
        if pedidos[app.pedido_cursor].id == ident:
            break
        tecla(app, pygame.K_DOWN)
    assert pedidos[app.pedido_cursor].id == ident
    tecla(app, pygame.K_RETURN)
    tecla(app, pygame.K_m)
    assert app.jogo.missao == ident
    assert objetivo_atual(app.jogo).id == (alvo or ident)


def test_tila_na_trilha_monta_descida_que_continua_apos_mudar_de_trabalho(app):
    j = iniciar(app)
    j.flags.update(("meio", "pino_ninho", "porta_ninho", "caruncho_vencido",
                    "inimigo_1875", "inimigo_1985", "inimigo_1978"))
    j.entrar(0)
    j.recolocar((1635, 1282))
    falar_resgate(app)
    tecla(app, pygame.K_RETURN)
    assert j.sobreviventes["tila"]["oficio"] == "trilha"
    assert not any(o.id == "borda_tila" for o in j.objetos)
    restaurar(app)
    posto = next(o for o in j.objetos if o.id == "borda_tila")
    rastrear(app, posto.id)
    assert not any(o.id == "corda_tila" for o in j.objetos)
    j.recolocar((posto.x, posto.y))
    falar_resgate(app)
    assert "cipó" in j.dialogo[1]
    tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    assert j.sobreviventes["tila"] == {"oficio": "abrigo", "premio": True}
    assert j.bolsa.estoque["pavio"] == 1
    assert any(o.id == "casa_tila" for o in j.objetos)
    assert not any(o.id == "borda_tila" for o in j.objetos)

    corda = next(o for o in j.objetos if o.id == "corda_tila")
    j.recolocar((corda.x, corda.y))
    usar(app)
    p = CampanhaPelaApp(app)
    p.esperar(60)
    assert p.lume.em_corda and CHAO+200 < p.lume.rect.bottom < 1282
    p.esperar(145)
    assert p.lume.rect.midbottom == (2180, 1282)
    usar(app)
    p.esperar(205)
    assert p.lume.rect.midbottom == (2180, CHAO)
    app.menu()
    tecla(app, pygame.K_RETURN)
    assert "corda_tila" in app.jogo.flags and app.jogo.bolsa.estoque["pavio"] == 1
    assert next(m for m in conhecidas(app.jogo) if m.id == "borda_tila").estado == "Concluída"
    assert "bento" not in app.jogo.sobreviventes


def test_bento_sozinho_amarra_subida_e_rota_sobrevive_ao_retorno(app):
    j = iniciar(app)
    j.historico[0, 1] = {"dreno", "lingueta", "ponte", "ralo", "meio", "inimigo_2860"}
    j.entrar(1); j.reiniciar()
    restaurar(app)
    j.recolocar((3060, 1102))
    falar_resgate(app)
    tecla(app, pygame.K_RETURN)
    assert set(j.sobreviventes) == {"bento"}
    posto = next(o for o in j.objetos if o.id == "borda_bento")
    rastrear(app, posto.id, "grade_saida_subsolo")
    app.menu()
    tecla(app, pygame.K_RETURN)
    j = app.jogo
    assert j.missao == "borda_bento" and objetivo_atual(j).id == "borda_bento"
    j.recolocar((posto.x, posto.y))
    falar_resgate(app)
    assert "corda" in j.dialogo[1]
    tecla(app, pygame.K_ESCAPE)
    app.menu()
    tecla(app, pygame.K_RETURN)
    j = app.jogo
    corda = next(o for o in j.objetos if o.id == "corda_bento")
    assert not j.bolsa.estoque["polen"]
    j.recolocar((corda.x, corda.y))
    usar(app)
    p = CampanhaPelaApp(app)
    p.esperar(65)
    assert p.lume.em_corda and p.lume.rect.bottom < 900
    p.esperar(105)
    assert p.lume.rect.midbottom == (3050, CHAO)
    p.lume.vida = 0.
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.5)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and p.lume.rect.midbottom == j.checkpoint
    assert "corda_bento" in j.flags and "corda_tila" not in j.flags
