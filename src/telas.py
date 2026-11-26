"""Menus e páginas desenhados em 960 × 540. As áreas clicáveis são as linhas visíveis."""
import math
from functools import lru_cache
import pygame
from .ensaios import ENSAIOS, INDICE_ARANHA
from . import abertura_bosque, ambiental, arte_ilustrada
from .controles import ACOES, ROTULOS_PAD, nome_tecla
from .narrativa import RAIZES
from .ilustracao import (AMBAR, OSSO, PALIDO, TEAL, ROMANOS, brilho, dica_teclado, imagem, linhas,
                         losango, painel, paragrafo, placa, tamanho_texto, texto)
from .paisagem import NPC_TAM, arte_npc
from .roteiro import CONTROLES, FINAL, PROLOGO, epilogo, linha_da_viagem, texto_travessia

SEMENTE_ANTERIOR=pygame.Rect(466,321,38,32)
SEMENTE_SEGUINTE=pygame.Rect(643,321,38,32)
VER_TENTATIVA=pygame.Rect(466,370,317,36)

@lru_cache(maxsize=1)
def _fundo_menu():
    fundo = abertura_bosque.fundo_sombrio(960,540).copy()
    sombra = pygame.Surface((502,540),pygame.SRCALPHA)
    for x in range(sombra.get_width()):
        pygame.draw.line(sombra,(7,12,17,round(238*(1-x/502)**1.3)),(x,0),(x,539))
    fundo.blit(sombra,(0,0))
    return fundo


def fundo(s,a):
    s.blit(_fundo_menu(),(0,0))
    for n in range(9):
        x=450+n*54+math.sin(a.relogio*.45+n)*14
        y=(160+n*41-a.relogio*(4+n%3))%480
        pygame.draw.circle(s,(171,155,107),(int(x),int(y)),1)


def opcoes(a,s,nomes,x,y,w,passo=34,tam=18,limite=None):
    from .cartografia import texto_curto
    a.alvos=[]
    primeiro=max(0,min(a.selecao-(limite or len(nomes))//2,len(nomes)-(limite or len(nomes))))
    for i,nome in enumerate(nomes):
        if limite is not None and not primeiro <= i < primeiro+limite:
            a.alvos.append(pygame.Rect(0,0,0,0))
            continue
        r=pygame.Rect(x,y+(i-primeiro)*passo,w,passo-2)
        ativo=a.selecao==i
        if ativo:
            s.blit(placa(r.w,r.h,199),r)
            pygame.draw.line(s,(129,124,94),r.bottomleft,r.bottomright)
            losango(s,r.x+12,r.centery,4)
        estilo="forte" if ativo else "normal"
        texto(s,texto_curto(nome,w-34,tam,estilo),r.x+26,r.y+(r.h-tamanho_texto(tam))//2-3,
              tam,AMBAR if ativo else OSSO,estilo)
        a.alvos.append(r)


def menu(a,s):
    fundo(s,a)
    texto(s,"Miopia",53,39,96,OSSO,"titulo")
    texto(s,"A ÚLTIMA LUZ DA MATA",62,147,17,AMBAR,"forte")
    pygame.draw.line(s,TEAL,(62,183),(282,183))
    losango(s,289,183,3)
    opcoes(a,s,a.menu_nomes(),55,203,270,32,18)
    guia="Direcional  escolher     A  confirmar" if a.controles.ultimo_pad else "Setas  escolher     Enter  confirmar"
    texto(s,guia,60,501,14,PALIDO)
    if a.mem.aviso: texto(s,a.mem.aviso,340,504,13,AMBAR)


def livro(a,s,titulo,supra=""):
    fundo(s,a)
    s.blit(placa(960,540,147),(0,0))
    painel(s,(52,35,856,470))
    if supra: texto(s,supra,81,54,13,AMBAR,"forte")
    texto(s,titulo,80,74,39,OSSO,"titulo")


def ensaios(a,s):
    livro(a,s,"Campo de testes","MIOPIA")
    texto(s,"Entre direto no trecho. Sua campanha fica salva à parte.",83,130,17,PALIDO)
    nomes=[c.nome for c in ENSAIOS]+["Voltar"]
    opcoes(a,s,nomes,78,160,355,26,17,limite=11)
    texto(s,f'{a.selecao+1} / {len(nomes)}',873,144,11,PALIDO,'normal','right')
    if a.selecao<len(ENSAIOS):
        c=ENSAIOS[a.selecao]
        texto(s,c.nome,467,196,24,AMBAR,"titulo")
        paragrafo(s,dica_teclado(c.pista),467,242,386,18)
        if a.selecao==INDICE_ARANHA:
            for botao,sinal in ((SEMENTE_ANTERIOR,"‹"),(SEMENTE_SEGUINTE,"›")):
                painel(s,botao,False)
                texto(s,sinal,botao.centerx,botao.y+1,22,AMBAR,"forte","centerx")
            texto(s,f"Semente {a.semente_aranha}",573,328,16,OSSO,"forte","centerx")
            if a.ultimo_replay is not None:
                painel(s,VER_TENTATIVA,False)
                texto(s,"V   Assistir à última tentativa",480,379,16,AMBAR,"forte")
                paragrafo(s,a.aviso_replay,467,412,380,14,PALIDO)
    texto(s,"Enter   abrir trecho      Esc   voltar",82,459,15,PALIDO)


def ajuda(a,s,rodape='Esc ou Enter   ·   voltar'):
    livro(a,s,"Controles","CADERNO DE CAMPO")
    for i,(key,acao) in enumerate(CONTROLES):
        if i < 11:
            key=dica_teclado(key)
        if i in (5, 6):
            acao=dica_teclado(acao)
        texto(s,key,86,130+i*22,16,AMBAR,"forte")
        texto(s,acao,302,130+i*22,14,OSSO)
    texto(s,dica_teclado("S + K"),86,439,14,AMBAR,"forte")
    texto(s,"Faz o clarão frear a queda. Consome brilho.",302,439,13,OSSO)
    texto(s,dica_teclado("G"),86,459,14,AMBAR,"forte")
    texto(s,"Lança uma fagulha à frente. Ilumina pousos, revela marcas e atrai alguns inimigos.",302,459,13,OSSO)
    texto(s,rodape,84,482,15,PALIDO)


def opcoes_ajustes(a,s):
    livro(a,s,"Ajustes","MIOPIA")
    p=a.mem.prefs
    labels=[f"Dificuldade  ·  {a.dificuldade_escolhida.capitalize()}",
            f"Ambiência  ·  {round(p['musica']*100)}%",f"Efeitos  ·  {round(p['efeitos']*100)}%",
            "Brilho da mata  ·  "+("Mínimo","Noturno","Médio","Alto")[p["brilho"]],
            "Som  ·  "+("silenciado" if p["mudo"] else "ligado"),"Controles","Acessibilidade","Voltar"]
    opcoes(a,s,labels,77,127,390,32,18)
    from .paisagem import mascara_luz, nevoa_distante
    # Demonstra foco e fundo escuro, sem a antiga amostra de breu absoluto.
    amostra = imagem("fundo_0.jpg",340,188).copy()
    borrado=pygame.Surface(amostra.get_size())
    nevoa_distante(amostra,borrado,pygame.Surface((102,56)),p["brilho"])
    mascara = pygame.Surface(amostra.get_size())
    mascara.fill((0,0,0))
    mascara.blit(mascara_luz(66,p["brilho"]),(104,30),special_flags=pygame.BLEND_RGB_MAX)
    inversa=pygame.Surface(amostra.get_size());inversa.fill((255,255,255))
    inversa.blit(mascara,(0,0),special_flags=pygame.BLEND_RGB_SUB)
    borrado.blit(inversa,(0,0),special_flags=pygame.BLEND_RGB_MULT)
    amostra.blit(mascara,(0,0),special_flags=pygame.BLEND_RGB_MULT)
    amostra.blit(borrado,(0,0),special_flags=pygame.BLEND_RGB_ADD)
    s.blit(amostra,(517,146))
    texto(s,"Visibilidade na mata",517,344,15,PALIDO)
    texto(s,"Esquerda / direita  ajustar     Enter ou clique  avançar",82,410,16,PALIDO)
    if a.ajustes_da_historia:
        j = a.jogo
        situacao = f"Ativa · {j.dificuldade.capitalize()}"
        if j.dificuldade_pendente:
            situacao += f"    |    {j.dificuldade_pendente.capitalize()} no próximo marco"
        else:
            situacao += "    |    Mudanças valem no próximo marco"
    else:
        situacao = "Preferência para novas histórias e ensaios."
    texto(s,situacao,82,448,16,PALIDO)


def remapeamento(a,s):
    livro(a,s,"Controles","AJUSTES")
    nomes = [f"{nome}   ·   {nome_tecla(a.controles.codigos(acao)[0])}   |   {ROTULOS_PAD[acao]}"
             for acao,(nome, _, _) in ACOES.items()]
    opcoes(a,s,[*nomes,"Restaurar teclas padrão","Voltar"],77,162,525,30,17,limite=9)
    texto(s,"Ação  ·  Teclado  |  Controle",84,128,15,PALIDO)
    paragrafo(s,"No controle, A confirma e B volta nos menus. O analógico esquerdo ou o direcional movem Lume.",628,166,235,16)
    texto(s,a.aviso_tecla or "Enter troca uma tecla. Esc volta.",84,459,16,AMBAR)


def acessibilidade(a,s):
    livro(a,s,"Acessibilidade","AJUSTES")
    p = a.mem.prefs
    opcoes(a,s,[f"Tamanho do texto  ·  {p['texto']}%",
                 "Alto contraste  ·  "+("Ligado" if p["contraste"] else "Desligado"),
                 "Clarões suaves  ·  "+("Ligados" if p["claroes_suaves"] else "Desligados"),
                 "Valores no HUD  ·  "+("Ligados" if p["numeros_hud"] else "Desligados"),
                 "Voltar"],77,134,415,41,19)
    texto(s,"Esquerda / direita ajusta · Esc volta",84,444,15,PALIDO)


def creditos(a,s):
    livro(a,s,"Créditos","MIOPIA")
    texto(s,"Projeto A3  ·  Universidade São Judas Tadeu",84,135,19,AMBAR,"forte")
    paragrafo(s,"Otávio Araújo Aredes Guedes, Caio Vidotte Vrech Sousa, Tiago Ribeiro Gomes, Thierry Henry Rocha da Silva, Victor Bersane Jasaitis e Iago Robert da Silva Andrade.",84,171,785,18)
    texto(s,"Arte e implementação",84,248,19,AMBAR,"forte")
    paragrafo(s,"Reformulação com Codex, ImageGen e pygame-ce. Tipografia Nunito e Liberation Serif, sob a licença SIL Open Font License.",84,279,780,17)
    texto(s,"Paisagem sonora",84,345,19,AMBAR,"forte")
    paragrafo(s,a.credito_audio,84,376,785,16)
    texto(s,"Esc ou Enter   ·   voltar",84,465,15,PALIDO)


def pausa(a,s):
    from .abertura_bosque import pausa as pausa_bosque
    pausa_bosque(a,s)


def morte(a,s):
    j=a.jogo
    s.blit(placa(960,540,174),(0,0))
    painel(s,(177,102,606,338))
    texto(s,"Você morreu",480,135,58,OSSO,"titulo","centerx")
    terminal=j.estado=="derrota"
    if terminal and j.modo=="historia" and a.ensaio is None:
        detalhe=FINAL["derrota"][1]
    else:
        detalhe=('A habilidade consumiu a última vida de Lume.' if j.motivo_morte=='sacrificio' else
                 'Lume caiu no vão.' if j.motivo_morte=='queda' else 'A vida de Lume se esgotou.')
        if a.ensaio is None:
            detalhe += (" Resta uma fagulha." if j.lume.vidas==1 else
                        f" Restam {j.lume.vidas} fagulhas." if j.lume.vidas else " A última fagulha se apagou.")
    paragrafo(s,detalhe,212,222,536,18,PALIDO)
    nome="Voltar ao último marco"
    if a.ensaio is not None:
        nome="Repetir o ensaio"
    voltar="Voltar ao campo de testes" if a.ensaio is not None else "Voltar ao menu"
    opcoes(a,s,[nome,voltar],209,328,540,40,19)


def replay(a,s):
    if a.reproducao is None:
        painel(s,(202,106,556,94))
        paragrafo(s,a.aviso_replay,223,118,512,17,OSSO)
        texto(s,"Esc   voltar ao campo",223,165,15,AMBAR)
    else:
        painel(s,(246,18,421,64),False)
        nome="Reprodução pausada" if a.replay_pausado else "Reprodução"
        texto(s,f"{nome}   ·   {a.jogo.tempo:.1f} s",456,24,17,AMBAR,"forte","centerx")
        texto(s,"Espaço   pausar / continuar      Esc   voltar",456,52,15,OSSO,"normal","centerx")


def confirmar(a,s):
    livro(a,s,a.conf_titulo,"MIOPIA")
    paragrafo(s,a.conf_msg,84,163,741,20)
    opcoes(a,s,["Cancelar",a.conf_acao],77,278,410,46)


def dialogo(a,s):
    j=a.jogo
    nome,msg=j.dialogo
    controle=a.controles.ultimo_pad
    avancar="RT / A" if controle else dica_teclado("E")+" / Enter"
    if j.escolha_resgate is not None:
        painel(s,(73,228,814,260))
        texto(s,nome,97,240,25,AMBAR,'titulo')
        paragrafo(s,a.fala_visivel,97,277,760,17,OSSO)
        ultima=a.pagina_fala==len(a.fala_paginas)-1 and a.letras==len(a.fala)
        if ultima:
            from .resgates import rotulos_trabalho
            nomes = rotulos_trabalho(j, j.escolha_resgate)
            opcoes(a,s,nomes,90,386,770,35,16)
            confirmar="A confirmar · B decidir depois" if controle else "Enter confirmar · Esc decidir depois"
            texto(s,'Cima / baixo escolher · '+confirmar,97,467,12,PALIDO)
        else:texto(s,f'{avancar} avançar · {a.pagina_fala+1}/{len(a.fala_paginas)}',863,465,12,PALIDO,'normal','right')
        return
    recuo=5*(tamanho_texto(17)-17)
    painel(s,(73,344-recuo,814,139+recuo))
    x=97
    if nome in arte_ilustrada.PERSONAGENS:
        arte_ilustrada.personagem(s,nome,126,459-recuo,82,78)
        x = 179
    elif nome in NPC_TAM:
        img=imagem(arte_npc(nome)+".png",76,70)
        s.blit(img,(88,379-recuo)); x=179
    rotulo, cor = arte_ilustrada.FUNCOES.get(nome, ("", AMBAR))
    nome_r = texto(s,nome,x,355-recuo,20,cor,"titulo")
    if rotulo:
        texto(s,rotulo,nome_r.right+14,360-recuo,12,PALIDO)
    paragrafo(s,a.fala_visivel,x,384-recuo,825-x,17,OSSO)
    texto(s,f'{avancar} avançar · {a.pagina_fala+1}/{len(a.fala_paginas)}',866,456,12,PALIDO,"normal","right")


def cena(a,s):
    titulo,msg,i=PROLOGO[a.quadro]
    img=imagem(f"fundo_{i}.jpg",1030,580)
    s.blit(img,(-30,-28))
    s.blit(placa(960,540,94),(0,0))
    painel(s,(0,302,960,238),False)
    texto(s,"PRÓLOGO     "+ROMANOS[a.quadro],65,323,14,AMBAR,"forte")
    texto(s,titulo,62,347,39,OSSO,"titulo")
    paragrafo(s,a.fala_visivel,65,411,810,19)
    texto(s,"Enter  avançar     Esc  pular prólogo",894,504,14,PALIDO,"normal","right")


def paginas_diario(a):
    return 2+bool(a.jogo.cartografia)+len(a.jogo.diario)+2*(a.ensaio is None)


def diario(a,s):
    j=a.jogo
    if a.ensaio==INDICE_ARANHA:
        livro(a,s,j.fase.name,"CADERNO DE ENSAIO")
        texto(s,f"Semente {j.semente}   ·   {j.dificuldade}",85,148,20,AMBAR,"titulo")
        texto(s,"Lume em âmbar. A pedra entre o abrigo e a aranha bloqueia a visão.",85,186,17,PALIDO)
        for tr in j.solidos:
            r=tr.rect
            x=86+round(r.x/j.fase.width*780)
            y=234+round(r.y*.23)
            pygame.draw.rect(s,TEAL,(x,y,max(2,round(r.w/j.fase.width*780)),max(2,round(r.h*.23))),1)
        for corpo,cor in ((j.lume.rect,AMBAR),(j.inimigos[0].rect,OSSO)):
            losango(s,86+round(corpo.centerx/j.fase.width*780),234+round(corpo.centery*.23),5,cor)
        texto(s,"Abrigo",115,379,16,PALIDO)
        texto(s,"Tab / Esc   fechar",84,465,15,PALIDO)
        return
    total=paginas_diario(a)
    if a.ensaio is None and a.pagina==total-1:
        ajuda(a,s,'Esquerda / direita   mudar página     M / Tab / Esc   fechar')
        texto(s,f'{total} / {total}',873,77,20,PALIDO,'titulo','right')
        return
    if a.ensaio is None and a.pagina==total-2:
        pagina_viagem(a,s,total)
        return
    livro(a,s,"Diário de Lume","CADERNO DE CAMPO")
    tem_corte=bool(j.cartografia)
    texto(s,f"{a.pagina+1} / {total}",873,77,20,PALIDO,"titulo","right")
    if a.pagina==0:
        pagina_mapa(a,s)
        return
    
    elif a.pagina==1:
        painel_pedidos(a,s)
    elif a.pagina==2 and tem_corte:
        pagina_mapa(a,s,corte=True)
        return
    else:
        nome,msg=j.diario[a.pagina-2-int(tem_corte)]
        texto(s,nome,84,161,30,AMBAR,"titulo")
        paragrafo(s,msg,84,221,750,22)
    texto(s,"Esquerda / direita   mudar página     Tab / Esc   fechar",84,465,15,PALIDO)


def pagina_viagem(a,s,total):
    livro(a,s,"A viagem de Lume","CADERNO DE CAMPO")
    texto(s,f"{a.pagina+1} / {total}",873,77,20,PALIDO,"titulo","right")
    for n,(nome,estado,trecho) in enumerate(linha_da_viagem(a.jogo)):
        y=134+n*81
        losango(s,90,y+13,5,AMBAR,estado=="Raiz restaurada")
        texto(s,nome,108,y,22,OSSO,"titulo")
        texto(s,estado,869,y+5,13,AMBAR,"forte","right")
        paragrafo(s,trecho,108,y+30,742,15,PALIDO)
        if n<3:
            pygame.draw.line(s,(56,77,70),(86,y+70),(873,y+70))
    texto(s,"Esq. / Dir. mudam a página. M, Tab ou Esc fecham.",84,472,14,PALIDO)


def pagina_mapa(a,s,corte=False):
    from .aula_sino import ativa as gruta
    from .cartografia import alvo_local,texto_curto
    from .mapa_visor import contexto
    j=contexto(a.jogo,corte);v=a.mapa_visor;v.preparar(j)
    ensaio=ENSAIOS[a.ensaio] if getattr(a,'ensaio',None) is not None else None
    titulo='Campo de testes · '+ensaio.nome if ensaio else a.jogo.objetivo
    alvo=alvo_local(j)
    acesso=alvo.acesso if alvo and not ensaio and not getattr(j,'_mapa_sem_lume',False) else ''
    if acesso:
        texto(s,texto_curto(titulo,780,17,'forte'),480,130,17,OSSO,'forte','centerx')
        rota=dica_teclado('Acesso · '+acesso)
        texto(s,texto_curto(rota,780,13,'forte'),480,157,13,AMBAR,'forte','centerx')
    else:
        for n,l in enumerate(linhas(titulo,780,17,'forte')[:2]):
            texto(s,l,480,132+n*(tamanho_texto(17)+4),17,OSSO,'forte','centerx')
    detalhe=ensaio.pista if ensaio else alvo.detalhe if alvo else 'Explore as trilhas e marque os lugares a que deseja voltar.'
    if getattr(a.jogo,'ensino_ate',0)>a.jogo.tempo:detalhe=getattr(a.jogo,'ensino_detalhe',detalhe)
    detalhe=dica_teclado(detalhe)
    if getattr(j,'_mapa_sem_lume',False):detalhe='Consulta do Corte · Lume está na superfície. Centralize para ver o último marco.'
    if a.mapa_aviso_ate>a.relogio:detalhe=a.mapa_aviso
    base_detalhe=177 if acesso and tamanho_texto(12)>12 else 180
    for n,l in enumerate(linhas(detalhe,780,12)[:2]):
        texto(s,l,480,base_detalhe+n*(tamanho_texto(12)+4),12,PALIDO,'normal','centerx')
    regiao='Corte da Figueira' if j.em_vertical else j.fase.name
    legenda = (" · Traços âmbar: piso pisado   Contorno verde: terreno visto   Setas: conexões"
               if gruta(j) else ' · Âmbar: Lume   Verde: objetivo   Sinais: descida')
    texto(s,texto_curto(regiao+legenda,728,11),85,215,11,AMBAR)
    texto(s,f'{v.zoom:.1f}×',864,212,14,AMBAR,'forte','right')
    v.desenhar(s,j)
    bolsa=a.jogo.bolsa
    bonus=[f'Bálsamos {bolsa.estoque["balsamo"]}/{bolsa.capacidade_balsamo} · reserva {bolsa.reserva_balsamo}']
    if a.jogo.agulha_disponivel:
        arma='Agulha de taquara' if a.jogo.lume.arma.equipamento=='agulha' else 'Espinho'
        bonus.append(f'{arma} (V na partida)')
    if bolsa.bonus_dano>1:bonus.append('dano +25%')
    if bolsa.bonus_velocidade>1:bonus.append('movimento +12%')
    if bolsa.estoque['resina']:bonus.append('K 18 · golpes luz −20%')
    if bolsa.estoque['lente']:bonus.append('visão +18 px')
    texto(s,texto_curto(dica_teclado(' · '.join(bonus)),780,11),85,442,11,TEAL)
    if a.controles.ultimo_pad:
        texto(s,'LB / RB zoom · Analógico move · R3 centraliza',85,463,12,PALIDO)
        texto(s,'Direcional troca a página · View fecha · Mouse marca',85,482,12,PALIDO)
        return
    texto(s,'+ / − ou roda: zoom · WASD ou arrastar: mover · C: centralizar',85,463,12,PALIDO)
    from .marcas_mapa import TIPOS,CORES
    guia=' · Esq. 2 vezes: viagem' if not corte and a.ensaio is None else ''
    fechar=dica_teclado("M")
    linha=f'Direito: marcar/remover · V: {TIPOS[a.mapa_tipo]} · Esq / Dir: páginas · {fechar} fecha{guia}'
    texto(s,texto_curto(linha,780,12),85,482,12,CORES[a.mapa_tipo])


def painel_pedidos(a,s):
    from .missoes import conhecidas, rastreada
    from .cartografia import texto_curto
    from .fases import FASES
    lista=conhecidas(a.jogo)
    cursor=a.pedido_cursor%len(lista)
    ativo=rastreada(a.jogo).id
    texto(s,"Missões e pedidos",85,137,24,AMBAR,"titulo")
    texto(s,"Só aparecem pedidos que você conheceu.",85,169,13,PALIDO)
    inicio=max(0,min(cursor-2,len(lista)-6))
    for n,m in enumerate(lista):
        if not inicio<=n<inicio+6:continue
        y=197+(n-inicio)*36
        if n==cursor:painel(s,(82,y-3,335,33),False)
        losango(s,95,y+10,3,AMBAR,m.id==ativo)
        texto(s,texto_curto(m.titulo,302,15,"forte"),107,y-2,15,OSSO,"forte")
        texto(s,m.estado,107,y+15,11,PALIDO)
    tecla="A" if a.controles.ultimo_pad else "R"
    texto(s,f"{cursor+1}/{len(lista)} · Cima / baixo escolher · {tecla} acompanhar",85,428,11,AMBAR)
    m=lista[cursor];x=449
    for n,l in enumerate(linhas(m.titulo,412,21,"titulo")[:2]):
        texto(s,l,x,145+n*25,21,AMBAR,"titulo")
    texto(s,"De "+m.origem+" para "+m.destino,x,207,13,OSSO,"forte")
    texto(s,(m.local or FASES[m.etapa].name)+" · "+m.estado,x,229,13,PALIDO)
    texto(s,"Próximo passo",x,261,14,AMBAR,"forte")
    for n,l in enumerate(linhas(m.passo,412,16)[:4]):texto(s,l,x,285+n*20,16,OSSO)
    texto(s,"Recebido" if m.estado=="Concluída" else "Recompensa",x,378,14,AMBAR,"forte")
    for n,l in enumerate(linhas(m.recompensa,412,14)[:3]):texto(s,l,x,402+n*17,14,PALIDO)


def registro(a,s):
    m=ambiental.MENSAGENS[a.registro_etapa]
    livro(a,s,m["bioma"],"REGISTRO DA RAIZ   "+ROMANOS[a.registro_etapa])
    titulo, trecho = RAIZES[a.registro_etapa]
    texto(s,titulo,83,137,21,AMBAR,"titulo")
    paragrafo(s,trecho,83,170,369,16)
    texto(s,"No caderno de campo",481,137,21,AMBAR,"titulo")
    paragrafo(s,m["mensagem"],481,170,389,16)
    texto(s,"Caderno opcional · resposta educativa, sem alterar a história",83,251,14,PALIDO)
    texto(s,m["pergunta"],83,271,18,OSSO,"forte")
    if a.resposta is None:
        opcoes(a,s,m["opcoes"],77,303,795,38,16)
    else:
        certo=m["correta"]==a.resposta
        texto(s,"A folha confirma sua leitura." if certo else "A folha guarda outra pista.",83,309,20,AMBAR,"titulo")
        paragrafo(s,m["explicacao"],83,346,755,17)
    texto(s,"Enter responder · ← / → outras raízes · Esc voltar à viagem",83,460,14,PALIDO)


def capitulo(a,s):
    j=a.jogo
    s.blit(imagem(f"fundo_{j.etapa}.jpg",960,540),(0,0))
    s.blit(placa(960,540,116),(0,0))
    painel(s,(60,270,840,213))
    texto(s,"TRAVESSIA   "+ROMANOS[j.etapa],83,287,14,AMBAR,"forte")
    texto(s,f"{j.restauradas}/4 raízes restauradas",873,287,14,PALIDO,"forte","right")
    texto(s,j.fase.name,81,314,37,OSSO,"titulo")
    paragrafo(s,texto_travessia(j),83,376,780,18)
    texto(s,"Enter   ·   continuar",873,453,14,PALIDO,"normal","right")


def fim(a,s):
    j=a.jogo
    if a.ensaio==INDICE_ARANHA:
        livro(a,s,"Duelo concluído","GALERIA DA SEDA")
        texto(s,f"Semente {j.semente}   ·   {j.tempo:.1f} s",84,162,23,AMBAR,"titulo")
        texto(s,f"Avisos da aranha: {j.inimigos[0].sequencia}",84,219,18,OSSO)
        texto(s,a.aviso_replay,84,256,16,PALIDO)
        opcoes(a,s,a.fim_nomes(),77,346,470,40)
        return
    chave=j.estado
    titulo,msg=FINAL[chave]
    livro(a,s,titulo,"DESFECHO")
    y = paragrafo(s,msg,82,143,770,19)
    if chave == "vitoria":
        from .resgates import mensagem_final

        y = paragrafo(s,mensagem_final(j),82,y+8,765,17,PALIDO)
        desdobramento = epilogo(j)
        if desdobramento:
            y = paragrafo(s,desdobramento,82,y+8,765,15,PALIDO)
    texto(s,f"{j.restauradas} raízes acesas    ·    {j.pontuacao} pontos    ·    {int(j.tempo//60)} min {int(j.tempo%60):02d} s",83,y+20,17,AMBAR,"forte")
    opcoes(a,s,a.fim_nomes(),77,max(342,y+73),400,40)
    if a.resultados_pendentes and a.mem.aviso:
        texto(s,a.mem.aviso,82,465,15,AMBAR)


def recordes(a,s):
    livro(a,s,"Recordes","CADERNO DE CAMPO")
    rows=a.mem.recordes()
    if not rows: paragrafo(s,"Conclua uma jornada para gravar o primeiro resultado.",85,168,724,20)
    for i,(modo,n,p,fase) in enumerate(rows):
        y=159+102*i
        texto(s,"História",84,y,27,AMBAR,"titulo")
        texto(s,f"{n} jornada(s) encerrada(s)     ·     {p} pontos de recorde     ·     trecho {fase}",85,y+44,17)
    texto(s,"Esc ou Enter   ·   voltar",84,462,15,PALIDO)
