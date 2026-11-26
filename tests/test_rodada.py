"""Regressões da rodada de avaliação: clarão, áudio, morte e ensaios isolados."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame
from src.audio import panoramica
from src.ensaios import ENSAIOS
from src.main import App
from src.travessia import Comando, Jornada
from src.visao import DURACAO


class Rodada(unittest.TestCase):
    def test_clarao_deixa_luz_no_mundo_e_se_fecha(self):
        j=Jornada()
        origem=j.lume.rect.center
        j.update(1/60,Comando(clarao=True))
        self.assertAlmostEqual(78,j.lume.energia,delta=.02)
        marca=j.vestigios[0]
        for _ in range(85):
            j.update(1/60,Comando(mover=1))
        self.assertGreater(j.lume.rect.centerx-origem[0],220)
        self.assertEqual((marca.x,marca.y),origem)
        self.assertTrue(j.visivel(origem))
        self.assertGreater(marca.raio(j.tempo),280)
        self.assertGreater(marca.raio(3.5),marca.raio(4.9))
        self.assertGreater(marca.raio(4.9),marca.raio(5.8))
        for _ in range(340):
            j.update(1/60)
        self.assertGreater(j.tempo,DURACAO)
        self.assertFalse(j.vestigios)
        self.assertFalse(j.visivel(origem))
        # O orvalho recolhido pelo caminho repõe brilho, que não drena sozinho.
        self.assertEqual(j.lume.energia,98)

    def test_aviso_estereo_indica_lado_e_distancia(self):
        centro=panoramica(0)
        esquerda=panoramica(-150)
        direita=panoramica(150)
        self.assertEqual(esquerda,direita[::-1])
        self.assertGreater(esquerda[0],esquerda[1]*1.75)
        self.assertGreater(sum(centro),sum(panoramica(340)))
        self.assertEqual(panoramica(600),(0.,0.))

    def test_field_and_death_do_not_overwrite_story(self):
        app=App(temporaria=True)
        try:
            app.iniciar("historia")
            app.jogo.flags.add("valvula")
            app.menu()
            real=app.mem.ler("campanha")
            app.selecao=app.menu_nomes().index("Campo de testes")
            app.ativar()
            for n,cena in enumerate(ENSAIOS):
                app.selecao=n
                app.ativar()
                self.assertEqual(app.ensaio,n)
                self.assertEqual(app.jogo.lume.rect.midbottom,cena.pos)
                app.atualizar(1/60)
                app.desenhar()
                app.mudar("pausa")
                app.selecao=4
                app.ativar()
                self.assertEqual(app.estado,"ensaios")
                self.assertEqual(app.mem.ler("campanha"),real)
            app.selecao=0
            app.ativar()
            app.jogo.lume.vida=0
            app.atualizar(.02)
            self.assertEqual(app.estado,"morte")
            for _ in range(30): app.atualizar(1/60)
            app.desenhar()
            app.ativar()
            self.assertEqual(app.estado,"jogo")
            self.assertEqual(app.jogo.checkpoint,ENSAIOS[0].pos)
            app.menu()
            self.assertEqual(app.mem.ler("campanha"),real)
            self.assertFalse(app.mem.recordes())
        finally:
            app.mem.db.close()
            pygame.quit()

    def test_morte_de_campanha_exige_confirmacao_e_retorna_ao_marco(self):
        app=App(temporaria=True)
        try:
            app.iniciar("historia");app.jogar()
            j=app.jogo
            j.flags.update(("meio","gota_0","valvula"))
            from src.fases import MEIO,CHAO
            j.checkpoint=(MEIO,CHAO)
            j.lume.vida=20
            j.lume.rect.top=557
            app.atualizar(1/60)
            self.assertEqual((app.estado,j.motivo_morte),("morte","queda"))
            tempo=j.tempo
            app.ativar()
            self.assertEqual(app.estado,"morte")
            app.atualizar(.41)
            self.assertEqual(j.tempo,tempo)
            app.ativar()
            self.assertEqual((app.estado,j.lume.rect.midbottom),("jogo",(MEIO,CHAO)))
            self.assertIn("valvula",j.flags)
            self.assertEqual(j.lume.vidas,2)
            self.assertEqual(j.lume.energia,100)
        finally:
            app.mem.db.close()
            pygame.quit()

    def test_brilho_do_menu_reabre_com_o_valor_escolhido(self):
        app=App(temporaria=True)
        try:
            app.mudar("ajustes")
            app.selecao=3
            app.ajustar(1)
            self.assertEqual(app.paisagem.brilho_mata,2)
            self.assertEqual(app.mem.ler("preferencias")["brilho"],2)
            app.desenhar()
        finally:
            app.mem.db.close()
            pygame.quit()
