"""Avisos dos chefes conservam uma voz mesmo com os efeitos ocupados."""
import pygame
import pytest

from src.ensaios import ENSAIOS


@pytest.mark.parametrize('saturado', [False, True])
def test_ultimo_chamado_reproduz_aviso_e_atenua_a_musica(app, saturado):
    indice = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == 'Último chamado')
    app.comecar_ensaio(indice)
    assert app.audio.atual == 'chefe_final'
    j = app.jogo
    j.boss.x = j.lume.rect.centerx + 100
    j.boss.tempo = .001
    efeito = app.audio.fx['impacto']
    if saturado:
        for canal in range(12, 28):
            pygame.mixer.Channel(canal).play(efeito, loops=-1)

    volume = pygame.mixer.music.get_volume()
    app.atualizar(1/60)
    assert 'aviso' in j.eventos
    voz = pygame.mixer.Channel(5 if saturado else 12)
    assert voz.get_sound() is app.audio.fx['coruja_eco']
    assert app.audio.silencio > 0 and pygame.mixer.music.get_volume() < volume

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F10))
    for evento in pygame.event.get():
        app.evento(evento)
    assert app.audio.mudo and pygame.mixer.music.get_volume() == 0
    assert not voz.get_busy()
