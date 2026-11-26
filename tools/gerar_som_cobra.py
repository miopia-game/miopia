"""Silvos próprios por ruído filtrado e envelope. Sem samples externos."""
from array import array
from pathlib import Path
import math,random,wave

def gerar(pasta):
    sr=22050
    for nome,duracao in (("silvo_perto",.52),("silvo_ataque",.35)):
        rng=random.Random(nome);filtro=0.;dados=array('h')
        for n in range(round(sr*duracao)):
            t=n/sr;ruido=rng.uniform(-1,1)
            filtro=.75*filtro+.25*ruido
            envelope=min(1,t/.025)*max(0,1-t/duracao)**1.4
            pulso=.6+.4*math.sin(t*math.pi*9)**2
            dados.append(round((ruido-filtro)*envelope*pulso*8500))
        with wave.open(str(pasta/(nome+".wav")),"wb") as f:
            f.setparams((1,2,sr,0,"NONE","not compressed"));f.writeframes(dados.tobytes())

if __name__=="__main__":gerar(Path(__file__).resolve().parents[1]/"assets"/"sons")
