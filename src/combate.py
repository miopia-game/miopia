"""Combate de Lume e percepção, escolha de ataques e deslocamento dos habitantes."""
from dataclasses import dataclass,replace
import math
from random import Random
import pygame

Vetor = pygame.Vector2


@dataclass(frozen=True)
class Corte:
    espera: float
    ativo: float
    total: float
    alcance: int
    dano: int


CORTES = {
    "avanco": Corte(.04, .18, .42, 100, 3),
    "corte1": Corte(.026, .13, .24, 68, 1),
    "corte2": Corte(.04, .14, .29, 77, 1),
    "corte3": Corte(.075, .17, .42, 85, 2),
    "queda": Corte(.035, .24, .39, 54, 2),
    'pesado':Corte(.11,.18,.46,96,2),
    'quebra':Corte(.14,.20,.56,108,3),
    'retorno':Corte(.055,.16,.35,82,2),
    'aurora':Corte(.09,.21,.49,106,3),
}

# Perfil de alcance longo, com preparação e recuperação maiores.
AGULHA = {
    'avanco': Corte(.08, .17, .55, 132, 4),
    'corte1': Corte(.07, .13, .35, 102, 2),
    'corte2': Corte(.10, .14, .42, 112, 2),
    'corte3': Corte(.15, .16, .58, 123, 3),
    'queda': Corte(.09, .24, .50, 75, 3),
}
ARMAS = {'espinho': CORTES, 'agulha': AGULHA}
AGULHA.update({n:replace(CORTES[n],alcance=CORTES[n].alcance+25,total=CORTES[n].total+.08) for n in ('pesado','quebra','retorno','aurora')})
LUZ_ARMAS={nome:{n:replace(p,dano=p.dano*2,alcance=p.alcance+16) for n,p in perfis.items()} for nome,perfis in ARMAS.items()}


class Arma:
    """Um toque solicita um golpe. Cada alvo pode ser atingido uma vez por arco."""
    def __init__(self, equipamento='espinho'):
        self.tipo = ""
        self.face = 1
        self.tempo = 0.
        self.serie = 0
        self.combo = 0
        self.intervalo = 0.
        self.pedido = 0.
        self.pedir_queda = False
        self.pedir_avanco = False
        self.rebote = 0.
        self.equipamento = equipamento
        self.historico=[];self.luminoso=False
        self.pedir_forte=self.pedir_luminoso=False

    @property
    def perfil(self):
        return (LUZ_ARMAS if self.luminoso else ARMAS)[self.equipamento][self.tipo] if self.tipo else None

    def cancelar(self):
        self.tipo = ''
        self.pedido = self.intervalo = 0.
        self.combo = 0
        self.historico=[];self.luminoso=False

    def trocar(self):
        if self.tipo or self.pedido > 0:
            return False
        self.equipamento = 'agulha' if self.equipamento == 'espinho' else 'espinho'
        self.combo = 0
        self.intervalo = 0.
        return True

    def pedir(self, queda, avanco=False,forte=False,luminoso=False):
        self.pedido = .22
        self.pedir_queda = queda
        self.pedir_avanco = avanco
        self.pedir_forte=forte;self.pedir_luminoso=luminoso

    def clarao(self):
        self.historico=(self.historico+['K'])[-3:];self.intervalo=max(self.intervalo,.9)

    def avancar(self, dt, lume):
        self.rebote = max(0., self.rebote - dt)
        self.intervalo = max(0., self.intervalo - dt)
        if self.tipo:
            self.tempo += dt
            # A fila tem um slot; o próximo toque aguarda o fim do movimento.
            # Dano pode interromper o golpe, mas J não elimina a recuperação.
            if self.tempo >= self.perfil.total:
                self.tipo = ""
        inicio = False
        if self.pedido > 0 and not self.tipo and lume.impacto <= 0 and not lume.em_corda:
            baixo = self.pedir_queda and not lume.chao
            self.combo = 0 if baixo else (self.combo % 3 + 1 if self.intervalo > 0 else 1)
            self.tipo = "queda" if baixo else "corte" + str(self.combo)
            self.historico=(self.historico if self.intervalo>0 else [])+['L' if self.pedir_forte else 'J']
            self.historico=self.historico[-3:]
            seq=''.join(self.historico)
            if not baixo:
                if self.pedir_forte:self.tipo='aurora' if seq.endswith('KL') else 'quebra' if seq.endswith('JL') else 'pesado'
                elif seq.endswith(('LJ','KJ')):self.tipo='retorno'
            if self.pedir_avanco and lume.chao:
                self.tipo="avanco"
            self.luminoso=self.pedir_luminoso
            custo=(14 if self.pedir_forte else 12 if self.tipo=='avanco' else 8) if self.luminoso else 0
            custo*=getattr(lume,'fator_custo_luz',1.)
            if not lume.gastar_brilho(custo):
                self.pedido = 0.
                self.tipo = ''
                lume.golpe = 0.
                return False
            self.tempo = 0.
            self.face = lume.face
            self.serie += 1
            self.intervalo = self.perfil.total + .43
            self.pedido = 0.
            if baixo:
                lume.vy = max(lume.vy, 205)
            inicio = True
        self.pedido = max(0., self.pedido - dt)
        lume.golpe = max(0., self.perfil.total - self.tempo) if self.tipo else 0.
        return inicio

    def area(self, lume):
        if not self.tipo:
            return None
        perfil = self.perfil
        if not perfil.espera <= self.tempo <= perfil.espera + perfil.ativo:
            return None
        if self.tipo == "queda":
            return pygame.FRect(lume.rect.centerx - 28, lume.rect.bottom - 7, 56, perfil.alcance)
        return self.area_corte(lume, perfil, self.face)

    def area_corte_rapido(self, lume):
        return self.area_corte(lume, ARMAS[self.equipamento]["corte1"], lume.face)

    @staticmethod
    def area_corte(lume, perfil, face):
        r = pygame.FRect(0, 0, perfil.alcance, lume.rect.h + 36)
        r.centery = lume.rect.centery
        if face == 1:
            r.left = lume.rect.centerx - 5
        else:
            r.right = lume.rect.centerx + 5
        return r


@dataclass(frozen=True)
class Especie:
    vida: int
    tamanho: tuple[int, int]
    percepcao: int
    aviso: float
    vigor: float
    som: str


ESPECIES = {
    "morcego": Especie(5, (41, 27), 250, .53, 420, "asa_perto"),
    "aranha": Especie(6, (49, 27), 255, .60, 276, "patas_perto"),
    "sombra": Especie(4, (37, 35), 210, .72, 305, "sopro_perto"),
    "vespa": Especie(3, (41, 28), 287, .53, 370, "zurro_perto"),
    "carabideo": Especie(5, (58, 37), 251, .68, 370, "casco_perto"),
    "cobra": Especie(6, (56,27),260,.58,340,"silvo_perto"),
}
AEREOS = ("morcego", "vespa")
ALTURA_SALTO = 49
ALTURA_SALTO_ALTO = 112


def segmento_bloqueado(inicio, fim, terrenos):
    return any(not t.atravessavel and t.rect.clipline(inicio, fim) for t in terrenos)


def direcao(inicio, fim):
    delta = Vetor(fim) - inicio
    return delta.normalize() if delta.length_squared() > .01 else Vetor(1, 0)


def ponto_salto(inicio, x_final, fase, altura):
    ponto = inicio.lerp((x_final, inicio.y), fase)
    ponto.y -= math.sin(fase * math.pi) * altura
    return ponto


@dataclass
class Projetil:
    tipo: str
    pos: Vetor
    vel: Vetor
    vida: float

    def avancar(self, dt, lume, terrenos, corte, clarao):
        origem = self.pos.copy()
        self.pos += self.vel * dt
        self.vida -= dt
        if self.vida <= 0:
            return "fim"
        # Fio e ferrão podem ser interceptados. A onda deve ser saltada.
        if clarao and self.pos.distance_to(lume.rect.center) < 214:
            return "corte"
        if self.tipo in ("fio", "ferrao", "veneno") and corte and corte.inflate(9, 9).clipline(origem, self.pos):
            return "corte"
        if segmento_bloqueado(origem, self.pos, terrenos):
            return "fim"
        if self.tipo == "onda":
            apoio = (self.pos.x, self.pos.y + 11)
            if not any(t.rect.collidepoint(apoio) for t in terrenos):
                return "fim"
        if lume.rect.inflate(7, 7).clipline(origem, self.pos):
            return "dano"
        return ""


class Inimigo:
    def __init__(self, tipo, x, y, dificuldade="normal", *, semente=None):
        self.tipo, self.origem = tipo, (x, y)
        self.ficha = ESPECIES[tipo]
        self.dificuldade = dificuldade
        forte = dificuldade in ("difícil", "dificil")
        facil = dificuldade in ("fácil", "facil", "sereno")
        self.max_vida = self.ficha.vida + int(forte) - int(facil)
        self.vida = self.max_vida
        self.ritmo = 1.13 if forte else (.86 if facil else 1.)
        self.ativo = True
        self.guarda = False
        self.rect = pygame.FRect(0, 0, *self.ficha.tamanho)
        self.ultimo_corte = -1
        # A posição identifica indivíduos da campanha. O ensaio fornece sua
        # semente explicitamente; desenho e som nunca consomem este gerador.
        self.semente = f"aranha/{x}/{y}/{dificuldade}/{semente}"
        self.repor()

    def repor(self):
        self.vida=self.max_vida
        self.rect.midbottom = self.origem
        self.estado = "patrulha"
        self.tecnica = ""
        self.t = .14
        self.relogio = 0.
        self.chamada = .25
        self.sequencia = 0
        self.frente = 1
        self.alvo = Vetor(self.rect.center)
        self.inicio = Vetor(self.rect.center)
        self.vetor = Vetor()
        self.duracao = 0.
        self.tranco = 0
        self.flash = 0.
        self.projeteis = []
        self.ultimo_corte = -1
        self.sorte = Random(self.semente)
        self.ultima_tecnica = ""
        self.repeticoes = 0
        self.pesos_decisao = {}
        self.destino_recuo = Vetor(self.rect.center)
        self.resistencia_leve = 0.
        self.lentidao = 0.
        self.cego=0.
        self.recuo_ferida = False

    def mover(self, dx, dy, terrenos):
        """O raio da busca é local; paredes e bordas limitam a perseguição terrestre."""
        novo = self.rect.copy()
        novo.x += dx
        if not any(not t.atravessavel and pygame.FRect(t.rect).colliderect(novo) for t in terrenos):
            if self.tipo in AEREOS or (self.tecnica in ("salto", "salto_alto") and self.estado == "investida") or not terrenos:
                self.rect.x = novo.x
            else:
                frente = novo.right - 1 if dx > 0 else novo.left + 1
                if any(t.rect.collidepoint(frente, self.origem[1] + 2) for t in terrenos):
                    self.rect.x = novo.x
        novo = self.rect.move(0, dy)
        if not any(not t.atravessavel and pygame.FRect(t.rect).colliderect(novo) for t in terrenos):
            self.rect.y = novo.y

    def seguir(self, destino, velocidade, dt, terrenos):
        atual = Vetor(self.rect.center)
        delta = Vetor(destino) - atual
        passo = delta.clamp_magnitude(velocidade * dt)
        self.mover(passo.x, passo.y, terrenos)

    def alcance(self, lume, raio, restaurado):
        if self.tipo == "morcego":
            return min(297, max(155, raio + 80))
        if self.tipo == "sombra":
            return 112 if restaurado else 186 + (100 - lume.energia)*.62
        if self.tipo == "aranha" and abs(lume.vx) < 40:
            return self.ficha.percepcao * .68
        return self.ficha.percepcao

    def alvo_observado(self, lume):
        previsao = max(-40., min(40., lume.vx*.16))
        return Vetor(lume.rect.centerx + previsao, lume.rect.centery)

    def carabideo_com_alvo_acima(self, lume):
        return self.tipo == "carabideo" and lume.rect.bottom <= self.rect.top

    def salto_alto_viavel(self, lume, terrenos):
        alvo = self.alvo_observado(lume)
        # A aproximação é curta para alcançar Lume perto do ápice do arco.
        return (abs(alvo.x - self.rect.centerx) <= 72
                and self.rect.centery - alvo.y <= 145
                and self.salto_livre(alvo, terrenos, ALTURA_SALTO_ALTO))

    def salto_livre(self, alvo, terrenos, altura=ALTURA_SALTO):
        """Confere o mesmo arco usado pelo ataque, com espaço para o corpo.

        Segmentos curtos varrem o volume entre amostras, incluindo paredes
        finas e tetos. O apoio final precisa caber sob ambos os lados do corpo.
        """
        if not terrenos:
            return True
        inicio = Vetor(self.rect.center)
        base = self.rect.bottom
        if not all(any(t.rect.collidepoint(x, base+2) for t in terrenos)
                   for x in (alvo.x-self.rect.w*.35, alvo.x+self.rect.w*.35)):
            return False
        anterior = inicio
        for n in range(1, 33):
            ponto = ponto_salto(inicio, alvo.x, n / 32, altura)
            for t in terrenos:
                if t.atravessavel:
                    continue
                volume = pygame.FRect(t.rect).inflate(self.rect.w-.1, self.rect.h-.1)
                if volume.clipline(anterior, ponto):
                    return False
            anterior = ponto
        return True

    def pesos_aranha(self, dx, lume, terrenos=()):
        """Afinidades do atlas, normalizadas somente entre ataques possíveis.

        A memória reduz uma repetição a 45% do peso, ou 20% após duas.
        Com uma única opção a memória não interfere. Zero nunca é sorteado.
        """
        distancia = abs(dx)
        alvo = self.alvo_observado(lume)
        visivel = not segmento_bloqueado(self.rect.center, lume.rect.center, terrenos)
        fio = (65 <= distancia <= 260 and visivel
               and not segmento_bloqueado(self.rect.center, alvo, terrenos))
        salto = (distancia <= 150 and abs(lume.rect.centery-self.rect.centery) <= 65
                 and visivel and self.salto_livre(alvo, terrenos))
        pesos = {
            "fio": max(0., 1-abs(distancia-150)/160) if fio else 0.,
            "salto": .95*max(0., 1-abs(distancia-65)/95) if salto else 0.,
        }
        if sum(p > 0 for p in pesos.values()) > 1 and self.ultima_tecnica in pesos:
            pesos[self.ultima_tecnica] *= .20 if self.repeticoes >= 2 else .45
        return pesos

    def escolher(self, dx, lume, terrenos=()):
        if self.tipo == "morcego":
            return "rasante" if self.sequencia % 2 else "mergulho"
        if self.tipo == "aranha":
            self.pesos_decisao = self.pesos_aranha(dx, lume, terrenos)
            total = sum(self.pesos_decisao.values())
            if total <= 0:
                return ""
            sorteio = self.sorte.random()*total
            acumulado = 0.
            for tecnica, peso in self.pesos_decisao.items():
                acumulado += peso
                if peso > 0 and sorteio < acumulado:
                    return tecnica
            return ""  # Total finito positivo sempre encontra um intervalo.
        if self.tipo == "vespa":
            return "mergulho" if abs(dx) < 78 else "ferrao"
        if self.tipo == "sombra":
            return "fenda" if abs(dx) > 84 or self.sequencia % 2 == 0 else "rasteira"
        if self.carabideo_com_alvo_acima(lume):
            return "salto_alto" if self.salto_alto_viavel(lume, terrenos) else ""
        return "onda" if abs(dx) < 97 or lume.rect.bottom < self.rect.top else "carga"

    def preparar(self, lume, terrenos=()):
        if self.cego>0:self.t=.12;return ''
        self.tecnica = self.escolher(lume.rect.centerx - self.rect.centerx, lume, terrenos)
        if not self.tecnica:
            self.t = .20  # Sem ataque viável, reavaliar depois de reposicionar.
            return ""
        if self.tipo == "aranha":
            self.repeticoes = self.repeticoes+1 if self.tecnica == self.ultima_tecnica else 1
            self.ultima_tecnica = self.tecnica
        self.sequencia += 1
        self.frente = 1 if lume.rect.centerx >= self.rect.centerx else -1
        self.alvo = self.alvo_observado(lume)
        self.inicio = Vetor(self.rect.center)
        if self.tipo == "aranha":
            self.destino_recuo = Vetor(max(self.origem[0]-130,
                min(self.origem[0]+130, self.rect.centerx-self.frente*42)), self.rect.centery)
        if self.tecnica == "rasante":
            self.alvo.y = lume.rect.bottom - 42
        if self.tecnica == "fenda":
            self.alvo.y = self.origem[1]
        self.estado, self.t = "aviso", self.ficha.aviso / self.ritmo
        return {"fio":"fio_disparo", "ferrao":"ferrao", "fenda":"pressagio",
                "carga":"casco_avanco", "onda":"casco_avanco",
                "salto_alto":"aviso_carabideo_4"}.get(self.tecnica, "rasgo")

    def disparar(self, tipo, origem, vetor, vida):
        self.projeteis.append(Projetil(tipo, Vetor(origem), Vetor(vetor), vida))

    def lancar(self):
        self.estado = "investida"
        self.inicio = Vetor(self.rect.center)
        self.vetor = direcao(self.inicio, self.alvo) * self.ficha.vigor * self.ritmo
        self.duracao = .43
        if self.tecnica in ("fio", "ferrao"):
            self.duracao = .18
            vel = direcao(self.inicio, self.alvo)*(235 if self.tecnica == "fio" else 304)*self.ritmo
            self.disparar(self.tecnica, self.inicio, vel, 1.45)
            if self.tecnica == "ferrao" and self.sequencia % 2 == 0:
                self.disparar("ferrao", self.inicio, vel.rotate(13*self.frente), 1.35)
        elif self.tecnica == "onda":
            self.duracao = .24
            self.disparar("onda", (self.rect.centerx + 18*self.frente, self.rect.bottom - 9),
                          (242*self.frente*self.ritmo, 0), 1.25)
        elif self.tecnica in ("carga", "rasteira", "rasante"):
            self.vetor.update(self.frente*self.ficha.vigor*self.ritmo, 0)
            self.duracao = .55
        elif self.tecnica in ("salto", "salto_alto"):
            self.duracao = .55
        elif self.tecnica == "fenda":
            self.duracao = .24
        self.t = self.duracao

    def executar_ataque(self, dt, lume, terrenos):
        contato = False
        if self.tecnica == "fenda":
            marca = pygame.FRect(self.alvo.x-28, self.alvo.y-39, 56, 39)
            contato = marca.colliderect(lume.rect)
        elif self.tecnica in ("salto", "salto_alto"):
            fase = min(1., max(0., 1-self.t/self.duracao))
            altura = ALTURA_SALTO_ALTO if self.tecnica == "salto_alto" else ALTURA_SALTO
            destino = ponto_salto(self.inicio, self.alvo.x, fase, altura)
            self.mover(destino.x-self.rect.centerx, destino.y-self.rect.centery, terrenos)
            contato = self.rect.colliderect(lume.rect)
        elif self.tecnica in ("mergulho", "rasante", "carga", "rasteira"):
            # O destino é fixado no aviso: a esquiva não é anulada por correção instantânea.
            self.mover(self.vetor.x*dt, self.vetor.y*dt, terrenos)
            contato = self.rect.colliderect(lume.rect)
        if self.t <= 0 or contato:
            self.estado, self.t = "recuo", .65 / self.ritmo
        return contato

    def patrulhar(self, lume, distancia, dt, terrenos):
        x, y = self.origem
        destino = Vetor(x + 51*math.sin(self.relogio*1.4), y-self.rect.h/2)
        if self.tipo in AEREOS:
            destino.y += 18*math.sin(self.relogio*2.1)
        if self.tipo == "vespa" and distancia < 290:
            # Mantém distância para mirar, mas não abandona sua clareira.
            destino.x = x + max(-95, min(95, lume.rect.centerx-x-self.frente*145))
        elif self.tipo == "sombra" and distancia < 240:
            # A sombra cerca a trilha sem se teletransportar para cima do jogador.
            destino.x = x + max(-102, min(102, lume.rect.centerx-x+self.frente*45))
        elif (self.tipo == "aranha" and distancia < self.ficha.percepcao
              and not segmento_bloqueado(self.rect.center, lume.rect.center, terrenos)):
            # Fecha espaço para manter as duas técnicas úteis. Não persegue
            # posição escondida e a verificação de apoio impede cair de bordas.
            face = 1 if lume.rect.centerx >= self.rect.centerx else -1
            destino.x = x + max(-130, min(130, lume.rect.centerx-x-face*102))
        self.seguir(destino, 94 if self.tipo in AEREOS else 62, dt, terrenos)

    def update(self, dt, lume, raio, restaurado, terrenos):
        """Entrega os avisos com posição no mundo e o eventual impacto no jogador."""
        self.cego=max(0.,self.cego-dt)
        sons = []
        dano = False
        lenta=self.lentidao>0
        self.lentidao=max(0.,self.lentidao-dt)
        if lenta:dt*=.60
        self.relogio += dt
        self.t -= dt
        self.flash = max(0., self.flash - dt)
        self.resistencia_leve = max(0., self.resistencia_leve-dt)
        self.chamada -= dt
        distancia = Vetor(self.rect.center).distance_to(lume.rect.center)
        if distancia <= 330 and self.chamada <= 0:
            sons.append((self.ficha.som, self.rect.centerx))
            self.chamada = 2.6 + .004*distancia
        if self.estado == "patrulha":
            self.patrulhar(lume, distancia, dt, terrenos)
            if (self.t <= 0 and distancia < self.alcance(lume, raio, restaurado)
                    and not segmento_bloqueado(self.rect.center, lume.rect.center, terrenos)):
                aviso = self.preparar(lume, terrenos)
                if aviso:
                    sons.append((aviso, self.rect.centerx))
        elif self.estado == "aviso":
            if self.tecnica == "rasante":
                # O segundo ataque nivela as asas numa faixa alta. Agachado, Lume
                # passa por baixo; de pé ele intercepta a mesma faixa.
                dy = max(-270*dt, min(270*dt, self.alvo.y-self.rect.centery))
                self.mover(0, dy, terrenos)
            if self.t <= 0:
                self.lancar()
        elif self.estado == "investida":
            dano = self.executar_ataque(dt, lume, terrenos)
        elif self.estado == "recuo":
            destino = self.destino_recuo if self.tipo == "aranha" else (self.origem[0], self.origem[1]-self.rect.h/2)
            self.seguir(destino, 460 if self.recuo_ferida else 186, dt, terrenos)
            if self.t <= 0:
                self.estado, self.t = "patrulha", 0. if self.recuo_ferida else .24
                self.recuo_ferida = False
        elif self.estado == "atordoado":
            self.mover(self.tranco * dt, 0, terrenos)
            self.tranco *= max(0., 1-9*dt)
            if self.t <= 0:
                self.estado, self.t = "recuo", .38 if self.recuo_ferida else .28
        return sons, dano

    def dano_corte(self, arma, lume):
        fator = 2.5 if self.tipo == "carabideo" and getattr(lume, "tanino", False) else 1.
        return arma.perfil.dano * getattr(lume, "bonus_dano", 1.) * fator

    def acertar(self, arma, area, clarao, lume):
        pulso = clarao and Vetor(self.rect.center).distance_to(lume.rect.center) < 214
        corte = arma.perfil is not None and area is not None and area.colliderect(self.rect) and self.ultimo_corte != arma.serie
        if not (pulso or corte):
            return ""
        if corte:
            self.ultimo_corte = arma.serie
        de_frente = (lume.rect.centerx-self.rect.centerx)*self.frente > 0
        blindado = (self.tipo == "carabideo" and self.estado in ("patrulha", "aviso", "investida")
                    and de_frente and arma.tipo in ("corte1", "corte2") and not pulso and not getattr(lume,"tanino",False))
        self.flash = .20
        if blindado:
            return "bloqueio"
        if pulso and self.tipo=="carabideo":
            return "bloqueio"
        dano_luz={"morcego":3,"sombra":3,"aranha":2,"vespa":1,"cobra":1}
        self.vida -= dano_luz[self.tipo] if pulso else self.dano_corte(arma, lume)
        self.ativo = self.vida > 0
        if not self.ativo:
            self.projeteis.clear()
            return "abatido"
        if self.tipo == "aranha" and not pulso and arma.tipo in ("corte1", "corte2"):
            # O aviso comprometido continua legível mesmo sob golpes leves.
            # Fora dele, um flinch abre uma janela curta sem poder ser renovado
            # a cada tecla. Terceiro corte, queda e clarão sempre interrompem.
            if self.estado in ("aviso", "investida") or self.resistencia_leve > 0:
                return "acerto"
        if self.tipo == "aranha":
            self.resistencia_leve = .95
            self.recuo_ferida = True
            lado = 1 if self.rect.centerx >= lume.rect.centerx else -1
            self.destino_recuo = Vetor(max(self.origem[0]-260, min(self.origem[0]+260,
                self.rect.centerx+lado*200)), self.origem[1]-self.rect.h/2)
        self.estado, self.t = "atordoado", .79 if pulso else .19
        self.tranco = (98 if arma.tipo == "corte3" else 61) * (1 if self.rect.centerx >= lume.rect.centerx else -1)
        return "acerto"
