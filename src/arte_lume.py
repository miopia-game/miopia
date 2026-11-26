"""Poses de Lume e articulações desenhadas em coordenadas da partida."""
from functools import lru_cache
import json
from math import cos, floor, pi

from . import movimento_arte, pygame_hd as pygame
from .ilustracao import ARTE, brilho, original

TAMANHO = (96,80)
PE = 66
POSES = {
    "parado":"guarda", "andar":"passo", "correr":"corrida", "pulo":"voo",
    "queda":"queda", "planar":"planeio", "golpe":"golpe", "agachar":"agachar",
    "deslize":"deslizar", "dano":"recuo", "clarao":"clarao", "corda":"escalar",
    "parede":"parede",
}
SUBIDAS = {"corte2","retorno","aurora"}


@lru_cache(maxsize=1)
def _farois():
    return json.loads((ARTE / "lume/farol.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _juntas():
    return json.loads((ARTE / "lume/juntas.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _folha(nome):
    return original(f"lume/{nome}.png")


@lru_cache(maxsize=1)
def preparar():
    # Decodifica na entrada da partida, antes de receber o primeiro golpe ou salto.
    for nome in (*_farois(),"asas","asas-planeio"):
        _folha(nome)
    _juntas()


def total_quadros(nome):
    return len(_farois()[nome])


@lru_cache(maxsize=512)
def _imagem(nome, indice, espelho):
    folha = _folha(nome)
    w,h = 2*TAMANHO[0],2*TAMANHO[1]
    linha,coluna = divmod(indice,folha.get_width()//w)
    im = pygame.nativa(folha.subsurface((coluna*w,linha*h,w,h)),TAMANHO)
    return pygame.transform.flip(im,True,False) if espelho else im


def _ponto(ponto, espelho):
    x,y = ponto
    return ((2*TAMANHO[0]-1-x if espelho else x)/2,y/2)


def _quadro(nome, indice, espelho):
    return _imagem(nome,indice,espelho), _ponto(_farois()[nome][indice],espelho)


@lru_cache(maxsize=32)
def imagem_lume(pose, quadro, largura, altura, espelho=False):
    nome = POSES[pose]
    im = _imagem(nome,quadro % total_quadros(nome),espelho)
    corpo = im.subsurface(im.get_bounding_rect(min_alpha=60))
    escala = min(largura/corpo.get_width(),altura/corpo.get_height())
    return pygame.transform.smoothscale(corpo,(round(corpo.get_width()*escala),round(corpo.get_height()*escala)))


def fracao_golpe(ataque):
    """Reserva o movimento mais rápido para a entrada na janela de contato real."""
    perfil,t = ataque.perfil,ataque.tempo
    if t < perfil.espera:
        return .35*t/perfil.espera
    if t < perfil.espera + perfil.ativo:
        return .35+.40*(t-perfil.espera)/perfil.ativo
    recuperacao = perfil.total-perfil.espera-perfil.ativo
    return min(1.,.75+.25*(t-perfil.espera-perfil.ativo)/recuperacao)


def animacao(lume, tempo, fagulha=None):
    pose = lume.pose
    passos = movimento_arte.deslocamento(lume,lume.rect.centerx,tempo,lume.face)
    ataque = lume.arma
    if lume.golpe > 0 and ataque.perfil and pose not in ("dano","corda"):
        nome = "mergulho" if ataque.tipo == "queda" else "subida" if ataque.tipo in SUBIDAS else "golpe"
        return nome,round(fracao_golpe(ataque)*(total_quadros(nome)-1)),ataque.face
    idade = tempo-fagulha.inicio if fagulha else -1
    if 0 <= idade < .19 and pose not in ("dano","corda"):
        face = 1 if fagulha.destino[0] >= fagulha.origem[0] else -1
        # O disparo parte no comando. A extensão vem cedo e a manga termina o gesto em seguida.
        t = idade/.19
        return "lancar",round((1-(1-t)**2)*59),face
    nome = POSES[pose]
    n = total_quadros(nome)
    if pose in ("andar","correr"):
        # A mesma fase atravessa o limiar de velocidade entre passo e corrida.
        fase = passos.distancia / 80
        return nome,floor(fase*n)%n,lume.face
    if pose == "clarao":
        fase = 1-lume.pulso/.55
    elif pose == "deslize":
        fase = 1-lume.slide/.62
    elif pose == "pulo":
        fase = 1+lume.vy/505
    elif pose == "queda":
        fase = lume.vy/430
    elif pose == "planar":
        fase = (1-cos(tempo*2*pi*.85))*.5
    else:
        ritmo = 1.1 if pose == "corda" else .78
        return nome,int(tempo*ritmo*n)%n,lume.face
    return nome,round(max(0.,min(1.,fase))*(n-1)),lume.face


def desenhar_lume(s, lume, x, pe, tempo, fagulha=None):
    nome,indice,face = animacao(lume,tempo,fagulha)
    espelho = face < 0
    im,farol = _quadro(nome,indice,espelho)
    caixa = im.get_rect(topleft=(round(x-TAMANHO[0]/2),round(pe-PE)))
    brilho(s,(caixa.x+farol[0],caixa.y+farol[1]),55)
    if nome in ("golpe","mergulho","subida") and lume.arma.tipo:
        from .arte_espinho import desenhar
        mx,my = _ponto(_juntas()["punho"][nome][indice],espelho)
        desenhar(s,lume,(caixa.x+mx,caixa.y+my),x,pe)
    if lume.iframes <= 0 or int(tempo*14)%3 != 1:
        if nome in ("voo","queda","planeio"):
            ombro = _ponto(_juntas()["ombro"][nome][indice],espelho)
            planeio = nome == "planeio"
            ritmo = 1.35 if planeio else 8 if lume.batida_asa>0 else 5.2
            asas = _imagem("asas-planeio" if planeio else "asas",int(tempo*ritmo*60)%60,espelho)
            pygame.blit(s,asas,(caixa.x+ombro[0]-48,caixa.y+ombro[1]-40))
        pygame.blit(s,im,caixa)
    return caixa
