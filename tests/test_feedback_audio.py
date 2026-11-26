import os
import unittest
from unittest.mock import Mock

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

from src.audio import Audio, INTERVALO_BATIMENTO


class MixagemDaMata(unittest.TestCase):
    def setUp(self):
        self.audio = Audio()
        self.addCleanup(pygame.mixer.quit)
        self.assertTrue(self.audio.disponivel)

    def test_presenca_nao_esconde_ataque_nem_bombeia_o_fundo(self):
        a = self.audio
        self.assertTrue(a.tocar_local("asa_perto", -100, 0))
        self.assertTrue(a.tocar_local("patas_perto", 100, 0))
        self.assertEqual(a.silencio, 0)
        self.assertTrue(a.tocar_local("fio_disparo", 110, 0))
        self.assertIs(pygame.mixer.Channel(12).get_sound(), a.fx["fio_disparo"])
        a.atualizar(1/60)
        self.assertLess(a.fundo, 1)
        self.assertGreater(a.fundo, .65)
        self.assertFalse(a.tocar_local("aviso", 1000, 0))

    def test_batimento_de_energia_critica_tem_intervalos_silenciosos(self):
        a = self.audio
        pulso = Mock()
        a.camadas[1] = pulso
        a.ambiente(combate=True, energia=12, raizes=0)
        a.atualizar(.01)
        pulso.play.assert_called_once_with(a.fx["camada_pulso"])
        a.atualizar(INTERVALO_BATIMENTO-.1)
        self.assertEqual(pulso.play.call_count, 1)
        a.atualizar(.2)
        self.assertEqual(pulso.play.call_count, 2)
        a.ambiente(combate=False, energia=100, raizes=0)
        a.atualizar(INTERVALO_BATIMENTO)
        self.assertEqual(pulso.play.call_count, 2)

    def test_passos_alternam_sem_acionar_alertas(self):
        a = self.audio
        a.tocar("passo")
        self.assertIs(pygame.mixer.Channel(16).get_sound(), a.fx["passo"])
        pygame.mixer.Channel(16).stop()
        a.tocar("passo")
        self.assertIs(pygame.mixer.Channel(16).get_sound(), a.fx["passo_folha"])
        self.assertEqual(a.silencio, 0)
