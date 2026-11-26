"""Percursos pelas duas bocas da ala leste, usando os comandos de Lume."""
import unittest

from src import corte_vertical as corte
from src.fases import CHAO, RAIZ, SAIDA
from src.travessia import Jornada
from tests.test_campanha import resolver_arena
from tests.test_travessia import Percurso


class EstaleiroTest(unittest.TestCase):
    def subir_da_galeria(self):
        p = Percurso()
        p.ir(630)
        p.usar()
        self.assertEqual(p.jogo.setor_vertical, "Galeria dos Casulos")
        p.ir(1611)
        # O beiral a 132 px do piso fica acima do alcance de um salto simples.
        p.ir(1611, pular=True)
        self.assertEqual(p.lume.rect.bottom, 988)
        for f in range(120):
            p.tick(salto=f in (0,20), segurar_salto=f!=19)
        self.assertEqual(p.lume.rect.bottom, 856)
        p.ir(1795)
        p.ir(1905, pular=True)
        p.usar()
        self.assertEqual(p.jogo.checkpoint, corte.MARCOS["estaleiro"])
        self.assertEqual(p.jogo.setor_vertical, "Estaleiro das Folhas")
        return p

    def descer(self, p, x, piso):
        p.ir(x)
        p.tick(baixo=True, salto=True)
        p.esperar(90)
        self.assertTrue(p.lume.chao)
        self.assertEqual(p.lume.rect.bottom, piso)

    def test_porta_trancada_e_reabertura_no_marco_da_oficina(self):
        p = self.subir_da_galeria()
        p.ir(2018)
        self.assertEqual(p.jogo.proximo().id, "volta_estaleiro")
        p.usar()
        self.assertTrue(p.jogo.em_vertical)
        self.assertIn("Estenda a ponte", p.jogo.aviso)
        novo = Jornada.carregar(p.jogo.salvar())
        self.assertEqual(novo.lume.rect.midbottom, corte.MARCOS["estaleiro"])
        self.assertEqual(novo.setor_vertical, "Estaleiro das Folhas")
        self.assertEqual(novo.cartografia, p.jogo.cartografia)
        self.assertEqual(novo.camera, min(corte.LARGURA-960, 1905-435))

    def test_bercos_e_comporta_inferior_abrem_a_volta_pela_cisterna(self):
        p = self.subir_da_galeria()
        self.assertNotIn("viveiro_aberto", p.jogo.cartografia)
        for x, piso in ((2215,886),(2215,982),(2195,1078),(2195,1174),(2085,1270)):
            self.descer(p, x, piso)
        self.assertEqual(p.jogo.setor_vertical, "Viveiro Afundado")
        p.ir(1982)
        p.usar()
        self.assertIn("leu_placa_viveiro", p.jogo.cartografia)
        p.jogo.fechar_dialogo()
        for x, piso in ((1950,1366),(1787,1462),(1715,1558),(1690,1654),(1690,1744),(1690,1828)):
            self.descer(p, x, piso)
        for _ in range(120):
            p.tick(mover=-1)
        self.assertEqual(p.lume.rect.left, 1438)
        p.ir(1570)
        p.usar()
        self.assertIn("viveiro_aberto", p.jogo.cartografia)
        p.jogo.fechar_dialogo()
        p.ir(1225)
        self.assertEqual(p.jogo.setor_vertical, "Cisterna das Duas Margens")
        novo = Jornada.carregar(p.jogo.salvar())
        self.assertEqual(novo.lume.rect.midbottom, corte.MARCOS["estaleiro"])
        self.assertTrue({"leu_placa_viveiro","viveiro_aberto","viu_cisterna"} <= novo.cartografia)
        self.assertFalse(any(t.tipo=="tranca" and t.rect.left==1394 for t in novo.solidos))

    def test_ponte_acionada_pelo_corrego_abre_entrada_e_saida(self):
        p = Percurso()
        p.bosque()
        resolver_arena(p)
        p.ir(RAIZ); p.usar()
        p.ir(SAIDA); p.usar()
        self.assertEqual(p.jogo.etapa, 1)
        self.assertNotIn("corte_estaleiro", {o.id for o in p.jogo.objetos})
        p.ir(273)
        p.ir(426, pular=True); p.usar()  # drenar
        p.ir(831)
        for f in range(65):
            p.tick(mover=1, baixo=True, deslize=f==0)
            if p.jogo.interacao=="Recolher a lingueta":
                break
        p.tick(interagir=True, baixo=True, mover=1)
        for _ in range(46):
            p.tick(mover=1, baixo=True)
        p.ir(1295); p.usar()  # estender a ponte
        self.assertIn("ponte", p.jogo.flags)
        p.ir(1944)
        self.assertEqual(p.jogo.proximo().id, "corte_estaleiro")
        p.usar()
        self.assertTrue(p.jogo.em_vertical)
        self.assertEqual(p.lume.rect.midbottom, corte.MARCOS["estaleiro"])
        p.ir(2018); p.usar()
        self.assertFalse(p.jogo.em_vertical)
        self.assertEqual(p.jogo.etapa, 1)
        self.assertEqual(p.lume.rect.midbottom, (1944,CHAO))
        p.usar()
        self.assertTrue(p.jogo.em_vertical)
