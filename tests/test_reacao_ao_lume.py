import pygame
import pytest

from src import agua_pintada as agua
from src import pygame_hd as hd
from src.fases import CHAO
from src.passagem_lume import Passagem
from src.travessia import Comando, Jornada
from src.travessia_fagulha import Fagulha


@pytest.mark.parametrize("etapa,ancora,altura", [(0, 174, 49), (2, 176, 82)])
def test_planta_ao_alcance_acompanha_corpo_nos_dois_sentidos_e_assenta(
    etapa, ancora, altura
):
    j = Jornada(etapa=etapa)

    def flexao():
        return j.passagem.flexao(
            ancora,
            CHAO - altura * 0.47,
            j.tempo,
            bambu=etapa == 2,
            alcance=altura * 0.65 + 15,
        )

    for direcao in (1, -1):
        j.recolocar((ancora - 76 * direcao, CHAO))
        assert flexao() == 0
        pico = 0.0
        for _ in range(44):
            j.update(1 / 60, Comando(mover=direcao))
            pico = max(pico, direcao * flexao())
        assert pico > 0.49
        assert j.passagem.flexao(ancora, CHAO - 190, j.tempo) == 0
        for _ in range(100):
            j.update(1 / 60)
        assert flexao() == 0


def test_rastro_e_independente_do_numero_de_subpassos():
    def percurso(hz):
        r = Passagem()
        for n in range(1, hz + 1):
            r.mover(n / hz, ((n - 1) * 180 / hz, 420), (n * 180 / hz, 420))
        return r.flexao(180, 420, 1), len(r.amostras)

    a, ca = percurso(60)
    b, cb = percurso(120)
    assert abs(a - b) < 0.04 and max(ca, cb) <= 31


def test_fonte_refletida_segue_voo_pouso_e_extincao():
    j = Jornada(etapa=1)
    j.fagulha = f = Fagulha(1.0, (200, 355), (455, 415))
    for t in [1.02, 1.11, f.pouso_em, f.pouso_em + 5, f.pouso_em + 6.98]:
        j.tempo = t
        luz = agua.luz_da_fagulha(j, 73)
        x, y = f.posicao(t)
        assert (luz.x, luz.y, luz.raio) == (x - 73, y, f.raio(t))
        assert luz.na_pintura((-31, -108)).x == pytest.approx((x - 73 + 31) * 0.75)
    assert luz.intensidade < 0.05
    j.tempo = f.pouso_em + 7.01
    assert agua.luz_da_fagulha(j, 73) is None


@pytest.mark.parametrize(
    "bioma,ponto,tempo",
    [(agua.corrego, (397, 420), 1.35), (agua.gruta, (488, 431), 0.10)],
)
def test_luz_muda_material_molhado_e_preserva_pedra_distante(bioma, ponto, tempo):
    def pintar(luz):
        s = hd.Surface((200, 140))
        s.fill((43, 55, 67))
        origem = (100 - ponto[0] * 4 / 3, 70 - ponto[1] * 4 / 3)
        bioma(s, origem, tempo, luz)
        return pygame.image.tobytes(s.pixels, "RGB")

    frio = pintar(None)
    assert frio == pintar(agua.LuzNaAgua(-1000, -900, 84, 1))
    quente = pintar(agua.LuzNaAgua(*ponto, 84, 1))
    assert quente != frio and quente[: 400 * 3] == frio[: 400 * 3]


def test_reflexo_da_lamina_respeita_a_margem_e_o_dreno():
    def pintar(nivel):
        # A coordenada vertical do compositor é a do mundo.
        s = hd.Surface((130, 460))
        s.fill((51, 77, 88))
        agua.reflexo_canal(s, agua.LuzNaAgua(59, 387, 150, 1), 760, nivel, 2.0)
        return pygame.mask.from_threshold(s.pixels, (51, 77, 88, 255), (1, 1, 1, 255))

    cheio, drenado = pintar(353), pintar(423)
    cheio.invert()
    drenado.invert()
    rect = cheio.get_bounding_rects()
    assert rect and min(r.x for r in rect) >= 2 * (804 - 760)
    assert max(r.bottom for r in rect) < 2 * 423
    assert min(r.top for r in drenado.get_bounding_rects()) >= 2 * 423
