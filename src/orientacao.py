"""Uma mesma pista alimenta o mapa, o clarão e as conversas de orientação.

As coordenadas são as bases dos objetos no mundo atual, sem deslocamento de
câmera. A leitura não altera flags, diário, inimigos ou geração aleatória.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import math

from .fases import ARENA, CHAO, RAIZ, SAIDA, VIGIA_X, FASES


@dataclass(frozen=True)
class Objetivo:
    id: str
    nome: str
    texto: str
    x: float
    y: float
    regiao: str
    local: str
    opcional: bool = False
    detalhe: str = ""
    motivo: str = ""
    acesso: str = ""


OBJETIVO_PRINCIPAL = "Leve orvalho às quatro raízes para reabrir o caminho dos sobreviventes."
MOTIVOS = {
    "peca": "A peça destrava o caminho usado para retirar os casulos.",
    "cunha": "Soltar a cunha reabre a passagem do berçário até a guardiã.",
    "dreno": "Baixar a água permite recuperar a peça da ponte sob a raiz.",
    "lingueta": "A ponte precisa desta peça para Fio levar os casulos pela margem.",
    "ponte": "A ponte reconecta a margem de Fio ao canal dos casulos.",
    "ralo": "Abrir o ralo devolve a água à borda e libera o caminho à guardiã.",
    "no": "A luz de Eco revela uma travessia para quem ficou isolado.",
    "brasa": "A brasa mantém a trilha acesa até a outra margem.",
    "vagem": "O cheiro da vagem permite reencontrar quem chama do outro lado.",
    "roldana": "A corda conduz ao contrapeso que sustenta a ponte do sino.",
    "contrapeso": "A ponte leva ao sino capaz de chamar a guardiã.",
    "eco_antigo": "O sino soterrado abre o caminho até a Coruja.",
}


# Nome breve para o mapa, ação para o HUD, instrução completa para diálogo.
PISTAS = {
    "peca": ("Peça da porteira", "Suba pelo cipó e recolha a peça",
        "Passe pelo galho de Véspera. Use E no cipó pendurado, suba e recolha a peça da porteira com E."),
    "cunha": ("Cunha do berçário", "Solte a cunha entre os troncos",
        "Depois do marco do ramal, alterne saltos entre os dois troncos. A cunha fica no galho à direita, no alto."),
    "dreno": ("Roda do dreno", "Gire a roda do primeiro galho",
        "Volte à margem inicial do Córrego. A roda do dreno fica no primeiro galho acima de Casca. Salte e use E."),
    "lingueta": ("Lingueta de Casca", "Recolha a lingueta sob a raiz",
        "Com o canal drenado, siga à direita. Deslize com Shift + direção sob a raiz baixa e recolha a lingueta com E."),
    "ponte": ("Roda da ponte", "Encaixe a lingueta na roda da ponte",
        "A roda da ponte fica no Córrego, no chão à direita de Fio e antes do primeiro vão. Use E com a lingueta. Não fica no Bosque nem na cisterna."),
    "ralo": ("Ralo da comporta", "Desça pela grade e abra o ralo",
        "Depois da ponte e do marco, suba os dois apoios. No centro da grade, S + Espaço desce até a roda do ralo. Use E para abrir a passagem à direita."),
    "no": ("Nó de Eco", "Acenda o nó na beira do vão",
        "O nó fica no chão, antes do primeiro vão do Taquaral. Use E. Os três apoios revelados conduzem à brasa."),
    "brasa": ("Brasa de seiva", "Cruze os apoios até a brasa",
        "Salte pelos três apoios de luz. A brasa está no galho da outra margem. Use E para recolhê-la."),
    "vagem": ("Vagem da margem", "Plane até a vagem do outro lado",
        "Após afastar o vigia, suba os apoios de bambu. Salte da beira alta, segure Espaço na queda e alcance a vagem na margem direita."),
    "roldana": ("Roldana da gruta", "Gire a roldana no segundo galho",
        "Suba os dois primeiros apoios da Gruta e use E na roldana. Uma corda desce à direita."),
    "contrapeso": ("Contrapeso do sino", "Suba a corda e solte o contrapeso",
        "Use E na base da corda para subir. O contrapeso está no estrado alto à direita. Soltá-lo sustenta a ponte sobre o vão."),
    "eco_antigo": ("Sino soterrado", "Desça e toque o sino da câmara",
        "Depois do marco, suba aos apoios. S + Espaço desce pela grade. Use E no sino e observe para onde o toque corre."),
}

ACESSOS = {
    "peca": "use E na base do cipó depois do galho de Véspera.",
    "cunha": "alterne saltos entre os troncos depois do marco.",
    "dreno": "salte para o primeiro galho acima de Casca.",
    "lingueta": "deslize sob a raiz baixa do canal drenado.",
    "ralo": "suba aos apoios após o marco e desça pela grade com S + Espaço.",
    "brasa": "cruze o vão pelos apoios de luz.",
    "vagem": "suba pelos bambus e plane a partir do apoio alto.",
    "roldana": "suba pelos dois primeiros apoios da Gruta.",
    "contrapeso": "use E na base da corda para alcançar o estrado alto.",
    "eco_antigo": "alcance o sino pela grade marcada da câmara.",
}


def direcao(j, x, y):
    """Direção de leitura, não uma afirmação de que existe linha reta livre."""
    dx, dy = x - j.lume.rect.centerx, y - j.lume.rect.bottom
    partes = []
    if abs(dx) > 65:
        partes.append("à direita" if dx > 0 else "à esquerda")
    if abs(dy) > 60:
        partes.append("acima" if dy < 0 else "abaixo")
    return " e ".join(partes) if partes else "perto de você"


def _alvo(j, ident, nome, acao, x, y, detalhe="", *, opcional=False, acesso=""):
    regiao = "corte" if j.em_vertical else "superficie"
    local = "Corte da Figueira" if j.em_vertical else j.fase.name
    return Objetivo(ident, nome, f"{acao} · {direcao(j, x, y)}", x, y,
                    regiao, local, opcional, detalhe or acao + ".",
                    "Desvio opcional: encontre recursos para a travessia." if opcional else OBJETIVO_PRINCIPAL,
                    acesso)


def _mecanismo(j, ident):
    objeto = next(o for o in j.fase.objetos if o.id == ident)
    nome, acao, detalhe = PISTAS[ident]
    acesso = ACESSOS.get(ident, "")
    return replace(_alvo(j, ident, nome, acao, objeto.x, objeto.y, detalhe, acesso=acesso),
                   motivo=MOTIVOS[ident])


def _superficie(j):
    from .aula_sino import orientar as orientar_escuta
    trecho = orientar_escuta(j)
    if trecho is not None:
        return trecho
    # Um save antigo com o chefe vencido já comprova o percurso anterior.
    if "chefe" not in j.flags:
        for flag, _ in j.fase.passos:
            if flag not in j.flags:
                if flag == "vagem" and j.tranca_fechada:
                    return _alvo(j, "vigia", "Vigia da passagem", "Afaste o vigia da trança",
                                 VIGIA_X, CHAO,
                                 "O vigia guarda a passagem do Taquaral. O terceiro corte de J ou o golpe S + J no ar rompe sua guarda.")
                return _mecanismo(j, flag)
        nome = ("Asa Fendida", "Tecelã", "Casco", "Coruja")[j.etapa]
        if j.boss and not j.boss.vencido:
            return _alvo(j, "chefe", nome, j.boss.dica, j.boss.x, j.boss.y,
                         "Observe o aviso do ataque e use a ferramenta da arena. " + j.boss.dica)
        return _alvo(j, "arena", "Entrada da arena", "Avance até a guardiã", ARENA + 60, CHAO,
                     "Os mecanismos abriram a porteira. Guarde seu retorno no marco antes de entrar na arena à direita.")
    if "raiz" not in j.flags:
        if j.orvalhos < 3:
            gotas = [o for o in j.objetos if o.tipo == "orvalho"]
            if gotas:
                o = min(gotas, key=lambda o: math.dist((o.x, o.y), j.lume.rect.center))
                return _alvo(j, o.id, "Orvalho da raiz", f"Recolha orvalho ({j.orvalhos}/3)", o.x, o.y,
                             "A raiz precisa de três gotas. Recolha o orvalho indicado no mapa e retorne à raiz, depois da arena.")
        return _alvo(j, "raiz", "Raiz da borda", "Devolva três gotas à raiz", RAIZ, CHAO,
                     "Depois da arena, use E na raiz luminosa para devolver o orvalho e reabrir o caminho da borda.")
    return _alvo(j, "saida", "Caminho seguinte", "Siga a trilha reaberta", SAIDA, CHAO,
                 "Use E na saída à direita da raiz. " +
                 ("A colônia espera na figueira." if j.etapa == 3 else "A próxima travessia continua por esse caminho."))


def _corte(j):
    from . import arquivo_casca as arquivo
    from . import corte_vertical as c
    setor, _ = c.setor(j.lume.rect.centery, j.lume.rect.centerx)
    def ponto(ident, nome, acao, detalhe):
        o = next(o for o in c.PONTOS if o.id == ident)
        return _alvo(j, ident, nome, acao, o.x, o.y, detalhe, opcional=True)
    if setor == "arquivo" and "leu_placa_arquivo" not in j.cartografia:
        return ponto("placa_arquivo", "Armário de Mimo", "Desvio · abra o armário",
                     "Este desvio guarda mantimentos. Use E no armário. Para a história, retorne ao Bosque pela galeria acima.")
    if setor == "arquivo" and not j.bolsa.estoque["espinho"]:
        return ponto("reliquia_espinho", "Espinho de acácia", "Desvio · recolha o espinho de acácia",
                     "À direita do armário, no mesmo patamar, use E no espinho. Ele reforça os cortes permanentemente. Depois, suba à galeria pelo lado direito.")
    if setor == 'arquivo' and arquivo.CONFIRMADOS not in j.cartografia:
        fechada = arquivo.FECHADA in j.cartografia
        if fechada and arquivo.LIDOS not in j.cartografia:
            return _alvo(j, 'sinais_arquivo', 'Traços do Arquivo', 'Leia os traços na parede',
                         arquivo.SINAIS[0], arquivo.PISO, 'Use E nos traços que aparecem à direita da janela.', opcional=True)
        x = min(arquivo.PUXADORES, key=lambda x: abs(x-j.lume.rect.centerx))
        acao = 'Reabra a veneziana' if fechada else 'Feche a veneziana'
        return _alvo(j, 'veneziana', 'Veneziana do Arquivo', acao, x, arquivo.PISO,
                     'E aciona um puxador ao lado da janela. Repare no que muda na parede.', opcional=True)
    if (setor == "viveiro" and j.lume.rect.bottom <= 1370
            and not j.bolsa.estoque["resina"]):
        return ponto("reliquia_resina", "Resina de âmbar", "Desvio · recolha a resina dos berços",
                     "A resina fica no primeiro patamar do viveiro, à direita da placa. Use E para reduzir o consumo de luz. Depois, os berços descem até a roda da cisterna.")
    if setor == "copa":
        if "atalho_copa" not in j.cartografia:
            return ponto("selo_copa", "Trava do observatório", "Desvio · solte a janela",
                         "Use E na roda do patamar esquerdo. A janela abre uma saída ao Bosque, à direita da copa.")
        return ponto("volta_copa", "Janela para o Bosque", "Retorne ao Bosque pela janela",
                     "Use E na janela da direita. A continuação principal fica na superfície; as câmaras são desvios opcionais.")
    if setor in ("estaleiro", "viveiro") and "viveiro_aberto" not in j.cartografia:
        if setor == "estaleiro":
            return _alvo(j, "grade_viveiro", "Descida ao viveiro", "Desvio · desça pela grade da oficina",
                         2240, 790, "Os apoios seguem até a roda no fundo.",
                         opcional=True, acesso="na grade à direita da oficina, use S + Espaço.")
        return ponto("comporta_viveiro", "Roda do viveiro", "Desvio · abra a ligação à cisterna",
                     "Desça pelos berços até o chão. A roda fica no canto esquerdo do viveiro e abre o retorno à cisterna.")
    if setor in ("cisterna", "viveiro", "estaleiro"):
        if "ralo_aberto" not in j.cartografia:
            return ponto("ralo_cisterna", "Ralo da cisterna", "Desvio · ilumine o ralo com K e use E",
                         "Na cisterna, siga à esquerda até a roda. K revela os dentes sob o lodo; E abre o canal e liga o elevador de cipó.")
        if j.etapa == 1 or "raiz" in j.historico.get((j.volta, 0), set()):
            return ponto("volta_corrego", "Saída ao Córrego", "Retorne à margem do Córrego",
                         "Use E na saída à direita da cisterna. A roda da ponte fica na superfície do Córrego, depois da raiz baixa.")
        return ponto("carro_baixo", "Elevador de cipó", "Suba no elevador até a copa",
                     "Use E no estrado com cipó, à direita da cisterna. Na copa, a janela leva de volta ao Bosque.")
    if setor == "poco":
        return _alvo(j, "grade_cisterna", "Grade do poço", "Desvio · desça a grade até a cisterna",
                     570, 1492, "Siga pelos apoios até a cisterna e ilumine o ralo com K.",
                     opcional=True, acesso="na grade do Poço da Seiva, use S + Espaço.")
    return ponto("volta_bosque", "Saída ao Bosque", "Retorne à trilha principal do Bosque",
                 "Use E na abertura à esquerda da galeria. Subir à copa ou descer às câmaras é opcional e guarda recompensas.")


def _subsolo(j):
    """Dentro do desvio, a pista termina numa abertura física da superfície."""
    from .rotas_borda import POSTOS
    trabalho = POSTOS["bento"]
    voltando = j.missao == "borda_bento" or j.bolsa.estoque["asa"]
    if voltando and trabalho.corda.id in j.flags and j.lume.rect.bottom >= 1000:
        corda = trabalho.corda
        return _alvo(j, corda.id, "Corda de Bento", corda.nome, corda.x, corda.y,
                     "A corda leva de volta à margem.",
                     opcional=True, acesso="use E na base da corda sob a grade leste.")
    if not voltando:
        return _alvo(j, "reliquia_asa", "Membrana de libélula",
                     "Desvio · encontre a membrana entre as raízes", 2940, 1102,
                     "Desça pelos galhos com S + Espaço. No chão, à direita, recolha a membrana com E para ganhar velocidade. O retorno sobe pelo outro lado.",
                     opcional=True)
    return _alvo(j, "grade_saida_subsolo", "Grade de retorno ao Córrego",
                 "Suba os galhos da direita até a grade de saída", 3030, CHAO,
                 "Do chão, use o salto duplo para chegar ao galho baixo à direita. Alterne os galhos até a grade no teto, sobre o poço direito. Salte por baixo dela para retornar à superfície.",
                 opcional=True, acesso="suba pelos galhos da direita e salte por baixo da grade.")


def objetivo_atual(j):
    if hasattr(j, "sala_id"):
        return None
    if j.boss and j.boss.coro_iniciado and not j.boss.vencido:
        from .ultimo_chamado import alvo as ninho_atual
        x, _ = ninho_atual(j.boss)
        sinal = j.boss.coro_sinais
        detalhe = 'Use K perto do ninho para devolver o sinal.'
        if j.boss.coro_gota:
            detalhe += ' Use E no ninho para recolher orvalho e repor brilho.'
        return _alvo(j, f'ninho_chamado_{sinal}', 'Ninho do Último Chamado',
                     f'Devolva o sinal {sinal+1}/3 no ninho', x, j.boss.chao, detalhe)
    from .fio_corte import orientar as orientar_fio
    fio = orientar_fio(j)
    if fio is not None:
        return fio
    from .resgates import orientar as orientar_resgates
    resgate=orientar_resgates(j)
    if resgate is not None:return resgate
    from .jardim import orientar as orientar_jardim
    jardim=orientar_jardim(j)
    if jardim is not None:return jardim
    if (j.concluida and j.missao in ('principal','resgates','jardim') and
            len(j.sobreviventes)==3 and 'jardim_plantado' in j.cartografia):
        return _alvo(j,'colonia_reunida','A colônia reunida','História concluída · explore os pedidos e caminhos restantes',
                     *j.lume.rect.midbottom,'Os três voltaram e a nascente foi plantada. M abre pedidos conhecidos e marcas pessoais; a floresta continua acessível.',opcional=True)
    from .raizes_bosque import orientar
    raizes=orientar(j)
    if raizes is not None:return raizes
    from .galeria_taquaral import orientar as orientar_galeria
    galeria = orientar_galeria(j)
    if galeria is not None:
        return galeria
    if getattr(j,'ensaio_armas',False):
        return _alvo(j,'oficina','Alvos de casca','Compare as duas armas',520,CHAO,
                     'V troca fora do golpe. E no abrigo repõe luz e alvos; este ensaio não altera a História.',opcional=True)
    if getattr(j,"ensaio_tatico",False):
        e=next((e for e in j.inimigos if e.ativo and e.origem[0] in (1548,1660)),None)
        return _alvo(j,"patrulha","Patrulha da margem","Afaste a patrulha",e.rect.centerx if e else 1510,
                     CHAO,"Use os avisos para escolher entre recuar, saltar, cortar e espalhar pólen. Seu save da História está separado.",opcional=True)
    from . import subsolo
    if (subsolo.ativo(j) and 2440 <= j.lume.rect.centerx <= 3190
            and j.lume.rect.bottom > CHAO + 50):
        return _subsolo(j)
    if not j.em_vertical:
        from .missoes import rastreada
        missao=rastreada(j)
        if missao.id!="principal":
            if missao.etapa!=j.etapa:
                if missao.etapa>j.etapa and "raiz" not in j.flags:
                    alvo=_superficie(j)
                    return replace(alvo,motivo="Antes do pedido na próxima região, restaure esta raiz.")
                x=34 if missao.etapa<j.etapa else SAIDA
                return _alvo(j,"rota_pedido",missao.titulo,"Volte ao pedido em "+FASES[missao.etapa].name,
                             x,CHAO,missao.passo,opcional=True)
            o=next((o for o in j.objetos if o.id==missao.alvo_id or
                    missao.alvo_id=="npc:"+o.nome),None)
            if o:
                if o.id in PISTAS:
                    alvo=_mecanismo(j,o.id)
                    return replace(alvo,nome=missao.titulo,opcional=True,motivo="Pedido de "+missao.origem+" · "+missao.recompensa)
                return replace(_alvo(j,o.id,missao.titulo,missao.passo,o.x,o.y,missao.passo,opcional=True),
                               motivo="Pedido de "+missao.origem+" · "+missao.recompensa)
    return _corte(j) if j.em_vertical else _superficie(j)


def pista_mecanismo(j, objeto):
    """Siga a cadeia até a primeira ação que realmente pode ser cumprida."""
    ident = objeto.id
    visitados = set()
    while ident in j.fase.mecanismos and ident not in visitados:
        visitados.add(ident)
        requer = j.fase.mecanismos[ident].requer
        if not requer or requer in j.flags:
            break
        ident = requer
    if ident in PISTAS:
        alvo = _mecanismo(j, ident)
        falta = ("A ponte precisa da lingueta. "
                 if objeto.id in ("ponte", "ralo") and "lingueta" not in j.flags else "")
        return falta + alvo.detalhe + " O mapa marca o destino; K indica sua direção."
    return j.fase.mecanismos[objeto.id].falta


def conselho(j):
    alvo = objetivo_atual(j)
    return "" if alvo is None else alvo.detalhe
