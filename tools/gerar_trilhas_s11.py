"""Partitura e síntese das trilhas S11. FFmpeg é usado só na exportação."""
import argparse
import math
import random
import shutil
import subprocess
import wave
from array import array
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory

TAXA = 24000
RAIZ = Path(__file__).resolve().parents[1]
TAU = math.tau


@dataclass(frozen=True)
class Arena:
    titulo: str
    bpm: int
    tonica: int
    acordes: tuple
    motivo: tuple
    pulsos: tuple
    caixa: tuple
    timbre: str


# Cada acorde especifica a raiz e a terça. O motivo traz tempo em batidas
# e distância em semitons, com centros tonais e cadências próprios.
ARENAS = {
    "chefe_0": Arena("Rasante de Âmbar", 142, 38,
        ((0,3),(-2,4),(1,4),(-4,3),(0,3),(3,4),(-2,4),(1,4)),
        ((0,7),(.75,10),(1.5,12),(2.5,8),(3.25,5),(3.75,3)),
        (0,1,1.75,2.5,3), (1,3), "pulso"),
    "chefe_1": Arena("Seda em Contratempo", 126, 40,
        ((0,3),(-3,4),(3,3),(1,4),(0,3),(-5,3),(-3,4),(1,3)),
        ((.25,12),(1,6),(1.75,15),(2.25,7),(3,10),(3.5,3)),
        (0,.75,1.5,2.5,3.25), (1.5,3), "vidro"),
    "chefe_2": Arena("Couraça de Seiva", 112, 42,
        ((0,3),(0,3),(-3,4),(-2,4),(0,3),(1,3),(-2,4),(-7,3)),
        ((0,0),(.5,0),(1.75,7),(2.5,6),(3,3)),
        (0,.5,1.75,2.75,3.5), (2,), "serra"),
    "chefe_3": Arena("O Sino sem Luz", 134, 45,
        ((0,3),(-5,3),(-3,4),(2,3),(-2,4),(-5,3),(-4,4),(0,3)),
        ((0,12),(1.25,16),(2,19),(2.75,10),(3.5,7)),
        (0,1.25,2.5,3.75), (1,3), "vidro"),
    "chefe_final": Arena("A Colônia Responde", 150, 45,
        ((0,3),(-4,4),(3,4),(-2,4),(0,3),(5,4),(3,4),(-2,4)),
        ((0,7),(.5,12),(1,15),(1.75,19),(2.5,17),(3.25,12)),
        (0,1,2,3,3.75), (1,3), "pulso"),
    "chefe_caruncho": Arena("Sob a Casca", 120, 36,
        ((0,3),(3,3),(0,3),(-1,4),(-5,3),(-3,4),(-2,3),(-1,4)),
        ((.5,3),(1.25,7),(1.75,6),(2.5,3),(3.5,10)),
        (0,1.25,1.75,2.5,3.5), (1,2.75), "madeira"),
}


@dataclass(frozen=True)
class Mata:
    titulo: str
    bpm: int
    tonica: int
    acordes: tuple
    cor: tuple
    timbre: str
    vento: float


AMBIENTES = {
    "menu": Mata("Quando a Mata Respira", 59, 43, ((0,3),(-3,4),(-5,3),(-2,4)), (7,14,10,3), "vidro", .041),
    "historia": Mata("A Noite do Raio", 52, 40, ((0,3),(1,4),(-5,3),(-2,4)), (0,13,7,2), "vidro", .050),
    "bosque": Mata("Entre Samambaias", 55, 40, ((0,3),(-2,4),(-5,3),(3,4)), (7,10,12,5), "madeira", .057),
    "corrego": Mata("Corrente sob as Raízes", 64, 43, ((0,3),(-5,3),(-3,4),(-2,4)), (2,7,12,14), "vidro", .085),
    "taquaral": Mata("O Ar entre os Colmos", 58, 42, ((0,3),(-2,4),(1,3),(-7,3)), (3,9,6,12), "madeira", .046),
    "gruta": Mata("Eco de Figueira", 49, 45, ((0,3),(-4,4),(-5,3),(-2,4)), (0,7,13,15), "vidro", .065),
    "jardim": Mata("A Primeira Muda", 62, 45, ((0,3),(-2,4),(3,4),(-4,4)), (7,12,17,15), "madeira", .040),
    "retorno": Mata("As Vozes do Orvalho", 60, 45, ((0,4),(-5,4),(-3,3),(-2,4)), (7,12,16,19), "vidro", .030),
}


@lru_cache(maxsize=56)
def sintetizar(timbre, nota, quadros):
    """Amostras de uma nota local. O envelope fecha antes de cada corte."""
    freq = 440 * 2 ** ((nota - 69) / 12)
    fase = TAU * freq / TAXA
    dados = array("f")
    for i in range(quadros):
        t = i / TAXA
        u = i / quadros
        x = fase * i
        if timbre == "névoa":
            env = min(1., u / .28, (1. - u) / .30)
            onda = (.65 * math.sin(x) + .23 * math.sin(x * 2 + 1.08 * t)
                    + .12 * math.sin(x * 3 - 1.7 * t))
            onda *= .82 + .18 * math.sin(1.8 * t + freq * .01)
        else:
            env = min(1., t/.012, (quadros-i)/(TAXA*.024)) * math.exp(-2.1*u)
            if timbre == "vidro":
                onda = .72 * math.sin(x + .85 * math.exp(-3*u) * math.sin(2.005*x)) + .18 * math.sin(x * 2)
            elif timbre == "madeira":
                onda = .68 * math.sin(x) + math.exp(-12*u) * (.23 * math.sin(x*2.77) + .12 * math.sin(x*4.15))
            elif timbre == "serra":
                onda = sum(math.sin(x*n)/n * (-1)**(n+1) for n in (1,2,3,4)) * .68
            elif timbre == "pulso":
                onda = .75 * math.sin(x) + .20 * math.sin(3*x) + .08 * math.sin(5*x)
            else:  # subgrave com o segundo harmônico para caixas pequenas
                onda = .83 * math.sin(x) + .21 * math.sin(2*x)
        dados.append(env * onda)
    return dados


@lru_cache(maxsize=8)
def batida(tipo):
    duracao = {"bumbo":.235,"caixa":.18,"metal":.10,"pó":.054}[tipo]
    rng = random.Random(f"miopia-s11/{tipo}")
    grave = 0.
    dados = array("f")
    for i in range(round(duracao*TAXA)):
        t = i/TAXA
        ruido = rng.uniform(-1,1)
        grave += .22 * (ruido-grave)
        bordas = min(1.,t/.004,(duracao-t)/.024)
        if tipo == "bumbo":
            sinal = math.sin(TAU * (47*t + 2.1*(1-math.exp(-37*t)))) * math.exp(-14*t)
        elif tipo == "caixa":
            sinal = (.52*(ruido-grave) + .42*math.sin(TAU*173*t)*math.exp(-17*t))*math.exp(-23*t)
        elif tipo == "metal":
            sinal = (.48*grave + .28*math.sin(TAU*245*t) + .16*math.sin(TAU*403*t))*math.exp(-35*t)
        else:
            sinal = (ruido-grave)*math.exp(-65*t)
        dados.append(bordas*sinal)
    return dados


class Mix:
    def __init__(self, batida_s, batidas):
        self.beat = batida_s
        self.frames = round(batida_s * batidas * TAXA)
        self.esq = array("f", [0.]) * self.frames
        self.dir = array("f", [0.]) * self.frames

    def somar(self, dados, tempo, ganho, pan=0.):
        pos = round(tempo*self.beat*TAXA) % self.frames
        e = ganho*math.sqrt((1-pan)/2)
        d = ganho*math.sqrt((1+pan)/2)
        for valor in dados:
            self.esq[pos] += valor*e
            self.dir[pos] += valor*d
            pos += 1
            if pos == self.frames:
                pos = 0

    def nota(self, tempo, duracao, midi, timbre, ganho, pan=0., ecos=()):
        voz = sintetizar(timbre,midi,round(duracao*self.beat*TAXA))
        self.somar(voz,tempo,ganho,pan)
        for intervalo, intensidade, posicao in ecos:
            self.somar(voz,tempo+intervalo,ganho*intensidade,posicao)

    def atmosfera(self, semente, ganho):
        rng = random.Random(semente)
        for faixa, fase in ((self.esq,0.),(self.dir,1.2)):
            lento = rapido = 0.
            for i in range(self.frames):
                ruido = rng.uniform(-1,1)
                lento += .017*(ruido-lento)
                rapido += .06*(ruido-rapido)
                subida = min(1., i/2800, (self.frames-i)/2800)
                envolvente = (.54+.32*math.sin(TAU*i*3/self.frames+fase)) * subida
                faixa[i] += (rapido*.48+lento*.52)*ganho*envolvente

    def salvar(self, caminho, rms_alvo):
        e, d = self.esq, self.dir
        rms = math.sqrt((sum(v*v for v in e)+sum(v*v for v in d))/(2*self.frames))
        pico = max(max(map(abs,e)),max(map(abs,d)))
        ganho = min(rms_alvo/rms,.80/pico)
        pcm = array("h",(round(v*ganho*32767) for par in zip(e,d) for v in par))
        import sys
        if sys.byteorder != "little":
            pcm.byteswap()
        with wave.open(str(caminho),"wb") as w:
            w.setparams((2,2,TAXA,self.frames,"NONE","not compressed"))
            w.writeframes(pcm.tobytes())


def compor_arena(ficha):
    mix = Mix(60/ficha.bpm, 96)
    for compasso in range(24):
        base = 4*compasso
        bloco, pos = divmod(compasso,8)
        raiz, terca = ficha.acordes[pos]
        raiz += ficha.tonica
        quebra = pos in (3,7)
        for i,pulso in enumerate(ficha.pulsos):
            if quebra and pulso >= 3:
                continue
            mix.somar(batida("bumbo"),base+pulso,.20 if i == 0 else .135)
            midi = raiz + (7 if i == 2 and bloco == 2 else 0)
            mix.nota(base+pulso,.36,midi,"sub",.19 if i%2 == 0 else .14)
            if ficha.timbre == "serra" or bloco == 2:
                mix.nota(base+pulso,.27,midi+12,"serra",.070,(-1)**i*.31)
        for pulso in ficha.caixa:
            mix.somar(batida("caixa"),base+pulso,.15,.22)
            if ficha.timbre == "serra":
                mix.somar(batida("metal"),base+pulso+.18,.087,-.42)
        for i in range(8 if bloco else 4):
            if quebra and i >= 6:
                break
            mix.somar(batida("pó"),base+(.5 if bloco else 1)*i+.25,.039+(.018 if i%3==0 else 0),(-1)**i*.59)
        acordes = (0, terca, 7, 10 if terca == 3 else 11)
        for i,grau in enumerate(acordes):
            mix.nota(base-.12,4.45,raiz+24+grau,"névoa",.067+.011*bloco,(-1)**i*.54)
        for i,(pulso,grau) in enumerate(ficha.motivo):
            if (bloco == 0 and i in (2,4)) or (quebra and pulso > 2.5):
                continue
            registro = 24 if ficha.timbre=="serra" else 36
            grau += 0 if bloco < 2 else (12 if i == 0 else -12 if i == 3 else 0)
            mix.nota(base+pulso,.46 if ficha.timbre=="serra" else .57,raiz+registro+grau,
                     ficha.timbre,.132,(-1)**i*.24,((.75,.28,-.55),(1.5,.12,.62)))
        if bloco and pos%2==0:
            for n in range(4):
                mix.nota(base+.25+n, .34, raiz+24+acordes[(n+pos)%4],"pulso",.058,.45)
    return mix


def compor_mata(ficha):
    mix = Mix(60/ficha.bpm, 48)
    mix.atmosfera(ficha.titulo,ficha.vento)
    for compasso in range(12):
        pos = compasso * 4
        deslocamento,terca = ficha.acordes[(compasso//2)%len(ficha.acordes)]
        raiz = ficha.tonica + deslocamento
        if compasso%2 == 0:
            mix.nota(pos-.70,9.30,raiz,"névoa",.145)
            for i,grau in enumerate((0,terca,7,14)):
                mix.nota(pos-.85+i*.15,9.15,raiz+12+grau,"névoa",.075,(-1)**i*.64)
        pulso = (1.35,.65,2.70,.10)[compasso%4]
        grau = ficha.cor[compasso%len(ficha.cor)]
        if compasso not in (3,11):
            mix.nota(pos+pulso,1.68,raiz+36+grau,ficha.timbre,.09,(-1)**compasso*.45,
                     ((.72,.37,.76),(1.55,.19,-.71),(2.9,.09,.46)))
        if compasso in (2,5,8,10):
            mix.nota(pos+2.2,2.8,raiz+19,"névoa",.062,.28)
    return mix


def gerar(destino, temas):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("FFmpeg com libvorbis é necessário apenas para gerar os arquivos de trilha.")
    destino.mkdir(parents=True,exist_ok=True)
    # O arquivo funcional continua disponível se a exportação for interrompida.
    with TemporaryDirectory(dir=destino, prefix=".trilha-s11-") as tmp:
        banco = Path(tmp)/"tema.wav"
        for nome in temas:
            arena = nome in ARENAS
            ficha = ARENAS[nome] if arena else AMBIENTES[nome]
            mix = compor_arena(ficha) if arena else compor_mata(ficha)
            mix.salvar(banco, .108 if arena else .068)
            ogg = destino/f"trilha_{nome}.ogg"
            temporaria = Path(tmp)/ogg.name
            subprocess.run([
                ffmpeg,"-nostdin","-hide_banner","-loglevel","error","-y",
                "-i",str(banco),"-map_metadata","-1","-c:a","libvorbis","-q:a","5",
                "-fflags","+bitexact","-flags:a","+bitexact",
                "-metadata",f"title={ficha.titulo}","-metadata","album=Miopia",
                str(temporaria),
            ],check=True)
            temporaria.replace(ogg)
            print(f"{ogg.name} | {ficha.titulo} | {ficha.bpm} BPM | {mix.frames/TAXA:.2f} s",flush=True)
            sintetizar.cache_clear()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--destino",type=Path,default=RAIZ/"assets"/"sons")
    p.add_argument("--tema",choices=tuple(ARENAS)+tuple(AMBIENTES),action="append")
    a = p.parse_args()
    gerar(a.destino,a.tema or (*ARENAS,*AMBIENTES))
