"""O mesmo piso leva à Galeria das Sementes e deixa voltar à trilha."""
import pygame

from src.descoberta import conhecida
from src.ensaios import ENSAIOS
from src.fases import CHAO
from src.luzes_mundo import claro
from src.missoes import conhecidas
from src.orientacao import objetivo_atual
from src.travessia import Jornada
from tests.test_s20_raiz import esperar_piso, ir, passo, tecla
from tests.test_s21_arquivo import fechar_fala


FUNDO = 968
X_GRADE = 2180
PEDIDO = "bercos_vento"
CAVILHA = "cavilha_sementes"
REPARO = "veneziana_sementes_aberta"


def ramal(app):
    app.iniciar("historia")
    app.jogar()
    j = app.jogo
    # Começa depois da Sentinela. A campanha inteira tem roteiro próprio.
    j.historico[0, 2] = {"no", "meio", "brasa", "inimigo_1980"}
    j.entrar(2)
    j.reiniciar()
    return j


def pela_grade(app):
    ir(app, X_GRADE)
    for piso in (590, 775, FUNDO):
        tecla(app, pygame.K_SPACE)
        passo(app, pygame.K_s)
        esperar_piso(app, piso)


def test_descida_fisica_mostra_patamares_e_cipo_funciona_sem_reparo(app):
    j = ramal(app)
    assert not conhecida(j, X_GRADE, FUNDO-12)
    assert any(t.descida and t.rect.collidepoint(X_GRADE, CHAO) for t in j.solidos)
    pela_grade(app)
    for _ in range(30):
        passo(app)
    assert j.camera_y > 430 and conhecida(j, X_GRADE, FUNDO-12)
    assert j.lume.vida == 100 and j.lume.rect.bottom == FUNDO
    tecla(app, pygame.K_e)
    passo(app)
    for _ in range(150):
        passo(app)
        if j.lume.chao and j.lume.rect.bottom == CHAO:
            break
    assert j.lume.rect.bottom == CHAO and not j.lume.em_corda


def test_grade_permite_seguir_por_cima_sem_entrar_na_galeria(app):
    j = ramal(app)
    ir(app, 2400)
    assert j.lume.chao and j.lume.rect.bottom == CHAO
    assert not conhecida(j, X_GRADE, FUNDO-12)


def test_vespa_ancora_o_ferrao_e_divide_a_pressao_com_a_aranha(app):
    j = ramal(app)
    vespa = next((e for e in j.inimigos if e.origem == (2087, 871)), None)
    aranha = next((e for e in j.inimigos if e.origem == (1910, FUNDO)), None)
    assert vespa is not None and aranha is not None
    # Fica na câmara para observar vários ciclos sem encerrar a tentativa.
    j.recolocar((1954, FUNDO))
    j.lume.iframes = 20
    viu_aranha = viu_ferrao = viu_projetil = False
    for _ in range(480):
        passo(app)
        assert sum(e.estado in ("aviso", "investida") for e in (vespa, aranha)) <= 1
        viu_aranha |= aranha.estado == "aviso"
        if vespa.estado == "aviso" and vespa.tecnica == "ferrao":
            assert vespa.no_poleiro
            viu_ferrao = True
        viu_projetil |= bool(vespa.projeteis)
    assert viu_aranha and viu_ferrao and viu_projetil
    assert (vespa.papel, aranha.papel) == ("cobertura", "flanco")


def test_patrulha_retorna_ao_ponto_inicial_apos_morte(app):
    j = ramal(app)
    grupo = [e for e in j.inimigos if e.origem == (2087, 871) or e.origem == (1910, FUNDO)]
    assert len(grupo) == 2
    for e in grupo:
        e.vida -= 2
        e.rect.centerx += 30
    j.lume.vida = 0
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.4)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo"
    assert [(e.vida, tuple(e.rect.midbottom)) for e in grupo] == [(e.max_vida, e.origem) for e in grupo]


def test_vespa_retoma_o_poleiro_antes_de_escolher_outro_golpe(app):
    j = ramal(app)
    j.recolocar((1954, FUNDO))
    j.lume.iframes = 12
    vespa = next(e for e in j.inimigos if e.origem == (2087, 871))
    vespa.rect.midbottom = (2017, 895)  # Posição depois de um mergulho.
    vespa.t = 0.
    for _ in range(18):
        passo(app)
        assert vespa.estado == "patrulha"
    for _ in range(430):
        passo(app)
        if vespa.estado == "aviso" and vespa.tecnica == "ferrao":
            assert vespa.no_poleiro
            return
    raise AssertionError("A vespa não retomou o disparo após voltar ao poleiro.")


def passar_pela_raiz(app, voltar=False):
    l = app.jogo.lume
    while l.slide_cd > 0:
        passo(app, pygame.K_s)
    tecla(app, pygame.K_LSHIFT)
    direcao = pygame.K_a if voltar else pygame.K_d
    for _ in range(180):
        passo(app, direcao, pygame.K_s, pygame.K_LSHIFT)
        if (l.rect.centerx < 2212 if voltar else l.rect.centerx > 2368):
            break
    assert (l.rect.centerx < 2212 if voltar else l.rect.centerx > 2368)
    assert l.rect.bottom == FUNDO


def recolher_cavilha(app):
    ir(app, 1725)
    assert app.jogo.proximo().id == CAVILHA
    tecla(app, pygame.K_e)
    passo(app)
    assert CAVILHA in app.jogo.flags


def test_pedido_de_risca_reparo_premio_e_retorno_apos_carregar(app):
    j = ramal(app)
    ir(app, X_GRADE)
    tecla(app, pygame.K_e)
    passo(app)
    assert j.dialogo and "Risca" in j.dialogo[1]
    fechar_fala(app)
    tecla(app, pygame.K_m)
    tecla(app, pygame.K_RIGHT)
    for _ in range(len(conhecidas(j))):
        if conhecidas(j)[app.pedido_cursor].id == PEDIDO:
            break
        tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    assert j.missao == PEDIDO
    tecla(app, pygame.K_m)
    assert objetivo_atual(j).id == "entrada_sementes"
    pela_grade(app)
    assert objetivo_atual(j).id == CAVILHA
    recolher_cavilha(app)
    app.salvar_campanha()
    app.iniciar("historia", continuar=True)
    app.jogar()
    j = app.jogo
    assert j.missao == PEDIDO and CAVILHA in j.flags
    assert all(o.id != CAVILHA for o in j.objetos)
    pela_grade(app)
    passar_pela_raiz(app)
    assert objetivo_atual(j).id == "veneziana_sementes"
    tecla(app, pygame.K_e)
    passo(app)
    assert REPARO in j.flags and j.bolsa.estoque["globo"] == 1
    for _ in range(30):
        passo(app)
    tecla(app, pygame.K_e)
    passo(app)
    assert j.bolsa.estoque["globo"] == 1
    assert next(m for m in conhecidas(j) if m.id == PEDIDO).estado == "Concluída"


def test_reparo_recusa_encaixe_vazio_e_cavilha_antecipada_registra_pedido(app):
    j = ramal(app)
    pela_grade(app)
    passar_pela_raiz(app)
    tecla(app, pygame.K_e)
    passo(app)
    assert REPARO not in j.flags and "cavilha" in j.aviso.lower()
    passar_pela_raiz(app, voltar=True)
    recolher_cavilha(app)
    assert next(m for m in conhecidas(j) if m.id == PEDIDO).estado == "Entregar"


def test_veneziana_libera_luz_e_atalho_fisico_nos_dois_sentidos(app):
    j = ramal(app)
    pela_grade(app)
    recolher_cavilha(app)
    ir(app, X_GRADE)
    passar_pela_raiz(app)
    assert not claro(j, (2400, 800))
    tecla(app, pygame.K_e)
    passo(app)
    assert REPARO in j.flags
    panel = next(t.rect.w for t in j.solidos if t.tipo == "veneziana_sementes")
    tecla(app, pygame.K_ESCAPE)
    app.atualizar(.5)
    assert next(t.rect.w for t in j.solidos if t.tipo == "veneziana_sementes") == panel
    tecla(app, pygame.K_ESCAPE)
    for _ in range(30):
        passo(app)
    assert 0 < next(t.rect.w for t in j.solidos if t.tipo == "veneziana_sementes") < panel
    for _ in range(45):
        passo(app)
    assert claro(j, (2400, 800))
    assert not any(t.tipo == "veneziana_sementes" for t in j.solidos)
    j.lume.energia = 0
    ir(app, 2400)
    tecla(app, pygame.K_SPACE)
    for _ in range(380):
        passo(app, pygame.K_SPACE)
        if j.lume.rect.bottom < CHAO-10:
            break
    assert j.lume.rect.bottom < CHAO-10 and j.lume.planando
    esperar_piso(app, CHAO)
    assert j.lume.energia == 0
    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_s)
    esperar_piso(app, FUNDO)
    assert j.lume.rect.centerx > 2336
    salvo = Jornada.carregar(j.salvar())
    assert claro(salvo, (2400, 800))
    assert any(t.descida and t.rect.collidepoint(2400, CHAO) for t in salvo.solidos)
    assert salvo.bolsa.estoque["globo"] == 1


def test_grade_leste_fica_fechada_ate_reparar(app):
    j = ramal(app)
    ir(app, 2400)
    tecla(app, pygame.K_SPACE)
    for _ in range(45):
        passo(app, pygame.K_s)
        assert j.lume.rect.bottom == CHAO


def test_save_anterior_mantem_marco_e_galeria_permanece_descobrivel(app):
    j = ramal(app)
    dados = j.salvar()
    dados["versao"] = 2
    j = app.jogo = Jornada.carregar(dados)
    assert j.lume.rect.midbottom == j.checkpoint == (1848, CHAO)
    assert all(m.id != PEDIDO for m in conhecidas(j))
    assert not conhecida(j, X_GRADE, FUNDO-12)
    pela_grade(app)
    assert j.lume.rect.midbottom[1] == FUNDO


def test_ensaio_inicia_na_grade_sem_mudar_o_save(app):
    j = ramal(app)
    app.salvar_campanha()
    campanha = app.mem.ler("campanha")
    i = next(i for i, cena in enumerate(ENSAIOS) if cena.nome == "Galeria das Sementes")
    app.comecar_ensaio(i)
    assert app.jogo is not j and app.jogo.lume.rect.midbottom == (X_GRADE, CHAO)
    assert app.jogo.proximo().id == "placa_sementes"
    pela_grade(app)
    assert app.mem.ler("campanha") == campanha
