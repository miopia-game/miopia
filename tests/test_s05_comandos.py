"""Fila, interrupção e armas isoladas exercitadas pelo modelo e pela App."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
import pygame
from src.combate import Inimigo
from src.ensaios import ENSAIOS
from src.fases import CHAO
from src.travessia import Comando, Jornada, Lume


class ComandosS05(unittest.TestCase):
    def test_fila_unica_preserva_parte_ativa_e_encadeia_tres_golpes(self):
        l=Lume(200,CHAO);a=l.arma
        a.pedir(False);a.avancar(1/120,l)
        for _ in range(8):a.avancar(1/120,l)
        a.pedir(False)
        for _ in range(7):a.avancar(1/120,l)
        self.assertEqual(a.tipo,'corte1')  # Antecipação e parte ativa não são canceladas.
        inicios=[]
        for n in range(90):
            if a.tipo=='corte2' and a.tempo>.12 and a.pedido==0:a.pedir(False)
            if a.avancar(1/120,l):inicios.append(a.tipo)
        self.assertEqual(inicios[:2],['corte2','corte3'])
        # A fila guarda um pedido; depois de terminá-lo não inventa outro.
        self.assertEqual(inicios,['corte2','corte3'])

    def test_dano_cancela_golpe_e_pedido_sem_acerto_fantasma(self):
        j=Jornada();l=j.lume
        l.iframes=0
        j.update(.05,Comando(golpe=True))
        area=l.arma.area(l)
        self.assertIsNotNone(area)
        l.arma.pedir(False)
        j.ferir()
        self.assertIsNone(l.arma.area(l))
        self.assertEqual(l.arma.pedido,0)
        e=Inimigo('aranha',l.rect.centerx+25,CHAO)
        self.assertEqual(e.acertar(l.arma,area,False,l),'')
        for _ in range(45):j.update(1/120)
        self.assertEqual(l.arma.serie,1)

    def test_agulha_alcance_cadencia_custo_e_falta_de_energia(self):
        espinho=Lume(200,CHAO);agulha=Lume(200,CHAO)
        agulha.arma.trocar()
        for l in (espinho,agulha):
            l.arma.pedir(False)
            for _ in range(12):l.arma.avancar(1/120,l)
        self.assertEqual((espinho.energia,agulha.energia),(100,100))
        self.assertGreater(agulha.arma.area(agulha).width,espinho.arma.area(espinho).width)
        self.assertGreater(agulha.arma.perfil.total,espinho.arma.perfil.total)
        self.assertFalse(agulha.arma.trocar())
        agulha.arma.cancelar();agulha.energia=1
        agulha.arma.pedir(False,luminoso=True)
        self.assertTrue(agulha.arma.avancar(.01,agulha))
        self.assertEqual((agulha.energia,agulha.vida),(0,93))
        agulha.arma.cancelar()
        agulha.energia=12;agulha.arma.pedir(False,True,luminoso=True)
        self.assertTrue(agulha.arma.avancar(.01,agulha))
        self.assertEqual((agulha.arma.tipo,agulha.energia),('avanco',0))

    def test_oficina_na_app_nao_grava_arma_na_historia_e_alvos_voltam(self):
        from src.main import App
        a=App(temporaria=True)
        try:
            a.iniciar('historia');a.jogar()
            a.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_v))
            self.assertEqual(a.jogo.lume.arma.equipamento,'espinho')
            a.menu();campanha=a.mem.ler('campanha')
            n=next(i for i,e in enumerate(ENSAIOS) if e.nome=='Oficina dos Espinhos')
            a.comecar_ensaio(n)
            a.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_v))
            self.assertEqual(a.jogo.lume.arma.equipamento,'agulha')
            for e in a.jogo.inimigos:e.ativo=False
            a.jogo.lume.energia=20
            a.jogo.update(.02,Comando(interagir=True))
            self.assertTrue(all(e.ativo and e.vida==20 for e in a.jogo.inimigos))
            self.assertGreater(a.jogo.lume.energia,99)
            a.menu();self.assertEqual(a.mem.ler('campanha'),campanha)
            a.iniciar('historia',True)
            self.assertEqual(a.jogo.lume.arma.equipamento,'espinho')
        finally:a.mem.db.close();pygame.quit()

    def test_lista_de_ensaios_mantem_clique_e_leitura_ao_rolar(self):
        from src.main import App
        a=App(temporaria=True)
        try:
            a.mudar('ensaios')
            for n in (0,len(ENSAIOS)-1,len(ENSAIOS)):
                a.selecao=n;a.desenhar()
                self.assertEqual(len(a.alvos),len(ENSAIOS)+1)
                visiveis=[r for r in a.alvos if r.width]
                self.assertEqual(len(visiveis),11)
                self.assertTrue(a.alvos[n].width)
                self.assertTrue(all(157<=r.top and r.bottom<449 for r in visiveis))
            a.selecao=next(i for i,e in enumerate(ENSAIOS) if e.nome=='Casco Oco')
            a.desenhar();r=a.alvos[a.selecao]
            a.evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=r.center))
            self.assertEqual((a.estado,a.jogo.etapa),('jogo',2))
        finally:a.mem.db.close();pygame.quit()


if __name__=='__main__':unittest.main()
