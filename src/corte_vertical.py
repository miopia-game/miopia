"""Cartografia e regras do Corte da Figueira, uma região contínua entre dois biomas."""
from __future__ import annotations

import math
from functools import lru_cache

import pygame

from . import arquivo_casca, fio_corte
from .taticas import Habitante as Inimigo
from .fases import CHAO, Objeto, Terreno

LARGURA = 4608
ALTURA = 1908
BOCA_LESTE = 1416
NIVEIS = (
    ("copa", "Copa do Observatório", 0, 702),
    ("galeria", "Galeria dos Casulos", 702, 1150),
    ("poco", "Poço da Seiva", 1150, 1630),
    ("cisterna", "Cisterna das Duas Margens", 1630, ALTURA),
)
ARQUIVO = arquivo_casca.AREA
RAIZ_X = 138
PISO_ARQUIVO = arquivo_casca.PISO
PISO_POCO = 1492
RAIZ_DUAS_BOCAS = 'raiz_duas_bocas'
FERROLHO = pygame.Rect(RAIZ_X-11, PISO_POCO-34, 22, 24)
CASULO_X = 947
NICHO_POCO = 1270
CASULO = pygame.Rect(CASULO_X-20, PISO_POCO-29, 40, 29)
PAVIO_CASULO = "pavio_casulo_poco"
COMPORTA = pygame.Rect(1394, 1670, 44, 158)
TEMPO_COMPORTA = .95
# Posições em que o pé toca efetivamente uma superfície. Os saves só guardam o ID.
MARCOS = {
    "bosque": (183, 988),
    "copa": (524, 316),
    "poco": (286, 1492),
    "cisterna": (455, 1828),
    "corrego": (1225, 1828),
    "estaleiro": (1905, 790),
    'jardim':(2510,790),
}
BOCAS = {"bosque": (0, 630), "copa": (0, 1320), "corrego": (1, 660), "estaleiro": (1, 1944)}
SUP = {
    "bosque": "Entrar no Corte da Figueira",
    "copa": "Voltar ao Observatório da Copa",
    "corrego": "Descer à cisterna sob o córrego",
    "estaleiro": "Entrar no Estaleiro das Folhas",
}


def setor(y,x=None):
    if x is not None and x>=2432:
        from .jardim import setor as setor_jardim
        return setor_jardim(y,x)
    if x is not None and x >= BOCA_LESTE:
        return ("estaleiro", "Estaleiro das Folhas") if y < 1160 else ("viveiro", "Viveiro Afundado")
    if x is not None and ARQUIVO.collidepoint(x,y):
        return "arquivo", "Arquivo da Casca"
    for ident, nome, topo, fundo in NIVEIS:
        if y < fundo:
            return ident, nome
    return NIVEIS[-1][:2]


def entradas(j):
    if j.modo != "historia":
        return ()
    return tuple(Objeto("corte_"+nome, "fenda", x, CHAO, SUP[nome])
                 for nome, (etapa, x) in BOCAS.items()
                 if etapa == j.etapa and (nome != "copa" or "atalho_copa" in j.cartografia)
                 and (nome != "estaleiro" or "ponte" in j.flags))


@lru_cache(maxsize=16)
def terrenos(comporta_aberta=False,jardim_flags=frozenset(),raiz_aberta=False,passarela_fio=False):
    partes = []
    def t(x,y,w,h,material):
        partes.append(Terreno(pygame.Rect(x,y,w,h), material))

    # Copa aberta em dois ombros separados por uma ponte de galhos.
    t(160,316,482,37,"plataforma")
    t(650,330,207,17,"ponte")
    # Janelas gradeadas alinham o ramal oriental aos patamares logo abaixo.
    # A terra de cada lado mantém espessura e colisão nas duas direções.
    t(851,316,217,40,"chao")
    t(1068,316,150,16,"grade")
    t(1218,316,150,40,"chao")
    # O caminho ocidental sobe em ziguezague. A queda oriental encontra outros apoios.
    for x,y,w in ((437,904,177),(360,820,160),(428,736,177),(493,652,174),
                  (421,568,168),(357,484,169),(427,400,172),
                  (933,907,182),(996,823,179),(951,739,133),(1010,655,168),
                  (976,571,154),(1062,487,168),(1023,403,192)):
        t(x,y,w,19,"plataforma")
    t(48,988,539,75,"chao")
    t(587,988,233,16,"grade")
    t(820,988,188,44,"chao")
    t(1008,988,160,16,"grade")
    t(1168,988,196,44,"chao")
    # Câmara escavada no oeste: teto, banco do arquivo e piso recortado
    # deixam abertos o corredor à direita e uma saída inferior ao poço.
    t(62,1038,300,36,"chao")
    t(51,1040,25,194,"parede")
    if raiz_aberta:
        t(70,PISO_ARQUIVO,42,38,"chao")
        t(112,PISO_ARQUIVO,52,16,"grade")
        t(164,PISO_ARQUIVO,213,38,"chao")
    else:
        t(70,PISO_ARQUIVO,307,38,"chao")
    t(369,1156,205,17,"plataforma")
    t(188,1330,146,17,"plataforma")
    t(247,1411,123,17,"plataforma")
    # A estaca de funil separa o poço central da galeria da contrapesagem.
    t(845,1062,67,247,"parede")
    for x,y,w in ((607,1072,188),(556,1156,181),(632,1240,175),(568,1324,183),
                  (638,1408,192),(992,1082,212),(1050,1166,178),(984,1250,172),
                  (1048,1334,190),(979,1418,206)):
        t(x,y,w,18,"plataforma")
    t(124,1492,324,77,"chao")
    t(448,1492,246,16,"grade")
    t(694,1492,362,36,"chao")
    t(922,NICHO_POCO,50,17,"plataforma")
    t(1056,1492,162,16,"grade")
    t(1218,1492,111,36,"chao")
    for x,y,w in ((544,1576,178),(617,1660,181),(556,1744,192),
                  (1067,1576,148),(1010,1660,164),(1066,1744,184)):
        t(x,y,w,18,"plataforma")
    t(36,1828,894,80,"chao")
    t(997,1828,397,80,"chao")  # uma fissura curta antes da desembocadura
    if passarela_fio:
        t(*fio_corte.PASSARELA, "ponte")
    # A parede entre as galerias tem duas aberturas em alturas distintas.
    t(1394,0,44,846,"parede")
    t(1394,1010,44,660,"parede")
    if not comporta_aberta:
        t(*COMPORTA,"tranca")
    t(1358,988,265,24,"plataforma")
    # O primeiro beiral pede a segunda batida de asas. A oficina fica sobre a grade.
    t(1600,856,200,20,"plataforma")
    t(1790,790,345,38,"plataforma")
    t(2135,790,216,16,"grade")
    t(2351,790,76,46,"chao")
    for x,y,w in ((2139,886,208),(2046,982,203),(2130,1078,206),
                  (2022,1174,217),(1895,1270,220),(1750,1366,219),
                  (1580,1462,225),(1638,1558,228),(1550,1654,216),
                  (1614,1744,228)):
        t(x,y,w,18,"plataforma")
    t(1388,1828,1038,80,"chao")
    from .jardim import terrenos as terrenos_jardim
    partes.extend(terrenos_jardim(jardim_flags))
    return tuple(partes)


PONTOS = (
    Objeto("volta_bosque", "passagem", 183,988, "Voltar à superfície do Bosque"),
    Objeto("placa_galeria", "registro", 356,988, "Ler a escala talhada por Nira"),
    Objeto("selo_copa", "valvula", 524,316, "Soltar a janela do observatório"),
    Objeto("volta_copa", "passagem", 1220,316, "Sair pelo atalho alto do Bosque"),
    Objeto("marco_poco", "refugio", 286,1492, "Firmar o marco do poço"),
    Objeto("placa_arquivo","registro",173,1173,"Abrir o armário dos casulos"),
    Objeto("placa_poco", "registro", 811,1492, "Ler as marcas antigas de água"),
    Objeto("ralo_cisterna", "valvula", 455,1828, "Examinar o ralo da cisterna"),
    Objeto("volta_corrego", "passagem", 1225,1828, "Sair na margem do Córrego"),
    Objeto("carro_alto", "elevador", 1040,316, "Descer pelo contrapeso"),
    Objeto("carro_baixo", "elevador", 1040,1828, "Subir pelo contrapeso"),
    Objeto("marco_estaleiro", "refugio", 1905,790, "Acender o marco do estaleiro"),
    Objeto("volta_estaleiro", "passagem", 2018,790, "Sair na ponte do Córrego"),
    Objeto("placa_viveiro", "registro", 1982,1270, "Ler o nível dos antigos berços"),
    Objeto("comporta_viveiro", "valvula", 1554,COMPORTA.bottom, "Levantar a comporta da cisterna"),
    Objeto("reliquia_espinho", "reliquia", 283,1173, "Recolher o espinho de acácia"),
    Objeto("reliquia_resina", "reliquia", 2050,1270, "Recolher a resina âmbar"),
)
REGISTROS = {
    "placa_galeria": ("Escala de Nira",
        "Os três riscos no tronco não são datas. Marcam alturas: casulos acima, passagem no meio, ralo no fundo. A mesma árvore foi casa nos três níveis."),
    "selo_copa": ("O vidro do observatório",
        "No vidro ainda se vê a fuligem dos antigos faróis. Nira sabia que a água faltava à copa antes de o raio cair. Ao abrir a janela, Lume vê outro caminho para o Bosque e encontra um pavio intacto."),
    "placa_arquivo": ("A cama dobrada",
        "Atrás da porta Mimo deixou uma folha contada: onze casulos, dez camas. A décima primeira dormiu na mochila dele. Ainda há bálsamo preso à alça."),
    "placa_poco": ("A régua do poço",
        "Quatro linhas antigas cercam a pedra. A marca mais funda está seca há duas estações. O risco escuro continua até a cisterna sob o Córrego."),
    "ralo_cisterna": ("Duas saídas da água",
        "A luz atravessa a argila e revela dois dentes de madeira. Girá-los deixa a água correr para as duas margens. O contrapeso sobe. Fio deixara aqui um casulo de reserva."),
    "placa_viveiro": ("Um risco em cada berço",
        "O risco baixo tem barro ressecado. O alto foi cortado na noite em que Fio levou os casulos para a oficina. "
        "Ela deixou resina neste patamar para proteger a luz dos mensageiros. A roda no fundo do Viveiro, à esquerda, abre a volta à cisterna."),
    "comporta_viveiro": ("A água encontra a cisterna",
        "A lâmina de casca sobe e a água corre para oeste. Lume pode voltar pela cisterna sem refazer o caminho pelos berços."),
}


def objetos(j):
    from .resgates import objetos as pessoas
    from .jardim import objetos as pontos_jardim
    from .encontros import objetos as lanternas
    raiz_aberta=RAIZ_DUAS_BOCAS in j.cartografia
    atalhos=(Objeto('raiz_boca_alta','atalho_raiz',RAIZ_X,PISO_ARQUIVO,
                    'Ler a marca da descida' if raiz_aberta else 'Examinar a raiz rachada'),
             Objeto('raiz_boca_baixa','atalho_raiz',RAIZ_X,PISO_POCO,
                    'Subir pelo cipó' if raiz_aberta else 'Examinar o ferrolho'))
    pontos=tuple(o for o in PONTOS
                 if not (o.tipo=="reliquia" and j.bolsa.estoque.get(o.id.removeprefix("reliquia_"))))
    if PAVIO_CASULO not in j.cartografia:
        pontos += (Objeto(PAVIO_CASULO, "pavio_nicho", CASULO_X+17, NICHO_POCO, "Recolher o pavio de Fio"),)
    return pontos+atalhos+arquivo_casca.objetos(j)+pessoas(j)+pontos_jardim(j)+lanternas(j)+fio_corte.objetos(j)


def camera(j,dt=None):
    l=j.lume.rect
    tx=max(0., min(LARGURA-960., l.centerx - 435.))
    ty=max(0., min(ALTURA-540., l.centery - 285.))
    if dt is None:
        j.camera,j.camera_y=tx,ty
    else:
        f=1.-math.exp(-8.5*dt)
        j.camera+=(tx-j.camera)*f
        j.camera_y+=(ty-j.camera_y)*f


def visitar(j):
    ident,_=setor(j.lume.rect.centery,j.lume.rect.centerx)
    j.cartografia.add("viu_"+ident)


def abertura_comporta(j):
    if "viveiro_aberto" not in j.cartografia:
        return 0.
    if j.comporta_inicio is None:
        return 1.
    u = min(1., max(0., (j.tempo - j.comporta_inicio) / TEMPO_COMPORTA))
    return u*u*(3.-2.*u)


def painel_comporta(j):
    painel = COMPORTA.copy()
    painel.height = round(painel.height*(1.-abertura_comporta(j)))
    return painel


def entrar(j,marco,pela_boca=False):
    j.em_vertical=True
    j.comporta_inicio = None
    j.marco_vertical=marco
    j.vestigios.clear()
    j.fagulha = None
    j.vespera_sinal = None
    j.boss=None
    j.dialogo=None
    alterada = j.aplicar_dificuldade_no_marco(repovoar=False)
    povoar(j)
    j.checkpoint=MARCOS[marco]
    chegada=(1220,316) if pela_boca and marco=="copa" else j.checkpoint
    j.recolocar(chegada)
    visitar(j)
    j.lume.iframes=1.
    camera(j)
    if not alterada:
        j.notificar(setor(j.lume.rect.centery,j.lume.rect.centerx)[1]+" · Tab abre o mapa.",4.)
    j.eventos.append("porta")


def povoar(j):
    j.inimigos=[Inimigo(tipo,x,y,dificuldade=j.dificuldade)
                for tipo,x,y in (("morcego",731,293),("aranha",1146,1492),("sombra",797,1828))
                if f"vigia_{x}" not in j.cartografia]
    from .fauna_jardim import PAR, MoradorDaPonte
    from .jardim import CRIATURAS
    par = {}
    for tipo,x,y in CRIATURAS:
        if f'vigia_{x}' in j.cartografia:continue
        if (tipo,x,y) in PAR:
            e = par[tipo] = MoradorDaPonte(tipo,x,y,j.dificuldade)
        else:
            e = Inimigo(tipo,x,y,dificuldade=j.dificuldade)
        e.dormir_distante = True
        j.inimigos.append(e)
    if "cobra" in par:
        par["cobra"].presa = par.get("vespa")


def ralo_iluminado(j,o):
    return any(math.dist((o.x,o.y-12), (v.x,v.y)) < v.raio(j.tempo) for v in j.vestigios)


def interagir(j,o):
    if o.tipo=='lanterna':
        from .encontros import interagir
        interagir(j,o);return
    if o.tipo=='jardim':
        from .jardim import interagir as usar_jardim
        usar_jardim(j,o)
        return
    if o.tipo=='sobrevivente':
        from .resgates import conversar
        conversar(j,o)
        return
    ident=o.id
    if ident.startswith("corte_"):
        entrar(j, ident.removeprefix("corte_"),pela_boca=True)
        return
    if j.destino_vertical is not None:
        return
    if o.tipo in ("fio_corte", "carretel_fio"):
        fio_corte.interagir(j, o)
        return
    if o.tipo in ('veneziana', 'sinal_arquivo'):
        arquivo_casca.interagir(j, o)
        return
    if ident == PAVIO_CASULO:
        if ident not in j.cartografia:
            j.cartografia.add(ident)
            j.bolsa.receber("pavio", 1)
            j.memorizar("O casulo de mola", "Fio guardava um pavio nesse nicho para ter luz quando voltava do fundo do poço.")
            j.eventos.append("coleta")
            j.notificar("Pavio de pólen guardado. Q escolhe e F acende.", 4.)
        return
    if o.tipo=='atalho_raiz':
        if RAIZ_DUAS_BOCAS not in j.cartografia:
            pista=('Fio deixou a trava por baixo. Desça ao poço pelos galhos a leste.'
                   if ident=='raiz_boca_alta' else 'O ferrolho é de resina. Um corte com J solta a grade e o cipó.')
            j.notificar(pista,6.)
        elif ident=='raiz_boca_alta':
            j.notificar('S + Espaço na grade desce direto ao poço.',6.)
        elif not j.lume.em_corda:
            j.lume.em_corda=True
            j.lume.corda_destino=PISO_ARQUIVO
            j.lume.rect.centerx=RAIZ_X
            j.lume.vx=j.lume.vy=0.
            j.eventos.append('corda')
        return
    if ident.startswith("volta_"):
        boca=ident.removeprefix("volta_")
        if boca=="estaleiro" and "ponte" not in j.historico.get((0,1),set()):
            j.notificar("A saída dá na ponte do Córrego. Estenda a ponte pela margem para abrir a passagem.")
            return
        if boca=="copa" and "atalho_copa" not in j.cartografia:
            j.notificar("A janela está presa por dentro. O pino fica no poleiro a oeste.")
            return
        if boca=="corrego":
            if j.etapa!=1 and "ralo_aberto" not in j.cartografia:
                j.notificar("O leito está alagado. Siga a marca de água até o ralo.")
                return
            if j.etapa!=1 and "raiz" not in j.historico.get((0,0),set()):
                j.notificar("A raiz ainda aperta a boca do canal. Reacenda a raiz principal do Bosque.")
                return
        etapa,x=BOCAS[boca]
        j.entrar(etapa)
        j.recolocar((x,CHAO))
        j.camera=min(j.fase.width-960,max(0,x-340))
        j.notificar("De volta à superfície · "+j.fase.name)
        return
    if ident.startswith("carro_"):
        if "ralo_aberto" not in j.cartografia:
            j.notificar("Contrapeso preso pela água. Desça à cisterna e use K + E no ralo a oeste, no fundo.",7.)
            return
        # A subida ou descida automática percorre o eixo em tempo real.
        j.destino_vertical=1828 if ident=="carro_alto" else 316
        j.lume.vx=j.lume.vy=0.
        j.eventos.append("corda")
        return
    if ident in ("marco_poco","marco_estaleiro"):
        j.marco_vertical=ident.removeprefix("marco_")
        j.checkpoint=MARCOS[j.marco_vertical]
        j.notificar("Retorno guardado neste patamar. O marco não repõe luz.")
        j.aplicar_dificuldade_no_marco()
        j.eventos.append("raiz")
        return
    if ident == "comporta_viveiro":
        if j.comporta_inicio is not None:
            return
        if "viveiro_aberto" not in j.cartografia:
            j.cartografia.update(("viveiro_aberto", "leu_comporta_viveiro"))
            j.comporta_inicio = j.tempo
            j.memorizar(*REGISTROS[ident])
            j.eventos.extend(("valvula", "agua"))
            return
    if ident=="ralo_cisterna" and "ralo_aberto" not in j.cartografia:
        if not ralo_iluminado(j,o):
            if j.lume.energia<=22:
                j.lume.energia=max(32., j.lume.energia)
                j.notificar("O musgo do ralo devolve um pouco de luz. Use K sobre a pedra.")
            else:
                j.notificar("Dois dentes sob o lodo. Deixe um clarão (K) aqui para encontrar a trava.")
            return
        j.cartografia.add("ralo_aberto")
        j.marco_vertical="cisterna"
        j.checkpoint=MARCOS["cisterna"]
        j.aplicar_dificuldade_no_marco()
        j.bolsa.receber("casulo",1)
        j.eventos.extend(("agua","porta"))
    if ident=="selo_copa" and "atalho_copa" not in j.cartografia:
        j.cartografia.add("atalho_copa")
        j.marco_vertical="copa"
        j.checkpoint=MARCOS["copa"]
        j.aplicar_dificuldade_no_marco()
        j.bolsa.receber("pavio",1)
        j.eventos.append("porta")
    if ident=="placa_arquivo" and "leu_placa_arquivo" not in j.cartografia:
        j.bolsa.receber("balsamo",1)
        j.eventos.append("coleta")
    if ident in REGISTROS:
        j.dialogo=REGISTROS[ident]
        j.memorizar(*j.dialogo)
        j.cartografia.add("leu_"+ident)
        j.eventos.append("pagina")


def objetivo(j):
    ident,_=setor(j.lume.rect.centery,j.lume.rect.centerx)
    if ident=="estaleiro":
        return ("A grade a leste da oficina desce ao viveiro" if j.lume.rect.bottom<850
                else "Bata as asas outra vez para alcançar a oficina")
    if ident=="viveiro":
        return ("Volte pela comporta a oeste ou suba aos berços"
                if "viveiro_aberto" in j.cartografia else "Siga os berços até a roda da comporta, no fundo")
    if ident=="arquivo":
        return "Examine o armário de Mimo. A galeria continua a leste"
    if ident=="copa":
        return ("Saia pela janela do Bosque ou explore o poço"
                if "atalho_copa" in j.cartografia else "Solte a janela na copa da figueira")
    if ident=="cisterna":
        return ("Siga à boca do Córrego ou suba no contrapeso"
                if "ralo_aberto" in j.cartografia else "Ilumine o ralo da cisterna e abra o canal")
    if ident=="poco":
        return "Leia a régua. A grade dá passagem à cisterna"
    return "O estaleiro fica a leste. A grade central desce ao poço"


def passo(j,dt,cmd,clarao):
    l=j.lume
    if j.comporta_inicio is not None and j.tempo - j.comporta_inicio >= TEMPO_COMPORTA:
        j.comporta_inicio = None
        j.eventos.append("porta")
    if j.destino_vertical is not None:
        if l.vida<=0:
            j.perder_fagulha()
            return
        distancia=j.destino_vertical-l.rect.bottom
        l.rect.centerx=1040
        l.rect.bottom+=math.copysign(min(abs(distancia),330*dt),distancia)
        if abs(distancia)<=330*dt:
            j.destino_vertical=None
            l.chao=True
        visitar(j)
        camera(j,dt)
        return
    estava_chao=l.chao
    if l.em_corda and l.corda_destino is not None:
        l.rect.bottom=max(l.corda_destino,l.rect.bottom-265*dt)
        l.vx=l.vy=0.;l.chao=False
        if l.rect.bottom<=l.corda_destino:
            l.em_corda=False;l.corda_destino=None;l.chao=True
    elif l.movimento(dt,cmd,j.solidos,0,True):
        j.eventos.append("pulo")
    l.rect.left=max(0,min(l.rect.left,LARGURA-l.rect.width))
    if l.rect.top>ALTURA+28:
        j.recuperar_queda()
        return
    if l.chao and not estava_chao:
        j.eventos.append("pouso")
    if cmd.deslize and l.slide>=.60:
        j.eventos.append("deslize")
    vida_antes=l.vida
    if l.arma.avancar(dt,l):
        j.eventos.append("golpe")
    if l.vida<vida_antes:
        j.eventos.append('sacrificio');j.notificar('O golpe usou vida porque faltou brilho.',3.)
    if l.vida<=0:j.perder_fagulha('sacrificio');return
    golpe=l.arma.area(l)
    if (golpe and l.arma.tipo == "queda" and not l.chao and l.vy >= 0
            and abs(l.rect.centerx - CASULO_X) <= 33 and golpe.colliderect(CASULO)):
        l.vy = -748.
        l.arma.rebote = .46
        j.eventos.append("rebote_casulo")
    if golpe and RAIZ_DUAS_BOCAS not in j.cartografia and golpe.colliderect(FERROLHO):
        j.cartografia.add(RAIZ_DUAS_BOCAS)
        j.eventos.extend(('madeira','porta'))
        j.notificar('A grade abriu no arquivo. Use E no cipó para subir.',6.)
        j.memorizar('O reparo de Fio',
                    'Fio amarrou um cipó entre o poço e o arquivo para levar os casulos acima da cheia. '
                    'A marca no alto e o ferrolho embaixo pertencem à mesma raiz.')
    from .fauna_jardim import aproximar_isca
    aproximar_isca(j)
    j.combater_inimigos(dt,golpe,clarao)
    from .jardim import atualizar
    atualizar(j)
    if l.vida<=0:
        j.perder_fagulha()
    visitar(j)
    camera(j,dt)


def desenhar_vertical(s,j,t,brilho_mata):
    from .arte_corte import desenhar
    desenhar(s,j,t,brilho_mata)


def desenhar_mapa(s,j,rect):
    from .cartografia import mapa_local
    mapa_local(s,j,rect)
