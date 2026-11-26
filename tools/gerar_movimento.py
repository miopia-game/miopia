"""Gera folhas de movimento a partir das ilustrações de Miopia.

Execute na raiz com Python e Pillow. O jogo só precisa dos PNGs e do manifesto.
As coordenadas dos membros abaixo seguem uma grade de 0 a 10 em cada pose.
"""
from functools import partial
from math import cos, exp, hypot, pi, radians, sin, tau
from pathlib import Path
import json

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ARTE = Path(__file__).resolve().parents[1] / "assets" / "arte"
SAIDA = ARTE / "movimento-v2"
MARGEM = 35
COLUNAS = 4
QUADROS = 24

# Cada grupo alterna o apoio. A primeira posição é a junta, a segunda é a ponta.
PATAS = {
    "lume": ((4.2,7.2,2.7,9.8), (5.1,7.1,4.1,9.8), (5.9,7.1,5.7,9.8), (6.6,7,7.4,9.8)),
    "aranha": ((2.5,4.4,.12,9.5), (3.4,4.3,1.7,9.6), (4.7,4.3,3.4,9.9),
               (5.4,4.7,5.5,9.1), (6.1,5.2,7.1,9.8), (8.2,5,9.6,9.5)),
    "carabideo": ((2.6,6.1,.45,9.9), (3.6,6.1,2.19,9.8), (4.7,6.1,3.7,9.8),
                  (5.4,6.2,5.4,9.8), (6.4,6,7.3,9.8)),
    "sombra": ((3.2,6.8,2.2,9.6), (4,6.2,3.1,9.7), (4.9,6.2,4.5,9.4),
               (5.6,6.7,5.7,9.55), (6.95,7.3,7.8,9.7)),
    "caruncho": ((1.8,6.9,.6,9.6), (2.7,6.4,2.1,9.9), (3.9,6.2,3.4,9.65),
                 (4.9,6.2,5.3,9.95), (6.6,7.4,7.6,9.45)),
    "casco-oco": ((1.95,7,.38,9.8), (2.8,7.3,2.25,9.72), (4.1,7.1,3.4,9.93),
                   (5.4,7.1,5.25,9.45), (6.3,7.3,7.1,9.99), (7.7,7.4,9.2,9.55)),
    "tecela": ((2.2,5.45,.28,9.15), (3.1,5.45,1.6,9.6), (3.8,5.65,3.15,9.76),
                (6.2,5.5,6.55,9.9), (7.45,5.1,8.45,9.5), (8.2,4.9,9.6,8.9)),
}

# Ajustes da posição das pernas nas poses baixas usadas nas investidas.
INVESTIDAS = {
    "aranha": ((2.55,4.5,.15,8.9),(3.35,4.4,2.65,9.45),(4.3,4.7,4.6,9.9),
               (5.05,5.5,5.4,9.4),(7.5,4.6,8,7.1),(8.25,5.5,9.8,9.05)),
    "carabideo": ((2,6.86,.18,9.9),(3.4,6.2,2.55,9.35),(4.2,6.25,3.1,9.85),
                  (5.4,6.3,5.7,9.7),(6.3,6.9,8,9.6)),
    "casco-oco": ((1.9,7.2,.25,9.9),(3.25,7.15,2.24,9.8),(5.1,7.05,4.95,9.72),
                   (6.2,7.5,7.13,9.83),(7.56,7.4,9.36,9.63)),
}

# Pivô, contorno pintado e amplitude da abertura de cada asa. As peças mantêm
# contato com a junta enquanto a ponta percorre a batida.
ASAS = {
    "lume-voo": (
        ((5.05,3.99), ((5.4,3.95),(4,3.03),(2.75,2.1),(.7,1.8),(.37,3.15),(1.37,4.02),(3.5,4.15)), 31),
        ((4.7,4.01), ((4.8,4.10),(3.63,3.88),(1.75,3.82),(0,4.06),(0,5.26),(1.1,5.45),(2.82,4.9)), 25),
    ),
    "lume-planar": (
        ((5.67,3.96), ((5.8,4),(4.65,2.4),(3.05,1.18),(1.08,.12),(0,.21),(0,1.96),(1.05,3.64),(2.89,4.35)), 14),
        ((4.88,4.35), ((4.94,4.41),(3.1,3.95),(2.1,4.2),(.68,4.65),(0,5.5),(0,6.57),(1.31,6.57),(2.14,5.84)), 12),
    ),

}


def origem_lume(indice):
    atlas = Image.open(ARTE / "lume_ilustrado_atlas.png").convert("RGBA")
    w,h = atlas.width//4,atlas.height//2
    x,y = (indice%4)*w,(indice//4)*h
    pose = atlas.crop((x,y,x+w,y+h))
    caixa = pose.getchannel("A").point(lambda alpha: 255 if alpha>=160 else 0).getbbox()
    return pose.crop(caixa)


def original(nome, pose):
    return Image.open(ARTE / "inimigos-v2" / f"{nome}-{pose}.png").convert("RGBA")


def quadro_base(imagem, escala=1):
    w = 144
    h = round(imagem.height*w/imagem.width)
    fundo = Image.new("RGBA",((w+2*MARGEM)*escala,(h+2*MARGEM)*escala))
    tamanho = w*escala,h*escala
    fundo.paste(imagem.resize(tamanho,Image.Resampling.LANCZOS),(MARGEM*escala,MARGEM*escala))
    return fundo,w,h


def coordenada(x, y, w, h):
    return MARGEM+x*w/10,MARGEM+y*h/10


def malha(imagem, w, h, deslocamento):
    largura,altura = imagem.size
    escala = largura//(w+2*MARGEM)
    resolucao = 6*escala
    pontos = {}
    for y in range(0,altura+resolucao,resolucao):
        for x in range(0,largura+resolucao,resolucao):
            px,py = min(x,largura),min(y,altura)
            dx,dy = deslocamento((px/escala-MARGEM)*10/w,(py/escala-MARGEM)*10/h)
            pontos[x,y] = px-dx*w*escala/10,py-dy*h*escala/10
    mosaico = []
    for y in range(0,altura,resolucao):
        for x in range(0,largura,resolucao):
            cantos = ((x,y),(x,y+resolucao),(x+resolucao,y+resolucao),(x+resolucao,y))
            area = x,y,min(x+resolucao,largura),min(y+resolucao,altura)
            mosaico.append((area,tuple(v for canto in cantos for v in pontos[canto])))
    return imagem.transform(imagem.size,Image.Transform.MESH,mosaico,Image.Resampling.BICUBIC)


# Fração do ciclo em apoio, intervalo entre pares e elevação da ponta.
# São ajustes de animação para as patas visíveis na vista lateral.
PASSADAS = {
    "aranha": (.57,.085,1.12), "tecela": (.64,.10,1.05),
    "carabideo": (.59,.015,.94), "caruncho": (.68,.032,.87),
    "casco-oco": (.72,.022,.76), "sombra": (.60,.07,1.06),
    "lume-andar": (.54,.045,1.16),
}


def passada(patas,fase,x,y,perfil,amplitude):
    apoio, intervalo, altura = perfil
    dx = dy = forca = 0.
    for i,(jx,jy,px,py) in enumerate(patas):
        baixo = max(0.,min(1.22,(y-jy+.10)/(py-jy+.10)))
        eixo = jx+(px-jx)*min(baixo,1.)
        peso = exp(-((x-eixo)/.63)**2) * baixo**1.33
        instante = (fase/tau + .5*(i%2) + intervalo*(i//2)) % 1.
        em_apoio = instante < apoio
        t = instante/apoio if em_apoio else (instante-apoio)/(1-apoio)
        suave = t*t*(3-2*t)
        alcance = (1-2*suave) if em_apoio else (2*suave-1)
        dx += peso*alcance
        if not em_apoio:
            dy -= peso*altura*sin(pi*t)**2
        forca += peso
    suavizar = max(1.,forca)
    # Antenas e carapaça absorvem parte da passada sem arrastar as pontas no piso.
    contrapeso = max(0.,1-y/7.)*.16*cos(fase*2)
    return amplitude*dx/suavizar,amplitude*dy/suavizar+contrapeso


def ondular(fase,x,y):
    corpo = max(0.,min(1.,(9.2-x)/4.2))
    ventre = max(0.,min(1.,(y-3.9)/3.8))
    # A onda segue da cabeça (+x) à cauda. A vista lateral encurta a
    # componente em profundidade e mantém a barriga junto ao chão.
    onda = fase+x*.84
    return corpo*ventre*.80*cos(onda), corpo*ventre*.28*sin(onda)


def assentar(imagem,h):
    # Usa o contorno pintado e ignora o halo semitransparente do recorte.
    limite = imagem.getchannel("A").point(lambda a: 255 if a>=80 else 0).getbbox()
    ajustada = Image.new("RGBA",imagem.size)
    ajustada.paste(imagem,(0,MARGEM+h-limite[3]))
    return ajustada


def percurso_serpente(nome, faixa, dados):
    # Preserva a cabeça e comprime o trecho longo do tronco para que o
    # animal continue legível ao ocupar entre 82 e 108 pixels na partida.
    alpha = faixa.getchannel("A").point(lambda a: 255 if a>32 else 0)
    faixa = faixa.crop(alpha.getbbox())
    pescoco = round(faixa.width*.73)
    tronco = faixa.crop((0,0,pescoco,faixa.height))
    frente = faixa.crop((pescoco,0,faixa.width,faixa.height))
    tronco = tronco.resize((round(pescoco*.56),faixa.height),Image.Resampling.LANCZOS)
    pose = Image.new("RGBA",(tronco.width+frente.width,faixa.height))
    pose.paste(tronco)
    pose.paste(frente,(tronco.width,0))
    inicio_pescoco = 10*tronco.width/pose.width
    def quadro(base,w,h,t):
        def arrastar(x,y):
            peso = max(0.,min(1.,(inicio_pescoco+1.1-x)/2.1))
            onda = t + x*(1.0 if nome=="cobra" else .81)
            # O deslocamento é comum a toda a seção transversal para que
            # barriga e dorso acompanhem a onda com a mesma espessura.
            return .37*peso*cos(onda), 1.0*peso*sin(onda)
        return malha(base,w,h,arrastar)
    salvar(nome,pose,quadro,dados,piso=True)

    def recolher(base,w,h,t):
        p = min(1.,t/tau * QUADROS/(QUADROS-1))
        p = p*p*(3-2*p)
        cauda, cabeca = 2.45*p, -1.05*p
        contracao = 1+(cabeca-cauda)/inicio_pescoco
        def curvar(x,y):
            # Inversa por trecho: a cauda se aproxima, o crânio translada
            # inteiro e o pescoço sobe sem comprimir o desenho do olho.
            xs = (x-cauda)/contracao if x < inicio_pescoco+cabeca else x-cabeca
            colo = max(0.,min(1.,(xs-inicio_pescoco+2.3)/2.3))
            subida = 2.65*colo + .63*sin(xs*1.35)*(1-colo)
            return x-xs, -subida*p
        return malha(base,w,h,curvar)
    salvar(nome+"-recolher",pose,recolher,dados,piso=True)


def mascaras(imagem,w,h,asas):
    corpo = imagem.copy()
    componentes = []
    for pivo,poligono,amplitude in asas:
        origem = coordenada(*pivo,w,h)
        recorte = Image.new("L",imagem.size)
        ImageDraw.Draw(recorte).polygon([coordenada(*v,w,h) for v in poligono],fill=255)
        asa = imagem.copy()
        asa.putalpha(ImageChops.multiply(imagem.getchannel("A"),recorte))
        # A junta fica sobreposta ao corpo para a membrana nunca se separar.
        retirar = recorte.copy()
        x,y = origem
        r = w*.068
        ImageDraw.Draw(retirar).ellipse((x-r,y-r,x+r,y+r),fill=0)
        corpo.putalpha(ImageChops.subtract(corpo.getchannel("A"),retirar))
        componentes.append((asa,origem,amplitude))
    return corpo,componentes


def recortar_residuos(imagem):
    """Retira fragmentos de tinta que ficam isolados ao fechar uma asa."""
    original = imagem.getchannel("A")
    largura,altura = original.size
    marcas = bytearray(int(a>35) for a in original.tobytes())
    manter = bytearray(len(marcas))
    for i,ocupado in enumerate(marcas):
        if not ocupado:
            continue
        grupo = [i]
        marcas[i] = 0
        for pos in grupo:
            x,y = pos%largura,pos//largura
            for viz in (pos-1 if x else pos,pos+1 if x<largura-1 else pos,
                        pos-largura if y else pos,pos+largura if y<altura-1 else pos):
                if marcas[viz]:
                    grupo.append(viz)
                    marcas[viz] = 0
        if len(grupo) >= 42:
            for pos in grupo:
                manter[pos] = 255
    borda = Image.frombytes("L", imagem.size, bytes(manter)).filter(ImageFilter.MaxFilter(5))
    imagem.putalpha(ImageChops.multiply(original,borda))
    return imagem


def bater(pecas,fase):
    corpo,asas = pecas
    imagem = Image.new("RGBA",corpo.size)
    for n,(asa,(px,py),amplitude) in enumerate(reversed(asas)):
        t = fase+n*.10
        a = radians(amplitude*sin(t))
        c,s = cos(a),sin(a)
        dobra = .82+.18*cos(t)
        afim = (c,s,px-c*px-s*py,-s/dobra,c/dobra,py+(s*px-c*py)/dobra)
        imagem.alpha_composite(asa.transform(asa.size,Image.Transform.AFFINE,afim,Image.Resampling.BICUBIC))
    imagem.alpha_composite(corpo)
    return recortar_residuos(imagem)


def salvar(nome, fonte, funcao, dados, *, piso=False):
    # As malhas dos inimigos trabalham no desenho em 2x. Só reduzimos
    # depois de mover os membros. A Coruja já compõe suas peças em 3x.
    escala = 1 if nome == "coruja" or nome.startswith("lume-") else 2
    base,w,h = quadro_base(fonte,escala)
    cw,ch = w+2*MARGEM,h+2*MARGEM
    atlas = Image.new("RGBA",(cw*COLUNAS,ch*(QUADROS//COLUNAS)))
    for indice in range(QUADROS):
        imagem = funcao(base,w,h,tau*indice/QUADROS)
        if escala != 1:
            imagem = imagem.resize((cw,ch),Image.Resampling.LANCZOS)
        if piso:
            imagem = assentar(imagem,h)
        atlas.paste(imagem,((indice%COLUNAS)*cw,(indice//COLUNAS)*ch))
    atlas.save(SAIDA / f"{nome}.png",optimize=True)
    dados[nome] = [w,h,MARGEM]


def asas(nome,imagem,dados):
    base,w,h = quadro_base(imagem)
    pecas = mascaras(base,w,h,ASAS[nome])
    salvar(nome,imagem,lambda _base,_w,_h,fase: bater(pecas,fase),dados)


# Limite horizontal da junta, altura da raiz da asa e amplitude por lado.
# O vôo usa a imagem completa com uma malha contínua. As pontas sobem e
# descem sem recortar a membrana, a plumagem ou os contornos do ombro.
VOO = {
    "morcego": ((4.9,7.5,2.65),(6.1,7.4,2.40)),
    "vespa": ((6.0,4.7,2.25),None),
    "vespa-impulso": ((6.6,4.9,2.05),None),
    "asa-fendida": ((5.5,6.8,2.40),(7.1,6.5,2.20)),
    "coruja-impulso": ((4.9,7.5,1.80),(6.5,7.0,2.05)),
}


# Em cada pose, a caixa abrange crista, máscara, olho e bico. Apenas fora
# dela a deformação das penas reaparece, com transição contínua no pescoço.
CABECAS = {
    "morcego": (6.05,7.25,9.4,9.85),
    "asa-fendida": (6.24,6.65,8.9,8.35),
    "vespa": (6.02,2.85,8.06,5.10),
    "vespa-impulso": (6.35,4.38,8.88,7.15),
    "coruja-impulso": (4.65, 3.75, 9.02, 8.14),
}


def mobilidade(x, y, cabeca):
    if cabeca is None:
        return 1.
    esquerda, topo, direita, base = cabeca
    dx = max(esquerda-x, 0., x-direita)
    dy = max(topo-y, 0., y-base)
    distancia = min(1., hypot(dx,dy)/.82)
    return distancia*distancia*(3.-2.*distancia)


def voo_continuo(nome,imagem,dados):
    esq,dir = VOO[nome]
    cabeca = CABECAS.get(nome)
    membrana = nome in {"morcego","asa-fendida"}
    e_vespa = nome.startswith("vespa")
    def quadro(base,w,h,t):
        def deslocar(x,y):
            dx = dy = 0.
            for lado,junta in ((-1,esq),(1,dir)):
                if junta is None:
                    continue
                eixo,raiz,curso = junta
                distancia = min(1.25,max(0.,lado*(x-eixo)/(10-eixo if lado>0 else eixo)))
                alcance = distancia**1.4
                # A transição larga limita o gradiente e conserva as regiões
                # pintadas entre a asa e a face enquanto as pontas se movem.
                peso = min(1.,max(0.,(raiz-y)/3.1))
                atraso = .68 if membrana else .23
                desloc = sin(t - atraso*distancia) * peso * alcance
                dy += curso * desloc
                dobra = 1.55 if membrana else .18 if e_vespa else .9
                recolher = ((1-cos(t))*.5)**2 if e_vespa else max(0.,-cos(t))**2
                dx += -lado * dobra * peso * alcance * recolher
                if membrana:
                    # O punho conduz o recolhimento, a membrana acompanha.
                    dy += .64*sin(pi*min(1.,distancia))*peso*sin(t-.58)
            if e_vespa:
                # Patas pendentes acompanham o tórax com uma oscilação menor.
                tarsos = max(0.,min(1.,(y-6.4)/3.4))*exp(-((x-5.1)/1.3)**2)
                dx += .44*tarsos*sin(t-.7)
            movimento = mobilidade(x, y, cabeca)
            return dx*movimento,dy*movimento
        return malha(base,w,h,deslocar)
    salvar(nome,imagem,quadro,dados)


def passos(nome,imagem,juntas,dados,amplitude=1.):
    especie = nome.removesuffix("-impulso")
    def quadro(base,w,h,t):
        def deslocar(x,y):
            dx,dy = passada(juntas,t,x,y,PASSADAS[especie],amplitude)
            if nome == "lume-andar":
                antena = max(0.,1-y/6.)*max(0.,min(1.,(x-4.8)/2))
                dx += antena*.55*sin(t+.7)
                dy += max(0.,1-y/8.)*.25*cos(2*t)
            elif especie == "sombra":
                manto = max(0.,1-x/6.4)*max(0.,1-abs(y-4.5)/3.8)
                dy += .61*manto*sin(t-.65)
            return dx,dy
        return malha(base,w,h,deslocar)
    salvar(nome,imagem,quadro,dados,piso=True)


def no_fio(base,w,h,t):
    def segurar(x,y):
        lateral = (x-5.)/5.
        ponta = min(1.,abs(lateral)**1.5)
        alto = max(0.,min(1.,(5.3-y)/3.8))
        peso = ponta*(.24+.76*alto)
        fase = t+(0. if lateral<0 else pi)
        puxada = sin(fase)
        # Ao soltar a seda a ponta abre para fora e retorna por outro arco.
        abrir = alto*cos(fase-.16)
        return lateral*peso*(.55+.72*puxada+.82*abrir), peso*1.18*puxada
    return malha(base,w,h,segurar)


def gesto(nome,base,w,h,t):
    # Um impulso curto que ganha extensão e termina assentado.
    p = min(1.,t/tau*QUADROS/(QUADROS-1))
    impulso = .18*(1-p) + .82*sin(pi*p)**2
    retorno = sin(tau*p)*sin(pi*p)
    def deslocar(x,y):
        lateral = (x-5.)/5
        topo = max(0.,min(1.,(8.8-y)/4.3))
        if nome == "aranha":
            patas = max(0.,min(1.,(y-4.2)/4.7))
            return -lateral*patas*1.18*impulso, -patas*1.46*impulso
        if nome == "tecela":
            ponta = abs(lateral)**1.4
            return lateral*ponta*.93*impulso, ponta*.98*retorno
        if nome == "sombra":
            manto = topo*max(0.,1-x/6.5)
            return -.84*manto*impulso, -1.38*manto*impulso
        # No golpe sísmico, a carapaça sobe e volta sobre patas plantadas.
        return .35*topo*retorno, -topo*.87*impulso
    return malha(base,w,h,deslocar)


# Ângulos do braço e da mão e profundidade das penas, da posição alta
# à descida estendida e à subida recolhida. Os dois ombros compartilham fase.
BATIDA_CORUJA = (
    (-44, -32, .72), (-24, -35, .85), (7, -8, 1.), (33, 23, .95),
    (43, 48, .82), (16, 54, .60), (-17, 38, .52), (-39, 5, .57),
)


def asa_coruja(peca, tela, ombro, largura, lado, pose):
    braco, mao, profundidade = pose
    braco, mao = radians(braco), radians(mao)
    # A junta fica dentro da pintura para continuar coberta pelo peito.
    # A dobra do punho muda a direção das primárias na volta da batida.
    junta = peca.width * (.92 if lado < 0 else .08)
    escala = largura / peca.width
    meia_asa = largura * .44
    corda = (braco + mao)*.40
    c,s = cos(corda),sin(corda)
    pulso = meia_asa*cos(braco-corda)

    def origem(x, y):
        dx,dy = lado*(x-ombro[0]), y-ombro[1]
        distancia = dx*c+dy*s
        interior = min(pulso, distancia) / cos(braco-corda)
        exterior = max(0., distancia-pulso) / cos(mao-corda)
        u = interior+exterior
        linha = interior*sin(braco-corda) + exterior*sin(mao-corda)
        v = (-dx*s+dy*c-linha) / (escala*profundidade)
        return junta + lado*u/escala, peca.height*.24 + v

    malha = []
    for y in range(0,tela[1],18):
        for x in range(0,tela[0],18):
            b,h = min(x+18,tela[0]),min(y+18,tela[1])
            pontos = origem(x,y) + origem(x,h) + origem(b,h) + origem(b,y)
            malha.append(((x,y,b,h),pontos))
    return peca.transform(tela,Image.Transform.MESH,malha,Image.Resampling.BICUBIC)


def voo_coruja(dados):
    folha = Image.open(Path(__file__).parent / "fontes" / "coruja-voo-tinta.png").convert("RGBA")
    partes = []
    for i in range(3):
        faixa = folha.crop((i*folha.width//3,0,(i+1)*folha.width//3,folha.height))
        faixa.putalpha(faixa.getchannel("A").point(lambda a: max(0,min(255,(a-10)*255//210))))
        caixa = faixa.getchannel("A").point(lambda a: 255 if a>=24 else 0).getbbox()
        partes.append(faixa.crop(caixa))
    perto, tronco, longe = partes
    # A composição é feita a 3x. Rosto e peito têm uma transformação única
    # para todos os quadros. Somente as duas asas giram e se recolhem.
    escala = 3
    tronco = tronco.resize((84*escala,80*escala),Image.Resampling.LANCZOS)
    tronco = tronco.rotate(-24,Image.Resampling.BICUBIC,expand=True)
    tronco = tronco.resize(tuple(round(v/escala) for v in tronco.size),Image.Resampling.LANCZOS)
    # Torna opaca a tinta sólida após a filtragem da borda. A asa que
    # passa atrás da máscara facial só aparece através do espaço livre.
    tronco.putalpha(tronco.getchannel("A").point(lambda a: 255 if a>=248 else a))
    def ponto(x,y):
        return (x+MARGEM)*escala, (y+MARGEM)*escala

    def quadro(base,w,h,t):
        tela = tuple(n*escala for n in base.size)
        pos = t*len(BATIDA_CORUJA)/tau
        i, f = int(pos), pos%1
        a,b,c,d = (BATIDA_CORUJA[(i+j)%len(BATIDA_CORUJA)] for j in (-1,0,1,2))
        # Tangentes compartilhadas entre poses, inclusive no fim do ciclo.
        pose = [v + .5*f*((z-u)+f*((2*u-5*v+4*z-k)+f*(3*v-3*z+k-u)))
                for u,v,z,k in zip(a,b,c,d)]
        distal = asa_coruja(longe,tela,ponto(74,45),78*escala,1,pose)
        proximal = asa_coruja(perto,tela,ponto(53,43),86*escala,-1,pose)
        imagem = distal.resize(base.size,Image.Resampling.LANCZOS)
        imagem.alpha_composite(tronco,(MARGEM+3,MARGEM-13))
        imagem.alpha_composite(proximal.resize(base.size,Image.Resampling.LANCZOS))
        return imagem

    salvar("coruja",original("coruja","preparacao"),quadro,dados)


def principal():
    SAIDA.mkdir(parents=True,exist_ok=True)
    dados = {}
    passos("lume-andar",origem_lume(0),PATAS["lume"],dados,1.30)
    asas("lume-voo",origem_lume(3),dados)
    asas("lume-planar",origem_lume(4),dados)
    for nome,pose in (("morcego","ataque"),("asa-fendida","ataque"),("vespa","repouso"),
                      ("vespa-impulso","ataque"),("coruja-impulso","ataque")):
        voo_continuo(nome,original(nome.removesuffix("-impulso"),pose),dados)
    voo_coruja(dados)
    for nome,juntas in PATAS.items():
        if nome == "lume":
            continue
        if nome == "tecela":
            salvar(nome,original(nome,"preparacao"),no_fio,dados)
        else:
            passos(nome,original(nome,"repouso"),juntas,dados,1.21)
            passos(nome+"-impulso",original(nome,"ataque"),INVESTIDAS.get(nome,juntas),dados,1.14)
        salvar(nome+"-gesto",original(nome,"ataque"),partial(gesto,nome),dados)
    fonte = Image.open(Path(__file__).parent / "fontes" / "serpentes-em-percurso-tinta.png").convert("RGBA")
    corte = round(fonte.height*.48)
    for nome,topo,base in (("cobra",0,corte),("cobra-dos-bercos",corte,fonte.height)):
        percurso_serpente(nome,fonte.crop((0,topo,fonte.width,base)),dados)
        salvar(nome+"-impulso",original(nome,"ataque"),
               lambda base,w,h,t: malha(base,w,h,partial(ondular,t)),dados)
    (SAIDA / "folhas.json").write_text(json.dumps(dados,indent=2)+"\n")


if __name__ == "__main__":
    principal()
