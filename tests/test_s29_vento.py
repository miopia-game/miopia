"""Travessia opcional de vento no Taquaral pelo fluxo da App."""
import pygame

from src.descoberta import conhecida
from src.ensaios import ENSAIOS
from src.fases import CHAO
from src.travessia import Jornada
from tests.test_s20_raiz import esperar_piso, ir, passo, tecla


def entrar(app):
    app.iniciar("historia")
    app.jogar()
    app.jogo.entrar(2)
    return app.jogo


def test_sementes_mostram_duas_direcoes_em_taquaral(app):
    j = entrar(app)
    j.recolocar((300, 333))
    app.desenhar()
    tela = pygame.display.get_surface()
    # O halo cobre o encontro das duas correntes. A semente é clara
    # e o risco ao lado parece uma haste, na direção do movimento.
    sementes = pygame.mask.from_threshold(tela, (203, 202, 146), (1, 1, 1))
    for rect in (pygame.Rect(226, 257, 90, 108), pygame.Rect(322, 261, 88, 106)):
        mascara = pygame.Mask(tela.get_size())
        faixa = pygame.Mask(rect.size, fill=True)
        mascara.draw(faixa, rect.topleft)
        assert sementes.overlap_area(mascara, (0, 0)) > 6
    assert j.camera_y == 0 and any(t.rect.collidepoint(300, CHAO) for t in j.solidos)


def subir_ao_beiral(app):
    j = app.jogo
    ir(app, 267)
    j.lume.energia = 0
    tecla(app, pygame.K_SPACE)
    for _ in range(160):
        passo(app, pygame.K_SPACE)
        if j.lume.rect.bottom < 209 and j.lume.planando:
            break
    assert j.lume.rect.bottom < 209 and j.lume.vy < -100
    for _ in range(39):
        passo(app, pygame.K_a, pygame.K_SPACE)
        if j.lume.rect.centerx < 190:
            break
    esperar_piso(app, 213)
    assert 113 < j.lume.rect.centerx < 213
    assert j.lume.rect.top > 154
    assert j.lume.energia == 0 and j.lume.vida == 100
    return j


def test_planeio_vai_do_chao_ao_beiral_com_os_controles_da_app(app):
    entrar(app)
    subir_ao_beiral(app)


def test_vento_exposto_so_arrasta_enquanto_as_asas_estao_abertas(app):
    j = entrar(app)
    j.recolocar((401, 310))
    j.lume.chao = False
    j.lume.vy = 76
    for _ in range(13):
        passo(app, pygame.K_SPACE)
    assert j.lume.rect.centerx > 425
    assert j.lume.planando
    fim = j.lume.rect.centerx
    for _ in range(9):
        passo(app)
    assert j.lume.rect.centerx == fim
    assert not j.lume.planando


def test_andar_no_chao_continua_possivel_sob_as_duas_correntes(app):
    j = entrar(app)
    for _ in range(104):
        passo(app, pygame.K_d)
        assert j.lume.chao and j.lume.rect.bottom == CHAO
    assert j.lume.rect.centerx > 520
    assert j.lume.vida == 100


def passar_sob_a_aba(app):
    l = app.jogo.lume
    # Sai do alto com Espaço retido e fecha as asas ao entrar na subida.
    for _ in range(70):
        passo(app, pygame.K_d, pygame.K_SPACE)
        if l.rect.centerx >= 257 and l.planando:
            break
    assert l.planando and l.rect.bottom < 230
    for _ in range(48):
        passo(app, pygame.K_d)
        if l.rect.bottom >= 282:
            break
    assert not l.planando and 332 < l.rect.centerx < 382
    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_d, pygame.K_SPACE)
    assert l.planando and l.vy > 0 and l.batida_asa == 0
    for _ in range(55):
        passo(app, pygame.K_SPACE)
        if l.chao:
            break
    assert l.chao and l.rect.bottom == 350
    return app.jogo


def test_da_borda_ao_pavio_soltar_e_retomar_espaco_abre_a_rota(app):
    j = entrar(app)
    assert not conhecida(j, 450, 342)
    subir_ao_beiral(app)
    j.lume.energia = 100
    passo(app)
    assert j.ensino_id == "aba_taquaral"
    passar_sob_a_aba(app)
    assert {"praticado_vento_taquaral", "praticado_aba_taquaral"} <= j.tutorial
    assert j.lume.vida == j.lume.energia == 100
    assert conhecida(j, 450, 342)
    assert j.proximo().id == "pavio_beiral"
    tecla(app, pygame.K_e)
    passo(app)
    assert j.bolsa.estoque["pavio"] == 1
    tecla(app, pygame.K_e)
    passo(app)
    assert j.bolsa.estoque["pavio"] == 1
    ir(app, 536)
    esperar_piso(app, CHAO)


def test_pavio_do_beiral_persiste_apos_morte_e_save_antigo_abre_a_rota(app):
    j = entrar(app)
    dados_antigos = j.salvar()
    dados_antigos["versao"] = 2
    assert any(o.id == "pavio_beiral" for o in Jornada.carregar(dados_antigos).objetos)
    subir_ao_beiral(app)
    passar_sob_a_aba(app)
    tecla(app, pygame.K_e)
    passo(app)
    assert "pavio_beiral" in j.flags
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and j.lume.rect.midbottom == j.checkpoint
    app.salvar_campanha()
    app.iniciar("historia", continuar=True)
    assert app.jogo.bolsa.estoque["pavio"] == 1
    assert all(o.id != "pavio_beiral" for o in app.jogo.objetos)


def test_sem_soltar_as_asas_passam_por_cima_da_aba(app):
    j = entrar(app)
    subir_ao_beiral(app)
    for _ in range(90):
        passo(app, pygame.K_d, pygame.K_SPACE)
        if j.lume.rect.centerx >= 416:
            break
    assert j.lume.rect.centerx >= 416
    assert j.lume.rect.bottom <= 226 and j.proximo() is None


def test_campo_de_testes_abre_repete_e_preserva_historia(app):
    app.iniciar("historia")
    app.jogar()
    app.salvar_campanha()
    campanha = app.mem.ler("campanha")
    i = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == "Beiral do Taquaral")
    app.menu()
    for _ in range(app.menu_nomes().index("Campo de testes")):
        tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    delta = i - app.selecao
    for _ in range(abs(delta)):
        tecla(app, pygame.K_DOWN if delta > 0 else pygame.K_UP)
    tecla(app, pygame.K_RETURN)
    assert app.ensaio == i
    j = app.jogo
    subir_ao_beiral(app)
    passar_sob_a_aba(app)
    tecla(app, pygame.K_e)
    passo(app)
    assert j.bolsa.estoque["pavio"] == 1
    tecla(app, pygame.K_ESCAPE)
    tecla(app, pygame.K_r)
    tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    assert app.jogo is not j and app.jogo.lume.rect.midbottom == ENSAIOS[i].pos
    assert app.jogo.bolsa.estoque["pavio"] == 0
    assert app.mem.ler("campanha") == campanha
