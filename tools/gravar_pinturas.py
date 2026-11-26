"""Reproduz quatro caminhadas de avaliação das pinturas pelo fluxo normal de entrada."""

import argparse
from array import array
from bisect import bisect_right
from collections import defaultdict
import ctypes
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import wave

FPS = 60
QUADROS = 480
TRECHOS = (("bosque", 2944), ("corrego", 262), ("taquaral", 65), ("gruta", 260))


PARTIDA_REACOES = (2932, 184, 65, 202)


def controles_reacao(indice, quadro):
    import pygame

    teclas = set()
    if indice in (0, 2):
        if 63 <= quadro < 135 or 316 <= quadro < 415:
            teclas.add(pygame.K_d)
        elif 168 <= quadro < 251:
            teclas.add(pygame.K_a)
        if quadro == 332:
            teclas.add(pygame.K_SPACE)
    else:
        if 40 <= quadro < 69 or 250 <= quadro < 350:
            teclas.add(pygame.K_d)
        elif 350 <= quadro < 393:
            teclas.add(pygame.K_a)
        if quadro == 97:
            teclas.add(pygame.K_g)
        if quadro == 282:
            teclas.add(pygame.K_SPACE)
    return teclas


def gravar(indice, pasta, modo, *, reacoes=False):
    import imageio_ffmpeg
    import pygame
    from pygame._sdl2.mixer import set_post_mix
    from src.fases import CHAO
    from src.main import App

    nome, partida = TRECHOS[indice]
    pasta.mkdir(parents=True, exist_ok=True)
    app = App(temporaria=True)
    app.iniciar("historia")
    app.jogar()
    j = app.jogo
    j.entrar(indice)
    if reacoes:
        partida = PARTIDA_REACOES[indice]
    j.recolocar((partida, CHAO))
    for _ in range(75):
        app.atualizar(1 / FPS, presso=defaultdict(bool))
    # O ensaio começa com a câmera estabilizada. A partir daqui só o teclado move Lume.
    instante_inicial = j.tempo
    rota = []
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    filmar = modo == "filme"
    mix, fronteiras = [], []
    video = None
    try:
        if filmar:
            video = subprocess.Popen(
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
                    str(FPS),
                    "-i",
                    "-",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-threads",
                    "3",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "16",
                    "-pix_fmt",
                    "yuv420p",
                    str(pasta / "imagem.mp4"),
                ],
                stdin=subprocess.PIPE,
            )
            set_post_mix(
                lambda _, dados: mix.append((time.perf_counter(), bytes(dados)))
            )
            time.sleep(0.12)
        proximo = time.perf_counter()
        anteriores = set()
        for n in range(QUADROS):
            if filmar:
                time.sleep(max(0, proximo - time.perf_counter()))
                fronteiras.append(time.perf_counter())
                proximo = max(proximo, fronteiras[-1] - 0.001) + 1 / FPS
            if reacoes:
                pressionadas = controles_reacao(indice, n)
            else:
                pressionadas = set()
                if 18 <= n < 258 or 382 <= n < 465:
                    pressionadas.add(pygame.K_d)
                elif 275 <= n < 369:
                    pressionadas.add(pygame.K_a)
                if n in (60, 153, 268, 328, 401):
                    pressionadas.add(pygame.K_SPACE)
                if n == 100:
                    pressionadas.add(pygame.K_g)
                if n == 220:
                    pressionadas.add(pygame.K_k)
                if n in (195, 312):
                    pressionadas.add(pygame.K_j)
            for tecla in anteriores - pressionadas:
                app.evento(pygame.event.Event(pygame.KEYUP, key=tecla))
            for tecla in sorted(pressionadas - anteriores):
                app.evento(pygame.event.Event(pygame.KEYDOWN, key=tecla))
            app.atualizar(
                1 / FPS, presso=defaultdict(bool, {k: True for k in pressionadas})
            )
            anteriores = pressionadas
            rota.append(
                (
                    round(j.lume.rect.centerx, 2),
                    round(j.lume.rect.bottom, 2),
                    round(j.camera, 2),
                    round(j.camera_y, 2),
                    j.lume.vida,
                    app.estado,
                )
            )
            if filmar or (modo == "amostras" and n in (35, 165, 235, 335)):
                app.desenhar()
                tela = app.quadro_renderizado
                assert tela.get_size() == (1920, 1080)
                if n in (35, 165, 235, 335):
                    pygame.image.save(tela, str(pasta / f"quadro-{n}.png"))
                if filmar:
                    video.stdin.write(pygame.image.tobytes(tela, "RGB"))
        if filmar:
            fronteiras.append(max(time.perf_counter(), proximo))
            time.sleep(0.08)
    finally:
        if filmar:
            # O mixer chama Python em outra thread. Soltar o GIL ao desregistrar evita um impasse.
            encerrar_mix()
        if video:
            video.stdin.close()
            if video.wait():
                raise RuntimeError("Falha ao gravar os quadros")
        app.mem.db.close()
        app.janela.fechar()
        pygame.quit()
    desloc = round(max(l[2] for l in rota) - min(l[2] for l in rota), 2)
    assert desloc > (55 if reacoes else 220) and all(
        l[-1] == "jogo" and l[-2] > 0 for l in rota
    ), (
        nome,
        desloc,
        rota[-1],
    )
    medidas = dict(
        fase=j.fase.name,
        quadros=len(rota),
        fps=FPS,
        deslocamento_camera=desloc,
        tempo_inicial=instante_inicial,
        rota=rota,
    )
    (pasta / "trajeto.json").write_text(json.dumps(medidas, ensure_ascii=False))
    if filmar:
        sincronizar_audio(mix, fronteiras, pasta / "mixer.wav")
        subprocess.run(
            [
                ffmpeg,
                "-v",
                "error",
                "-y",
                "-i",
                str(pasta / "imagem.mp4"),
                "-i",
                str(pasta / "mixer.wav"),
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                str(pasta / f"{nome}.mp4"),
            ],
            check=True,
        )
    print(nome, desloc, "unidades de câmera", flush=True)


def encerrar_mix():
    from pygame._sdl2.mixer import set_post_mix
    import pygame

    biblioteca = "SDL2_mixer.dll" if os.name == "nt" else pygame.mixer.__file__
    retirar = ctypes.CDLL(biblioteca).Mix_SetPostMix
    retirar.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    retirar.restype = None
    retirar(None, None)
    set_post_mix(None)


def sincronizar_audio(buffers, fronteiras, caminho):
    # Relaciona o som produzido pelo SDL ao instante de cada quadro da simulação.
    tempos = [t for t, _ in buffers]
    pcm = array("h")
    offsets = []
    for _, dados in buffers:
        offsets.append(len(pcm) // 2)
        pcm.frombytes(dados)

    def indice(t):
        k = max(0, min(len(tempos) - 2, bisect_right(tempos, t) - 1))
        p = max(0.0, min(1.0, (t - tempos[k]) / (tempos[k + 1] - tempos[k])))
        return round(offsets[k] + p * (offsets[k + 1] - offsets[k]))

    amostras = array("h")
    indices = list(map(indice, fronteiras))
    por_quadro = 44100 // FPS
    for a, b in zip(indices, indices[1:]):
        for n in range(por_quadro):
            pos = a + (b - a) * n / por_quadro
            k = int(pos) * 2
            f = pos - int(pos)
            for canal in (0, 1):
                amostras.append(
                    round((1 - f) * pcm[k + canal] + f * pcm[k + 2 + canal])
                )
    with wave.open(str(caminho), "wb") as arquivo:
        arquivo.setparams((2, 2, 44100, 0, "NONE", "not compressed"))
        arquivo.writeframes(amostras.tobytes())


def montar_filme(saida):
    """Reúne os quatro trechos sem recomprimir a imagem e codifica o som uma só vez."""
    import imageio_ffmpeg

    nomes = ("Bosque das Samambaias", "Córrego Fundo", "Taquaral", "Gruta da Figueira")
    with tempfile.TemporaryDirectory(dir=saida) as temporaria:
        pasta = Path(temporaria)
        lista = pasta / "videos.ffconcat"
        # O diretório temporário é filho da saída. Os nomes abaixo são fixos.
        lista.write_text(
            "ffconcat version 1.0\n"
            + "".join(f"file '../{nome}/imagem.mp4'\n" for nome, _ in TRECHOS),
            encoding="utf-8",
        )
        meta = pasta / "capitulos.txt"
        meta.write_text(
            ";FFMETADATA1\n"
            + "".join(
                f"[CHAPTER]\nTIMEBASE=1/{FPS}\nSTART={i * QUADROS}\nEND={(i + 1) * QUADROS}\ntitle={titulo}\n"
                for i, titulo in enumerate(nomes)
            ),
            encoding="utf-8",
        )
        with wave.open(str(pasta / "som.wav"), "wb") as destino:
            destino.setparams((2, 2, 44100, 0, "NONE", "not compressed"))
            for nome, _ in TRECHOS:
                with wave.open(str(saida / nome / "mixer.wav"), "rb") as origem:
                    if origem.getparams()[:4] != (2, 2, 44100, QUADROS * 44100 // FPS):
                        raise ValueError(f"Som incompatível no trecho {nome}")
                    destino.writeframes(origem.readframes(origem.getnframes()))
        subprocess.run(
            [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-v",
                "error",
                "-y",
                "-safe",
                "0",
                "-i",
                str(lista),
                "-i",
                str(pasta / "som.wav"),
                "-f",
                "ffmetadata",
                "-i",
                str(meta),
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-map_chapters",
                "2",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                str(saida / "quatro-pinturas-em-jogo.mp4"),
            ],
            check=True,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, required=True)
    parser.add_argument(
        "--modo", choices=("filme", "amostras", "rota"), default="filme"
    )
    parser.add_argument(
        "--reacoes",
        action="store_true",
        help="Cruzar a folhagem nos dois sentidos e lançar perto da água.",
    )
    parser.add_argument("--fase", choices=[n for n, _ in TRECHOS])
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="miopia-pinturas-") as perfil:
        os.environ.update(
            MIOPIA_DADOS=perfil, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy"
        )
        for i, (nome, _) in enumerate(TRECHOS):
            if args.fase in (None, nome):
                gravar(i, args.saida / nome, args.modo, reacoes=args.reacoes)
        if args.modo == "filme" and args.fase is None:
            montar_filme(args.saida)
