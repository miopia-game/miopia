"""Validação do quadro realmente composto, sem alterar o progresso do jogador."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import pygame

from src.cartografia import mapa_local, minimapa, rastro_objetivo
from src.paisagem import Paisagem
from src.travessia import Jornada
from src.visao import Vestigio


def luminosidade(s,rect):
    return sum(pygame.transform.average_color(s,pygame.Rect(rect))[:3])/3


class MapaELuzTest(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((960,540))
        self.s=pygame.Surface((960,540))
        self.p=Paisagem()

    def tearDown(self):
        pygame.quit()

    def test_breu_cobre_terreno_fundo_e_folhas_e_clarao_revela_regiao(self):
        j=Jornada()
        j.recolocar((450,442));j.camera=0
        self.p.desenhar(self.s,j,j.tempo)
        # Terra e primeiro plano além da luz ficam efetivamente escuros.
        escuro=luminosidade(self.s,(730,410,90,70))
        self.assertGreater(escuro,10)
        self.assertLess(escuro,100)
        self.assertGreater(luminosidade(self.s,(730,220,90,100)),5)
        self.p.brilho_mata=3
        self.p.desenhar(self.s,j,j.tempo)
        self.assertGreater(luminosidade(self.s,(730,410,90,70)),escuro)
        self.p.brilho_mata=1
        self.p.desenhar(self.s,j,j.tempo)
        antes=luminosidade(self.s,(635,370,25,35))
        j.tempo=1
        j.vestigios.append(Vestigio(450,425,.5))
        self.p.desenhar(self.s,j,j.tempo)
        self.assertGreater(luminosidade(self.s,(635,370,25,35)),antes*1.2+1)

    def test_luz_acompanha_camera_ao_descer_sem_trocar_de_mapa(self):
        from src import subsolo
        j=Jornada(etapa=1)
        j.recolocar((2850,1102));j.camera=2400
        subsolo.camera(j)
        self.assertGreater(j.camera_y,600)
        self.p.desenhar(self.s,j,j.tempo)
        py=round(j.lume.rect.centery-j.camera_y)
        self.assertGreater(luminosidade(self.s,(425,py-10,50,30)),15)
        self.assertGreater(luminosidade(self.s,(30,160,80,100)),5)
        self.assertFalse(j.em_vertical)

    def test_mapa_e_rumo_do_clarao_nao_mutam_a_partida(self):
        j=Jornada(etapa=1)
        j.flags.update(("dreno","lingueta"))
        j.tempo=1;j.vestigios.append(Vestigio(*j.lume.rect.center,.5))
        antes=j.salvar()
        for _ in range(3):
            mapa_local(self.s,j,(85,197,780,153))
            minimapa(self.s,j)
            rastro_objetivo(self.s,j)
        self.assertEqual(j.salvar(),antes)


if __name__=="__main__":
    unittest.main()
