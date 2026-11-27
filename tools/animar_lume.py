"""Empacota os desenhos individuais de Lume sem criar poses intermediárias."""
import json
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
FONTES = RAIZ / "docs/arte/fontes/lume/quadros"
DESTINO = RAIZ / "assets/arte/lume"
CELULA = (192, 160)
COLUNAS = 4


def empacotar(pintura, registros):
    """Cada registro identifica uma pintura inteira, sua escala uniforme e sua posição."""
    linhas = (len(registros) + COLUNAS - 1) // COLUNAS
    folha = Image.new("RGBA", (CELULA[0]*COLUNAS, CELULA[1]*linhas))
    for i, registro in enumerate(registros):
        desenho = pintura.crop(registro["recorte"])
        escala = registro["escala"]
        tamanho = tuple(round(v*escala) for v in desenho.size)
        desenho = desenho.resize(tamanho, Image.Resampling.LANCZOS)
        x, y = registro["origem"]
        if x < 0 or y < 0 or x + tamanho[0] > CELULA[0] or y + tamanho[1] > CELULA[1]:
            raise ValueError(f"Desenho {i} excede a célula")
        linha, coluna = divmod(i, COLUNAS)
        folha.paste(desenho, (coluna*CELULA[0]+x, linha*CELULA[1]+y))
    return folha


def preparar():
    registro = json.loads((FONTES / "registro.json").read_text(encoding="utf-8"))
    farois, punhos = {}, {}
    for nome, quadros in registro.items():
        with Image.open(FONTES / f"{nome}.png") as pintura:
            folha = empacotar(pintura.convert("RGBA"), quadros)
        folha.save(DESTINO / f"{nome}.png", optimize=True)
        farois[nome] = [q["luz"] for q in quadros]
        if "punho" in quadros[0]:
            punhos[nome] = [q["punho"] for q in quadros]
    for nome, dados in (("farol", farois), ("juntas", {"punho": punhos})):
        (DESTINO / f"{nome}.json").write_text(json.dumps(dados)+"\n", encoding="utf-8")


if __name__ == "__main__":
    preparar()
