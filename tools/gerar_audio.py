"""Produção offline das ambiências de Miopia. Apenas este gerador usa NumPy."""
from pathlib import Path
import wave
import numpy as np

SR = 44100
TAU = 2 * np.pi
# Nível de vento, água, canas, ressonância grave. Cada ambiente tem seu espaço.
CENAS = {
    "menu": (.55, .16, .05, .23), "historia": (.64, .20, .18, .29),
    "bosque": (.48, .32, .09, .19), "corrego": (.23, .85, .03, .16),
    "taquaral": (.68, .03, .62, .22), "gruta": (.22, .48, .04, .53),
    "derrota": (.34, .02, .05, .49), "vitoria": (.34, .43, .06, .13),
    "creditos": (.39, .25, .04, .21),
}
def eixo(d): return np.arange(round(d*SR))/SR

def ru(t,rng,passo):
    x=np.arange(0,len(t)+passo,passo)
    return np.interp(np.arange(len(t)),x,rng.normal(0,1,len(x)))

def colocar(mix,voz,quando,gain=1):
    i=round(quando*SR)%len(mix)
    n=min(len(voz),len(mix)-i)
    mix[i:i+n]+=voz[:n]*gain
    if n<len(voz): mix[:len(voz)-n]+=voz[n:]*gain

def salvar(path,som,pico=.76):
    fade=min(450,len(som)//4)
    som[:fade]*=np.linspace(0,1,fade);som[-fade:]*=np.linspace(1,0,fade)
    som*=pico/max(.04,float(np.max(np.abs(som))))
    with wave.open(str(path),"wb") as f:
        f.setparams((1,2,SR,0,"NONE","not compressed"))
        f.writeframes(np.round(np.clip(som,-1,1)*32767).astype("<i2").tobytes())

def sopro(t, rng, passo):
    raw = ru(t, rng, passo)
    return raw - np.roll(raw, passo//2)


def folhico(t, textura, freq):
    """Apoio na folha: atrito seco e uma ressonância grave muito breve."""
    ataque = np.minimum(1., t/.007)
    madeira = np.sin(TAU*freq*t) * np.exp(-68*t)
    return ataque * (.18*madeira + textura*np.exp(-43*t))


def ambiente(nome, mistura, out):
    seed = 101 + sum(map(ord, nome))
    rng = np.random.default_rng(seed)
    t = eixo(24 + seed % 5)
    vento, agua, taquara, caverna = mistura
    mar = .35 + .65 * (.5+.5*np.cos(TAU*t/(len(t)/SR)))**2
    # Ruído colorido de folhas e de água, sem progressão harmônica nem batida.
    voz = (sopro(t,rng,220)*.13 + sopro(t,rng,63)*.027)*vento*mar
    voz += np.sin(TAU*(42*t + .13*np.sin(TAU*t*.15))) * caverna * mar * .085
    voz += (sopro(t,rng,14)*.045 + sopro(t,rng,50)*.042) * agua
    for quando in rng.uniform(0,len(t)/SR,max(2,round(agua*21))):
        t2=eixo(.65)
        gota=np.sin(TAU*(510*t2+164*t2**2))*np.exp(-19*t2)*np.minimum(1,t2*140)
        colocar(voz,gota,quando,agua*.16)
        colocar(voz,gota,quando+.17,caverna*.04)
    for quando in rng.uniform(0,len(t)/SR,round(taquara*20)):
        t2=eixo(.19)
        madeira=(sopro(t2,rng,33)+np.sin(TAU*245*t2)*.31)*np.exp(-32*t2)
        colocar(voz,madeira,quando,taquara*.12)
    salvar(out/("trilha_"+nome+".wav"),voz,.28)


def sons(out):
    rng=np.random.default_rng(4207)
    # duração, frequência inicial/final, madeira ou ar, ruído
    specs={"pulo":(.19,168,360,.11),"pouso":(.15,128,63,.35),"passo":(.085,96,62,.36),
        "deslize":(.35,175,55,.65),"golpe":(.23,340,97,.50),"pulso":(.68,147,538,.10),
        "coleta":(.47,507,780,.02),"acerto":(.21,198,62,.37),"dano":(.37,180,48,.45),
        "valvula":(.48,146,84,.48),"corda":(.42,109,301,.22),"porta":(.80,75,42,.42),
        "agua":(.92,260,103,.73),"sino":(1.05,470,440,.01),"raiz":(.83,210,410,.04),
        "aviso":(.40,126,267,.18),"teia":(.44,403,123,.17),"impacto":(.39,104,42,.43),
        "seiva":(.48,209,64,.45),"abertura":(.68,112,286,.03),"vulneravel":(.51,272,442,.03),
        "arena":(.72,145,74,.15),"derrota":(.94,272,73,.025),"vitoria":(.98,219,553,.02),
        "pagina":(.13,324,128,.51),"clique":(.13,271,381,.02),"navegar":(.11,248,209,.03),
        "retorno":(.57,172,330,.04),"vencer":(.74,209,415,.05)}
    for nome,(d,f1,f2,ar) in specs.items():
        t=eixo(d);u=t/d;p=TAU*(f1*t+(f2-f1)*t*t/(2*d))
        e=(1-np.exp(-t*100))*np.exp(-u*(3 if nome!="pulso" else 2.3))*np.clip((d-t)/.033,0,1)
        textura=ru(t,rng,17)
        sinal=(.72*np.sin(p)+.19*np.sin((2.71 if nome=="sino" else 2.02)*p)*np.exp(-u*5)
               +ar*textura)*e
        if nome in ("valvula","passo","porta"):sinal*=.5+.5*np.cos(TAU*t*(10 if nome=="porta" else 15))**2
        pico=.60
        if nome in ("passo","pouso"):
            sinal=folhico(t,textura,94 if nome=="passo" else 71)
            pico=.22 if nome=="passo" else .32
        elif nome in ("pulo","golpe","deslize"):
            # O contorno de ar substitui o glissando a cada movimento de Lume.
            asa=np.sin(np.pi*u)**2
            sinal=textura*asa*np.exp(-2.8*u) + .08*np.sin(TAU*116*t)*e
            pico=.34 if nome=="golpe" else .29
        elif nome in ("navegar","clique"):
            sinal=folhico(t,textura,164)
            pico=.22 if nome=="navegar" else .28
        salvar(out/(nome+".wav"),sinal,pico)
    # O novo passo tem seu próprio gerador e não altera os sons antigos.
    t=eixo(.094)
    salvar(out/"passo_folha.wav",folhico(t,ru(t,np.random.default_rng(743),31),76),.20)
    espaciais = {
        "asa_perto":(540,.48,19,.05), "patas_perto":(270,.53,8,.30),
        "sopro_perto":(159,.72,3,.70), "zurro_perto":(245,.60,63,.04),
        "casco_perto":(82,.63,6,.35), "rasgo":(190,.31,12,.54),
        "fio_disparo":(609,.38,3,.11), "ferrao":(532,.32,24,.15),
        "casco_avanco":(76,.52,8,.61), "pressagio":(161,.58,4,.33),
        "morte":(93,1.12,2,.13), "rebote":(285,.21,5,.15),
        "bloqueio":(895,.23,2,.12), "abatido":(90,.42,6,.34),
    }
    for nome,(freq,d,asas,ar) in espaciais.items():
        t=eixo(d)
        textura=sopro(t,rng,17)
        tom=np.sin(TAU*(freq*t - freq*.23*t*t/d))
        modulacao=(.5+.5*np.cos(TAU*asas*t))**3
        if nome.endswith("_perto"):
            # Cada espécie conserva sua cadência, mas as pistas de presença
            # usam fricção de asa/patas; a ação perigosa tem seu próprio ataque.
            sinal=(textura*.70 + tom*(.15 if nome=="zurro_perto" else .065))*modulacao
            pico=.36
        else:
            sinal=(tom*.37+textura*ar)*(.18+.82*modulacao)
            pico=.60
        sinal *= np.minimum(1,t*45)*np.exp(-1.9*t/d)*np.minimum(1,(d-t)*22)
        salvar(out/(nome+".wav"),sinal,pico)
    for nome,d in (("camada_combate",5.),("camada_pulso",1.22),("camada_vida",9.)):
        t=eixo(d)
        if nome=="camada_combate":
            # Um rumor de ar sob tensão deixa espaço para ouvir o aviso localizado.
            som=sopro(t,rng,230)*(.07+.10*np.sin(np.pi*t/d)**4)
        elif nome=="camada_pulso":
            som=np.zeros_like(t)
            for pos,g in ((.11,1.),(.32,.55)):
                t2=eixo(.18)
                colocar(som,np.sin(TAU*(79*t2-70*t2*t2))*np.sin(np.pi*t2/.18)**2,pos,g)
        else:
            som=np.zeros_like(t)
            for pos,dur in ((.72,.40),(4.10,.65),(7.36,.27)):
                t2=eixo(dur)
                folhas=sopro(t2,rng,44)*np.sin(np.pi*t2/dur)**2
                colocar(som,folhas,pos,.17)
        salvar(out/(nome+".wav"),som,.34)


if __name__ == "__main__":
    import sys
    out = Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1]/"assets"/"sons"
    out.mkdir(parents=True,exist_ok=True)
    for nome, params in CENAS.items():
        ambiente(nome, params, out)
    sons(out)
