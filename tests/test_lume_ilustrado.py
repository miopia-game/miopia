"""A pose, a iluminação e o apoio compartilham as âncoras da arte final."""

import pygame

from src import arte_lume
from src.travessia import Lume
from src.travessia_fagulha import Fagulha


def test_cache_preserva_a_luz_pintada_em_todos_os_quadros_e_nos_espelhos():
    for nome in set(arte_lume.POSES.values()) | {"mergulho","lancar"}:
        for indice in range(arte_lume.QUADROS):
            for espelho in (False, True):
                im,(x,y) = arte_lume._quadro(nome,indice,espelho)
                pixels = im.pixels
                xx, yy = round(2*x), round(2*y)
                vizinhanca = [pixels.get_at((xx+i,yy+j)) for i in range(-2,3) for j in range(-2,3)]
                assert any(r>209 and g>132 and b<135 and a>180 for r,g,b,a in vizinhanca)
                assert pixels.get_rect().contains(pixels.get_bounding_rect(min_alpha=80).inflate(2,2))
                if nome in ("guarda","passo","corrida","agachar","deslizar","golpe"):
                    assert abs(pixels.get_bounding_rect(min_alpha=90).bottom-2*arte_lume.PE) <= 1


def test_apoio_alterna_com_deslocamento_sem_mover_a_colisao():
    lume = Lume(100, 140)
    lume.vx = 210
    nome,primeiro,_ = arte_lume.animacao(lume, 0.)
    lume.rect.x += 14
    nome,segundo,_ = arte_lume.animacao(lume, .08)
    antes = lume.rect.copy()
    assert nome == "corrida" and primeiro != segundo
    im1,_ = arte_lume._quadro(nome,primeiro,False)
    im2,_ = arte_lume._quadro(nome,segundo,False)
    sola = pygame.Rect(40,122,110,12)
    assert pygame.image.tobytes(im1.pixels.subsurface(sola),"RGBA") != pygame.image.tobytes(im2.pixels.subsurface(sola),"RGBA")
    assert arte_lume.animacao(lume, .08)[1] == segundo and lume.rect == antes


def test_braco_encontra_a_janela_do_golpe_e_vira_para_o_lancamento():
    lume = Lume(100,140)
    lume.golpe = .1
    lume.arma.tipo = "pesado"
    perfil = lume.arma.perfil
    for tempo, faixa in ((0,range(3)),(perfil.espera,range(3,12)),(perfil.total-.001,range(12,16))):
        lume.arma.tempo = tempo
        assert arte_lume.animacao(lume,tempo)[1] in faixa
    lume.golpe = 0
    fagulha = Fagulha(1.,(100,100),(42,101))
    assert arte_lume.animacao(lume,1.,fagulha) == ("lancar",0,-1)
    assert arte_lume.animacao(lume,1.2,fagulha)[0] == "guarda"
