"""Gera as poses nativas por deformação localizada do panorama desenhado."""

from pathlib import Path
from struct import pack
from tempfile import TemporaryDirectory
from math import cos, pi
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image, ImageChops

from src.vento_pintado import ESCALA, PASSOS, PASTA, PLANTAS

# Centro, raios e excursão de cada zona flexível, em coordenadas de composição.
# As bases dos caules ficam fora dos picos de influência. Nas pontas o peso é maior.
FLEXAO = {
    "fronde_central": (
        (474, 307, 92, 55, 3.1, 8.0),
        (514, 346, 38, 42, 2.3, 6.8),
        (465, 450, 79, 48, -2.4, 5.4),
        (349, 373, 40, 58, 1.8, 3.6),
    ),
    "fronde_alta": (
        (671, 168, 78, 69, -2.1, 10.5),
        (733, 102, 88, 65, -2.4, 8.1),
        (808, 52, 65, 52, -1.4, 4.8),
        (864, 171, 45, 64, 1.2, 3.9),
    ),
    "fronde_baixa": (
        (625, 381, 73, 63, -3.5, 11.8),
        (704, 311, 83, 48, -2.8, 7.8),
        (743, 272, 63, 42, -1.6, 5.7),
        (726, 430, 70, 36, -1.9, 5.1),
    ),
    "colmos": (
        (124, 75, 222, 290, 11.8, -2.3),
        (169, 209, 140, 188, 4.2, -1.4),
        (225, 79, 83, 106, 3.1, 2.7),
    ),
    "ramagem": (
        (479, 169, 162, 133, 6.9, 5.8),
        (619, 126, 111, 114, 10.0, 7.5),
        (502, 237, 67, 58, 5.8, 4.1),
        (691, 52, 77, 73, 5.1, 6.2),
    ),
    "touceira": ((866, 152, 122, 139, 7.5, 4.6), (810, 230, 65, 77, 6.0, 5.5)),
}


def rampa(distancia):
    return (1 - cos(pi * max(0.0, min(1.0, distancia / 18)))) / 2


def deslocamento(x, y, nome, caixa):
    x0, y0, x1, y1 = caixa
    bordas = [rampa(x - x0), rampa(x1 - x), rampa(y1 - y)]
    if y0:  # Os colmos ultrapassam o alto do próprio quadro.
        bordas.append(rampa(y - y0))
    margem = min(bordas)
    dx = dy = 0.0
    for cx, cy, rx, ry, vx, vy in FLEXAO[nome]:
        r = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        peso = max(0.0, 1 - r) ** 2
        dx += vx * peso
        dy += vy * peso
    return dx * margem, dy * margem


def malha(nome, caixa, largura, altura):
    xs = list(range(0, largura, 24)) + [largura]
    ys = list(range(0, altura, 24)) + [altura]
    campos = {
        (x, y): deslocamento(caixa[0] + x / ESCALA, caixa[1] + y / ESCALA, nome, caixa)
        for x in xs
        for y in ys
    }
    for xa, xb in zip(xs, xs[1:]):
        for ya, yb in zip(ys, ys[1:]):
            cantos = [(xa, ya), (xa, yb), (xb, yb), (xb, ya)]
            yield (xa, ya, xb, yb), [(x, y, *campos[x, y]) for x, y in cantos]


def gravar(pacote, nome, dados):
    entrada = ZipInfo(nome)
    entrada.compress_type = ZIP_DEFLATED
    pacote.writestr(entrada, dados, compresslevel=5)


def gravar_poses(bioma, destino):
    with (
        Image.open(PASTA / f"{bioma}.jpg") as fonte,
        ZipFile(destino, "w") as pacote,
    ):
        for nome, caixa, _, _ in PLANTAS[bioma]:
            recorte = fonte.crop(tuple(round(v * ESCALA) for v in caixa))
            paleta = recorte.quantize(colors=255, dither=Image.Dither.NONE)
            cores = bytes(paleta.getpalette()[: 255 * 3])
            # O índice zero deixa a pintura original aparecer entre as folhas.
            cores_luz = bytes(
                (v * (191, 202, 211)[i % 3] + 255) // 256 for i, v in enumerate(cores)
            )
            gravar(pacote, f"{nome}/cores", bytes(3) + cores_luz)
            base = list(malha(nome, caixa, *recorte.size))
            for passo in range(-PASSOS, PASSOS + 1):
                if not passo:
                    continue
                escala = ESCALA * passo / PASSOS
                grade = [
                    (
                        area,
                        tuple(
                            v
                            for x, y, dx, dy in pontos
                            for v in (x - dx * escala, y - dy * escala)
                        ),
                    )
                    for area, pontos in base
                ]
                pose = recorte.transform(
                    recorte.size, Image.Transform.MESH, grade, Image.Resampling.BICUBIC
                )
                r, g, b = ImageChops.difference(pose, recorte).split()
                mascara = ImageChops.lighter(ImageChops.lighter(r, g), b).point(
                    lambda v: 255 if v > 2 else 0
                )
                caixa_ativa = mascara.getbbox()
                imagem = pose.crop(caixa_ativa).quantize(
                    palette=paleta, dither=Image.Dither.NONE
                )
                indices = Image.frombytes("L", imagem.size, imagem.tobytes())
                indices = indices.point(lambda v: min(255, v + 1))
                indices.paste(0, mask=ImageChops.invert(mascara.crop(caixa_ativa)))
                dados = pack("<4H", *caixa_ativa[:2], *indices.size) + indices.tobytes()
                gravar(pacote, f"{nome}/{passo:+d}", dados)


def exportar(bioma):
    destino = PASTA / f"vento_{bioma}.atlas"
    with TemporaryDirectory(dir=PASTA) as pasta:
        temporario = Path(pasta) / destino.name
        gravar_poses(bioma, temporario)
        temporario.replace(destino)


if __name__ == "__main__":
    for bioma in PLANTAS:
        exportar(bioma)
