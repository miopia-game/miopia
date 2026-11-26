"""Ensino contextual durante a partida. Não pausa e não exige abrir um menu."""
from .narrativa import ITENS
from . import vento_taquaral
from . import galeria_taquaral
from .fases import CHAO, GALHO_DO_MORCEGO
from .travessia_fagulha import ORIGEM_MORCEGO

RECUPERAVEIS = {'primeiros_passos', 'salto'}

CURTAS={
    'primeiros_passos':'Ande com A / D ou com as setas.',
    'salto':'Aperte Espaço para saltar.',
    'interacao':'Chegue perto de um morador e aperte E quando aparecer a opção.',
    'bolsa':'Q escolhe o item. F usa. O bálsamo recupera vida e brilho quando alguma barra está baixa.',
    'mapa':'Aperte M ou Tab. O mapa registra o trecho que você já conseguiu enxergar.',
    'reservas':'Vida recebe dano. K e Ctrl usam brilho; se faltar, usam vida. Brilho não drena sozinho.',
    'salto_duplo':'Salte, solte Espaço e aperte de novo no ar para alcançar um galho mais alto.',
    'combate':'J rápido, L pesado. Alterne J/L/J. S + J no ar rebate; Shift + direção + J avança.',
    'deslize':'S agacha. Shift + direção desliza sob raízes. Solte S para saltar.',
    'luz_combate':'K clareia. Ctrl + J / L carrega luz. No escuro, K atrapalha a visão dos inimigos.',
    'menus':'M / Tab abre o mapa. Esc / P pausa. F10 silencia; F11 alterna tela cheia.',
    'grade':'S + Espaço desce de grades e galhos. Terra firme não deixa passar.',
    'corda':'E na base sobe pelo cipó. Marcos guardam retorno, sem curar.',
    'parede':'Toque o tronco e salte para a parede oposta. Alterne as faces para subir.',
    'casulo_impulso':'Pule sobre o casulo e aperte S + J no ar. O golpe lança Lume até o nicho.',
    'planagem':'Segure Espaço ao cair para planar. Solte ou aperte S para descer mais rápido.',
    'vento_taquaral':'Salte onde as sementes sobem. Segure Espaço ao cair e o vento leva Lume para cima.',
    'aba_taquaral':'Saia à direita e solte Espaço. Ao ficar na altura da abertura sob a aba, segure Espaço de novo.',
    'chamine_sementes':'Salte entre as sementes. Segure Espaço ao cair. Solte acima da grade para pousar.',
    'combos_luz':'Acertos devolvem brilho. Sem sofrer dano, o retorno cresce até 8×; um golpe ou queda zera.',
    'tochas':'Vença os guardas, recolha o núcleo com E e acenda a tocha. O globo Q/F ilumina outro local.'}


def praticado(j):
    return 'praticado_'+getattr(j,'ensino_id','') in j.tutorial


def pouso_para_mapa(j):
    if not j.lume.chao or j.lume.em_corda:
        return False
    x, y = j.lume.rect.midbottom
    if 920 <= x < 1040 and abs(y - CHAO) < 2:
        return True
    # A ponta de saída do galho é uma pausa depois do encontro.
    inicio, altura, largura = GALHO_DO_MORCEGO
    ponta = inicio + largura
    return ponta-40 <= x < ponta and abs(y-altura) < 2 and f"inimigo_{ORIGEM_MORCEGO}" in j.flags


def confirmar(j, ident):
    if getattr(j,'ensino_id','')!=ident or getattr(j,'ensino_ate',0)<=j.tempo or praticado(j):
        return
    j.tutorial.add('praticado_'+ident)
    j.ensino_ate=min(j.ensino_ate,max(j.tempo+1.,j.ensino_inicio+1.8))


def verificar_pratica(j,cmd):
    l=j.lume
    pulo='pulo' in j.eventos
    x, pe = l.rect.midbottom
    acoes={
        'primeiros_passos':bool(cmd.mover and abs(l.vx)>70),
        'salto':pulo,
        'salto_duplo':pulo and l.batida_asa>0,
        'planagem':l.planando,
        'vento_taquaral':l.planando and l.vy < -60,
        'galeria_sementes':galeria_taquaral.dentro(j),
        'chamine_sementes':l.planando and l.vy < -60 and galeria_taquaral.CHAMINE.contem(x, pe),
        'aba_taquaral':l.planando and l.vy > 0 and vento_taquaral.EXPOSTA.contem(x, pe)
                          and vento_taquaral.ALTURA_ENTRADA <= pe < vento_taquaral.POUSO[1],
        'combate':'golpe' in j.eventos,
        'deslize':'deslize' in j.eventos,
        'luz_combate':'pulso' in j.eventos or 'golpe' in j.eventos and l.arma.luminoso,
        'corda':l.em_corda or j.destino_vertical is not None,
        'grade':cmd.baixo and cmd.salto and l.ignorar_topo is not None,
        'parede':pulo and l.trava_lateral>0,
        'casulo_impulso':'rebote_casulo' in j.eventos,
    }
    atual=j.ensino_id
    if acoes.get(atual):confirmar(j,atual)


def atualizar(j,cmd):
    if (j.modo!='historia' or hasattr(j,'sala_id') or getattr(j,'ensaio_armas',False) or
            getattr(j,'campo_testes',False) or j.dialogo or j.boss and not j.boss.vencido):return
    if getattr(j,'ensino_ate',0)>j.tempo:
        verificar_pratica(j,cmd)
    x,y=j.lume.rect.midbottom
    bosque=j.etapa==0 and not j.em_vertical and y<500
    if bosque and x<710 and 'pulso' in j.eventos:
        j.tutorial.add('praticado_clarao_bosque')
    taquaral=j.etapa==2 and not j.em_vertical
    candidatos=[];condicoes=set()
    def dica(ident,cond,titulo,texto):
        if cond:condicoes.add(ident)
        pendente = ident in RECUPERAVEIS and 'praticado_'+ident not in j.tutorial
        if cond and (ident not in j.tutorial or pendente):
            curto=CURTAS.get(ident,texto.split('.')[0]+'.')
            candidatos.append((ident,titulo,curto,texto))
    dica('primeiros_passos',bosque and x<220,'O primeiro caminho','A / D ou as setas movem Lume. Siga pela direita.')
    dica('salto',bosque and 70<x<250,'Salte para o primeiro galho','Aperte Espaço para saltar. A borda clara à direita mostra onde pousar.')
    dica('interacao',bosque and 119<x<269,'Encontre os moradores','Aproxime-se de Nira ou Mimo e use E quando a opção aparecer. E também opera mecanismos e abre bolsas de trilha.')
    dica('vento_taquaral',taquaral and 197<x<318 and y>230,'As sementes sobem',
         'Salte entre os colmos onde as sementes sobem e segure Espaço quando começar a cair. O vento leva Lume até o beiral. Do lado exposto, as sementes correm de lado e mostram para onde as asas são levadas.')
    beiral_x, beiral_y, beiral_largura = vento_taquaral.BEIRAL
    dica('aba_taquaral',taquaral and beiral_x<x<beiral_x+beiral_largura and y<=beiral_y,'Por baixo da aba',
         'Saia do beiral à direita. Solte Espaço para baixar e retome ao alcançar as sementes que correm de lado, à altura da abertura. Na corrente, as asas freiam a queda e levam ao abrigo de Risca.')
    esquerda, direita = galeria_taquaral.ENTRADA
    dica('galeria_sementes',taquaral and esquerda-48<x<direita and 403<y<480,'Sob a ponte',
         'S + Espaço desce pela grade e pelos patamares da galeria. O cipó no fundo sempre permite subir de volta.')
    dica('chamine_sementes',taquaral and galeria_taquaral.ABERTA in j.flags
         and galeria_taquaral.CHAMINE.esquerda<x<galeria_taquaral.CHAMINE.direita and y>820,
         'A corrente voltou', 'Salte entre as sementes que sobem e segure Espaço ao cair. Solte acima da grade para pousar. S + Espaço nessa grade volta à galeria.')
    dica('reservas',bosque and x>=290,'Vida e brilho','Vida recebe dano. Brilho só gasta no K e nos ataques de luz. Ao zerar, o halo apaga; insistir numa habilidade usa vida. Derrotar inimigos recupera um pouco das duas barras.')
    dica('salto_duplo',bosque and 269<=x<610,'Outra batida de asas','Solte Espaço depois do salto e aperte novamente no ar. A segunda batida de asas permite alcançar galhos mais altos.')
    dica('bolsa',bosque and 395<x<665,'Use a bolsa','Q escolhe um item. F usa o item equipado. O Bálsamo de Mimo restaura até 35 de vida e 35 de brilho. Se as duas barras estiverem cheias, você guarda a carga.')
    dica('combate',bosque and 635<x<920,'Cortes e respostas','J faz cortes rápidos. L faz um golpe pesado. Alterne J, L, J; use S + J no ar para atacar para baixo e rebater. Shift + direção + J avança. Observe o aviso antes de se aproximar.')
    dica('mapa',bosque and pouso_para_mapa(j),'Abra o mapa','M ou Tab abre o mapa e os pedidos. Pressione Esquerda para consultar os controles. M fecha e devolve Lume à trilha.')
    dica('deslize',bosque and 1040<=x<1260,'Por baixo das raízes','S agacha. Shift + direção desliza pelos vãos baixos. Solte S antes de tentar saltar. Terra firme não permite descer; grades e galhos elevados permitem.')
    dica('planagem',bosque and (1260<=x<1380 or 2700<x<3200),'Sustente as asas','Salte da borda e segure Espaço enquanto cai para planar continuamente. Soltar Espaço acelera a descida; S também encerra o planeio.')
    dica('luz_combate',bosque and 1390<x<1530,'Luz contra a emboscada','K ilumina uma área ampla e atrapalha por instantes a visão dos inimigos no escuro. Ctrl + J / L executa golpes de luz, mais fortes e com custo de brilho. Ataques normais são gratuitos.')
    dica('menus',bosque and 1840<x<2080,'Leve o caminho com você','M / Tab: mapa. + / - amplia; WASD ou arrasto move; botão direito marca e V muda o tipo. C centraliza no mapa. Esc / P pausa; R na pausa retorna ao marco. F10 silencia; F11 alterna tela cheia.')
    perto_grade=j.em_vertical and any(t.tipo=='grade' and t.rect.left-40<x<t.rect.right+40
                                     and abs(t.rect.top-y)<65 for t in j.solidos)
    dica('grade',bosque and 1530<x<1720 or perto_grade,'A floresta continua abaixo','Sobre uma grade ou galho elevado, segure S e aperte Espaço para descer. Pule por baixo de galhos para subir. M abre o mapa; ele guarda o que você já iluminou dentro da tela.')
    dica('corda',any((o.tipo=='corda' or o.tipo=='elevador' and 'ralo_aberto' in j.cartografia)
                    and abs(o.x-x)<100 and abs(o.y-y)<70 for o in j.objetos),'Cipós e cordas','E junto à base faz Lume subir. Os cipós dos poços permitem retornar mesmo antes de vencer o guardião. O marco guarda seu retorno e não cura.')
    dica('parede',bosque and 2110<x<2380,'Entre dois troncos','Salte encostado numa face de impulso e aperte Espaço novamente: Lume salta para a parede oposta. Alterne as duas faces e direcione a saída para o galho do alto.')
    if j.em_vertical:
        from . import corte_vertical
        perto_casulo = abs(x-corte_vertical.CASULO_X) < 110 and corte_vertical.CASULO.top-95 < y <= corte_vertical.PISO_POCO
        dica('casulo_impulso', perto_casulo, 'O casulo elástico',
             'Pule sobre o casulo e use S + J no ar. O golpe para baixo lança Lume até o nicho. S + Espaço no nicho desce ao piso firme.')
    dica('agulha',j.agulha_disponivel,'Uma arma de maior alcance','Aperte V fora de um golpe para alternar entre o Espinho rápido e a Agulha de taquara, que alcança mais longe e demora mais para recuperar a guarda.')
    dica('combos_luz',j.lume.combo_acertos>=3,'Uma sequência sem ferimentos','Acertar golpes recupera um pouco de brilho. A cada três acertos sem sofrer dano, o retorno cresce exponencialmente, até 8×. Um golpe recebido ou uma queda zera o multiplicador.')
    dica('tochas',any(o.tipo=='lanterna' and abs(o.x-x)<100 and abs(o.y-y)<100 for o in j.objetos),'Conquiste a clareira','Derrote os guardas, recolha o núcleo com E e use E na tocha. A região fica nítida para sempre. O globo recebido pode ser fixado em outro caminho usando Q / F.')
    for item in ITENS:
        dica('item_'+item.id,j.bolsa.estoque[item.id]>0 and (item.id!='balsamo' or j.lume.vida<90 or j.etapa==0 and x>380),'Na sua bolsa: '+item.nome,item.descricao+(' Use E na tocha da clareira.' if item.id=='semente_luz' else ' Q escolhe; F usa uma carga. Sem efeito, a carga é guardada.' if not item.passivo else ' A melhoria já está ativa; não precisa equipar.'))
    genericas=lambda ident:ident in ('reservas','combos_luz') or ident.startswith('item_')
    locais=[c for c in candidatos if not genericas(c[0])]
    atual=getattr(j,'ensino_id','')
    if getattr(j,'ensino_ate',0)>j.tempo:
        if not locais or atual in condicoes and not genericas(atual):return
        candidatos=locais
    elif locais:candidatos=locais
    if candidatos:
        ident,titulo,texto,detalhe=min(candidatos, key=lambda dica:dica[0] in j.tutorial)
        j.tutorial.add(ident)
        j.ensino_id=ident
        j.ensino_titulo=titulo;j.ensino_texto=texto;j.ensino_detalhe=detalhe
        j.ensino_inicio=j.tempo;j.ensino_ate=j.tempo+6.


def desenhar(s,j):
    from .avisos import desenhar as aviso
    aviso(s,j)
