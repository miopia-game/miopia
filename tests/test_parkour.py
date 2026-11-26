"""Controles verticais, checkpoints e trajetos novos no mesmo modelo da partida."""
import unittest
import pygame
from src.fases import ARENA, CHAO, MEIO, RAMAIS, Terreno
from src.travessia import Comando, Jornada, Lume
from tests.test_travessia import Percurso


class ParkourTest(unittest.TestCase):
    def test_grade_desce_um_nivel_e_terra_ou_ponte_seguram(self):
        def descer(tipo):
            pisos=[Terreno(pygame.Rect(0,y,250,16),t)
                   for y,t in ((245,tipo),(307,"grade"),(420,"chao"))]
            l=Lume(82,245)
            for i in range(110):
                l.movimento(1/120,Comando(baixo=True,salto=(i==0)),pisos,0,True)
            return round(l.rect.bottom)
        for tipo in ("plataforma","apoio","grade"):
            self.assertEqual(descer(tipo),307)
        for tipo in ("chao","ponte","arena"):
            self.assertEqual(descer(tipo),245)

    def test_lingueta_so_e_alcancada_dentro_da_passagem(self):
        j=Jornada(etapa=1)
        lingueta=next(o for o in j.objetos if o.id=="lingueta")
        teto=next(t.rect for t in j.solidos if t.tipo=="teto" and t.rect.width==200)
        self.assertGreater(lingueta.x-51,teto.left)
        self.assertLess(lingueta.x+51,teto.right)
        self.assertFalse(any(t.tipo=="vedacao" and t.rect.left<900 and t.rect.height>24 for t in j.solidos))
        j.recolocar((lingueta.x,teto.top))
        self.assertIsNone(j.proximo())
        j.flags.add("dreno")
        a=Percurso(1)
        a.corrego()
        self.assertIn("lingueta",a.jogo.flags)

    def test_planeio_continua_ate_o_pouso_sem_consumo_extra(self):
        piso=[Terreno(pygame.Rect(0,CHAO,200,90),"chao")]
        l=Lume(110,112)
        l.chao=False
        for i in range(95): l.movimento(1/120,Comando(segurar_salto=True),piso,0,True)
        self.assertTrue(l.planando)
        self.assertLessEqual(l.vy,80)
        self.assertEqual(l.planeio,Lume.PLANEIO)
        self.assertEqual(l.energia,100.)
        for i in range(80): l.movimento(1/120,Comando(segurar_salto=True),piso,0,True)
        self.assertTrue(l.planando)
        self.assertLessEqual(l.vy,80)
        for i in range(600): l.movimento(1/120,Comando(segurar_salto=True),piso,0,True)
        self.assertTrue(l.chao)
        self.assertFalse(l.planando)
        self.assertEqual(l.planeio,Lume.PLANEIO)

    def test_salto_pela_forquilha_exige_alternar_as_faces(self):
        a=Percurso()
        a.bosque()
        self.assertIn("cunha",a.jogo.flags)
        self.assertEqual(a.jogo.checkpoint,(ARENA-20,CHAO))
        # A face lisa da comporta não dá um impulso de escalada.
        lume=Lume(88,320);lume.chao=False
        fundo=[Terreno(pygame.Rect(100,95,45,347),"vedacao")]
        for i in range(8):
            lume.movimento(1/120,Comando(mover=1,salto=True,segurar_salto=True),fundo,0,True)
        self.assertFalse(lume.na_parede)
        self.assertGreater(lume.vy,0)

    def test_cada_ramal_tem_uma_bolsa_acessivel_por_controles(self):
        for etapa in range(4):
            a=Percurso(etapa)
            # Começar no marco do ramal representa uma sessão salva nesse ponto.
            j=a.jogo
            j.flags.update(("meio",j.fase.passos[-2][0]))
            j=Jornada.carregar(j.salvar())
            a.jogo,a.lume=j,j.lume
            self.assertEqual(j.checkpoint,(MEIO,CHAO))
            if etapa==0:
                a.forquilha()
                a.ir(3450)
                a.ir(3410,pular=True)
                # Voltar pela varanda de bambu do lado de fora.
                a.ir(3090,pular=True)
                a.ir(3040,pular=True)
                a.ir(3210,pular=True)
                a.ir(3390,pular=True)
            elif etapa==1:
                a.ir(1930);a.ir(2015,pular=True);a.ir(2160,pular=True)
                a.ir(2070,pular=True)
            elif etapa==2:
                a.sementes()
                a.ir(3475);a.ir(3277);a.ir(3277,pular=True);a.ir(3400,pular=True)
            else:
                a.ir(1905);a.ir(2022,pular=True);a.ir(2175,pular=True);a.ir(2310,pular=True)
            o=j.proximo()
            self.assertIsNotNone(o,(etapa,a.lume.rect))
            self.assertEqual(o.id,"reserva",(etapa,o,a.lume.rect))
            a.usar()
            self.assertIn("reserva",j.flags)

    def test_volta_da_camara_com_a_saida_ainda_trancada(self):
        for etapa in (1,3):
            a=Percurso(etapa)
            a.jogo.flags.add("meio")
            a.jogo=Jornada.carregar(a.jogo.salvar())
            a.lume=a.jogo.lume
            if etapa==1:
                a.ir(1930);a.ir(2020,pular=True);a.ir(2160,pular=True);a.ir(2316)
            else:
                a.ir(1905);a.ir(2022,pular=True);a.ir(2175,pular=True)
                a.ir(2315,pular=True);a.ir(2530)
            a.tick(baixo=True,salto=True)
            a.esperar(55)
            a.usar()
            self.assertNotIn(a.jogo.fase.preparo,a.jogo.flags)
            if etapa==1:
                a.ir(2227,pular=True);a.ir(2162,pular=True)
            else:
                a.ir(2450,pular=True);a.ir(2462,pular=True);a.ir(2380,pular=True)
            a.ir(2060)
            self.assertLess(a.lume.rect.centerx,2070)

    def test_save_v1_para_o_marco_novo_sem_perder_o_progresso(self):
        j=Jornada()
        j.flags.update(("peca","marco","gota_2","registro","atalho"))
        dados=j.salvar();dados["versao"]=1
        novo=Jornada.carregar(dados)
        self.assertEqual(novo.checkpoint,(ARENA-20,CHAO))
        self.assertEqual(novo.lume.rect.midbottom,novo.checkpoint)
        self.assertTrue({"meio",RAMAIS[0].objetivo.id,"peca","registro","gota_2","atalho"}<=novo.flags)
        self.assertNotIn("chefe",novo.flags)

    def test_cair_do_ramal_exibe_morte_e_marco_guarda_portas(self):
        j=Jornada(); j.flags.update(("meio","peca"));j=Jornada.carregar(j.salvar())
        j.lume.vida=20
        j.lume.rect.centerx=3500  # O antigo ponto agora está dentro da galeria contínua.
        j.lume.rect.top=590; j.update(.02)
        self.assertEqual(j.estado,"caido")
        j.reiniciar()
        self.assertEqual(j.lume.rect.midbottom,(MEIO,CHAO))
        self.assertIn("peca",j.flags)
        self.assertEqual(j.estado,"jogando")
