"""Gravação íntegra, retorno voluntário e troca de dificuldade da História."""
import pygame

from src import corte_vertical
from src.chefes import DIFICIL, NORMAL
from src.fases import ARENA, CHAO, MEIO
from src.memoria import Memoria
from tests.test_s20_raiz import passo, tecla
from tests.test_s31_historia import iniciar


def test_falha_no_save_da_vitoria_reverte_registro_e_preserva_campanha(app, tmp_path, monkeypatch):
    monkeypatch.setenv("MIOPIA_DADOS", str(tmp_path))
    app.mem.db.close()
    app.mem = Memoria()
    j = iniciar(app)
    anterior = app.mem.ler("campanha")
    app.mem.db.execute("""
        CREATE TRIGGER falhar_save BEFORE INSERT ON estado
        WHEN NEW.chave = 'campanha'
        BEGIN SELECT RAISE(ABORT, 'falha de gravação simulada'); END
    """)
    j.concluida, j.estado = True, "vitoria"
    j.pontuacao = 800
    passo(app)
    assert app.estado == "fim"
    assert app.resultados_pendentes and "save anterior foi preservado" in app.mem.aviso
    recuperado = Memoria()
    try:
        assert recuperado.ler("campanha") == anterior
        assert recuperado.recordes() == []
    finally:
        recuperado.db.close()

    app.mem.db.execute("DROP TRIGGER falhar_save")
    tecla(app, pygame.K_RETURN)
    app.menu()
    assert app.mem.ler("campanha")["concluida"]
    assert app.mem.recordes() == [("historia", 1, 800, 1)]


def voltar_ao_marco(app):
    tecla(app, pygame.K_ESCAPE)
    assert app.estado == "pausa"
    for _ in range(3):
        tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "confirmar"
    tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo"


def test_retorno_voluntario_conserva_recursos_e_morte_ainda_recupera(app):
    j = iniciar(app)
    j.lume.vida, j.lume.energia = 18., 0.
    j.bolsa.receber("casulo", 2)
    j.recolocar((400, 442))
    voltar_ao_marco(app)
    assert j.lume.rect.midbottom == j.checkpoint
    assert (j.lume.vida, j.lume.energia, j.lume.vidas) == (18., 0., 3)
    save = app.mem.ler("campanha")
    assert save["vida"] == 18. and save["energia"] == 0.
    assert j.bolsa.estoque["casulo"] == 2

    j.lume.vida = 0.
    passo(app)
    assert app.estado == "morte"
    app.atualizar(.5)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo"
    assert (j.lume.vida, j.lume.energia, j.lume.vidas) == (100., 100., 2)
    assert j.bolsa.estoque["casulo"] == 2


def escolher_dificil(app):
    tecla(app, pygame.K_ESCAPE)
    for _ in range(2):
        tecla(app, pygame.K_DOWN)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "ajustes"
    tecla(app, pygame.K_RIGHT)


def fechar_ajustes(app):
    tecla(app, pygame.K_ESCAPE)
    tecla(app, pygame.K_ESCAPE)
    assert app.estado == "jogo"


def test_dificuldade_espera_pelo_marco_e_recompoe_a_arena(app):
    j = iniciar(app)
    j.flags.update(("meio", "marco", j.fase.preparo))
    j.checkpoint = (ARENA - 20, CHAO)
    from src.travessia_fagulha import MorcegoDoGalho
    abatido = next(e for e in j.inimigos if isinstance(e, MorcegoDoGalho))
    abatido.ativo = False
    j.flags.add("inimigo_875")  # Identificador do save S40, anterior à mudança do poleiro.
    j.recolocar((ARENA + 65, CHAO))
    passo(app)
    boss = j.boss
    assert boss.ritmo == NORMAL
    escolher_dificil(app)
    assert j.dificuldade_pendente == "difícil"
    assert (j.dificuldade, j.boss) == ("normal", boss)
    fechar_ajustes(app)
    passo(app)
    assert j.boss is boss and boss.ritmo == NORMAL
    voltar_ao_marco(app)
    assert j.dificuldade == "difícil" and j.dificuldade_pendente is None
    assert j.lume.vidas == 3
    assert not any(e.origem == abatido.origem for e in j.inimigos)
    assert j.inimigos and all(e.dificuldade == "difícil" for e in j.inimigos)
    for _ in range(50):
        passo(app, pygame.K_d)
        if j.boss:
            break
    assert j.boss is not boss and j.boss.ritmo == DIFICIL
    app.menu()
    tecla(app, pygame.K_RETURN)
    assert app.jogo.dificuldade == "difícil" and app.jogo.lume.vidas == 3
    assert app.mem.prefs["dificuldade"] == "normal"


def test_dificuldade_pendente_persiste_e_e_aplicada_no_marco_da_rota(app):
    j = iniciar(app)
    j.lume.vida, j.lume.energia = 18., 27.
    escolher_dificil(app)
    salvo = app.mem.ler("campanha")
    assert salvo["dificuldade_pendente"] == "difícil"
    assert salvo["dificuldade"] == "normal"
    fechar_ajustes(app)
    j.recolocar((MEIO - 20, CHAO))
    passo(app)
    assert j.checkpoint == (MEIO, CHAO)
    assert j.dificuldade == app.mem.ler("campanha")["dificuldade"] == "difícil"
    assert (j.lume.vida, j.lume.energia, j.lume.vidas) == (18., 27., 3)
    app.menu()
    app.mem.guardar("campanha", salvo)
    app.menu()
    tecla(app, pygame.K_RETURN)
    assert app.jogo.dificuldade == "difícil" and app.jogo.dificuldade_pendente is None
    assert (app.jogo.lume.vida, app.jogo.lume.energia) == (18., 27.)


def test_dificuldade_aplica_em_marco_do_corte_e_nas_fagulhas_da_proxima_tentativa(app):
    j = iniciar(app)
    corte_vertical.entrar(j, "poco")
    marco = next(o for o in j.objetos if o.id == "marco_poco")
    escolher_dificil(app)
    fechar_ajustes(app)
    j.recolocar((marco.x, marco.y))
    tecla(app, pygame.K_e)
    passo(app)
    assert j.dificuldade == "difícil"
    assert j.inimigos and all(e.dificuldade == "difícil" for e in j.inimigos)
    assert j.lume.vidas == 3
    j.lume.vidas, j.lume.vida = 1, 0.
    passo(app)
    assert app.estado == "morte" and j.estado == "derrota"
    app.atualizar(.5)
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and j.lume.vidas == 2
