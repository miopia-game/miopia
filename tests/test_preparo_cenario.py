"""Uma entrada fria precisa chegar ao primeiro quadro com a pintura pesada pronta."""
from pathlib import Path

import pygame

from src import arte_corte, paisagem
from src.ilustracao import imagem, original
from src.main import App
from src.ensaios import ENSAIOS
from src.travessia import Jornada


def test_encontros_nao_reabrem_atlas_e_panoramas_no_primeiro_quadro(monkeypatch):
    for cache in (paisagem.fundo, arte_corte.camadas, imagem, original):
        cache.cache_clear()
    app = App(temporaria=True)
    lidos = []
    carregar = pygame.image.load

    def observar(arquivo, *args, **kwargs):
        lidos.append(Path(arquivo).name)
        return carregar(arquivo, *args, **kwargs)

    monkeypatch.setattr(pygame.image, "load", observar)
    durante = set()
    try:
        for etapa in (0, 1, 2, 3, 0):
            app.jogo = Jornada(etapa=etapa)
            app.jogo.campo_testes = True
            app.jogar()
            lidos.clear()
            app.desenhar()
            durante.update(lidos)
        for nome in ("Asa Fendida", "Jardim do Último Sinal"):
            app.comecar_ensaio(next(i for i, e in enumerate(ENSAIOS) if e.nome == nome))
            lidos.clear()
            app.desenhar()
            durante.update(lidos)
    finally:
        app.mem.db.close()
        app.janela.fechar()
        pygame.quit()
    caros = {"galhos_atlas.png", "objetos_atlas.png", "hud_miopia_atlas.png",
             "passagem_raizes.png", "corte_da_figueira.jpg",
             *(nome + ".jpg" for nome in paisagem.PANORAMAS)}
    assert durante.isdisjoint(caros), durante & caros


def test_compor_clarao_indexado_nas_bordas(app, monkeypatch):
    from src import pygame_hd as hd, visao

    jogo = Jornada(etapa=3)
    fontes = ((-50, -30, 520), (880, 468, 376), (1070, 60, 168))
    monkeypatch.setattr(visao, "fontes", lambda j, vestigios: fontes)
    luz = hd.Surface((960, 540))
    esperado = hd.Surface(luz.get_size())
    clip = pygame.Rect(13, 23, 904, 481)
    for tela in (luz, esperado):
        tela.fill((17, 17, 17))
        tela.set_clip(clip)
    paisagem.compor_luz(luz, jogo, 0, 0, 1, minimo=17)
    for x, y, raio in fontes:
        mascara = paisagem.mascara_luz(raio, 1).pixels
        assert mascara.get_bitsize() == 8
        rgb = hd.nativa(mascara.convert(esperado.pixels), (raio*2, raio*2))
        esperado.blit(rgb, (x-raio, y-raio), special_flags=pygame.BLEND_RGB_MAX)
    assert pygame.image.tobytes(luz.pixels, "RGB") == pygame.image.tobytes(esperado.pixels, "RGB")
