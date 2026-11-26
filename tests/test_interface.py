"""Percursos por eventos do pygame, com SQLite local e renderização real."""
import os
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
import unittest

os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame
from src.main import App
from src.fases import RAIZ
from src.memoria import Memoria


class InterfaceTest(TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env=patch.dict(os.environ,{"MIOPIA_DADOS":self.tmp.name})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.app=App()

    def tearDown(self):
        self.app.mem.db.close()
        pygame.quit()

    def tecla(self,key):
        self.app.evento(pygame.event.Event(pygame.KEYDOWN,key=key))
        self.app.desenhar()

    def test_menu_clicavel_pausa_diario_e_marco(self):
        a=self.app
        a.desenhar()
        a.evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=a.alvos[0].center))
        self.assertEqual(a.estado,"prologo")
        self.tecla(pygame.K_ESCAPE)
        for _ in range(50): a.atualizar(1/60)
        self.tecla(pygame.K_p)
        t=a.jogo.tempo
        for _ in range(45): a.atualizar(1/60)
        self.assertEqual(a.jogo.tempo,t)
        self.tecla(pygame.K_r)
        self.tecla(pygame.K_ESCAPE)
        self.assertEqual(a.estado,"pausa")
        self.tecla(pygame.K_ESCAPE)
        self.tecla(pygame.K_TAB)
        self.tecla(pygame.K_RIGHT)
        self.assertEqual(a.pagina,1)
        self.tecla(pygame.K_TAB)
        a.jogo.flags.add("valvula")
        a.menu()
        self.assertEqual(a.menu_nomes()[0],"Continuar história")
        self.tecla(pygame.K_RETURN)
        self.assertEqual(a.estado,"jogo")
        self.assertIn("valvula",a.jogo.flags)
        self.assertEqual(a.tela.get_size(),(960,540))

    def test_ajustes_creditos_e_modo_removido_preservam_campanha(self):
        a=self.app
        a.mudar("ajustes")
        self.tecla(pygame.K_RIGHT)
        self.assertEqual(a.mem.prefs["dificuldade"],"difícil")
        self.tecla(pygame.K_F10)
        db=Memoria()
        self.assertTrue(db.prefs["mudo"])
        db.db.close()
        a.menu()
        a.selecao=a.menu_nomes().index("Créditos")
        self.tecla(pygame.K_RETURN)
        self.assertEqual(a.estado,"creditos")
        self.assertEqual(a.audio.atual,"creditos")
        self.tecla(pygame.K_RETURN)
        self.assertEqual(a.audio.atual,"menu")
        a.iniciar("historia");a.jogar();a.menu()
        campanha=a.mem.ler("campanha")
        with self.assertRaises(ValueError):a.iniciar('infinito')
        self.assertEqual(a.mem.ler("campanha"),campanha)
        self.assertFalse(a.mem.recordes())

    def test_fala_congela_ate_finalizar_e_sem_punicao_no_registro(self):
        a=self.app
        a.iniciar("historia");a.jogar()
        j=a.jogo
        nira=next(o for o in j.objetos if o.id=="nira")
        j.lume.rect.midbottom=(nira.x,nira.y)
        self.tecla(pygame.K_e);a.atualizar(.02)
        t=j.tempo
        for _ in range(27): a.atualizar(1/60)
        self.assertTrue(j.dialogo); self.assertEqual(t,j.tempo)
        for pagina in range(len(a.fala_paginas)):
            self.assertEqual(a.pagina_fala, pagina)
            self.tecla(pygame.K_RETURN)  # Completa o texto desta página.
            self.tecla(pygame.K_RETURN)  # Avança ou encerra a conversa.
        self.assertIsNone(j.dialogo)
        j.flags.update(("chefe","gota_0","gota_1","gota_2"))
        j.lume.rect.midbottom=(RAIZ,442)
        self.tecla(pygame.K_e);a.atualizar(.02)
        self.assertEqual(a.estado,'jogo')  # Restaurar a raiz não abre questionário.
        self.tecla(pygame.K_c)
        self.assertEqual(a.estado,"registro")
        valor=(j.lume.energia,j.lume.vidas,j.pontuacao)
        self.tecla(pygame.K_RETURN);self.tecla(pygame.K_RETURN)
        self.assertEqual(a.estado,"jogo")
        self.assertEqual((j.lume.energia,j.lume.vidas,j.pontuacao),valor)
        self.assertEqual(j.restauradas,1)


if __name__=="__main__":
    unittest.main()
