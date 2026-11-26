"""A interação coincide com os apoios e mecanismos da travessia."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src import corte_vertical as corte
from src.fases import CHAO
from src.main import App
from src.travessia import Comando, Jornada
from tests.test_travessia import Percurso


class ManivelasTest(unittest.TestCase):
    def test_cipo_do_bosque_fica_disponivel_desde_a_entrada(self):
        p = Percurso()
        self.assertNotIn("valvula", {o.id for o in p.jogo.objetos})
        self.assertIn("corda", {o.id for o in p.jogo.objetos})
        p.ir(990)
        self.assertEqual(p.jogo.interacao, "Subir pelo cipó")
        pontos = p.jogo.pontuacao
        p.usar()
        self.assertIn("corda", p.jogo.eventos)
        self.assertTrue(p.lume.em_corda)
        self.assertEqual(p.jogo.pontuacao, pontos + 25)

    def test_save_com_manivela_ja_acionada_nao_repete_pontos_no_cipo(self):
        j = Jornada()
        j.flags.add("valvula")
        retomado = Jornada.carregar(j.salvar())
        retomado.recolocar((990, CHAO))
        pontos = retomado.pontuacao
        retomado.update(1/60, Comando(interagir=True))
        self.assertTrue(retomado.lume.em_corda)
        self.assertEqual(retomado.pontuacao, pontos)

    def test_ponte_travada_explica_a_peca_e_salva_a_posicao(self):
        j = Jornada(etapa=1)
        j.recolocar((1295, CHAO))
        self.assertIn("lingueta", j.interacao)
        j.update(1/60, Comando(interagir=True))
        self.assertNotIn("ponte", j.flags)
        self.assertIn("lingueta", j.aviso)
        j.flags.update(("dreno", "lingueta"))
        self.assertEqual(j.interacao, "Soltar a ponte")
        j.update(1/60, Comando(interagir=True))
        self.assertIn("valvula", j.eventos)
        self.assertTrue(any(t.tipo == "ponte" for t in j.solidos))
        retomado = Jornada.carregar(j.salvar())
        retomado.recolocar((1295, CHAO))
        self.assertEqual(retomado.interacao, "Examinar a ponte estendida")
        self.assertTrue(any(t.tipo == "ponte" for t in retomado.solidos))

    def test_cisterna_teclas_juntas_abrem_o_ralo_uma_vez(self):
        app = App(temporaria=True)
        try:
            app.iniciar("historia")
            app.jogar()
            j = app.jogo
            corte.entrar(j, "cisterna")
            self.assertIn("precisa de K", j.interacao)
            for tecla in (pygame.K_e, pygame.K_k):
                app.evento(pygame.event.Event(pygame.KEYDOWN, key=tecla))
            app.atualizar(1/60)
            self.assertIn("pulso", j.eventos)
            self.assertIn("ralo_aberto", j.cartografia)
            self.assertEqual(j.bolsa.estoque["casulo"], 1)
            j.fechar_dialogo()
            self.assertEqual(j.interacao, "Examinar o ralo aberto")
            j.update(1/60, Comando(interagir=True))
            self.assertEqual(j.bolsa.estoque["casulo"], 1)
            self.assertNotIn("porta", j.eventos)
        finally:
            app.mem.db.close()
            pygame.quit()
