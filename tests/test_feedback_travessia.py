"""Percursos do Bosque e do Corte atravessam apoios por baixo e voltam pelo topo."""
import unittest
import pygame

from src import corte_vertical
from src.fases import CHAO, Terreno
from src.travessia import Comando, Jornada, Lume
from tests.test_travessia import Percurso


class FeedbackTravessiaTest(unittest.TestCase):
    def test_varanda_do_bosque_exige_segunda_batida_e_guarda_orvalho(self):
        a = Percurso()
        a.ir(255)
        a.ir(374, pular=True)
        self.assertEqual(a.lume.rect.bottom, 376)
        def saltar(novamente):
            for f in range(115):
                a.tick(salto=f == 0 or (novamente and f == 20),
                       segurar_salto=f != 19)
        saltar(False)
        self.assertEqual(a.lume.rect.bottom, 376)
        quantidade = a.jogo.orvalhos
        saltar(True)
        self.assertEqual(a.lume.rect.bottom, 228)
        a.ir(414)  # A gota e a mochila de Mimo ocupam pontos distintos da varanda.
        self.assertEqual(a.jogo.orvalhos, quantidade + 1)
        a.tick(baixo=True, salto=True)
        a.esperar(70)
        self.assertEqual(a.lume.rect.bottom, 376)
        saltar(True)
        self.assertEqual(a.jogo.orvalhos, quantidade + 1)

    def test_uma_batida_por_voo_com_mesma_altura_a_30_60_e_120_hz(self):
        maximos = []
        for hz in (30, 60, 120):
            with self.subTest(hz=hz):
                j = Jornada()
                l = j.lume
                pico = l.rect.bottom
                impulsos = 0
                for f in range(3*hz):
                    # O segundo toque acontece no ar. O terceiro vem enquanto
                    # Lume ainda sobe, bem antes da margem de buffer do pouso.
                    segundo, terceiro = hz // 3, hz // 2
                    salto = f in (0, segundo, terceiro)
                    solto = hz // 30
                    segurar = not (segundo - solto <= f < segundo or terceiro - solto <= f < terceiro)
                    j.update(1 / hz, Comando(salto=salto, segurar_salto=segurar))
                    pico = min(l.rect.bottom, pico)
                    impulsos += j.eventos.count("pulo")
                    if f == segundo:
                        self.assertGreater(l.batida_asa, 0)
                        self.assertFalse(l.asa_disponivel)
                self.assertEqual(impulsos, 2)
                self.assertTrue(l.chao)
                self.assertTrue(l.asa_disponivel)
                maximos.append(CHAO - pico)
        self.assertGreater(min(maximos), 155)
        self.assertLess(max(maximos) - min(maximos), 5)

    def test_rebote_de_parede_tem_prioridade_sem_recarregar_a_asa(self):
        l = Lume(115, CHAO)
        chao = Terreno(pygame.Rect(0, CHAO, 300, 90), "chao")
        parede = Terreno(pygame.Rect(132, 105, 24, CHAO-105), "parede")
        parede_esquerda = Terreno(pygame.Rect(0, 95, 14, CHAO-95), "parede")
        pisos = (chao, parede, parede_esquerda)
        dt = 1 / 120
        for f in range(24):
            l.movimento(dt, Comando(mover=1, salto=f==0, segurar_salto=True), pisos, 0, True)
        self.assertTrue(l.na_parede)
        self.assertTrue(l.movimento(dt, Comando(salto=True, segurar_salto=True), pisos, 0, True))
        self.assertTrue(l.impulso_parede)
        self.assertTrue(l.asa_disponivel)
        for _ in range(30):
            l.movimento(dt, Comando(), pisos, 0, True)
        self.assertTrue(l.movimento(dt, Comando(salto=True, segurar_salto=True), pisos, 0, True))
        self.assertFalse(l.asa_disponivel)
        self.assertFalse(l.impulso_parede)
        # Outro contato válido com a parede não fornece uma segunda carga.
        for _ in range(60):
            l.movimento(dt, Comando(mover=-1, segurar_salto=True), pisos, 0, True)
            if l.na_parede:
                break
        self.assertTrue(l.na_parede)
        self.assertTrue(l.movimento(dt, Comando(salto=True, segurar_salto=True), pisos, 0, True))
        self.assertTrue(l.impulso_parede)
        self.assertFalse(l.asa_disponivel)

    def test_cair_do_apoio_e_planar_preservam_uma_unica_batida(self):
        l = Lume(38, 100)
        pisos = (Terreno(pygame.Rect(0, 100, 52, 20), "plataforma"),)
        for _ in range(75):
            l.movimento(1/120, Comando(mover=1, segurar_salto=True), pisos, 0, True)
        self.assertTrue(l.planando)
        restante = l.planeio
        l.movimento(1/120, Comando(), pisos, 0, True)
        self.assertTrue(l.movimento(1/120, Comando(salto=True, segurar_salto=True), pisos, 0, True))
        self.assertFalse(l.planando)
        self.assertFalse(l.asa_disponivel)
        self.assertEqual(l.planeio, restante)

    def test_grades_orientais_do_corte_transitam_e_a_rocha_segura(self):
        for baixo, alto, rocha in ((403,316,1050), (1082,988,1189), (1576,1492,1061)):
            for x, grade in ((1134,True), (rocha,False)):
                with self.subTest(baixo=baixo,x=x):
                    l = Lume(x, baixo)
                    for f in range(160):
                        l.movimento(1/120, Comando(salto=f==0, mover=int(f<3),
                                     segurar_salto=f<70), corte_vertical.terrenos(), 0, True)
                    self.assertAlmostEqual(l.rect.centerx, x, delta=1)
                    self.assertEqual(l.rect.bottom, alto if grade else baixo)
                    if grade:
                        for f in range(100):
                            l.movimento(1/120, Comando(salto=f==0, baixo=True),
                                        corte_vertical.terrenos(), 0, True)
                        self.assertEqual(l.rect.bottom, baixo)

    def test_voltar_pela_mesma_grade_apos_descer_ou_reiniciar(self):
        a = Percurso()
        a.ir(255)
        a.ir(374,pular=True)
        a.tick(baixo=True,salto=True)
        self.assertFalse(a.lume.chao)
        a.tick()
        a.tick(salto=True,segurar_salto=True)
        for _ in range(110):
            a.tick(segurar_salto=True)
        self.assertEqual(a.lume.rect.bottom, 376)
        a.lume.asa_disponivel = False
        a.lume.batida_asa = .1
        a.jogo.reiniciar()
        self.assertTrue(a.lume.asa_disponivel)
        self.assertEqual(a.lume.batida_asa, 0)
