"""Quatro temas instrumentais próprios. Síntese local, sem samples externos."""
from array import array
from pathlib import Path
import math
import random
import wave

def gerar(destino):
    sr=22050
    motivos=((0,7,3,10,7,3,2,5),(0,2,7,5,3,7,10,5),
             (0,0,7,3,0,5,2,7),(0,7,12,10,7,3,5,2))
    for boss,motivo in enumerate(motivos):
        bpm=(116,124,132,128)[boss];beat=60/bpm;duracao=beat*32
        voz=[0.]*round(duracao*sr);rng=random.Random(9100+boss)
        def nota(inicio,dur,midi,ganho):
            freq=440*2**((midi-69)/12)
            for i in range(round(dur*sr)):
                pos=round(inicio*sr)+i
                if pos>=len(voz): break
                t=i/sr;env=min(1,t/.012)*math.exp(-4*t/dur)*min(1,(dur-t)/.025)
                voz[pos]+=ganho*env*(math.sin(2*math.pi*freq*t)+.22*math.sin(4*math.pi*freq*t))
        for passo in range(32):
            tonica=(45,43,40,45)[boss]+(0,0,-2,3)[passo//8]
            nota(passo*beat,beat*.8,tonica,.16)
            nota(passo*beat,beat*.65,tonica+24+motivo[passo%8],.11)
            if boss in (1,3):nota((passo+.5)*beat,beat*.4,tonica+31,.045)
            for i in range(round(.1*sr)):
                t=i/sr;p=round(passo*beat*sr)+i
                if p<len(voz):
                    voz[p]+=.11*math.sin(2*math.pi*(75*t-180*t*t))*math.exp(-45*t)
                    if passo%2:voz[p]+=.035*rng.uniform(-1,1)*math.exp(-65*t)
        pico=max(1.,max(map(abs,voz))/.65)
        dados=array('h',(round(max(-1,min(1,v/pico))*32767) for v in voz))
        with wave.open(str(destino/f'trilha_chefe_{boss}.wav'),'wb') as f:
            f.setparams((1,2,sr,0,'NONE','not compressed'));f.writeframes(dados.tobytes())

if __name__=='__main__':gerar(Path(__file__).resolve().parents[1]/'assets'/'sons')
