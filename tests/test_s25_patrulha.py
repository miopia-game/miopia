"""A oportunidade de atacar depende de quem pode ser visto na patrulha."""
import pygame

from src import encontros, luzes_mundo
from src.ensaios import ENSAIOS
from src.fases import CHAO
from src.travessia import Jornada
from tests.test_s20_raiz import ir, passo, tecla


def vigilia(jogo):
    return [e for e in jogo.inimigos if e.origem[0] in encontros.CLAREIRAS[0].membros]


def em_ataque(grupo):
    return [e for e in grupo if e.estado in ("aviso", "investida")]


def iniciar_ensaio(app):
    indice = next(n for n, cena in enumerate(ENSAIOS) if cena.nome == "Clareira da Vigília")
    app.comecar_ensaio(indice)
    jogo = app.jogo
    jogo.lume.iframes = 30.
    for _ in range(20):
        passo(app)
        assert jogo.lume.chao and jogo.lume.rect.bottom == CHAO
    ir(app, 1580)
    return jogo


def test_patrulha_se_reveza_no_escuro_e_mantem_pressao_no_flanco(app):
    jogo = iniciar_ensaio(app)
    grupo = vigilia(jogo)
    inicios = set()
    flanco_durante_ataque = False
    for _ in range(420):
        passo(app)
        ativos = em_ataque(grupo)
        inicios.update(e.tipo for e in ativos if e.estado == "investida")
        assert len(ativos) <= 1
        flanco_durante_ataque |= bool(ativos and any(e.estado == "manobra" for e in grupo))
    assert len(inicios) >= 2
    assert flanco_durante_ataque


def test_flanco_pode_comecar_mas_golpe_na_fila_espera_no_escuro():
    jogo = Jornada()
    jogo.recolocar((1580, CHAO))
    grupo = vigilia(jogo)
    for e in grupo:
        e.rect.midbottom = (1600, CHAO)
    encontros.coordenar(jogo)
    frente, flanco, cobertura = grupo
    frente.plano = [0]
    assert frente.preparar(jogo.lume)
    frente.t = .10
    flanco.plano = ["flanco", 0]
    assert flanco.preparar(jogo.lume)
    assert flanco.estado == "manobra" and flanco.plano == [0]
    cobertura.plano = [0]
    assert cobertura.preparar(jogo.lume) == ""
    assert cobertura.plano == [0] and cobertura.sequencia == 0
    frente.estado = "recuo"
    assert cobertura.preparar(jogo.lume)


def test_lume_iluminado_nao_libera_um_atacante_ainda_no_escuro():
    jogo = Jornada()
    jogo.recolocar((1580, CHAO))
    jogo.globos = [{"regiao": "0:0", "x": 1340, "y": CHAO-13}]
    frente, flanco, _ = vigilia(jogo)
    frente.rect.midbottom = (1520, CHAO)
    flanco.rect.midbottom = (1650, CHAO)
    assert luzes_mundo.claro(jogo, jogo.lume.rect.center)
    assert luzes_mundo.claro(jogo, frente.rect.center)
    assert not luzes_mundo.claro(jogo, flanco.rect.center)
    encontros.coordenar(jogo)
    frente.plano = [0]
    flanco.plano = [0]
    assert frente.preparar(jogo.lume)
    frente.t = .10
    assert flanco.preparar(jogo.lume) == ""
    assert flanco.plano == [0]


def test_clarao_libera_dois_golpes_e_morte_limpa_ameacas(app):
    jogo = iniciar_ensaio(app)
    grupo = vigilia(jogo)
    tecla(app, pygame.K_k)
    anterior = None
    sobreposicao = False
    for _ in range(220):
        passo(app)
        avisos = [nome for nome, _ in jogo.sons_espaciais if nome.startswith("aviso_")]
        assert len(em_ataque(grupo)) <= 2 and len(avisos) <= 1
        if avisos:
            if anterior is not None:
                assert jogo.tempo - anterior >= .16
            anterior = jogo.tempo
        if len(em_ataque(grupo)) == 2:
            sobreposicao = True
            break
    assert sobreposicao and jogo.lume.energia < 100
    for _ in range(450):
        passo(app)
        if not jogo.vestigios and len(em_ataque(grupo)) <= 1:
            break
    assert not jogo.vestigios
    for _ in range(240):
        passo(app)
        assert len(em_ataque(grupo)) <= 1

    tecla(app, pygame.K_k)
    passo(app)
    assert jogo.vestigios
    jogo.lume.vida = 0
    for _ in range(18):
        passo(app)
        if app.estado == "morte":
            break
    assert app.estado == "morte"
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo"
    jogo = app.jogo
    grupo = vigilia(jogo)
    assert not jogo.vestigios and not em_ataque(grupo)
    assert all(not e.plano and not e.projeteis for e in grupo)


def test_save_antigo_sem_globo_e_luz_recalculada_ao_reabrir():
    salvo = Jornada().salvar()
    salvo.pop("globos")
    salvo.pop("tochas")
    jogo = Jornada.carregar(salvo)
    jogo.recolocar((1580, CHAO))
    encontros.coordenar(jogo)
    assert not any(e.ataque_iluminado for e in vigilia(jogo))

    jogo.bolsa.receber("globo", 1)
    jogo.bolsa.equipado = "globo"
    assert jogo.usar_item()
    reaberto = Jornada.carregar(jogo.salvar())
    reaberto.recolocar((1580, CHAO))
    encontros.coordenar(reaberto)
    assert len(reaberto.globos) == 1
    assert all(e.ataque_iluminado for e in vigilia(reaberto))
