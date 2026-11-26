"""Desenhos articulados originais. Gera as quatro folhas RGBA em assets/chefes."""
from math import sin, cos, tau
from pathlib import Path

from PIL import Image, ImageDraw

TAMANHO = (188, 152)
ESCALA = 3
TINTA = "#101922"
SOMBRA = "#1d2b32"
PELE = "#34494e"
VEIO = "#76928c"
OSSO = "#bcba9f"
OURO = "#efbc76"
FERRUGEM = "#ba7055"


class Gravura:
    def __init__(self):
        self.im = Image.new("RGBA", tuple(n * ESCALA for n in TAMANHO))
        self.draw = ImageDraw.Draw(self.im)

    @staticmethod
    def ponto(xy):
        return (round((TAMANHO[0] / 2 + xy[0]) * ESCALA),
                round((TAMANHO[1] / 2 + xy[1]) * ESCALA))

    def poli(self, tom, *vertices, borda=None):
        pontos = [self.ponto(v) for v in vertices]
        self.draw.polygon(pontos, fill=tom)
        if borda:
            self.draw.line(pontos + pontos[:1], width=ESCALA, fill=borda)

    def linha(self, tom, largura, *vertices):
        self.draw.line([self.ponto(v) for v in vertices],
                       width=max(1, round(largura * ESCALA)), fill=tom, joint="curve")

    def oval(self, tom, x, y, rx, ry, borda=None):
        self.draw.ellipse([self.ponto((x-rx, y-ry)), self.ponto((x+rx, y+ry))],
                          fill=tom, outline=borda, width=ESCALA)

    def pronta(self):
        return self.im.resize(TAMANHO, Image.Resampling.LANCZOS)


def morcego(g, pose, t):
    batida = sin(t) * (8 if pose == 0 else 3)
    alto = {0:-35, 1:-46, 2:4, 3:16}[pose] + batida
    # A membrana é rasgada em uma asa. As hastes nunca formam uma máscara.
    for dx, dy, tom in [(-14, -5, SOMBRA), (1, 0, PELE)]:
        punho = (-17+dx, alto+dy)
        pontas = [(-75+dx, alto+5+dy), (-64+dx, 2+dy), (-48+dx, 18+dy),
                  (-37+dx, 9+dy), (-15+dx, 18+dy), (6+dx, 10+dy)]
        g.poli(tom, (14, 2), punho, *pontas, (5, 4), borda=VEIO)
        for j, ponta in enumerate(pontas[1::2]):
            g.linha(VEIO, 1, punho, ((punho[0] + ponta[0]) / 2, (alto + ponta[1]) / 2 - 3), ponta)
        g.linha(OSSO, 1.3, (12, 1), punho, pontas[0])
    g.poli(TINTA, (-32, 17), (-12, -3), (17,-7), (32,2), (20,17), (1,22),(-9,29), borda=VEIO)
    for i in range(6):
        x=-15+i*5
        g.linha(PELE, 2, (x,-1), (x-6,12), (x-10,17))
    g.poli(PELE, (10,-7), (12,-24),(22,-16),(30,-22),(30,-8),(42,-2),(34,8),(21,12),(14,7), borda=VEIO)
    g.poli(FERRUGEM,(14,-21),(20,-16),(15,-11))
    g.oval(OURO,29,-4,2.6,1.7)
    for x in (-6,7):
        g.linha(OSSO,1.5,(x,17),(x-4,27),(x-9,29))
    g.linha(OURO,1.6,(-18,1),(-13,-3),(-8,0),(-6,-3))


def aranha(g, pose, t):
    base = {0:0, 1:-7, 2:0, 3:8}[pose]
    for lado in [-1,1]:
        for i in range(4):
            inicio=(4-i*3,base+4)
            joelho=(lado*(27+i*9), base-16-i*3+sin(t+i)*3)
            pe=(lado*(32+i*12), base+28-i*3+cos(t+i)*4)
            g.linha(TINTA,5.5,inicio,joelho,pe,(pe[0]+lado*4,pe[1]+2))
            g.linha(VEIO,2,inicio,joelho,pe)
            g.oval(OSSO,*joelho,2,2)
    g.poli(PELE,(-37,base+1),(-29,base-21),(-14,base-30),(1,base-22),(8,base-5),(0,base+11),(-21,base+17),(-33,base+8), borda=VEIO)
    for i in range(4):
        g.linha(OSSO,1,(-32+i*4,base-2-i*5),(-19+i*2,base+1-i*3),(-5,base-7-i*3))
    g.linha(OURO,2,(-27,base-17),(-20,base-11),(-24,base-6),(-16,base+2))
    g.oval(SOMBRA,8,base+3,13,10,VEIO)
    g.oval(TINTA,20,base+7,9,7,VEIO)
    for i in range(3):
        g.oval(OURO,18+i*3,base+4-i%2,1.1,1.8)
    for x in (22,26):
        g.linha(OSSO,2.3,(x,base+10),(x+4,base+17),(x+1,base+22))


def besouro(g, pose, t):
    abrir = 1 if pose==3 else 0
    for i in range(3):
        x=-25+i*21
        g.linha(TINTA,6,(x,12),(x+9,23),(x-2+sin(t+i)*4,33),(x-10,34))
        g.linha(VEIO,1.6,(x+1,12),(x+10,22),(x-1+sin(t+i)*4,32))
    g.poli(SOMBRA,(-50,8),(-47,-11),(-25,-24),(7,-23),(32,-10),(40,7),(27,18),(-16,23),(-42,16), borda=VEIO)
    # Placas entalhadas e encaixadas. A última levanta com o calor da seiva.
    for i in range(4):
        x=-52+i*17
        a=[-3,-13,-17,-12][i] - abrir*(9 if i in (1,2) else 1)
        g.poli(["#3b4843","#4b5750","#535d52","#454f49"][i],(x,9),(x+4,a),(x+18,a-9),(x+26,a-5),(x+19,10),(x+4,15),borda=OSSO)
        for k in range(3):
            g.linha(SOMBRA,1.3,(x+8+k*4,a+2),(x+4+k*4,7))
    g.poli(TINTA,(17,-7),(34,-12),(43,-6),(48,-10),(46,-22),(54,-13),(56,-2),(48,4),(41,12),(27,13),borda=VEIO)
    g.oval(OURO,37,-4,2.3,1.5)
    g.linha(OURO if abrir else FERRUGEM,2.2,(-14,-7),(-18,0),(-13,4),(-17,10))


def coruja(g, pose, t):
    asa = {0:-22,1:-38,2:0,3:9}[pose] + 5*sin(t)
    # Asa posterior, cauda comprida, tufos de ouvido e máscara facial em perfil.
    g.poli(SOMBRA,(5,1),(-20,asa-7),(-72,asa+3),(-48,asa+8),(-65,asa+14),
           (-40,asa+14),(-46,asa+25),(-22,asa+20),(-15,22),borda=VEIO)
    g.poli(PELE,(10,-19),(26,-12),(30,3),(21,26),(9,32),(-30,38),(-55,50),
           (-43,34),(-72,40),(-36,17),(-23,0),borda=VEIO)
    for i in range(4):
        x=-9+i*6
        g.poli(["#5a6a64","#4b5e5b","#6f7970","#4b5e5b"][i],(x,-1),(x+6,6),(x,24),(x-7,30),(x-3,18))
    for x in (-5,9):
        g.linha(PELE,4,(x,24),(x-1,34),(x+6,35))
        g.linha(OSSO,1.4,(x+2,33),(x+9,35),(x+8,39))
    for i in range(7):
        sx=-5+i*2
        tx=-81+i*8
        ty=asa+6+i*3
        g.poli(["#465854","#324648","#55675e"][i%3],(sx+5,-2+i),
               (sx-18,asa-2+i),(tx,ty),(tx+12,ty+2),(sx-10,12+i),borda=VEIO)
        g.linha(SOMBRA,1,(tx+6,ty),(sx-14,asa+3+i),(sx,5+i))
    g.poli(SOMBRA,(6,-7),(6,-28),(9,-41),(17,-31),(31,-31),(40,-34),(42,-22),
           (40,-9),(50,-3),(38,1),(28,8),(16,10),borda=VEIO)
    g.poli("#9b9e8b",(18,-22),(29,-28),(39,-24),(38,-17),(31,-12),(27,0),(16,-5),(12,-12),borda=OSSO)
    g.poli("#4d5a54",(18,-19),(31,-22),(37,-20),(32,-16),(24,-13))
    g.linha(OSSO,2.5,(22,-18),(29,-16),(35,-19))
    g.poli(OSSO,(35,-13),(46,-10),(39,-6),(37,-2))
    g.linha(FERRUGEM if pose!=3 else OURO,1.7,(10,-35),(18,-27),(15,-22),(25,-15),(22,-9))
    for i in range(4):
        g.linha(OSSO,1,(8+i*2,-25),(4+i*2,-14),(7+i*2,-8))


GUARDIOES = [("asa-fendida",morcego),("tecela",aranha),("casco-oco",besouro),("coruja",coruja)]


def gerar():
    pasta = Path(__file__).resolve().parents[1] / "assets" / "chefes"
    pasta.mkdir(exist_ok=True, parents=True)
    for nome, desenhar in GUARDIOES:
        folha = Image.new("RGBA", (4*TAMANHO[0],4*TAMANHO[1]))
        for pose in range(4):
            for quadro in range(4):
                g = Gravura()
                desenhar(g,pose,quadro*tau/4)
                folha.paste(g.pronta(),(quadro*TAMANHO[0],pose*TAMANHO[1]))
        folha.save(pasta / (nome + ".png"), optimize=True)


if __name__ == "__main__":
    gerar()
