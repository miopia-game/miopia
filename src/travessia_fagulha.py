"""Fagulha pousada, leitura do terreno e reação a uma luz lançada."""
from dataclasses import dataclass
from math import dist, pi, sin

from .combate import Vetor, segmento_bloqueado
from .taticas import Habitante

CHEGADA = (1038, 237)
CORTE_PRATICADO = "praticado_corte_morcego"
ORIGEM_MORCEGO = 875  # Identificador já usado em saves da campanha.
CUSTO = 26.
VOO = .38
DURACAO = 7.
RAIO = 160
FORA_DA_MARCA = "Vire até a marca brilhar antes de lançar."


def na_borda(j):
    x, y = j.lume.rect.midbottom
    return (j.etapa == 0 and not j.em_vertical and not getattr(j, "campo_testes", False)
            and not hasattr(j, "sala_id") and 786 <= x <= 810 and abs(y-248) <= 8)


@dataclass(frozen=True)
class Fagulha:
    inicio: float
    origem: tuple[float, float]
    destino: tuple[float, float]

    def progresso(self, agora):
        return min(1., max(0., (agora-self.inicio)/VOO))

    def restante(self, agora):
        return min(1., max(0., (self.inicio+VOO+DURACAO-agora)/DURACAO))

    def posicao(self, agora):
        t = self.progresso(agora)
        x, y = self.origem
        return x+(self.destino[0]-x)*t, y+(self.destino[1]-y)*t-37*sin(pi*t)

    def raio(self, agora):
        if self.progresso(agora) < 1:
            return 36
        return round(RAIO*min(1., self.restante(agora)*5))


def disponivel(j):
    arena = j.boss and not j.boss.vencido
    return not hasattr(j,"sala_id") and (arena or (
        not getattr(j,"campo_testes",False) and not getattr(j,"ensaio_armas",False)))


def _destino(j):
    from .desvios_fagulha import destino
    if na_borda(j) and j.lume.face > 0:
        return CHEGADA
    marca = destino(j)
    if marca:
        return marca
    x, y = j.lume.rect.midbottom
    face = j.lume.face
    if j.boss:
        marcas = [p for p in j.boss.marcas_fagulha()
                  if 65 <= (p[0]-x)*face <= 325 and abs(p[1]-y) <= 132]
        if marcas:
            return min(marcas,key=lambda p:abs(p[0]-(x+face*240)))
    # Procura longe primeiro. Um salto sobre o vazio pode encontrar um galho mais perto.
    apoios = [t.rect for t in j.solidos if t.atravessavel or t.tipo in ("chao","teto")]
    for alcance in (240,324,178,112,48):
        xx = x+face*alcance
        candidatos = [r for r in apoios if r.left+3 <= xx <= r.right-3 and -114 <= r.top-y <= 170]
        if candidatos:
            r = min(candidatos,key=lambda r:abs(r.top-y))
            return round(xx),r.top-4
    return None


def _preparar(j):
    if j.fagulha_ativa:
        return None, "Ainda há uma fagulha acesa."
    if j.lume.energia < CUSTO:
        return None, "A fagulha precisa de 26 de brilho."
    destino = _destino(j)
    if destino is None:
        return None, "Vire para um chão ou galho onde a fagulha possa pousar."
    fagulha = Fagulha(j.tempo, tuple(j.lume.rect.center), destino)
    paredes = [t for t in j.solidos if not t.atravessavel]
    pontos = [fagulha.posicao(j.tempo+i*VOO/12) for i in range(13)]
    if any(segmento_bloqueado(a,b,paredes) for a,b in zip(pontos,pontos[1:])):
        return None, "A parede bloqueia o lançamento."
    return fagulha, ""


def prever_marca(j):
    e = j.boss
    borda_vespera = not e and na_borda(j)
    if (not borda_vespera and (not e or not e.marcas_fagulha())) or not disponivel(j):
        return None
    fagulha, _ = _preparar(j)
    if borda_vespera:
        return CHEGADA if fagulha and fagulha.destino == CHEGADA else None
    return e.marca_fagulha(fagulha)


def lancar(j):
    if not disponivel(j):
        return
    fagulha, aviso = _preparar(j)
    if not fagulha:
        j.notificar(aviso,2. if j.fagulha_ativa else 3.)
        return
    j.lume.energia -= CUSTO
    j.fagulha = fagulha
    j.eventos.append("fagulha")


def avisar_pouso(j, tempo_anterior):
    f = j.fagulha_ativa
    if not f or not tempo_anterior < f.inicio+VOO <= j.tempo:
        return
    if j.boss and j.boss.marcas_fagulha() and j.boss.marca_fagulha(f) is None:
        j.notificar(FORA_DA_MARCA,3.6)
    elif na_borda(j) and f.destino != CHEGADA:
        j.notificar(FORA_DA_MARCA,3.6)


REACOES = {"morcego":"isca_fagulha","vespa":"isca_fagulha",
           "aranha":"isca_fagulha","sombra":"fuga_fagulha"}


def reagir(j,e,dt,terrenos):
    """Uma só reação por lançamento e apenas quando nenhum bote foi iniciado."""
    if type(e) not in (Habitante,MorcegoDoGalho) or e.guarda or e.tipo not in REACOES:
        return False
    f = j.fagulha_ativa
    if e.estado in ("isca_fagulha","fuga_fagulha"):
        e.t -= dt
        if e.t <= 0 or f is not e.fagulha_observada:
            e.estado,e.t = "patrulha",.24
            return False
        e.flash = max(0.,e.flash-dt)
        e.lentidao = max(0.,e.lentidao-dt)
        e.resistencia_leve = max(0.,e.resistencia_leve-dt)
        e.seguir(e.destino_fagulha,74 if e.lentidao else 118,dt,terrenos)
        return True
    if (not f or f.progresso(j.tempo)<1 or e.estado!="patrulha"
            or f is getattr(e,"fagulha_observada",None)):
        return False
    ex, ey = e.rect.center
    x, y = f.destino
    limite = f.raio(j.tempo)+66
    if dist((ex,ey),(x,y))>limite or segmento_bloqueado((ex,ey),(x,y),terrenos):
        return False
    if e.tipo in ("aranha","sombra") and abs(y-ey)>55:
        return False
    lado = 1 if x>=ex else -1
    estado = REACOES[e.tipo]
    if estado == "fuga_fagulha":
        lado *= -1
        x,y = ex+90*lado,ey
    else:
        x -= 24*lado
        y = ey if e.tipo=="aranha" else y-20
    e.estado,e.t = estado,1.24
    e.frente = lado
    e.fagulha_observada = f
    e.destino_fagulha = Vetor(x,y)
    j.sons_espaciais.append((e.ficha.som,e.rect.centerx))
    return True


def desenhar(s,j,cx):
    from .ilustracao import brilho, claroes_suaves, sprite
    f = j.fagulha_ativa
    if not f:
        return
    wx,wy = f.posicao(j.tempo)
    x,y = round(wx-cx),round(wy)
    if not claroes_suaves():
        brilho(s,(x,y),20+round(15*f.restante(j.tempo)))
    sprite(s,"hud_fagulha",x,y+10,20,20)


@dataclass(frozen=True)
class ImpactoDoCorte:
    inicio: float
    ponto: tuple[float, float]
    lado: int
    abate: bool


class MorcegoDoGalho(Habitante):
    def __init__(self, dificuldade):
        super().__init__("morcego", 1056, 293, dificuldade)

    def repor(self):
        super().repor()
        self.impacto_corte = None
        self.estado = "poleiro"
        self.t = 0.

    def update(self,dt,lume,raio,restaurado,terrenos):
        if self.estado == "poleiro":
            if abs(lume.rect.centerx-self.rect.centerx) > 124 or abs(lume.rect.centery-self.rect.centery) > 105:
                return [], False
            self.frente = 1 if lume.rect.centerx > self.rect.centerx else -1
            self.estado, self.t = "patrulha", .36
            return [("asa_perto", self.rect.centerx)], False
        return super().update(dt,lume,raio,restaurado,terrenos)
