"""O sino soterrado demonstra o sinal que a Coruja segue na arena."""
from . import pygame_hd as pygame

from .descoberta import TAMANHO
from .ilustracao import PALIDO

SINO = (2530, 469)
MARCA = (2635, 428)
ENTRADA = (2530, 237)
FUNDO = 700
ALTURA = 810
SAIDA = (2985, 442)
PASSARELA = "passarela_escuta"
ECO = "eco_antigo"
TRECHO = (2370, 3040)
DURACAO = 1.42
COR = (219, 198, 133)
COR_PISADA = (230, 167, 86)
PATAMAR = (2606, 561)
POUSO = (2630, FUNDO)


def ativa(j):
    return j.etapa == 3 and not j.em_vertical


def dentro(j):
    return ativa(j) and TRECHO[0] <= j.lume.rect.centerx < TRECHO[1]


def camera(j, dt=None):
    from .sinalizacao import camera_vertical
    camera_vertical(j, ALTURA, dt, enquadrar=dentro(j))


def soltar(j):
    if PASSARELA in j.flags:
        j.notificar("A passarela liga a saída ao sino. A grade desce ao fundo.")
        return
    j.flags.add(PASSARELA)
    j.memorizar("Passarela da escuta", "A corda que leva o toque também sustenta o caminho de volta.")
    j.notificar("A passarela baixou. Ela liga a saída ao sino.")
    j.eventos.extend(("corda", "porta"))


def orientar(j):
    if not ativa(j) or "contrapeso" not in j.flags or "chefe" in j.flags:
        return None
    from .orientacao import _alvo

    x, y = j.lume.rect.midbottom
    chegando = x <= 2410 or (x < 2576 and y < 355)
    if chegando and PASSARELA not in j.flags:
        return _alvo(j, "grade_escuta", "Grade da escuta", "Desça pela grade",
                     *ENTRADA, "A trama marcada leva ao sino soterrado.",
                     acesso="suba aos galhos após o marco. Na grade, use S + Espaço.")
    if ECO not in j.flags or not dentro(j):
        return None
    if PASSARELA in j.flags and y < 485:
        return None
    if x < 2664 and y < 600:
        return _alvo(j, "fundo_escuta", "Grade do fundo", "Siga o eco para baixo",
                     *PATAMAR, "O eco aponta para o piso baixo entre as raízes.",
                     acesso="siga até a próxima grade abaixo do sino e use S + Espaço.")
    if y < 460:
        return _alvo(j, PASSARELA, "Trava da passarela", "Baixe a passarela",
                     *SAIDA, "Use E para ligar a saída ao sino. A passagem mantém-se aberta.")
    return _alvo(j, "saida_escuta", "Saída da câmara", "Suba pelos degraus à direita",
                 *SAIDA, "A trava da passarela fica no topo.",
                 acesso="salte pelos degraus marcados à direita até a grade alta.")


def pisar(j):
    """Chamado quando a física confirma um apoio, inclusive com o halo apagado."""
    if not dentro(j):
        return
    x, y = j.lume.rect.midbottom
    j.pisadas_escuta.add((j.volta, int(x) // TAMANHO, round(y)))


def carregar_pisadas(dados):
    if not isinstance(dados, list) or len(dados) > 2000:
        raise ValueError("Pisadas da Gruta inválidas")
    pisadas = set()
    for ponto in dados:
        if (not isinstance(ponto, (list, tuple)) or len(ponto) != 3
                or any(type(n) is not int for n in ponto)):
            raise ValueError("Pisada da Gruta inválida")
        volta, coluna, y = ponto
        if not (volta >= 0 and TRECHO[0] // TAMANHO <= coluna <= (TRECHO[1] - 1) // TAMANHO
                and ENTRADA[1] <= y <= FUNDO):
            raise ValueError("Pisada fora da Gruta")
        pisadas.add(tuple(ponto))
    return pisadas


def tocar(j):
    j.sino_eco_inicio = j.tempo
    j.eventos.append("sino")
    j.notificar("O eco aponta a fenda. A Coruja segue a mesma marca.", 4.)


def idade(j):
    inicio = getattr(j, "sino_eco_inicio", None)
    if inicio is None or j.em_vertical or j.etapa != 3:
        return None
    tempo = j.tempo - inicio
    return tempo if 0 <= tempo < DURACAO else None


def luzes(j):
    fixas = ()
    if dentro(j):
        fundo = j.lume.rect.bottom
        if fundo >= 545 and ECO in j.flags:
            fixas = ((POUSO[0], FUNDO - 14, 51),)
        elif 357 <= fundo <= 490 and j.lume.rect.centerx < 2576:
            fixas = ((2511, 451, 36),)
    tempo = idade(j)
    if tempo is None:
        return fixas
    x = SINO[0] + min(1., tempo/.40)*(MARCA[0]-SINO[0])
    luzes_eco = (*fixas, (x, MARCA[1], 105))
    if tempo >= .68:
        return (*luzes_eco, (PATAMAR[0], PATAMAR[1]-28, 69))
    return luzes_eco


def marca(s, x, y, acesa):
    cor = COR if acesa else (114, 131, 105)
    pygame.draw.lines(s, cor, False, [(x-11,y+3),(x,y-8),(x+11,y+3)], 2)
    pygame.draw.lines(s, cor, False, [(x-11,y+11),(x,y),(x+11,y+11)], 2)
    if acesa:
        pygame.draw.circle(s, PALIDO, (x,y+7), 2)


def desenhar(s, j, cx):
    if cx > TRECHO[1]+30 or cx+960 < TRECHO[0]-30:
        return
    # As duas setas da descida repetem o mesmo entalhe da trama.
    for x, y in (ENTRADA, PATAMAR):
        px = x-cx
        pygame.draw.lines(s, (118, 101, 64), False, [(px-15, y-9), (px, y+3), (px+15, y-9)], 5)
        pygame.draw.lines(s, COR, False, [(px-11, y-10), (px, y-1), (px+11, y-10)], 2)
    for x, y in (SINO, POUSO):
        for n in range(5):
            wx = x-cx-27+12*n
            pygame.draw.ellipse(s, (86, 120, 91), (wx, y-7-(n%2)*3, 13, 6))
            pygame.draw.circle(s, (155, 176, 111), (wx+6, y-7-(n%2)*3), 2)
    for x, y in ((2750, 628), (2855, 561), (2960, 500), SAIDA):
        marca(s, round(x-cx), y-14, ECO in j.flags)

    piso = SINO[1]
    ix, fim = round(SINO[0]-cx), round(MARCA[0]-cx)
    tempo = idade(j)
    for n in range(11):
        x = ix+10*n
        y = piso-12-round(30*(n/10)**2)
        pygame.draw.line(s, COR if tempo is not None and tempo>.033*n else (96, 112, 84),
                         (x,y), (x+6,y-1), 2)
    marca(s, fim, MARCA[1], tempo is not None and tempo>.33)
    if ECO in j.flags:
        # O traço de baixo aponta para a fenda, seguindo a fibra da raiz.
        segmentos = ((2640, 445), (2621, 470), (2609, 497), (2606, 527))
        for n, (x, y) in enumerate(segmentos):
            ativo = tempo is not None and tempo > .43 + n*.09
            pygame.draw.line(s, COR if ativo else (123, 111, 74),
                             (x-cx, y), (x-cx-4, y+9), 2)
