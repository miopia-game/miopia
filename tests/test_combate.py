"""Contragolpes, leitura de alvo, resistência e projéteis nos mesmos passos da partida."""
import unittest
import pygame
from src.combate import ESPECIES, Inimigo, Projetil
from src.travessia import Lume, Comando, Jornada
from src.fases import MEIO, TRANCA_X, VIGIA_X, Terreno, CHAO


class CombateTest(unittest.TestCase):
    def test_encadeia_tres_cortes_sem_drenar_orvalho_ou_repetir_acerto(self):
        l = Lume(210, CHAO)
        e = Inimigo("carabideo",249,CHAO)
        e.frente=1  # O flanco é vulnerável.
        janelas=[]
        for i in range(55):
            if i in (0,11,29): l.arma.pedir(False)
            inicio = l.arma.avancar(1/60, l)
            if inicio: janelas.append(l.arma.tipo)
            e.acertar(l.arma,l.arma.area(l),False,l)
        self.assertEqual(janelas, ["corte1","corte2","corte3"])
        self.assertEqual(l.energia,100)
        self.assertEqual(e.vida,e.max_vida-4)

    def test_queda_rebate_no_mundo(self):
        j = Jornada()
        e = Inimigo("aranha",512,CHAO)
        j.inimigos=[e]
        j.recolocar((512,CHAO-51))
        j.lume.chao=False
        j.update(1/60,Comando(golpe=True,baixo=True))
        eventos=list(j.eventos)
        for _ in range(7):
            j.update(1/60,Comando(baixo=True))
            eventos+=j.eventos
        self.assertIn("rebote",eventos)
        self.assertLess(j.lume.vy,-200)
        self.assertEqual(e.vida,e.max_vida-2)

    def test_patruha_escuta_mas_nao_ataca_atraves_de_parede(self):
        l=Lume(65,CHAO)
        parede=Terreno(pygame.Rect(120,200,28,242),"porta")
        solo=Terreno(pygame.Rect(0,CHAO,500,88),"chao")
        for tipo in ESPECIES:
            e=Inimigo(tipo,210,CHAO)
            sons=[]
            for frame in range(80):
                chamadas,_=e.update(1/60,l,140,False,[parede,solo])
                sons.extend(chamadas)
            self.assertEqual(e.estado,"patrulha",tipo)
            self.assertIn(e.ficha.som,[k for k,_ in sons])
            self.assertTrue(all(x>l.rect.centerx for _,x in sons))

    def test_ataque_trava_alvo_e_avisa_antes_da_investida(self):
        l=Lume(195,CHAO); e=Inimigo("morcego",280,350)
        for _ in range(20):
            e.update(1/60,l,160,False,[])
            if e.estado=="aviso":break
        self.assertEqual(e.estado,"aviso")
        destino=e.alvo.copy()
        l.rect.centerx+=280
        for _ in range(50):
            e.update(1/60,l,160,False,[])
            if e.estado=="investida":break
        self.assertEqual(e.estado,"investida")
        self.assertEqual(e.alvo,destino)
        self.assertLess(e.vetor.x,0)

    def test_rasante_nivelado_passa_por_cima_de_lume_agachado(self):
        for baixo in (True, False):
            l=Lume(190,CHAO)
            l.altura(baixo, [])
            e=Inimigo("morcego",295,350)
            e.sequencia=1
            e.preparar(l)
            self.assertEqual(e.tecnica,"rasante")
            danos=[]
            for _ in range(93):
                _, atingiu=e.update(1/60,l,150,False,[])
                danos.append(atingiu)
            self.assertEqual(any(danos),not baixo)

    def test_intercepta_projeteis_e_bloqueia_somente_armadura_frontal(self):
        l=Lume(178,CHAO); l.arma.tipo="corte1";l.arma.face=1;l.arma.tempo=.1
        golpe=l.arma.area(l)
        fio=Projetil("fio",pygame.Vector2(211,418),pygame.Vector2(-150,0),1.)
        self.assertEqual(fio.avancar(1/60,l,[],golpe,False),"corte")
        e=Inimigo("carabideo",224,CHAO);e.frente=-1
        self.assertEqual(e.acertar(l.arma,golpe,False,l),"bloqueio")
        self.assertEqual(e.vida,e.max_vida)
        l.arma.serie+=1;l.arma.tipo="corte3"
        self.assertEqual(e.acertar(l.arma,golpe,False,l),"acerto")
        self.assertEqual(e.vida,e.max_vida-2)

    def test_fio_ferrao_onda_e_fenda_tem_cada_um_uma_esquiva(self):
        l=Lume(151,CHAO)
        for tipo,tecnica,projetil in (("aranha","fio","fio"),("vespa","ferrao","ferrao"),
                                     ("carabideo","onda","onda"),("sombra","fenda",None)):
            e=Inimigo(tipo,230 if tipo=="carabideo" else 347,CHAO)
            e.preparar(l)
            self.assertEqual(e.tecnica,tecnica)
            e.lancar()
            self.assertEqual([p.tipo for p in e.projeteis],[projetil] if projetil else [])
            if tipo=="sombra":
                l.rect.centerx=465
                self.assertFalse(e.executar_ataque(1/60,l,[]))

    def test_tranca_bloqueia_depois_do_marco_e_guarda_a_vitoria(self):
        from tests.test_travessia import Percurso
        a=Percurso(2)
        j=a.jogo
        a.jogo.recolocar((MEIO, CHAO))
        a.tick()
        self.assertEqual(j.checkpoint, (MEIO, CHAO))
        for _ in range(90):
            a.tick(mover=1)
        self.assertTrue(j.tranca_fechada)
        self.assertLessEqual(j.lume.rect.right, TRANCA_X + .01)
        vigia=next(e for e in j.inimigos if e.guarda)
        self.assertTrue(vigia.ativo)
        j.reiniciar()
        self.assertTrue(j.tranca_fechada)
        self.assertEqual(j.lume.rect.midbottom,(MEIO, CHAO))
        a.sentinela()
        self.assertFalse(j.tranca_fechada)
        recarregado=Jornada.carregar(j.salvar())
        self.assertFalse(recarregado.tranca_fechada)
        self.assertFalse(any(e.origem[0] == VIGIA_X for e in recarregado.inimigos))
        self.assertFalse(any(t.tipo == "tranca" for t in recarregado.solidos))
        anterior=Jornada(etapa=2)
        anterior.flags.add("marco")
        self.assertFalse(Jornada.carregar(anterior.salvar()).tranca_fechada)

    def test_dificuldade_muda_resistencia_e_tempo_de_aviso(self):
        l=Lume(65,CHAO)
        f=Inimigo("aranha",140,CHAO,"fácil")
        d=Inimigo("aranha",140,CHAO,"difícil")
        f.preparar(l);d.preparar(l)
        self.assertGreater(d.vida,f.vida)
        self.assertLess(d.t,f.t)


if __name__=="__main__":
    unittest.main()
