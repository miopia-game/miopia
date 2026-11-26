"""Tipografia, imagens e pequenos sinais compartilhados pelas telas."""
from functools import lru_cache
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import pygame as sdl

from . import pygame_hd as pygame

RAIZ = Path(__file__).resolve().parents[1]
ARTE = RAIZ / "assets" / "arte"
_FORMATO_RGB = sdl.Surface((1, 1), depth=32)
_FORMATO_RGBA = sdl.Surface((1, 1), sdl.SRCALPHA, depth=32)
OBJETOS_ATLAS = {
    nome: indice for indice, nome in enumerate((
        "obj_orvalho.png", "obj_valvula.png", "obj_corda.png", "obj_peca.png",
        "obj_tocha_acesa.png", "obj_refugio.png", "obj_marco.png", "obj_raiz.png",
    ))
}
GALHOS_ATLAS = {
    "galho_enraizado.png": 0, "galho_musgo.png": 1,
    "galho_seco.png": 2, "galho_broto.png": 3,
}
TERRENO_PINTADO = {
    "pintado_raiz.png": 0, "pintado_galho.png": 1,
    "pintado_solo.png": 2, "pintado_broto.png": 3,
}
ELENCO_PINTADO = {
    "pintado_mimo.png": 0, "pintado_nira.png": 1, "pintado_vespera.png": 2,
    "pintado_roda.png": 3, "pintado_registro.png": 4, "pintado_pacote.png": 5,
    "pintado_passagem.png": 6, "pintado_orvalho.png": 7,
}
UTENSILIOS_BOSQUE = {
    "mochila_bosque.png": 2,
}
FLORA_BOSQUE = {
    "bosque_sarcas.png": 0, "bosque_samambaias.png": 1,
    "bosque_fungos.png": 2, "bosque_juncos.png": 3,
}
HUD_MIOPIA = {
    "hud_asa.png": 0, "hud_asa_ferida.png": 1, "hud_asa_critica.png": 2,
    "hud_abdomen.png": 3, "hud_folha.png": 4, "hud_fagulha.png": 5,
}
OSSO = (232, 231, 210)
PALIDO = (176, 197, 184)
AMBAR = (241, 183, 101)
TINTA = (10, 18, 23)
TEAL = (104, 139, 132)
PERIGO = (245, 154, 122)
ROMANOS = ("I", "II", "III", "IV")
_leitura = ContextVar("leitura", default=(100, False, False, None, False))


@contextmanager
def estilo(preferencias, controles=None):
    estado = (preferencias.get("texto",100), preferencias.get("contraste",False),
              preferencias.get("claroes_suaves",False), controles, preferencias.get("numeros_hud",False))
    anterior = _leitura.set(estado)
    try:
        yield
    finally:
        _leitura.reset(anterior)


def tamanho_texto(tam):
    return round(tam*_leitura.get()[0]/100) if tam <= 22 else tam


def alto_contraste():
    return _leitura.get()[1]


def claroes_suaves():
    return _leitura.get()[2]


def numeros_hud():
    return _leitura.get()[4]


def dica_teclado(msg):
    controles = _leitura.get()[3]
    return controles.dicas(msg) if controles is not None else msg


@lru_cache(maxsize=48)
def fonte(tamanho, estilo="normal"):
    arquivo = {"titulo":"LiberationSerif-Regular.ttf", "forte":"Nunito-Bold.ttf",
               "normal":"Nunito-Regular.ttf"}[estilo]
    return pygame.font.Font(RAIZ / "assets" / "fontes" / arquivo, tamanho)


@lru_cache(maxsize=384)
def tinta(msg, tamanho, cor, estilo):
    # O layout usa as métricas do caderno. A fonte rasteriza o contorno em Full HD.
    medidas = fonte(tamanho, estilo).size(msg)
    pixels = fonte(tamanho * 2, estilo).render(msg, True, cor)
    tamanho_fisico = (medidas[0] * 2, medidas[1] * 2)
    if pixels.get_size() != tamanho_fisico:
        pixels = sdl.transform.smoothscale(pixels, tamanho_fisico)
    return pygame.nativa(pixels, medidas)


def texto(surf, msg, x, y, tam=17, cor=OSSO, estilo="normal", alinhar="left"):
    if alto_contraste():
        cor = tuple(round(c*.76 + 61) for c in cor)
    im = tinta(str(msg), tamanho_texto(tam), cor, estilo)
    rect = im.get_rect(top=y)
    setattr(rect, alinhar, x)
    pygame.blit(surf, im, rect)
    return rect


def linhas(msg, largura, tam=17, estilo="normal"):
    f = fonte(tamanho_texto(tam), estilo)
    linha = ""
    out = []
    for palavra in msg.split():
        tentativa = (linha + " " + palavra).strip()
        if linha and f.size(tentativa)[0] > largura:
            out.append(linha)
            linha = palavra
        else:
            linha = tentativa
    if linha:
        out.append(linha)
    return out


def dica_local(s, tecla, rotulo, ponto):
    """Desenha uma ação curta acima de um ponto da cena, em coordenadas da tela."""
    tecla = dica_teclado(tecla)
    rotulo = dica_teclado(rotulo)
    estilo = "forte"
    tamanho = tamanho_texto(16)
    f = fonte(tamanho, estilo)
    chave = fonte(tamanho_texto(15), estilo)
    largura_tecla = max(24, chave.size(tecla)[0] + 12) if tecla else 0
    margem = largura_tecla + 8 if tecla else 0
    corpo = linhas(rotulo, 250 - margem, 16, estilo)
    largura = margem + max(f.size(linha)[0] for linha in corpo)
    passo = f.get_height()
    altura = max(passo + 4, passo * len(corpo))
    x, y = ponto
    x = max(12, min(s.get_width() - largura - 12, round(x - largura / 2)))
    y = max(90, min(s.get_height() - altura - 12, round(y - altura - 12)))
    if tecla:
        caixa = pygame.Rect(x, y, largura_tecla, passo + 4)
        pygame.draw.rect(s, (16, 22, 32), caixa, border_radius=5)
        pygame.draw.rect(s, AMBAR if alto_contraste() else (204, 167, 109), caixa, 1, border_radius=5)
        texto(s, tecla, caixa.centerx, y + 2, 15, AMBAR, estilo, "centerx")
    for n, linha in enumerate(corpo):
        pos = x + margem, y + 2 + n * passo
        sombra = tinta(linha, tamanho, (10, 13, 22), estilo)
        for dx, dy in ((-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)):
            pygame.blit(s, sombra, (pos[0] + dx, pos[1] + dy))
        texto(s, linha, *pos, 16, OSSO, estilo)


def paragrafo(surf, msg, x, y, largura, tam=17, cor=OSSO, estilo="normal", entre=None):
    for linha in linhas(msg, largura, tam, estilo):
        texto(surf, linha, x, y, tam, cor, estilo)
        y += entre or (tamanho_texto(tam) + 5)
    return y


@lru_cache(maxsize=150)
def original(nome):
    if nome in OBJETOS_ATLAS:
        return _celula("objetos_atlas.png", OBJETOS_ATLAS[nome], 4)
    if nome in GALHOS_ATLAS:
        return _celula("galhos_atlas.png", GALHOS_ATLAS[nome], 2)
    if nome in TERRENO_PINTADO:
        return _celula("bosque_terreno_atlas.png", TERRENO_PINTADO[nome], 2)
    if nome in ELENCO_PINTADO:
        return _celula("bosque_elenco_atlas.png", ELENCO_PINTADO[nome], 4)
    if nome in UTENSILIOS_BOSQUE:
        return _celula("bosque_utensilios_atlas.png", UTENSILIOS_BOSQUE[nome], 2)
    if nome in FLORA_BOSQUE:
        return _celula("bosque_flora_atlas.png", FLORA_BOSQUE[nome], 2, divisor_superior=.60)
    if nome in HUD_MIOPIA:
        return _celula("hud_miopia_atlas.png", HUD_MIOPIA[nome], 3)
    path = ARTE / nome
    im = sdl.image.load(str(path))
    if path.suffix != ".png":
        return im.convert(_FORMATO_RGB)
    im = im.convert(_FORMATO_RGBA)
    if nome in ("passagem_raizes.png", "morcego_poleiro.png"):
        return im.subsurface(im.get_bounding_rect(min_alpha=100)).copy()
    return im


def _celula(atlas, indice, colunas, *, divisor_superior=None):
    folha = original(atlas)
    largura, altura = folha.get_width()//colunas, folha.get_height()//2
    linha, coluna = divmod(indice, colunas)
    x = coluna*largura
    if linha == 0 and divisor_superior is not None:
        divisao = round(folha.get_width()*divisor_superior)
        x, largura = (divisao, folha.get_width()-divisao) if coluna else (0, divisao)
    celula = folha.subsurface((x, linha*altura, largura, altura))
    return celula.subsurface(celula.get_bounding_rect(min_alpha=100)).copy()


@lru_cache(maxsize=600)
def imagem(nome, largura, altura, espelho=False):
    im = pygame.transform.smoothscale(original(nome), (max(1, largura), max(1, altura)))
    return pygame.transform.flip(im, True, False) if espelho else im


def sprite(surf, nome, x, pe, largura, altura, espelho=False):
    im = imagem(nome + ".png", int(largura), int(altura), espelho)
    r = im.get_rect(midbottom=(round(x), round(pe)))
    pygame.blit(surf, im, r)
    return r


def manivela(surf, x, pe, largura, altura, girada):
    sprite(surf, "obj_valvula", x, pe, largura, altura)
    eixo = round(x), round(pe - altura * .61)
    lado = 1 if girada else -1
    pino = eixo[0] + lado * round(largura * .27), eixo[1] + lado * round(altura * .17)
    pygame.draw.line(surf, TINTA, eixo, pino, 5)
    pygame.draw.line(surf, AMBAR, eixo, pino, 2)
    pygame.draw.circle(surf, OSSO, pino, 3)


def losango(surf, x, y, r=4, cor=AMBAR, cheio=True):
    pts = ((x,y-r),(x+r,y),(x,y+r),(x-r,y))
    pygame.draw.polygon(surf, cor, pts, 0 if cheio else 1 + int(alto_contraste()))


@lru_cache(maxsize=90)
def placa(w, h, opacidade=213):
    out = pygame.Surface((w,h), pygame.SRCALPHA)
    out.fill((*TINTA,opacidade))
    return out


def painel(surf, r, friso=True):
    r = pygame.Rect(r)
    pygame.blit(surf, placa(r.w,r.h,249 if alto_contraste() else 213),r)
    if friso:
        pygame.draw.line(surf, TEAL, r.topleft,(r.right-1,r.top))
        pygame.draw.line(surf, (53,72,70), r.bottomleft,(r.right-1,r.bottom))
        losango(surf,r.left+2,r.top,3)


@lru_cache(maxsize=40)
def halo(raio):
    im = pygame.Surface((raio*2,raio*2), pygame.SRCALPHA)
    for r in range(raio,0,-2):
        f = 1-r/raio
        pygame.draw.circle(im,(250,177,88,int(65*f*f)),(raio,raio),r)
    return im


def brilho(surf, xy, raio):
    pygame.blit(surf, halo(raio),(int(xy[0])-raio,int(xy[1])-raio))
