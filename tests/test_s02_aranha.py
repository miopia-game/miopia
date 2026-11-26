"""Escolhas contextualizadas com geometria, memória e sorte reproduzível."""
from collections import Counter
import random
import unittest

import pygame

from src.combate import Inimigo
from src.fases import CHAO, Terreno
from src.travessia import Lume, Comando
from src.ensaios import INDICE_ARANHA, preparar_ensaio
from src.replay_aranha import GravacaoAranha, iterar_reproducao, estado


def solo(largura=800):
    return Terreno(pygame.Rect(0, CHAO, largura, 120), "chao")


class AranhaContextualTest(unittest.TestCase):
    def test_parede_teto_e_borda_excluem_ataques_em_cem_sementes(self):
        lume = Lume(330, CHAO)
        parede = Terreno(pygame.Rect(272, 300, 8, 142), "parede")
        teto = Terreno(pygame.Rect(190, 365, 180, 45), "parede")
        for semente in range(100):
            e = Inimigo("aranha", 220, CHAO, semente=semente)
            with self.subTest(semente=semente):
                self.assertEqual(e.escolher(110, lume, [solo(), parede]), "")
                self.assertEqual(e.escolher(110, lume, [solo(), teto]), "fio")
                self.assertEqual(e.escolher(110, lume, [solo(300)]), "fio")
                self.assertEqual(e.sequencia, 0)

    def test_pesos_continuos_e_frequencias_do_modelo(self):
        lume = Lume(330, CHAO)
        e = Inimigo("aranha", 220, CHAO, semente=20261106)
        pesos = e.pesos_aranha(110, lume, [solo()])
        self.assertAlmostEqual(pesos["fio"], .75)
        self.assertAlmostEqual(pesos["salto"], .5)
        for ultima, repeticoes in (("", 0), ("fio", 1), ("fio", 2)):
            e.ultima_tecnica, e.repeticoes = ultima, repeticoes
            pesos = e.pesos_aranha(110, lume, [solo()])
            observadas = Counter(e.escolher(110, lume, [solo()]) for _ in range(10_000))
            self.assertEqual(set(observadas), {"fio", "salto"})
            for tecnica, peso in pesos.items():
                self.assertLess(abs(observadas[tecnica]/10_000-peso/sum(pesos.values())), .02)
        for dx in (101, 103, 105):
            vizinho = e.pesos_aranha(dx, lume, [solo()])
            self.assertLess(abs(vizinho["fio"]-e.pesos_aranha(dx+2, lume, [solo()])["fio"]), .02)

    def test_memoria_nao_proibe_repetir_ou_elimina_unica_tecnica(self):
        e = Inimigo("aranha", 220, CHAO, semente=1701)
        lume = Lume(330, CHAO)
        e.ultima_tecnica, e.repeticoes = "fio", 1
        primeira = e.pesos_aranha(110, lume, [solo()])
        e.repeticoes = 2
        segunda = e.pesos_aranha(110, lume, [solo()])
        self.assertAlmostEqual(primeira["fio"], .75*.45)
        self.assertAlmostEqual(segunda["fio"], .75*.20)
        self.assertGreater(segunda["fio"], 0)
        lume.rect.centerx = 420
        pesos = e.pesos_aranha(200, lume, [solo()])
        self.assertEqual(pesos["salto"], 0)
        self.assertAlmostEqual(pesos["fio"], 1-50/160)
        self.assertEqual({e.escolher(200, lume, [solo()]) for _ in range(100)}, {"fio"})

    def test_alvo_nao_muda_durante_aviso_nem_le_teclas(self):
        for semente in range(12):
            e = Inimigo("aranha", 220, CHAO, semente=semente)
            lume = Lume(330, CHAO)
            lume.vx = 100
            e.preparar(lume, [solo()])
            alvo, tecnica = e.alvo.copy(), e.tecnica
            lume.rect.centerx = 50
            lume.vx = -250
            for _ in range(37):
                e.update(1/60, lume, 140, False, [solo()])
                self.assertEqual((e.tecnica, e.alvo), (tecnica, alvo))
            self.assertEqual(e.estado, "investida")

    def test_mesma_semente_recomeca_e_ignora_sorte_do_desenho(self):
        e = Inimigo("aranha", 220, CHAO, semente=6)
        lume = Lume(330, CHAO)
        def escolhas():
            resultado = []
            for _ in range(30):
                e.preparar(lume, [solo()])
                resultado.append(e.tecnica)
                random.random()
            return resultado
        primeira = escolhas()
        e.repor()
        self.assertEqual(escolhas(), primeira)
        outra = Inimigo("aranha", 220, CHAO, semente=7)
        self.assertNotEqual([outra.escolher(110, lume, [solo()]) for _ in range(30)], primeira)
        self.assertTrue(any(a == b for a, b in zip(primeira, primeira[1:])))

    def test_recuperacao_nao_atravessa_borda_apos_salto(self):
        for ferida in (False, True):
            e = Inimigo("aranha", 280, CHAO)
            e.tecnica, e.estado = "salto", "recuo"
            e.recuo_ferida = ferida
            e.destino_recuo.update(350, e.rect.centery)
            lume = Lume(400, CHAO)
            for _ in range(20):
                e.update(1/60, lume, 140, False, [solo(310)])
            self.assertLess(e.rect.right, 312)

    def test_entrada_real_reproduz_decisoes_e_estado(self):
        resultados = []
        for semente in (1701, 1702, 1703):
            j = preparar_ensaio(INDICE_ARANHA, "normal", semente)
            g = GravacaoAranha(j)
            for i in range(300):
                g.avancar(j, 1/60, Comando(mover=int(i < 124), salto=i == 34,
                                         segurar_salto=34 <= i < 82))
            dados = g.documento(j, "comparacao_s02")
            copia = preparar_ensaio(INDICE_ARANHA, "normal", semente)
            self.assertEqual(len(list(iterar_reproducao(dados, copia))), 300)
            self.assertEqual(estado(copia), estado(j))
            resultados.append([ev["acao"] for ev in dados["eventos"] if ev["tipo"] == "aviso"])
        self.assertTrue(all(resultados))

    def test_mira_classica_permanece_fixa_com_morcego_mais_rapido(self):
        # O S04 aumentou o vigor do morcego de 385 para 420. A mira continua fixa.
        referencias = {
            "morcego": [(8,"mergulho"),(119,"rasante"),(226,"mergulho"),
                         (330,"rasante"),(436,"mergulho"),(541,"rasante")],
            "vespa": [(8,"ferrao"),(105,"ferrao"),(202,"ferrao"),(299,"ferrao"),
                       (396,"ferrao"),(493,"ferrao"),(590,"ferrao")],
        }
        for tipo, esperados in referencias.items():
            e = Inimigo(tipo, 347, CHAO)
            lume = Lume(151, CHAO)
            obtidos = []
            for i in range(600):
                numero = e.sequencia
                e.update(1/60, lume, 150, False, [])
                if e.sequencia != numero:
                    obtidos.append((i, e.tecnica))
                    self.assertEqual(e.alvo.x, 151)
                    self.assertEqual(e.alvo.y, 400 if e.tecnica == "rasante" else 421)
            self.assertEqual(obtidos, esperados)

    def test_reliquia_aumenta_dano_sem_alterar_pulso(self):
        lume = Lume(220, CHAO)
        lume.bonus_dano = 1.25
        lume.arma.tipo, lume.arma.tempo = "corte1", .08
        e = Inimigo("aranha", 260, CHAO)
        self.assertEqual(e.acertar(lume.arma, lume.arma.area(lume), False, lume), "acerto")
        self.assertAlmostEqual(e.vida, e.max_vida-1.25)
        e.acertar(lume.arma, None, True, lume)
        self.assertAlmostEqual(e.vida, e.max_vida-3.25)

    def test_leve_preserva_aviso_e_golpe_forte_interrompe(self):
        lume = Lume(220, CHAO)
        lume.arma.tipo, lume.arma.tempo = "corte1", .08
        e = Inimigo("aranha", 270, CHAO)
        e.preparar(lume, [solo()])
        tecnica, alvo, espera = e.tecnica, e.alvo.copy(), e.t
        e.acertar(lume.arma, lume.arma.area(lume), False, lume)
        self.assertEqual((e.estado, e.tecnica, e.alvo, e.t), ("aviso", tecnica, alvo, espera))
        self.assertEqual(e.vida, e.max_vida-1)
        for _ in range(37):
            e.update(1/60, lume, 140, False, [solo()])
        self.assertEqual(e.estado, "investida")
        lume.arma.serie += 1
        lume.arma.tipo = "corte3"
        e.acertar(lume.arma, e.rect.copy(), False, lume)
        self.assertEqual(e.estado, "atordoado")
        self.assertEqual(e.vida, e.max_vida-3)

    def test_repetir_leve_na_patrulha_nao_renova_atordoamento(self):
        lume = Lume(220, CHAO)
        lume.arma.tipo, lume.arma.tempo = "corte1", .08
        e = Inimigo("aranha", 270, CHAO)
        e.acertar(lume.arma, e.rect.copy(), False, lume)
        for _ in range(14):
            e.update(1/60, lume, 140, False, [solo()])
        self.assertEqual(e.estado, "recuo")
        espera = e.t
        lume.arma.serie += 1
        e.acertar(lume.arma, e.rect.copy(), False, lume)
        self.assertEqual((e.estado, e.t), ("recuo", espera))

    def test_ler_aviso_permite_vencer_sem_dano_na_mesma_aproximacao(self):
        danos = []
        for ler in (False, True):
            j = preparar_ensaio(INDICE_ARANHA, "normal", 1701)
            e = j.inimigos[0]
            for i in range(94):
                j.update(1/60, Comando(mover=1, salto=i == 34, segurar_salto=34 <= i < 82))
            recebidos = 0
            for i in range(360):
                dx = e.rect.centerx-j.lume.rect.centerx
                mover = 1 if dx > 33 else -1 if dx < -33 else 0
                golpe, salto = i % 17 == 0, False
                if ler and e.estado in ("aviso", "investida"):
                    mover = -1 if dx > 0 else 1
                    salto = e.estado == "aviso" and e.t < .20 and j.lume.chao
                    golpe = False
                j.update(1/60, Comando(mover=mover, golpe=golpe, salto=salto, segurar_salto=salto))
                recebidos += "dano" in j.eventos
                if j.estado != "jogando":
                    break
            self.assertEqual(j.estado, "vitoria")
            danos.append(recebidos)
        self.assertGreater(danos[0], 0)
        self.assertEqual(danos[1], 0)

    def test_aranha_reposiciona_em_vez_de_morrer_ao_spam_parado(self):
        for perseguir in (False, True):
            j = preparar_ensaio(INDICE_ARANHA, "normal", 1701)
            e = j.inimigos[0]
            j.recolocar((j.poleiro-50, CHAO))
            j.lume.iframes = 0
            self.assertFalse(any(t.rect.colliderect(e.rect) for t in j.solidos))
            for i in range(360):
                dx = e.rect.centerx-j.lume.rect.centerx
                mover = (1 if dx > 33 else -1 if dx < -33 else 0) if perseguir else 0
                j.update(1/60, Comando(mover=mover, golpe=i % 17 == 0))
                if j.estado != "jogando":
                    break
            self.assertGreaterEqual(e.sequencia, 2)
            if perseguir:
                self.assertEqual(j.estado, "vitoria")
            else:
                self.assertEqual(j.estado, "jogando")
                self.assertGreater(e.vida, 0)
                self.assertGreater(e.rect.centerx, e.origem[0]+100)


if __name__ == "__main__":
    unittest.main()
