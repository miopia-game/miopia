"""Empacota os desenhos inteiros da fauna no formato lido pelo jogo."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
FONTES = RAIZ / "docs/arte/fontes/fauna-quadros"
DESTINO = RAIZ / "assets/arte/movimento-v2"


def empacotar(nome, folha, destino):
    largura, altura, margem = folha["medida"]
    escala = folha["escala"]
    tela = (largura + 2*margem, altura + 2*margem)
    if len(folha["quadros"]) != 16:
        raise ValueError(f"{nome} precisa de 16 desenhos")

    with Image.open(FONTES / f"{nome}.png") as pintura, ZipFile(destino, "w") as pacote:
        for indice, (x0, y0, x1, y1, x, y) in enumerate(folha["quadros"]):
            recorte = pintura.crop((x0, y0, x1, y1)).convert("RGBA")
            tamanho = tuple(round(v*escala) for v in recorte.size)
            if min(x, y) < 0 or x+tamanho[0] > tela[0] or y+tamanho[1] > tela[1]:
                raise ValueError(f"{nome}/{indice} fora da célula")
            cel = Image.new("RGBA", tela)
            cel.paste(recorte.resize(tamanho, Image.Resampling.LANCZOS), (x, y))
            # A data fixa mantém os pacotes reproduzíveis.
            entrada = ZipInfo(f"{indice:02}.rgba")
            pacote.writestr(entrada, cel.tobytes(), compress_type=ZIP_DEFLATED, compresslevel=3)


def preparar():
    registros = json.loads((FONTES / "registro.json").read_text(encoding="utf-8"))
    with TemporaryDirectory(dir=DESTINO) as pasta:
        temp = Path(pasta)
        for nome, folha in registros.items():
            empacotar(nome, folha, temp / f"{nome}.zip")
        medidas = {nome: folha["medida"] for nome, folha in registros.items()}
        manifesto = temp / "folhas.json"
        manifesto.write_text(json.dumps(medidas, indent=2) + "\n", encoding="utf-8")
        for pacote in temp.glob("*.zip"):
            pacote.replace(DESTINO / pacote.name)
        manifesto.replace(DESTINO / manifesto.name)


if __name__ == "__main__":
    preparar()
