"""Mede um encontro da fauna no laço da App e registra o custo de cada quadro em JSON."""
import argparse
import json
import os
from pathlib import Path
from statistics import mean
from tempfile import TemporaryDirectory
from time import perf_counter

import pygame

from src.main import App
from tools.gravar_fauna import NOMES, amostra, chefe, controles, preparar


def medir(indice=1, total=300):
    app = App(temporaria=True)
    driver = pygame.display.get_driver()
    jogo, criatura = preparar(app, indice)
    atualizar, desenhar, apresentar = app.atualizar, app.desenhar, app.janela.apresentar
    quadros = []
    ultimo = inicio = fim_ia = fim_desenho = perf_counter()

    def atualizar_medido(dt):
        nonlocal inicio, fim_ia
        inicio = perf_counter()
        fase = amostra(jogo, criatura, chefe(indice))[0]
        atualizar(dt, presso=controles(app, indice, len(quadros), fase, criatura))
        fim_ia = perf_counter()

    def desenhar_medido():
        nonlocal fim_desenho
        desenhar()
        fim_desenho = perf_counter()

    def apresentar_medido(superficie):
        nonlocal ultimo
        enviado = apresentar(superficie)
        fim = perf_counter()
        fase, tecnica, _, visivel = amostra(jogo, criatura, chefe(indice))
        quadros.append({
            "n": len(quadros) + 1, "estado": app.estado, "fase": fase, "tecnica": tecnica,
            "criatura_na_cena": visivel, "enviado": enviado,
            "intervalo_ms": round((fim - ultimo) * 1000, 3),
            "entrada_e_espera_ms": round((inicio - ultimo) * 1000, 3),
            "atualizacao_ms": round((fim_ia - inicio) * 1000, 3),
            "desenho_ms": round((fim_desenho - fim_ia) * 1000, 3),
            "apresentacao_ms": round((fim - fim_desenho) * 1000, 3),
        })
        if indice == 1:
            quadros[-1]["aranha_na_cena"] = visivel
        ultimo = fim
        if len(quadros) >= total:
            app.rodando = False

    app.atualizar = atualizar_medido
    app.desenhar = desenhar_medido
    app.janela.apresentar = apresentar_medido
    app.rodar()
    amostras = quadros[60:]
    if len(amostras) != total - 60 or any(q["estado"] != "jogo" for q in quadros):
        raise RuntimeError("A luta foi interrompida.")
    if not any(q["fase"] == "ataque" and q["criatura_na_cena"] for q in amostras):
        raise RuntimeError(f"Nenhum ataque visível no encontro {NOMES[indice]}.")
    return {
        "encontro": NOMES[indice],
        "driver": driver,
        "fps_do_laco": round(1000 / mean(q["intervalo_ms"] for q in amostras), 2),
        "envios_apos_aquecimento": sum(q["enviado"] for q in amostras),
        "pior_apos_aquecimento": max(amostras, key=lambda q: q["intervalo_ms"]),
        "quadros": quadros,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeticoes", type=int, default=3)
    parser.add_argument("--encontro", choices=NOMES, default=NOMES[1])
    parser.add_argument("--quadros", type=int, default=300)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()
    if args.repeticoes < 1:
        parser.error("Use pelo menos uma repetição.")
    if args.quadros <= 60:
        parser.error("O encontro deve continuar após os 60 quadros de aquecimento.")
    with TemporaryDirectory() as perfil:
        os.environ["MIOPIA_DADOS"] = perfil
        rodadas = [medir(NOMES.index(args.encontro), args.quadros) for _ in range(args.repeticoes)]
    args.saida.write_text(json.dumps(rodadas, ensure_ascii=False, indent=2), encoding="utf-8")
