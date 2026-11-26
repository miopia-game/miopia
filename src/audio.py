"""Mistura local de trilha, combate, batimento, vida da mata e ações em primeiro plano."""
from pathlib import Path
import math
import pygame

PASTA=Path(__file__).resolve().parents[1]/"assets"/"sons"
# Os sinais de perigo, dano e mecanismo têm canais distintos para não se encobrirem.
ALIASES={"etapa":"abertura","selo":"seiva","chefe_exposto":"vulneravel","chefe_acerto":"acerto",
         "chefe_vencido":"vencer","chefe_resolvido":"vencer","investida":"deslize","parede":"impacto","brasa":"seiva",
         "vulneravel":"vulneravel","exposto":"vulneravel","madeira":"impacto","barril":"valvula",
         'sacrificio':'dano', 'rebote_casulo':'corda', 'fagulha':'seiva', 'brecha_fagulha':'vulneravel', 'teia_queimada':'seiva', 'casco_presaseiva':'seiva'}
ALERTAS={"aviso":5,"dano":6,"acerto":7,"sino":8,"impacto":9,"vulneravel":8,
         "raiz":9,"porta":8,"seiva":8,'casco_muda':5,'coruja_muda':5}
PRESENCA = {"asa_perto", "patas_perto", "sopro_perto", "zurro_perto", "casco_perto", "silvo_perto"}
INTERVALO_BATIMENTO = 6.


def panoramica(delta, alcance=550):
    """Distância lateral de uma fonte relativa a Lume, em pixels do mundo."""
    distancia = abs(delta)
    if distancia >= alcance:
        return 0., 0.
    desvio = max(-1., min(1., delta/215))
    ganho = 1 - .82 * distancia / alcance
    return (ganho * math.sqrt((1 - .83*desvio) / 2),
            ganho * math.sqrt((1 + .83*desvio) / 2))


class Audio:
    def __init__(self,pasta=PASTA):
        self.disponivel=False
        self.mudo=False
        self.volume_musica=.65
        self.volume_efeitos=.85
        self.atual=None
        self.ativos=(0.,0.,0.)
        self.niveis=[0.,0.,0.]
        self.silencio=0.
        self.fundo=1.
        self.proximo_batimento=0.
        self.passo_alterno=False
        self.grave=0.
        self.pasta=Path(pasta)
        self.fx={}
        self.camadas=[]
        self.trilhas={}
        try:
            if not pygame.mixer.get_init(): pygame.mixer.init(44100,-16,2,512)
            pygame.mixer.set_num_channels(28)
            pygame.mixer.set_reserved(16)
            for p in self.pasta.glob("*.wav"):
                nome=p.stem
                if nome.startswith("trilha_"): self.trilhas[nome[7:]]=p
                else: self.fx[nome]=pygame.mixer.Sound(str(p))
            # A trilha é decodificada durante a reprodução. Ogg prevalece
            # sobre o WAV de mesmo nome em uma instalação atualizada.
            self.trilhas.update((p.stem[7:], p) for p in self.pasta.glob("trilha_*.ogg"))
            for n,nome in enumerate(("camada_combate","camada_pulso","camada_vida")):
                canal=pygame.mixer.Channel(n)
                canal.set_volume(0.)
                if nome=="camada_pulso":
                    canal.stop()
                elif nome in self.fx:
                    canal.play(self.fx[nome],loops=-1)
                self.camadas.append(canal)
            self.disponivel=True
        except (pygame.error,OSError):
            return

    def tocar_musica(self,nome):
        if nome==self.atual or not self.disponivel: return
        caminho=self.trilhas.get(nome)
        if not caminho: return
        try:
            pygame.mixer.music.load(str(caminho))
            pygame.mixer.music.play(-1,fade_ms=560)
            self.atual=nome
            self.aplicar_volumes()
        except (pygame.error,OSError):
            pass

    def tocar(self,nome,*,aviso_de_chefe=False):
        if not self.disponivel or self.mudo: return
        nome=ALIASES.get(nome,nome)
        som=self.fx.get(nome)
        if nome=="passo":
            if self.passo_alterno:
                som=self.fx.get("passo_folha",som)
            self.passo_alterno=not self.passo_alterno
        if not som: return
        n=ALERTAS['aviso'] if aviso_de_chefe else ALERTAS.get(nome)
        canal=pygame.mixer.Channel(n) if n is not None else next((pygame.mixer.Channel(i) for i in range(16,28) if not pygame.mixer.Channel(i).get_busy()),None)
        if not canal: return
        volume=self.volume_efeitos*(.32 if nome=="passo" else (.50 if nome in ("clique","navegar") else .82))
        canal.set_volume(volume)
        canal.play(som)
        if aviso_de_chefe or nome in ("aviso","sino","dano"): self.silencio=.47

    def tocar_local(self, nome, fonte_x, ouvinte_x):
        if not self.disponivel or self.mudo:
            return False
        som = self.fx.get(nome)
        if som is None:
            return False
        esq, dire = panoramica(fonte_x-ouvinte_x)
        if esq + dire == 0:
            return False
        # O ruído de aproximação jamais ocupa uma voz reservada ao ataque.
        presenca = nome in PRESENCA
        canais = [pygame.mixer.Channel(n) for n in (range(10,12) if presenca else range(12,16))]
        livre = next((c for c in canais if not c.get_busy()), None)
        if livre is None:
            return False
        ganho = self.volume_efeitos * (.72 if presenca else 1.)
        livre.set_volume(esq*ganho, dire*ganho)
        livre.play(som)
        if not presenca:
            self.silencio = .38
        return True

    def ambiente(self,*,combate,energia,raizes,suspenso=False):
        self.grave=max(0.,min(1.,(31.-energia)/21.))
        self.ativos=(.28 if combate else 0.,self.grave*.42,
                     0. if suspenso else min(.32,.08*raizes))

    def aplicar_volumes(self):
        if not self.disponivel: return
        musica=0 if self.mudo else self.volume_musica
        fx=0 if self.mudo else self.volume_efeitos
        corte=(1-.25*self.grave)*self.fundo
        pygame.mixer.music.set_volume(musica*corte*.62)
        for i,canal in enumerate(self.camadas):
            canal.set_volume(self.niveis[i]*(fx if i==1 else musica*self.fundo))
        if self.mudo:
            for n in range(5,pygame.mixer.get_num_channels()): pygame.mixer.Channel(n).stop()

    def atualizar(self,dt):
        if not self.disponivel: return
        self.silencio=max(0.,self.silencio-dt)
        alvo = .65 if self.silencio else 1.
        tempo = .07 if self.silencio else .48
        self.fundo += (alvo-self.fundo)*(1-math.exp(-dt/tempo))
        for i,destino in enumerate(self.ativos):
            self.niveis[i]+=(destino-self.niveis[i])*min(1,dt*5)
        self.aplicar_volumes()
        self.proximo_batimento=max(0.,self.proximo_batimento-dt)
        if self.grave >= .4 and not self.mudo and self.proximo_batimento == 0:
            batimento=self.fx.get("camada_pulso")
            if batimento is not None:
                self.camadas[1].play(batimento)
            self.proximo_batimento=INTERVALO_BATIMENTO
