"""O atlas deve chegar ao pixel físico do galho no mesmo recorte usado na partida."""
import pygame

from src import arte_ilustrada, pygame_hd
from src.fases import Terreno
from src.ilustracao import original


def test_galho_retem_pintura_do_atlas_na_densidade_final(app):
    pixels = pygame.Surface((1920, 1080), pygame.SRCALPHA)
    tela = pygame_hd.nativa(pixels, (960, 540))
    apoio = Terreno(pygame.Rect(481, 312, 174, 12), "plataforma")
    camera = 100
    arte_ilustrada.terreno(tela, apoio, camera)
    # O alvo já tem a densidade da janela antes do primeiro blit.
    largura, altura = 178, 52
    fonte = original("pintado_galho.png")
    detalhe = pygame.transform.flip(pygame.transform.smoothscale(fonte, (2*largura, 2*altura)), True, False)
    posicao = ((apoio.rect.x-camera-2)*2, (apoio.rect.y-3)*2)
    esperado = pygame.Surface(detalhe.get_size(), pygame.SRCALPHA)
    esperado.blit(detalhe, (0, 0))
    recorte = pixels.subsurface(pygame.Rect(posicao, detalhe.get_size()))
    assert pygame.image.tobytes(recorte, "RGBA") == pygame.image.tobytes(esperado, "RGBA")
    base = pygame.transform.flip(pygame.transform.smoothscale(fonte, (largura, altura)), True, False)
    ampliado = pygame.transform.smoothscale(base, detalhe.get_size())
    assert pygame.image.tobytes(detalhe, "RGBA") != pygame.image.tobytes(ampliado, "RGBA")
