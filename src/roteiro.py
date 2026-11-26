PROLOGO = (
    ("Os turnos da figueira",
     "Quando o sino tocava, Tila virava os casulos, Bento levava orvalho e Aru regava as sementes. Nas últimas noites, o sino ainda tocava. Só um dos quatro canais trazia água.", 3),
    ("A noite do raio",
     "O raio abriu o tronco e o Breu se fechou em torno das lanternas mais fortes. A luz de Lume mal alcançava as próprias asas. Ele seguiu pelo chão até encontrar Mimo e o berçário vazio.", 0),
    ("O último turno",
     "Tila, Bento e Aru ainda não tinham voltado. Mimo reconheceu a marca de Tila na grade, os frascos de Bento no Córrego e uma folha de Aru na oficina. “Se ouvir alguém, responda. Eu guardo lugar aqui.”", 0),
    ("Água para a volta",
     "Cada raiz precisa de três gotas para reabrir sua trilha. A primeira roda fica nos galhos acima de Nira. Lume partiu com uma pergunta: por que o berçário já estava vazio quando o raio caiu?", 0),
)
ENTRADAS = (
    "As cascas dos casulos foram abertas por dentro. Quem levou os pequenos conhecia a passagem entre os troncos. Nira ainda guarda o mapa.",
    "A raiz do Bosque voltou a correr e trouxe Lume até o Córrego. Um dos braços do riacho está seco. Casca ainda guarda a roda que desviou a água.",
    "Com a ponte e o ralo abertos, a água chegou de novo à borda. Mesmo assim, há taquaras secas. Da outra margem vêm dois lampejos. O nó perto do vão pode dar a resposta.",
    "A brasa e a vagem levaram Lume à ferida do raio. Sob a figueira há um sino com marcas de garra. Se ele já soava antes da tempestade, alguém ouviu a borda secar.",
)
EFEITOS_RAIZ = (
    "O orvalho voltou e Véspera firmou a ponte dos casulos.",
    "A água voltou aos dois braços. Na volta, use a ponte acima do ralo.",
    "A borda do Taquaral voltou a receber água. Eco pode cruzar.",
    "A Coruja ouviu as quatro correntes e reconheceu o chamado.",
)
DESCOBERTAS = (
    "As marcas na cunha mostram por onde Véspera retirou os casulos antes do raio.",
    "O sulco seco e a roda de Casca revelam que a água foi desviada para o tronco.",
    "A brasa e a vagem revelaram por onde a borda podia voltar à figueira.",
    "O sino já vibrava antes do raio. O chamado era para quem ficou sem água.",
)


def texto_travessia(j):
    if "raiz" in j.flags:
        return EFEITOS_RAIZ[j.etapa] + " Lume reconhece o caminho que reabriu."
    return ENTRADAS[j.etapa]


def linha_da_viagem(j):
    """Quatro fatos derivados dos marcos da campanha, inclusive em saves antigos."""
    from .fases import FASES

    for i, fase in enumerate(FASES):
        flags = j.historico.get((j.volta, i), ())
        if "raiz" in flags:
            yield fase.name, "Raiz restaurada", DESCOBERTAS[i] + " " + EFEITOS_RAIZ[i]
        elif fase.preparo in flags:
            yield fase.name, "Passagem aberta", DESCOBERTAS[i]
        elif i <= j.etapa or flags:
            yield fase.name, "Em curso", ENTRADAS[i]
        else:
            yield f"Travessia {i+1}", "Por descobrir", "Um caminho que Lume ainda vai conhecer."


FINAL = {
    "vitoria": ("O turno da borda",
        "Ao amanhecer, Brasa leva a primeira gota para fora do tronco. Casca abre os dois canais. A Coruja ouve a água chegar onde antes só havia silêncio."),
    "derrota": ("Quando a raiz silencia",
        "A última fagulha se apaga. No abrigo, Mimo ainda guarda lugar para quem ficou nas bordas. O marco guarda o caminho de volta."),
}
def epilogo(jogo):
    entregues = [i for i in range(4) if "pedido_entregue" in jogo.historico.get((0, i), ())]
    cenas = (
        "Mimo deixa Véspera ler, ao lado dos casulos, os nomes que Nira conseguiu salvar.",
        "Casca segura a roda enquanto Fio faz na madeira uma marca nova para a água desta manhã.",
        "Risca abre a trilha antes de Eco piscar duas vezes. Agora conhece o chamado.",
        "Pingo volta com Brasa. Os dois escutam juntos a última vibração do sino.",
    )
    if len(entregues) == 4:
        return "Véspera traz o mapa. Fio anota a cheia. Risca deixa a trilha aberta para Eco. E Pingo espera Brasa na ponta da fila."
    if "casca_fio_reencontro" in jogo.historico.get((0, 1), ()):
        return "Casca segura a corda e espera Fio terminar o nó. A água passa por baixo dos berços."
    return cenas[entregues[-1]] if entregues else ""


CONTROLES = (
    ("A / D   ou   setas", "Andar. Encoste numa parede e salte para a oposta."),
    ("Espaço", "Saltar; solte e aperte no ar para o salto duplo. Segure na queda para planar."),
    ("S   /   S + Espaço", "Agachar / descer de uma plataforma vazada."),
    ("Shift + direção", "Deslizar. A corrente do córrego exige impulso."),
    ("E", "Conversar, operar mecanismos e abrir bolsas de trilha."),
    ("J / L / S+J", "Corte rápido / pesado / golpe descendente. Alterne J, L, J e K, L."),
    ("Ctrl + J / L", "Ataques de luz: mais dano; gastam brilho e depois vida se faltar."),
    ("K", "Clarão de 520 px por 5,5 s. Custa 22 de brilho; pavio prolonga para 9 s."),
    ("Q   /   F", "Escolher item na bolsa / usar o item escolhido."),
    ("V", "Alterna Espinho e Agulha após a entrega do âmbar a Mimo."),
    ("Tab / M / C", "Mapa e pedidos / mapa / caderno opcional. No mapa, C centraliza."),
    ("Mapa: + / - / WASD", "Ampliar / reduzir / mover. Arraste com mouse; botão direito marca; V troca tipo."),
    ("Esc   ou   P", "Pausar. Na pausa, R retorna ao marco."),
    ("F10 / F11", "Silenciar / alternar tela cheia."),
)
