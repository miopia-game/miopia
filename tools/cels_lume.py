"""Prepara os desenhos e os intervalos de Lume na densidade da tela Full HD."""
from dataclasses import dataclass
from functools import lru_cache
from math import cos, pi
from pathlib import Path

from PIL import Image

FONTES = Path(__file__).resolve().parents[1] / "docs/arte/fontes/lume/movimento"
CELULA = (192,160)
BASE = 132
AMOSTRAS = 60
# Coordenadas das luvas que conduzem o gesto, na quadrícula de 200 unidades da folha.
PUNHOS = {
    "caminhada": ((151,106),(143,115),(131,123),(139,102),(147,105),(146,113),(132,124),(140,108)),
    "corrida": ((162,117),(151,124),(155,95),(167,93),(163,119),(152,122),(158,98),(165,97)),
    "espinho": ((149,83),(149,69),(142,38),(148,76),(161,89),(160,137),(139,141),(150,83)),
    "fagulha": ((63,132),(111,119),(126,110),(161,95),(162,86),(150,101),(141,108),(108,123)),
    "aereo": ((78,61),(136,102),(140,151),(136,180),(146,163),(152,116),(158,83),(157,50)),
    "impulsos": ((155,116),(164,102),(157,98),(91,118),(145,178),(153,136),(164,146),(157,180)),
}
# Frente e trás são acompanhadas também na passagem em que uma bota oculta a outra.
BOTAS = {
    "caminhada": ((65,179,142,176),(72,168,117,181),(93,182,99,161),(60,178,135,164),
                  (68,171,140,177),(76,167,117,182),(88,181,103,162),(56,178,137,168)),
    "corrida": ((44,154,151,182),(53,148,119,181),(68,173,131,151),(42,151,175,138),
                (43,159,156,181),(57,157,119,181),(66,177,124,145),(44,151,176,147)),
}
# Cada série indexa as pinturas na ordem da sua ação, incluindo a volta à guarda.
SERIES = {
    "passo": ("caminhada",range(8)), "corrida": ("corrida",range(8)),
    "golpe": ("espinho",range(8)), "subida": ("aereo",(4,4,5,6,7,7,6,5,4)),
    "mergulho": ("aereo",(0,0,1,2,3,3,2,1)),
    "lancar": ("fagulha",range(8)), "clarao": ("fagulha",(1,3,4,5,6,7)),
    "voo": ("impulsos",(0,1,2)), "queda": ("impulsos",(2,1,0)),
    "planeio": ("impulsos",(2,3)), "deslizar": ("impulsos",(4,5,6,6,7,4)),
}
CICLOS = {"passo","corrida"}


@dataclass
class Cel:
    imagem: Image.Image
    pontos: tuple


@lru_cache
def folha(nome):
    im = Image.open(FONTES / (nome+".png")).convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda a: 0 if a<28 else min(255,round(a*255/252))))
    return im.resize((800,400),Image.Resampling.LANCZOS)


def ouro(im, perto, raio):
    """Localiza pigmento do farol, inclusive quando a palma cobre parte do abdômen."""
    x,y = perto
    cx,cy = round(x),round(y)
    pontos = []
    for j in range(max(0,cy-raio),min(im.height,cy+raio+1)):
        for i in range(max(0,cx-raio),min(im.width,cx+raio+1)):
            r,g,b,a = im.getpixel((i,j))
            if r>209 and g>132 and b<135 and a>180:
                pontos.append((i,j))
    return min(pontos,key=lambda p:(x-p[0])**2+(y-p[1])**2)


@lru_cache
def chave(nome, i):
    linha,col = divmod(i,4)
    separacao = 231 if nome == "impulsos" else 199
    y0,y1 = (0,separacao) if linha == 0 else (separacao,400)
    im = Image.new("RGBA",(200,231))
    im.paste(folha(nome).crop((col*200,y0,col*200+200,y1)),(0,y0-linha*200))
    # Centro da máscara, implante do lenço e ponto luminoso são referências de registro.
    caixa = im.getchannel("A").point(lambda a:255 if a>=100 else 0).getbbox()
    x0,y0,x1,y1 = caixa
    w,h = x1-x0,y1-y0
    olho = ouro(im,(x0+.76*w,y0+.30*h),round(.25*h))
    farol = ouro(im,(x0+.23*w,y0+.73*h),round(.31*h))
    luva = PUNHOS[nome][i]
    ombro = ((olho[0]+farol[0])*.5,olho[1]+(farol[1]-olho[1])*.30)
    botas = BOTAS[nome][i] if nome in BOTAS else (x0+.25*w,y1-5,x0+.76*w,y1-6)
    escala = .565
    # Saúde da silhueta: a escala é compartilhada entre cels. O apoio só corrige a translação.
    eixo = (olho[0]*.63+farol[0]*.37)
    base = y1
    if nome in ("aereo","impulsos") and i < 4:
        base += 5
    dx,dy = round(96-eixo*escala),round(BASE-base*escala)
    out = Image.new("RGBA",CELULA)
    out.paste(im.resize((round(im.width*escala),round(im.height*escala)),Image.Resampling.LANCZOS),(dx,dy))
    marcos=(farol,luva,ombro,olho,(botas[0],botas[1]),(botas[2],botas[3]),
            (x0+.12*w,y0+.50*h),(x0+.24*w,y0+.08*h))
    return Cel(out,tuple((dx+x*escala,dy+y*escala) for x,y in marcos))


def intervalo(a,b,t):
    """Leva juntas correspondentes à mesma posição conservando a tinta de um único cel."""
    pos = tuple((x+(xx-x)*t,y+(yy-y)*t) for (x,y),(xx,yy) in zip(a.pontos,b.pontos))
    fonte = a if t < .5 else b
    if t<.001 or t>.999 or a is b:
        return fonte.imagem,pos
    deltas = tuple((fx-x,fy-y,x,y) for (fx,fy),(x,y) in zip(fonte.pontos,pos))
    def inversa(x,y):
        tx=ty=0.
        total=.000018
        for dx,dy,px,py in deltas:
            peso=1/((x-px)**2+(y-py)**2+3.)**1.52
            total+=peso
            tx+=peso*dx
            ty+=peso*dy
        return (x+tx/total,y+ty/total)
    xs=list(range(0,CELULA[0],6))+[CELULA[0]]
    ys=list(range(0,CELULA[1],6))+[CELULA[1]]
    grade={(x,y):inversa(x,y) for x in xs for y in ys}
    malha=[]
    for y,y1 in zip(ys,ys[1:]):
        for x,x1 in zip(xs,xs[1:]):
            quad=grade[x,y]+grade[x,y1]+grade[x1,y1]+grade[x1,y]
            malha.append(((x,y,x1,y1),quad))
    return fonte.imagem.transform(CELULA,Image.Transform.MESH,malha,Image.Resampling.BICUBIC),pos


def preparar(nome):
    material,ordem = SERIES[nome]
    chaves = [chave(material,i) for i in ordem]
    atlas = Image.new("RGBA",(CELULA[0]*10,CELULA[1]*6))
    farois, maos, ombros = [],[],[]
    for indice in range(AMOSTRAS):
        t = indice/(AMOSTRAS if nome in CICLOS else AMOSTRAS-1)
        if nome == "planeio":
            t=.88+.12*cos(2*pi*t)
        fase=t*(len(chaves) if nome in CICLOS else len(chaves)-1)
        a=int(fase)
        b=(a+1)%len(chaves) if nome in CICLOS else min(a+1,len(chaves)-1)
        im,pontos=intervalo(chaves[a],chaves[b],fase-a)
        sola=im.getchannel("A").point(lambda a:255 if a>=90 else 0).getbbox()[3]
        dy=BASE-sola if nome not in ("voo","queda","planeio","mergulho") else 0
        cel=Image.new("RGBA",CELULA)
        cel.paste(im,(0,dy))
        farol,punho,ombro=pontos[:3]
        farois.append(ouro(cel,(farol[0],farol[1]+dy),10))
        maos.append((round(punho[0]),round(punho[1]+dy)))
        ombros.append((round(ombro[0]),round(ombro[1]+dy)))
        atlas.paste(cel,(indice%10*CELULA[0],indice//10*CELULA[1]))
    return atlas,farois,maos,ombros
