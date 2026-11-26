"""Regressões de continuidade após saltar a ponte e de recompensas passivas."""
import unittest

from src.narrativa import Bolsa
from src.orientacao import objetivo_atual, pista_mecanismo
from src.travessia import Jornada
from tests.test_travessia import Percurso


class OrientacaoTest(unittest.TestCase):
    def test_ralo_aponta_primeira_pendencia_real_no_corrego(self):
        j = Jornada(etapa=1)
        ralo = next(o for o in j.objetos if o.id == "ralo")
        j.recolocar((ralo.x, ralo.y))
        for flags, ident, x in (((), "dreno", 432), (("dreno",), "lingueta", 982),
                               (("dreno", "lingueta"), "ponte", 1295)):
            with self.subTest(ident=ident):
                j.flags.clear()
                j.flags.update(flags)
                alvo = objetivo_atual(j)
                self.assertEqual((alvo.id, alvo.x, alvo.regiao), (ident, x, "superficie"))
                self.assertIn("esquerda", alvo.texto)
                self.assertEqual(alvo.local, "Córrego Fundo")
                pista = pista_mecanismo(j, ralo)
                self.assertNotIn("segundo", pista)
                self.assertNotIn("primeiro trecho", pista)
                self.assertIn(alvo.detalhe, pista)
        j.flags.add("ponte")
        self.assertEqual(objetivo_atual(j).id, "ralo")

    def test_pular_a_ponte_permite_voltar_abrir_e_prosseguir_por_comandos(self):
        p = Percurso(1)
        p.ir(273)
        p.ir(426, pular=True)
        p.usar()
        p.ir(831)
        for frame in range(65):
            p.tick(mover=1, baixo=True, deslize=frame == 0)
            if p.jogo.interacao == "Recolher a lingueta":
                break
        p.tick(interagir=True, baixo=True, mover=1)
        for _ in range(46):
            p.tick(mover=1, baixo=True)
        p.ir(1320)
        p.ir(1580, pular=True)
        p.ir(1930)
        p.ir(2020, pular=True)
        p.ir(2160, pular=True)
        p.ir(2316)
        p.tick(baixo=True, salto=True)
        p.esperar(35)
        p.usar()
        self.assertNotIn("ralo", p.jogo.flags)
        self.assertEqual(objetivo_atual(p.jogo).id, "ponte")
        # Há retorno físico pela mesma câmara, sem trocar de mapa ou alterar posição.
        p.ir(2220, pular=True)
        p.ir(2316, pular=True)
        p.ir(2130)
        p.ir(1580)
        p.ir(1310, pular=True)
        p.ir(1295)
        self.assertEqual(p.jogo.interacao, "Soltar a ponte")
        p.usar()
        self.assertIn("ponte", p.jogo.flags)
        self.assertEqual(objetivo_atual(p.jogo).id, "ralo")
        self.assertIn("Ponte estendida", p.jogo.aviso)

    def test_mapa_nao_muda_estado_e_casca_da_direcao_atual(self):
        j = Jornada(etapa=1)
        j.flags.update(("dreno", "lingueta"))
        antes = j.salvar()
        for _ in range(20):
            objetivo_atual(j)
        self.assertEqual(j.salvar(), antes)
        casca = next(o for o in j.objetos if o.nome == "Casca")
        j.interagir(casca)
        self.assertIn("roda da ponte", j.dialogo[1])
        self.assertIn("antes do primeiro vão", j.dialogo[1])
        self.assertTrue(any(t == "Caminho indicado por Casca" for t, _ in j.diario))

    def test_subsolo_guia_a_recompensa_e_a_grade_aberta_antes_da_arena(self):
        from src.fases import CHAO
        j = Jornada(etapa=1)
        j.flags.update(flag for flag, _ in j.fase.passos)
        j.recolocar((2620, 712))
        alvo = objetivo_atual(j)
        self.assertEqual(alvo.id, "reliquia_asa")
        self.assertTrue(alvo.opcional)
        self.assertGreater(alvo.y, j.lume.rect.bottom)
        j.bolsa.receber("asa", 1)
        j.aplicar_reliquias()
        j.recolocar((2940, 1102))
        retorno = objetivo_atual(j)
        self.assertEqual(retorno.id, "grade_saida_subsolo")
        self.assertTrue(any(t.tipo == "grade" and t.rect.collidepoint(retorno.x, retorno.y)
                            for t in j.solidos))
        self.assertIn("direita", retorno.texto)
        # Sair do poço devolve a indicação principal sem mudar etapa ou save.
        j.recolocar((3030, CHAO))
        self.assertEqual(objetivo_atual(j).id, "arena")
        self.assertFalse(objetivo_atual(j).opcional)


class ReliquiasTest(unittest.TestCase):
    def test_espinho_e_resina_alcancaveis_pelo_arquivo_e_pelos_bercos(self):
        from tests.test_corte_vertical import CorteTest
        from tests.test_feedback_estaleiro import EstaleiroTest
        corte = CorteTest()
        p = corte.entrar()
        p.ir(690)
        corte.descer(p, 2)
        p.ir(173)
        p.usar()
        p.jogo.fechar_dialogo()
        self.assertEqual(objetivo_atual(p.jogo).id, "reliquia_espinho")
        p.ir(283)
        self.assertEqual(p.jogo.proximo().id, "reliquia_espinho")
        p.usar()
        self.assertEqual(p.lume.bonus_dano, 1.25)
        # A outra relíquia pode ser alcançada pela entrada original do Bosque,
        # antes de a ponte do Córrego ser aberta.
        estaleiro = EstaleiroTest()
        p = estaleiro.subir_da_galeria()
        for x, piso in ((2215, 886), (2215, 982), (2195, 1078), (2195, 1174), (2085, 1270)):
            estaleiro.descer(p, x, piso)
        self.assertEqual(objetivo_atual(p.jogo).id, "reliquia_resina")
        p.ir(2050)
        self.assertEqual(p.jogo.proximo().id, "reliquia_resina")
        p.usar()
        self.assertEqual(p.jogo.bolsa.fator_dreno, .65)
        self.assertEqual(objetivo_atual(p.jogo).id, "comporta_viveiro")
        p.jogo.perder_fagulha("queda")
        p.jogo.reiniciar()
        salvo = Jornada.carregar(p.jogo.salvar())
        self.assertEqual(salvo.bolsa.fator_dreno, .65)
        self.assertFalse(any(o.id == "reliquia_resina" for o in salvo.objetos))

    def test_passivas_nao_consumem_bolso_nem_empilham_bonus(self):
        bolsa = Bolsa()
        bolsa.estoque["balsamo"] = 0
        for ident in ("espinho", "asa", "resina"):
            bolsa.receber(ident, 1)
            bolsa.receber(ident, 9)
        self.assertEqual((bolsa.bonus_dano, bolsa.bonus_velocidade, bolsa.fator_dreno), (1.25, 1.12, .65))
        self.assertEqual(tuple(i.id for i in bolsa.reliquias), ("espinho", "asa", "resina"))
        self.assertEqual(bolsa.equipado, "balsamo")
        self.assertIn("vazia", bolsa.trocar())
        bolsa.receber("pavio", 2)
        self.assertEqual(bolsa.equipado, "pavio")
        for _ in range(8):
            bolsa.trocar()
            self.assertEqual(bolsa.equipado, "pavio")
        nova = Bolsa.carregar(bolsa.salvar(3.), 7.)
        self.assertEqual(nova.estoque, bolsa.estoque)
        self.assertEqual(nova.bonus_dano, 1.25)
        self.assertEqual(nova.fator_dreno, .65)

    def test_save_anterior_sem_reliquias_e_sem_equipar_passiva(self):
        antiga = Bolsa.carregar({"estoque": {"balsamo": 2, "concha": 1}, "equipado": "concha"}, 0)
        self.assertEqual(antiga.bonus_dano, 1.)
        self.assertEqual(antiga.bonus_velocidade, 1.)
        self.assertEqual(antiga.fator_dreno, 1.)
        adulterada = Bolsa.carregar({"estoque": {"espinho": 999}, "equipado": "espinho"}, 0)
        self.assertEqual(adulterada.estoque["espinho"], 1)
        self.assertEqual(adulterada.equipado, "balsamo")
