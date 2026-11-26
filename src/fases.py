"""Plantas laterais, pontos de interação e consequências dos quatro mecanismos."""
from __future__ import annotations

from dataclasses import dataclass, replace
import pygame
from . import aula_sino, vento_taquaral

CHAO = 442
GALHO_DO_MORCEGO = (985, 240, 220)
# O arquivo salvo guarda o identificador do marco; sua posição vem da planta atual.
MEIO = 1848
VIGIA_X = 1980
TRANCA_X = 2034
ARENA = 3680
FIM_ARENA = ARENA + 760
RAIZ = FIM_ARENA + 110
SAIDA = RAIZ + 120
LARGURA = SAIDA + 50


@dataclass(frozen=True)
class Terreno:
    rect: pygame.Rect
    tipo: str

    @property
    def atravessavel(self):
        return self.tipo in ("plataforma", "ponte", "apoio", "apoio_fagulha", "arena", "grade")

    @property
    def descida(self):
        return self.tipo in ("plataforma", "apoio", "apoio_fagulha", "grade")


@dataclass(frozen=True)
class Objeto:
    id: str
    tipo: str
    x: int
    y: int
    nome: str
    # Objeto só aparece depois desta mudança. Itens marcados com seu próprio
    # identificador somem; mecanismos permanecem visíveis após o uso.
    requer: str = ""


@dataclass(frozen=True)
class Mecanismo:
    requer: str
    falta: str
    efeito: str
    audio: tuple[str, ...]


@dataclass(frozen=True)
class Fase:
    name: str
    pisos: tuple[tuple[int, int], ...]
    plataformas: tuple[tuple[int, int, int], ...]
    tetos: tuple[tuple[int, int, int, int], ...]
    objetos: tuple[Objeto, ...]
    mecanismos: dict[str, Mecanismo]
    preparo: str
    passos: tuple[tuple[str, str], ...]
    inimigos: tuple[tuple[str, int, int], ...]
    orvalhos: tuple[tuple[int, int], ...]
    registro: tuple[str, str]
    fonte: str
    width: int = LARGURA


O = Objeto
M = Mecanismo
FASES = (
    Fase(
        "Bosque das Samambaias",
        ((0, 1380), (1480, LARGURA)),
        ((310, 376, 130), (481, 312, 174), (680, 248, 127), GALHO_DO_MORCEGO,
         (1270, 372, 110), (321, 228, 109)),
        ((1160, 350, 110, 68),),
        (O("nira", "npc", 224, CHAO, "Nira"), O("vespera", "npc", 755, 248, "Véspera"),
         O("encomenda_mimo", "encomenda", 374,228,"Recolher a mochila de Mimo"),
         O("registro", "registro", 708, 248, "Ler o mapa do berçário"),
         O("corda", "corda", 990, CHAO, "Subir pelo cipó"),
         O("peca", "peca", 1128, 240, "Retirar a peça de raiz")),
        {"peca": M("", "", "A peça se encaixa. Siga para a forquilha dos ninhos.", ("coleta", "porta"))},
        "peca", (("peca", "Suba pelo cipó e retire a peça de raiz"),),
        (("morcego", 875, 344), ("morcego", 1548, 356), ("aranha",1660,CHAO)),
        ((278, 417), (407, 350), (850, 415), (1145, 208), (1322, 346), (1680, 414)),
        ("Mapa do berçário", "Nira riscou a data na seda. A trilha do berçário sumiu duas luas antes do raio. O diário (M) guarda a rota para o berçário. Conte a data a Véspera."),
        "Uma peça de raiz mantém a arena aberta.",
    ),
    Fase(
        "Córrego Fundo",
        ((0, 1350), (1550, LARGURA)),
        ((330, 374, 132), (500, 310, 154), (682, 245, 120)),
        ((855, 322, 200, 96),),
        (O("casca", "npc", 218, CHAO, "Casca"), O("fio", "npc", 1220, CHAO, "Fio"),
         O("registro", "registro", 738, 245, "Nível antigo"),
         O("dreno", "valvula", 432, 374, "Drenar o canal"),
         O("lingueta", "peca", 982, CHAO, "Recolher a lingueta"),
         O("placa_canal", "pista", 798, CHAO, "Ler a marca de Casca"),
         O("ponte", "valvula", 1295, CHAO, "Soltar a ponte")),
        {"dreno": M("", "", "Canal drenado. Deslize sob a raiz à direita e recolha a lingueta com E.", ("valvula", "agua")),
         "lingueta": M("dreno", "Primeiro gire a roda do dreno, no primeiro galho acima de Casca.",
                       "Lingueta recolhida. A roda da ponte fica no chão, depois de Fio e antes do vão.", ("coleta",)),
         "ponte": M("lingueta", "Falta a lingueta sob a raiz baixa à esquerda. Drene o canal para recolhê-la.",
                    "Ponte estendida. A amarra liberou o ralo do outro lado; desça pela grade depois do marco.", ("valvula", "corda", "porta"))},
        "ponte", (("dreno", "Gire a roda do primeiro galho, acima de Casca"), ("lingueta", "Deslize sob a raiz baixa e recolha a lingueta"),
                  ("ponte", "Use a lingueta na roda da ponte, depois de Fio")),
        (("aranha", 1610, CHAO), ("morcego",1698,350), ("cobra",2890,CHAO)),
        ((285, 416), (418, 347), (740, 216), (805, 416), (1130, 415), (1668, 414)),
        ("Nível antigo", "No fundo, dois sulcos de água. Um alimentava a borda; o outro, mais recente, dobra rumo à figueira."),
        "O mecanismo de Casca permite chamar a cortina de água.",
    ),
    Fase(
        "Taquaral",
        ((0, 920), (1235, 1480), (1555, LARGURA)),
        (vento_taquaral.BEIRAL, (318, 377, 146), (508, 310, 154), (685, 243, 135), (1300, 375, 135)),
        ((1618, 350, 115, 68), vento_taquaral.ABA, vento_taquaral.POUSO),
        (O("eco", "npc", 245, CHAO, "Eco"), O("risca", "npc", 604, 310, "Risca"),
         O("registro", "registro", 745, 243, "Pele de taquara"),
         O("no", "no", 830, CHAO, "Acender o nó lateral"),
         O(vento_taquaral.PAVIO, "pavio_nicho", 443, vento_taquaral.POUSO[1], "Recolher o pavio sob a aba"),
         O("brasa", "brasa", 1370, 375, "Recolher a brasa de seiva")),
        {"no": M("", "", "O brilho de Eco alcança três apoios no vão. As sombras encolhem.", ("raiz",)),
         "brasa": M("no", "A fonte só amadurece sob o nó aceso.", "A brasa pulsa em sua casca. Além da ponte quebrada, há uma vagem seca.", ("coleta", "porta"))},
        "brasa", (("no", "Acenda o nó de Eco à beira do vão"), ("brasa", "Salte pelos apoios e recolha a brasa")),
        (("sombra", 1320, CHAO), ("vespa",1404,350), ("morcego", 1620, 340)),
        ((308, 416), (430, 349), (728, 215), (855, 415), (1290, 416), (1770, 413)),
        ("Pele de taquara", "Na face voltada ao descampado, a taquara está seca. Na face de sombra há marcas de vaga-lume."),
        "A brasa protegida responde à seiva do guardião.",
    ),
    Fase(
        "Gruta da Figueira",
        ((0, 1220), (1390, LARGURA)),
        ((315, 377, 156), (508, 309, 152), (695, 245, 120), (980, 242, 218),
         (1455, 372, 105)),
        ((1580, 344, 130, 74),),
        (O("no_memoria", "npc", 242, CHAO, "Nó"), O("pingo", "npc", 1450, CHAO, "Pingo"),
         O("registro", "registro", 748, 245, "Cicatriz por dentro"),
         O("roldana", "valvula", 580, 309, "Girar a roldana"),
         O("corda", "corda", 988, CHAO, "Subir pela corda", "roldana"),
         O("contrapeso", "sino", 1120, 242, "Soltar o contrapeso")),
        {"roldana": M("", "", "A corda tomba ao lado do estrado. O sino ainda está preso acima.", ("valvula", "corda")),
         "contrapeso": M("roldana", "A trava depende da roldana.", "O estrado pousa sobre o vão. O eco vem de outro sino, mais fundo.", ("corda", "porta"))},
        "contrapeso", (("roldana", "Gire a roldana sobre as raízes"), ("contrapeso", "Suba a corda e solte o contrapeso")),
        (("sombra", 1508, CHAO), ("morcego",1594,344), ("aranha", 1750, CHAO)),
        ((278, 416), (414, 349), (735, 217), (835, 415), (1144, 212), (1735, 413)),
        ("Cicatriz por dentro", "A sombra acompanha os veios da árvore. Onde ninguém trouxe orvalho, a própria figueira escureceu."),
        "O sino está ao alcance da guardiã.",
    ),
)

# A segunda metade de cada mapa tem uma função própria. As grades de casca são
# plataformas atravessáveis; paredes de escalada recebem o impulso lateral de Lume.
@dataclass(frozen=True)
class Ramal:
    nome: str
    pisos: tuple
    pecas: tuple
    objetivo: Objeto
    reserva: tuple
    gotas: tuple
    inimigos: tuple
    passo: str
    efeito: str


RAMAIS = (
    Ramal("Forquilha dos ninhos",
          ((1780, 2735), (2900, LARGURA)),
          ((2130, -16, 34, 405, "parede"), (2264, 201, 44, 241, "parede"),
           (2306, 205, 198, 15, "plataforma"), (2430, 291, 93, 15, "plataforma"),
           (2510, 365, 94, 15, "plataforma"), (2650, 358, 80, 15, "plataforma"),
           (3010, 369, 114, 15, "plataforma"), (3160, 307, 162, 15, "grade"),
           (3325, 246, 120, 15, "plataforma")),
          O("cunha", "peca", 2379, 205, "Soltar a cunha do berçário"),
          (3392, 246), ((2195, 357), (2395, 177), (3082, 340)),
          (("vespa", 1978, 336), ("carabideo", 3150, CHAO)),
          "Suba a forquilha pelos dois troncos e solte a cunha",
          "A cunha solta a casca presa no alto. O caminho dos ninhos alcança a arena."),
    Ramal("Comporta de fundo",
          ((1780, 2168), (2462, 2745), (2845, 3095), (3230, LARGURA)),
          ((1970, 377, 133, 15, "plataforma"), (2115, 315, 84, 15, "plataforma"),
           (2150, 315, 44, 155, "vedacao"), (2194, 315, 244, 15, "grade"),
           (2167, 470, 309, 90, "chao"), (2194, 387, 68, 15, "plataforma"),
           (2440, 315, 40, 155, "comporta"),
           (2020, 235, 112, 15, "plataforma"), (2640, 374, 101, 15, "plataforma"),
           (2805, 312, 110, 15, "grade"), (2990, 369, 110, 15, "plataforma"),
           (3190, 354, 112, 15, "plataforma")),
          O("ralo", "valvula", 2316, 470, "Destravar o ralo da comporta"),
          (2070, 235), ((2006, 349), (2298, 439), (3030, 337)),
          (("aranha", 2590, CHAO), ("vespa", 3280, 337)),
          "Desça pela grade com baixo + Espaço e destrave o ralo",
          "A folha de fundo sobe. Água e casulos voltam a passar pelo mesmo canal."),
    Ramal("Ponte das sementes",
          ((1780, 2500), (2845, 3120), (3240, LARGURA)),
          ((2050, 371, 142, 15, "plataforma"), (2227, 300, 175, 15, "grade"),
           (2400, 298, 100, 15, "plataforma"), (2890, 374, 115, 15, "plataforma"),
           (3030, 307, 132, 15, "grade"), (3216, 358, 117, 15, "plataforma"),
           (3380, 291, 120, 15, "plataforma")),
          O("vagem", "peca", 2920, CHAO, "Colher a vagem da outra margem"),
          (3400, 291), ((2210, 414), (2440, 270), (2880, 412)),
          (("carabideo", VIGIA_X, CHAO), ("vespa", 3058, 338)),
          "Plane do bambuzal quebrado até a vagem na outra margem",
          "A vagem se abre ao calor. A raiz conduz o cheiro de volta a Eco."),
    Ramal("Câmara da escuta",
          ((1780, 2380), (3260, LARGURA)),
          ((1982, 374, 122, 15, "plataforma"), (2141, 307, 136, 15, "plataforma"),
           (2265, 237, 136, 15, "plataforma"), (2370, 237, 40, 232, "parede"),
           (2410, 237, 166, 15, "grade"), (2370, 469, 206, 95, "chao"),
           (2410, 384, 74, 15, "plataforma"), (2434, 306, 70, 15, "plataforma"),
           (2576, 0, 41, aula_sino.FUNDO, "comporta"),
           (2574, aula_sino.FUNDO, 466, 110, "chao"),
           (2564, 561, 82, 15, "grade"), (2678, 628, 150, 15, "plataforma"),
           (2780, 561, 160, 15, "plataforma"), (2904, 500, 108, 15, "plataforma"),
           (2940, CHAO, 100, 16, "grade"),
           (2960, 367, 80, 15, "plataforma"), (3160, 357, 72, 15, "plataforma"),
           (3340, 353, 120, 15, "plataforma")),
          O(aula_sino.ECO, "sino", *aula_sino.SINO, "Tocar o sino soterrado"),
          (2310, 237), ((2020, 346), (2500, 440), (2858, 674)),
          (("vespa", 2090, 334), ("sombra", 2870, aula_sino.FUNDO), ("carabideo", 3415, CHAO)),
          "Na câmara, desça pela grade para tocar o sino soterrado",
          "O sino devolve três batidas. Por baixo da figueira, a guardiã responde."),
)


def ampliar(fase, ramal):
    objeto = ramal.objetivo
    pendencia = {
        "peca": "A peça da porteira fica no galho alto do Bosque. Use o cipó à direita para chegar a ela.",
        "ponte": "A amarra ainda prende o ralo. A roda da ponte fica à esquerda, na superfície do Córrego, depois de Fio e antes do vão.",
        "brasa": "A brasa fica no galho da outra margem do primeiro vão. Acenda o nó de Eco para alcançar os apoios.",
        "contrapeso": "Solte o contrapeso no estrado alto da Gruta. A roldana dos primeiros galhos baixa a corda até ele.",
    }[fase.preparo]
    mecanismo = M(fase.preparo, pendencia, ramal.efeito, ("raiz", "porta"))
    return replace(fase,
        pisos=tuple((a, min(b,1780)) for a,b in fase.pisos if a<1780) + ramal.pisos,
        objetos=fase.objetos + (objeto, O("reserva","reserva",*ramal.reserva,"Abrir a bolsa de trilha")),
        mecanismos={**fase.mecanismos, objeto.id:mecanismo},
        preparo=objeto.id, passos=fase.passos+((objeto.id,ramal.passo),),
        inimigos=fase.inimigos+ramal.inimigos, orvalhos=fase.orvalhos+ramal.gotas)


FASES = tuple(ampliar(fase, ramal) for fase,ramal in zip(FASES,RAMAIS))
# A gota da varanda nova vai ao fim da lista: os IDs de coleta de saves
# anteriores continuam apontando para as mesmas gotas no Bosque.
FASES = (replace(FASES[0], orvalhos=FASES[0].orvalhos + ((414, 200),)), *FASES[1:])

# Vozes mudam com o mecanismo local e com a restauração da mata.
FALAS = {
    "Nira": ("Apaguei dois caminhos do meu mapa antes da tempestade. Véspera ainda canta lá em cima.",
             "O cipó leva ao galho onde Véspera guardou a peça da porteira.",
             "Agora posso redesenhar a trilha até o berçário. Vou deixar os ninhos vazios no mapa."),
    "Véspera": ("Três chamados. Espero até o galho responder. Eu conhecia cada ninho pelo eco. Agora conheço os que ficaram em silêncio.",
                "Quando o morcego dobrar as asas, procure os riscos na parede. Ele não consegue frear.",
                "Reconheci a primeira gota pelo barulho na casca. Usei as amarras dos casulos na ponte. "
                "Fico aqui para firmar os nós. Se alguém voltar atrasado, a travessia já estará pronta."),
    "Casca": ("Fechei a comporta quando Brasa pediu. Não contei a Fio por que o canal secou.",
              "A corrente empurra quem anda devagar. Use o deslize sob a raiz, a lingueta está na outra margem.",
              "Ainda tenho a chave. Desta vez vou deixá-la ao alcance de Fio."),
    "Fio": ("Remendo as teias por cima, onde a corrente não leva a seda.",
            "A Tecelã desce quando a cortina de água corta seus fios. A lingueta serve nas duas válvulas.",
            "Casca voltou com água. Ainda vai levar tempo para o canal encher."),
    "Eco": ("Quando eu piscar, olhe para a borda do vão. Ficou um nó de luz lá embaixo.",
            "O guardião dormia sob os bambus. Leve a brasa protegida; ele sente o calor pela casca.",
            "Ouvi Risca chamar. Pela primeira vez a resposta chegou ao outro lado."),
    "Risca": ("Vi olhos nas taquaras. Talvez a Coruja tenha vindo antes da tempestade.",
              "Eco reconheceu as luzes. Eram os que ficaram para trás, não os olhos da guardiã.",
              "Ainda olho duas vezes. Agora há um caminho para ir conferir."),
    "Nó": ("Guardo o que passou por estas raízes. Nem toda lembrança chegou inteira.",
           "O sino e a parede falam mais alto que os passos. A guardiã precisa ouvir um caminho de volta.",
           "A sombra continua em nós. O orvalho pode circular mesmo assim."),
    "Pingo": ("Mimo procura um casulo seco. Levarei seu recado pela trilha da borda.",
              "A porta se moveu. Já posso atravessar de novo com os recados.",
              "Levei as notícias a Candeia. De longe já dava para ver o refúgio."),
    "Brasa": ("Mandei juntar o orvalho no centro. Eu conseguia ver os pequenos dali.",
              "Nira diz que os galhos das bordas já secavam. Nunca fui até lá para olhar.",
              "Amanhã vou levar a primeira gota até o berçário."),
    "Mimo": ("Dois casulos, uma folha seca. Fique um instante; posso reacender sua luz.",
             "Pingo encontrou um teto para quem estava no córrego. Falta abrir o caminho.",
             "Temos outra folha seca. Já cabe mais alguém."),
    "Candeia": ("Estou contando as luzes. Daqui só vejo a do centro.",
                "Uma veia já pulsa longe do abrigo. É assim que os perdidos acham a volta.",
                "Deixei uma trilha em cada raiz. Agora também se vê a mata daqui."),
    "Coruja": ("Antes do raio, toquei o sino quando a água deixou a borda. Do tronco só veio silêncio.",
               "Bati o sino antes do raio, quando a água deixou a borda. Quando o raio me feriu, as batidas pareciam vir de todo lado. Você respondeu nos três ninhos. Falta devolver as gotas à última raiz.",
               "Agora escuto as quatro correntes. Quando o sino tocar, vou ficar junto à margem. Quero ouvir quem vem de longe."),
}


def terrenos(indice, flags):
    fase = FASES[indice]
    out = []
    def add(x, y, w, h, tipo):
        out.append(Terreno(pygame.Rect(x, y, w, h), tipo))

    for left, right in fase.pisos:
        add(left, CHAO, right - left, 128, "chao")
    for x, y, w in fase.plataformas:
        add(x, y, w, 16, "plataforma")
    for x, y, w, h in fase.tetos:
        add(x, y, w, h, "teto")
    if indice == 1:
        # O tampão fecha apenas a boca do canal. A lingueta fica deitada sob
        # a raiz, alcançável de ambas as margens pela passagem de 24 px.
        if "dreno" not in flags:
            add(853, CHAO-24, 30, 24, "vedacao")
        if "ponte" in flags:
            add(1345, CHAO, 210, 18, "ponte")
    if indice == 2 and "no" in flags:
        for x, y in ((944, 405), (1045, 354), (1150, 396)):
            add(x, y, 80, 15, "apoio")
    if indice == 3 and "contrapeso" in flags:
        add(1214, CHAO, 182, 16, "ponte")
        if aula_sino.PASSARELA in flags:
            add(2573, CHAO, 367, 16, "grade")
        else:
            # A raiz suspensa direciona a ida pelo piso baixo.
            add(2866, 0, 32, 473, "parede")
    for x,y,w,h,tipo in RAMAIS[indice].pecas:
        if tipo=="comporta":
            if fase.preparo in flags:
                continue
            tipo="vedacao"
        add(x,y,w,h,tipo)
    if fase.preparo not in flags:
        add(ARENA-50, 65, 38, CHAO-65, "porta")
    if "chefe" not in flags:
        add(FIM_ARENA, 78, 26, CHAO - 78, "porta")
    return out
