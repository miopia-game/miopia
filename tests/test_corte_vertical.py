"""Rotas por entradas normais, sem teletransportar Lume entre os patamares."""
import unittest
from tests.test_travessia import Percurso
from tests.test_campanha import resolver_arena
from src.travessia import Jornada
from src.fases import CHAO, RAIZ, SAIDA
from src import corte_vertical as corte


class CorteTest(unittest.TestCase):
    def entrar(self):
        p=Percurso()
        p.ir(630)
        self.assertEqual(p.jogo.interacao,"Entrar no Corte da Figueira")
        p.usar()
        self.assertTrue(p.jogo.em_vertical)
        return p

    def descer(self,p,quantidade):
        for _ in range(quantidade):
            p.tick(baixo=True,salto=True)
            p.esperar(60)

    def entrar_cisterna(self,p):
        p.ir(690)
        self.descer(p,6)
        p.ir(286)
        p.usar()
        self.assertEqual(p.jogo.checkpoint,corte.MARCOS["poco"])
        p.ir(571)
        self.descer(p,1)
        p.ir(609)
        self.descer(p,3)
        p.ir(455)
        self.assertEqual(p.jogo.setor_vertical,"Cisterna das Duas Margens")

    def test_copa_acima_da_superficie_e_saida_diferente(self):
        p=self.entrar()
        inicio=p.jogo.camera_y
        self.assertNotIn("atalho_copa",p.jogo.cartografia)
        p.ir(480)
        for x in (500,447,505,560,500,425,500,524):
            p.ir(x,pular=True)
        self.assertEqual(p.lume.rect.bottom,316)
        self.assertGreater(inicio-p.jogo.camera_y,620)
        self.assertEqual(p.jogo.setor_vertical,"Copa do Observatório")
        p.usar()
        self.assertIn("atalho_copa",p.jogo.cartografia)
        self.assertEqual(p.jogo.bolsa.estoque["pavio"],1)
        p.jogo.fechar_dialogo()
        p.usar();p.jogo.fechar_dialogo()
        self.assertEqual(p.jogo.bolsa.estoque["pavio"],1)
        p.ir(711);p.ir(808);p.ir(918,pular=True);p.ir(1220);p.usar()
        self.assertFalse(p.jogo.em_vertical)
        self.assertEqual(p.lume.rect.midbottom,(1320,CHAO))
        self.assertEqual(p.jogo.interacao,"Voltar ao Observatório da Copa")
        p.usar()
        self.assertTrue(p.jogo.em_vertical)
        self.assertEqual(p.jogo.checkpoint,corte.MARCOS["copa"])
        self.assertEqual(p.lume.rect.midbottom,(1220,316))
        self.assertEqual(p.jogo.camera_y,10)

    def test_descida_luz_contrapeso_e_bloqueio_de_historia(self):
        p=self.entrar()
        self.entrar_cisterna(p)
        p.usar()
        self.assertNotIn("ralo_aberto",p.jogo.cartografia)
        p.tick(clarao=True);p.esperar(22);p.usar()
        self.assertIn("ralo_aberto",p.jogo.cartografia)
        p.jogo.fechar_dialogo()
        p.ir(899);p.ir(1040,pular=True);p.ir(1225);p.usar()
        self.assertTrue(p.jogo.em_vertical)
        self.assertNotIn((0,1),p.jogo.historico)
        p.ir(1040);p.usar()
        antes=p.jogo.camera_y
        p.esperar(90)
        self.assertIsNotNone(p.jogo.destino_vertical)
        self.assertGreater(antes-p.jogo.camera_y,140)
        p.esperar(250)
        self.assertIsNone(p.jogo.destino_vertical)
        self.assertEqual(p.lume.rect.midbottom,(1040,316))
        self.assertGreater(antes-p.jogo.camera_y,1250)
        self.assertTrue({"viu_copa","viu_galeria","viu_poco","viu_cisterna"}<=p.jogo.cartografia)

    def test_desvio_do_arquivo_marco_e_retomada(self):
        p=self.entrar()
        p.ir(690)
        self.descer(p,2)
        p.ir(173);p.usar()
        self.assertEqual(p.jogo.setor_vertical,"Arquivo da Casca")
        self.assertEqual(p.jogo.dialogo[0],"A cama dobrada")
        self.assertEqual(p.jogo.bolsa.estoque["balsamo"],2)
        p.jogo.fechar_dialogo()
        p.usar();p.jogo.fechar_dialogo()
        self.assertEqual(p.jogo.bolsa.estoque["balsamo"],2)
        p.ir(339);p.ir(474,pular=True);p.ir(690);self.descer(p,4);p.ir(286);p.usar()
        p.jogo.perder_fagulha("queda")
        p.jogo.reiniciar()
        self.assertEqual(p.lume.rect.midbottom,(286,1492))
        salvo=Jornada.carregar(p.jogo.salvar())
        self.assertEqual(salvo.cartografia,p.jogo.cartografia)
        self.assertEqual(salvo.lume.rect.midbottom,(286,1492))
        self.assertEqual(salvo.bolsa.estoque,p.jogo.bolsa.estoque)
        self.assertTrue(salvo.em_vertical)
        self.assertTrue(salvo.visivel(salvo.lume.rect.center))

    def test_cisterna_retorna_a_um_corrego_aberto_pela_campanha(self):
        p=Percurso()
        p.bosque();resolver_arena(p);p.ir(RAIZ);p.usar();p.ir(SAIDA);p.usar()
        self.assertEqual(p.jogo.etapa,1)
        p.ir(660);p.usar()
        self.assertTrue(p.jogo.em_vertical)
        self.assertEqual(p.lume.rect.midbottom,corte.MARCOS["corrego"])
        p.usar()
        self.assertFalse(p.jogo.em_vertical)
        p.usar()
        p.ir(1024);p.ir(890,pular=True);p.ir(455)
        p.tick(clarao=True);p.esperar(24);p.usar();p.jogo.fechar_dialogo()
        p.ir(899);p.ir(1040,pular=True);p.usar();p.esperar(330)
        p.ir(914);p.ir(808);p.ir(702);p.ir(576,pular=True);p.ir(524)
        p.usar();p.jogo.fechar_dialogo()
        p.ir(711);p.ir(808);p.ir(918,pular=True);p.ir(1220);p.usar()
        self.assertFalse(p.jogo.em_vertical)
        self.assertEqual(p.jogo.etapa,0)
        p.usar();p.ir(1040);p.usar();p.esperar(330)
        p.ir(1225);p.usar()
        self.assertFalse(p.jogo.em_vertical)
        self.assertEqual(p.jogo.etapa,1)
        self.assertIn("raiz",p.jogo.historico[(0,0)])
        self.assertEqual(p.lume.rect.midbottom,(660,CHAO))

    def test_save_anterior_preserva_superficie_e_recusa_modo_removido(self):
        j=Jornada()
        anterior=j.salvar()
        anterior["versao"]=2
        anterior.pop("corte")
        novo=Jornada.carregar(anterior)
        self.assertFalse(novo.em_vertical)
        self.assertFalse(novo.cartografia)
        with self.assertRaises(ValueError):Jornada('infinito')

if __name__=="__main__":
    unittest.main()
