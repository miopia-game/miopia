"""Percursos por comandos normais no encontro S01 e isolamento da campanha."""
import os
import random
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

from src.combate import segmento_bloqueado
from src.ensaios import ENSAIOS, INDICE_ARANHA, SALA_ARANHA, SEMENTE_ARANHA, preparar_ensaio
from src.fases import CHAO
from src.main import App
from src.travessia import Comando, Jornada


def atravessar_pedra(j):
    for _ in range(240):
        lume = j.lume
        if lume.rect.left > 405:
            return
        saltar = 280 < lume.rect.centerx < 407 and lume.chao and abs(lume.rect.bottom - CHAO) < 1
        j.update(1/60, Comando(mover=1, salto=saltar, segurar_salto=True))
    raise AssertionError("Lume não atravessou a cobertura por controles normais.")


class GaleriaDaSedaTest(unittest.TestCase):
    def test_sala_exclusiva_e_semente_independente(self):
        normal = Jornada()
        self.assertNotEqual(ENSAIOS[INDICE_ARANHA].nome, normal.fase.name)
        self.assertGreater(len(normal.inimigos), 1)
        global_antes = random.getstate()
        a = preparar_ensaio(INDICE_ARANHA, "normal")
        b = preparar_ensaio(INDICE_ARANHA, "normal", SEMENTE_ARANHA)
        c = preparar_ensaio(INDICE_ARANHA, "normal", SEMENTE_ARANHA + 1)
        self.assertEqual(random.getstate(), global_antes)
        self.assertEqual((a.sala_id, a.semente), (SALA_ARANHA, SEMENTE_ARANHA))
        self.assertEqual(a.inimigos[0].origem, b.inimigos[0].origem)
        self.assertNotEqual(a.inimigos[0].origem, c.inimigos[0].origem)
        self.assertEqual([e.tipo for e in a.inimigos], ["aranha"])
        self.assertEqual([o.tipo for o in a.objetos], ["refugio"])
        self.assertTrue(any(t.rect.collidepoint(a.poleiro, CHAO+2) for t in a.solidos))
        self.assertFalse(any(t.rect.colliderect(a.inimigos[0].rect) for t in a.solidos))
        self.assertFalse(any(a.bolsa.estoque.values()))

    def test_abrigo_bloqueio_e_ataque_ao_sair_da_cobertura(self):
        j = preparar_ensaio(INDICE_ARANHA, "normal")
        e = j.inimigos[0]
        j.update(1/60, Comando(clarao=True))
        self.assertLess(j.lume.energia, 80)
        j.update(1/60, Comando(interagir=True))
        self.assertGreater(j.lume.energia, 99)
        for _ in range(150):
            j.update(1/60, Comando(mover=1))
        self.assertAlmostEqual(j.lume.rect.right, 335)
        self.assertTrue(segmento_bloqueado(j.lume.rect.center, e.rect.center, j.solidos))
        self.assertEqual(e.sequencia, 0)
        atravessar_pedra(j)
        for _ in range(100):
            j.update(1/60)
            if e.sequencia:
                break
        self.assertGreater(e.sequencia, 0)
        self.assertIsInstance(e.observacao, tuple)
        self.assertGreater(e.instante_aviso, 0)

    def test_vitoria_por_controles_e_reinicio_completo(self):
        j = preparar_ensaio(INDICE_ARANHA, "normal", 1702)
        e = j.inimigos[0]
        atravessar_pedra(j)
        for f in range(360):
            dx = e.rect.centerx - j.lume.rect.centerx
            mover = 1 if dx>33 else -1 if dx < -33 else 0
            j.update(1/60, Comando(mover=mover, golpe=f%17==0 and abs(dx)<115,
                                   clarao=f%150==0 and abs(dx)<130))
            if j.estado != "jogando":
                break
        self.assertEqual(j.estado, "vitoria")
        self.assertFalse(e.ativo)
        self.assertIs(e, j.inimigos[0])
        self.assertFalse(j.restauradas)
        j.reiniciar()
        self.assertEqual(j.estado, "jogando")
        self.assertEqual(j.tempo, 0)
        self.assertFalse(j.flags)
        self.assertEqual(j.lume.rect.midbottom, j.checkpoint)
        self.assertEqual(j.lume.energia, 100.)
        self.assertEqual((j.inimigos[0].origem, j.inimigos[0].vida), (e.origem, e.max_vida))

    def test_menu_abre_e_fecha_sem_alterar_save_e_recordes(self):
        with TemporaryDirectory() as tmp, patch.dict(os.environ, {"MIOPIA_DADOS":tmp}):
            app = App(temporaria=True)
            try:
                app.iniciar("historia")
                app.jogo.flags.add("valvula")
                app.menu()
                campanha = app.mem.ler("campanha")
                recordes = app.mem.recordes()
                app.selecao = app.menu_nomes().index("Campo de testes")
                app.ativar()
                app.selecao = INDICE_ARANHA
                app.ativar()
                self.assertEqual(app.jogo.sala_id, SALA_ARANHA)
                app.atualizar(1/60)
                app.desenhar()
                app.evento(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
                app.selecao = 4
                app.ativar()
                self.assertEqual(app.estado, "ensaios")
                self.assertEqual(app.mem.ler("campanha"), campanha)
                self.assertEqual(app.mem.recordes(), recordes)
            finally:
                app.mem.db.close()
                pygame.quit()
