"""O corpo anuncia o golpe e cada efeito ativo nasce junto ao agressor."""
import pygame
import pytest

from src import arte_golpes_fauna as arte
from src.arte_arena import postura
from src.chefes import Encontro


def tinta(tela):
    return pygame.image.tobytes(tela,"RGBA")


@pytest.mark.parametrize("ident,tecnica",(
    ("morcego","rasante"),("aranha","mordida"),("vespa","mergulho"),
    ("carabideo","carga"),("sombra","fenda_dupla"),("cobra","mordida"),
    ("caruncho","onda_dupla"),("cobra-dos-bercos","veneno"),("cria","pique"),
    ("asa-fendida","rasante"),("tecela","fio"),("casco-oco","varrida_casco"),("coruja","garra"),
))
def test_efeito_local_se_anima_na_fase_ativa(ident,tecnica):
    s=pygame.Surface((240,180),pygame.SRCALPHA)
    for fase in ("neutro","preparacao"):
        arte.efeito_ataque(s,ident,tecnica,fase,(120,90),1,.8)
        assert not s.get_bounding_rect()
    for lado in (-1,1):
        momentos=set()
        for p in (.27,.52,.79):
            s.fill((0,0,0,0))
            arte.efeito_ataque(s,ident,tecnica,"ataque",(120,90),lado,p)
            caixa=s.get_bounding_rect()
            assert caixa and pygame.Rect(60,36,120,108).contains(caixa)
            momentos.add(tinta(s))
        assert len(momentos)==3


def test_guardiao_prepara_no_ritmo_de_cada_ataque():
    e=Encontro(2,3680,442)
    for duracao in (.47,.63,1.02):
        e._mudar("aviso",duracao)
        assert postura(e)[2]==0
        e.tempo=duracao*.2
        assert postura(e)[2]==pytest.approx(.8)

@pytest.mark.parametrize("raio,forca",((16,85),(144,255),(520,145),(904,255)))
def test_mascara_do_clarao_tem_os_mesmos_pixels_dos_discos_cheios(raio,forca):
    from src import pygame_hd as hd
    from src.paisagem import mascara_luz

    referencia=hd.Surface((raio*2,raio*2))
    for r in range(raio,0,-8 if raio>=900 else -2):
        v=min(1.,(raio-r)/100) if raio>=900 else min(1.,(1-r/raio)*1.8)
        v=v*v*(3-2*v)
        hd.draw.circle(referencia,(round(forca*v),)*3,(raio,raio),r)
        if v>=1:
            break
    atual=mascara_luz(raio,1,forca)
    assert pygame.image.tobytes(atual.pixels,"RGB")==pygame.image.tobytes(referencia.pixels,"RGB")
