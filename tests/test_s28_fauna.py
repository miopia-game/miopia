"""As rotinas da ponte disputam a flor e dão uma abertura de travessia."""
import pygame

from src.arte_combate import corpo
from src.ensaios import ENSAIOS
from src.travessia import Jornada
from src.visao import fontes
from tests.test_s20_raiz import esperar_piso, ir, passo, tecla
from tests.test_s21_arquivo import fechar_fala


def ponte(app):
    i = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == "Jardim do Último Sinal")
    app.comecar_ensaio(i)
    j = app.jogo
    cobra = next(e for e in j.inimigos if e.origem == (2720, 790))
    vespa = next(e for e in j.inimigos if e.origem == (2870, 680))
    return j, cobra, vespa


def esperar(app, predicado, quadros=360):
    for _ in range(quadros):
        passo(app)
        if predicado():
            return
    raise AssertionError("A rotina não chegou ao estado esperado.")


def test_vespa_desce_a_flor_e_cobra_da_bote_no_ponto_que_avistou(app):
    j, cobra, vespa = ponte(app)
    x0 = vespa.rect.centerx
    assert j.lume.rect.midbottom == (2510, 790)
    esperar(app, lambda: cobra.estado == "aviso_caca")
    assert vespa.estado == "nectar" and vespa.rect.centerx < x0-90
    mira = tuple(cobra.alvo)
    esperar(app, lambda: vespa.estado == "fuga")
    esperar(app, lambda: cobra.estado == "bote_caca")
    assert tuple(cobra.alvo) == mira and vespa.rect.centery < mira[1]
    esperar(app, lambda: cobra.estado == "recuo_caca")
    esperar(app, lambda: vespa.estado == "nectar")
    esperar(app, lambda: cobra.estado == "aviso_caca")
    assert j.lume.vida == 100 and cobra.vida == cobra.max_vida and vespa.vida == vespa.max_vida


def test_k_deixa_isca_fixa_e_abre_passagem_acima_da_cobra(app):
    j, cobra, vespa = ponte(app)
    tecla(app, pygame.K_k)
    esperar(app, lambda: vespa.estado == "isca")
    alvo = tuple(vespa.alvo_isca)
    assert alvo[0] == j.vestigios[-1].x
    espera = vespa.rect.centerx
    for _ in range(28):
        passo(app, pygame.K_d)
        assert tuple(vespa.alvo_isca) == alvo
    assert vespa.rect.centerx < espera-70 and j.lume.rect.centerx > alvo[0]+70
    tecla(app, pygame.K_SPACE)
    for _ in range(24):
        passo(app, pygame.K_d, pygame.K_SPACE)
    esperar_piso(app, 694)
    ir(app, 2778)
    tecla(app, pygame.K_SPACE)
    for _ in range(40):
        passo(app, pygame.K_d, pygame.K_SPACE)
    esperar_piso(app, 598)
    assert j.lume.rect.centerx >= 2860 and j.lume.vida == 100
    assert cobra.ativo and vespa.ativo


def test_lume_percebido_recebe_aviso_de_ataque_e_morte_restaura_rotina(app):
    j, cobra, vespa = ponte(app)
    for _ in range(80):
        passo(app, pygame.K_d)
        if cobra.estado == "aviso":
            break
    assert cobra.estado == "aviso"
    assert cobra.sequencia > 0
    assert any(nome.startswith("aviso_cobra_") for nome, _ in j.sons_espaciais)
    esperar(app, lambda: j.lume.vida < 100)
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo"
    bichos = {e.origem[0]: (e.estado, e.rect.midbottom, e.vida, e.max_vida)
              for e in app.jogo.inimigos if e.origem[0] in (2720, 2870)}
    assert bichos[2720][0:2] == ("espreita", (2720, 790))
    assert bichos[2870][0:2] == ("nectar", (2870, 680))
    assert all(vida == total for _, _, vida, total in bichos.values())


def test_save_anterior_preserva_derrota_e_vespa_volta_a_flor_sozinha(app):
    j, _, _ = ponte(app)
    dados = j.salvar()
    dados["corte"]["memoria"].append("vigia_2720")
    novo = Jornada.carregar(dados)
    assert not any(e.origem[0] == 2720 for e in novo.inimigos)
    e = next(e for e in novo.inimigos if e.origem[0] == 2870)
    for _ in range(150):
        novo.update(1/60)
    assert e.estado == "nectar" and e.rect.centerx < 2770


def test_mesmo_clarao_nao_reinicia_a_isca_quando_a_vespa_volta(app):
    j, _, vespa = ponte(app)
    tecla(app, pygame.K_k)
    esperar(app, lambda: vespa.estado == "isca")
    inicio = vespa.ultima_isca
    esperar(app, lambda: vespa.estado == "nectar")
    assert j.vestigios and j.vestigios[-1].inicio == inicio
    for _ in range(180):
        passo(app)
        assert vespa.estado != "isca"


def test_tres_posturas_de_cobra_e_vespa_tem_formas_distintas(app):
    _, cobra, vespa = ponte(app)
    tecla(app, pygame.K_F10)
    assert app.audio.mudo
    area = pygame.Surface((160, 110), pygame.SRCALPHA)
    for e, estados in ((cobra, ("aviso_caca", "bote_caca", "recuo_caca")),
                       (vespa, ("aviso", "investida", "recuo"))):
        e.rect.midbottom = (80, 84)
        e.t = .2
        e.tecnica = "mergulho" if e.tipo == "vespa" else "rasteira"
        quadros = []
        for estado in estados:
            area.fill((0, 0, 0, 0))
            e.estado = estado
            corpo(area, e, 0, 0.)
            quadros.append(area.get_bounding_rect(1).size)
        assert len(set(quadros)) == 3


def test_pista_de_aru_pode_ser_lida_em_chao_firme(app):
    j, _, vespa = ponte(app)
    ir(app, 2572)
    assert j.lume.chao and j.proximo().id == "jardim_placa_nectar"
    tecla(app, pygame.K_e)
    passo(app)
    assert j.dialogo[0] == "A flor da ponte" and "clarão" in j.dialogo[1]
    fechar_fala(app)
    assert j.lume.vida == 100 and sum(t == "A flor da ponte" for t, _ in j.diario) == 1
    esperar(app, lambda: vespa.estado == "nectar" and vespa.rect.centerx-j.lume.rect.centerx < 191)
    vida = vespa.vida
    tecla(app, pygame.K_k)
    esperar(app, lambda: vespa.estado == "isca", 48)
    assert vespa.vida == vida


def test_clarao_de_perto_continua_acertando_a_vespa(app):
    j, _, vespa = ponte(app)
    j.recolocar((2740, 790))
    vida = vespa.vida
    tecla(app, pygame.K_k)
    passo(app)
    assert vespa.vida < vida and vespa.estado == "atordoado"


def test_flor_ilumina_enquanto_esta_na_camera_acima_e_abaixo_da_ponte(app):
    j, _, _ = ponte(app)
    j.recolocar((2730, 472))
    j.camera_y = 240.
    assert (2740, 758, 108) in fontes(j)
    j.camera_y = 930.
    assert (2740, 758, 108) not in fontes(j)
