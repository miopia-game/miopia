"""Fatos do Córrego podem ser lidos em qualquer ordem e voltam com o save."""
import pygame

from src.fases import CHAO
from src.travessia import Jornada
from tests.test_s20_raiz import passo, tecla
from tests.test_s21_arquivo import fechar_fala
from tests.test_s31_historia import iniciar


def preparar(app):
    j = iniciar(app)
    j.entrar(1)
    j.flags.update(("dreno", "lingueta", "ponte"))
    return j


def usar(app, x):
    app.jogo.recolocar((x, CHAO))
    tecla(app, pygame.K_e)
    passo(app)


def test_os_dois_indicios_reconstituem_as_marcas_em_qualquer_ordem(app):
    j = preparar(app)
    for primeira, segunda in ((798, 1476), (1476, 798)):
        j.flags.discard("pista_canal")
        j.flags.discard("leu_bercos_corrego")
        j.diario.clear()
        usar(app, primeira)
        assert j.dialogo
        fechar_fala(app)
        assert not any(t == "Os dois lados do canal" for t, _ in j.diario)
        usar(app, segunda)
        fechar_fala(app)
        notas = [msg for titulo, msg in j.diario if titulo == "Os dois lados do canal"]
        assert len(notas) == 1 and "antes do raio" in notas[0]
    novo = Jornada.carregar(j.salvar())
    assert {"leu_bercos_corrego", "pista_canal"} <= novo.flags
    assert any(t == "Os dois lados do canal" for t, _ in novo.diario)


def test_casca_muda_para_a_margem_e_reage_as_marcas_ja_vistas(app):
    j = preparar(app)
    assert next(o for o in j.objetos if o.nome == "Casca").x == 218
    j.flags.update(("raiz", "chefe", "ralo"))
    j.entrar(1, retorno=True)
    assert next(o for o in j.objetos if o.nome == "Casca").x == 1430
    usar(app, 1430)
    assert "Fio" in j.dialogo[1] and "três riscos" not in j.dialogo[1]
    fechar_fala(app)
    j.flags.update(("leu_bercos_corrego", "pista_canal"))
    usar(app, 1430)
    assert "três riscos" in j.dialogo[1]
    fechar_fala(app)
    assert sum(t == "A margem de Casca e Fio" for t, _ in j.diario) == 1
    salvo = Jornada.carregar(j.salvar())
    assert next(o for o in salvo.objetos if o.nome == "Casca").x == 1430
    assert "casca_fio_reencontro" in salvo.flags
