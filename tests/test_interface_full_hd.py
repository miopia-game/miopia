"""Pixels físicos do atlas e das fontes nas dimensões de exibição da interface."""
import pygame

from src import ilustracao, pygame_hd


def test_asa_do_hud_e_amostrada_do_atlas_no_tamanho_final(app):
    original = ilustracao.original("hud_asa.png")
    largura, altura = 35, 29
    icon = ilustracao.imagem("hud_asa.png", largura, altura)
    esperado = pygame.transform.smoothscale(original, (70, 58))
    assert icon.get_size() == (largura, altura)
    assert icon.pixels.get_size() == esperado.get_size()
    assert pygame.image.tobytes(icon.pixels, "RGBA") == pygame.image.tobytes(esperado, "RGBA")


def test_texto_125_mantem_ancora_e_rasteriza_contorno_em_full_hd(app):
    tela = pygame_hd.Surface((180, 62), pygame.SRCALPHA)
    cor = (232, 231, 210)
    with ilustracao.estilo(dict(texto=125)):
        caixa = ilustracao.texto(tela, "Fagulha", 91, 9, 17, cor, "forte", "centerx")
        tamanho = ilustracao.tamanho_texto(17)
    antiga = ilustracao.fonte(tamanho, "forte").render("Fagulha", True, cor)
    assert caixa.centerx == 91 and caixa.top == 9 and caixa.size == antiga.get_size()
    recorte = tela.pixels.subsurface((caixa.x*2, caixa.y*2, caixa.w*2, caixa.h*2))
    ampliada = pygame.transform.scale(antiga, recorte.get_size())
    assert pygame.image.tobytes(recorte, "RGBA") != pygame.image.tobytes(ampliada, "RGBA")
    assert recorte.get_bounding_rect().w > caixa.w
