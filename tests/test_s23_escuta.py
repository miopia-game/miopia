"""Os pousos da App viram pistas locais para a aranha do fundo do Córrego."""
import pygame

from src.ensaios import ENSAIOS
from src.fases import Terreno
from src.travessia import Comando, Jornada
from tests.test_s20_raiz import esperar_piso, passo, tecla


FUNDO = 1102


def aranha(jogo):
    return next(e for e in jogo.inimigos if e.origem == (2860, FUNDO))


def cair(jogo, x=2600, altura=3):
    jogo.recolocar((x, FUNDO-altura))
    jogo.lume.chao = False
    jogo.lume.vy = 270.


def test_descida_pela_app_dispara_escuta_apenas_no_piso_do_encontro(app):
    indice = next(n for n, cena in enumerate(ENSAIOS) if cena.nome == "Raízes do Córrego")
    app.comecar_ensaio(indice)
    jogo = app.jogo
    e = aranha(jogo)
    for piso in (532, 622, 712, 802, 892, 982):
        tecla(app, pygame.K_SPACE)
        passo(app, pygame.K_s)
        esperar_piso(app, piso)
        assert e.estado == "patrulha"

    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_s)
    for _ in range(60):
        passo(app)
        if "pouso" in jogo.eventos:
            break
    assert jogo.lume.chao and jogo.lume.rect.bottom == FUNDO
    assert e.estado == "investigar"
    assert [nome for nome, _ in jogo.sons_espaciais].count("patas_perto") == 1
    assert e.alvo_escuta == jogo.lume.rect.centerx

    # Atraia a aranha para oeste e atravesse pelo apoio acima dela.
    tecla(app, pygame.K_SPACE)
    for _ in range(25):
        passo(app, pygame.K_SPACE)
    passo(app)
    tecla(app, pygame.K_SPACE)
    for _ in range(4):
        passo(app, pygame.K_SPACE)
    for _ in range(81):
        passo(app, pygame.K_d, pygame.K_SPACE)
    assert jogo.lume.rect.bottom == 982 and jogo.lume.rect.centerx > 2890
    assert e.rect.centerx < 2640 and e.alvo_escuta == 2600
    passo(app)
    passo(app)
    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_s)
    esperar_piso(app, FUNDO)
    assert jogo.proximo().id == "reliquia_asa"
    tecla(app, pygame.K_e)
    passo(app)
    assert jogo.bolsa.estoque["asa"] == 1
    assert e.ativo and e.sequencia == 0 and jogo.lume.vida == 100


def test_escuta_guarda_o_primeiro_ponto_e_termina_sem_um_alvo_visivel():
    j = Jornada(etapa=1)
    e = aranha(j)
    j.recolocar((2600, FUNDO))
    for _ in range(12):
        j.update(1/60, Comando(mover=1))
        assert e.estado == "patrulha"

    cair(j)
    j.update(1/60)
    assert e.estado == "investigar" and e.alvo_escuta == 2600
    partida = e.rect.centerx
    # Lume muda de lado e pousa de novo. A busca já tem um destino.
    cair(j, 3090)
    for _ in range(90):
        j.update(1/60)
        assert e.alvo_escuta == 2600
        assert not any(nome.startswith("aviso_aranha_") for nome, _ in j.sons_espaciais)
    assert e.rect.centerx < partida-140
    for _ in range(70):
        j.update(1/60)
    assert e.estado == "patrulha" and e.alvo_escuta is None
    assert e.sequencia == 0 and not e.projeteis and j.lume.vida == 100


def test_o_som_cruza_obstaculo_local_sem_permitir_ataque_as_cegas(monkeypatch):
    j = Jornada(etapa=1)
    e = aranha(j)
    muro = Terreno(pygame.Rect(2810, 1030, 24, 72), "parede")
    solidos = Jornada.solidos.fget
    monkeypatch.setattr(Jornada, "solidos", property(lambda jogo: [*solidos(jogo), muro]))
    cair(j, 2778)
    j.update(1/60)
    assert j.lume.chao and e.estado == "investigar"
    for _ in range(150):
        j.update(1/60)
        assert e.rect.left >= muro.rect.right and e.sequencia == 0
    assert e.alvo_escuta is None and e.estado == "patrulha"


def test_aviso_so_com_visao_e_morte_limpa_busca_sem_gravar_no_save(app):
    app.iniciar("historia")
    app.jogar()
    j = app.jogo
    j.entrar(1)
    e = aranha(j)
    cair(j)
    passo(app)
    assert e.estado == "investigar"
    j.recolocar((e.rect.centerx+55, FUNDO))
    for _ in range(22):
        passo(app)
        if e.estado == "aviso":
            break
    assert e.estado == "aviso" and e.alvo_escuta is None
    assert e.sequencia == 1 and j.lume.vida == 100
    assert any(nome.startswith("aviso_aranha_") for nome, _ in j.sons_espaciais)

    e.repor()
    cair(j)
    passo(app)
    assert e.estado == "investigar"
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo"
    assert e.estado == "patrulha" and e.alvo_escuta is None
    assert e.rect.midbottom == e.origem and e.vida == e.max_vida
    salvo = j.salvar()
    assert "alvo_escuta" not in str(salvo)
    assert aranha(Jornada.carregar(salvo)).estado == "patrulha"
    j.flags.add("inimigo_2860")
    reaberto = Jornada.carregar(j.salvar())
    assert not any(a.origem == e.origem for a in reaberto.inimigos)
