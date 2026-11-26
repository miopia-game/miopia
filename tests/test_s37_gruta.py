"""Câmara da Escuta pela entrada, pelo fundo e de volta à grade."""
import pygame

from src import aula_sino
from src.cartografia import mapa_local
from src.descoberta import conhecida
from src.orientacao import objetivo_atual
from tests.test_s20_raiz import passo, tecla
from tests.test_s31_historia import CampanhaPelaApp, iniciar


def preparar(app):
    j = iniciar(app)
    j.entrar(3)
    j.flags.update(("roldana", "contrapeso", "meio"))
    app.salvar_campanha()
    app.menu()
    tecla(app, pygame.K_RETURN)
    return CampanhaPelaApp(app)


def test_travessia_pelo_fundo_e_volta_pela_passarela(app):
    p = preparar(app)
    p.descer_camara()
    p.usar()
    assert "eco_antigo" in p.jogo.flags
    p.fundo_camara()
    p.subir_camara()
    assert p.jogo.proximo().id == "passarela_escuta"
    p.usar()
    assert "passarela_escuta" in p.jogo.flags
    assert "porta" in p.jogo.eventos
    p.ir(2530)
    assert p.lume.rect.bottom == 469
    p.usar()
    assert "sino" in p.jogo.eventos
    p.lume.vida = 0.
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.5)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and p.lume.rect.midbottom == p.jogo.checkpoint
    assert {"eco_antigo", "passarela_escuta"} <= p.jogo.flags
    app.menu()
    tecla(app, pygame.K_RETURN)
    assert {"eco_antigo", "passarela_escuta"} <= app.jogo.flags


def test_mapa_distingue_degrau_iluminado_do_piso_pisado(app):
    p = preparar(app)
    assert objetivo_atual(p.jogo).id == "grade_escuta"
    p.descer_camara()
    assert p.jogo.camera_y > 90
    assert not conhecida(p.jogo, aula_sino.SAIDA[0], aula_sino.SAIDA[1]-34)
    p.usar()
    p.tick(clarao=True)
    p.esperar(34)
    j = p.jogo
    assert conhecida(j, 2762, 628)
    assert (j.volta, 2762 // 24, 628) not in j.pisadas_escuta
    recorte = pygame.Rect(2688, 602, 168, 70)
    planta = pygame.Surface(recorte.size)
    mapa_local(planta, j, planta.get_rect(), janela_mundo=recorte)
    centro_celula = (2762 // 24) * 24 + 12
    ponto = (centro_celula-recorte.x, 626-recorte.y)
    assert planta.get_at(ponto)[:3] != aula_sino.COR_PISADA
    p.fundo_camara()
    assert j.camera_y > 190
    assert any(y == aula_sino.FUNDO for _, _, y in j.pisadas_escuta)
    p.subir_camara()
    assert (j.volta, 2762 // 24, 628) in j.pisadas_escuta
    mapa_local(planta, j, planta.get_rect(), janela_mundo=recorte)
    assert planta.get_at(ponto)[:3] == aula_sino.COR_PISADA
    anteriores = j.pisadas_escuta.copy()
    tecla(app, pygame.K_m)
    tecla(app, pygame.K_EQUALS)
    tecla(app, pygame.K_d)
    app.desenhar()
    assert j.pisadas_escuta == anteriores
    assert app.tela.get_size() == (960, 540)
    app.menu()
    tecla(app, pygame.K_RETURN)
    assert app.jogo.pisadas_escuta == anteriores
