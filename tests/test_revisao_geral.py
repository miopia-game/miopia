"""Ações novas pelo caminho de entrada da App."""
import pygame

from src.abertura_bosque import BROTO
from tests.test_s20_raiz import passo, tecla
from tests.test_s22_tutorial import iniciar
from tests.test_s31_historia import CampanhaPelaApp


def test_clarao_abre_apoio_temporario_para_o_pacote_de_mimo(app):
    j = iniciar(app)
    piloto = CampanhaPelaApp(app)
    piloto.ir(255)
    piloto.ir(380, pular=True)
    assert BROTO not in j.solidos
    tecla(app, pygame.K_k)
    piloto.esperar(15)
    assert BROTO in j.solidos
    piloto.ir(280, pular=True)
    assert j.lume.rect.bottom == BROTO.rect.top
    piloto.ir(374, pular=True)
    piloto.usar()
    assert 'encomenda_recolhida' in j.flags
    piloto.esperar(330)
    assert BROTO not in j.solidos


def test_clarao_com_baixo_freia_queda_e_gasta_brilho(app):
    j = iniciar(app)
    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_SPACE)
    for _ in range(100):
        if not j.lume.chao and j.lume.vy > 135:
            break
        passo(app)
    velocidade, brilho = j.lume.vy, j.lume.energia
    tecla(app, pygame.K_k)
    passo(app, pygame.K_s)
    assert 'freio_luz' in j.eventos
    assert j.lume.vy < velocidade
    assert j.lume.energia == brilho - j.lume.custo_clarao
