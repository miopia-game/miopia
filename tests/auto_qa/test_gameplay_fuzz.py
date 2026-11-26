"""Playtests determinísticos pelo fluxo real de eventos, sem relógio de parede."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
from collections import defaultdict
from dataclasses import replace
import gc,math,random,tracemalloc
import pygame
import pytest
from src.travessia import Jornada,Lume,Comando
from src.fases import CHAO,SAIDA,Terreno
from src.ensaios import ENSAIOS


def eventos_do_quadro(a,teclas,eventos=()):
    for tipo,key in eventos:pygame.event.post(pygame.event.Event(tipo,key=key))
    for e in pygame.event.get():
        if e.type in (pygame.KEYDOWN,pygame.KEYUP):teclas[e.key]=e.type==pygame.KEYDOWN
        a.evento(e)


def quadro(a,teclas,eventos=(),dt=1/60,render=False):
    eventos_do_quadro(a,teclas,eventos)
    a.atualizar(dt,presso=teclas)
    if render:a.desenhar()


def toque(a,teclas,key,dt=1/60):
    quadro(a,teclas,[(pygame.KEYDOWN,key),(pygame.KEYUP,key)],dt)


def quantidades(j):
    proj=sum(len(e.projeteis) for e in j.inimigos)
    return len(j.inimigos),proj,len(j.vestigios)


def invariante(j,contexto):
    l=j.lume
    assert all(math.isfinite(v) for v in (*l.rect,l.vx,l.vy,l.vida,l.energia)),contexto
    assert 0<=l.vida<=100 and 0<=l.energia<=100,contexto
    largura=4608 if j.em_vertical else j.fase.width
    assert -.01<=l.rect.left<=largura-l.rect.w+.01,contexto
    if j.estado=='jogando':assert l.rect.top<=j.altura_mundo+28,contexto
    inimigos,proj,halos=quantidades(j)
    assert inimigos<50 and proj<160 and halos<=5,(contexto,quantidades(j))


def test_estabilidade_3000_quadros_memoria_e_entidades(app):
    app.iniciar('historia');app.jogar();t=defaultdict(bool)
    for _ in range(180):quadro(app,t,render=True)
    gc.collect();tracemalloc.start();inicio=tracemalloc.get_traced_memory()[0]
    entidades=quantidades(app.jogo)[0]
    try:
        for n in range(3000):
            quadro(app,t,render=n%30==0)
            invariante(app.jogo,('estabilidade',n))
            assert app.estado=='jogo'
        gc.collect();final=tracemalloc.get_traced_memory()[0]
        assert final-inicio<3_000_000,('memória Python retida',inicio,final)
        assert quantidades(app.jogo)[0]==entidades
    finally:tracemalloc.stop()


@pytest.mark.parametrize('semente',[9101,9102,9103])
def test_fuzz_1000_quadros_teclas_simultaneas_e_lag(app,semente):
    rng=random.Random(semente);t=defaultdict(bool)
    indice=next(i for i,e in enumerate(ENSAIOS) if e.nome=='Clareira da Vigília')
    app.comecar_ensaio(indice)
    keys=(pygame.K_a,pygame.K_d,pygame.K_s,pygame.K_SPACE,pygame.K_j,pygame.K_l,
          pygame.K_k,pygame.K_e,pygame.K_q,pygame.K_f,pygame.K_LSHIFT,pygame.K_LCTRL,pygame.K_p,pygame.K_m)
    preso=0;quadros_jogados=0
    for n in range(1100):
        eventos=[]
        for key in rng.sample(keys,rng.randint(0,5)):
            eventos.append((pygame.KEYUP if t[key] else pygame.KEYDOWN,key))
        if n%45==0:eventos.extend([(pygame.KEYDOWN,pygame.K_a),(pygame.KEYDOWN,pygame.K_d)])
        if app.estado=='morte' and app.relogio-app.morte_desde>.4:
            eventos=[(pygame.KEYUP,k) for k,v in t.items() if v]+[(pygame.KEYDOWN,pygame.K_RETURN),(pygame.KEYUP,pygame.K_RETURN)]
        if app.estado=='jogo' and app.jogo.dialogo and n%9==0:eventos.append((pygame.KEYDOWN,pygame.K_RETURN))
        if app.jogo is None:
            # Espaço e S também navegam na pausa e podem escolher voltar ao
            # menu. Reabrir um ensaio real, sem atribuir um Jornada de mentira.
            app.comecar_ensaio(indice)
            eventos=[(pygame.KEYUP,k) for k,v in t.items() if v]
        dt=.15 if n%71==0 else 1/60
        quadro(app,t,eventos,dt,render=n%37==0)
        if app.jogo is None:
            assert app.estado in ('menu','ensaios'),('retorno sem jogo',semente,n,app.estado)
            continue
        j=app.jogo;contexto=('fuzz',semente,n,app.estado,tuple(j.lume.rect),eventos)
        invariante(j,contexto)
        if app.estado=='jogo':quadros_jogados+=1
        if j.estado=='jogando' and not j.lume.em_corda and j.destino_vertical is None:
            corpo=j.lume.rect
            colisao=any(not p.atravessavel and corpo.clip(p.rect).w>.5 and corpo.clip(p.rect).h>.5 for p in j.solidos)
            preso=preso+1 if colisao else 0
            assert preso<=10,('penetração persistente',contexto)
        else:preso=0
    assert quadros_jogados>100,('fuzzer não exercitou gameplay',semente,quadros_jogados)


class SalaColisao(Jornada):
    def __init__(self,solidos):
        self._solidos=solidos
        super().__init__()
        self.inimigos=[]
        self.fase=replace(self.fase,width=960)
    @property
    def solidos(self):return self._solidos
    @property
    def objetos(self):return ()


@pytest.mark.parametrize('dt',[1/120,1/60,.05,.15])
def test_dash_nao_atravessa_parede_de_um_pixel(dt):
    piso=Terreno(pygame.Rect(0,442,960,100),'chao')
    parede=Terreno(pygame.Rect(240,0,1,442),'parede')
    j=SalaColisao((piso,parede));j.recolocar((200,442))
    for n in range(40):
        j.update(dt,Comando(mover=1,deslize=n==0))
        assert j.lume.rect.right<=240.01,(dt,n,j.lume.rect)
        assert j.estado=='jogando'


@pytest.mark.parametrize('dt',[1/60,.15])
def test_queda_terminal_nao_atravessa_plataforma_fina(dt):
    piso=Terreno(pygame.Rect(0,442,960,1),'chao')
    j=SalaColisao((piso,));j.recolocar((400,300));j.lume.chao=False;j.lume.vy=710
    for n in range(70):
        j.update(dt)
        assert j.lume.rect.bottom<=442.01,(dt,n,j.lume.rect)
    assert j.lume.chao


def test_spam_de_espaco_nao_cria_salto_duplo_infinito():
    l=Lume(300,442);saltos=0
    for n in range(150):
        cmd=Comando(salto=n%15==0,segurar_salto=True)
        saltos+=l.movimento(1/120,cmd,(),0,True)
    assert saltos==2


def test_ciclo_menu_pausa_game_over_reinicio_e_transicao_5_vezes(app):
    t=defaultdict(bool)
    for ciclo in range(5):
        app.menu();nomes=app.menu_nomes()
        app.selecao=nomes.index('Nova história' if 'Nova história' in nomes else 'Jogar história')
        toque(app,t,pygame.K_RETURN)
        if app.estado=='confirmar':app.selecao=1;toque(app,t,pygame.K_RETURN)
        assert app.estado=='prologo';toque(app,t,pygame.K_ESCAPE);assert app.estado=='jogo'
        toque(app,t,pygame.K_p);assert app.estado=='pausa'
        # Tecla solta durante a pausa não pode vazar para o retorno.
        quadro(app,t,[(pygame.KEYDOWN,pygame.K_d),(pygame.KEYUP,pygame.K_d),
                     (pygame.KEYDOWN,pygame.K_j),(pygame.KEYUP,pygame.K_j)])
        toque(app,t,pygame.K_p)
        for _ in range(20):quadro(app,t)
        assert app.jogo.lume.arma.serie==0 and abs(app.jogo.lume.vx)<.01
        j=app.jogo;e=j.inimigos[0];e.vida=1;e.rect.x+=80
        j.lume.vida=0;j.lume.vidas=1
        quadro(app,t);assert app.estado=='morte'
        for _ in range(26):quadro(app,t)
        eventos_do_quadro(app,t,[(pygame.KEYDOWN,pygame.K_RETURN),(pygame.KEYUP,pygame.K_RETURN)])
        assert app.estado=='jogo'
        assert (j.lume.vida,j.lume.energia)==(100,100)
        assert e.vida==e.max_vida and e.rect.midbottom==e.origem
        # Fixture abre a saída para testar só a troca de região; a campanha
        # completa por controles é verificada em test_campanha.
        j.flags.update(('raiz','chefe'));j.recolocar((SAIDA,CHAO))
        toque(app,t,pygame.K_e);assert (j.etapa,app.estado)==(1,'capitulo')
        toque(app,t,pygame.K_RETURN);assert app.estado=='jogo'
        app.desenhar();invariante(j,('ciclo',ciclo))
