"""Apresentação sem faixa de missão e descidas físicas no mesmo mapa."""
import pygame
import pytest
from src import avisos,telas,tutorial,sinalizacao
from src.paisagem import hud
from src.travessia import Jornada,Comando
from src.mapa_visor import QUADRO
from src.descoberta import conhecida
from tests.test_s06_raizes import percurso


@pytest.mark.parametrize('pos',[(100,220),(730,150),(925,120),(730,275)])
def test_aviso_escolhe_canto_sem_cobrir_lume(app,pos):
    app.iniciar('historia');j=app.jogo;j.recolocar(pos);j.camera=j.camera_y=0
    j.notificar('Núcleo recolhido. A tocha pode receber luz.');j.ensino_ate=0
    r=avisos.caixa(j)
    assert not r.colliderect(j.lume.rect.inflate(28,28))
    assert r.top<200 and r.left>=0 and r.right<=960


def test_sem_faixa_inferior_ou_objetivo_em_hud(app,monkeypatch):
    app.iniciar('historia');j=app.jogo
    j.aviso_t=0;j.ensino_ate=0
    s=pygame.Surface((960,540));s.fill((27,31,35))
    base=pygame.image.tobytes(s.subsurface((0,470,960,70)),'RGB')
    escritos=[]
    def espiar(surface,msg,x,y,*args,**kw):escritos.append((msg,x,y))
    monkeypatch.setattr('src.paisagem.texto',espiar)
    hud(s,j)
    assert all(j.objetivo not in str(msg) for msg,_,_ in escritos)
    assert pygame.image.tobytes(s.subsurface((0,470,960,70)),'RGB')==base
    assert not avisos.conteudo(j)


def test_objetivo_centralizado_acima_do_mapa_e_fechamento_m(app,monkeypatch):
    app.iniciar('historia');app.jogar();j=app.jogo;j.update(.02)
    antes=(set(j.explorado),set(j.cartografia));escritos=[]
    original=telas.texto
    def espiar(s,msg,x,y,*args,**kw):
        escritos.append((msg,x,y,args));return original(s,msg,x,y,*args,**kw)
    monkeypatch.setattr(telas,'texto',espiar)
    app.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_m));app.desenhar()
    objetivo=[d for d in escritos if d[0] in j.objetivo]
    assert objetivo and all(x==480 and y<QUADRO.top and 'centerx' in args for _,x,y,args in objetivo)
    assert antes==(set(j.explorado),set(j.cartografia))
    app.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_m));assert app.estado=='jogo'


def test_tutorial_curto_tem_detalhe_no_mapa(app):
    app.iniciar('historia');app.jogar();j=app.jogo
    j.recolocar((2000,442));j.update(.02)
    assert j.ensino_id=='menus' and len(j.ensino_texto)<120
    assert 'botão direito' in j.ensino_detalhe and 'WASD' in j.ensino_detalhe
    assert j.ensino_ate-j.tempo<=6.01


def test_sinal_de_descida_respeita_luz_e_camera_nao_revela_sala(app):
    j=Jornada();j.recolocar((1640,442));j.camera=1160
    for _ in range(60):j.update(1/60)
    assert 90<j.camera_y<160
    assert any(r.top==442 and r.collidepoint(1640,445) for r in sinalizacao.descidas(j))
    assert not conhecida(j,1800,1250)
    s=pygame.Surface((960,1400));s.fill('black');j.lume.energia=0
    sinalizacao.desenhar(s,j,j.camera);assert not any(pygame.image.tobytes(s,'RGB'))
    j.lume.energia=100;sinalizacao.desenhar(s,j,j.camera)
    assert any(pygame.image.tobytes(s,'RGB'))


def test_grade_com_camera_nova_desce_e_retorna_por_comandos():
    p=percurso();p.ir(1640);j=p.jogo
    for y in (542,642,742,842):
        p.tick(baixo=True,salto=True);p.esperar(60)
        assert p.lume.rect.bottom==y
        assert 190<p.lume.rect.centery-j.camera_y<350
    for y in (742,642,542,442):
        p.ir(1640,pular=True);assert p.lume.rect.bottom==y
    assert not j.em_vertical and j.etapa==0


def test_perda_de_foco_pausa_e_limpa_ataque_pendente(app):
    app.iniciar('historia');app.jogar()
    app.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_j))
    app.evento(pygame.event.Event(pygame.WINDOWFOCUSLOST))
    assert app.estado=='pausa' and not app.bordas
    app.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_p))
    from collections import defaultdict
    app.atualizar(1/60,presso=defaultdict(bool))
    assert app.jogo.lume.arma.serie==0
