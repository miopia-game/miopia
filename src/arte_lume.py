"""Silhueta, articulação e luz de Lume no espaço de desenho da partida."""
from functools import lru_cache
import json
from math import floor

from . import movimento_arte, pygame_hd as pygame
from .ilustracao import ARTE, brilho, original

# A célula tem 192 × 160 pixels físicos. As botas pousam na linha 132.
TAMANHO = (96, 80)
PE = 66
QUADROS = 16
POSES = {
    "parado": "guarda", "andar": "passo", "correr": "corrida", "pulo": "voo",
    "queda": "queda", "planar": "planeio", "golpe": "golpe", "agachar": "agachar",
    "deslize": "deslizar", "dano": "recuo", "clarao": "clarao", "corda": "escalar",
    "parede": "parede",
}


@lru_cache(maxsize=1)
def _farois():
    return json.loads((ARTE / "lume" / "farol.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=512)
def _quadro(nome, indice, espelho):
    folha = original(f"lume/{nome}.png")
    w, h = folha.get_width() // 4, folha.get_height() // 4
    linha, coluna = divmod(indice, 4)
    imagem = pygame.nativa(folha.subsurface((coluna*w, linha*h, w, h)), TAMANHO)
    fx, fy = _farois()[nome][indice]
    if espelho:
        imagem = pygame.transform.flip(imagem, True, False)
        fx = w - 1 - fx
    return imagem, (fx / 2, fy / 2)


@lru_cache(maxsize=32)
def imagem_lume(pose, quadro, largura, altura, espelho=False):
    """Também fornece ao lançador a silhueta que aparece na partida."""
    im, _ = _quadro(POSES[pose], quadro % QUADROS, espelho)
    corpo = im.subsurface(im.get_bounding_rect(min_alpha=60))
    escala = min(largura/corpo.get_width(), altura/corpo.get_height())
    return pygame.transform.smoothscale(corpo, (round(corpo.get_width()*escala), round(corpo.get_height()*escala)))


def animacao(lume, tempo, fagulha=None):
    pose = lume.pose
    nome = POSES[pose]
    passos = movimento_arte.deslocamento(lume, lume.rect.centerx, tempo, lume.face)
    idade = tempo - fagulha.inicio if fagulha else -1
    if 0 <= idade < .17 and pose in ("parado", "andar", "correr", "pulo", "queda", "planar"):
        face = 1 if fagulha.destino[0] >= fagulha.origem[0] else -1
        return "lancar", min(15, int(idade/.17*QUADROS)), face
    if pose == "golpe" and lume.arma.perfil:
        if lume.arma.tipo == "queda":
            nome = "mergulho"
        ataque = lume.arma
        perfil = ataque.perfil
        if ataque.tempo < perfil.espera:
            indice = int(3 * ataque.tempo / perfil.espera)
        elif ataque.tempo < perfil.espera + perfil.ativo:
            indice = 3 + int(9 * (ataque.tempo-perfil.espera) / perfil.ativo)
        else:
            recuperacao = perfil.total - perfil.espera - perfil.ativo
            indice = min(15, 12 + int(4 * (ataque.tempo-perfil.espera-perfil.ativo) / recuperacao))
        return nome, indice, ataque.face
    if pose in ("andar", "correr"):
        return nome, floor(passos.distancia / 55 * QUADROS) % QUADROS, lume.face
    ritmo = {"pulo": 5.4, "queda": 4.1, "planar": 1.15, "corda": 1.1, "parede": .85}.get(pose, .78)
    if lume.batida_asa > 0 and pose in ("pulo", "queda"):
        ritmo = 8
    return nome, int(tempo * ritmo * QUADROS) % QUADROS, lume.face


def desenhar_lume(s, lume, x, pe, tempo, fagulha=None):
    nome, indice, face = animacao(lume, tempo, fagulha)
    im, farol = _quadro(nome, indice, face < 0)
    caixa = im.get_rect(topleft=(round(x - TAMANHO[0]/2), round(pe - PE)))
    brilho(s, (caixa.x+farol[0], caixa.y+farol[1]), 55)
    if lume.iframes <= 0 or int(tempo*14) % 3 != 1:
        pygame.blit(s, im, caixa)
    return caixa
