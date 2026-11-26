import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
import pygame
from src.travessia import Jornada, Comando
from src.descoberta import revelar, conhecida
from src.chefes import Encontro
from src.main import App

class RodadaS03(unittest.TestCase):
    def test_descoberta_persiste_sem_revelar_mecanismo_distante(self):
        j=Jornada(etapa=1);revelar(j)
        self.assertTrue(conhecida(j,*j.lume.rect.center))
        self.assertFalse(conhecida(j,1295,420))
        j.recolocar((1295,442));j.camera=860;revelar(j)
        novo=Jornada.carregar(j.salvar())
        self.assertTrue(conhecida(novo,1295,420))
        legado=j.salvar();legado.pop('explorado')
        self.assertFalse(conhecida(Jornada.carregar(legado),1295,420))

    def test_m_abre_mapa_sem_silenciar_e_r_muda_rastreamento(self):
        a=App(temporaria=True)
        try:
            a.iniciar('historia');a.jogar()
            def tecla(k):a.evento(pygame.event.Event(pygame.KEYDOWN,key=k))
            mudo=a.mem.prefs['mudo'];tecla(pygame.K_m)
            self.assertEqual(a.estado,'diario');self.assertEqual(a.mem.prefs['mudo'],mudo)
            tecla(pygame.K_r);self.assertEqual(a.jogo.missao,'secundaria')
            tecla(pygame.K_m);self.assertEqual(a.estado,'jogo')
            tecla(pygame.K_F10);self.assertNotEqual(a.mem.prefs['mudo'],mudo)
        finally:a.mem.db.close();pygame.quit()

    def test_queda_cobra_vida_e_so_mata_se_ela_acabar(self):
        j=Jornada();vidas=j.lume.vidas;origem=j.lume.rect.midbottom
        j.lume.chao=False;j.lume.rect.top=590;j.update(.02)
        self.assertEqual(j.estado,'jogando');self.assertEqual(j.lume.vidas,vidas)
        self.assertEqual(j.lume.rect.midbottom,origem);self.assertEqual(j.lume.vida,75)
        j.lume.vida=20;j.lume.chao=False;j.lume.rect.top=590;j.update(.02)
        self.assertEqual(j.estado,'caido')

    def test_pavio_estende_clarao_e_resina_reduz_custo(self):
        j=Jornada();j.bolsa.luz_ate=12;j.bolsa.receber('resina',1);j.aplicar_reliquias()
        j.update(1/60,Comando(clarao=True))
        v=j.vestigios[0]
        self.assertEqual(v.duracao,9);self.assertAlmostEqual(j.lume.energia,82,delta=.1)
        self.assertEqual(v.raio(1),520)

    def test_chefe_um_dano_por_arco_critico_maior(self):
        e=Encontro(0,0,442);r=pygame.FRect(e.x-10,e.y-10,20,20)
        corte=pygame.FRect(e.x-40,e.y-40,80,80)
        for _ in range(8):e.update(.01,r,golpe=corte,serie=1)
        self.assertAlmostEqual(e.vida,98.84)
        e.estado='aberto';e.tempo=4
        x,y=e._marca();e.update(.01,pygame.FRect(x-10,330,20,35),golpe=pygame.FRect(x-20,y-10,40,20),serie=2)
        self.assertAlmostEqual(e.vida,64.84)

    def test_avanco_consumo_unico_e_mais_dano(self):
        j=Jornada();j.update(.02,Comando(mover=1,deslize=True,golpe=True,carregado=True))
        self.assertEqual(j.lume.arma.tipo,'avanco')
        self.assertAlmostEqual(j.lume.energia,88,delta=.1)
