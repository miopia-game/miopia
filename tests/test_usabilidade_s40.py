"""Regressões de leitura do Bosque, da arena e da orientação vertical."""
import pygame

from src import avisos
from src.fases import FASES
from tests.test_s20_raiz import passo
from tests.test_s22_tutorial import iniciar


def test_primeira_dica_continua_disponivel_ate_praticar(app):
    j = iniciar(app)
    posicao = j.lume.rect.center
    for _ in range(450):
        passo(app)
    assert j.lume.rect.center == posicao
    assert 'praticado_primeiros_passos' not in j.tutorial
    assert avisos.conteudo(j)[0] == 'O primeiro caminho'
    passo(app, pygame.K_d, dt=.10)
    assert avisos.conteudo(j)[0] == 'Praticado'


def test_borda_do_primeiro_galho_aparece_fora_do_halo(app):
    j = iniciar(app)
    x, y, _ = FASES[0].plataformas[0]
    assert not j.visivel((x+16, y))
    app.desenhar()
    linha = (round(x+16-j.camera), round(y-j.camera_y))
    assert app.tela.get_at(linha)[:3] == (158, 143, 100)
    casca = (linha[0], linha[1]+6)
    com_casca = app.tela.get_at(casca)

    j.flags.add('valvula')
    app.desenhar()
    assert app.tela.get_at(linha)[:3] != (158, 143, 100)
    assert app.tela.get_at(casca) != com_casca


def test_nevoa_preserva_detalhe_do_fundo_e_esconde_o_terreno(app):
    from src.paisagem import aplicar_nevoa

    fundo = pygame.Surface((960, 540))
    pygame.draw.rect(fundo, (220, 220, 220), (120, 0, 7, 540))
    cena = pygame.Surface(fundo.get_size())
    cena.fill((255, 0, 0))
    luz = pygame.Surface(fundo.get_size())

    aplicar_nevoa(cena, luz, fundo=fundo)
    faixa = cena.get_at((123, 270))
    assert faixa.b >= 75
    assert cena.get_at((500, 270))[:3] == (0, 0, 0)


def textos_do_hud(monkeypatch):
    from src import paisagem

    escritos = []
    desenhar = paisagem.texto

    def registrar(s, msg, *args, **kwargs):
        escritos.append(msg)
        return desenhar(s, msg, *args, **kwargs)

    monkeypatch.setattr(paisagem, 'texto', registrar)
    return escritos


def test_clarao_antecipa_custo_letal_e_respeita_resina(app, monkeypatch):
    from tests.test_s20_raiz import tecla

    j = iniciar(app)
    j.lume.vida, j.lume.energia = 11., 10.
    escritos = textos_do_hud(monkeypatch)
    app.desenhar()
    assert 'K fatal · custa 12 de vida' in escritos

    j.bolsa.receber('resina', 1)
    passo(app)
    escritos.clear()
    app.desenhar()
    assert 'K custa 8 de vida' in escritos
    tecla(app, pygame.K_k)
    passo(app)
    assert j.lume.vida == 3. and j.lume.energia == 0.


def test_asa_distingue_avisos_e_brecha_no_hud_em_mudo(app, monkeypatch):
    from src.chefes import Encontro
    from src.fases import ARENA, CHAO
    from tests.test_s20_raiz import tecla

    j = iniciar(app)
    j.boss = e = Encontro(0, ARENA, CHAO)
    e.estado = 'aviso'
    tecla(app, pygame.K_F10)
    escritos = textos_do_hud(monkeypatch)
    app.desenhar()
    assert 'Abaixe-se · voo alto' in escritos

    escritos.clear()
    e.asa_rasteira = True
    app.desenhar()
    assert 'Salte · voo baixo' in escritos

    escritos.clear()
    e.estado = 'aberto'
    app.desenhar()
    assert 'Brecha · suba e ataque o dorso' in escritos


def test_mapa_destaca_acesso_vertical_mesmo_com_tutorial(app, monkeypatch):
    from src import telas
    from tests.test_s20_raiz import tecla

    iniciar(app)
    vistos = []
    desenhar = telas.texto

    def registrar(s, msg, *args, **kwargs):
        vistos.append(msg)
        return desenhar(s, msg, *args, **kwargs)

    monkeypatch.setattr(telas, 'texto', registrar)
    tecla(app, pygame.K_m)
    assert app.estado == 'diario'
    app.desenhar()
    assert 'Acesso · use E na base do cipó depois do galho de Véspera.' in vistos
    assert any('Siga pela direita' in linha for linha in vistos)


def test_raiz_do_corrego_mostra_agua_logo_apos_restaurar_e_ao_recarregar(app):
    from src.corrego_historia import desenhar_agua
    from src.fases import CHAO, RAIZ
    from tests.test_s20_raiz import tecla

    j = iniciar(app)
    j.entrar(1)
    j.flags.update(('dreno', 'lingueta', 'ponte', 'ralo', 'chefe'))
    j.flags.update(f'gota_{n}' for n in range(3))
    j.recolocar((RAIZ-30, CHAO))
    cx = j.fase.width-960
    ponto = RAIZ-cx-64, CHAO+13

    def cor_da_corrente(jornada):
        s = pygame.Surface((960, 540))
        desenhar_agua(s, jornada, cx)
        return s.get_at(ponto)[:3]

    cor_seca = cor_da_corrente(j)
    tecla(app, pygame.K_e)
    passo(app)
    assert 'raiz' in j.flags and j.restauradas == 1
    cor_molhada = cor_da_corrente(j)
    assert cor_molhada != cor_seca
    app.menu()
    tecla(app, pygame.K_RETURN)
    assert 'raiz' in app.jogo.flags
    assert cor_da_corrente(app.jogo) == cor_molhada
