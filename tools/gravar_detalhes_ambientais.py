"""Filma em escala 1:1 quatro recortes do compositor ambiental com a câmera fixa."""

import argparse
import os
from pathlib import Path
import subprocess

import imageio_ffmpeg
import pygame

from src import pygame_hd as hd
from src.ilustracao import RAIZ
from src.paisagem import TONS_PANORAMA, desenhar_panorama

DETALHES = (
    ("Bosque das Samambaias", (700, 352)),
    ("Córrego Fundo", (182, 365)),
    ("Taquaral", (463, 188)),
    ("Gruta da Figueira", (622, 296)),
)


def gravar(saida):
    pygame.font.init()
    fonte = pygame.font.Font(str(RAIZ / "assets" / "fontes" / "Nunito-Bold.ttf"), 24)
    tela = pygame.Surface((1920, 1080))
    alvos = []
    for i, (titulo, centro) in enumerate(DETALHES):
        canto = (960 * (i % 2), 540 * (i // 2))
        alvo = hd.nativa(tela.subsurface((*canto, 960, 540)), (480, 270))
        origem = (240 - centro[0] * 4 / 3, 135 - centro[1] * 4 / 3)
        rotulo = fonte.render(titulo, True, (233, 229, 213))
        alvos.append((alvo, origem, rotulo))
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    saida.parent.mkdir(parents=True, exist_ok=True)
    with subprocess.Popen(
        [
            ffmpeg,
            "-v",
            "error",
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            "1920x1080",
            "-r",
            "60",
            "-i",
            "-",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "15",
            "-threads",
            "3",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(saida),
        ],
        stdin=subprocess.PIPE,
    ) as video:
        for n in range(360):
            for i, (alvo, origem, rotulo) in enumerate(alvos):
                desenhar_panorama(alvo, i, origem, 1.25 + n / 60)
                alvo.pixels.fill(TONS_PANORAMA[1], special_flags=pygame.BLEND_RGB_MULT)
                pygame.draw.rect(
                    alvo.pixels,
                    (19, 24, 29),
                    (20, 18, rotulo.get_width() + 28, 43),
                    border_radius=6,
                )
                alvo.pixels.blit(rotulo, (34, 25))
            video.stdin.write(pygame.image.tobytes(tela, "RGB"))
        video.stdin.close()
        if video.wait():
            raise RuntimeError("Falha na codificação dos detalhes")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--saida", type=Path, required=True)
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    gravar(cli.parse_args().saida)
