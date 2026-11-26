"""Síntese original S07. Sem samples, melodias importadas ou dependências extras."""
from array import array
import json, math, random, wave
from pathlib import Path

SR=22050
ESPECIES=('morcego','aranha','sombra','vespa','carabideo','cobra')


def escrever(p,voz):
    pico=max(.001,max(map(abs,voz)))
    # Pico de 0,48; avisos deixam margem para duas criaturas simultâneas.
    ganho=min(1.,.48/pico)
    dados=array('h',(round(max(-1,min(1,v*ganho))*32767) for v in voz))
    import sys
    if sys.byteorder!='little':dados.byteswap()
    with wave.open(str(p),'wb') as f:
        f.setparams((1,2,SR,0,'NONE','not compressed'));f.writeframes(dados.tobytes())


def aviso(especie,familia):
    rng=random.Random(700+especie*17+familia)
    dur=.31+familia*.037;voz=[]
    for i in range(round(SR*dur)):
        t=i/SR;u=t/dur
        base=(820,270,155,630,105,440)[especie]
        # Cadência identifica a família; timbre e registro identificam a espécie.
        pulso=max(0.,math.sin(math.pi*(familia+1)*u))**.45
        freq=base*(1+(familia-2)*.06)+(-1 if familia%2 else 1)*base*.28*u
        fase=2*math.pi*freq*t
        cor=(math.sin(fase)+.24*math.sin(fase*2.01)+rng.uniform(-1,1)*(.2 if especie in (1,4,5) else .05))
        env=min(1,t/.012)*min(1,(dur-t)/.025)*pulso
        voz.append(.29*cor*env)
    return voz


def tema(nome):
    bpm={'jardim':78,'retorno':84,'chefe_final':144}[nome]
    beat=60/bpm;dur=32*beat;voz=[0.]*round(dur*SR)
    motivo=(0,7,10,7,3,2,7,5) if nome!='retorno' else (0,7,12,9,7,4,2,7)
    def nota(inicio,comprimento,midi,ganho):
        freq=440*2**((midi-69)/12)
        for i in range(round(comprimento*SR)):
            p=round(inicio*SR)+i
            if p>=len(voz):break
            t=i/SR;env=min(1,t/.018)*math.exp(-3*t/comprimento)*min(1,(comprimento-t)/.035)
            voz[p]+=ganho*env*(math.sin(2*math.pi*freq*t)+.16*math.sin(2*math.pi*freq*2*t))
    for k in range(32):
        raiz=45+(0,-2,3,0)[k//8]
        nota(k*beat,beat*.9,raiz,.13)
        nota(k*beat,beat*1.6,raiz+24+motivo[k%8],.11)
        if k%4==0:nota(k*beat,beat*3.8,raiz+19,.055)
        if nome=='chefe_final':
            nota((k+.5)*beat,beat*.35,raiz+31,.065)
            for n in range(round(.1*SR)):
                t=n/SR;p=round(k*beat*SR)+n
                if p<len(voz):voz[p]+=.13*math.sin(2*math.pi*(78*t-190*t*t))*math.exp(-40*t)
    return voz


def gerar(destino):
    destino.mkdir(exist_ok=True,parents=True)
    for e,especie in enumerate(ESPECIES):
        for familia in range(5):escrever(destino/f'aviso_{especie}_{familia}.wav',aviso(e,familia))
    for nome in ('jardim','retorno','chefe_final'):escrever(destino/f'trilha_{nome}.wav',tema(nome))
    for nome,e,f in (('coruja_eco',2,4),('resgate',0,1),('chamado_final',2,2),('harmonia',0,4)):
        escrever(destino/f'{nome}.wav',aviso(e,f))
    print('30 avisos, quatro sinais e três temas sintetizados em',destino)


if __name__=='__main__':gerar(Path(__file__).resolve().parents[1]/'assets'/'sons')
