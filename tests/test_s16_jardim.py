"""O diário guia a travessia física do retorno do Jardim já plantado."""
import pygame

from src.ensaios import ENSAIOS
from src.orientacao import objetivo_atual
from src.travessia import Jornada


def tecla(app, key):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))
    for evento in pygame.event.get():
        app.evento(evento)


def test_plantar_orienta_para_a_passagem_ocidental_e_aceita_retorno(app):
    indice = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == 'Jardim do Último Sinal')
    app.comecar_ensaio(indice)
    j = app.jogo
    # Preparar a última tarefa sem coletar os dois segredos do circuito.
    j.cartografia.update(('jardim_orvalho', 'jardim_comporta', 'jardim_brotos', 'jardim_calha'))
    j.recolocar((3020, 1828))
    assert objetivo_atual(j).id == 'jardim_plantar'
    tecla(app, pygame.K_e)
    app.atualizar(1/60)
    assert 'jardim_plantado' in j.cartografia

    tecla(app, pygame.K_m)
    assert app.estado == 'diario'
    alvo = objetivo_atual(j)
    assert alvo.id == 'retorno_jardim' and alvo.x < 2432 < j.lume.rect.centerx
    assert 'à esquerda' in alvo.texto
    tecla(app, pygame.K_m)

    app.jogo = j = Jornada.carregar(j.salvar())
    assert j.lume.rect.midbottom == (2510, 790)
    descida = objetivo_atual(j)
    assert descida.id == 'vao_retorno_jardim' and 2800 < descida.x < 2950
    assert 'jardim_memoria' not in j.cartografia and not j.bolsa.estoque['lente']
    assert j.bolsa.estoque['pavio'] == 2

    j.lume.iframes = 999
    teclas = dict.fromkeys((pygame.K_RIGHT, pygame.K_d, pygame.K_LEFT, pygame.K_a,
             pygame.K_s, pygame.K_DOWN, pygame.K_SPACE, pygame.K_LSHIFT, pygame.K_RSHIFT,
             pygame.K_LCTRL, pygame.K_RCTRL), False)
    for _ in range(300):
        teclas[pygame.K_d] = j.lume.rect.centerx < descida.x
        app.atualizar(1/60, presso=teclas)
        if j.lume.rect.bottom >= 1828:
            break
    assert j.lume.rect.bottom == 1828 and objetivo_atual(j).id == 'retorno_jardim'
    teclas[pygame.K_d] = False
    teclas[pygame.K_a] = True
    for _ in range(300):
        app.atualizar(1/60, presso=teclas)
        if j.lume.rect.centerx < 2340:
            break
    assert j.em_vertical and j.lume.rect.centerx < 2340
    assert objetivo_atual(j).id != 'retorno_jardim'
