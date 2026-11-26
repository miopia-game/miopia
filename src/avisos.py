"""Avisos breves no canto; a missão completa pertence à tela do mapa."""
import pygame
from .ilustracao import dica_local, dica_teclado, painel, tamanho_texto, texto, linhas, AMBAR, PALIDO

MAX_LINHAS=5


def linhas_corpo(msg):
    corpo=linhas(msg,238,13)
    if len(corpo)>MAX_LINHAS:
        from .cartografia import texto_curto
        restante=corpo[MAX_LINHAS-1]+'…'
        corpo=corpo[:MAX_LINHAS-1]+[texto_curto(restante,238,13)]
    return corpo


def caixa(j,altura=126):
    jogador=j.lume.rect.move(-j.camera,-j.camera_y).inflate(28,28)
    direita=pygame.Rect(676,94,266,altura)
    baixo = 180 if j.lume.custo_em_vida(j.lume.custo_clarao) else 164
    esquerda=pygame.Rect(18,baixo,266,altura)
    return esquerda if direita.colliderect(jogador) else direita


def conteudo(j):
    if j.dialogo:return None
    from .travessia_fagulha import FORA_DA_MARCA
    if j.aviso_t>0 and j.aviso==FORA_DA_MARCA:
        return 'Fagulha fora da marca',dica_teclado(j.aviso)
    ensino=getattr(j,'ensino_ate',0)>j.tempo
    if ensino:
        from .tutorial import praticado
        titulo='Praticado' if praticado(j) else j.ensino_titulo
        return titulo,dica_teclado(j.ensino_texto)
    if j.aviso_t>0 and j.aviso and j.aviso!=j.fase.name:
        return 'Na trilha',dica_teclado(j.aviso)
    from .desvios_fagulha import pista
    indicio = pista(j)
    if indicio:
        return 'Marca na casca',dica_teclado(indicio)
    return None


def usa_interacao_local(j):
    return (j.modo == "historia" and not getattr(j, "campo_testes", False)
            and not hasattr(j, "sala_id") and (not j.boss or j.boss.vencido))


def pista_interacao(j, descricao):
    if not descricao or j.lume.em_corda:
        return None
    objeto = j.proximo()
    if objeto is None:
        return None
    y = j.lume.rect.top
    if objeto.tipo == "corda":
        from .fases import CHAO
        return "E", "Descer" if j.lume.rect.bottom < CHAO - 120 else "Subir", (objeto.x, y)
    if objeto.tipo == "npc":
        return "E", "Ouvir", (objeto.x, objeto.y - 71)
    rotulo = "Recolher mochila" if objeto.id == "encomenda_mimo" else descricao
    return "E", rotulo, (objeto.x, min(y, objeto.y - 20))


def altura(msg,interacao):
    rodape = 12 + tamanho_texto(12) if interacao else 0
    return 38+len(linhas_corpo(msg))*(tamanho_texto(13)+4)+rodape


def ocupa_esquerda(j):
    aviso = conteudo(j)
    interacao = '' if usa_interacao_local(j) else j.interacao
    if aviso is None and not interacao:return False
    return caixa(j,altura(aviso[1] if aviso else '',interacao)).x<100


def desenhar(s,j):
    if j.dialogo:return
    aviso = conteudo(j)
    interacao = j.interacao
    if usa_interacao_local(j):
        acao = pista_interacao(j, interacao)
        if acao:
            tecla, rotulo, (x, y) = acao
            dica_local(s, tecla, rotulo, (x - j.camera, y - j.camera_y))
        interacao = ''
    if aviso is None and not interacao:return
    titulo,msg=aviso if aviso else ('Perto de Lume','')
    corpo=linhas_corpo(msg)
    r=caixa(j,altura(msg,interacao));painel(s,r,False)
    texto(s,titulo,r.x+12,r.y+8,14,AMBAR,'forte')
    for n,l in enumerate(corpo):texto(s,l,r.x+12,r.y+32+n*(tamanho_texto(13)+4),13,PALIDO)
    if interacao:
        from .cartografia import texto_curto
        texto(s,texto_curto(dica_teclado('E · ')+interacao,240,12,'forte'),r.x+12,r.bottom-9-tamanho_texto(12),12,AMBAR,'forte')
