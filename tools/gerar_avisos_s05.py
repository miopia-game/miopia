"""Avisos autorais sintetizados por osciladores e ruído local, sem samples."""
from array import array
from math import sin, pi
from pathlib import Path
from random import Random
import sys
import wave


def gerar(pasta):
    sr=22050
    sons={'casco_salto':(.46,180,570), 'casco_chifre':(.39,510,150),
          'coruja_garra':(.43,740,220), 'coruja_penas':(.46,940,680),
          'casco_muda':(.75,105,78), 'coruja_muda':(.75,300,420)}
    for nome,(duracao,inicio,fim) in sons.items():
        rng=Random(nome);fase=0.;dados=array('h');filtro=0.
        for n in range(round(sr*duracao)):
            t=n/sr;p=t/duracao
            fase+=2*pi*(inicio+(fim-inicio)*p)/sr
            ruido=rng.uniform(-1,1);filtro=.7*filtro+.3*ruido
            env=min(1.,t/.018)*max(0.,1-p)**1.5
            if nome=='coruja_penas':env*=.3+.7*sin(pi*p*3)**2
            sinal=(sin(fase)*.45+sin(fase*1.51)*.16+(ruido-filtro)*.28)*env
            dados.append(round(sinal*12500))
        if sys.byteorder!='little':dados.byteswap()
        with wave.open(str(pasta/(nome+'.wav')),'wb') as f:
            f.setparams((1,2,sr,0,'NONE','not compressed'));f.writeframes(dados.tobytes())


if __name__=='__main__':gerar(Path(__file__).resolve().parents[1]/'assets'/'sons')
