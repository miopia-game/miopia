"""A história acompanha as ações da campanha e o que ficou por fazer."""
import pygame

from src import arte_arena, resgates, roteiro, telas
from src.chefes import Encontro
from src.fases import ARENA, CHAO, FIM_ARENA, RAIZ, SAIDA
from src.orientacao import objetivo_atual
from tests.test_campanha import resolver_arena
from tests.test_s20_raiz import esperar_piso, ir, passo, tecla
from tests.test_s21_arquivo import fechar_fala
from tests.test_travessia import Percurso


def iniciar(app):
    app.iniciar("historia")
    while app.estado == "prologo":
        tecla(app, pygame.K_RETURN)
    return app.jogo


def test_o_caderno_mostra_so_os_fatos_da_viagem_salva(app):
    j = iniciar(app)
    inicio = tuple(roteiro.linha_da_viagem(j))
    assert len(inicio) == 4
    assert inicio[0][0] == "Bosque das Samambaias"
    assert all(estado == "Por descobrir" for _, estado, _ in inicio[1:])
    j.flags.update(("meio", "valvula", "peca", "cunha", "chefe", "raiz", "gota_0", "gota_1", "gota_2"))
    j.restauradas = 1
    j.entrar(1)
    app.salvar_campanha()
    app.iniciar("historia", continuar=True)
    j = app.jogo
    linha = tuple(roteiro.linha_da_viagem(j))
    assert linha[0][1] == "Raiz restaurada"
    assert linha[1][1] == "Em curso"
    assert linha[2][1] == "Por descobrir"
    tecla(app, pygame.K_m)
    tecla(app, pygame.K_LEFT)
    assert app.pagina == telas.paginas_diario(app)-1  # Controles.
    tecla(app, pygame.K_LEFT)
    assert app.pagina == telas.paginas_diario(app)-2  # A viagem.
    app.desenhar()
    assert pygame.display.get_surface().get_size() == (960, 540)


def test_capitulo_em_revisita_lembra_o_que_ja_foi_restaurado(app):
    j = iniciar(app)
    j.entrar(1)
    entrada = roteiro.texto_travessia
    assert "Casca" in entrada(j)
    j.flags.add("raiz")
    assert entrada(j) != roteiro.ENTRADAS[1]
    assert "ponte" in entrada(j).lower()


def test_nira_conta_do_mapa_sem_trocar_o_rastreio_de_tila(app):
    j = iniciar(app)
    j.missao = "resgates"
    ir(app, 224)
    tecla(app, pygame.K_e)
    passo(app)
    assert j.dialogo[0] == "Nira"
    assert "Véspera" in j.dialogo[1] and "data" in j.dialogo[1].lower()
    assert "cipó" in j.dialogo[1].lower()
    assert j.missao == "resgates" and objetivo_atual(j).id == "grade_raizes"


def test_casca_relata_o_desvio_e_indica_a_roda_alcancavel(app):
    j = iniciar(app)
    j.entrar(1)
    j.flags.update(("dreno", "lingueta"))
    ir(app, 218)
    tecla(app, pygame.K_e)
    passo(app)
    assert j.dialogo[0] == "Casca"
    assert "Brasa" in j.dialogo[1] and "roda da ponte" in j.dialogo[1]
    assert any(t == "Caminho indicado por Casca" for t, _ in j.diario)


def test_o_sino_ensina_o_sinal_sem_audio_e_repete_apos_recarregar(app):
    j = iniciar(app)
    j.entrar(3)
    j.flags.update(("roldana", "contrapeso"))
    j.recolocar((2530, 237))
    tecla(app, pygame.K_SPACE)
    passo(app, pygame.K_s)
    esperar_piso(app, 469)
    tecla(app, pygame.K_F10)
    assert app.audio.mudo
    j.lume.energia = 0
    tecla(app, pygame.K_e)
    passo(app)
    assert "eco_antigo" in j.flags and "sino" in j.eventos
    assert not any(t.tipo == "vedacao" and t.rect.x == 2576 for t in j.solidos)
    for _ in range(27):
        passo(app)
    assert j.visivel((2635, 428)) and j.lume.energia == 0
    app.desenhar()
    cores = pygame.mask.from_threshold(pygame.display.get_surface(), (219, 198, 133), (1, 1, 1))
    assert cores.count() > 15
    salvo = j.carregar(j.salvar())
    assert not salvo.visivel((2635, 428))
    app.jogo = salvo
    salvo.recolocar((2530, 469))
    tecla(app, pygame.K_e)
    passo(app)
    assert "sino" in salvo.eventos
    assert salvo.diario == j.diario and salvo.pontuacao == j.pontuacao


def test_reencontro_cita_os_resgates_feitos_e_o_estado_real_do_jardim(app):
    j = iniciar(app)
    assert "três lugares vazios" in resgates.mensagem_final(j)
    j.sobreviventes = {"tila": {"oficio": "trilha", "premio": False}}
    parcial = resgates.mensagem_final(j)
    assert "Tila" in parcial and "luz" in parcial and "dois lugares" in parcial
    j.sobreviventes.update(bento={"oficio": "abrigo", "premio": True})
    assert "um lugar para Aru" in resgates.mensagem_final(j)
    j.sobreviventes.update(aru={"oficio": "abrigo", "premio": True})
    completo = resgates.mensagem_final(j)
    assert all(nome in completo for nome in ("Tila", "Bento", "Aru"))
    assert "sementes" in completo and "muda" not in completo and "luz" in completo
    j.cartografia.add("jardim_plantado")
    assert "muda" in resgates.mensagem_final(j)


def test_coruja_reconhece_a_seca_antes_de_lume_restaurar_a_ultima_raiz(app):
    j = iniciar(app)
    j.entrar(3)
    j.restauradas = 3
    j.flags.update(("roldana", "contrapeso", "eco_antigo", "chefe"))
    j.recolocar((FIM_ARENA+43, CHAO))
    tecla(app, pygame.K_e)
    passo(app)
    antes = j.dialogo[1]
    assert "sino" in antes and "antes do raio" in antes
    fechar_fala(app)
    j.flags.add("raiz")
    tecla(app, pygame.K_e)
    passo(app)
    assert antes != j.dialogo[1] and "correntes" in j.dialogo[1]


def test_arena_conserva_sino_sem_desenhar_uma_segunda_coruja(app, monkeypatch):
    j = iniciar(app)
    j.entrar(3)
    j.flags.update(("eco_antigo", "chefe"))
    j.boss = Encontro(3, ARENA, CHAO)
    j.boss.vencido = True
    j.recolocar((FIM_ARENA+43, CHAO))
    j.camera = 3700
    chamadas = []
    cenario = arte_arena._cenario
    corpo = arte_arena.fauna.corpo

    def cenario_observado(*args):
        chamadas.append("arena")
        cenario(*args)

    def corpo_observado(s, ident, *args, **kwargs):
        if ident == "coruja":
            chamadas.append("chefe")
        return corpo(s, ident, *args, **kwargs)

    monkeypatch.setattr(arte_arena, "_cenario", cenario_observado)
    monkeypatch.setattr(arte_arena.fauna, "corpo", corpo_observado)
    app.desenhar()
    assert chamadas == ["arena"]
    assert j.proximo().id == "coruja_calma"


class CampanhaPelaApp(Percurso):
    """Reusa o piloto de saltos e envia entradas à App, como no jogo."""

    def __init__(self, app, observar=None):
        self.app = app
        self.observar = observar
        self.registrados = set()

    @property
    def jogo(self):
        return self.app.jogo

    @property
    def lume(self):
        return self.jogo.lume

    def registrar(self, ident):
        if self.observar is not None and ident not in self.registrados:
            self.registrados.add(ident)
            self.observar(self.app, ident)

    def tomar_balsamo(self):
        for _ in self.jogo.bolsa.estoque:
            if self.jogo.bolsa.equipado == "balsamo":
                break
            tecla(self.app, pygame.K_q)
        tecla(self.app, pygame.K_f)

    def tick(self, **cmd):
        a = self.app
        pressionadas = []
        mover = cmd.get("mover", 0)
        if mover:
            pressionadas.append(pygame.K_d if mover > 0 else pygame.K_a)
        if cmd.get("segurar_salto"):
            pressionadas.append(pygame.K_SPACE)
        if cmd.get("baixo"):
            pressionadas.append(pygame.K_s)
        for acao, key in (("salto", pygame.K_SPACE), ("interagir", pygame.K_e),
                          ("golpe", pygame.K_j), ("deslize", pygame.K_LSHIFT),
                          ("clarao", pygame.K_k)):
            if cmd.get(acao):
                tecla(a, key)
        passo(a, *pressionadas)
        while a.impacto_restante > 0:
            passo(a, *pressionadas)
        j = self.jogo
        if a.estado == "capitulo":
            self.registrar(f"travessia-{j.etapa}")
            tecla(a, pygame.K_RETURN)
        if j.dialogo:
            if j.dialogo[0] == "Coruja":
                a.atualizar(12)
                self.registrar("coruja")
            fechar_fala(a)
        e = j.boss
        if e and e.estado == "aberto":
            self.registrar(f"guardiao-{j.etapa}")
        if e and e.coro_iniciado and not e.vencido:
            self.registrar("ultimo-chamado")
        if j.sino_eco_inicio is not None and .40 < j.tempo-j.sino_eco_inicio < .70:
            self.registrar("sino-soterrado")
        if "raiz" in j.eventos and "raiz" in j.flags:
            self.registrar(f"raiz-{j.etapa}")
        if a.estado == "morte":
            raise AssertionError(f"Lume caiu em {j.fase.name} na posição {j.lume.rect.midbottom}.")


def percorrer_historia(app, observar=None):
    tecla(app, pygame.K_RETURN)  # História, no menu de um perfil temporário vazio.
    assert app.estado == "prologo"
    piloto = CampanhaPelaApp(app, observar)
    while app.estado == "prologo":
        tecla(app, pygame.K_RETURN)
        if app.estado == "prologo":
            piloto.registrar(f"prologo-{app.quadro}")
            tecla(app, pygame.K_RETURN)
    j = piloto.jogo
    for etapa, caminho in enumerate((piloto.bosque, piloto.corrego, piloto.taquaral, piloto.gruta)):
        assert j.etapa == etapa
        caminho()
        assert j.orvalhos >= 3
        resolver_arena(piloto)
        assert "chefe" in j.flags and j.boss.vencido
        if etapa == 3:
            assert j.boss.coro_sinais == 3
            piloto.ir(FIM_ARENA+43)
            piloto.usar()
        piloto.ir(RAIZ)
        piloto.usar()
        assert j.restauradas == etapa+1
        assert tuple(roteiro.linha_da_viagem(j))[etapa][1] == "Raiz restaurada"
        piloto.ir(SAIDA)
        piloto.usar()
    assert app.estado == "fim" and j.concluida and len(j.sobreviventes) == 0
    piloto.registrar("desfecho")
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and j.concluida
    assert objetivo_atual(j).id == "rota_resgate"
    assert "reacesa" in j.aviso
    piloto.registrar("floresta-reacesa")
    tecla(app, pygame.K_m)
    tecla(app, pygame.K_LEFT)
    tecla(app, pygame.K_LEFT)
    piloto.registrar("diario")
    tecla(app, pygame.K_m)
    app.menu()
    tecla(app, pygame.K_RETURN)
    assert app.estado == "jogo" and app.jogo.concluida
    assert app.jogo.restauradas == 4 and objetivo_atual(app.jogo).id == "rota_resgate"


def test_campanha_do_prologo_ao_pos_jogo_pela_app(app):
    percorrer_historia(app)
