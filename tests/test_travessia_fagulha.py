"""Travessia de Véspera pelo teclado e preservação das regras de luz."""
import pygame

from src.licao_vespera import PRATICADO
from src.travessia_fagulha import CUSTO, CHEGADA, MorcegoDoGalho, prever_marca
from tests.test_s20_raiz import passo, tecla
from tests.test_s22_tutorial import iniciar
from tests.test_s31_historia import CampanhaPelaApp
from tests.test_s40_acessibilidade import botao


def test_fagulha_revela_o_morcego_e_o_salto_alcanca_o_outro_galho(app):
    j = iniciar(app)
    p = CampanhaPelaApp(app)
    for x in (255,380,558,708):
        p.ir(x,pular=x!=255)
    assert j.vespera_sinal is not None and j.dialogo is None
    p.esperar(35)
    assert not j.fagulha_ativa and PRATICADO not in j.tutorial
    p.ir(801)
    passo(app,pygame.K_a)
    assert prever_marca(j) is None
    passo(app,pygame.K_d)
    assert prever_marca(j) == CHEGADA
    morcego = next(e for e in j.inimigos if isinstance(e,MorcegoDoGalho))
    assert not j.visivel(morcego.rect.center)
    brilho, halo = j.lume.energia, j.raio
    tecla(app,pygame.K_g)
    passo(app)
    assert j.lume.energia == brilho-CUSTO and j.raio < halo
    p.esperar(28)
    assert j.fagulha_ativa.posicao(j.tempo) == CHEGADA
    assert j.visivel(morcego.rect.center) and morcego.estado == "poleiro"
    assert PRATICADO in j.tutorial
    assert PRATICADO in j.carregar(j.salvar()).tutorial
    p.ir(1011,pular=True)
    assert j.lume.rect.bottom == 240 and morcego.estado != "poleiro"


def test_fagulha_nao_consume_vida_e_apaga_sem_debitar_de_novo(app):
    j = iniciar(app)
    p = CampanhaPelaApp(app)
    j.campo_testes = True
    tecla(app,pygame.K_g)
    passo(app)
    assert j.fagulha_ativa is None
    j.campo_testes = False
    j.recolocar((799,248))
    j.lume.energia = CUSTO-1
    vida = j.lume.vida
    tecla(app,pygame.K_g)
    passo(app)
    assert j.fagulha_ativa is None and j.lume.vida == vida
    j.lume.energia = 80
    botao(app,pygame.CONTROLLER_BUTTON_LEFTSHOULDER)
    botao(app,pygame.CONTROLLER_BUTTON_RIGHTSHOULDER)
    passo(app)
    assert j.fagulha_ativa and not j.vestigios
    botao(app,pygame.CONTROLLER_BUTTON_RIGHTSHOULDER,False)
    botao(app,pygame.CONTROLLER_BUTTON_LEFTSHOULDER,False)
    tecla(app,pygame.K_g)
    passo(app)
    assert j.lume.energia == 80-CUSTO
    p.esperar(460)
    assert j.fagulha_ativa is None and j.lume.energia == 80-CUSTO
    assert j.raio == 90+.38*j.lume.energia


def test_desvios_aparecem_no_pouso_da_fagulha_e_ficam_no_save(app):
    from src.desvios_fagulha import DESVIOS

    j = iniciar(app)
    p = CampanhaPelaApp(app)
    rotas = {1: ((946,322),(1110,303),(1257,265)),
             3: ((1613,344),(1681,306),(1810,260))}
    for etapa, d in DESVIOS.items():
        j.entrar(etapa)
        j.flags.add(d.requisito)
        j.recolocar(d.partida)
        j.lume.energia = 100.
        j.lume.face = 1
        assert not any(t in j.solidos for t in d.apoios)
        assert d.reserva not in j.objetos
        tecla(app,pygame.K_g)
        passo(app)
        assert j.fagulha_ativa.destino == d.marca and d.chave not in j.flags
        p.esperar(27)
        assert all(t in j.solidos for t in d.apoios)
        for x,y in rotas[etapa]:
            p.ir(x,pular=True)
            assert j.lume.rect.bottom == y
        antes = j.bolsa.estoque[d.item]
        p.usar()
        assert d.reserva.id in j.flags and j.bolsa.estoque[d.item] == antes+1
        salvo = j.carregar(j.salvar())
        assert d.chave in salvo.flags and d.reserva not in salvo.objetos
        assert all(t in salvo.solidos for t in d.apoios)


def test_aranha_vira_para_a_isca_sem_sofrer_dano(app):
    from src.fases import CHAO

    j = iniciar(app)
    j.entrar(1)
    j.flags.update(("dreno","lingueta","ponte"))
    j.recolocar((1388,CHAO))
    aranha = next(e for e in j.inimigos if e.origem[0]==1610)
    vida = aranha.vida
    tecla(app,pygame.K_g)
    passo(app)
    for _ in range(60):
        passo(app)
        if aranha.estado == "isca_fagulha":
            break
    assert aranha.estado == "isca_fagulha" and aranha.frente == 1
    x = aranha.rect.centerx
    for _ in range(20):
        passo(app)
    assert aranha.rect.centerx > x+5 and aranha.vida == vida


def test_sombra_recua_e_ataque_em_andamento_nao_e_interrompido():
    from src.travessia import Jornada
    from src.travessia_fagulha import Fagulha, reagir

    j = Jornada(etapa=2)
    sombra = next(e for e in j.inimigos if e.tipo=="sombra")
    x, y = sombra.rect.center
    j.tempo = 1.
    j.fagulha = Fagulha(0.,(x-120,y),(x-68,y))
    for estado in ("aviso","investida"):
        sombra.estado = estado
        assert not reagir(j,sombra,1/60,j.solidos)
        assert sombra.estado == estado
    sombra.estado = "patrulha"
    assert reagir(j,sombra,1/60,j.solidos)
    assert sombra.estado == "fuga_fagulha" and sombra.destino_fagulha.x > x


def test_dica_local_do_cipo_e_do_primeiro_corte(app):
    from src.abertura_bosque import pista
    from src.fases import CHAO

    j = iniciar(app)
    j.recolocar((980, CHAO))
    tecla_local, rotulo, (x, _) = pista(j)
    assert (tecla_local, rotulo, x) == ("E", "Subir", 990)
    j.recolocar((1001, 240))
    assert pista(j)[:2] == ("E", "Descer")

    j.recolocar((1034, 240))
    j.lume.face = 1
    morcego = next(e for e in j.inimigos if isinstance(e, MorcegoDoGalho))
    morcego.rect.midbottom = (1099, 240)
    morcego.estado, morcego.t = "recuo", 2.
    assert pista(j)[:2] == ("J", "Cortar")
    tecla(app, pygame.K_j)
    for _ in range(12):
        passo(app)
    assert morcego.vida < morcego.max_vida
    assert "praticado_corte_morcego" in j.tutorial
    assert "praticado_corte_morcego" in j.carregar(j.salvar()).tutorial
    assert not pista(j) or pista(j)[0] != "J"


def test_deslize_parado_segue_a_face_e_respeita_recarga(app):
    j = iniciar(app)
    for face in (-1, 1):
        j.recolocar((520, 442))
        passo(app)
        j.lume.face = face
        x = j.lume.rect.centerx
        tecla(app, pygame.K_LSHIFT)
        passo(app)
        assert j.lume.slide > 0 and (j.lume.rect.centerx - x) * face > 0
        recarga = j.lume.slide_cd
        tecla(app, pygame.K_LSHIFT)
        passo(app)
        assert 0 < j.lume.slide_cd < recarga


def test_aviso_do_morcego_distingue_rasante_e_mergulho(app):
    from src.abertura_bosque import pista

    j = iniciar(app)
    j.recolocar((1034, 240))
    j.lume.face = 1
    morcego = next(e for e in j.inimigos if isinstance(e, MorcegoDoGalho))
    morcego.rect.midbottom = (1083, 240)
    morcego.estado = "aviso"
    for tecnica, comando in (("rasante", "S"), ("mergulho", "A / D")):
        morcego.tecnica = tecnica
        assert pista(j)[0] == comando
    morcego.estado = "recuo"
    assert pista(j)[:2] == ("J", "Cortar")
