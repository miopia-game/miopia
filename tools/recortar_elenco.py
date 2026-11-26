"""Recorta as três folhas transparentes de inimigos preparadas para Miopia."""
from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageFilter

ELENCO = {
    "patrulha": ("aranha", "morcego", "vespa", "carabideo"),
    "subsolo": ("sombra", "cobra", "caruncho", "cobra-dos-bercos"),
    "guardioes": ("asa-fendida", "tecela", "casco-oco", "coruja"),
}


def figuras(imagem):
    largura, altura = imagem.size
    alpha = imagem.getchannel("A")
    pixels = bytearray(int(x >= 70) for x in alpha.tobytes())
    itens = []
    for i, opaco in enumerate(pixels):
        if not opaco:
            continue
        grupo = [i]
        pixels[i] = 0
        for indice in grupo:
            x, y = indice % largura, indice // largura
            for lado in (indice-1 if x else indice, indice+1 if x<largura-1 else indice,
                         indice-largura if y else indice, indice+largura if y<altura-1 else indice):
                if pixels[lado]:
                    grupo.append(lado)
                    pixels[lado] = 0
        if len(grupo) < 600:
            continue
        xs = [i % largura for i in grupo]
        ys = [i // largura for i in grupo]
        caixa = (max(0,min(xs)-2), max(0,min(ys)-2),
                 min(largura,max(xs)+3), min(altura,max(ys)+3))
        sprite = imagem.crop(caixa)
        marca = Image.new("L",sprite.size)
        mascara = marca.load()
        for x,y in zip(xs,ys):
            mascara[x-caixa[0],y-caixa[1]] = 255
        borda = marca.filter(ImageFilter.MaxFilter(5))
        sprite.putalpha(ImageChops.multiply(alpha.crop(caixa),borda))
        itens.append((sum(xs)/len(xs),sum(ys)/len(ys),sprite))
    return sorted(itens, key=lambda item: item[1])


def recortar(origem, destino):
    destino.mkdir(parents=True, exist_ok=True)
    for folha, nomes in ELENCO.items():
        sprites = figuras(Image.open(origem/f"{folha}.png").convert("RGBA"))
        if len(sprites) != 12:
            raise ValueError(f"{folha}: esperadas 12 figuras, chegaram {len(sprites)}")
        for linha,pose in enumerate(("repouso","preparacao","ataque")):
            ordenadas = sorted(sprites[linha*4:linha*4+4], key=lambda item: item[0])
            for nome,(_,_,sprite) in zip(nomes,ordenadas):
                sprite.save(destino/f"{nome}-{pose}.png",optimize=True)


if __name__ == "__main__":
    recortar(Path(sys.argv[1]),Path(sys.argv[2]))
