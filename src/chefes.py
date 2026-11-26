"""Encontros laterais. Toda geometria de combate usa coordenadas do mundo."""
from dataclasses import dataclass
from functools import lru_cache
from math import ceil, hypot, sin
from pathlib import Path

import pygame


@dataclass(frozen=True)
class Ficha:
    nome: str
    folha: str
    pista: str
    janela: str
    desfecho: str


@dataclass(frozen=True)
class Ritmo:
    criticos: int
    janela: float
    dano_comum: float
    recuperacao: float


SERENO = Ritmo(2, 1., 1., 1.)
NORMAL = Ritmo(3, .86, .58, .85)
DIFICIL = Ritmo(3, .72, .44, .72)


FICHAS = (
    Ficha("Asa Fendida", "asa-fendida", "Atraia a asa até uma raiz marcada. Observe a altura das asas.",
          "Dorso exposto. Suba no patamar e golpeie com J.", "Asa Fendida recolhe as asas."),
    Ficha("Tecelã do Vão", "tecela", "Gire a válvula à esquerda para romper os fios.",
          "O ventre tocou o leito. Aproxime-se e golpeie com J.", "A teia solta a margem."),
    Ficha("Casco Oco", "casco-oco", "Leve a seiva ao entalhe. Depois, acione a brasa.",
          "A casca se abriu. Salte até a marca e golpeie com J.", "O guardião baixa a carapaça."),
    Ficha("A Coruja", "coruja", "Mova o sino pela válvula e toque a corda com E.",
          "Ela escuta. Suba perto da face e lance um clarão (K).", "A Coruja reconhece Lume."),
)

FERRUGEM = (222, 132, 99)
OURO = (252, 206, 132)
TEAL = (118, 176, 167)
FIO = (183, 211, 197)
ESCURO = (31, 44, 48)
PELE = (75, 95, 88)


@dataclass
class Fio:
    x: float
    y: float
    vx: float
    vy: float
    tempo: float = 3.


@dataclass
class Trama:
    faixa: pygame.FRect
    tempo: float = 2.8
    tocada: bool = False


def aproximar(a, b, passo):
    return a + max(-passo, min(passo, b-a))


@lru_cache(maxsize=4)
def _quadros(nome):
    """Folhas compartilhadas; o espelhamento acontece uma vez por pose/quadro."""
    raiz = Path(__file__).resolve().parent.parent
    folha = pygame.image.load(str(raiz / "assets" / "chefes" / (nome + ".png")))
    w, h = folha.get_width() // 4, folha.get_height() // 4
    quadros = {}
    for pose in range(4):
        for frame in range(4):
            quadro = folha.subsurface((frame*w, pose*h, w, h))
            quadros[(pose, frame, 1)] = quadro
            quadros[(pose, frame, -1)] = pygame.transform.flip(quadro, True, False)
    return quadros


class Encontro:
    """Um encontro novo restaura a geometria e todos os objetos essenciais."""
    def __init__(self, indice: int, inicio: int, chao: int, largura: int = 760, *,
                 despertar=False, aliados=0, dificuldade="normal"):
        self.indice, self.inicio, self.chao, self.largura = indice, inicio, chao, largura
        self.dificuldade = dificuldade
        self.ritmo = (SERENO if dificuldade in ("fácil", "facil", "sereno") else
                      DIFICIL if dificuldade in ("difícil", "dificil") else NORMAL)
        self.meta = self.ritmo.criticos
        self.despertar=despertar and indice==3
        self.aliados=max(0,min(3,aliados));self.coro_iniciado=False
        self.ficha = FICHAS[indice]
        self.nome = self.ficha.nome
        self.esq = inicio + 62
        self.dir = inicio + largura - 62
        self.x, self.y = self.dir - 40., chao - 110.
        self.frente = -1
        self.estado = "busca"
        self.tempo, self.relogio = 1.65, 0.
        self.duracao_estado = self.tempo
        self.progresso = 0
        self.vida = self.vida_max = 100.
        self.contato_corte = None
        self.ultimo_corte = None
        self.ultimo_golpe_t = -1.
        self.vencido = False
        self.turno = 0
        self.destino = self.esq
        self.alvo_y = chao - 28.
        self.impacta = False
        self.atingiu = False
        self.asa_rasteira = False
        self.asa_mira_no_ar = False
        self.asa_isca = None
        self.ultima_fagulha = None
        self.asa_brecha_fagulha = False
        self.marca_acesa = None
        self.reacao_fagulha = ""
        self.fios = []
        self.segundo_fio = None
        self.tramas = []
        self.agua = self.onda = 0.
        self.barrel_x = self.inicio + 102.
        self.engatado = self.assentado = self.tabua_quebrada = False
        self.sino_movido = self.sino_soou = False
        self.x_ouvido = None
        self.ninhada = None
        if indice == 1:
            self.x, self.y = self.cortina, chao-203.
            from .ninhada import Ninhada
            self.ninhada = Ninhada(self)
        if indice == 2:
            self.x, self.y = self.inicio + largura * .77, chao-35.
            from .casco import iniciar
            iniciar(self)
        if indice == 3:
            from .coruja import iniciar
            iniciar(self)
        if indice in (2, 3):
            self.tempo = .75

    @property
    def valvula(self):
        return self.inicio + 180

    @property
    def cortina(self):
        return self.inicio + self.largura * .39

    @property
    def brasa(self):
        return self.inicio + self.largura * .60

    @property
    def entalhe(self):
        return self.inicio + self.largura * (.46 if self.progresso == 0 else .69)

    @property
    def dica(self):
        if self.vencido:
            return self.ficha.desfecho
        if self.estado == "chama_ninhada":
            return "Os casulos se abrem nas marcas. A cortina freia as crias próximas."
        if self.estado.startswith('coro_'):
            if self.coro_faixas:
                return 'Penas no alto. Mova-se antes que caiam.'
            if self.estado in ('coro_aviso', 'coro_investida'):
                return 'Leia a altura do voo e desvie do rasante.'
            return 'E recolhe orvalho · K responde no ninho marcado'
        if self.estado == "aberto":
            if self.reacao_fagulha == "teia":
                return "Seda queimada · ataque o ventre com J"
            if self.reacao_fagulha == "seiva":
                return "Patas presas · salte e ataque a casca com J"
            if self.reacao_fagulha == "sino":
                return "Sino soou à distância · suba e use K na face"
            if self.indice == 0:
                if self.asa_brecha_fagulha:
                    return "Brecha da fagulha · suba e ataque o dorso"
                return "Brecha · suba e ataque o dorso"
            return self.ficha.janela
        if self.indice == 0 and self.estado in ("aviso", "investida"):
            if self.asa_isca:
                return "Voo na fagulha · saia da altura da asa"
            if self.asa_mira_no_ar:
                return "Mude de altura · mira no ar"
            if self.asa_rasteira:
                return "Salte · voo baixo"
            return "Abaixe-se · voo alto"
        if self.indice == 1 and self.estado == "desce" and self.reacao_fagulha == "teia":
            return "O fio queimou · a Tecelã está caindo"
        if self.indice == 1 and self.estado == "aviso":
            return ("Dois fios vindo · E na roda abre a água" if self.segundo_fio
                    else "Fio vindo · E na roda abre a água")
        if self.indice == 2:
            if self.estado == 'muda_casco':
                return 'O casco rachou: agora encadeia dois golpes. Leia o segundo aviso.'
            if self.estado == 'aviso':
                return {'salto': 'Ele vai saltar. Mova-se e pule a onda.',
                        'varrida': 'O chifre varre a frente. Afaste-se ou passe por cima.',
                        'retorno': 'Ele muda de lado: prepare outra esquiva.',
                        'carga': 'Chifre baixo. Salte quando ele se aproximar.'}.get(self.tecnica, self.ficha.pista)
            if self.estado in ("rastro", "investida_seiva", "flor"):
                return "O guardião segue a seiva. Salte sobre o casco."
            if self.assentado:
                return "A seiva encaixou. Toque a fonte de brasa (E)."
            if self.engatado:
                return "Caminhe com a seiva até o aro âmbar no chão."
        if self.indice == 3:
            if self.tecnica == "sino" and self.reacao_fagulha == "sino" and self.estado in ("aviso","investida"):
                return "Sino soou · desvie do voo até a raiz direita"
            if self.estado == 'aviso':
                return {'garra': 'A garra desce em diagonal. Mude de altura.',
                        'penas': 'Duas penas vindo. Saia de frente à Coruja.',
                        'rasante': 'Leia a altura do voo antes de saltar ou abaixar.'}.get(self.tecnica, 'O sino a leva à raiz riscada. Suba para lançar K perto da face.')
            if self.sino_movido:
                return "E na roda toca o sino. Na raiz direita, suba e lance K perto da face exposta."
        return self.ficha.pista

    @property
    def som_aviso(self):
        if self.estado == "chama_ninhada":
            return "teia"
        if self.estado.startswith('coro_'):
            return 'coruja_penas' if self.coro_faixas else 'coruja_eco'
        if self.indice == 2:
            return {'salto': 'casco_salto', 'varrida': 'casco_chifre'}.get(self.tecnica, 'casco_avanco')
        if self.indice == 3:
            return {'garra': 'coruja_garra', 'penas': 'coruja_penas'}.get(self.tecnica, 'pressagio')
        if self.indice==0 and self.asa_rasteira:
            return "casco_avanco"
        return ("rasgo","fio_disparo","casco_avanco","pressagio")[self.indice]

    def apoios(self):
        """Apoios de mão única; os degraus junto às marcas sempre ficam disponíveis."""
        base = self.chao
        apoios = [
            pygame.Rect(self.inicio+16, base-66, 147, 12),
            pygame.Rect(self.inicio+self.largura-163, base-66, 147, 12),
            pygame.Rect(self.inicio+186, base-120, 116, 11),
            pygame.Rect(self.inicio+self.largura-302, base-120, 116, 11),
        ]
        if self.indice == 2 and not self.tabua_quebrada:
            apoios.append(pygame.Rect(self.inicio+self.largura//2-46, base-45, 92, 10))
        return apoios

    def marcas_fagulha(self):
        if self.vencido:
            return ()
        if self.indice == 0:
            return tuple((apoio.centerx, apoio.top-4) for apoio in self.apoios()[2:])
        if self.indice == 1:
            return ((round(self.cortina),self.chao-4),)
        if self.indice == 2:
            return ((self.inicio+self.largura//2,self.chao-4),)
        if self.sino_movido and not self.estado.startswith("coro_"):
            return ((self.valvula,self.chao-4),)
        return ()

    def marca_fagulha(self, fagulha):
        if not fagulha:
            return None
        return next((p for p in self.marcas_fagulha()
                     if hypot(fagulha.destino[0]-p[0],fagulha.destino[1]-p[1]) <= 24), None)

    def alvo_fagulha(self, fagulha):
        if fagulha is self.ultima_fagulha:
            return None
        return self.marca_fagulha(fagulha)

    @property
    def pista_fagulha(self):
        return (
            "G · lance a fagulha num patamar marcado",
            "G na seda · faça o fio cruzar a marca",
            "G na seiva · induza a carga a cruzar a marca",
            "G sob o sino · toque à distância" if self.sino_movido else
            "E move o sino · G pode tocá-lo depois",
        )[self.indice]

    def _perto(self, corpo, x, alcance=59):
        return abs(corpo.centerx-x) <= alcance and self.chao-86 <= corpo.bottom <= self.chao+24

    def interacao(self, corpo):
        if self.estado.startswith('coro_'):
            from .ultimo_chamado import perto
            return 'Recolher orvalho do último ninho' if self.coro_gota and perto(self,corpo) else ''
        if self.vencido or self.estado in ("aberto","desce","flor","rastro","investida_seiva",'muda_casco','muda_coruja'):
            return ""
        if self.indice == 1 and self.agua <= 0 and self._perto(corpo, self.valvula):
            return "Abrir cortina de água"
        if self.indice == 2:
            if self.assentado and self._perto(corpo, self.brasa):
                return "Despertar brasa"
            if not self.assentado and self._perto(corpo, self.barrel_x):
                return "Soltar seiva" if self.engatado else "Empurrar seiva"
        if self.indice == 3 and self._perto(corpo, self.valvula):
            return "Tanger sino" if self.sino_movido else "Mover sino"
        return ""

    def _mudar(self, estado, tempo):
        self.estado, self.tempo = estado, tempo
        self.duracao_estado = tempo

    def _usar(self, corpo, eventos):
        acao = self.interacao(corpo)
        if acao == "Abrir cortina de água":
            self.agua = 4.
            self.tramas.clear()
            eventos.extend(("valvula", "agua"))
        elif acao == "Despertar brasa":
            self.engatado = False
            self.destino = self.entalhe
            self.alvo_y = self.chao - 35
            self.frente = 1 if self.destino > self.x else -1
            self.atingiu = False
            self.combo_restante = 0
            self._mudar("rastro", .75)
            eventos.extend(("seiva", "aviso"))
        elif acao in ("Soltar seiva", "Empurrar seiva"):
            self.engatado = not self.engatado
            eventos.append("valvula")
        elif acao == "Mover sino":
            self.sino_movido = True
            eventos.append("valvula")
        elif acao == "Tanger sino":
            self.sino_soou = True
            self.onda = 1.
            eventos.append("sino")
            # O som aciona a busca mesmo quando Lume fica inteiramente imóvel.
            if self.estado == "busca":
                self.tempo = min(self.tempo, .15)

    def _abrir(self, duracao, eventos):
        for nome in ('ondas', 'penas'):
            getattr(self, nome, []).clear()
        self._mudar("aberto", duracao * self.ritmo.janela)
        self.onda = .7
        eventos.append("impacto")

    def _marca(self):
        if self.indice == 0:
            y = self.y-7 if self.asa_brecha_fagulha else self.chao-80
            return self.x-self.frente*27, y
        if self.indice == 1:
            return self.x, self.chao - 30
        if self.indice == 2:
            return self.x - 12, self.chao - (71 if self.progresso == 0 else 97)
        return self.x - 16, self.chao - 94

    def _acertou(self, corpo, golpe, clarao):
        mx, my = self._marca()
        ponto = pygame.Rect(round(mx)-18, round(my)-19, 36, 38)
        if self.indice == 3:
            return (clarao and corpo.bottom <= self.chao - 32
                    and hypot(corpo.centerx-mx, corpo.centery-my) < 130)
        altura = self.indice == 1 or corpo.bottom <= self.chao - 30
        return altura and golpe is not None and ponto.colliderect(golpe)

    def _fechar(self):
        self.fios.clear()
        self.segundo_fio = None
        self.agua = 0.
        self.sino_soou = False
        self.engatado = self.assentado = False
        self.barrel_x = self.inicio + 102
        self.asa_brecha_fagulha = False
        self.reacao_fagulha = ""
        self._mudar("busca", (.55 if self.indice in (2, 3) else 1.6) * self.ritmo.recuperacao)

    def _atualizar_aberto(self, corpo, golpe, clarao, eventos, permitir=True):
        if permitir and self._acertou(corpo, golpe, clarao):
            self.progresso += 1
            self.vida = max(0., self.vida - ceil(self.vida_max/self.meta))
            self.onda = 1.
            eventos.append("acerto")
            if self.vida <= 0:
                self._resolver(eventos)
                return
            self._fechar()
        elif self.tempo <= 0:
            self._fechar()

    def _colisao(self, corpo, area, eventos):
        if not self.atingiu and area.colliderect(corpo):
            self.atingiu = True
            eventos.append("dano_jogador")

    def _resolver(self,eventos):
        if self.despertar and not self.coro_iniciado:
            from .ultimo_chamado import iniciar
            iniciar(self,eventos)
            return
        self.vencido=True;self.estado='repouso'
        if self.ninhada is not None:
            self.ninhada.limpar()
        eventos.append('chefe_resolvido')

    def _aviso_investida(self, destino, y, duracao, impacta, eventos):
        self.destino = max(self.esq, min(self.dir, destino))
        self.alvo_y = y
        self.frente = 1 if self.destino > self.x else -1
        self.impacta, self.atingiu = impacta, False
        self._mudar("aviso", duracao)
        eventos.append("aviso")

    def _voar(self, dt, corpo, eventos, velocidade, fagulha=None):
        self.y = self.alvo_y
        self.x = aproximar(self.x, self.destino, velocidade*dt)
        # A faixa anunciada permanece na mesma altura até o fim do voo.
        faixa = pygame.FRect(self.x-32, self.y-12, 64, 19)
        self._colisao(corpo, faixa, eventos)
        if abs(self.x-self.destino) < .01:
            if self.asa_isca:
                isca = self.asa_isca
                self.asa_isca = None
                if fagulha is isca:
                    self.asa_brecha_fagulha = True
                    self._abrir(3.3, eventos)
                    eventos.append("brecha_fagulha")
                    return
            if self.impacta:
                self.y = self.chao - (57 if self.indice == 0 else 72)
                janela = 2.8
                if self.indice == 0:
                    janela = 2.1 if self.progresso else 3.8
                self._abrir(janela, eventos)
            else:
                self._mudar("busca", .95*self.ritmo.recuperacao)

    def _asa_altura_da_mira(self, corpo):
        apoio = next((a for a in self.apoios()
                      if a.left < corpo.right and corpo.left < a.right
                      and abs(corpo.bottom - a.top) <= 3), None)
        self.asa_mira_no_ar = apoio is None and corpo.bottom <= self.chao - 45
        # No chão e nos apoios, a segunda fase alterna ataques baixos e de peito.
        self.asa_rasteira = not self.asa_mira_no_ar and self.progresso > 0 and (
            corpo.height <= 24 or (not self.asa_rasteira and corpo.bottom >= self.chao - 20))
        if self.asa_mira_no_ar:
            return corpo.centery
        piso = apoio.top if apoio is not None else self.chao
        return piso - (10 if self.asa_rasteira else 31)

    def _asa(self, dt, corpo, eventos, fagulha):
        if self.estado == "busca":
            altura_vigia = self.chao - 93 + sin(self.relogio * 3) * 5
            self.y = aproximar(self.y, min(altura_vigia, corpo.centery), dt * 120)
            if self.tempo <= 0:
                marca = self.alvo_fagulha(fagulha)
                if marca and abs(self.x-marca[0]) >= 95:
                    self.asa_isca = self.ultima_fagulha = fagulha
                    self.asa_mira_no_ar = False
                    self.asa_rasteira = False
                    self._aviso_investida(marca[0],marca[1]-27,.92,False,eventos)
                    return
                esquerda = corpo.centerx <= self.esq+133
                direita = corpo.centerx >= self.dir-133
                impacta = esquerda or direita
                destino = self.esq if esquerda else self.dir if direita else corpo.centerx
                # Reposiciona a aproximação do lado oposto quando a vítima está atrás.
                if abs(self.x-destino) < 105:
                    self._mudar("contorna", .65)
                    self.destino = self.dir if destino < (self.esq+self.dir)/2 else self.esq
                else:
                    altura = self._asa_altura_da_mira(corpo)
                    self._aviso_investida(destino, altura, .78 if self.progresso else .95,
                                         impacta, eventos)
        elif self.estado == "contorna":
            self.x = aproximar(self.x, self.destino, 330*dt)
            self.frente = 1 if self.destino >= self.x else -1
            self.y = self.chao-135
            if self.tempo <= 0:
                self._mudar("busca", .35)
        elif self.estado == "aviso":
            self.y = aproximar(self.y, self.alvo_y, dt*170)
            if self.tempo <= 0:
                self._mudar("investida", 2.)
        elif self.estado == "investida":
            self._voar(dt, corpo, eventos, 552 if self.asa_rasteira else 498, fagulha)

    def _tecela(self, dt, corpo, eventos, fagulha):
        # A roda abre a água imediatamente. A aranha cai quando um fio tenso
        # encontra a cortina, o que também funciona para quem abriu antes do aviso.
        if self.agua > 0 and (self.estado == "aviso" or self.fios):
            self.fios.clear()
            self._mudar("desce", 1.0)
        if self.ninhada.atualizar(corpo, eventos):
            return
        if self.estado == "desce":
            self.x = aproximar(self.x, self.cortina, dt*260)
            self.y = aproximar(self.y, self.chao-31, dt*215)
            if self.tempo <= 0:
                self.y = self.chao-31
                janela = 2.85 if self.reacao_fagulha == "teia" or self.progresso else 4.8
                self._abrir(janela, eventos)
            return
        if self.estado == "busca":
            self.y = aproximar(self.y, self.chao-208, dt*172)
            self.x = aproximar(self.x, self.cortina+sin(self.relogio*.8)*65, dt*125)
            if (self.tempo <= 0 and not self.fios and not self.ninhada.atacando()
                    and not self.ninhada.ceder_turno(corpo)):
                self.destino = corpo.centerx
                self.alvo_y = corpo.centery
                self.frente = 1 if self.destino > self.x else -1
                if self.progresso:
                    # Depois do primeiro corte cobre também a saída que leva ao
                    # centro. Ambas as pontas ficam marcadas antes de disparar.
                    lado = 1 if corpo.centerx < (self.esq+self.dir)/2 else -1
                    lateral = max(self.esq, min(self.dir, corpo.centerx+lado*118))
                    self.segundo_fio = (lateral, min(self.chao-7,corpo.bottom-5))
                self._mudar("aviso", 1.02 if self.segundo_fio else .92)
                eventos.append("aviso")
        elif self.estado == "aviso" and self.tempo <= 0:
            alvos = [(self.destino,self.alvo_y)]
            if self.segundo_fio is not None:
                alvos.append(self.segundo_fio)
            for x, y in alvos:
                vx, vy = x-self.x, y-self.y
                n = max(1., hypot(vx, vy))
                self.fios.append(Fio(self.x, self.y, vx*265/n, vy*265/n))
            self.turno += 1
            self._mudar("busca", .98*self.ritmo.recuperacao)
            eventos.append("teia")
        vivos = []
        marca = self.alvo_fagulha(fagulha)
        for fio in self.fios:
            fio.x += fio.vx*dt
            fio.y += fio.vy*dt
            if marca and hypot(fio.x-marca[0],fio.y-marca[1]) <= 45:
                self.fios.clear()
                self.segundo_fio = None
                self.reacao_fagulha = "teia"
                self.ultima_fagulha = fagulha
                self._mudar("desce",.85)
                eventos.append("teia_queimada")
                return
            if pygame.FRect(fio.x-6,fio.y-6,12,12).colliderect(corpo):
                eventos.append("dano_jogador")
            elif self.esq-28 <= fio.x <= self.dir+28 and fio.y >= self.chao-4:
                # Um tiro desviado forma uma trama alta ou baixa no leito.
                # Cada faixa tem uma passagem livre e se desfaz após um contato.
                topo = self.chao - (57 if self.turno % 2 else 20)
                self.tramas.append(Trama(pygame.FRect(fio.x-28, topo, 56, 18)))
            elif self.inicio <= fio.x <= self.inicio+self.largura and self.chao-340 <= fio.y <= self.chao+3:
                vivos.append(fio)
        self.fios = vivos
        for trama in self.tramas:
            trama.tempo -= dt
            if not trama.tocada and trama.faixa.colliderect(corpo):
                trama.tocada = True
                eventos.append("dano_jogador")
        self.tramas = [t for t in self.tramas if t.tempo > 0 and not t.tocada]

    def _casco(self, dt, corpo, direcao, eventos, fagulha):
        from .casco import atualizar
        atualizar(self, dt, corpo, direcao, eventos, fagulha)

    def _coruja(self, dt, corpo, ruido, eventos, fagulha):
        from .coruja import atualizar
        atualizar(self, dt, corpo, ruido, eventos, fagulha)

    def update(self, dt, corpo, *, ruido=0., golpe=None, clarao=False, interagir=False, direcao=0, serie=None, bonus_dano=1., dano_corte=2., fagulha=None):
        """Recebe bordas de comando (golpe, clarão e E); retorna eventos desta atualização."""
        eventos = []
        self.relogio += dt
        self.onda = max(0., self.onda-dt)
        self.agua = max(0., self.agua-dt)
        if self.vencido:
            return eventos
        self.marca_acesa = self.marca_fagulha(fagulha)
        if self.estado.startswith('coro_'):
            from .ultimo_chamado import atualizar
            self.tempo-=dt
            atualizar(self,dt,corpo,clarao,interagir,eventos)
            return eventos
        # A arena aceita um acerto por arco, mesmo quando a fraqueza não está
        # exposta. Um crítico mantém o valor dos mecanismos de cada guardião.
        novo = serie != self.ultimo_corte if serie is not None else self.relogio-self.ultimo_golpe_t>.3
        # Clarão e espada têm identificadores independentes: K não renova um
        # arco que já acertou. Um corte comum também não vira um segundo crítico.
        fraco = (self.estado=="aberto" and self._acertou(corpo,golpe,clarao)
                 and (clarao if self.indice == 3 else novo))
        corpo_chefe=pygame.FRect(self.x-46,self.y-55,92,110)
        acertou = golpe is not None and corpo_chefe.colliderect(golpe)
        pulso_perto = clarao and hypot(corpo.centerx-self.x,corpo.centery-self.y)<214
        if (novo and acertou) or pulso_perto:
            if novo and acertou:
                self.contato_corte = corpo_chefe.clip(golpe).center
                self.ultimo_corte=serie
                self.ultimo_golpe_t=self.relogio
            if not fraco:
                base = (7.,3.,0.,4.)[self.indice] if pulso_perto else dano_corte*bonus_dano
                dano = base*self.ritmo.dano_comum
                self.vida=max(0.,self.vida-dano)
                eventos.append("acerto" if dano else "bloqueio")
                if self.vida<=0:
                    self._resolver(eventos)
                    return eventos
        # Casco e Coruja possuem tempos reais próprios, inclusive avisos.
        dt *= 1.35 if self.indice==0 else 1.2 if self.indice==1 else 1.
        self.tempo -= dt
        if interagir:
            self._usar(corpo, eventos)
        if self.estado == "aberto":
            if fraco and golpe is not None and self.indice != 3:
                self.contato_corte = self._marca()
                self.ultimo_corte = serie
                self.ultimo_golpe_t = self.relogio
            self._atualizar_aberto(corpo, golpe, clarao, eventos, permitir=fraco)
        elif self.indice == 0:
            self._asa(dt, corpo, eventos, fagulha)
        elif self.indice == 1:
            self._tecela(dt, corpo, eventos, fagulha)
        elif self.indice == 2:
            self._casco(dt, corpo, direcao, eventos, fagulha)
        else:
            self._coruja(dt, corpo, ruido, eventos, fagulha)
        return eventos

    def desenhar(self, tela, camera_x, camera_y=0):
        from .arte_arena import desenhar_encontro
        desenhar_encontro(tela, self, camera_x, camera_y)
