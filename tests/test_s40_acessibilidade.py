"""Entrada pela App e apresentação de acessibilidade do S40."""
import pygame

from src import ilustracao
from src.controles import carregar
from src.memoria import Memoria
from src.paisagem import compor_luz
from src.visao import Vestigio
from tests.test_s20_raiz import passo, tecla
from tests.test_s31_historia import iniciar


def escolher(app, indice):
    for _ in range(indice):
        tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)


def test_remapeamento_pela_pausa_chega_ao_salto_e_as_dicas(app):
    j = iniciar(app)
    tecla(app, pygame.K_ESCAPE)
    escolher(app, 2)
    escolher(app, 5)
    assert app.estado == "controles"
    escolher(app, 3)  # Saltar
    tecla(app, pygame.K_j)
    assert app.capturando_tecla and "ocupada" in app.aviso_tecla
    tecla(app, pygame.K_x)
    assert not app.capturando_tecla
    assert app.mem.ler("preferencias")["teclas"]["salto"] == pygame.K_x
    assert app.controles.dicas("Segure Espaço ao cair.") == "Segure X ao cair."
    tecla(app, pygame.K_ESCAPE)
    tecla(app, pygame.K_ESCAPE)
    tecla(app, pygame.K_ESCAPE)
    assert app.estado == "jogo"
    tecla(app, pygame.K_SPACE)
    passo(app)
    assert j.lume.chao
    tecla(app, pygame.K_x)
    passo(app, pygame.K_x)
    assert not j.lume.chao and j.lume.vy < 0


def controle(app, tipo, **dados):
    pygame.event.post(pygame.event.Event(tipo, which=21, **dados))
    for evento in pygame.event.get():
        app.evento(evento)


def botao(app, botao, pressionar=True):
    tipo = pygame.CONTROLLERBUTTONDOWN if pressionar else pygame.CONTROLLERBUTTONUP
    controle(app, tipo, button=botao)


def test_controle_navega_e_desconectar_solta_o_movimento(app):
    botao(app, pygame.CONTROLLER_BUTTON_A)
    assert app.estado == "prologo"
    botao(app, pygame.CONTROLLER_BUTTON_B)
    assert app.estado == "jogo"
    j = app.jogo
    x = j.lume.rect.centerx
    controle(app, pygame.CONTROLLERAXISMOTION, axis=pygame.CONTROLLER_AXIS_LEFTX, value=28000)
    for _ in range(18):
        passo(app)
    assert j.lume.rect.centerx > x+20
    controle(app, pygame.CONTROLLERDEVICEREMOVED)
    for _ in range(18):
        passo(app)
    assert abs(j.lume.vx) < 1


def test_clarao_e_mapa_remapeados_preservam_o_progresso_e_o_tab(app, tmp_path, monkeypatch):
    monkeypatch.setenv("MIOPIA_DADOS", str(tmp_path))
    j = iniciar(app)
    tecla(app, pygame.K_ESCAPE)
    escolher(app, 2)
    escolher(app, 5)
    escolher(app, 7)  # Clarão
    tecla(app, pygame.K_u)
    for _ in range(3):
        tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    tecla(app, pygame.K_w)
    for _ in range(3):
        tecla(app, pygame.K_ESCAPE)
    energia = j.lume.energia
    tecla(app, pygame.K_k)
    passo(app)
    assert j.lume.energia == energia
    tecla(app, pygame.K_u)
    passo(app)
    assert j.lume.energia == energia - 22 and j.vestigios
    tecla(app, pygame.K_w)
    assert app.estado == "diario"
    tecla(app, pygame.K_w)
    assert app.estado == "jogo"
    tecla(app, pygame.K_TAB)
    assert app.estado == "diario"

    gravada = Memoria()
    try:
        gravada.guardar("preferencias", app.mem.prefs)
        gravada.guardar("campanha", {"etapa": 1})
    finally:
        gravada.db.close()
    reaberta = Memoria()
    try:
        assert reaberta.prefs["teclas"] == {"luz": pygame.K_u, "mapa": pygame.K_w}
        assert reaberta.ler("campanha") == {"etapa": 1}
    finally:
        reaberta.db.close()
    assert carregar({"luz": pygame.K_j, "golpe": pygame.K_v, "arma": pygame.K_ESCAPE}) == {}


def test_controle_salta_interage_abre_pedidos_e_pausa(app):
    j = iniciar(app)
    botao(app, pygame.CONTROLLER_BUTTON_A)
    passo(app)
    assert j.lume.vy < 0
    botao(app, pygame.CONTROLLER_BUTTON_A, False)
    for _ in range(60):
        passo(app)
    j.recolocar((224, 442))
    controle(app, pygame.CONTROLLERAXISMOTION, axis=pygame.CONTROLLER_AXIS_TRIGGERRIGHT, value=27000)
    passo(app)
    assert j.dialogo and j.dialogo[0] == "Nira"
    for _ in range(10):
        if not j.dialogo:
            break
        botao(app, pygame.CONTROLLER_BUTTON_A)
        botao(app, pygame.CONTROLLER_BUTTON_A, False)
    assert not j.dialogo
    botao(app, pygame.CONTROLLER_BUTTON_BACK)
    assert app.estado == "diario"
    botao(app, pygame.CONTROLLER_BUTTON_DPAD_RIGHT)
    assert app.pagina == 1
    botao(app, pygame.CONTROLLER_BUTTON_A)
    assert app.pagina == 0
    botao(app, pygame.CONTROLLER_BUTTON_BACK)
    assert app.estado == "jogo"
    botao(app, pygame.CONTROLLER_BUTTON_START)
    assert app.estado == "pausa"


def test_escala_e_contraste_sao_configuraveis_e_alteram_a_leitura(app):
    escolher(app, app.menu_nomes().index("Ajustes"))
    escolher(app, 6)
    assert app.estado == "acessibilidade"
    tecla(app, pygame.K_RIGHT)
    tecla(app, pygame.K_RIGHT)
    tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RIGHT)
    p = app.mem.ler("preferencias")
    assert p["texto"] == 125 and p["contraste"]
    s = pygame.Surface((240, 78))
    normal = ilustracao.texto(s, "Texto em prova", 0, 0, 16)
    with ilustracao.estilo(p):
        grande = ilustracao.texto(s, "Texto em prova", 0, 0, 16)
        assert ilustracao.alto_contraste()
    assert grande.width > normal.width and grande.height > normal.height
    app.desenhar()


def test_clarao_suave_reduz_pico_visual_com_mesmo_alcance(app):
    j = iniciar(app)
    j.recolocar((160, 442))
    j.lume.energia = 0.
    j.vestigios.append(Vestigio(160, 420, j.tempo))
    j.tempo += .28
    p = (460, 420)
    assert j.visivel(p)
    luz = pygame.Surface((960, 540))
    compor_luz(luz, j, 0, 0, 1)
    normal = luz.get_at(p).r
    with ilustracao.estilo({"claroes_suaves": True}):
        compor_luz(luz, j, 0, 0, 1)
        assert 0 < luz.get_at(p).r < normal
        assert j.visivel(p)
    assert j.vestigios[-1].raio(j.tempo) == 520
