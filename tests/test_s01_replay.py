"""Reprodução dos comandos reais do duelo, independente do save e de dispositivos SDL."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.ensaios import INDICE_ARANHA, preparar_ensaio
from src import replay_aranha as replay
from src.travessia import Comando


def sala(semente=1701):
    return preparar_ensaio(INDICE_ARANHA, "normal", semente=semente)


def percorrer(saltar):
    j = sala()
    registro = replay.GravacaoAranha(j)
    for i in range(300):
        cmd = Comando(mover=int(i < 124), salto=saltar and i == 34,
                      segurar_salto=saltar and 34 <= i < 82)
        registro.avancar(j, 1/60, cmd)
    return j, registro


class ReplayDaAranhaTest(unittest.TestCase):
    def test_barreira_e_pulo_geram_dois_contextos_reprodutiveis(self):
        curvas = []
        for saltar in (False, True):
            j, registro = percorrer(saltar)
            dados = registro.documento(j, "saida")
            dados = json.loads(json.dumps(dados))
            repetido = sala()
            tempos = list(replay.iterar_reproducao(dados, repetido))
            self.assertEqual(tempos, [1/60]*300)
            self.assertEqual(replay.estado(repetido), replay.estado(j))
            curvas.append(dados)
        protegida, exposta = curvas
        self.assertLess(protegida["fim"]["lume"][0], 335)
        self.assertEqual(protegida["eventos"], [])
        self.assertIsNone(protegida["primeiro_impacto"])
        escolhas = [ev for ev in exposta["eventos"] if ev["tipo"] == "aviso"]
        self.assertGreaterEqual(len(escolhas), 2)
        self.assertEqual({ev["acao"] for ev in escolhas}, {"fio", "salto"})
        self.assertTrue(any(ev["alvo"] != ev["observado"] for ev in escolhas))
        self.assertLess(escolhas[0]["instante_aviso"], exposta["primeiro_impacto"]["tempo"])
        self.assertEqual(exposta["primeiro_impacto"]["atingido"], "Lume")

    def test_verifica_eventos_estado_e_semente(self):
        j, registro = percorrer(True)
        dados = registro.documento(j, "pausa")
        for campo in ("inicio", "eventos", "fim", "primeiro_impacto", "assinatura"):
            invalido = deepcopy(dados)
            if campo == "eventos":
                invalido["eventos"][0]["observado"] = [1, 1]
            else:
                invalido[campo] = "outra versão" if campo == "assinatura" else {}
            with self.subTest(campo=campo), self.assertRaises(ValueError):
                list(replay.iterar_reproducao(invalido, sala()))
        with self.assertRaises(ValueError):
            list(replay.iterar_reproducao(dados, sala(1800)))

    def test_acoes_imediatas_e_dt_variavel_na_ordem(self):
        j = sala()
        g = replay.GravacaoAranha(j)
        g.acao(j, "trocar_item")
        g.avancar(j, .017, Comando(mover=1))
        g.acao(j, "usar_item")
        g.avancar(j, .032, Comando(salto=True, segurar_salto=True))
        g.acao(j, "trocar_item")
        dados = g.documento(j, "saida")
        self.assertEqual([x.get("acao") for x in dados["entradas"]],
                         ["trocar_item", None, "usar_item", None, "trocar_item"])
        self.assertEqual(list(replay.iterar_reproducao(dados, sala())), [.017, .032])
        g.avancar(j, .016, Comando())
        self.assertEqual(len(dados["entradas"]), 5)

    def test_compressao_limite_e_rejeicao_sem_expandir(self):
        j = sala()
        g = replay.GravacaoAranha(j)
        with patch.object(replay, "MAX_PASSOS", 3):
            for _ in range(6):
                g.avancar(j, 1/60, Comando(mover=1))
            dados = g.documento(j, "saida")
            self.assertEqual(dados["fim"]["motivo"], "limite")
            self.assertLess(dados["fim"]["tempo"], j.tempo)
            self.assertEqual(dados["entradas"], [{"dt":1/60, "vezes":3, "comando":{"mover":1}}])
            self.assertEqual(len(list(replay.iterar_reproducao(dados, sala()))), 3)
            dados["entradas"][0]["vezes"] = 10**9
            with self.assertRaisesRegex(ValueError, "máximo"):
                replay.validar(dados)
            for cmd in ({"mover": 3}, {"clarao": "sim"}, {"codigo": "qualquer"}):
                dados["entradas"][0].update(vezes=3, comando=cmd)
                with self.assertRaisesRegex(ValueError, "Tecla"):
                    replay.validar(dados)

    def test_tentativas_concorrentes_nao_sobrescrevem(self):
        j, g = percorrer(True)
        with TemporaryDirectory() as tmp, patch.object(replay, "MAX_ARQUIVOS", 2):
            pasta = Path(tmp) / "replays"
            def gravar(motivo):
                return replay.gravar_tentativa(g, j, motivo, pasta)
            with ThreadPoolExecutor(max_workers=2) as executor:
                arquivos = list(executor.map(gravar, ["saida", "repetir"]))
            self.assertEqual(len(set(arquivos)), 2)
            antes = [p.read_bytes() for p in arquivos]
            with self.assertRaisesRegex(OSError, "ocupados"):
                gravar("saida")
            self.assertEqual(antes, [p.read_bytes() for p in arquivos])
            self.assertEqual(set(pasta.iterdir()), set(arquivos))
            for arq, motivo in zip(arquivos, ("saida", "repetir")):
                dados = replay.ler_tentativa(arq)
                self.assertEqual(dados["fim"]["motivo"], motivo)
                self.assertEqual(len(list(replay.iterar_reproducao(dados, sala()))), 300)


if __name__ == "__main__":
    unittest.main()
