"""Marcas do canal e retomada do trabalho de Casca e Fio."""
import math

from . import pygame_hd as pygame

from .fases import CHAO, RAIZ, Objeto


BERCOS = Objeto("marca_bercos_corrego", "pista", 1476, CHAO, "Examinar a marca dos berços")
LEITURA = "leu_bercos_corrego"
COMPARACAO = "Os dois lados do canal"
REENCONTRO = "casca_fio_reencontro"
CASCA_MARGEM = (1430, CHAO)


def comparar(j):
    if {"pista_canal", LEITURA} <= j.flags:
        j.memorizar(COMPARACAO,
                    "Os três riscos de Casca marcam o último turno com água na borda. "
                    "Fio amarrou os berços abaixo da linha que secou. As duas marcas são de antes do raio.")


def examinar(j):
    j.flags.add(LEITURA)
    j.dialogo = ("Os berços de Fio",
                 "Há três riscos no apoio. A seda dos berços está amarrada mais embaixo, no trecho seco. "
                 "Quem baixou os berços deixou espaço para a água voltar. Um fio novo sobe até os casulos da Tecelã no vão.")
    j.memorizar(*j.dialogo)
    comparar(j)
    j.eventos.append("pagina")


def fala_da_margem(j):
    if REENCONTRO not in j.flags:
        j.flags.add(REENCONTRO)
        j.memorizar("A margem de Casca e Fio",
                    "Casca segura a amarra enquanto Fio termina o nó. A água alcança os berços e sustenta a travessia acima do ralo.")
    passagem = " Dá para atravessar acima do ralo. A grade ainda desce para quem quer ver o leito."
    if {"pista_canal", LEITURA} <= j.flags:
        return ("Você viu os três riscos nas duas margens. Fui eu que parei a água naquela altura. "
                "Hoje Fio me deixou segurar a corda. Quando a primeira gota passou, ela riu.") + passagem
    return ("Fio baixou os berços. Desta vez segurei a corda enquanto ela amarrava. "
            "Achei que ia dizer alguma coisa sobre a noite em que fechei o canal. Ela só pediu que eu segurasse mais firme.") + passagem


def desenhar(s, j, cx):
    """Os entalhes repetidos ligam as duas margens sem exigir leitura."""
    cor = (178, 155, 109)
    for mundo in (788, BERCOS.x-13):
        x = round(mundo-cx)
        if not -75 <= x <= 1035:
            continue
        pygame.draw.lines(s, (78, 71, 47), False, [(x+7,CHAO),(x-2,CHAO-20),(x+3,CHAO-59)], 10)
        for n in range(3):
            y = CHAO-46+n*7
            pygame.draw.line(s, cor, (x-3,y), (x+4,y-2), 2)
    if cx+960 < 1410 or cx > 1640:
        return
    for n, mundo in enumerate((1457, 1496, 1548)):
        x = round(mundo-cx)
        y = CHAO - 15 - (n%2)*5
        pygame.draw.aaline(s, (161, 177, 142), (x-14,y-20), (x+14,y-15))
        pygame.draw.arc(s, (155, 132, 81), (x-12,y-8,24,16), math.pi, 2*math.pi, 3)
        pygame.draw.line(s, (120, 103, 65), (x-11,y+2), (x+10,y+3), 2)
    if "raiz" in j.flags:
        corda = [(round(x-cx), CHAO-26+math.sin((x-1430)/137*math.pi)*13)
                 for x in range(1430, 1568, 7)]
        pygame.draw.lines(s, (191, 179, 137), False, corda, 3)
        for mundo, lado in ((CASCA_MARGEM[0], 1), (1567, -1)):
            x = round(mundo-cx)
            mao = (x+lado*(22+math.sin(j.tempo*4)*4), CHAO-20)
            pygame.draw.line(s, (166, 143, 91), (x,CHAO-29), mao, 3)


def _veios_da_raiz(s, j, cx):
    if not -95 <= RAIZ-cx <= s.get_width()+95:
        return
    restaurada = "raiz" in j.flags
    for sentido in (-1, 1):
        pontos = [pygame.Vector2(RAIZ-cx+sentido*x, CHAO+y) for x, y in
                  ((3,-13), (18,-5), (35,5), (64,13), (91,16))]
        pygame.draw.lines(s, (39, 51, 45), False, pontos, 7)
        cor = (82, 150, 133) if restaurada else (74, 72, 55)
        pygame.draw.lines(s, cor, False, pontos, 3)
        if restaurada:
            for n in range(3):
                posicao = (j.tempo*1.7+n/3+sentido*.1) % 1 * (len(pontos)-1)
                trecho = int(posicao)
                fracao = posicao-trecho
                inicio, fim = pontos[trecho:trecho+2]
                pygame.draw.aaline(s, (157, 210, 189), inicio.lerp(fim,fracao),
                                   inicio.lerp(fim,min(1., fracao+.34)))


def desenhar_agua(s, j, cx):
    _veios_da_raiz(s, j, cx)
    if cx+960 < 1386 or cx > 1558:
        return
    # A água se divide junto à margem e corre sob os berços.
    reaberto = "raiz" in j.flags
    for n in range(2):
        rapidos = []
        for d in range(0, 169, 7):
            x = round(1558-cx-d)
            y = round(CHAO+13+d*(.075+n*.15)+math.sin(d*.052+n)*3)
            largura = (1 + math.sin(d/168*math.pi) * (5 if n == 0 else 3))
            rapidos.append((x, y, largura))
        leito = [(x,y-l) for x,y,l in rapidos] + [(x,y+l) for x,y,l in reversed(rapidos)]
        pygame.draw.polygon(s, (62, 111, 105) if reaberto else (44, 69, 66), leito)
        if reaberto:
            for k in range(4):
                i = int(j.tempo*10+k*6+n*3) % (len(rapidos)-2)
                x, y, _ = rapidos[i]
                fim_x, fim_y, _ = rapidos[i+2]
                pygame.draw.aaline(s, (141, 200, 174), (x,y), (fim_x,fim_y+1))
