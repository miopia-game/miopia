"""Cenas isoladas da campanha para as rodadas de avaliação com o jogador."""
from dataclasses import dataclass
from .fases import ARENA, CHAO, FASES, MEIO
from .sala_aranha import ABRIGO, DueloAranha, SALA_ARANHA, SEMENTE_ARANHA
from .travessia import Jornada


@dataclass(frozen=True)
class Ensaio:
    nome: str
    etapa: int
    pos: tuple[int, int]
    flags: tuple[str, ...]
    pista: str


ENSAIOS = (
    Ensaio("Combate no Bosque",0,(796,CHAO),(),
           "Escute o morcego antes de avançar. Experimente J em sequência e S + J no ar."),
    Ensaio("Túnel do Córrego",1,(804,CHAO),("dreno",),
           "K deixa o trecho iluminado. Use Shift + direita para atravessar a corrente e E junto à lingueta."),
    Ensaio("Pulo entre paredes",0,(2200,CHAO),("meio","valvula","peca"),
           "Salte encostando na face riscada à direita. Pressione Espaço de novo e alterne entre as duas faces."),
    Ensaio("Descida pela grade",1,(2316,315),("meio","dreno","lingueta","ponte"),
           "Segure S ou seta para baixo e aperte Espaço. No fundo, E destrava a comporta."),
    Ensaio("Planeio no Taquaral",2,(2442,298),("meio","no","brasa","inimigo_1980"),
           "Corra até a ponta. Salte à direita e continue segurando Espaço enquanto cai."),
    Ensaio("Sentinela do Taquaral",2,(MEIO,CHAO),("meio","no","brasa"),
           "Escute o casco. Golpeie por trás ou de cima para abrir a trama que protege o bambuzal."),
    Ensaio("Mundo vertical",0,(630,CHAO),(),
           "Pressione E na fenda. Suba até a copa ou desça à cisterna. Tab abre o mapa das regiões visitadas."),
    Ensaio("Estaleiro das Folhas",1,(1944,CHAO),("dreno","lingueta","ponte","meio"),
           "E na fenda leva à oficina. Desça pelas grades do viveiro e abra o retorno à cisterna. Para saltar de novo, solte Espaço e aperte no ar."),
    Ensaio("Asa Fendida",0,(ARENA-20,CHAO),("meio","marco","peca",FASES[0].preparo),
           "Entre pela direita. Observe a altura da asa antes de escolher entre agachar e saltar. A raiz riscada expõe o dorso."),
    Ensaio("Tecelã do Vão",1,(ARENA-20,CHAO),("meio","marco","dreno","lingueta","ponte",FASES[1].preparo),
           "Use E na roda para abrir a água. Para usar a fagulha, ilumine a seda marcada no chão e atraia um fio até ela."),
    Ensaio("Raízes do Córrego",1,(2600,CHAO),("meio","dreno","lingueta","ponte","ralo"),
           "S + Espaço desce pelas grades. A aranha investiga onde Lume pousou. Pegue a membrana e suba pelos galhos a leste."),
    Ensaio("Patrulha em dupla",0,(1510,CHAO),("inimigo_1595",),
           "Morcego pressiona, aranha flanqueia. V troca de arma. Ctrl + J interrompe a preparação. Q/F usa pólen, que retarda asas e desfaz projéteis à frente."),
    Ensaio('Casco Oco',2,(ARENA-20,CHAO),('meio','marco','no','brasa','vagem'),
           'Salte o chifre e a onda da queda. Use G na seiva central e faça a carga cruzá-la, ou empurre a seiva e acenda a brasa com E.'),
    Ensaio('A Coruja',3,(ARENA-20,CHAO),('meio','marco','roldana','contrapeso','eco_antigo'),
           'Mova o sino com E. Use G na marca sob o sino para tocá-lo de longe, ou use E de novo. Na raiz direita, lance K perto da face.'),
    Ensaio('Oficina dos Espinhos',0,(160,CHAO),(),
           'V alterna espinho rápido e agulha longa. Compare em dois alvos imóveis. Ctrl carrega luz; ataques normais são gratuitos. E no abrigo restaura reservas e alvos. Protótipo isolado.'),
    Ensaio('Raízes do Bosque',0,(1538,CHAO),('pedido_raizes','inimigo_1548','inimigo_1660','inimigo_1978'),
           'Leia a marca com E. S + Espaço na grade à direita desce por três salas no mesmo mapa. O pino da galeria abre o viveiro; o cipó do poço sempre permite voltar.'),
    Ensaio('Caruncho do Viveiro',0,(2230,1282),('pedido_raizes','pino_ninho','porta_ninho'),
           'Siga à esquerda. Carapaça frontal: terceiro corte, ataque por cima ou pelas costas. Pule as ondas e leia o segundo golpe. Recolha o âmbar e solte o nó ao fundo após vencer.'),
    Ensaio('Resgate no berçário',0,(1635,1282),('pino_ninho','porta_ninho','caruncho_vencido'),
           'E conversa com Tila. Leia as páginas e escolha entre marcar a trilha com luz ou preparar um pavio único. Esc deixa a escolha para depois.'),
    Ensaio('Jardim do Último Sinal',1,(2510,790),(),
           'Fale com Tila na ponte. Busque o orvalho na copa. A grade da estufa leva à calha de Bento.'),
    Ensaio('Último chamado',3,(ARENA+75,CHAO),('meio','marco','roldana','contrapeso','eco_antigo'),
           'E recolhe orvalho e K responde no ninho ativo. Leia a altura dos rasantes. Nas faixas verticais, saia da mira das penas.'),
    Ensaio('Floresta reacesa',0,(450,CHAO),(),
           'Atravesse a ponte de Véspera e fale com Tila na forquilha. M → Missões e pedidos acompanha a amarra. Vá ao Córrego para visitar Bento.'),
    Ensaio('Escuta dos ataques',0,(160,CHAO),(),
           'J escolhe a família; K escolhe a espécie; E toca o aviso à direita. Trinta avisos próprios. Compare por ouvido antes de avaliar no combate.'),
    Ensaio('Clareira da Vigília',0,(1510,CHAO),('meio','valvula','peca'),
           'No escuro, os guardas cercam e revezam golpes. K clareia e cega por instantes. Na luz, dois podem atacar juntos. Após vencer, E recolhe o núcleo e E na tocha acende a clareira.'),
    Ensaio('Globos e tochas',0,(1700,1282),('pino_ninho','porta_ninho','caruncho_vencido'),
           'Recolha núcleo e globo com E. Vá à tocha à direita e use E: a região ficará clara. Q escolhe globo; F fixa outra luz permanente no local. Os ensaios preservam a História.'),
    Ensaio('Combos da colônia',0,(160,CHAO),(),
           'J/J/J, J/L/J, K/L. Ctrl + J ou L dobra o dano e gasta brilho, depois vida se faltar. Acertos recuperam brilho; dano zera o multiplicador. E no abrigo repõe alvos.'),
    Ensaio("Beiral do Taquaral",2,(263,CHAO),(),
           "Salte nas sementes que sobem. Segure Espaço ao cair; saia pela esquerda para pousar no alto. Na descida à direita, solte e retome Espaço sob a aba."),
    Ensaio("Galeria das Sementes",2,(2180,CHAO),("no","meio","brasa","inimigo_1980"),
           "E lê a placa de Risca. Use S + Espaço nos patamares. O cipó sempre permite voltar."),
    Ensaio("O sino soterrado",3,(2530,237),("meio","roldana","contrapeso"),
           "Desça pelas duas grades com S + Espaço. E toca o sino. Suba pelos degraus da direita para baixar a passarela."),
    Ensaio("Nicho dos Berços",2,(1700,968),("no","meio","brasa","inimigo_1980","cavilha_sementes",
           "veneziana_sementes_aberta","inimigo_1910","inimigo_2087"),
           "Erga a tranca com E. Salte o bote e ataque a brecha. Ctrl + J atravessa as escamas e K desfaz o veneno próximo. V troca de arma."),
    Ensaio("Duelo da aranha",0,ABRIGO,(),
           "Referência S02 de fio e salto, com replay. Os vinte combos novos estão em Patrulha em dupla e na História. E recupera luz no abrigo."),
)
INDICE_ARANHA = len(ENSAIOS) - 1


def preparar_ensaio(indice, dificuldade, semente=SEMENTE_ARANHA):
    if indice == INDICE_ARANHA:
        return DueloAranha(dificuldade, semente)
    cena=ENSAIOS[indice]
    if cena.nome=='Escuta dos ataques':
        from .escuta import Escuta
        return Escuta(dificuldade)
    if cena.nome in ('Oficina dos Espinhos','Combos da colônia'):
        from .oficina_armas import Oficina
        jogo=Oficina(dificuldade)
        if cena.nome=='Combos da colônia':jogo.ensaio_combos=True
        jogo.notificar(cena.pista,8)
        return jogo
    jogo=Jornada("historia",dificuldade,cena.etapa)
    jogo.campo_testes=True
    jogo.flags.update(cena.flags)
    jogo.entrar(cena.etapa)
    jogo.checkpoint=cena.pos
    jogo.reiniciar()
    if cena.nome in ('Jardim do Último Sinal','Último chamado','Floresta reacesa'):
        jogo.sobreviventes={i:{'oficio':'trilha','premio':False} for i in ('tila','bento','aru')}
    if cena.nome=='Jardim do Último Sinal':
        from .corte_vertical import entrar
        jogo.cartografia.add('jardim_aberto');jogo.missao='jardim'
        entrar(jogo,'jardim');jogo.bolsa.receber('balsamo',2)
    elif cena.nome=='Último chamado':
        from .chefes import Encontro
        from .ultimo_chamado import iniciar
        jogo.boss=Encontro(3,ARENA,CHAO,despertar=True,aliados=3,dificuldade=dificuldade)
        iniciar(jogo.boss,jogo.eventos)
    elif cena.nome=='Floresta reacesa':
        jogo.concluida=True
        for n in range(4):
            jogo.historico.setdefault((0,n),set()).update(('raiz','chefe','meio','marco',FASES[n].preparo,*FASES[n].mecanismos))
        jogo.restauradas=4
    if cena.nome=="Patrulha em dupla":
        jogo.ensaio_tatico=True
        jogo.bolsa.receber("polen",2)
        jogo.bolsa.receber("pavio",1)
    if cena.nome=="Nicho dos Berços":
        jogo.bolsa.receber("polen",2)
        jogo.bolsa.receber("casulo",1)
    if cena.nome in ("Patrulha em dupla", "Nicho dos Berços"):
        jogo.ensaio_troca_arma = True
    if cena.nome in ('Raízes do Bosque','Caruncho do Viveiro'):
        jogo.missao='pedido_raizes'
        jogo.bolsa.receber('balsamo',1)
    if cena.nome=='Clareira da Vigília':
        jogo.bolsa.receber('balsamo',1)
    jogo.lume.iframes=0.
    jogo.notificar(cena.pista,8)
    return jogo
