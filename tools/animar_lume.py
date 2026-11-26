"""Prepara os quadros HD de Lume com as cinco poses pintadas do elenco."""
from functools import lru_cache
import json
from math import cos, pi, radians, sin, tau
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

RAIZ = Path(__file__).resolve().parents[1]
FONTES = RAIZ / "docs/arte/fontes/lume"
DESTINO = RAIZ / "assets/arte/lume"
CELULA = (192, 160)
PE = 132
SS = 2
FAIXAS = ("guarda", "passo", "corrida", "voo", "queda", "planeio", "agachar",
          "deslizar", "escalar", "parede", "golpe", "mergulho", "recuo", "clarao", "lancar")


def limpar(im):
    im = im.convert("RGBA")
    im.putalpha(im.getchannel("A").point(lambda a: 0 if a < 28 else min(255, round(a*255/252))))
    return im.crop(im.getchannel("A").getbbox())


@lru_cache
def pintura(nome):
    if nome == "guarda":
        return limpar(Image.open(FONTES / "guarda.png"))
    indice = ("baixa", "bote", "salto", "escalada").index(nome)
    folha = Image.open(FONTES / "acoes.png")
    x, y = indice % 2, indice // 2
    w, h = folha.size
    return limpar(folha.crop((x*w//2, y*h//2, (x+1)*w//2, (y+1)*h//2)))


@lru_cache
def roupa_e_botas():
    """Separa as botas da guarda para alternar o apoio sem deformar a máscara."""
    im = pintura("guarda")
    w,h = im.size
    m = Image.new("L", im.size)
    d = ImageDraw.Draw(m)
    limites = (
        ((.19,.90),(.29,.88),(.32,.86),(.333,.835),(.405,.824),(.41,.856),(.48,.87),(.48,1),(.19,1)),
        ((.53,.85),(.57,.81),(.627,.798),(.665,.804),(.71,.823),(.81,.89),(.81,1),(.53,1)),
    )
    botas = []
    for i, limite in enumerate(limites):
        d.polygon([(round(x*w),round(y*h)) for x,y in limite],fill=255)
        x0,x1 = ((.20,.46),(.53,.79))[i]
        bota = im.crop((round(w*x0),round(.882*h),round(w*x1),h))
        botas.append(bota.crop(bota.getchannel("A").getbbox()))
    roupa = im.copy()
    roupa.putalpha(ImageChops.subtract(im.getchannel("A"),m))
    return roupa, botas


def escolha(nome, t):
    if nome in ("agachar","deslizar"):
        return "baixa", 56 if nome == "agachar" else 52
    if nome in ("voo","queda","planeio","mergulho"):
        return "salto", 88
    if nome in ("escalar","parede"):
        return "escalada", 96
    if nome in ("golpe","lancar") and .18 <= t <= .78:
        return "bote", 85
    return "guarda", 107


def desenhar_asas(im, raiz, t, planar):
    """Duas membranas batem na mesma frequência em planos de profundidade distintos."""
    d = ImageDraw.Draw(im)
    for perto in (False,True):
        fase = tau*t + (.14 if perto else 0)
        if planar:
            angulo = (156 if perto else 132) + 5*cos(fase)
        else:
            angulo = (153 if perto else 135) + 43*cos(fase)
        a = radians(angulo)
        comp = (55 if perto else 47)*SS
        larg = (9 if perto else 8)*SS*(.68+.32*abs(sin(a)))
        def pt(u,v):
            return (round(raiz[0]+u*comp*cos(a)+v*larg*sin(a)),
                    round(raiz[1]-u*comp*sin(a)+v*larg*cos(a)))
        pol = [(0,0),(.22,-.68),(.58,-1),(.90,-.72),(1,-.15),(.93,.28),(.71,.65),(.33,.62)]
        d.polygon([pt(u,v) for u,v in pol],fill="#392738")
        d.polygon([pt(.02+.94*u,.72*v) for u,v in pol],fill="#e1cea5" if perto else "#a4b8a4")
        d.polygon([pt(u,v) for u,v in ((.08,0),(.55,-.25),(.94,-.40),(.71,.38),(.29,.41))],
                  fill="#c2ae88" if perto else "#809992")
        d.line([pt(.02,0),pt(.54,-.13),pt(.96,-.28)],fill="#675752",width=SS)
        for u in (.38,.66):
            d.line([pt(u-.09,.47),pt(u,-.14),pt(u+.1,-.72)],fill="#857366",width=SS)


def pano(im, t, nome):
    """A ponta do lenço atrasa em relação ao nó; a cabeça fica rígida."""
    w,h = im.size
    forca = 1.2 if nome in ("guarda","agachar","escalar","parede") else 3.3
    passo = 8*SS
    malha = []
    def origem(x,y):
        u,v = x/w,y/h
        livre = max(0.,1-u/.55)**1.4
        altura = max(0.,1-abs(v-.46)/.22)
        atraso = sin(t*tau-u*3)
        return x, y - SS*forca*atraso*livre*altura
    for y in range(0,h,passo):
        y1=min(h,y+passo)
        for x in range(0,w,passo):
            x1=min(w,x+passo)
            vertices=((x,y),(x,y1),(x1,y1),(x1,y))
            malha.append(((x,y,x1,y1),tuple(v for ponto in vertices for v in origem(*ponto))))
    return im.transform(im.size,Image.Transform.MESH,malha,Image.Resampling.BICUBIC)


def quadro(nome, t):
    chave,altura = escolha(nome,t)
    andando = nome in ("passo","corrida")
    base = roupa_e_botas()[0] if andando else pintura(chave)
    largura = round(altura*base.width/base.height)
    im = pano(base.resize((largura*SS,altura*SS),Image.Resampling.LANCZOS),t,nome)
    ciclo = tau*t
    angulo,dx,dy = 0.,0.,0.
    eixo = {"guarda":.54, "baixa":.59, "bote":.59, "salto":.57, "escalada":.68}[chave]
    if andando:
        angulo = (-13 if nome == "corrida" else -6)+2*cos(2*ciclo)
        dy = (-2.5 if nome == "corrida" else -1.6)*(1-cos(2*ciclo))
    elif nome in ("voo","queda","planeio","mergulho"):
        angulo = {"voo":5, "queda":-7, "planeio":-16, "mergulho":-34}[nome]+1.6*sin(ciclo)
        dy = -3.5
    elif nome in ("golpe","lancar"):
        impulso = sin(pi*min(1,max(0,(t-.13)/.78)))
        preparar = sin(pi*min(1.,t/.18))
        angulo = 7*preparar - 8*impulso
        dx = -3*preparar + (6 if nome == "golpe" else -4)*impulso
    elif nome == "recuo":
        angulo, dx = 10+2*sin(ciclo),-3
    elif nome == "deslizar":
        angulo, dx = -6,2
    elif nome == "escalar":
        dy = -2*(1-cos(ciclo))
    else:
        angulo = 1.2*sin(ciclo)
    # Rotações acontecem em torno da bacia. Os pés de apoio usam a linha do chão.
    px,py = eixo*largura,altura*.79
    ox,oy = CELULA[0]/2+dx, PE-altura+py+dy
    c,s = cos(radians(angulo)),sin(radians(angulo))
    def mundo(u,v):
        x,y = u*largura-px,v*altura-py
        return ((ox+x*c+y*s)*SS,(oy-x*s+y*c)*SS)
    inversa = (c,-s,(px-c*ox+s*oy)*SS,s,c,(py-s*ox-c*oy)*SS)
    out = Image.new("RGBA",tuple(x*SS for x in CELULA))
    if andando:
        d = ImageDraw.Draw(out)
        for i, bota in enumerate(roupa_e_botas()[1]):
            f = ciclo + i*pi
            coxa = mundo((.365,.64)[i],.805)
            alcance = 15 if nome == "corrida" else 10
            x = (CELULA[0]/2+(-7,6)[i]+alcance*cos(f))*SS
            y = (PE-(12 if nome == "corrida" else 8)*max(0.,sin(f)))*SS
            h = round(altura*.118*SS)
            b = bota.resize((round(h*bota.width/bota.height),h),Image.Resampling.LANCZOS)
            joelho = ((coxa[0]+x)*.5+3*SS*max(0.,sin(f)),(coxa[1]+y-h)*.5)
            d.line([coxa,joelho,(x,y-h*.55)],fill="#382031",width=round(5.8*SS),joint="curve")
            out.alpha_composite(b,(round(x-b.width*.48),round(y-b.height)))
    if nome in ("voo","queda","planeio","mergulho"):
        desenhar_asas(out,mundo(.58,.44),t,nome in ("planeio","mergulho"))
    out.alpha_composite(im.transform(out.size,Image.Transform.AFFINE,inversa,Image.Resampling.BICUBIC))
    # Posição pintada dos segmentos de âmbar em cada chave.
    farol = mundo(*{"guarda":(.17,.745), "baixa":(.213,.747), "bote":(.205,.778),
                    "salto":(.32,.738), "escalada":(.323,.722)}[chave])
    if nome not in ("voo","queda","planeio","mergulho","escalar","parede"):
        sola = out.getchannel("A").point(lambda a: 255 if a >= 100 else 0).getbbox()[3]
        correcao = PE*SS - sola
        alinhada = Image.new("RGBA",out.size)
        alinhada.paste(out,(0,correcao))
        out,farol = alinhada,(farol[0],farol[1]+correcao)
    return out, [round(x/SS) for x in farol]


def preparar():
    DESTINO.mkdir(parents=True,exist_ok=True)
    farois = {}
    for nome in FAIXAS:
        folha = Image.new("RGBA",(CELULA[0]*4,CELULA[1]*4))
        farois[nome] = []
        for i in range(16):
            t = i/(15 if nome in ("golpe","lancar","mergulho") else 16)
            im,farol = quadro(nome,t)
            folha.paste(im.resize(CELULA,Image.Resampling.LANCZOS),(CELULA[0]*(i%4),CELULA[1]*(i//4)))
            farois[nome].append(farol)
        folha.save(DESTINO / (nome+".png"),optimize=True)
    (DESTINO / "farol.json").write_text(json.dumps(farois)+"\n",encoding="utf-8")


if __name__ == "__main__":
    preparar()
