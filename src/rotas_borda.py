"""Travessias que a água permite reparar e trabalho nas margens."""
from dataclasses import dataclass
import math

from . import pygame_hd as pygame

from .fases import CHAO, Objeto, Terreno

VESPERA = (1322, CHAO)
PASSARELAS = (
    pygame.Rect(1375, CHAO, 110, 16),
    pygame.Rect(2135, 426, 345, 15),
)
PREFIXO = "borda_"
TIPO_CORDA = "corda_borda"


@dataclass(frozen=True)
class Posto:
    etapa: int
    posicao: tuple[int, int]
    corda: Objeto
    destino: int
    titulo: str
    pista: str
    fala: str
    registro: str


POSTOS = {
    "tila": Posto(0, (2250, CHAO),
                  Objeto("corda_tila", TIPO_CORDA, 2180, CHAO, "Descer pelo cipó de Tila"), 1282,
                  "A amarra de Tila",
                  "Com a raiz acesa, procure Tila na forquilha junto ao cipó do poço.",
                  "A seda já secou. Soltei a trava e passei uma laçada pelo cipó. Agora dá para descer daqui até o poço. "
                  "Se ouvir o Caruncho em sonho, já sei por onde voltar.",
                  "Tila estendeu o cipó do poço para descer pela grade da forquilha. A amarra fica."),
    "bento": Posto(1, (2708, CHAO),
                   Objeto("corda_bento", TIPO_CORDA, 3050, 1102, "Subir pela corda de Bento"), CHAO,
                   "A corda de Bento",
                   "Com a raiz acesa, procure Bento entre a primeira grade das raízes e o vão.",
                   "Deixei dois riscos na régua para a água de hoje. A corda ficou seca. Prendi uma ponta na grade "
                   "da direita, acima do lugar onde eu esperei. Quem estiver no fundo pode subir por ela.",
                   "Bento prendeu uma corda sob a grade leste do Córrego, da base dos galhos até a superfície."),
}


def posto(j, pessoa):
    trabalho = POSTOS.get(pessoa)
    if trabalho is not None and j.sobreviventes.get(pessoa, {}).get("oficio") == "trilha":
        if "raiz" in j.historico.get((j.volta, trabalho.etapa), ()):
            return trabalho
    return None


def conversar(j, pessoa):
    trabalho = POSTOS[pessoa]
    if trabalho.corda.id not in j.flags:
        j.flags.add(trabalho.corda.id)
        if pessoa == "tila":
            j.flags.add("cipo_estendido")
        j.memorizar(trabalho.titulo, trabalho.registro)
        j.eventos.extend(("corda", "porta"))
    return trabalho.fala


def objetos(j):
    return tuple(p.corda for p in POSTOS.values() if j.etapa == p.etapa and p.corda.id in j.flags)


def usar_corda(j, identificador):
    trabalho = next(p for p in POSTOS.values() if p.corda.id == identificador)
    l = j.lume
    l.em_corda = True
    l.chao = False
    l.corda_destino = trabalho.destino
    l.rect.centerx = trabalho.corda.x
    l.vx = l.vy = 0.
    j.eventos.append("corda")


def terrenos(base, etapa, flags):
    if etapa not in (0, 1) or "raiz" not in flags:
        return base
    if etapa == 0:
        return (*base, Terreno(PASSARELAS[0], "ponte"))
    sem_vedacao = tuple(t for t in base if (t.tipo, t.rect.x) != ("vedacao", 2150))
    return (*sem_vedacao, Terreno(PASSARELAS[1], "grade"))


def desenhar(s, j, cx):
    if j.etapa not in (0, 1) or "raiz" not in j.flags:
        return
    vao = PASSARELAS[j.etapa]
    r = vao.move(-round(cx), 0)
    if not r.inflate(36, 110).colliderect(s.get_clip()):
        return
    casca, seda = (101, 79, 49), (174, 151, 95)
    for x in (r.left+6, r.right-6):
        pygame.draw.line(s,casca,(x,r.top-32),(x,r.top+16),6)
        for y in (r.top-18,r.top-13):
            pygame.draw.line(s,seda,(x-5,y),(x+5,y),2)
    for x in range(r.left+12,r.right-12,22):
        pygame.draw.line(s,casca,(x,r.top+2),(x,r.top+13),4)
    rede = [(x, r.top-16 + math.sin((x-r.left)/r.w*math.pi)*9)
            for x in range(r.left+6,r.right-5,7)]
    pygame.draw.lines(s,seda,False,rede,2)
    if j.etapa == 1:
        for n in range(6):
            x = r.left+25+round((j.tempo*52+n*61) % (r.w-50))
            y = r.bottom+12+n%3*4
            pygame.draw.line(s,(104,177,161),(x-8,y),(x,y+1),1)


def desenhar_corda(s, o, cx):
    trabalho = next(p for p in POSTOS.values() if p.corda.id == o.id)
    x = round(o.x-cx)
    if not -30 <= x <= 990:
        return
    topo, fim = sorted((o.y, trabalho.destino))
    if o.id == "corda_bento":
        corda = [(x+math.sin(y*.031)*1.5,y) for y in range(topo-12,fim+1,6)]
        pygame.draw.lines(s,(65,77,57),False,corda,6)
        pygame.draw.lines(s,(180,172,110),False,corda,2)
    for y, direcao in ((topo-13, 1), (fim-20, -1)):
        pygame.draw.ellipse(s,(164,194,136),(x-9,y-10,18,16),2)
        pygame.draw.lines(s,(222,197,125),False,[(x-5,y-direcao*4),(x,y+direcao*2),(x+5,y-direcao*4)],2)
