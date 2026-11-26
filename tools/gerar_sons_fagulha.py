"""Sintetiza os dois gestos da fagulha sem amostras externas."""
from array import array
from math import exp, pi, sin
from pathlib import Path
from random import Random
import sys
import wave

PASTA = Path(__file__).resolve().parents[1] / "assets" / "sons"
TAXA = 44100


def gerar(nome, duracao, pouso):
    ruido = Random(397 if pouso else 748)
    dados = array("h")
    anterior = 0.
    for i in range(round(duracao * TAXA)):
        t = i / TAXA
        grao = ruido.uniform(-1, 1)
        agudo = (grao - anterior) * .5
        anterior = grao
        if pouso:
            # Casca oca no contato, seguida do som fino da brasa aderindo.
            madeira = .56 * sin(2*pi*(245*t + .8*(1-exp(-100*t)))) * exp(-38*t)
            ataque = madeira + .33 * agudo * exp(-165*t)
            vibracao = sum(a * sin(2*pi*hz*t)*exp(-k*t)
                           for a,hz,k in ((.17,760,23),(.12,1245,16),(.06,1830,19)))
        else:
            ataque = .44 * agudo * exp(-78*t) + .25 * sin(2*pi*310*t) * exp(-50*t)
            fase = 2*pi*(510*t + 750*.037*(1-exp(-t/.037)))
            vibracao = (.34*sin(fase) + .10*sin(1.98*fase)) * exp(-23*t)
        borda = min(1., i/(.0015*TAXA), (duracao-t)/.012)
        dados.append(round(28200 * borda * (ataque+vibracao)))
    if sys.byteorder != "little":
        dados.byteswap()
    with wave.open(str(PASTA / (nome + ".wav")), "wb") as arquivo:
        arquivo.setparams((1, 2, TAXA, 0, "NONE", "not compressed"))
        arquivo.writeframes(dados.tobytes())


if __name__ == "__main__":
    gerar("fagulha", .19, False)
    gerar("pouso_fagulha", .39, True)
