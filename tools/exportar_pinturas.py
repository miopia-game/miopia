"""Exporta as pinturas de tela e as versões com margem de câmera dos quatro mestres."""

from io import BytesIO
from pathlib import Path

from PIL import Image
import resvg_py

RAIZ = Path(__file__).resolve().parents[1]
NOMES = ("bosque", "corrego", "taquaral", "gruta")


def exportar(mestre, tamanho, destino):
    png = resvg_py.svg_to_bytes(
        svg_path=str(mestre),
        width=tamanho[0],
        height=tamanho[1],
        skip_system_fonts=True,
    )
    with Image.open(BytesIO(png)) as im:
        if im.size != tamanho:
            raise ValueError(f"{mestre.name} gerou {im.size}, esperado {tamanho}")
        im.convert("RGB").save(destino, quality=96, subsampling=0, optimize=True)


if __name__ == "__main__":
    arte = RAIZ / "assets" / "arte"
    for i, nome in enumerate(NOMES):
        mestre = RAIZ / "docs" / "arte" / "fontes" / "panoramas" / f"{nome}.svgz"
        exportar(mestre, (1920, 1080), arte / f"fundo_{i}.jpg")
        exportar(mestre, (2560, 1440), arte / "panoramas" / f"{nome}.jpg")
