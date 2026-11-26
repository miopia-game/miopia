"""O quadro da campanha e a área clicável percorrem as mesmas transformações."""
import pygame

from src import pygame_hd
from src.janela_hd import QUADRO, area_de_jogo


def test_canvas_rasteriza_uma_diagonal_em_pixels_fisicos():
    s = pygame_hd.Surface((10, 8))
    s.set_clip((1, 1, 7, 5))
    pygame_hd.draw.line(s, "white", (0, 0), (8, 5))
    assert s.pixels.get_size() == (20, 16)
    assert s.pixels.get_clip() == pygame.Rect(2, 2, 14, 10)
    # Ao cruzar um bloco de 2x2, uma reta nativa pode cobrir só parte do bloco.
    assert any(0 < sum(s.pixels.get_at((x+dx,y+dy)).r>0 for dx in (0,1) for dy in (0,1)) < 4
               for x in range(2,16,2) for y in range(2,12,2))


def test_janela_limita_imagem_e_preserva_proporcao():
    assert area_de_jogo(QUADRO) == pygame.Rect(0, 0, 1920, 1080)
    assert area_de_jogo((3840,2160)) == pygame.Rect(960,540,1920,1080)
    assert area_de_jogo((1280,800)) == pygame.Rect(0,40,1280,720)


def test_menu_recebe_clique_fisico_no_mesmo_alvo_da_arte(app):
    app.desenhar()
    assert app.quadro_renderizado is app.tela.pixels
    assert app.quadro_renderizado.get_size() == QUADRO
    alvo = app.alvos[0].center
    toque = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(2*alvo[0], 2*alvo[1]))
    evento = app.janela.evento_logico(toque)
    assert alvo == evento.pos
    app.evento(evento)
    assert app.estado != "menu"


def test_clique_na_barra_lateral_nao_avanca_prologo(app):
    app.iniciar("historia")
    assert app.estado == "prologo"
    estado = (app.estado, app.quadro, app.letras)
    app.evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(-1, 270)))
    assert (app.estado, app.quadro, app.letras) == estado
