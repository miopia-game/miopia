"""Repete a aranha do Bosque no laço real e registra o custo de cada quadro em JSON."""
import argparse
import json
import os
from pathlib import Path
from statistics import mean
from tempfile import TemporaryDirectory
from time import perf_counter

from src.main import App
from tools.gravar_fauna import amostra, controles, preparar


def medir():
    app = App(temporaria=True)
    jogo, aranha = preparar(app, 1)
    atualizar, desenhar, apresentar = app.atualizar, app.desenhar, app.janela.apresentar
    quadros = []
    ultimo = inicio = fim_ia = fim_desenho = perf_counter()

    def atualizar_medido(dt):
        nonlocal inicio, fim_ia
        inicio = perf_counter()
        fase = amostra(jogo, aranha, False)[0]
        atualizar(dt, presso=controles(app, 1, len(quadros), fase, aranha))
        fim_ia = perf_counter()

    def desenhar_medido():
        nonlocal fim_desenho
        desenhar()
        fim_desenho = perf_counter()

    def apresentar_medido(superficie):
        nonlocal ultimo
        enviado = apresentar(superficie)
        fim = perf_counter()
        fase, tecnica, _, visivel = amostra(jogo, aranha, False)
        quadros.append({
            "n": len(quadros) + 1, "estado": app.estado, "fase": fase, "tecnica": tecnica,
            "aranha_na_cena": visivel, "enviado": enviado,
            "intervalo_ms": round((fim - ultimo) * 1000, 3),
            "entrada_e_espera_ms": round((inicio - ultimo) * 1000, 3),
            "atualizacao_ms": round((fim_ia - inicio) * 1000, 3),
            "desenho_ms": round((fim_desenho - fim_ia) * 1000, 3),
            "apresentacao_ms": round((fim - fim_desenho) * 1000, 3),
        })
        ultimo = fim
        if len(quadros) >= 300:
            app.rodando = False

    app.atualizar = atualizar_medido
    app.desenhar = desenhar_medido
    app.janela.apresentar = apresentar_medido
    app.rodar()
    amostras = quadros[60:]
    if len(amostras) != 240 or any(q["estado"] != "jogo" for q in quadros):
        raise RuntimeError("A luta foi interrompida.")
    if not any(q["fase"] == "ataque" and q["aranha_na_cena"] for q in amostras):
        raise RuntimeError("Nenhum ataque da aranha foi registrado na cena.")
    return {
        "fps_do_laco": round(1000 / mean(q["intervalo_ms"] for q in amostras), 2),
        "envios_apos_aquecimento": sum(q["enviado"] for q in amostras),
        "pior_apos_aquecimento": max(amostras, key=lambda q: q["intervalo_ms"]),
        "quadros": quadros,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeticoes", type=int, default=3)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()
    if args.repeticoes < 1:
        parser.error("Use pelo menos uma repetição.")
    with TemporaryDirectory() as perfil:
        os.environ["MIOPIA_DADOS"] = perfil
        rodadas = [medir() for _ in range(args.repeticoes)]
    args.saida.write_text(json.dumps(rodadas, ensure_ascii=False, indent=2), encoding="utf-8")
