"""Marcas que a luz pousada revela e os desvios opcionais por cima das raízes."""
from dataclasses import dataclass
from math import dist

from . import pygame_hd as pygame

from .fases import Objeto, Terreno


@dataclass(frozen=True)
class Desvio:
    chave: str
    nome: str
    partida: tuple[int, int]
    marca: tuple[int, int]
    requisito: str
    apoios: tuple[Terreno, ...]
    reserva: Objeto
    item: str


def _apoios(*retangulos):
    return tuple(Terreno(pygame.Rect(x,y,w,12),"apoio_fagulha") for x,y,w in retangulos)


DESVIOS = {
    1: Desvio("desvio_seda_fagulha", "Passarela da seda", (749,245), (1008,315), "dreno",
              _apoios((1045,303,125),(1190,265,116)),
              Objeto("reserva_seda_fagulha","reserva_fagulha",1261,265,"Recolher um casulo"), "casulo"),
    3: Desvio("desvio_costelas_fagulha", "Costelas da Figueira", (1500,372), (1663,337), "contrapeso",
              _apoios((1631,306,89),(1740,260,135)),
              Objeto("reserva_costelas_fagulha","reserva_fagulha",1820,260,"Recolher um pavio"), "pavio"),
}


def local(j):
    desvio = DESVIOS.get(j.etapa)
    if (desvio and not j.em_vertical and not getattr(j,"campo_testes",False)
            and desvio.requisito in j.flags):
        return desvio
    return None


def na_partida(j, desvio):
    x, y = j.lume.rect.midbottom
    px, py = desvio.partida
    return abs(x-px) <= 57 and abs(y-py) <= 24


def destino(j):
    desvio = local(j)
    if desvio and desvio.chave not in j.flags and j.lume.face > 0 and na_partida(j,desvio):
        return desvio.marca
    return None


def pista(j):
    desvio = local(j)
    if desvio and desvio.chave not in j.flags and not j.fagulha_ativa and na_partida(j,desvio):
        return "Vire à direita e use G. Uma marca de resina brilha além do galho."
    return ""


def revelar(j):
    desvio = local(j)
    f = j.fagulha_ativa
    if (not desvio or desvio.chave in j.flags or not f or f.progresso(j.tempo) < 1
            or dist(f.destino,desvio.marca)>50):
        return
    j.flags.add(desvio.chave)
    j.memorizar(desvio.nome, "A fagulha revelou apoios por cima das raízes. O desvio leva a uma reserva na ponta do último galho.")
    j.notificar(f"{desvio.nome} revelada pela fagulha." if j.etapa == 1
                else f"{desvio.nome} reveladas pela fagulha.", 5.)
    j.eventos.append("abertura")


def terrenos(j):
    desvio = local(j)
    return desvio.apoios if desvio and desvio.chave in j.flags else ()


def objetos(j):
    desvio = local(j)
    if desvio and desvio.chave in j.flags and desvio.reserva.id not in j.flags:
        return (desvio.reserva,)
    return ()


def recolher(j, o):
    desvio = local(j)
    if not desvio or o.id != desvio.reserva.id or o.id in j.flags:
        return
    from .narrativa import POR_ID
    j.flags.add(o.id)
    j.bolsa.receber(desvio.item,1)
    j.notificar(f"{POR_ID[desvio.item].nome} guardado na bolsa.", 4.)
    j.eventos.append("coleta")


def marca(s,j,cx):
    from .ilustracao import AMBAR, losango
    desvio = local(j)
    if not desvio or desvio.chave in j.flags:
        return
    x, y = round(desvio.marca[0]-cx), desvio.marca[1]
    if -20 < x < 980:
        losango(s,x,y,4,AMBAR,False)
        pygame.draw.aaline(s, (123,97,62), (x-7,y+4), (x+7,y+4))
