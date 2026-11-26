"""O tutorial da História ensina e reage às ações reais do primeiro trecho."""
import pygame

from src import avisos
from src.fases import CHAO
from tests.test_s20_raiz import passo, tecla


def iniciar(app):
    tecla(app, pygame.K_RETURN)
    assert app.estado == 'prologo'
    tecla(app, pygame.K_ESCAPE)
    assert app.estado == 'jogo'
    passo(app)
    return app.jogo


def esperar_licao(app, ident):
    for _ in range(420):
        if app.jogo.ensino_id == ident:
            return
        passo(app)
    raise AssertionError(f'Lição {ident} não apareceu')


def test_historia_ensina_andar_e_pular_automaticamente(app):
    j = iniciar(app)
    assert j.ensino_id == 'primeiros_passos' and 'A / D' in j.ensino_texto
    assert 'Espaço' not in j.ensino_texto
    x = j.lume.rect.centerx
    for _ in range(30):
        passo(app, pygame.K_d)
        if j.lume.rect.centerx >= x+39:
            break
    assert j.lume.rect.centerx >= x+39
    assert 'praticado_primeiros_passos' in j.tutorial
    assert avisos.conteudo(j)[0] == 'Praticado'
    esperar_licao(app, 'salto')
    assert 'Espaço' in j.ensino_texto
    assert 'praticado_salto' not in j.tutorial
    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_SPACE)
    assert j.lume.rect.bottom < CHAO and app.estado == 'jogo'
    assert 'praticado_salto' in j.tutorial

    app.salvar_campanha()
    app.iniciar('historia', continuar=True)
    assert {'praticado_primeiros_passos','praticado_salto'} <= app.jogo.tutorial


def test_salto_duplo_so_conta_na_segunda_batida(app):
    j = iniciar(app)
    j.recolocar((292, CHAO))
    esperar_licao(app, 'salto_duplo')
    tecla(app, pygame.K_SPACE)
    for _ in range(16):
        passo(app, pygame.K_SPACE)
    assert 'praticado_salto_duplo' not in j.tutorial
    passo(app)
    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_SPACE)
    assert 'praticado_salto_duplo' in j.tutorial and not j.lume.asa_disponivel


def test_licao_da_bolsa_respeita_o_efeito_e_mantem_o_item_se_cheio(app):
    j = iniciar(app)
    j.recolocar((540, CHAO))
    j.tutorial.add('salto_duplo')  # Examina o trecho seguinte, com a lição anterior já vista.
    esperar_licao(app, 'bolsa')
    assert 'Q' in j.ensino_texto and 'F' in j.ensino_texto
    estoque = j.bolsa.quantidade
    tecla(app, pygame.K_f)
    assert j.bolsa.quantidade == estoque and 'praticado_bolsa' not in j.tutorial
    j.lume.energia = 65
    tecla(app, pygame.K_f)
    assert j.bolsa.quantidade == estoque-1 and j.lume.energia == 100
    assert 'praticado_bolsa' in j.tutorial


def test_diario_tem_consulta_de_controles_sem_sair_da_historia(app, monkeypatch):
    j = iniciar(app)
    escritos = []
    from src import telas
    original = telas.texto
    def registrar(s, msg, *args, **kwargs):
        escritos.append(msg)
        return original(s, msg, *args, **kwargs)
    monkeypatch.setattr(telas, 'texto', registrar)

    tecla(app, pygame.K_m)
    assert app.estado == 'diario'
    tempo = j.tempo
    tecla(app, pygame.K_LEFT)
    app.desenhar()
    assert 'Controles' in escritos and 'Q   /   F' in escritos
    assert any('Agulha' in texto for texto in escritos)
    tecla(app, pygame.K_m)
    assert app.estado == 'jogo' and app.jogo is j and j.tempo == tempo


def test_mapa_e_clarao_confirmam_a_acao_no_bosque(app):
    j = iniciar(app)
    j.recolocar((945, CHAO))
    esperar_licao(app, 'mapa')
    tecla(app, pygame.K_m)
    assert app.estado == 'diario' and 'praticado_mapa' in j.tutorial
    tecla(app, pygame.K_m)

    j.recolocar((1500, CHAO))
    esperar_licao(app, 'luz_combate')
    antes = j.lume.energia
    tecla(app, pygame.K_k)
    passo(app)
    assert j.lume.energia == antes-22 and 'praticado_luz_combate' in j.tutorial


def test_deslize_e_planagem_contam_quando_a_fisica_executa(app):
    j = iniciar(app)
    j.recolocar((1090, CHAO))
    esperar_licao(app, 'deslize')
    tecla(app, pygame.K_LSHIFT)
    passo(app, pygame.K_LSHIFT)
    assert 'praticado_deslize' not in j.tutorial
    tecla(app, pygame.K_LSHIFT)
    passo(app, pygame.K_LSHIFT, pygame.K_d)
    assert j.lume.slide>0 and 'praticado_deslize' in j.tutorial

    j.recolocar((1320, CHAO))
    esperar_licao(app, 'planagem')
    tecla(app, pygame.K_SPACE)
    for _ in range(70):
        passo(app, pygame.K_SPACE)
        if j.lume.planando:
            break
    assert j.lume.planando and 'praticado_planagem' in j.tutorial


def test_interacao_conta_quando_o_morador_responde(app):
    j = iniciar(app)
    j.tutorial.add('salto')
    j.recolocar((217, CHAO))
    esperar_licao(app, 'interacao')
    tecla(app, pygame.K_e)
    passo(app)
    assert j.dialogo[0] == 'Nira' and 'praticado_interacao' in j.tutorial
