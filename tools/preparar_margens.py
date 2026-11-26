"""Prepara as quatro margens laterais a partir da pintura em faixas."""
from pathlib import Path
from statistics import median

from PIL import Image, ImageChops, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
CORES = ((32, 30, 39), (30, 38, 45), (48, 37, 36), (39, 29, 44))
# Limites verticais e janela de detalhe de cada pintura (coordenadas do mestre).
CORTES = ((0, 200, 275), (203, 372, 175), (377, 550, 340), (552, 724, 215))


def preparar():
    folha = Image.open(RAIZ / "docs/arte/fontes/panoramas/margens.png").convert("RGBA")
    pasta = RAIZ / "assets/arte/margens"
    for i, (y0, y1, inicio) in enumerate(CORTES):
        faixa = folha.crop((0, y0, folha.width, y1))
        alfa = faixa.getchannel("A").point(lambda a: 0 if a < 28 else min(255, round(a * 255/252)))
        faixa.putalpha(alfa)
        faixa = faixa.crop(alfa.getbbox())
        recorte = faixa.crop((inicio, 0, inicio + 850, faixa.height))
        # Guarda a borda real do pouso e deixa raízes e lascas acima dela.
        alpha = recorte.getchannel("A")
        perfil = [alpha.crop((x, 0, x+1, alpha.height)).getbbox()[1] for x in range(0, alpha.width, 6)]
        topo = round(median(perfil))
        # Usa a extensão da gravura. A borda final se funde ao início antes do corte
        # do ladrilho, sem duplicar pedras simetricamente em cada emenda.
        terra = faixa.crop((80, 0, faixa.width-80, faixa.height))
        alfa_terra = terra.getchannel("A")
        solo = Image.new("RGB", (terra.width, 150), CORES[i])
        for x in range(terra.width):
            coluna = terra.crop((x, 0, x+1, terra.height))
            borda = alfa_terra.crop((x, 0, x+1, terra.height)).point(lambda a: 255 if a>=160 else 0).getbbox()
            inicio_coluna = max(topo-3, borda[1] if borda else topo)
            solo.paste(coluna, (x, -inicio_coluna), coluna)
        mix = Image.new("L", solo.size)
        pincel = ImageDraw.Draw(mix)
        for y in range(solo.height):
            pincel.line((0, y, solo.width, y), fill=round(255 * max(0, (y-65)/84)**1.3))
        solo = Image.composite(Image.new("RGB", solo.size, CORES[i]), solo, mix)
        margem = 110
        for x in range(margem):
            a = solo.crop((solo.width-margem+x, 0, solo.width-margem+x+1, solo.height))
            b = solo.crop((x, 0, x+1, solo.height))
            solo.paste(Image.blend(a,b,x/(margem-1)),(solo.width-margem+x,0))
        solo.crop((margem,0,solo.width,solo.height)).save(pasta / f"solo-{i}.png", optimize=True)

        # Mantém as pontas quebradas da ilustração na escala dos patamares curtos.
        miolo = recorte.crop((0, 0, 590, recorte.height))
        patamar = Image.new("RGBA", (750, 180))
        dy = 22 - topo
        patamar.alpha_composite(miolo, (80, dy))
        for x, pos in ((0, 0), (faixa.width - 100, 650)):
            ponta = faixa.crop((x, 0, x + 100, faixa.height))
            mascara = Image.new("L", ponta.size, 255)
            d = ImageDraw.Draw(mascara)
            for k in range(20):
                col = 99-k if pos == 0 else k
                d.line((col, 0, col, ponta.height), fill=round(255*k/19))
            ponta.putalpha(ImageChops.multiply(ponta.getchannel("A"), mascara))
            patamar.alpha_composite(ponta, (pos, dy))
        patamar.save(pasta / f"patamar-{i}.png", optimize=True)


if __name__ == "__main__":
    preparar()
