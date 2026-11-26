"""Feedback humano: planagem, exploração sem portal e recompensas persistentes."""
import unittest

from src import corte_vertical
from src.combate import CORTES, Inimigo
from src.ensaios import ENSAIOS, preparar_ensaio
from src.fases import CHAO
from src.travessia import Comando, Jornada, Lume
from tests.test_travessia import Percurso


class FeedbackS02(unittest.TestCase):
    def test_planeio_de_dez_segundos_independe_da_reserva_de_luz(self):
        for energia in (1., 100.):
            l = Lume(100, 0)
            l.chao = False
            l.vy = 400.
            l.energia = energia
            for _ in range(1200):
                l.movimento(1/120, Comando(segurar_salto=True), (), 0, True)
            self.assertTrue(l.planando)
            self.assertAlmostEqual(l.vy, 76.)
            self.assertEqual(l.energia, energia)
            l.movimento(1/120, Comando(), (), 0, True)
            self.assertFalse(l.planando)
            self.assertGreater(l.vy, 80)

    def test_caminho_continuo_desce_coleta_e_retorna_por_outra_grade(self):
        n = next(i for i,c in enumerate(ENSAIOS) if c.nome == "Raízes do Córrego")
        p = Percurso(1)
        p.jogo = preparar_ensaio(n,"normal")
        p.lume = p.jogo.lume
        identidade = id(p.jogo)
        for piso in (532,622,712,802,892,982,1102):
            p.tick(baixo=True,salto=True)
            p.esperar(70)
            self.assertEqual(p.lume.rect.bottom, piso)
            self.assertFalse(p.jogo.em_vertical)
            self.assertEqual(id(p.jogo), identidade)
            self.assertEqual(p.jogo.etapa,1)
        self.assertGreater(p.jogo.camera_y,600)
        p.ir(2940)
        self.assertEqual(p.jogo.proximo().id,"reliquia_asa")
        p.usar()
        self.assertEqual(p.jogo.bolsa.estoque["asa"],1)
        # Salto duplo do chão ao primeiro galho. A asa aumenta só a corrida.
        for f in range(150):
            p.tick(salto=f in (0,20),segurar_salto=f != 19, golpe=f%17==0)
        self.assertEqual(p.lume.rect.bottom,982)
        for x, piso in ((3010,892),(2890,802),(3010,712),(2890,622),(3030,532),(3030,CHAO)):
            if piso == 532:
                p.ir(3030)  # Encoste na boca do poço antes de saltar sob a terra.
            p.ir(x,pular=True)
            self.assertEqual(p.lume.rect.bottom,piso)
        self.assertFalse(p.jogo.em_vertical)
        self.assertEqual(p.jogo.etapa,1)
        p.esperar(90)
        # S09 mantém um enquadramento inferior ao estar sobre a abertura.
        self.assertGreater(p.jogo.camera_y,90)
        self.assertLess(p.jogo.camera_y,160)
        p.ir(2890)
        p.esperar(90)
        self.assertLess(p.jogo.camera_y,1)
        novo=Jornada.carregar(p.jogo.salvar())
        self.assertEqual(novo.lume.bonus_velocidade,1.12)
        self.assertFalse(any(o.id=="reliquia_asa" for o in novo.objetos))

    def test_reliquias_modificam_dano_velocidade_e_dreno_sem_gastar_carga(self):
        base, melhor = Jornada(), Jornada()
        for item in ("espinho","asa","resina"):
            melhor.bolsa.receber(item,1)
        for j in (base,melhor):
            j.aplicar_reliquias()
            for _ in range(35):
                j.update(1/120,Comando(mover=1))
        self.assertGreater(melhor.lume.vx,base.lume.vx)
        self.assertAlmostEqual(100-melhor.lume.energia,(100-base.lume.energia)*.65)
        for j,multiplicador in ((base,1.),(melhor,1.25)):
            l=j.lume
            e=Inimigo("aranha",l.rect.centerx+38,CHAO)
            l.arma.pedir(False)
            l.arma.avancar(.001,l)
            l.arma.avancar(.06,l)
            e.acertar(l.arma,l.arma.area(l),False,l)
            self.assertEqual(e.max_vida-e.vida,CORTES["corte1"].dano*multiplicador)
        novo=Jornada.carregar(melhor.salvar())
        self.assertEqual([i.id for i in novo.bolsa.reliquias],["espinho","asa","resina"])
        self.assertEqual(novo.lume.bonus_dano,1.25)
        self.assertEqual(novo.lume.bonus_velocidade,1.12)
        for _ in range(12):
            novo.trocar_item()
            self.assertNotIn(novo.bolsa.equipado,("espinho","asa","resina"))

    def test_cipo_trancado_da_uma_acao_e_so_transporta_depois_do_ralo(self):
        j=Jornada()
        corte_vertical.entrar(j,"cisterna")
        carro=next(o for o in j.objetos if o.id=="carro_baixo")
        j.interagir(carro)
        self.assertIsNone(j.destino_vertical)
        self.assertIn("ralo",j.aviso)
        j.cartografia.add("ralo_aberto")
        j.interagir(carro)
        self.assertEqual(j.destino_vertical,316)

    def test_reliquias_do_corte_nao_duplicam_ao_reabrir_o_save(self):
        j=Jornada()
        corte_vertical.entrar(j,"bosque")
        for item in ("espinho","resina"):
            o=next(o for o in j.objetos if o.id=="reliquia_"+item)
            j.interagir(o)
            j.interagir(o)
            self.assertEqual(j.bolsa.estoque[item],1)
        j=Jornada.carregar(j.salvar())
        self.assertFalse(any(o.tipo=="reliquia" for o in j.objetos))
        self.assertEqual(j.lume.bonus_dano,1.25)
        self.assertEqual(j.bolsa.fator_dreno,.65)
