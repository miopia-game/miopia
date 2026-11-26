"""Clareiras conquistáveis e coordenação das patrulhas da colônia."""
from dataclasses import dataclass
import math
from .fases import Objeto,CHAO


@dataclass(frozen=True)
class Clareira:
    id:str
    regiao:str
    area:tuple
    tocha:tuple
    membros:tuple


CLAREIRAS=(
    Clareira('vigilia','0:0',(1350,60,950,520),(1810,CHAO),(1548,1595,1660)),
    Clareira('bercario','0:0',(1470,1050,640,330),(1760,1282),(1800,)),
    Clareira('jardim','corte',(3460,205,1110,650),(4520,790),(3500,3710,4240,4350)),
)


def povoar(j):
    if j.modo!='historia' or j.etapa!=0 or hasattr(j,'sala_id') or getattr(j,'ensaio_armas',False):return
    if 'inimigo_1595' not in j.flags:
        from .taticas import Habitante
        j.inimigos.append(Habitante('vespa',1595,360,j.dificuldade))
    for e in j.inimigos:
        if e.origem[0] in CLAREIRAS[0].membros:
            e.max_vida+=6;e.vida=e.max_vida


def derrotados(j,c):
    if c.id=='bercario':return 'caruncho_vencido' in j.historico.get((0,0),set())
    mem=j.cartografia if c.regiao=='corte' else j.historico.get((0,0),set())
    prefixo='vigia_' if c.regiao=='corte' else 'inimigo_'
    return all(prefixo+str(x) in mem for x in c.membros)


def objetos(j):
    from .luzes_mundo import regiao
    if j.modo!='historia' or hasattr(j,'sala_id') or getattr(j,'ensaio_armas',False):return ()
    out=[]
    for c in CLAREIRAS:
        if c.regiao!=regiao(j):continue
        x,y=c.tocha
        if c.id not in j.tochas and derrotados(j,c) and c.id not in j.nucleos:
            out.append(Objeto('nucleo_'+c.id,'lanterna',x-60,y,'Recolher núcleo e globo da clareira'))
        out.append(Objeto('tocha_'+c.id,'lanterna',x,y,'Acender a tocha da clareira' if c.id not in j.tochas else 'Ouvir os vaga-lumes da clareira'))
    return tuple(out)


def interagir(j,o):
    ident=o.id.split('_',1)[1];c=next(c for c in CLAREIRAS if c.id==ident)
    if o.id.startswith('nucleo_'):
        if not derrotados(j,c) or ident in j.nucleos:return
        j.nucleos.add(ident);j.bolsa.receber('semente_luz',1);j.bolsa.receber('globo',1)
        j.eventos.append('coleta')
        j.notificar('Núcleo e globo recolhidos. E na tocha ilumina a clareira; Q/F coloca o globo onde preferir.',9.)
    elif ident in j.tochas:j.notificar('Esta clareira permanece acesa, mesmo após morrer ou carregar. A luz do K não cega criaturas aqui.',7.)
    elif ident not in j.nucleos or not j.bolsa.estoque['semente_luz']:
        j.notificar('Afaste os guardas desta clareira e recolha o núcleo. Ele alimenta a tocha dos vaga-lumes.',7.)
    else:
        j.bolsa.estoque['semente_luz']-=1;j.bolsa.revisao+=1;j.tochas.add(ident)
        j.eventos.append('resgate');j.notificar('Clareira acesa: terreno nítido e luz permanente nesta região.',7.)


def coordenar(j):
    """Atualiza os papéis e a iluminação usada para liberar ataques."""
    from .luzes_mundo import pontos_claros, regiao
    atual = regiao(j)
    alvo = j.lume.rect.center
    for e in j.inimigos:
        e.grupo=None;e.papel='';e.colegas=[]
    grupos = [(c.id, c.membros) for c in CLAREIRAS if c.regiao == atual and c.id != "bercario"]
    from . import galeria_taquaral
    if galeria_taquaral.ativo(j):
        grupos.append(("galeria_sementes", galeria_taquaral.MEMBROS))
    for ident, membros in grupos:
        vivos=[e for e in j.inimigos if e.ativo and e.origem[0] in membros]
        luz = (False,) * len(vivos)
        alvo_claro = False
        if len(vivos) > 1 and any(math.dist(alvo, e.rect.center) < 335 for e in vivos):
            alvo_claro, *luz = pontos_claros(j, (alvo, *(e.rect.center for e in vivos)))
        for n,e in enumerate(vivos):
            e.grupo=ident;e.papel=('pressao','flanco','cobertura')[n%3]
            e.colegas=vivos
            e.ataque_iluminado = alvo_claro and luz[n]
            if ident == "galeria_sementes":
                e.papel = "cobertura" if e.tipo == "vespa" else "flanco"


def desenhar(s,o,j,cx):
    import pygame
    from .ilustracao import brilho,sprite
    x,y=o.x-cx,o.y;ident=o.id.split('_',1)[1]
    if o.id.startswith('nucleo_'):
        pygame.draw.polygon(s,(146,194,148),[(x,y-34),(x+11,y-17),(x,y-4),(x-11,y-17)])
        brilho(s,(x,y-17),20)
    elif ident in j.tochas:
        sprite(s,"obj_tocha_acesa",x,y,46,80)
        brilho(s,(x,y-49),38)
    else:
        pygame.draw.lines(s,(103,117,68),False,[(x-12,y),(x-4,y-24),(x,y-72),(x+10,y-58)],6)
        pygame.draw.ellipse(s,(170,162,100),(x-15,y-81,30,18),2)
