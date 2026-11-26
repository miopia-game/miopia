"""S10: dicas inteiras sem painel ilimitado e consulta pelo mapa normal."""
import pygame
import pytest
from src import avisos,telas
from src.ensaios import ENSAIOS
from src.fases import CHAO

LONGOS=('Oficina dos Espinhos','Caruncho do Viveiro','Jardim do Último Sinal',
        'Clareira da Vigília','Globos e tochas')


def observar_texto(monkeypatch,modulo):
    original=modulo.texto;saida=[]
    def registrar(s,msg,*args,**kw):
        rect=original(s,msg,*args,**kw);saida.append((msg,rect));return rect
    monkeypatch.setattr(modulo,'texto',registrar)
    return saida


@pytest.mark.parametrize('nome',LONGOS)
def test_pista_aparece_inteira_sem_cobrir_lume(app,monkeypatch,nome):
    indice=next(i for i,e in enumerate(ENSAIOS) if e.nome==nome)
    app.comecar_ensaio(indice);j=app.jogo
    escritos=observar_texto(monkeypatch,avisos)
    avisos.desenhar(app.tela,j)
    corpo=[(msg,r) for msg,r in escritos if msg!='Na trilha' and not msg.startswith('E · ')]
    assert ' '.join(msg for msg,_ in corpo)==' '.join(ENSAIOS[indice].pista.split())
    assert len(corpo)==(3 if nome=='Jardim do Último Sinal' else 5)
    painel=avisos.caixa(j,avisos.altura(j.aviso,j.interacao))
    assert all(painel.contains(r) for _,r in corpo)
    assert not painel.colliderect(j.lume.rect.move(-j.camera,-j.camera_y).inflate(28,28))


def test_aviso_muito_longo_marca_corte_e_mantem_limite(app,monkeypatch):
    app.iniciar('historia');j=app.jogo;j.notificar('Uma orientação muito longa para uma clareira. '*30)
    escritos=observar_texto(monkeypatch,avisos);avisos.desenhar(app.tela,j)
    corpo=[(msg,r) for msg,r in escritos if msg!='Na trilha' and not msg.startswith('E · ')]
    assert len(corpo)==5 and corpo[-1][0].endswith(('…','...'))
    assert avisos.altura(j.aviso,j.interacao)<=147


def test_interacao_fica_na_cena_e_aviso_muda_de_canto(app,monkeypatch):
    app.iniciar('historia');j=app.jogo
    j.recolocar((163,CHAO))  # E junto a Mimo, sem substituir os objetos reais.
    j.camera=j.lume.rect.centerx-730;j.camera_y=260
    j.notificar(next(e.pista for e in ENSAIOS if e.nome=='Clareira da Vigília'))
    escritos = observar_texto(monkeypatch, avisos)
    locais = []
    original = avisos.dica_local
    def observar(s, tecla, rotulo, ponto):
        locais.append((tecla, rotulo, ponto))
        original(s, tecla, rotulo, ponto)
    monkeypatch.setattr(avisos, "dica_local", observar)

    avisos.desenhar(app.tela, j)
    corpo = [r for msg, r in escritos if msg != 'Na trilha']
    assert len(corpo) == 5 and locais == [("E", "Ouvir", (730, CHAO-71-260))]
    assert avisos.caixa(j, avisos.altura(j.aviso, '')).left == 18


@pytest.mark.parametrize('nome',LONGOS)
def test_m_mantem_pista_completa_apos_aviso_expirar(app,monkeypatch,nome):
    from collections import defaultdict
    indice=next(i for i,e in enumerate(ENSAIOS) if e.nome==nome)
    app.comecar_ensaio(indice)
    # Encurtar só a espera do aviso; expiração e entrada M são as da App real.
    app.jogo.notificar(ENSAIOS[indice].pista,.001)
    app.atualizar(1/60,presso=defaultdict(bool));assert not app.jogo.aviso
    antes=(set(app.jogo.explorado),set(app.jogo.cartografia))
    escritos=observar_texto(monkeypatch,telas)
    app.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_m));app.desenhar()
    cabecalho=' '.join(msg for msg,r in escritos if r.top in (132,153))
    assert 'Campo de testes' in cabecalho and nome in cabecalho
    detalhe=' '.join(msg for msg,r in escritos if r.top in (180,196))
    assert detalhe==' '.join(ENSAIOS[indice].pista.split())
    assert antes==(set(app.jogo.explorado),set(app.jogo.cartografia))
    app.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_m));assert app.estado=='jogo'


def test_campanha_mantem_detalhe_normal_e_marca_tem_prioridade(app,monkeypatch):
    from src.cartografia import alvo_local
    app.iniciar('historia');app.jogar()
    esperado=alvo_local(app.jogo).detalhe
    escritos=observar_texto(monkeypatch,telas)
    app.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_m));app.desenhar()
    assert ' '.join(msg for msg,r in escritos if r.top in (180,196))==' '.join(esperado.split())
    app.mapa_aviso='Marque apenas um caminho já descoberto.';app.mapa_aviso_ate=app.relogio+3
    escritos.clear();app.desenhar()
    assert any(msg==app.mapa_aviso for msg,_ in escritos)


def test_consulta_corte_mantem_recado_da_localizacao(app,monkeypatch):
    app.comecar_ensaio(next(i for i,e in enumerate(ENSAIOS) if e.nome=='Clareira da Vigília'))
    escritos=observar_texto(monkeypatch,telas)
    telas.pagina_mapa(app,app.tela,corte=True)
    assert 'Lume está na superfície.' in ' '.join(msg for msg,r in escritos if r.top in (180,196))


def test_descida_e_ensinada_antes_da_primeira_grade(app):
    from collections import defaultdict
    app.iniciar('historia');app.jogar();j=app.jogo;j.recolocar((1510,CHAO))
    teclas=defaultdict(bool);teclas[pygame.K_d]=True
    for _ in range(30):
        app.atualizar(1/60,presso=teclas)
        if getattr(j,'ensino_id','')=='grade':break
    assert j.ensino_id=='grade' and j.lume.rect.centerx<1580
    assert 'S + Espaço' in j.ensino_texto


def test_reticencias_nao_reprocessam_toda_a_cauda_do_aviso(app,monkeypatch):
    from src import cartografia
    app.iniciar('historia');j=app.jogo
    j.notificar('Uma orientação muito longa para uma clareira. '*30)
    original=cartografia.fonte;medicoes=[]
    class FonteMedida:
        def __init__(self,real):self.real=real
        def size(self,msg):
            medicoes.append(len(msg))
            return self.real.size(msg)
    # Instrumenta o trabalho das fontes reais, sem limiar de tempo de CPU.
    monkeypatch.setattr(cartografia,'fonte',lambda *a,**kw:FonteMedida(original(*a,**kw)))
    avisos.desenhar(app.tela,j)
    assert medicoes and sum(medicoes)<2000,('caracteres medidos para encurtar',sum(medicoes))
