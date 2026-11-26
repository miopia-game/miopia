"""Conversas, entregas e ferramentas dão consequências verificáveis ao trajeto."""
import unittest

from src.narrativa import PEDIDOS
from src.travessia import Comando, Jornada
from tests.test_travessia import Percurso


def conversar(j, nome):
    pessoa = next(o for o in j.objetos if o.tipo == "npc" and o.nome == nome)
    j.interagir(pessoa)
    j.fechar_dialogo()


class MoradoresTest(unittest.TestCase):
    def test_bercario_por_movimento_e_conversa(self):
        a = Percurso()
        a.ir(224)
        a.usar()
        self.assertEqual(a.jogo.dialogo[0], "Nira")
        a.jogo.fechar_dialogo()
        self.assertIn("mapa", a.jogo.pedido_local)
        a.ir(255)
        a.ir(382, pular=True)
        a.ir(550, pular=True)
        a.ir(708, pular=True)
        a.usar()
        self.assertEqual(a.jogo.dialogo[0], "Mapa do berçário")
        a.jogo.fechar_dialogo()
        a.ir(778)
        a.usar()
        self.assertEqual(a.jogo.dialogo[0], "Véspera")
        self.assertEqual(a.jogo.bolsa.estoque["pavio"], 2)
        self.assertEqual(a.jogo.pedido_local, "")
        a.jogo.fechar_dialogo()
        a.usar()
        self.assertEqual(a.jogo.bolsa.estoque["pavio"], 2)

    def test_pedidos_aceitam_evidencia_antes_do_convite_e_preservam_recibos(self):
        for etapa, pedido in enumerate(PEDIDOS):
            with self.subTest(etapa=etapa):
                j = Jornada(etapa=etapa)
                conversar(j, pedido.destino)
                self.assertTrue(j.pedido_local)
                self.assertNotIn("pedido_entregue", j.flags)
                j.flags.update(flag for flag, _ in pedido.passos)
                conversar(j, pedido.destino)
                self.assertIn("pedido_entregue", j.flags)
                for item, quant in pedido.itens:
                    self.assertGreaterEqual(j.bolsa.estoque[item], quant)
                salvo = Jornada.carregar(j.salvar())
                antes = dict(salvo.bolsa.estoque)
                conversar(salvo, pedido.destino)
                self.assertEqual(salvo.bolsa.estoque, antes)
                self.assertTrue(any(t == pedido.titulo + " · entregue" for t, _ in salvo.diario))

    def test_mimo_balsamo_e_acampamento_persistem(self):
        j = Jornada()
        conversar(j, "Mimo")
        self.assertEqual(j.bolsa.quantidade, 2)
        self.assertIsNone(j.usar_item())
        self.assertEqual(j.bolsa.quantidade, 2)
        j.lume.energia = 20
        self.assertEqual(j.usar_item(), "coleta")
        self.assertEqual(j.lume.energia, 55)
        salvo = Jornada.carregar(j.salvar())
        conversar(salvo, "Mimo")
        self.assertEqual(salvo.bolsa.quantidade, 1)
        # A ausência da bolsa em saves existentes preserva a campanha e dá uma carga inicial.
        sem_bolsa = salvo.salvar()
        del sem_bolsa["bolsa"]
        self.assertEqual(Jornada.carregar(sem_bolsa).bolsa.quantidade, 1)

    def test_pavio_congela_no_dialogo_e_casulo_so_absorve_um_golpe(self):
        j = Jornada()
        j.bolsa.receber("pavio", 2)
        j.bolsa.receber("casulo", 1)
        j.trocar_item()
        raio = j.raio
        j.usar_item()
        self.assertEqual(j.bolsa.quantidade, 1)
        self.assertGreater(j.raio, raio)
        j.usar_item()
        self.assertEqual(j.bolsa.quantidade, 1)
        j.dialogo = ("Véspera", "Escute.")
        j.update(.5, Comando())
        j.fechar_dialogo()
        nova = Jornada.carregar(j.salvar())
        self.assertAlmostEqual(nova.bolsa.luz_ate - nova.tempo, 12.)
        nova.trocar_item()
        nova.usar_item()
        nova.lume.iframes = 0
        nova.ferir()
        self.assertFalse(nova.bolsa.escudo)
        self.assertEqual(nova.lume.energia, 100)
        nova.lume.iframes = 0
        nova.ferir()
        self.assertLess(nova.lume.vida, 100)

    def test_resposta_de_eco_precisa_do_no_e_da_luz_perto(self):
        j = Jornada(etapa=2)
        no = next(o for o in j.objetos if o.id == "no")
        j.flags.add("no")
        j.update(1 / 60, Comando(clarao=True))
        self.assertNotIn("chamado_eco", j.flags)
        j.lume.pulso_cd = 0
        j.lume.rect.midbottom = (no.x, no.y)
        j.update(1 / 60, Comando(clarao=True))
        self.assertIn("chamado_eco", j.flags)
        conversar(j, "Risca")
        self.assertEqual(j.bolsa.estoque["casulo"], 2)
        self.assertTrue(any(o.id == "via" for o in j.objetos))

    def test_concha_tem_recarga_e_direcao(self):
        j = Jornada()
        j.bolsa.receber("concha", 1)
        j.trocar_item()
        e = j.inimigos[0]
        j.lume.rect.center = (e.rect.centerx + 80, e.rect.centery)
        self.assertEqual(j.usar_item(), "sino")
        self.assertIn("esquerda", j.aviso)
        self.assertIsNone(j.usar_item())
        j.tempo += 6
        j.lume.rect.centerx = e.rect.centerx - 80
        self.assertEqual(j.usar_item(), "sino")
        self.assertIn("direita", j.aviso)
        self.assertEqual(j.bolsa.quantidade, 1)

    def test_recado_da_gruta_permite_voltar_pelo_poco_e_atalho(self):
        a = Percurso(3)
        a.ir(242)
        a.usar()
        a.jogo.fechar_dialogo()
        a.ir(260)
        a.ir(395, pular=True)
        a.ir(582, pular=True)
        a.usar()
        a.ir(748, pular=True)
        a.usar()
        self.assertEqual(a.jogo.dialogo[0], "Cicatriz por dentro")
        a.jogo.fechar_dialogo()
        a.ir(988)
        a.usar()
        a.esperar(62)
        a.ir(1120)
        a.usar()
        a.ir(1540)
        a.ir(1710, agachar=True)
        a.ir(1848)
        a.ir(1905)
        for x in (2022, 2175, 2315):
            a.ir(x, pular=True)
        a.ir(2530)
        a.tick(baixo=True, salto=True)
        a.esperar(45)
        a.usar()
        self.assertIn("eco_antigo", a.jogo.flags)
        a.ir(2441)
        for x in (2444, 2455, 2455):
            a.ir(x, pular=True)
        a.ir(2310)
        a.ir(1985)
        a.ir(1748)
        a.usar()
        self.assertIn("atalho", a.jogo.flags)
        a.ir(303)
        a.ir(366, pular=True)
        a.usar()
        self.assertEqual(a.jogo.dialogo[0], "Pingo")
        self.assertEqual(a.jogo.bolsa.estoque["pavio"], 2)

    def test_bolsa_de_trilha_so_e_coletada_uma_vez(self):
        j = Jornada()
        reserva = next(o for o in j.objetos if o.tipo == "reserva")
        j.interagir(reserva)
        self.assertNotIn(reserva, j.objetos)
        self.assertEqual(j.bolsa.estoque["casulo"], 1)
        j.interagir(reserva)
        self.assertEqual(j.bolsa.estoque["casulo"], 1)
        nova = Jornada.carregar(j.salvar())
        self.assertNotIn(reserva, nova.objetos)


if __name__ == "__main__":
    unittest.main()
