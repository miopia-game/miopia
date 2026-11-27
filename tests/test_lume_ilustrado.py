"""A pose, a iluminação e o apoio compartilham as âncoras da arte final."""

from struct import iter_unpack

import pygame
import pytest

from src import arte_lume
from src.travessia import Lume
from src.travessia_fagulha import Fagulha


def test_cache_preserva_a_luz_pintada_em_todos_os_quadros_e_nos_espelhos():
    for nome in set(arte_lume.POSES.values()) | {"mergulho","lancar","subida"}:
        for indice in range(arte_lume.total_quadros(nome)):
            for espelho in (False, True):
                im,(x,y) = arte_lume._quadro(nome,indice,espelho)
                pixels = im.pixels
                xx, yy = round(2*x), round(2*y)
                vizinhanca = [pixels.get_at((xx+i,yy+j)) for i in range(-2,3) for j in range(-2,3)]
                assert any(r>209 and g>132 and b<135 and a>180 for r,g,b,a in vizinhanca)
                assert pixels.get_rect().contains(pixels.get_bounding_rect(min_alpha=80).inflate(2,2))
                if nome in ("guarda","passo","agachar","deslizar","golpe"):
                    assert abs(pixels.get_bounding_rect(min_alpha=90).bottom-2*arte_lume.PE) <= 1


def test_apoio_alterna_com_deslocamento_sem_mover_a_colisao():
    lume = Lume(100, 140)
    lume.vx = 210
    nome,primeiro,_ = arte_lume.animacao(lume, 0.)
    lume.rect.x += 14
    nome,segundo,_ = arte_lume.animacao(lume, .08)
    antes = lume.rect.copy()
    assert nome == "corrida" and primeiro != segundo
    im1,_ = arte_lume._quadro(nome,primeiro,False)
    im2,_ = arte_lume._quadro(nome,segundo,False)
    sola = pygame.Rect(40,122,110,12)
    assert pygame.image.tobytes(im1.pixels.subsurface(sola),"RGBA") != pygame.image.tobytes(im2.pixels.subsurface(sola),"RGBA")
    assert arte_lume.animacao(lume, .08)[1] == segundo and lume.rect == antes


def test_braco_encontra_a_janela_do_golpe_e_vira_para_o_lancamento():
    lume = Lume(100,140)
    lume.golpe = .1
    lume.arma.tipo = "pesado"
    perfil = lume.arma.perfil
    for tempo, indice in ((0, 0), (perfil.espera, 5), (perfil.espera+perfil.ativo, 11), (perfil.total-.001, 15)):
        lume.arma.tempo = tempo
        assert arte_lume.animacao(lume,tempo)[1] == indice
    lume.golpe = 0
    fagulha = Fagulha(1.,(100,100),(42,101))
    assert arte_lume.animacao(lume,1.,fagulha) == ("lancar",0,-1)
    assert arte_lume.animacao(lume,1.2,fagulha)[0] == "guarda"

def test_combo_e_efeito_de_luz_nao_escondem_a_mao_no_primeiro_quadro():
    lume = Lume(100,140)
    lume.pulso = .4
    lume.golpe = .1
    for tipo,nome in (("corte1","golpe"),("corte2","subida"),("queda","mergulho")):
        lume.arma.tipo = tipo
        assert arte_lume.animacao(lume,0) == (nome,0,lume.arma.face)
        assert arte_lume.total_quadros(nome) == 16


def test_corrida_alterna_apoios_e_suspensao():
    sola = [arte_lume._quadro("corrida", i, False)[0].pixels.get_bounding_rect(min_alpha=90).bottom
            for i in range(16)]
    for inicio in (0, 8):
        assert sola[inicio] == 2*arte_lume.PE
        assert sola[inicio+5] < sola[inicio+3] < sola[inicio]
    assert max(sola) == 2*arte_lume.PE


def test_cada_cel_vem_de_um_desenho_inteiro_da_folha():
    # Pillow é necessário apenas para conferir os mestres de arte.
    import json
    from pathlib import Path
    Image = pytest.importorskip("PIL.Image")
    pasta = Path(__file__).resolve().parents[1] / "docs/arte/fontes/lume/quadros"
    registro = json.loads((pasta / "registro.json").read_text())
    assert set(registro) == set(arte_lume.POSES.values()) | {"mergulho", "subida", "lancar"}
    for nome, quadros in registro.items():
        assert len(quadros) == arte_lume.total_quadros(nome) == 16
        assert len({tuple(q["recorte"]) for q in quadros}) == len(quadros)
        desenhos = set()
        with Image.open(pasta / f"{nome}.png") as mestre:
            for i, q in enumerate(quadros):
                original = mestre.crop(q["recorte"])
                tamanho = tuple(round(v*q["escala"]) for v in original.size)
                cel = Image.new("RGBA", (192, 160))
                cel.paste(original.resize(tamanho, Image.Resampling.LANCZOS), q["origem"])
                pixel = pygame.image.tobytes(arte_lume._quadro(nome,i,False)[0].pixels, "RGBA")
                assert pixel == cel.tobytes(), (nome, i)
                desenhos.add(pixel)
        assert len(desenhos) == len(quadros), nome


def test_espinho_responde_na_preparacao_e_separa_a_estocada_do_arco():
    from src.arte_espinho import desenhar
    lume = Lume(100,140)
    lume.arma.tipo = "corte1"
    s = pygame.Surface((240,240),pygame.SRCALPHA)
    desenhar(s,lume,(111,125),100,140)
    assert s.get_bounding_rect().width > 8
    silhuetas = []
    for arma in ("espinho","agulha"):
        s.fill((0,0,0,0))
        lume.arma.equipamento = arma
        perfil = lume.arma.perfil
        lume.arma.tempo = perfil.espera + perfil.ativo*.68
        desenhar(s,lume,(111,125),100,140)
        silhuetas.append(s.get_bounding_rect())
    assert silhuetas[1].right > silhuetas[0].right
    assert silhuetas[0].height > silhuetas[1].height


def test_placas_do_abdomen_continuam_visiveis_em_cada_quadro():
    # Área opaca de âmbar ao redor da luz no sprite Full HD, antes do halo.
    for nome in set(arte_lume.POSES.values()) | {"mergulho", "lancar", "subida"}:
        for indice in range(arte_lume.total_quadros(nome)):
            sprite, (x, y) = arte_lume._quadro(nome, indice, False)
            area = pygame.Rect(round(x*2)-23, round(y*2)-22, 47, 45)
            cores = pygame.image.tobytes(sprite.pixels.subsurface(area), "RGBA")
            pixels = iter_unpack("4B", cores)
            ambar = sum(r > 200 and g > 132 and b < 135 and r-g > 15 and a > 175
                        for r, g, b, a in pixels)
            assert ambar >= 50, (nome, indice, ambar)
