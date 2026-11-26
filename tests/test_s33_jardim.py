"""As escolhas e o trabalho dos três sobreviventes aparecem no percurso."""
import pygame

from src import corte_vertical, resgates
from src.ensaios import ENSAIOS
from tests.test_s14_tila import rotulos
from tests.test_s20_raiz import passo, tecla
from tests.test_s21_arquivo import fechar_fala
from tests.test_s31_historia import iniciar


POSICOES = {"tila": (2648, 790), "bento": (3665, 1828), "aru": (3136, 1828)}


def falar(app):
    tecla(app, pygame.K_e)
    passo(app)
    assert app.jogo.dialogo
    tecla(app, pygame.K_RETURN)
    while app.pagina_fala < len(app.fala_paginas)-1:
        tecla(app, pygame.K_RETURN)
        tecla(app, pygame.K_RETURN)


def test_mantimentos_de_bento_e_aru_tem_nome_efeito_e_recibo(app):
    j = iniciar(app)
    fichas = (("bento", "raízes", "Pólen aderente", "projéteis"),
              ("aru", "oficina", "Casulo de seda", "um ataque"))
    for ident, lugar, nome, efeito in fichas:
        pessoa = resgates.POR_ID[ident]
        j.sobreviventes[ident] = {"oficio": "trilha", "premio": False}
        j.recolocar(pessoa.abrigo)
        falar(app)
        trilha, abrigo = rotulos(app)
        assert lugar in trilha and nome in abrigo and efeito in abrigo
        tecla(app, pygame.K_DOWN)
        tecla(app, pygame.K_RETURN)
        assert j.bolsa.estoque[pessoa.item] == 1
        falar(app)
        assert app.selecao == 1 and "já recebido" in rotulos(app)[1]
        tecla(app, pygame.K_RETURN)
        assert j.bolsa.estoque[pessoa.item] == 1


def iniciar_jardim(app):
    indice = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == "Jardim do Último Sinal")
    app.comecar_ensaio(indice)
    return app.jogo


def postos(j):
    return {o.id for o in j.objetos if o.id.startswith("jardim_turno_")}


def test_o_trabalho_no_jardim_reage_a_cada_mecanismo(app):
    j = iniciar_jardim(app)
    j.cartografia.clear()
    assert not postos(j)
    for local, flag, ident in (
        ((2360, 790), "jardim_aberto", "tila"),
        ((3830, 1462), "jardim_calha", "bento"),
        ((3020, 1828), "jardim_plantado", "aru"),
    ):
        j.recolocar(local)
        if ident == "aru":
            j.cartografia.update(("jardim_brotos", "jardim_orvalho"))
        tecla(app, pygame.K_e)
        passo(app)
        assert flag in j.cartografia
        pos = POSICOES[ident]
        j.recolocar(pos)
        corte_vertical.camera(j)
        assert j.proximo().id == "jardim_turno_" + ident
        falar(app)
        assert j.dialogo[0] == resgates.POR_ID[ident].nome and j.escolha_resgate is None
        fechar_fala(app)
    assert len(postos(j)) == 3
    assert j.bolsa.estoque["pavio"] == 2
    assert any(t == "O trabalho dos três sinais" for t, _ in j.diario)


def test_as_luzes_e_a_conversa_do_jardim_reaparecem_apos_recarga(app):
    j = iniciar(app)
    j.sobreviventes = {ident: {"oficio": "trilha", "premio": False} for ident in resgates.POR_ID}
    j.cartografia.update(("jardim_aberto", "jardim_orvalho", "jardim_comporta", "jardim_brotos",
                          "jardim_calha", "jardim_plantado"))
    corte_vertical.entrar(j, "jardim")
    j.recolocar(POSICOES["tila"])
    corte_vertical.camera(j)
    j.lume.energia = 0
    alvo = (2760, 600)
    assert j.visivel(alvo)
    j.sobreviventes["tila"]["oficio"] = "abrigo"
    assert not j.visivel(alvo)
    falar(app)
    assert "seda" in j.dialogo[1]
    fechar_fala(app)
    app.menu()
    tecla(app, pygame.K_RETURN)
    novo = app.jogo
    assert app.estado == "jogo" and novo is not j
    assert len(postos(novo)) == 3
    novo.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.5)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and novo.lume.rect.midbottom == (2510, 790)
    assert len(postos(novo)) == 3 and "jardim_plantado" in novo.cartografia
    novo.recolocar(POSICOES["tila"])
    falar(app)
    fechar_fala(app)
    assert sum(t == "Tila na ponte do Jardim" for t, _ in novo.diario) == 1
    assert novo.sobreviventes["tila"] == {"oficio": "abrigo", "premio": False}


def percorrer_jardim(app, observar=None):
    from tests.test_s31_historia import CampanhaPelaApp

    j = iniciar_jardim(app)
    p = CampanhaPelaApp(app, observar)
    p.ir(2620)
    p.registrar("ponte-de-tila")
    falar(app)
    p.registrar("fala-de-tila")
    fechar_fala(app)
    for x, saltar in ((2680, False), (2750, True), (2910, True), (3008, False),
                     (3125, True), (3210, True), (3330, True), (3420, False), (3520, True)):
        p.ir(x, pular=saltar)
    assert p.lume.rect.bottom == 316
    p.usar()
    p.ir(3300)
    p.ir(3900)
    p.usar()
    assert "jardim_comporta" in j.cartografia
    p.ir(4110, pular=True)
    p.ir(4290)
    combater(p, 4350)
    p.ir(4500)
    p.usar()
    p.ir(4170)
    for espera in (60, 65, 90):
        p.tick(baixo=True, salto=True)
        p.esperar(espera)
    assert p.lume.rect.bottom == 1462
    p.ir(3830, agachar=True)
    p.usar()
    assert "jardim_calha" in j.cartografia
    p.tick(baixo=True, salto=True)
    p.esperar(90)
    p.ir(3705)
    p.registrar("calha-de-bento")
    falar(app)
    p.registrar("fala-de-bento")
    fechar_fala(app)
    combater(p, 3270)
    p.ir(3020)
    p.usar()
    assert "jardim_plantado" in j.cartografia
    p.ir(3096)
    p.registrar("nascente-de-aru")
    falar(app)
    p.registrar("fala-de-aru")
    fechar_fala(app)
    p.ir(2300)
    assert j.em_vertical and p.lume.rect.bottom == 1828
    assert {posto.titulo for posto in resgates.POSTOS.values()} <= {t for t, _ in j.diario}
    return j


def combater(p, origem):
    for n in range(1000):
        e = next((e for e in p.jogo.inimigos if e.origem[0] == origem and e.ativo), None)
        if e is None:
            break
        dx = e.rect.centerx - p.lume.rect.centerx
        p.tick(mover=1 if dx > 44 else -1 if dx < -44 else 0, golpe=n%12 == 0,
               clarao=n%180 == 0, deslize=n%240 == 0)
        if p.lume.vida < 35 and p.jogo.bolsa.estoque["balsamo"]:
            p.tomar_balsamo()
    assert f"vigia_{origem}" in p.jogo.cartografia


def test_jardim_percorrido_com_controles_da_app_e_retorno_pelo_viveiro(app):
    j = percorrer_jardim(app)
    assert j.bolsa.estoque["pavio"] == 2 and j.checkpoint == (2510, 790)
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.5)
    tecla(app, pygame.K_RETURN)
    # O Campo de testes prepara um novo cenário. A História tem persistência.
    assert app.estado == "jogo" and app.jogo.lume.rect.midbottom == (2510, 790)
