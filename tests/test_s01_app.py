"""Percorre o duelo, o menu e o replay com as mesmas entradas usadas pelo jogador."""
from collections import defaultdict
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

from src import telas
from src.ensaios import INDICE_ARANHA, SEMENTE_ARANHA
from src.main import App
from src.replay_aranha import estado, ler_tentativa


class DueloNaInterface(unittest.TestCase):
    def setUp(self):
        perfil = TemporaryDirectory()
        self.addCleanup(perfil.cleanup)
        ambiente = patch.dict(os.environ, {"MIOPIA_DADOS": perfil.name})
        ambiente.start()
        self.addCleanup(ambiente.stop)
        self.pasta = Path(perfil.name) / "ensaios" / "aranha"
        self.app = App()
        self.addCleanup(pygame.quit)
        self.addCleanup(self.app.mem.db.close)
        self.tecla(pygame.K_RETURN)
        self.tecla(pygame.K_ESCAPE)
        self.tick(pygame.K_d)
        self.app.menu()
        self.campanha = self.app.mem.ler("campanha")
        self.assertIsNotNone(self.campanha)
        self.recordes = self.app.mem.recordes()
        for _ in range(self.app.menu_nomes().index("Campo de testes")):
            self.tecla(pygame.K_DOWN)
        self.tecla(pygame.K_RETURN)
        self.assertEqual((self.app.estado, self.app.selecao), ("ensaios", INDICE_ARANHA))

    def tecla(self, tecla):
        self.app.evento(pygame.event.Event(pygame.KEYDOWN, key=tecla))

    def clique(self, area):
        self.app.evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=area.center, button=1))

    def tick(self, *segurar):
        teclas = defaultdict(bool, {tecla: True for tecla in segurar})
        self.app.atualizar(1 / 60, teclas)

    def sair_do_ensaio(self):
        self.tecla(pygame.K_ESCAPE)
        self.tecla(pygame.K_UP)
        self.tecla(pygame.K_RETURN)
        self.assertEqual(self.app.estado, "ensaios")

    def verificar_campanha(self):
        self.assertEqual(self.app.mem.ler("campanha"), self.campanha)
        self.assertEqual(self.app.mem.recordes(), self.recordes)

    def cruzar_pedra(self):
        for _ in range(180):
            lume = self.app.jogo.lume
            if lume.rect.left > 405:
                return
            if lume.chao and 280 < lume.rect.centerx < 407 and lume.rect.bottom > 440:
                self.tecla(pygame.K_SPACE)
            self.tick(pygame.K_d, pygame.K_SPACE)
        self.fail("Lume não conseguiu saltar a pedra.")

    def test_semente_bolsa_pausa_e_video_sem_regravar(self):
        app = self.app
        app.desenhar()
        self.tecla(pygame.K_RIGHT)
        self.clique(telas.SEMENTE_SEGUINTE)
        self.clique(telas.SEMENTE_ANTERIOR)
        self.assertEqual(app.semente_aranha, SEMENTE_ARANHA + 1)
        self.clique(app.alvos[INDICE_ARANHA])
        self.tick(pygame.K_d)
        self.tecla(pygame.K_q)
        self.tecla(pygame.K_f)
        for _ in range(30):
            self.tick(pygame.K_d)
        self.tecla(pygame.K_TAB)
        app.desenhar()
        self.tecla(pygame.K_TAB)
        self.sair_do_ensaio()
        caminho, = self.pasta.glob("*.json")
        dados = ler_tentativa(caminho)
        self.assertEqual(dados, app.ultimo_replay)
        self.assertEqual(dados["quadros"], 31)
        self.assertEqual(dados["fim"]["motivo"], "saida")
        self.assertEqual([e["acao"] for e in dados["entradas"] if "acao" in e],
                         ["trocar_item", "usar_item"])

        self.tecla(pygame.K_RIGHT)  # Assistir usa a semente gravada.
        self.tecla(pygame.K_v)
        self.assertEqual(app.estado, "replay")
        self.assertEqual(app.jogo.semente, dados["semente"])
        self.tecla(pygame.K_SPACE)
        self.tick()
        self.assertEqual(app.jogo.tempo, 0)
        self.tecla(pygame.K_SPACE)
        for _ in range(dados["quadros"] + 3):
            self.tick(pygame.K_a)  # Controles atuais não dirigem Lume no replay.
        app.desenhar()
        self.assertIsNone(app.reproducao)
        self.assertIn("conferida", app.aviso_replay)
        self.assertEqual(estado(app.jogo)["lume"], dados["fim"]["lume"])
        self.tecla(pygame.K_ESCAPE)
        self.assertEqual(app.estado, "ensaios")
        self.assertEqual(list(self.pasta.glob("*.json")), [caminho])
        self.verificar_campanha()

    def test_reinicio_pela_pausa_preserva_a_semente(self):
        app = self.app
        self.tecla(pygame.K_RETURN)
        inicio = estado(app.jogo)
        for _ in range(45):
            self.tick(pygame.K_d)
        self.tecla(pygame.K_ESCAPE)
        self.tecla(pygame.K_r)
        self.assertEqual(app.estado, "confirmar")
        self.tecla(pygame.K_RETURN)  # Cancelar volta à mesma tentativa.
        self.assertEqual(app.estado, "pausa")
        self.assertFalse(self.pasta.exists())
        self.tecla(pygame.K_r)
        self.tecla(pygame.K_DOWN)
        self.tecla(pygame.K_RETURN)
        self.assertEqual(app.estado, "jogo")
        self.assertEqual(estado(app.jogo), inicio)
        self.assertEqual(app.ultimo_replay["fim"]["motivo"], "reinicio")
        self.sair_do_ensaio()
        self.assertEqual(len(list(self.pasta.glob("*.json"))), 2)
        self.verificar_campanha()

    def test_vitoria_e_repeticao_do_duelo(self):
        app = self.app
        self.tecla(pygame.K_RIGHT)
        self.tecla(pygame.K_RETURN)
        inicio = estado(app.jogo)
        self.cruzar_pedra()
        pausas_ao_vivo = 0
        for n in range(460):
            dx = app.jogo.inimigos[0].rect.centerx - app.jogo.lume.rect.centerx
            if n % 17 == 0 and abs(dx) < 115:
                self.tecla(pygame.K_j)
            if n % 150 == 0 and abs(dx) < 130:
                self.tecla(pygame.K_k)
            direcao = (pygame.K_d,) if dx > 33 else (pygame.K_a,) if dx < -33 else ()
            pausas_ao_vivo += app.impacto_restante > 0
            self.tick(*direcao)
            if app.estado != "jogo":
                break
        self.assertEqual(app.estado, "fim")
        app.desenhar()
        self.assertEqual(app.ultimo_replay["fim"]["motivo"], "vitoria")
        self.assertGreater(pausas_ao_vivo, 0)
        dados = app.ultimo_replay
        self.tecla(pygame.K_RETURN)
        self.assertEqual(estado(app.jogo), inicio)
        self.assertEqual(len(list(self.pasta.glob("*.json"))), 1)
        self.verificar_campanha()
        app.assistir_tentativa(dados)
        pausas_no_replay = 0
        for _ in range(dados["quadros"] + pausas_ao_vivo + 3):
            pausas_no_replay += app.impacto_restante > 0
            self.tick()
        self.assertEqual(pausas_no_replay, pausas_ao_vivo)
        self.assertIsNone(app.reproducao)

    def test_morte_aguarda_confirmacao_e_volta_ao_abrigo(self):
        app = self.app
        self.tecla(pygame.K_RETURN)
        inicio = estado(app.jogo)
        self.cruzar_pedra()
        for n in range(3600):
            if n % 65 == 0:
                self.tecla(pygame.K_k)
            self.tick()
            if app.estado != "jogo":
                break
        self.assertEqual(app.estado, "morte")
        app.desenhar()
        self.assertEqual(app.ultimo_replay["fim"]["motivo"], "morte")
        self.tecla(pygame.K_RETURN)
        self.assertEqual(app.estado, "morte")
        for _ in range(30):
            self.tick()
        self.tecla(pygame.K_RETURN)
        self.assertEqual(app.estado, "jogo")
        self.assertEqual(estado(app.jogo), inicio)
        self.assertEqual(len(list(self.pasta.glob("*.json"))), 1)
        self.verificar_campanha()
