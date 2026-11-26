from collections import defaultdict
import unittest
import pygame

from src.chefes import Encontro
from src.ensaios import ENSAIOS
from src.fases import ARENA, CHAO
from tests.auto_qa.test_gameplay_fuzz import quadro


def corpo(x, base=CHAO, altura=42):
    rect = pygame.FRect(0,0,24,altura)
    rect.midbottom = x,base
    return rect


def avancar_ate(encontro, estado, jogador):
    eventos = []
    for _ in range(480):
        if encontro.estado == estado:
            return eventos
        eventos.extend(encontro.update(1/60,jogador))
    raise AssertionError(f"{encontro.nome}: não chegou a {estado} de {encontro.estado}.")


class LeituraDeChefes(unittest.TestCase):
    def test_rasante_baixo_acerta_agachado_e_poupa_o_salto(self):
        for fase,altura_ao_passar,dano in ((0,0,False),(1,0,True),(1,48,False)):
            with self.subTest(fase=fase,altura=altura_ao_passar):
                e = Encontro(0,0,CHAO,dificuldade="fácil")
                e.progresso = fase
                isca = corpo(72,altura=20)
                avancar_ate(e,"aviso",isca)
                self.assertEqual(e.asa_rasteira,bool(fase))
                self.assertEqual(e.som_aviso,"casco_avanco" if fase else "rasgo")
                alvo = e.destino,e.alvo_y
                avancar_ate(e,"investida",corpo(480))
                self.assertEqual((e.destino,e.alvo_y),alvo)
                eventos = avancar_ate(e,"aberto",corpo(72,CHAO-altura_ao_passar,20))
                self.assertEqual(eventos.count("dano_jogador"),int(dano))
                self.assertEqual(e.tempo,2.1 if fase else 3.8)

    def test_asa_mira_o_apoio_real_mas_nao_rastreia_lume_no_ar(self):
        e = Encontro(0,0,CHAO)
        e.progresso = 1
        apoio = e.apoios()[0]
        jogador = corpo(apoio.centerx,apoio.top,20)
        avancar_ate(e,"aviso",jogador)
        self.assertEqual(e.alvo_y,apoio.top-10)
        avancar_ate(e,"investida",corpo(jogador.centerx,CHAO))
        self.assertEqual(e.alvo_y,apoio.top-10)

    def test_asa_pode_acertar_os_quatro_patamares_nas_duas_fases(self):
        for fase in (0, 1):
            for indice in range(4):
                with self.subTest(fase=fase, apoio=indice):
                    e = Encontro(0, 0, CHAO)
                    e.progresso = fase
                    apoio = e.apoios()[indice]
                    jogador = corpo(apoio.centerx, apoio.top)
                    avancar_ate(e, "aviso", jogador)
                    self.assertEqual(e.alvo_y, apoio.top - 31)
                    avancar_ate(e, "investida", jogador)
                    fim = "aberto" if indice < 2 else "busca"
                    eventos = avancar_ate(e, fim, jogador)
                    self.assertEqual(eventos.count("dano_jogador"), 1)

    def test_asa_busca_no_ar_mas_trava_altura_no_aviso(self):
        for esquivou in (False, True):
            with self.subTest(esquivou=esquivou):
                e = Encontro(0, 0, CHAO)
                jogador = corpo(365, CHAO - 150)
                inicio = e.y
                for _ in range(18):
                    e.update(1 / 60, jogador)
                self.assertEqual(e.estado, "busca")
                self.assertLess(e.y, inicio)
                avancar_ate(e, "aviso", jogador)
                alvo = e.destino, e.alvo_y
                self.assertEqual(alvo, jogador.center)
                if esquivou:
                    jogador.bottom = CHAO
                avancar_ate(e, "investida", jogador)
                eventos = avancar_ate(e, "busca", jogador)
                self.assertEqual((e.destino, e.alvo_y), alvo)
                self.assertEqual(eventos.count("dano_jogador"), int(not esquivou))

    def test_tecela_anuncia_as_duas_pontas_antes_de_fiar(self):
        for fase in (0,1):
            with self.subTest(fase=fase):
                e=Encontro(1,0,CHAO,dificuldade="fácil")
                e.progresso=fase
                isca=corpo(445)
                avancar_ate(e,"aviso",isca)
                alvos=[(e.destino,e.alvo_y)]
                if fase:
                    self.assertIsNotNone(e.segundo_fio)
                    alvos.append(e.segundo_fio)
                    self.assertGreater(abs(alvos[0][0]-alvos[1][0]),100)
                else:
                    self.assertIsNone(e.segundo_fio)
                ox,oy=e.x,e.y
                avancar_ate(e,"busca",corpo(600))
                self.assertEqual(len(e.fios),len(alvos))
                for (x,y),fio in zip(alvos,e.fios):
                    self.assertAlmostEqual(fio.vx*(y-oy),fio.vy*(x-ox),places=7)
                e.update(1/60,corpo(e.valvula),interagir=True)
                self.assertFalse(e.fios)
                avancar_ate(e,"aberto",corpo(e.valvula))
                self.assertEqual(e.tempo,2.85 if fase else 4.8)


def test_asa_acerta_lume_no_patamar_superior_pela_app(app):
    indice = next(i for i, ensaio in enumerate(ENSAIOS) if ensaio.nome == "Asa Fendida")
    app.comecar_ensaio(indice)
    lume = app.jogo.lume
    teclas = defaultdict(bool)

    def avancar_ate_condicao(condicao, limite):
        for _ in range(limite):
            if condicao():
                return
            quadro(app, teclas)
        assert condicao(), (tuple(lume.rect), app.jogo.boss.estado)

    quadro(app, teclas, [(pygame.KEYDOWN, pygame.K_d)])
    avancar_ate_condicao(lambda: lume.rect.centerx >= ARENA + 63, 60)
    quadro(app, teclas, [(pygame.KEYUP, pygame.K_d), (pygame.KEYDOWN, pygame.K_SPACE)])
    avancar_ate_condicao(lambda: lume.chao and lume.rect.bottom == CHAO - 66, 90)
    quadro(app, teclas, [(pygame.KEYUP, pygame.K_SPACE)])
    quadro(app, teclas, [(pygame.KEYDOWN, pygame.K_d), (pygame.KEYDOWN, pygame.K_SPACE)])
    avancar_ate_condicao(lambda: lume.rect.centerx >= ARENA + 224, 65)
    quadro(app, teclas, [(pygame.KEYUP, pygame.K_d)])
    avancar_ate_condicao(lambda: lume.chao and lume.rect.bottom == CHAO - 120, 60)
    quadro(app, teclas, [(pygame.KEYUP, pygame.K_SPACE)])

    vida = lume.vida
    avancar_ate_condicao(lambda: lume.vida < vida, 360)
    assert app.jogo.boss.progresso == 0


def test_fagulha_na_marca_so_abre_a_brecha_se_continuar_acesa():
    from src.travessia_fagulha import Fagulha

    for apaga in (False, True):
        e = Encontro(0,0,CHAO)
        alvo = e.marcas_fagulha()[0]
        isca = Fagulha(0.,(70,CHAO-22),alvo)
        jogador = corpo(295)
        eventos = []
        for _ in range(300):
            eventos.extend(e.update(1/60,jogador,fagulha=isca))
            if e.estado == "aviso":
                break
        assert e.asa_isca is isca and e.destino == alvo[0]
        plano = e.destino,e.alvo_y
        for _ in range(300):
            eventos.extend(e.update(1/60,jogador,fagulha=None if apaga else isca))
            if e.estado not in ("aviso","investida"):
                break
        assert (e.destino,e.alvo_y) == plano
        assert ("brecha_fagulha" in eventos) is not apaga
        assert e.asa_brecha_fagulha is not apaga
        assert e.alvo_fagulha(isca) is None


def test_fagulha_fora_dos_patamares_nao_desvia_o_voo():
    from src.travessia_fagulha import Fagulha

    e = Encontro(0,0,CHAO)
    jogador = corpo(360)
    isca = Fagulha(0.,(100,CHAO-22),(340,CHAO-4))
    for _ in range(170):
        e.update(1/60,jogador,fagulha=isca)
        if e.estado == "aviso":
            break
    assert e.estado == "aviso" and e.asa_isca is None
    assert e.destino == jogador.centerx


def test_fagulha_abre_dorso_e_aceita_critico_no_patamar_pela_app(app):
    from tests.test_s20_raiz import passo, tecla
    from tests.test_s31_historia import CampanhaPelaApp

    app.comecar_ensaio(next(i for i,sala in enumerate(ENSAIOS) if sala.nome=="Asa Fendida"))
    p = CampanhaPelaApp(app)
    j = app.jogo
    p.ir(ARENA+74)
    e = j.boss
    passo(app,pygame.K_d)
    tecla(app,pygame.K_g)
    passo(app)
    assert j.fagulha_ativa.destino == e.marcas_fagulha()[0]
    p.ir(ARENA+141,pular=True)
    for _ in range(180):
        p.tick()
        if e.asa_brecha_fagulha:
            break
    assert e.estado=="aberto" and e.asa_brecha_fagulha
    assert j.lume.vida == 100 and e.vida == 100
    p.ir(ARENA+232,pular=True)
    passo(app,pygame.K_d)
    for _ in range(32):
        p.tick(golpe=True)
        if e.progresso:
            break
    assert e.progresso == 1 and e.vida == 66


def test_tecela_precisa_de_um_fio_disparado_ao_alcance_da_fagulha():
    from src.chefes import Fio
    from src.travessia_fagulha import Fagulha

    e = Encontro(1,0,CHAO)
    x,y = e.marcas_fagulha()[0]
    isca = Fagulha(0.,(x-190,y),(x,y))
    jogador = corpo(x-95)
    assert "teia_queimada" not in e.update(1/60,jogador,fagulha=isca)
    e.fios = [Fio(x,y-80,0,0)]
    assert "teia_queimada" not in e.update(1/60,jogador,fagulha=isca)
    e.fios[0].y = y-32
    eventos = e.update(1/60,jogador,fagulha=isca)
    assert "teia_queimada" in eventos and e.estado == "desce" and e.agua == 0
    assert not e.fios and e.alvo_fagulha(isca) is None


def test_casco_so_fica_preso_quando_a_carga_cruza_a_seiva():
    from src.travessia_fagulha import Fagulha

    e = Encontro(2,0,CHAO)
    x,y = e.marcas_fagulha()[0]
    isca = Fagulha(0.,(x-190,y),(x,y))
    e.x = x+72
    e.destino = x-122
    e.frente = -1
    e.combo_restante = 1
    e._mudar("investida",1.)
    jogador = corpo(x-134)
    eventos = e.update(1/60,jogador,fagulha=isca)
    assert "casco_presaseiva" not in eventos and e.estado == "investida"
    for _ in range(28):
        eventos = e.update(1/60,jogador,fagulha=isca)
        if e.estado == "aberto":
            break
    assert e.estado == "aberto" and "casco_presaseiva" in eventos
    assert e.combo_restante == 0 and e.vida == 100


def test_coruja_ouve_sino_acionado_remotamente_depois_de_move_lo():
    from src.travessia_fagulha import Fagulha

    e = Encontro(3,0,CHAO)
    x,y = e.valvula,CHAO-4
    isca = Fagulha(0.,(x+140,y),(x,y))
    longe = corpo(x+190)
    assert not e.marcas_fagulha()
    assert "sino_fagulha" not in e.update(1/60,longe,fagulha=isca)
    e.update(1/60,corpo(x),interagir=True)
    assert e.sino_movido and not e.sino_soou
    eventos = e.update(1/60,longe,fagulha=isca)
    assert "sino_fagulha" in eventos and e.sino_soou
    eventos = e.update(1/60,longe,fagulha=isca)
    assert "sino_fagulha" not in eventos


def test_previsao_de_fagulha_corresponde_ao_pouso_e_some_durante_o_voo(app):
    from src.travessia_fagulha import CUSTO, prever_marca
    from tests.test_s20_raiz import passo,tecla
    from tests.test_s31_historia import CampanhaPelaApp

    app.comecar_ensaio(next(i for i,sala in enumerate(ENSAIOS) if sala.nome=="Asa Fendida"))
    p = CampanhaPelaApp(app)
    j = app.jogo
    p.ir(ARENA+74)
    passo(app,pygame.K_d)
    antes = j.lume.energia
    prevista = prever_marca(j)
    assert prevista == j.boss.marcas_fagulha()[0] and not j.fagulha_ativa
    assert j.lume.energia == antes
    tecla(app,pygame.K_g)
    passo(app)
    assert j.fagulha_ativa.destino == prevista
    assert prever_marca(j) is None and j.lume.energia == antes-CUSTO
    p.esperar(28)
    assert j.boss.marca_acesa == prevista


def test_fagulha_fora_da_marca_avisa_no_pouso_e_mantem_custo(app):
    from src.avisos import conteudo
    from src.travessia_fagulha import CUSTO, prever_marca
    from tests.test_s20_raiz import passo,tecla
    from tests.test_s31_historia import CampanhaPelaApp

    app.comecar_ensaio(next(i for i,sala in enumerate(ENSAIOS) if sala.nome=="Asa Fendida"))
    p = CampanhaPelaApp(app)
    j = app.jogo
    p.ir(ARENA+74)
    passo(app,pygame.K_a)
    assert prever_marca(j) is None
    antes = j.lume.energia
    tecla(app,pygame.K_g)
    passo(app)
    assert j.fagulha_ativa and j.lume.energia == antes-CUSTO
    assert j.boss.marca_fagulha(j.fagulha_ativa) is None
    p.esperar(28)
    assert conteudo(j)[0] == "Fagulha fora da marca"
    assert j.boss.marca_acesa is None and j.lume.energia == antes-CUSTO


def test_hud_da_tecela_mostra_esquiva_e_fagulha_durante_o_aviso(app,monkeypatch):
    from src import paisagem
    from tests.test_s31_historia import CampanhaPelaApp

    app.comecar_ensaio(next(i for i,sala in enumerate(ENSAIOS) if sala.nome=="Tecelã do Vão"))
    p = CampanhaPelaApp(app)
    p.ir(ARENA+90)
    for _ in range(180):
        if p.jogo.boss.estado == "aviso":
            break
        p.tick()
    assert p.jogo.boss.estado == "aviso"
    escritas = []
    texto = paisagem.texto

    def registrar(s,msg,*args,**kw):
        escritas.append(msg)
        return texto(s,msg,*args,**kw)

    monkeypatch.setattr(paisagem,"texto",registrar)
    app.desenhar()
    assert "Fio vindo · E na roda abre a água" in escritas
    assert "G na seda · faça o fio cruzar a marca" in escritas
