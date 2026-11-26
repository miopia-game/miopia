"""Regras de arena exercitadas com os mesmos comandos discretos da partida."""
import unittest
import pygame

from src.chefes import Encontro


class GuardioesTest(unittest.TestCase):
    def corpo(self, x=50, base=442, altura=35):
        return pygame.FRect(x-10,base-altura,20,altura)

    def ate(self, e, estado, corpo, segundos=9., **entrada):
        for _ in range(round(segundos*60)):
            if e.estado == estado:
                return
            e.update(1/60,corpo,**entrada)
        self.fail(f"{e.nome} não atingiu {estado}; ficou em {e.estado}")

    def marca(self, e):
        x,y=e._marca()
        return pygame.Rect(round(x)-20,round(y)-8,40,16)

    def test_mesmo_arco_nao_tira_vida_a_cada_quadro(self):
        for i in range(4):
            e = Encontro(i,0,442,dificuldade="fácil")
            corpo = self.corpo(365)
            for _ in range(360):
                e.update(1/60,corpo,golpe=pygame.Rect(0,0,760,442),serie=1)
            self.assertEqual(e.progresso,0)
            self.assertEqual(e.vida,98)
            self.assertFalse(e.vencido)

    def test_asa_exige_parede_e_ataque_do_alto(self):
        e = Encontro(0,0,442)
        isca=self.corpo(70,442,18)
        self.ate(e,"aberto",isca)
        self.assertIn("acerto",e.update(1/60,isca,golpe=self.marca(e),serie=1))
        for rodada in range(e.meta):
            self.ate(e,"aberto",isca)
            eventos=e.update(1/60,self.corpo(88,376),golpe=self.marca(e),serie=rodada+2)
            self.assertIn("acerto",eventos)
        self.assertTrue(e.vencido)
        self.assertIn("chefe_resolvido",eventos)

    def test_investida_alta_deixa_passagem_agachada(self):
        for altura,esperado in [(18,False),(38,True)]:
            e=Encontro(0,0,442)
            corpo=self.corpo(72,442,altura)
            danos=0
            for i in range(380):
                eventos=e.update(1/60,corpo)
                danos+=eventos.count("dano_jogador")
                if e.estado=="aberto":
                    break
            self.assertEqual(danos, int(esperado))

    def test_tecela_valvula_limpa_fios_e_rebaixa(self):
        e=Encontro(1,0,442)
        perto=self.corpo(e.valvula)
        self.ate(e,"aviso",perto)
        self.ate(e,"busca",perto)
        self.assertTrue(e.fios)
        for rodada in range(e.meta):
            self.assertIn("água",e.interacao(perto))
            eventos=e.update(1/60,perto,interagir=True)
            self.assertIn("agua",eventos)
            self.assertFalse(e.fios)
            self.ate(e,"aberto",perto)
            self.assertEqual(e.y,411)
            e.update(1/60,self.corpo(e.x),golpe=self.marca(e))
        self.assertTrue(e.vencido)

    def test_casco_precisa_empurrar_semente_e_despertar_brasa(self):
        e=Encontro(2,0,442)
        for rodada in range(e.meta):
            self.assertFalse(e.interacao(self.corpo(e.brasa)))
            corpo=self.corpo(e.barrel_x-20)
            e.update(1/60,corpo,interagir=True)
            self.assertTrue(e.engatado)
            for _ in range(220):
                corpo.x+=3.
                e.update(1/60,corpo,direcao=1)
                if e.assentado:
                    break
            self.assertTrue(e.assentado)
            self.assertEqual(e.barrel_x,e.entalhe)
            eventos=e.update(1/60,self.corpo(e.brasa),interagir=True)
            self.assertIn("seiva",eventos)
            self.ate(e,"aberto",corpo)
            self.assertIn("acerto",e.update(1/60,self.corpo(e.x),golpe=self.marca(e),serie=rodada*2+1))
            # Atingir de baixo não expõe a fraqueza. É necessário outro arco
            # ao saltar, pois o mesmo golpe não pode causar dano duas vezes.
            e.update(1/60,self.corpo(e.x,357),golpe=self.marca(e),serie=rodada*2+2)
        self.assertTrue(e.vencido)

    def test_coruja_escuta_ruido_so_aceita_clarao_acima(self):
        e=Encontro(3,0,442)
        fonte=self.corpo(328)
        self.ate(e,"aviso",fonte,ruido=.9)
        self.assertEqual(e.destino,fonte.centerx)
        self.ate(e,"busca",fonte)
        corda=self.corpo(e.valvula)
        e.update(1/60,corda,interagir=True)
        self.assertTrue(e.sino_movido)
        for rodada in range(e.meta):
            eventos=e.update(1/60,corda,interagir=True)
            self.assertIn("sino",eventos)
            self.ate(e,"aberto",corda)
            self.assertIn("acerto",e.update(1/60, self.corpo(e.dir),clarao=True))
            alto=self.corpo(e.dir-30,376)
            progresso=e.progresso
            e.update(1/60,alto,golpe=self.marca(e),serie=rodada+1)
            self.assertEqual(e.progresso,progresso)  # Corte comum é permitido; crítico exige K.
            eventos=e.update(1/60,alto,clarao=True)
            self.assertIn("acerto",eventos)
        self.assertTrue(e.vencido)

    def test_objetos_e_colisoes_recompostos(self):
        e=Encontro(2,40,442)
        self.assertEqual(len(e.apoios()),5)
        e.tabua_quebrada=True
        e.assentado=True
        e.progresso=1
        self.assertEqual(len(e.apoios()),4)
        novo=Encontro(2,40,442)
        self.assertFalse(novo.assentado)
        self.assertEqual(novo.barrel_x,142)
        self.assertEqual(len(novo.apoios()),5)


if __name__ == "__main__":
    unittest.main()
