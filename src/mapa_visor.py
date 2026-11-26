"""Enquadramento do mapa; navegar é uma ação de interface, nunca descoberta."""
from copy import copy
from . import pygame_hd as pygame
from .cartografia import dimensoes

QUADRO=pygame.Rect(85,231,780,202)


def contexto(j,corte=False):
    if not corte or j.em_vertical:return j
    # A página da figueira pode ser consultada na superfície. O jogador não
    # está nessa região: não desenhar sua posição superficial sobre o Corte.
    outro=copy(j);outro.em_vertical=True;outro._mapa_sem_lume=True
    return outro


def foco(j):
    if getattr(j,'_mapa_sem_lume',False):
        from .corte_vertical import MARCOS
        return MARCOS[j.marco_vertical]
    return j.lume.rect.center


def regiao(j):return 'corte' if j.em_vertical else f'{j.volta}:{j.etapa}'


class Visor:
    def __init__(self):
        self.regiao=None;self.zoom=1.;self.centro=pygame.Vector2();self.arrastando=False
        self.chave_cache=None;self.camada=None;self.construcoes=0

    def preparar(self,j,centralizar=False):
        if self.regiao!=regiao(j):
            self.regiao=regiao(j);self.zoom=3. if j.em_vertical else 2.
            centralizar=True
        if centralizar:self.centro.update(foco(j));self.arrastando=False
        self.limitar(j)

    def escala(self,j):
        w,h=dimensoes(j)
        return min(QUADRO.w/w,QUADRO.h/h)*self.zoom

    def limitar(self,j):
        w,h=dimensoes(j);esc=self.escala(j)
        for eixo,total,meio in ((0,w,QUADRO.w/esc/2),(1,h,QUADRO.h/esc/2)):
            self.centro[eixo]=total/2 if meio>=total/2 else max(meio,min(total-meio,self.centro[eixo]))

    def janela(self,j):
        esc=self.escala(j);w,h=QUADRO.w/esc,QUADRO.h/esc
        return pygame.FRect(self.centro.x-w/2,self.centro.y-h/2,w,h)

    def mundo(self,j,pos):
        r=self.janela(j);esc=self.escala(j)
        return r.x+(pos[0]-QUADRO.x)/esc,r.y+(pos[1]-QUADRO.y)/esc

    def ampliar(self,j,passos,pos=None):
        pos=QUADRO.center if pos is None else pos
        antes=pygame.Vector2(self.mundo(j,pos))
        self.zoom=max(1.,min(10.,self.zoom*1.35**max(-4,min(4,passos))))
        depois=pygame.Vector2(self.mundo(j,pos));self.centro+=antes-depois
        self.limitar(j)

    def mover(self,j,dx,dy):
        self.centro+=pygame.Vector2(dx,dy)/self.escala(j);self.limitar(j)

    def desenhar(self,s,j):
        from .cartografia import mapa_local,alvo_local
        from .ilustracao import alto_contraste, tamanho_texto
        r=self.janela(j);alvo=alvo_local(j)
        assinatura=(regiao(j),dimensoes(j),tamanho_texto(14),alto_contraste(),tuple(r),frozenset(j.explorado),frozenset(j.cartografia),frozenset(j.pisadas_escuta),
                    tuple((g['regiao'],g['x'],g['y']) for g in j.globos),frozenset(j.tochas),frozenset(j.nucleos),
                    frozenset(j.flags),j.missao,j.concluida,tuple(sorted(j.bolsa.estoque.items())),
                    tuple((k,v['oficio']) for k,v in sorted(j.sobreviventes.items())),
                    tuple((m['celula'],m['tipo']) for m in j.marcas),
                    tuple((tuple(t.rect),t.tipo) for t in j.solidos),
                    tuple((o.id,o.tipo,o.x,o.y) for o in j.objetos),
                    (alvo.id,alvo.nome,alvo.x,alvo.y) if alvo else None,
                    tuple(j.lume.rect),j.camera,j.camera_y,getattr(j,'_mapa_sem_lume',False))
        if self.camada is None:
            self.camada = pygame.Surface(QUADRO.size).pixels
        desenho = pygame.nativa(self.camada, QUADRO.size)
        if assinatura!=self.chave_cache:
            mapa_local(desenho,j,desenho.get_rect(),janela_mundo=r)
            self.chave_cache=assinatura;self.construcoes+=1
        pygame.blit(s,desenho,QUADRO)


def ativo(a):
    return a.estado=='diario' and a.jogo is not None and not hasattr(a.jogo,'sala_id') and (
        a.pagina==0 or a.pagina==2 and bool(a.jogo.cartografia))


def evento(a,e):
    if not ativo(a):return False
    j=contexto(a.jogo,a.pagina==2);v=a.mapa_visor;v.preparar(j)
    if e.type==pygame.MOUSEBUTTONUP:
        v.arrastando=False;return e.button==1
    if e.type==pygame.MOUSEWHEEL:
        pos=getattr(e,'pos',pygame.mouse.get_pos())
        if not QUADRO.collidepoint(pos):return False
        v.ampliar(j,e.y,pos);return True
    if e.type==pygame.MOUSEBUTTONDOWN and QUADRO.collidepoint(e.pos):
        if e.button==1:v.arrastando=True;return True
        if e.button in (4,5):v.ampliar(j,1 if e.button==4 else -1,e.pos);return True
        if e.button==3:
            from .marcas_mapa import alternar,TIPOS
            ok,msg=alternar(j,v.mundo(j,e.pos),TIPOS[a.mapa_tipo])
            a.mapa_aviso=msg;a.mapa_aviso_ate=a.relogio+4
            if ok:a.salvar_campanha();a.som('pagina')
            return True
    if e.type==pygame.MOUSEMOTION and v.arrastando:
        v.mover(j,-e.rel[0],-e.rel[1]);return True
    if e.type==pygame.KEYDOWN and not getattr(e,'repeat',False):
        if e.key in (pygame.K_EQUALS,pygame.K_PLUS,pygame.K_KP_PLUS):v.ampliar(j,1);return True
        if e.key in (pygame.K_MINUS,pygame.K_KP_MINUS):v.ampliar(j,-1);return True
        if e.key==pygame.K_c:v.preparar(j,True);return True
        if e.key==pygame.K_v:a.mapa_tipo=(a.mapa_tipo+1)%4;return True
        passos={pygame.K_w:(0,-65),pygame.K_s:(0,65),pygame.K_a:(-65,0),pygame.K_d:(65,0)}
        if e.key in passos:v.mover(j,*passos[e.key]);return True
    return False
