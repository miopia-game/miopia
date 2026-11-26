import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import unittest
import pygame
from src.travessia import Jornada,Lume,Comando
from src.fases import Terreno,CHAO
from src.descoberta import revelar,conhecida
from src.visao import ponto_visivel
from src.taticas import Habitante,RECEITAS,FAMILIAS
from src.paisagem import aplicar_nevoa


class VisaoS04(unittest.TestCase):
    def test_s08_luz_atravessa_teto_mas_nao_ultrapassa_o_alcance(self):
        class Camara(Jornada):
            @property
            def solidos(self):return (Terreno(pygame.Rect(0,320,600,20),"plataforma"),)
        j=Camara();j.recolocar((220,442))
        for _ in range(30):revelar(j)
        self.assertTrue(conhecida(j,220,410))
        self.assertTrue(ponto_visivel(j,(220,298)))
        self.assertTrue(conhecida(j,220,298))
        self.assertFalse(ponto_visivel(j,(220,220)))
        self.assertFalse(conhecida(j,220,220))
        j.recolocar((220,310));revelar(j)
        self.assertTrue(conhecida(j,220,298))
        salvo=Jornada.carregar(j.salvar())
        self.assertEqual(salvo.explorado,j.explorado)

    def test_terreno_fora_da_luz_nao_vaza_silhueta(self):
        pygame.init();self.addCleanup(pygame.quit)
        fundo=pygame.Surface((960,540));fundo.fill((40,80,120))
        a=fundo.copy();b=fundo.copy()
        pygame.draw.rect(b,(255,255,20),(500,200,230,25))
        luz=pygame.Surface((960,540));luz.fill((0,0,0))
        aplicar_nevoa(a,luz,fundo=fundo);aplicar_nevoa(b,luz,fundo=fundo)
        self.assertTrue(pygame.image.tobytes(a,"RGB")==pygame.image.tobytes(b,"RGB"))
        pygame.draw.rect(b,(255,255,20),(500,200,230,25))
        luz.fill((255,255,255));aplicar_nevoa(b,luz,fundo=fundo)
        # A informação passa a aparecer quando existe luz na mesma composição.
        self.assertNotEqual(a.get_at((550,210)),b.get_at((550,210)))

    def test_mapa_antigo_nao_importa_os_blocos_grandes_que_revelavam_tetos(self):
        j=Jornada();d=j.salvar();d.pop("mapa_grade");d["explorado"]=["0:0/1/1"]
        self.assertFalse(Jornada.carregar(d).explorado)


class TaticasS04(unittest.TestCase):
    def test_vinte_sequencias_distintas_e_selecionaveis_por_especie(self):
        self.assertEqual(len({c.passos for c in RECEITAS}),20)
        piso=(Terreno(pygame.Rect(0,CHAO,1000,90),"chao"),)
        for tipo in FAMILIAS:
            with self.subTest(tipo=tipo):
                e=Habitante(tipo,350,CHAO,semente=731)
                l=Lume(245,CHAO)
                escolhas={e.escolher_combo(l,piso) for _ in range(1600)}
                self.assertEqual(escolhas,set(range(20)))

    def test_parede_bloqueia_planejamento_e_alvo_nao_persegue_no_aviso(self):
        e=Habitante("vespa",350,350,semente=8);l=Lume(240,CHAO)
        parede=(Terreno(pygame.Rect(290,0,20,CHAO),"parede"),)
        self.assertEqual(e.escolher_combo(l,parede),-1)
        e.plano=[1];e.preparar(l,())
        alvo=tuple(e.alvo);l.rect.x-=100
        for _ in range(8):e.update(1/120,l,150,False,())
        self.assertEqual(tuple(e.alvo),alvo)

    def test_flanco_e_movimento_fisico_sem_teleporte_atraves_da_parede(self):
        e=Habitante("aranha",250,CHAO,semente=3);l=Lume(310,CHAO)
        pisos=(Terreno(pygame.Rect(0,CHAO,650,100),"chao"),Terreno(pygame.Rect(330,0,22,CHAO),"parede"))
        e.plano=["flanco",3];e.preparar(l,pisos)
        anterior=e.rect.x
        for _ in range(40):
            e.update(1/120,l,150,False,pisos)
            self.assertLessEqual(abs(e.rect.x-anterior),3)
            self.assertLessEqual(e.rect.right,330)
            anterior=e.rect.x

    def test_campanha_tem_duplas_e_reinicio_repete_escolha(self):
        j=Jornada();self.assertTrue(all(isinstance(e,Habitante) for e in j.inimigos))
        dupla=[e for e in j.inimigos if 1500<e.rect.centerx<1720]
        self.assertGreaterEqual(len(dupla),2)
        e=dupla[0];l=Lume(e.rect.centerx-100,CHAO)
        a=[e.escolher_combo(l,()) for _ in range(12)]
        e.repor();self.assertEqual(a,[e.escolher_combo(l,()) for _ in range(12)])

    def test_familias_executam_com_aviso_e_sem_coordenadas_invalidas(self):
        piso=(Terreno(pygame.Rect(0,CHAO,1000,90),"chao"),)
        for tipo in FAMILIAS:
            for familia in range(5):
                with self.subTest(tipo=tipo,familia=familia):
                    e=Habitante(tipo,350,CHAO,semente=10);l=Lume(245,CHAO)
                    e.plano=[familia];som=e.preparar(l,piso)
                    self.assertEqual(som,f'aviso_{tipo}_{familia}');self.assertEqual(e.estado,"aviso")
                    self.assertGreaterEqual(e.t,.36)
                    chegou=False
                    for _ in range(160):
                        e.update(1/120,l,150,False,piso)
                        self.assertTrue(all(-2000<v<2000 for v in (*e.rect.center,*e.alvo)))
                        if e.estado=="investida":chegou=True
                        if chegou and e.estado=="recuo":break
                    self.assertTrue(chegou)
