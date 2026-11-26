"""Verificações com comandos de jogo e passos reais de física, sem janela."""
import unittest

from src.fases import ARENA, RAIZ, SAIDA, CHAO, FIM_ARENA, Terreno
from src.travessia import Comando, Jornada, Lume
import pygame


class Percurso:
    """Piloto determinístico: anda, espera, salta, usa E; não transmite posições."""
    def __init__(self, etapa=0, modo="historia"):
        self.jogo = Jornada(modo=modo, etapa=etapa)
        self.lume = self.jogo.lume

    def tick(self, **cmd):
        self.jogo.update(1 / 60, Comando(**cmd))

    def ir(self, x, *, pular=False, agachar=False, quadros=420):
        for frame in range(quadros):
            # O piloto agora acompanha vida, separada do brilho no S08. Usa F
            # com cargas reais da bolsa; não restaura recursos artificialmente.
            if self.lume.vida<35 and self.jogo.bolsa.estoque['balsamo']:
                self.tomar_balsamo()
            dx = x - self.lume.rect.centerx
            mover = 0 if abs(dx) < 5 else (1 if dx > 0 else -1)
            self.tick(mover=mover, salto=pular and frame == 0, segurar_salto=pular, baixo=agachar)
            if abs(dx) < 6 and abs(self.lume.vx) < 32 and self.lume.chao and frame > 5:
                return
        raise AssertionError(f"Não chegou em x={x}: {self.lume.rect} ({self.jogo.aviso})")

    def tomar_balsamo(self):
        self.jogo.bolsa.equipado='balsamo';self.jogo.usar_item()

    def usar(self):
        self.tick(interagir=True)

    def esperar(self, quadros):
        for _ in range(quadros):
            self.tick()

    def forquilha(self):
        """Mantém a direção até encostar em cada tronco, então pressiona Espaço."""
        self.ir(2200)
        direcao = 1
        impulsos = []
        for f in range(220):
            parede = self.lume.lado_parede if self.lume.na_parede else 0
            saltar = f==0 or bool(parede and parede != self.lume.ultimo_impulso)
            if parede and saltar:
                direcao = -parede
                impulsos.append(parede)
            if self.lume.rect.bottom <= 195:
                direcao = 1
            self.tick(mover=direcao, salto=saltar, segurar_salto=True)
            if self.lume.rect.centerx >= 2320 and self.lume.rect.bottom < 218:
                break
        if -1 not in impulsos or 1 not in impulsos:
            raise AssertionError(f"Não alternou paredes: {impulsos} {self.lume.rect}")
        self.ir(2379)
        self.usar()
        self.ir(2712)
        self.ir(2950,pular=True)
        self.ir(ARENA-22)

    def comporta(self):
        self.ir(1930)
        self.ir(2020,pular=True)
        self.ir(2160,pular=True)
        self.ir(2316)
        self.tick(baixo=True,salto=True)
        self.esperar(35)
        self.usar()
        self.ir(2440)
        self.ir(2520,pular=True)
        self.ir(2720)
        self.ir(2868,pular=True)
        self.ir(3050)
        self.ir(3280,pular=True)
        self.ir(ARENA-22)

    def sentinela(self):
        if not self.jogo.tranca_fechada:
            return
        vigia = next(e for e in self.jogo.inimigos if e.guarda)
        for n in range(420):
            dx = vigia.rect.centerx - self.lume.rect.centerx
            lado = 1 if dx > 0 else -1
            mover = lado if abs(dx) > 45 or self.lume.face != lado else 0
            self.tick(mover=mover, golpe=abs(dx)<80 and n%11==0)
            if not vigia.ativo:
                return
            if self.jogo.estado != "jogando":
                break
        raise AssertionError(f"Vigia não cedeu à sequência de J: {vigia.vida}, {self.jogo.estado}")

    def sementes(self):
        self.sentinela()
        self.ir(2004)
        self.ir(2110,pular=True)
        self.ir(2275,pular=True)
        self.ir(2474)
        self.ir(2870,pular=True)
        self.ir(2922)
        self.usar()
        self.ir(3080)
        self.ir(3280,pular=True)
        self.ir(ARENA-22)

    def descer_camara(self):
        self.ir(1905)
        self.ir(2022,pular=True)
        self.ir(2175,pular=True)
        self.ir(2315,pular=True)
        self.ir(2530)
        self.tick(baixo=True,salto=True)
        self.esperar(45)
        assert self.lume.rect.bottom == 469

    def fundo_camara(self):
        self.ir(2554)
        self.ir(2618)
        assert self.lume.rect.bottom == 561
        self.tick(baixo=True, salto=True)
        self.esperar(38)
        assert self.lume.rect.bottom == 700
        self.ir(2704)

    def subir_camara(self):
        for x, piso, pular in ((2762, 628, True), (2850, 561, True), (2913, 561, False),
                               (2954, 500, True), (2985, CHAO, True)):
            self.ir(x, pular=pular)
            assert self.lume.rect.bottom == piso

    def camara(self):
        self.descer_camara()
        self.usar()
        self.fundo_camara()
        self.subir_camara()
        self.usar()
        self.ir(3000,pular=True)
        self.ir(3210,pular=True)
        self.ir(3370,pular=True)
        self.ir(ARENA-22)

    def bosque(self):
        self.ir(255)
        self.ir(380, pular=True)
        self.ir(558, pular=True)
        self.ir(990)
        self.usar()
        self.esperar(60)
        self.ir(1125)
        self.usar()
        self.ir(1354)
        self.ir(1523, pular=True)
        self.ir(1848)
        self.forquilha()

    def corrego(self):
        self.ir(82);self.usar()  # Reserva finita do abrigo deste bioma.
        self.ir(273)
        self.ir(426, pular=True)
        self.usar()
        self.ir(831)
        for f in range(65):
            self.tick(mover=1, baixo=True, deslize=f == 0)
            if self.jogo.interacao == "Recolher a lingueta":
                break
        self.tick(interagir=True, baixo=True, mover=1)
        for _ in range(46):
            self.tick(mover=1, baixo=True)
        self.ir(1295)
        self.usar()
        self.ir(1848)
        self.comporta()

    def taquaral(self):
        self.ir(82);self.usar()
        self.ir(830)
        self.usar()
        self.ir(899)
        self.ir(985, pular=True)
        self.ir(1079, pular=True)
        self.ir(1189, pular=True)
        self.ir(1273)
        self.ir(1370, pular=True)
        self.usar()
        self.ir(1578, pular=True)
        self.ir(1763, agachar=True)
        self.ir(1848)
        self.sementes()

    def gruta(self):
        self.ir(82);self.usar()
        self.ir(260)
        self.ir(395, pular=True)
        self.ir(582, pular=True)
        self.usar()
        self.ir(988)
        self.usar()
        self.esperar(62)
        self.ir(1120)
        self.usar()
        self.ir(1540)
        self.ir(1730, agachar=True)
        self.ir(1848)
        self.camara()


class TravessiaTest(unittest.TestCase):
    def test_salto_variavel_e_controle_de_borda(self):
        chao = [Terreno(pygame.Rect(0, CHAO, 80, 90), "chao")]
        def salto(segurar):
            l = Lume(40, CHAO)
            topo = l.rect.bottom
            for f in range(80):
                l.movimento(1/120, Comando(salto=f == 0, segurar_salto=segurar), chao, 0, False)
                topo = min(topo, l.rect.bottom)
            return CHAO - topo
        self.assertGreater(salto(True), 98)
        self.assertLess(salto(False), 30)
        l = Lume(76, CHAO)
        for _ in range(19):
            l.movimento(1/120, Comando(mover=1), chao, 0, False)
        self.assertFalse(l.chao)
        l.movimento(1/120, Comando(salto=True, segurar_salto=True), chao, 0, False)
        self.assertLess(l.vy, -400)

    def test_buffer_e_teto(self):
        chao = [Terreno(pygame.Rect(0, CHAO, 800, 90), "chao")]
        l = Lume(120, CHAO - 5)
        l.chao = False
        l.vy = 170
        for f in range(12):
            l.movimento(1/120, Comando(salto=f == 0, segurar_salto=True), chao, 0, False)
        self.assertLess(l.vy, -350)
        teto = Terreno(pygame.Rect(140, 300, 100, CHAO - 24 - 300), "teto")
        l = Lume(120, CHAO)
        for f in range(24):
            l.movimento(1/120, Comando(mover=1, deslize=f == 0), chao+[teto], 0, False)
        self.assertTrue(140 < l.rect.centerx < 240)
        l.vx = 0
        for _ in range(28):
            l.slide = 0
            l.movimento(1/120, Comando(), chao+[teto], 0, False)
        self.assertEqual(l.rect.h, l.BAIXO)
        parede = Terreno(pygame.Rect(240, 0, 20, CHAO), "porta")
        for _ in range(80): l.movimento(1/120, Comando(mover=1), chao+[teto,parede], 0, False)
        self.assertLessEqual(l.rect.right, 240.01)

    def test_bosque_ate_o_marco(self):
        a = Percurso(0)
        a.bosque()
        self.assertTrue({'marco', 'peca', 'valvula'} <= a.jogo.flags)
        self.assertGreaterEqual(a.jogo.orvalhos, 3)

    def test_corrego_tunel_e_ponte(self):
        a = Percurso(1)
        a.corrego()
        self.assertTrue({'ponte', 'lingueta', 'marco', 'dreno'} <= a.jogo.flags)
        self.assertGreaterEqual(a.jogo.orvalhos, 3)

    def test_taquaral_apoios_e_fonte(self):
        a = Percurso(2)
        a.taquaral()
        self.assertTrue({'no', 'marco', 'brasa'} <= a.jogo.flags)
        self.assertGreaterEqual(a.jogo.orvalhos, 3)

    def test_gruta_roldana_contrapeso_estrado(self):
        a = Percurso(3)
        a.gruta()
        self.assertTrue({'roldana', 'marco', 'contrapeso'} <= a.jogo.flags)
        self.assertGreaterEqual(a.jogo.orvalhos, 3)

    def test_diario_congela_e_restauro_de_sessao(self):
        a = Percurso()
        a.ir(223)
        a.usar()
        self.assertEqual(a.jogo.dialogo[0], "Nira")
        tempo = a.jogo.tempo
        a.esperar(60)
        self.assertEqual(tempo, a.jogo.tempo)
        a.jogo.fechar_dialogo()
        a.jogo.flags.update(("valvula", "peca", "marco", "gota_0", "gota_2"))
        novo = Jornada.carregar(a.jogo.salvar())
        self.assertEqual(novo.checkpoint, (ARENA-20, CHAO))
        self.assertEqual(novo.flags, a.jogo.flags)
        self.assertEqual(novo.diario, a.jogo.diario)
        self.assertEqual(novo.orvalhos, 2)
        novo.lume.energia = 0
        self.assertEqual(novo.raio, 0)

    def test_raiz_e_revisita_recompensam_uma_unica_vez(self):
        a = Percurso()
        j = a.jogo
        j.flags.update(("marco", "valvula", "peca", "chefe", "gota_0", "gota_1"))
        j.recolocar((RAIZ, CHAO))
        a.usar()
        self.assertNotIn("raiz", j.flags)
        j.flags.add("gota_2")
        a.usar()
        pontos = j.pontuacao
        a.usar()
        self.assertEqual(j.pontuacao, pontos)
        self.assertEqual(j.restauradas, 1)
        a.ir(SAIDA)
        a.usar()
        self.assertEqual(j.etapa, 1)
        a.ir(34)
        a.usar()
        self.assertEqual(j.etapa, 0)
        self.assertIn("raiz", j.flags)
        self.assertEqual(j.orvalhos, 3)
        a.ir(SAIDA)
        a.usar()
        self.assertEqual(j.etapa, 1)

    def test_vitoria_e_derrota_da_historia(self):
        j = Jornada(etapa=3)
        j.flags.update(("chefe", "raiz"))
        j.recolocar((SAIDA, CHAO))
        j.update(1/60, Comando(interagir=True))
        self.assertEqual(j.estado,"vitoria")
        j = Jornada()
        j.lume.vida, j.lume.vidas = 0, 1
        j.update(1/30, Comando())
        self.assertEqual(j.estado, "derrota")

    def test_distancia_independe_da_taxa_de_frames(self):
        dif = []
        for hz in (30, 60):
            j = Jornada()
            for _ in range(hz):
                j.update(1/hz, Comando(mover=1))
            dif.append(j.lume.rect.centerx)
        self.assertAlmostEqual(*dif, places=1)

    def test_golpe_pressao_e_recuperacao(self):
        a = Percurso()
        e = a.jogo.inimigos[0]
        a.jogo.recolocar((e.origem[0] - 35, e.origem[1]))
        vida = e.vida
        a.tick(golpe=True)
        self.assertEqual(e.vida, vida)    # antecipação
        a.esperar(4)
        self.assertEqual(e.vida, vida-1)
        a.tick(golpe=True)
        self.assertEqual(e.vida, vida-1)
        a.tick(clarao=True)
        self.assertTrue(e.ativo)
        self.assertEqual(e.vida,1)  # 5 PV: o clarão feriu mais, sem resolver sozinho.
        a.jogo.lume.energia = 100
        a.jogo.ferir()
        energia = a.jogo.lume.energia
        a.jogo.ferir()
        self.assertEqual(a.jogo.lume.energia, energia)

    def test_luz_com_custo_unico(self):
        a = Percurso()
        energia = a.lume.energia
        a.tick(clarao=True)
        self.assertGreaterEqual(energia - a.lume.energia, 22)
        a.tick(clarao=True)
        self.assertLess(energia - a.lume.energia, 22.1)

if __name__ == "__main__":
    unittest.main()
