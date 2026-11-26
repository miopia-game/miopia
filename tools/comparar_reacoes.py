"""Compara a mesma partida com e sem a contribuição local de passagem e reflexo."""

import argparse
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest.mock import patch

import imageio_ffmpeg

from src import agua_pintada
from src.passagem_lume import Passagem
from tools.gravar_pinturas import gravar, TRECHOS

# Cada par de recortes é idêntico. Na Gruta o detalhe é ampliado 2× para ver a gota.
RECORTES = {
    "bosque": ("Bosque", (320, 530, 960, 540), "Só vento", "Passagem de Lume"),
    "taquaral": ("Taquaral", (0, 520, 960, 540), "Só vento", "Passagem de Lume"),
    "corrego": (
        "Córrego",
        (560, 530, 960, 540),
        "Sem reflexo na água",
        "Com reflexo na água",
    ),
    "gruta": (
        "Gruta  2×",
        (865, 590, 480, 270),
        "Sem reflexo na gota",
        "Com reflexo na gota",
    ),
}


def controle(destino):
    with (
        TemporaryDirectory(prefix="miopia-perfil-") as perfil,
        patch.dict(
            os.environ,
            {
                "MIOPIA_DADOS": perfil,
                "SDL_VIDEODRIVER": "dummy",
                "SDL_AUDIODRIVER": "dummy",
            },
        ),
        patch.object(Passagem, "flexao", lambda *a, **kw: 0.0),
        patch.object(agua_pintada, "luz_da_fagulha", lambda *a: None),
    ):
        for i, (nome, _) in enumerate(TRECHOS):
            gravar(i, destino / nome, "filme", reacoes=True)


def comparar(jogo, referencia, destino, pasta):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    fonte = (
        Path(__file__).resolve().parents[1] / "assets" / "fontes" / "Nunito-Bold.ttf"
    )
    # Lê o texto e a fonte de arquivos para os filtros não interpretarem os rótulos.
    (pasta / "fonte.ttf").write_bytes(fonte.read_bytes())
    for capitulo, nomes in enumerate((("bosque", "taquaral"), ("corrego", "gruta"))):
        entradas = []
        filtros = []
        for linha, nome in enumerate(nomes):
            titulo, (x, y, w, h), esquerda, direita = RECORTES[nome]
            for coluna, (raiz, legenda) in enumerate(
                ((referencia, esquerda), (jogo, direita))
            ):
                i = 2 * linha + coluna
                entradas.extend(
                    [
                        "-ss",
                        "0.35",
                        "-t",
                        "7",
                        "-i",
                        str((raiz / nome / "imagem.mp4").resolve()),
                    ]
                )
                (pasta / f"rotulo{i}.txt").write_text(
                    f"{titulo}   ·   {legenda}", encoding="utf-8"
                )
                filtros.append(
                    f"[{i}:v]crop={w}:{h}:{x}:{y},scale=960:540:flags=lanczos,"
                    f"drawtext=fontfile=fonte.ttf:textfile=rotulo{i}.txt:fontsize=23:fontcolor=0xefe8d8:"
                    f"box=1:boxcolor=0x151a20@0.90:boxborderw=9:x=21:y=23[v{i}]"
                )
        filtros.append(
            "[v0][v1][v2][v3]xstack=inputs=4:layout=0_0|960_0|0_540|960_540[v]"
        )
        subprocess.run(
            [
                ffmpeg,
                "-v",
                "error",
                "-y",
                *entradas,
                "-filter_complex",
                ";".join(filtros),
                "-map",
                "[v]",
                "-an",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-preset",
                "veryfast",
                "-crf",
                "16",
                "-threads",
                "3",
                f"grupo{capitulo}.mp4",
            ],
            cwd=pasta,
            check=True,
        )
    (pasta / "lista.txt").write_text("file 'grupo0.mp4'\nfile 'grupo1.mp4'\n")
    subprocess.run(
        [
            ffmpeg,
            "-v",
            "error",
            "-y",
            "-f",
            "concat",
            "-i",
            "lista.txt",
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(destino.resolve()),
        ],
        cwd=pasta,
        check=True,
    )


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument(
        "--jogo", type=Path, required=True, help="Saída de gravar_pinturas --reacoes"
    )
    cli.add_argument("--saida", type=Path, required=True)
    cli.add_argument(
        "--controle", type=Path, help="Reusar uma gravação de controle da mesma revisão"
    )
    args = cli.parse_args()
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="miopia-comparativo-") as tmp:
        pasta = Path(tmp)
        referencia = args.controle or pasta / "controle"
        if args.controle is None:
            controle(referencia)
        comparar(args.jogo, referencia, args.saida, pasta)
