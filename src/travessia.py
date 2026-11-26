"""Simulação do caminho de Lume. Coordenadas e colisões ficam no espaço do mundo."""
from __future__ import annotations

from dataclasses import dataclass
import math
import pygame
from .passagem_lume import Passagem
from .visao import DURACAO, Vestigio
from .combate import Arma, Inimigo
from .taticas import Habitante
from .travessia_fagulha import CORTE_PRATICADO, ORIGEM_MORCEGO, ImpactoDoCorte, MorcegoDoGalho, avisar_pouso, lancar, reagir
from .fases import VIGIA_X, TRANCA_X
from .fases import (ARENA, CHAO, FIM_ARENA, FALAS, FASES, MEIO, RAIZ, SAIDA,
                    RAMAIS, Objeto, Terreno, terrenos)


from . import narrativa, corte_vertical, subsolo, raizes_bosque, recursos, resgates, vento_taquaral
from . import aula_sino, corrego_historia, desvios_fagulha, galeria_taquaral, licao_vespera, nicho_taquaral, rotas_borda


@dataclass(frozen=True)
class Comando:
    mover: int = 0
    baixo: bool = False
    salto: bool = False
    segurar_salto: bool = False
    deslize: bool = False
    golpe: bool = False
    clarao: bool = False
    interagir: bool = False
    forte: bool = False
    carregado: bool = False
    fagulha: bool = False


def aproximar(valor, alvo, passo):
    return valor + max(-passo, min(alvo - valor, passo))


class Lume:
    ALTURA = 42
    BAIXO = 20
    # Compatibilidade com ferramentas que inspecionam esta reserva. A asa agora
    # sustenta a queda enquanto Espaço estiver pressionado, sem cronômetro.
    PLANEIO = 1.

    def __init__(self, x, y, vidas=3):
        self.rect = pygame.FRect(0, 0, 24, self.ALTURA)
        self.rect.midbottom = x, y
        self.vx = self.vy = 0.
        self.face = 1
        self.chao = True
        self.coyote = self.buffer = self.slide = self.slide_cd = 0.
        self.golpe = self.golpe_cd = self.pulso = self.pulso_cd = 0.
        self.iframes = self.impacto = self.planeio = 0.
        self.energia = 100.
        self.vida = 100.
        self.custo_clarao = 22.
        self.abate_ate=0.;self.ganho_abate=(0.,0.)
        self.combo_acertos=0
        self.vidas = vidas
        self.em_corda = False
        self.corda_destino = None
        self.bateu = False
        self.na_parede = self.planando = self.impulso_parede = False
        self.ultimo_impulso = self.lado_parede = 0
        self.trava_lateral = self.graca_parede = 0.
        self.ignorar_topo = None
        self.planeio = self.PLANEIO
        self.asa_disponivel = False
        self.batida_asa = 0.
        self.arma = Arma()
        self.bonus_dano = self.bonus_velocidade = 1.

    @property
    def pose(self):
        if self.impacto > 0: return "dano"
        if self.em_corda: return "corda"
        if self.pulso > 0: return "clarao"
        if self.golpe > 0: return "golpe"
        if self.slide > 0: return "deslize"
        if self.rect.height < self.ALTURA: return "agachar"
        if self.planando: return "planar"
        if not self.chao and self.na_parede and self.vy>=0: return "parede"
        if not self.chao: return "pulo" if self.vy < 0 else "queda"
        if abs(self.vx) > 196: return "correr"
        return "andar" if abs(self.vx) > 10 else "parado"

    def altura(self, baixo, solidos):
        altura = self.BAIXO if baixo else self.ALTURA
        if self.rect.height == altura:
            return
        novo = self.rect.copy()
        novo.height = altura
        novo.bottom = self.rect.bottom
        if baixo or not any(not t.atravessavel and novo.colliderect(t.rect) for t in solidos):
            self.rect = novo

    def movimento(self, dt, cmd, solidos, corrente, asas, *, vento=None):
        planava = self.planando
        self.bateu = self.planando = self.impulso_parede = False
        saltou = False
        for timer in ("buffer", "slide", "slide_cd", "golpe", "golpe_cd", "pulso",
                      "pulso_cd", "iframes", "impacto", "trava_lateral", "graca_parede", "batida_asa"):
            setattr(self, timer, max(0., getattr(self, timer) - dt))
        if self.chao:
            self.asa_disponivel = True
        self.coyote = .105 if self.chao else max(0., self.coyote - dt)
        self.altura(cmd.baixo or self.slide > 0, solidos)
        r = self.rect

        # O pé identifica a peça que de fato sustenta a personagem. Solos e
        # pontes continuam bloqueando para baixo mesmo encostados numa grade.
        apoio = [t for t in solidos if r.right > t.rect.left and r.left < t.rect.right
                 and abs(r.bottom - t.rect.top) < 1.2]
        desceu = (cmd.baixo and cmd.salto and self.chao and apoio
                  and all(t.descida for t in apoio))
        if desceu:
            self.ignorar_topo = r.bottom
            self.buffer = self.coyote = self.slide = 0.
            self.chao = False
            self.vy = max(125., self.vy)
            r.y += 2
        elif cmd.salto and not cmd.baixo:
            self.buffer = .125

        contato = 0
        if not self.chao:
            for t in solidos:
                if t.tipo != "parede" or r.bottom <= t.rect.top + 3 or r.top >= t.rect.bottom - 1:
                    continue
                if abs(r.right - t.rect.left) <= 2.5:
                    contato = 1
                elif abs(r.left - t.rect.right) <= 2.5:
                    contato = -1
                if contato:
                    self.lado_parede = contato
                    self.graca_parede = .11
                    break
        self.na_parede = bool(contato)
        if cmd.mover and self.trava_lateral <= 0 and self.slide <= 0:
            self.face = 1 if cmd.mover > 0 else -1
        if cmd.deslize and self.chao and self.slide_cd <= 0:
            self.slide, self.slide_cd = .62, 1.04
            self.altura(True, solidos)
            r = self.rect
        asas_abertas = asas and cmd.segurar_salto and not cmd.baixo
        if self.buffer > 0 and self.slide <= 0 and r.h == self.ALTURA:
            if self.coyote > 0:
                self.vy = -502.
                self.buffer = self.coyote = 0.
                self.chao = False
                saltou = True
            elif self.graca_parede > 0 and self.lado_parede != self.ultimo_impulso:
                # A distância entre os troncos permite alternar paredes. Uma
                # mesma face só volta a dar impulso depois de outro apoio.
                self.ultimo_impulso = self.lado_parede
                self.face = -self.lado_parede
                self.vx, self.vy = self.face * 345., -523.
                self.trava_lateral = .15
                self.buffer = self.graca_parede = 0.
                self.impulso_parede = True
                saltou = True
            elif asas_abertas and vento_taquaral.permite_retomar(vento, r.bottom, self.vy):
                self.buffer = 0.
                self.vy = min(self.vy, 200.)
            elif asas and self.asa_disponivel:
                self.vy = -440.
                self.asa_disponivel = False
                self.batida_asa = .18
                self.buffer = 0.
                saltou = True
        if not cmd.segurar_salto and self.vy < -233 and self.arma.rebote <= 0:
            self.vy = -233.
        if self.slide > 0:
            self.vx = self.face * 530.
        elif self.trava_lateral <= 0:
            limite = (94 if r.h < self.ALTURA else 247) * self.bonus_velocidade
            self.vx = aproximar(self.vx, cmd.mover * limite, (1750 if self.chao else 950) * dt)
        subida = vento.subida if vento else 0
        if planava and self.vy < 0 and not asas_abertas and not saltou:
            # Fechar as asas cancela o impulso do ar sem afetar um novo salto.
            self.vy = 0.
        self.planando = bool(asas_abertas and not (contato and cmd.mover == contato)
                             and (self.vy > 48 or (subida and planava and not saltou)))
        deriva = vento.deslocamento if vento and self.planando else 0
        old = r.copy()
        dx = (self.vx + corrente + deriva) * dt
        r.x += dx
        for t in solidos:
            if not t.atravessavel and r.colliderect(t.rect):
                if t.tipo != "parede":
                    self.bateu = self.bateu or abs(self.vx) > 185
                if dx > 0: r.right = t.rect.left
                elif dx < 0: r.left = t.rect.right
                self.vx = self.slide = 0.

        if self.planando:
            self.vy = aproximar(self.vy, subida or 76., dt * 840)
        elif contato and cmd.mover == contato and self.vy > 0:
            self.vy = min(self.vy + 240 * dt, 78.)
        else:
            self.vy = min(self.vy + 1190 * dt, 710.)
        self.chao = False
        r.y += self.vy * dt
        for t in solidos:
            if not r.colliderect(t.rect):
                continue
            if self.ignorar_topo is not None and t.descida and abs(t.rect.top-self.ignorar_topo)<1.2:
                continue
            if self.vy >= 0 and old.bottom <= t.rect.top + .5:
                r.bottom = t.rect.top
                self.vy = 0.
                self.chao = True
                self.planando = False
                self.planeio = self.PLANEIO
                self.asa_disponivel = True
                self.batida_asa = 0.
                self.ultimo_impulso = self.lado_parede = 0
                self.graca_parede = 0.
            elif self.vy < 0 and not t.atravessavel and old.top >= t.rect.bottom - .5:
                r.top = t.rect.bottom
                self.vy = 0.
        if self.ignorar_topo is not None and (r.top > self.ignorar_topo or r.bottom < self.ignorar_topo):
            self.ignorar_topo = None
        return saltou

    def custo_em_vida(self, custo):
        return max(0., custo-self.energia)

    def gastar_brilho(self,custo):
        if self.vida<=0:return False
        vida = self.custo_em_vida(custo)
        brilho=min(self.energia,custo)
        self.energia=max(0.,self.energia-brilho)
        self.vida=max(0.,self.vida-vida)
        return True

    def atacar(self, cmd):
        if cmd.golpe or cmd.forte:
            self.arma.pedir(cmd.baixo and not self.chao, cmd.deslize and bool(cmd.mover),cmd.forte,cmd.carregado)
        if cmd.clarao and self.pulso_cd <= 0 and self.gastar_brilho(self.custo_clarao):
            self.pulso, self.pulso_cd = .55, 2.50
            self.arma.clarao()
            return True
        return False


NIVEIS = {
    "facil": (.32, 12, 4), "fácil": (.32, 12, 4), "sereno": (.32, 12, 4),
    "normal": (.5, 19, 3), "dificil": (.74, 25, 2), "difícil": (.74, 25, 2),
}
DIFICULDADES = ("fácil", "normal", "difícil")
MAX_FAGULHAS = max(perfil[2] for perfil in NIVEIS.values())

# O pino da roda fica nesta posição quando a alteração no mundo já foi feita.
MANIVELAS = {
    aula_sino.PASSARELA: (aula_sino.PASSARELA, "Examinar a passarela baixada"),
    "dreno": ("dreno", "Examinar o canal drenado"),
    "ponte": ("ponte", "Examinar a ponte estendida"),
    "ralo": ("ralo", "Examinar a comporta aberta"),
    "roldana": ("roldana", "Examinar a roldana destravada"),
    "selo_copa": ("atalho_copa", "Examinar a janela aberta"),
    "ralo_cisterna": ("ralo_aberto", "Examinar o ralo aberto"),
    "comporta_viveiro": ("viveiro_aberto", "Examinar a comporta aberta"),
}


class Jornada:
    def __init__(self, modo="historia", dificuldade="normal", etapa=0):
        if modo.lower()!='historia':raise ValueError('Somente o modo História está disponível.')
        self.modo = 'historia'
        self.configurar_dificuldade(dificuldade.lower())
        self.dificuldade_pendente = None
        self.vestigios = []
        self.em_vertical = False
        self.camera_y = 0.
        self.cartografia = set()
        self.explorado = set()
        self.pisadas_escuta = set()
        self.marcas = []
        self.globos=[];self.tochas=set();self.nucleos=set();self.tutorial=set()
        self.missao = "principal"
        self.marco_vertical = "bosque"
        self.destino_vertical = None
        self.motivo_morte = ""
        self.sobreviventes = {}
        self.concluida = False
        self.escolha_resgate = None
        self.tempo = 0.
        self.pontuacao = 0
        self.restauradas = 0
        self.volta = 0
        self.historico = {}
        self.diario = []
        self.bolsa = narrativa.Bolsa()
        self.estado = "jogando"
        self.dialogo = None
        self.eventos = []
        self.sons_espaciais = []
        self.aviso = ""
        self.aviso_t = 0.
        self.lume = Lume(95, CHAO, self.vidas_iniciais)
        self.entrar(etapa)

    def configurar_dificuldade(self, nivel):
        nivel = {"facil": "fácil", "sereno": "fácil", "dificil": "difícil"}.get(nivel, nivel)
        self.dificuldade = nivel if nivel in DIFICULDADES else "normal"
        self.dreno, self.dano, self.vidas_iniciais = NIVEIS[self.dificuldade]
        self.dreno *= .36

    @property
    def fagulhas_para_nova_tentativa(self):
        return NIVEIS[self.dificuldade_pendente or self.dificuldade][2]

    def aplicar_dificuldade_no_marco(self, *, repovoar=True):
        if self.dificuldade_pendente is None or (self.boss and not self.boss.vencido):
            return False
        self.configurar_dificuldade(self.dificuldade_pendente)
        self.dificuldade_pendente = None
        if repovoar:
            if self.em_vertical:
                corte_vertical.povoar(self)
            else:
                self.povoar_superficie()
        self.notificar(f"Dificuldade ativa · {self.dificuldade.capitalize()}.")
        return True

    def entrar(self, indice, retorno=False):
        self.em_vertical = False
        self.destino_vertical = None
        self.comporta_inicio = None
        self.veneziana_inicio = None
        self.sino_eco_inicio = None
        self.camera_y = 0.
        self.vestigios.clear()
        self.fagulha = None
        self.vespera_sinal = None
        self.etapa = indice
        self.fase = FASES[indice]
        self.flags = self.historico.setdefault((self.volta, indice), set())
        self.boss = None
        alterada = self.aplicar_dificuldade_no_marco(repovoar=False)
        self.gotas = self.fase.orvalhos
        self.povoar_superficie()
        # No Bosque, a primeira silhueta a aparecer precisa ser a de Lume.
        # Nos demais biomas ele chega entre o abrigo e o primeiro morador.
        entrada = 42 if indice == 0 else 139
        marco = ARENA-20 if "marco" in self.flags else (MEIO if "meio" in self.flags else entrada)
        self.checkpoint = (marco, CHAO)
        pos = (RAIZ+42, CHAO) if retorno else (entrada, CHAO)
        self.recolocar(pos)
        self.camera = max(0, min(self.fase.width - 960, pos[0] - 340))
        self.eventos.append("etapa")
        if not alterada:
            self.notificar(self.fase.name)

    def povoar_superficie(self):
        self.inimigos = [
            MorcegoDoGalho(self.dificuldade) if self.etapa == 0 and e[1] == ORIGEM_MORCEGO
            else Habitante(*e, dificuldade=self.dificuldade) for e in self.fase.inimigos
                         if "inimigo_" + str(e[1]) not in self.flags]
        if subsolo.ativo(self) and "inimigo_2860" not in self.flags:
            self.inimigos.append(Habitante("aranha", 2860, 1102, dificuldade=self.dificuldade, ouve_pousos=True))
        if raizes_bosque.ativo(self):raizes_bosque.povoar(self)
        if galeria_taquaral.ativo(self):galeria_taquaral.povoar(self)
        from .encontros import povoar
        povoar(self)
        for e in self.inimigos:
            e.guarda = self.tranca_fechada and e.origem[0] == VIGIA_X and e.tipo == "carabideo"

    def salvar(self):
        """Salva o progresso assentado. Objetos transitórios da arena renascem no marco."""
        return {
            "versao": 3, "mapa_grade": 24, "explorado": sorted(self.explorado), "missao": self.missao,
            'marcas':[dict(m) for m in self.marcas],
            'globos':[dict(g) for g in self.globos],'tochas':sorted(self.tochas),'nucleos':sorted(self.nucleos),'tutorial':sorted(self.tutorial),
            "corte": {"ativo": self.em_vertical, "marco": self.marco_vertical,
                      "memoria": sorted(self.cartografia)}, "modo": self.modo, "dificuldade": self.dificuldade,
            "dificuldade_pendente": self.dificuldade_pendente,
            "pisadas_escuta": sorted(self.pisadas_escuta),
            "etapa": self.etapa, "volta": self.volta, "vidas": self.lume.vidas,
            'energia': max(0.,self.lume.energia), 'retorno_pendente':self.estado in ('caido','derrota'),
            'vida':max(0.,self.lume.vida),
            "tempo": self.tempo,
            "pontuacao": self.pontuacao, "diario": list(self.diario),
            "bolsa": self.bolsa.salvar(self.tempo),
            'arma': self.lume.arma.equipamento,
            'sobreviventes':{k:dict(v) for k,v in self.sobreviventes.items()},'concluida':self.concluida,
            "fases": [{ "volta": volta, "etapa": etapa, "flags": sorted(flags)}
                      for (volta, etapa), flags in sorted(self.historico.items())],
        }

    @classmethod
    def carregar(cls, dados):
        """Carrega campanha local. Um arquivo inválido é recusado pelo chamador."""
        if not isinstance(dados, dict) or dados.get("versao") not in (1, 2, 3):
            raise ValueError("Formato de campanha desconhecido")
        etapa = int(dados["etapa"])
        if not 0 <= etapa < len(FASES):
            raise ValueError("Bioma desconhecido")
        jogo = cls(dados["modo"], dados["dificuldade"], etapa)
        jogo.volta = max(0, int(dados["volta"]))
        memoria = dados.get("explorado", [])
        if not isinstance(memoria,list) or len(memoria)>60000 or not all(isinstance(v,str) and len(v)<80 for v in memoria):
            raise ValueError("Mapa descoberto inválido")
        jogo.explorado = set(memoria) if dados.get("mapa_grade")==24 else set()
        jogo.pisadas_escuta = aula_sino.carregar_pisadas(dados.get("pisadas_escuta", []))
        from .marcas_mapa import carregar as carregar_marcas
        jogo.marcas=carregar_marcas(dados.get('marcas') if dados.get('mapa_grade')==24 else None,jogo.explorado)
        from .luzes_mundo import carregar as carregar_globos
        jogo.globos=carregar_globos(dados.get('globos'))
        for nome,permitidos in (('tochas',{'vigilia','bercario','jardim'}),('nucleos',{'vigilia','bercario','jardim'})):
            valor=dados.get(nome,[])
            if not isinstance(valor,list) or len(valor)>3 or not all(isinstance(v,str) for v in valor) or not set(valor)<=permitidos:raise ValueError('Clareira salva inválida')
            setattr(jogo,nome,set(valor))
        tutorial=dados.get('tutorial',[])
        if not isinstance(tutorial,list) or len(tutorial)>100 or not all(isinstance(v,str) and len(v)<60 for v in tutorial):raise ValueError('Tutorial salvo inválido')
        jogo.tutorial=set(tutorial)
        escolha=dados.get("missao")
        from .fio_corte import ID as pedido_fio
        missoes_borda = tuple(rotas_borda.PREFIXO + pessoa for pessoa in rotas_borda.POSTOS)
        jogo.missao = escolha if escolha in ("principal","secundaria","entrega_mimo",'pedido_raizes','resgates','jardim',pedido_fio,galeria_taquaral.PEDIDO,*(f"pedido_{i}" for i in range(4)),*missoes_borda) else "principal"
        for visita in dados["fases"]:
            nivel = int(visita["etapa"])
            if not 0 <= nivel < len(FASES):
                raise ValueError("Bioma desconhecido")
            flags = visita["flags"]
            if not isinstance(flags, list) or not all(isinstance(f, str) for f in flags):
                raise ValueError("Estado de bioma inválido")
            marcos = set(flags)
            if dados["versao"] == 1 and marcos.intersection(("marco","chefe","raiz")):
                # V1 terminava diretamente na arena após o primeiro mecanismo.
                marcos.update(("meio", FASES[nivel].preparo))
            jogo.historico[int(visita["volta"]), nivel] = marcos
        jogo.restauradas = sum("raiz" in flags for flags in jogo.historico.values())
        jogo.sobreviventes=resgates.carregar(dados.get('sobreviventes'))
        concluida=dados.get('concluida',jogo.restauradas>=4 and jogo.modo=='historia')
        if type(concluida) is not bool:raise ValueError('Desfecho salvo inválido')
        jogo.concluida=concluida
        jogo.diario = [(str(titulo), str(texto)) for titulo, texto in dados["diario"]]
        jogo.tempo = max(0., float(dados["tempo"]))
        jogo.bolsa = narrativa.Bolsa.carregar(dados.get("bolsa"), jogo.tempo)
        jogo.pontuacao = max(0, int(dados["pontuacao"]))
        jogo.lume.vidas = min(MAX_FAGULHAS, max(1, int(dados["vidas"])))
        jogo.entrar(etapa)
        if dados.get("versao")==3:
            corte=dados.get("corte",{})
            if not isinstance(corte,dict):
                raise ValueError("Cartografia do corte inválida")
            marco=corte.get("marco","bosque")
            memoria=corte.get("memoria",[])
            if marco not in corte_vertical.MARCOS or not isinstance(memoria,list) or not all(isinstance(v,str) for v in memoria):
                raise ValueError("Cartografia do corte inválida")
            jogo.marco_vertical=marco
            jogo.cartografia=set(memoria)
            if corte.get("ativo") and jogo.modo=="historia":
                corte_vertical.entrar(jogo,marco)
        pendente = dados.get("dificuldade_pendente")
        if pendente is not None and pendente not in DIFICULDADES:
            raise ValueError("Dificuldade pendente inválida")
        jogo.dificuldade_pendente = pendente
        jogo.reiniciar()
        if jogo.agulha_disponivel and dados.get('arma')=='agulha':
            jogo.lume.arma.equipamento='agulha'
        energia=dados.get('energia',100.)
        if type(energia) not in (int,float) or not math.isfinite(energia):raise ValueError('Luz salva inválida')
        vida=dados.get('vida',max(.01,min(100.,energia)))
        if type(vida) not in (int,float) or not math.isfinite(vida):raise ValueError('Vida salva inválida')
        if not dados.get('retorno_pendente',False):
            jogo.lume.energia=max(0.,min(100.,energia));jogo.lume.vida=max(0.,min(100.,vida))
        return jogo

    @property
    def setor_vertical(self):
        return corte_vertical.setor(self.lume.rect.centery,self.lume.rect.centerx)[1] if self.em_vertical else ""

    @property
    def altura_mundo(self):
        if aula_sino.ativa(self):
            return aula_sino.ALTURA
        return corte_vertical.ALTURA if self.em_vertical else (raizes_bosque.ALTURA if raizes_bosque.ativo(self)
                else subsolo.ALTURA if subsolo.ativo(self)
                else galeria_taquaral.ALTURA if galeria_taquaral.ativo(self) else 540)

    @property
    def orvalhos(self):
        return sum(1 for k in self.flags if k.startswith("gota_"))

    @property
    def fagulha_ativa(self):
        f = self.fagulha
        return f if f and f.restante(self.tempo) > 0 else None

    @property
    def raio(self):
        if self.lume.energia<=0:return 0.
        portatil = 90 + .38 * max(0., min(100., self.lume.energia))
        if self.bolsa.luz_ate > self.tempo:
            portatil += 65
        if self.bolsa.estoque['lente']:portatil+=18
        if self.boss and not self.boss.vencido:
            portatil += 22
        elif self.minichefe is not None:portatil+=14
        return portatil*.77 if self.fagulha_ativa else portatil

    @property
    def minichefe(self):
        if not raizes_bosque.ativo(self) or not 1474<self.lume.rect.centerx<2080 or self.lume.rect.bottom<1054:return None
        return next((e for e in self.inimigos if isinstance(e,raizes_bosque.Caruncho) and e.ativo),None)

    def visivel(self, centro, margem=0):
        from .visao import ponto_visivel
        return ponto_visivel(self,centro,margem)

    @property
    def combate(self):
        return bool(self.boss and not self.boss.vencido) or any(
            e.estado in ("aviso", "investida") for e in self.inimigos if e.ativo)

    @property
    def tranca_fechada(self):
        # Um marco de arena obtido em versão anterior já comprova a passagem.
        liberada = (f"inimigo_{VIGIA_X}" in self.flags or "marco" in self.flags
                    or "vagem" in self.flags or "chefe" in self.flags)
        return self.modo == "historia" and self.etapa == 2 and not liberada

    @property
    def solidos(self):
        if self.em_vertical:
            from .jardim import FLAGS
            from .fio_corte import REPARADA
            base = corte_vertical.terrenos("viveiro_aberto" in self.cartografia, frozenset(self.cartografia&FLAGS),
                                          corte_vertical.RAIZ_DUAS_BOCAS in self.cartografia, REPARADA in self.cartografia)
            if self.comporta_inicio is not None:
                painel = corte_vertical.painel_comporta(self)
                if painel.height:
                    return (*base, Terreno(painel, "tranca"))
            return base
        geometria=frozenset(self.flags.intersection(("dreno","ponte","no","contrapeso",self.fase.preparo,"chefe","raiz",'porta_ninho','cipo_estendido', galeria_taquaral.ABERTA, nicho_taquaral.ABERTO, aula_sino.PASSARELA)))
        ident=(self.etapa,geometria,subsolo.ativo(self),raizes_bosque.ativo(self))
        if getattr(self,"_geometria_id",None)!=ident:
            base=rotas_borda.terrenos(terrenos(self.etapa,geometria),self.etapa,geometria)
            self._geometria_base=tuple(subsolo.terrenos(base) if subsolo.ativo(self) else base)
            if raizes_bosque.ativo(self):self._geometria_base=tuple(raizes_bosque.terrenos(base,geometria))
            if galeria_taquaral.ativo(self):
                self._geometria_base = tuple(galeria_taquaral.terrenos(
                    base, galeria_taquaral.ABERTA in geometria, nicho_taquaral.ABERTO in geometria))
            self._geometria_id=ident
        out=list(self._geometria_base)
        if galeria_taquaral.ativo(self) and galeria_taquaral.ABERTA in self.flags and self.veneziana_inicio is not None:
            painel = galeria_taquaral.painel(self)
            if painel.w:
                out.append(Terreno(painel, "veneziana_sementes"))
        if self.tranca_fechada:
            out.append(Terreno(pygame.Rect(TRANCA_X, 223, 36, CHAO-223), "tranca"))
        if self.boss:
            out.extend(Terreno(rect, "arena") for rect in self.boss.apoios())
        if self.etapa == 0 and self.vestigios:
            from .abertura_bosque import BROTO, broto_aceso
            if broto_aceso(self):
                out.append(BROTO)
        out.extend(desvios_fagulha.terrenos(self))
        return out

    @property
    def objetos(self):
        if self.em_vertical:
            return corte_vertical.objetos(self)
        out = [o for o in self.fase.objetos if (not o.requer or o.requer in self.flags)
               and not (o.id in self.flags and o.tipo in ("peca", "registro", "brasa", "reserva", "pavio_nicho"))]
        if "encomenda_recolhida" in self.flags:
            out=[o for o in out if o.id!="encomenda_mimo"]
        deslocados = {}
        if self.etapa == 0 and "raiz" in self.flags:
            deslocados["vespera"] = rotas_borda.VESPERA
        if self.etapa == 1 and "ponte" in self.flags:
            deslocados["fio"] = (1567, CHAO)
            out.append(corrego_historia.BERCOS)
            if "raiz" in self.flags:
                deslocados["casca"] = corrego_historia.CASCA_MARGEM
        if self.etapa == 2 and "raiz" in self.flags:
            deslocados["eco"] = (RAIZ-74, CHAO)
        if self.etapa == 3 and "contrapeso" in self.flags:
            deslocados["pingo"] = (366, 377)
            if aula_sino.ECO in self.flags:
                out.append(Objeto(aula_sino.PASSARELA, "valvula", *aula_sino.SAIDA, "Baixar a passarela"))
        out = [Objeto(o.id, o.tipo, *deslocados[o.id], o.nome, o.requer) if o.id in deslocados else o for o in out]
        out.extend(Objeto(f"gota_{n}", "orvalho", x, y, "Orvalho") for n, (x, y) in
                   enumerate(self.gotas) if f"gota_{n}" not in self.flags)
        tipo_marco='marco' if recursos.limitado(self) else 'refugio'
        out.extend((
            Objeto("abrigo", "refugio", 70 if self.etapa == 0 else 82, CHAO, "Descansar sob a casca"),
            Objeto("abrigo_npc", "npc", 163, CHAO, ("Mimo", "Brasa", "Candeia", "Brasa")[self.etapa]),
            Objeto("atalho", "atalho", 1756, CHAO, "Abrir atalho ao abrigo" if "atalho" not in self.flags else "Voltar ao abrigo"),
            Objeto("meio", tipo_marco, MEIO, CHAO, "Guardar retorno no ramal"),
            Objeto("marco", tipo_marco, ARENA-24, CHAO, "Guardar retorno antes da arena"),
            Objeto("raiz", "raiz", RAIZ, CHAO, "Devolver orvalho" if "raiz" not in self.flags else "Ouvir a raiz"),
            Objeto("saida", "saida", SAIDA, CHAO, "Seguir a raiz"),
        ))
        if "atalho" in self.flags:
            out.append(Objeto("via", "atalho", 303, CHAO, "Voltar ao marco"))
        if self.etapa > 0:
            out.append(Objeto("voltar", "voltar", 34, CHAO, "Voltar ao bioma anterior"))
        if self.etapa == 3 and "chefe" in self.flags:
            out.append(Objeto("coruja_calma", "npc", FIM_ARENA+43, CHAO, "Coruja"))
        out.extend(corte_vertical.entradas(self))
        if subsolo.ativo(self):
            out.extend(subsolo.objetos(self))
        if raizes_bosque.ativo(self):out.extend(raizes_bosque.objetos(self))
        if galeria_taquaral.ativo(self):
            out.extend(galeria_taquaral.objetos(self))
        out.extend(resgates.objetos(self))
        out.extend(rotas_borda.objetos(self))
        out.extend(desvios_fagulha.objetos(self))
        from .encontros import objetos as lanternas
        out.extend(lanternas(self))
        return out

    def proximo(self):
        if self.destino_vertical is not None:
            return None
        p = self.lume.rect
        candidatos = []
        for o in self.objetos:
            if o.tipo in ('orvalho','orvalho_jardim'):
                continue
            if o.id == "comporta_viveiro" and self.comporta_inicio is not None:
                continue
            if o.tipo == "pavio_nicho" and (not self.lume.chao or abs(o.y - p.bottom) > 1.5):
                continue
            if o.tipo == rotas_borda.TIPO_CORDA and not self.lume.chao:
                continue
            dx = abs(o.x - p.centerx)
            if o.tipo == "corda" and dx < 50 and 216 <= p.bottom <= CHAO + 3:
                candidatos.append((dx, o))
            elif o.tipo == "valvula":
                # O desenho é apoiado no piso, mas Lume alcança seu aro acima da base.
                eixo = o.x, o.y - 35
                if dx <= 51 and p.top - 25 <= eixo[1] <= p.bottom + 25 and not any(
                    not t.atravessavel and t.rect.clipline(p.center, eixo) for t in self.solidos
                ):
                    candidatos.append((math.dist(p.center, eixo), o))
            elif dx <= 51 and abs(o.y - p.bottom) <= 48:
                candidatos.append((math.hypot(dx, o.y - p.bottom), o))
        return min(candidatos, key=lambda par: par[0])[1] if candidatos else None

    def manivela_girada(self, o):
        memoria = self.cartografia if self.em_vertical else self.flags
        return o.id in MANIVELAS and MANIVELAS[o.id][0] in memoria

    @property
    def interacao(self):
        if self.boss and not self.boss.vencido:
            return self.boss.interacao(self.lume.rect) or ""
        o = self.proximo()
        if not o:
            return ""
        if o.tipo=='refugio' and recursos.limitado(self):
            if 'descanso_'+o.id in self.flags:
                return f'Retirar bálsamos da reserva ({self.bolsa.reserva_balsamo})' if self.bolsa.reserva_balsamo else 'Abrigo sem provisões'
            return 'Usar reserva do abrigo (uma vez)'
        if o.tipo == "npc":
            return "Ouvir " + o.nome
        if o.id == aula_sino.ECO and o.id in self.flags:
            return "Tocar o sino novamente"
        if o.tipo == "elevador" and "ralo_aberto" not in self.cartografia:
            return "Examinar o contrapeso preso"
        if o.tipo == "valvula":
            if self.manivela_girada(o):
                return MANIVELAS[o.id][1]
            if o.id == "ralo_cisterna":
                return "Destravar o ralo" if corte_vertical.ralo_iluminado(self, o) else "Examinar a trava (precisa de K)"
            if o.id == "ponte" and "lingueta" not in self.flags:
                return "Examinar encaixe sem lingueta"
            if o.id == "ralo" and "ponte" not in self.flags:
                return "Examinar ralo preso à ponte"
        if o.id in self.fase.mecanismos and o.id in self.flags:
            return "Examinar o mecanismo"
        return o.nome

    @property
    def objetivo(self):
        if getattr(self,"ensaio_tatico",False):
            vivos=sum(e.ativo for e in self.inimigos if e.origem[0] in (1548,1660))
            return f"Afaste a patrulha da margem · {vivos} inimigo(s)" if vivos else "Patrulha vencida · Esc volta ao Campo de testes"
        from .orientacao import objetivo_atual
        alvo = objetivo_atual(self)
        if alvo:
            return alvo.texto
        return "Observe o fio e o salto. Enfrente a aranha e volte ao abrigo para tentar de novo."

    @property
    def dica_local(self):
        if self.em_vertical:
            return "Tab  mapa do corte   ·   S + Espaço  descer por uma grade"
        if raizes_bosque.setor(self):
            return 'S + Espaço desce pelos galhos. E no cipó do poço permite voltar mesmo sem vencer o Caruncho.'
        if galeria_taquaral.dentro(self):
            return "E no cipó central volta à superfície. S + Espaço desce dos galhos."
        x = self.lume.rect.centerx
        if subsolo.ativo(self) and 2480 < x < 3200:
            return "Raízes inferiores · S + Espaço desce. Salte pelos galhos para voltar."
        if self.tranca_fechada and 1700 < x < TRANCA_X:
            return "A casca bloqueia de frente. O 3º J ou S + J no ar rompe a guarda."
        if self.etapa == 0:
            if x < 295: return "A D  mover     Espaço  saltar     E  interagir"
            if x < 580: return "No ar, solte e aperte Espaço de novo para alcançar o galho de orvalho."
            if 622 < x < 1100: return "J, J, J: três cortes. No ar, S + J rebate sobre o alvo."
            if 1135 < x < 1285: return "S  agachar     Shift + direção  deslizar"
            if 1415 < x < 1720: return "J  golpe curto     K  clarão (22 de luz)"
        if self.etapa == 1 and 750 < x < 1120:
            return "A marca de Casca mostra a peça da ponte. Siga o sulco sob a raiz; direção + Shift vence a corrente."
        if MEIO-50 < x < MEIO+100: return RAMAIS[self.etapa].nome + " · marco do ramal"
        if self.etapa == 0 and 1970 < x < 2495:
            return "Troncos riscados: salte encostado, depois aperte Espaço a cada troca de parede."
        if self.etapa == 1 and 1980 < x < 2720:
            return "Na grade de casca, segure baixo e aperte Espaço para descer."
        if self.etapa == 2 and 1990 < x < 2930:
            return "Salte da beira do bambu. Segure Espaço ao cair para planar."
        if ARENA-95 < x < ARENA: return self.fase.fonte
        return ""

    def recolocar(self, pos):
        self.passagem = Passagem()
        self.lume.rect.size = (24, self.lume.ALTURA)
        self.lume.rect.midbottom = pos
        self.retorno_queda = tuple(pos)
        self.lume.vx = self.lume.vy = 0.
        self.lume.coyote = self.lume.buffer = self.lume.slide = self.lume.slide_cd = 0.
        self.lume.golpe = self.lume.pulso = self.lume.impacto = 0.
        self.lume.chao = True
        self.lume.em_corda = self.lume.na_parede = self.lume.planando = False
        self.lume.corda_destino = None
        self.lume.trava_lateral = self.lume.graca_parede = 0.
        self.lume.ultimo_impulso = self.lume.lado_parede = 0
        self.lume.ignorar_topo = None
        self.lume.planeio = self.lume.PLANEIO
        self.lume.asa_disponivel = True
        self.lume.batida_asa = 0.
        self.lume.arma = Arma(self.lume.arma.equipamento)
        self.aplicar_reliquias()

    def aplicar_reliquias(self):
        self.lume.bonus_dano = self.bolsa.bonus_dano
        self.lume.bonus_velocidade = self.bolsa.bonus_velocidade
        self.lume.custo_clarao = 18. if self.bolsa.estoque["resina"] else 22.
        self.lume.fator_custo_luz=.8 if self.bolsa.estoque['resina'] else 1.
        self.lume.tanino = self.bolsa.tanino_ate>self.tempo

    def notificar(self, texto, segundos=3.8):
        self.aviso, self.aviso_t = texto, segundos

    def memorizar(self, titulo, texto):
        if (titulo, texto) not in self.diario:
            self.diario.append((titulo, texto))

    @property
    def pedido_local(self):
        return narrativa.pedido_local(self)

    def trocar_item(self):
        if self.estado == "jogando" and not self.dialogo:
            self.notificar(self.bolsa.trocar())
        return self.bolsa.item.nome

    def usar_item(self):
        if self.estado!='jogando' or self.lume.vida<=0:return None
        if self.estado == "jogando" and not self.dialogo:
            return self.bolsa.usar(self)
        return None

    @property
    def agulha_disponivel(self):
        return (getattr(self, 'ensaio_armas', False) or
                getattr(self, 'ensaio_troca_arma', False) or
                'pedido_raizes_entregue' in self.historico.get((self.volta, 0), ()))

    def trocar_arma(self):
        if not self.agulha_disponivel or self.estado != 'jogando' or self.dialogo:
            return False
        if self.lume.impacto > 0 or not self.lume.arma.trocar():
            self.notificar('Conclua o golpe antes de trocar a arma.')
            return False
        agulha = self.lume.arma.equipamento == 'agulha'
        self.notificar('Agulha de taquara: alcance longo e golpe mais lento. Só Ctrl carrega luz e tem custo.' if agulha
                       else 'Espinho: cortes rápidos e curtos, sem custo de luz.')
        return True

    def fechar_dialogo(self):
        self.dialogo = None
        self.escolha_resgate=None

    def reiniciar(self, *, recuperar=True):
        self.motivo_morte=""
        self.ensino_ate=0.
        self.destino_vertical=None
        self.comporta_inicio = None
        self.veneziana_inicio = None
        self.sino_eco_inicio = None
        self.vestigios.clear()
        self.fagulha = None
        self.vespera_sinal = None
        if self.estado == "caido":
            self.estado = "jogando"
        self.boss = None
        self.dialogo = None
        self.escolha_resgate=None
        alterada = self.aplicar_dificuldade_no_marco()
        if not alterada:
            for inimigo in self.inimigos:
                if inimigo.ativo:
                    inimigo.repor()
        self.recolocar(self.checkpoint)
        if recuperar:
            self.lume.energia = 100.
            self.lume.vida = 100.
        self.lume.abate_ate=0.
        self.lume.combo_acertos=0
        self.lume.iframes = 1.35
        self.lume.golpe_cd = self.lume.pulso_cd = 0.
        self.camera = max(0, min(self.fase.width - 960, self.checkpoint[0] - 340))
        if self.em_vertical:
            corte_vertical.camera(self)
        elif subsolo.ativo(self):
            subsolo.camera(self)
        elif raizes_bosque.ativo(self):raizes_bosque.camera(self)
        elif galeria_taquaral.ativo(self):galeria_taquaral.camera(self)
        elif aula_sino.ativa(self):aula_sino.camera(self)
        if not alterada:
            self.notificar("Lume reencontra a luz do marco." if recuperar else "Lume voltou ao marco com os recursos da viagem.")
        self.eventos.append("retorno")

    def ferir(self, forcar=False):
        if self.lume.iframes > 0 and not forcar:
            return
        if not forcar and self.bolsa.absorver():
            self.lume.iframes = 1.0
            self.notificar("O casulo se rompeu e amorteceu o ataque.")
            self.eventos.append("corda")
            return
        self.lume.iframes, self.lume.impacto = 1.25, .25
        self.lume.arma.cancelar()
        self.lume.golpe = 0.
        self.lume.vida = max(0., self.lume.vida - self.dano)
        self.lume.combo_acertos=0
        self.eventos.append("dano")

    def recuperar_queda(self):
        vida=self.lume.vida-25.
        if vida<=0:
            self.perder_fagulha(motivo="queda")
            return
        destino=getattr(self,"retorno_queda",self.checkpoint)
        self.recolocar(destino)
        self.lume.vida=vida
        self.lume.combo_acertos=0
        self.lume.iframes=1.5
        self.eventos.append("dano")
        self.notificar("A queda custou 25 de vida. Lume voltou à última borda segura.")
        if self.em_vertical:
            corte_vertical.camera(self)
        elif subsolo.ativo(self):
            subsolo.camera(self)
        elif raizes_bosque.ativo(self):raizes_bosque.camera(self)
        elif galeria_taquaral.ativo(self):galeria_taquaral.camera(self)
        elif aula_sino.ativa(self):aula_sino.camera(self)

    def perder_fagulha(self, motivo="vida"):
        if self.estado != "jogando":
            return
        if self.boss and self.boss.ninhada is not None:
            self.boss.ninhada.limpar()
        self.lume.vidas = max(0, self.lume.vidas - 1)
        self.lume.energia = 0.
        self.lume.vida = 0.
        self.motivo_morte = motivo
        self.estado = "caido" if self.lume.vidas else "derrota"
        self.eventos.append("morte")

    def interagir(self, o):
        if o.tipo=='lanterna':
            from .encontros import interagir
            interagir(self,o);return
        if o.tipo == "reserva_fagulha":
            desvios_fagulha.recolher(self,o)
            return
        if o.tipo=='sobrevivente':
            resgates.conversar(self,o)
            return
        if o.tipo == rotas_borda.TIPO_CORDA:
            rotas_borda.usar_corda(self, o.id)
            return
        if o.tipo=='raizes':
            raizes_bosque.interagir(self,o)
            return
        if o.tipo=="galeria_sementes":
            galeria_taquaral.interagir(self,o)
            return
        if o.tipo == "reliquia":
            item = o.id.removeprefix("reliquia_")
            if not self.bolsa.estoque.get(item):
                self.bolsa.receber(item, 1)
                self.aplicar_reliquias()
                ficha = narrativa.POR_ID[item]
                self.memorizar(ficha.nome, ficha.descricao)
                self.notificar(ficha.nome + " · " + ficha.descricao, 7.)
                self.eventos.append("coleta")
            return
        if self.em_vertical or o.tipo=="fenda":
            corte_vertical.interagir(self,o)
            return
        l = self.lume
        if o.tipo == "npc":
            estado = 2 if "raiz" in self.flags else int(
                self.fase.passos[0][0] in self.flags or (o.id == "abrigo_npc" and self.restauradas > 0))
            narrativa.conversar(self, o.nome, FALAS[o.nome][estado])
        elif o.tipo == "reserva":
            narrativa.abrir_reserva(self)
        elif o.id == vento_taquaral.PAVIO and o.id not in self.flags:
            self.flags.add(o.id)
            self.bolsa.receber("pavio", 1)
            self.memorizar("O beiral do Taquaral", "Risca enrolou um pavio seco e guardou aqui, longe da chuva.")
            self.notificar("Pavio de pólen na bolsa. Q escolhe; F prolonga a luz.")
            self.eventos.append("coleta")
        elif o.tipo == "encomenda":
            if "encomenda_recolhida" not in self.flags:
                self.flags.update(("encomenda_aceita","encomenda_recolhida"))
                self.missao="entrega_mimo"
                self.notificar("Mochila de ervas recolhida. Leve-o a Mimo no abrigo da entrada.",7.)
                self.memorizar("A mochila dos casulos","A mochila de ervas de Mimo ficou na varanda alta. Mimo prometeu preparar a lâmina para atravessar carapaças.")
                self.eventos.append("coleta")
        elif o.id == "placa_canal":
            self.flags.add("pista_canal")
            self.dialogo=("A peça levada pela cheia",
                "Casca desenhou a roda sem pino e uma peça de três dentes. Um sulco de metal segue sob a raiz baixa. "
                "Drene a água na roda acima de Casca. Depois, direção + Shift atravessa a corrente. "
                "Use E junto ao metal para recolher a lingueta e encaixá-la na roda da ponte. "
                "Três riscos no apoio marcam o último turno de água na borda.")
            self.memorizar(*self.dialogo)
            corrego_historia.comparar(self)
            self.eventos.append("pagina")
        elif o.id == corrego_historia.BERCOS.id:
            corrego_historia.examinar(self)
        elif o.tipo == "registro":
            self.flags.add(o.id)
            self.dialogo = self.fase.registro
            self.memorizar(*self.dialogo)
            mapas = ("O cipó depois da vigia leva à peça da porteira. Além do marco, as paredes do poço levam à cunha.",
                     "Drene o canal e busque a lingueta no túnel. Depois da ponte, desça pela grade e solte o ralo.",
                     "O nó revela três apoios para alcançar a brasa. A vagem fica do outro lado da ponte quebrada.",
                     "A roldana solta a corda do contrapeso. Além do marco, o sino fica sob a grade da câmara.")
            self.memorizar("Mapa parcial · " + self.fase.name, mapas[self.etapa])
            self.eventos.append("pagina")
        elif o.id == aula_sino.PASSARELA:
            aula_sino.soltar(self)
        elif o.id in self.fase.mecanismos:
            m = self.fase.mecanismos[o.id]
            if m.requer and m.requer not in self.flags:
                from .orientacao import pista_mecanismo
                self.notificar(pista_mecanismo(self, o), 7.)
            elif o.id in self.flags:
                self.notificar(m.efeito)
            else:
                self.flags.add(o.id)
                self.notificar(m.efeito)
                self.eventos.extend(m.audio)
                self.pontuacao += 25
                if o.id in ("peca", "ponte", "brasa", "contrapeso"):
                    narrativa.guardar_virada(self, narrativa.VESTIGIOS)
                if o.id == self.fase.preparo:
                    narrativa.guardar_virada(self, narrativa.RAMAIS)
            if o.id == aula_sino.ECO and o.id in self.flags:
                aula_sino.tocar(self)
        elif o.tipo == "corda":
            if l.rect.bottom < CHAO - 120:
                self.recolocar((o.x - 40, CHAO))
            else:
                l.em_corda = True
                l.rect.centerx = o.x + 10
                l.vx = l.vy = 0.
                self.eventos.append("corda")
                if self.etapa == 0 and o.id == "corda" and "valvula" not in self.flags:
                    # A mesma marca evita conceder a pontuação de passagem duas vezes em saves antigos.
                    self.flags.add("valvula")
                    self.pontuacao += 25
        elif o.tipo == "refugio":
            recursos.descansar(self,o)
        elif o.tipo=='marco':
            if o.id=='marco' and self.fase.preparo not in self.flags:
                self.notificar('Abra a passagem principal antes de guardar este retorno.');return
            self.flags.add(o.id)
            self.checkpoint=(MEIO if o.id=='meio' else ARENA-20,CHAO)
            self.notificar('Retorno guardado. Este marco não cura; guarde os bálsamos para o perigo.',6.)
            self.aplicar_dificuldade_no_marco()
        elif o.tipo == "atalho":
            self.flags.add("atalho")
            self.recolocar((1728 if o.id == "via" else 320, CHAO))
            self.notificar("Os dois lados da casca agora se comunicam.")
            self.eventos.append("porta")
        elif o.tipo == "raiz":
            if "chefe" not in self.flags:
                self.notificar("A guardiã ainda guarda o caminho.")
            elif self.orvalhos < 3:
                self.notificar(f"A raiz precisa de três gotas. Você encontrou {self.orvalhos}.")
            elif "raiz" not in self.flags:
                self.flags.add("raiz")
                self.restauradas += 1
                self.pontuacao += 180
                self.lume.energia = 100.
                self.lume.vida = 100.
                self.eventos.append("raiz")
                self.notificar("O orvalho corre pelas raízes de fora. O caminho responde.")
                narrativa.guardar_virada(self, narrativa.RAIZES)
            else:
                self.notificar("Há insetos cantando no galho molhado.")
        elif o.tipo == "saida":
            if "raiz" not in self.flags:
                self.notificar("A trilha se abre quando a raiz recebe o orvalho.")
            elif self.etapa == 3:
                if self.concluida:
                    self.notificar('A floresta continua aberta. Volte pelos biomas e procure quem ficou para trás.',6.)
                else:
                    self.concluida=True
                    self.estado = "vitoria"
                    self.eventos.append("vitoria")
            else:
                self.entrar(self.etapa + 1)
        elif o.tipo == "voltar":
            self.entrar(self.etapa - 1, retorno=True)

    def update(self, dt, cmd=None):
        self.eventos = []
        self.sons_espaciais = []
        if self.estado != "jogando" or self.dialogo or dt <= 0:
            return
        cmd = cmd or Comando()
        # E e os ataques são bordas de tecla, mesmo quando um frame precisa
        # de vários passos de física. Conversa congela até o último relógio.
        o = self.proximo() if cmd.interagir and not (self.boss and not self.boss.vencido) else None
        # Na cisterna, K e E podem chegar no mesmo quadro. Teste o clarão já lançado.
        examinar_apos_clarao = o is not None and o.id == "ralo_cisterna" and cmd.clarao
        if o and not examinar_apos_clarao:
            origem = self.etapa, self.em_vertical
            self.interagir(o)
            if self.dialogo or self.estado != "jogando" or origem != (self.etapa, self.em_vertical):
                if self.dialogo:
                    from .tutorial import confirmar
                    confirmar(self,'interacao')
                return
        if cmd.fagulha:
            lancar(self)
        vida_antes=self.lume.vida
        clarao = self.lume.atacar(cmd)
        if self.lume.vida<vida_antes:
            self.eventos.append('sacrificio')
            self.notificar('Sem brilho suficiente: a habilidade consome vida.',3.)
        if self.lume.vida<=0:
            self.perder_fagulha('sacrificio' if self.lume.vida<vida_antes else 'vida');return
        if clarao:
            from .luzes_mundo import claro
            if cmd.baixo and not self.lume.chao and self.lume.vy > 96:
                self.lume.vy = 38.
                self.eventos.append("freio_luz")
            for e in self.inimigos:
                if e.ativo and math.dist(e.rect.center,self.lume.rect.center)<=520 and not claro(self,e.rect.center):
                    e.cego=.8 if e.tipo!='carabideo' else .4
            self.vestigios.append(Vestigio(*self.lume.rect.center, self.tempo, 9. if self.bolsa.luz_ate>self.tempo else DURACAO))
            self.eventos.append("pulso")
            if not self.em_vertical:
                narrativa.responder_chamado(self)
        if examinar_apos_clarao:
            self.interagir(o)
            if self.dialogo:
                return
        dt = min(.1, dt)
        passos = max(1, math.ceil(dt * 120 - 1e-7))
        retido = Comando(mover=cmd.mover, baixo=cmd.baixo, segurar_salto=cmd.segurar_salto)
        for i in range(passos):
            self.passo(dt / passos, cmd if i == 0 else retido, clarao and i == 0)
            if self.estado != "jogando":
                break
        licao_vespera.atualizar(self)
        from .descoberta import revelar
        revelar(self)
        from .tutorial import atualizar as ensinar
        ensinar(self,cmd)

    def passo(self, dt, cmd, clarao):
        l = self.lume
        if l.chao and not l.em_corda and l.vida>0 and any(
                abs(l.rect.bottom-t.rect.top)<1.5 and l.rect.right>t.rect.left
                and l.rect.left<t.rect.right for t in self.solidos):
            self.retorno_queda = tuple(l.rect.midbottom)
            aula_sino.pisar(self)
        antes = self.tempo
        self.tempo += dt
        avisar_pouso(self,antes)
        desvios_fagulha.revelar(self)
        while self.vestigios and self.tempo - self.vestigios[0].inicio >= self.vestigios[0].duracao:
            self.vestigios.pop(0)
        self.aviso_t = max(0., self.aviso_t - dt)
        if self.aviso_t <= 0: self.aviso = ""
        self.aplicar_reliquias()
        # Brilho estável: só habilidades de luz têm custo (decisão S08).
        if self.em_vertical:
            corte_vertical.passo(self,dt,cmd,clarao)
            return
        posicao_anterior = l.rect.center
        estava_chao, estava_corda = l.chao, l.em_corda
        if l.em_corda:
            alvo = l.corda_destino if l.corda_destino is not None else 240 if self.etapa == 0 else 242
            l.rect.bottom = aproximar(l.rect.bottom, alvo, 265 * dt)
            if l.rect.bottom == alvo:
                l.em_corda = False
                l.corda_destino = None
                l.chao = True
            else:
                l.chao = False
        else:
            corrente = -128 if self.etapa == 1 and 855 < l.rect.centerx < 1032 and l.rect.bottom > 406 else 0
            vento = ((vento_taquaral.sobre(*l.rect.midbottom) or galeria_taquaral.vento(self))
                     if self.etapa == 2 else None)
            if l.movimento(dt, cmd, self.solidos, corrente, True, vento=vento):
                self.eventos.append("pulo")
            if l.bateu:
                self.eventos.append("impacto")
        l.rect.left = max(0, min(l.rect.left, self.fase.width - l.rect.w))
        if self.etapa in (0, 2) and not hasattr(self, "sala_id"):
            self.passagem.mover(self.tempo, posicao_anterior, l.rect.center)
        pouso = not estava_chao and l.chao
        if pouso: self.eventos.append("pouso")
        pos_pouso = l.rect.midbottom if pouso and not estava_corda else None
        if cmd.deslize and l.slide >= .60: self.eventos.append("deslize")
        limite=raizes_bosque.limite_queda(self) if raizes_bosque.ativo(self) else subsolo.limite_queda(self)
        if galeria_taquaral.dentro(self):
            limite = galeria_taquaral.ALTURA
        elif aula_sino.dentro(self) and self.lume.rect.bottom > 475:
            limite = aula_sino.ALTURA
        if l.rect.top > limite:
            self.recuperar_queda()
            return
        for o in self.objetos:
            if o.tipo == "orvalho" and l.rect.inflate(16, 18).collidepoint(o.x, o.y):
                self.flags.add(o.id)
                l.energia = min(100., l.energia + 20)
                self.pontuacao += 10
                self.eventos.append("coleta")
        if self.tranca_fechada and l.rect.centerx > MEIO+20 and "viu_vigia" not in self.flags:
            self.flags.add("viu_vigia")
            self.notificar("O vigia aperta a trança. Ataque pelas costas ou quebre a guarda com o terceiro corte.", 5.)
        if l.rect.centerx >= MEIO-36 and l.rect.bottom<=CHAO+24 and "meio" not in self.flags:
            self.flags.add("meio")
            self.checkpoint = (MEIO, CHAO)
            recursos.iluminar_marco(self)
            self.notificar("Retorno no ramal · sem cura automática · " + RAMAIS[self.etapa].nome)
            self.aplicar_dificuldade_no_marco()
            self.eventos.append("coleta")
        if l.rect.centerx >= ARENA-52 and self.fase.preparo in self.flags and "marco" not in self.flags:
            self.flags.add("marco")
            self.checkpoint = (ARENA-20, CHAO)
            recursos.iluminar_marco(self)
            self.notificar("Retorno antes da arena. O marco guarda a volta; não repõe luz.")
            self.aplicar_dificuldade_no_marco()
            self.eventos.append("coleta")
        if l.rect.left >= ARENA + 5 and self.fase.preparo in self.flags and "chefe" not in self.flags and self.boss is None:
            from .chefes import Encontro
            self.boss = Encontro(self.etapa, ARENA, CHAO, FIM_ARENA - ARENA,
                                 despertar=self.modo=='historia',aliados=len(self.sobreviventes),
                                 dificuldade=self.dificuldade)
            self.eventos.append("arena")
        vida_antes=l.vida
        if l.arma.avancar(dt, l):
            self.eventos.append("golpe")
        if l.vida<vida_antes:
            self.eventos.append('sacrificio');self.notificar('O golpe usou vida porque faltou brilho.',3.)
        if l.vida<=0:self.perder_fagulha('sacrificio');return
        golpe = l.arma.area(l)
        if self.boss and not self.boss.vencido:
            l.rect.left = max(l.rect.left, ARENA)
            ruido = 1.0 if l.slide > 0 or pouso else min(.66, abs(l.vx) / 360) if l.chao else .08
            vida_chefe=self.boss.vida
            fagulha = self.fagulha_ativa
            if fagulha and fagulha.progresso(self.tempo) < 1:
                fagulha = None
            eventos = self.boss.update(dt, l.rect, ruido=ruido, golpe=golpe, clarao=clarao,
                                       interagir=cmd.interagir, direcao=cmd.mover,
                                       serie=l.arma.serie,bonus_dano=l.bonus_dano,
                                       dano_corte=2*l.arma.perfil.dano if l.arma.perfil else 2.,
                                       fagulha=fagulha)
            self.eventos.extend(e for e in eventos if e != "dano_jogador")
            if self.boss.vida<vida_chefe and golpe and self.boss.ultimo_corte==l.arma.serie:self.acertou_combo()
            if 'gota_final' in eventos:
                l.energia=max(l.energia,32.+5*self.boss.aliados)
                self.notificar('Orvalho do ninho: um pulso guardado. K perto da marca devolve o sinal.',5.)
            if "dano_jogador" in eventos: self.ferir()
            if self.boss.vencido:
                self.flags.add("chefe")
                self.recuperar_abate(15,25)
                self.notificar("A guardiã encontra a calma." if self.etapa == 3 else "A raiz libera a saída da arena.")
                self.pontuacao += 120
                self.eventos.append("porta")
            elif self.boss.ninhada is not None and self.boss.ninhada.vivos:
                self.combater_inimigos(dt, golpe, clarao, reforcos=self.boss.ninhada.vivos)
        else:
            self.combater_inimigos(dt, golpe, clarao, pos_pouso=pos_pouso)
        if l.vida <= 0:
            self.perder_fagulha()
        alvo = l.rect.centerx - (410 if l.face < 0 else 340)
        if self.boss and not self.boss.vencido:
            alvo = ARENA - (960 - (FIM_ARENA - ARENA)) / 2
        alvo = max(0., min(self.fase.width - 960, alvo))
        self.camera += (alvo - self.camera) * (1. - math.exp(-7.5 * dt))
        if subsolo.ativo(self):
            subsolo.camera(self, dt)
        if raizes_bosque.ativo(self):raizes_bosque.atualizar(self,dt)
        if galeria_taquaral.ativo(self):
            galeria_taquaral.atualizar(self, dt)
        if aula_sino.ativa(self):
            aula_sino.camera(self, dt)

    def recuperar_abate(self,vida=3.,brilho=8.):
        l=self.lume
        if l.vida<=0:return
        ganho=(min(100.,l.vida+vida)-l.vida,min(100.,l.energia+brilho)-l.energia)
        l.vida+=ganho[0];l.energia+=ganho[1]
        if any(ganho):
            l.ganho_abate=ganho;l.abate_ate=self.tempo+1.4;self.eventos.append('coleta')

    def acertou_combo(self):
        l=self.lume
        if l.vida<=0:return
        l.combo_acertos+=1
        l.energia=min(100.,l.energia+.35*min(8.,1.25**min(10,l.combo_acertos//3)))

    def combater_inimigos(self, dt, golpe, clarao, *, pos_pouso=None, reforcos=None):
        from .encontros import coordenar
        if reforcos is None:
            coordenar(self)
        moradores = self.inimigos if reforcos is None else reforcos
        lume = self.lume
        terrenos = self.solidos
        for e in moradores:
            if not e.ativo:
                continue
            if getattr(e,'dormir_distante',False) and (abs(e.rect.centerx-lume.rect.centerx)>1000 or abs(e.rect.centery-lume.rect.centery)>760) and not e.projeteis:
                continue
            golpe = lume.arma.area(lume)
            e.companhia=next((outro.rect.centerx for outro in moradores if outro is not e
                and outro.ativo and abs(outro.rect.centerx-e.rect.centerx)<350),None)
            vida_antes=e.vida
            resultado = e.acertar(lume.arma, golpe, clarao, lume)
            if e.vida < vida_antes and golpe and lume.arma.serie == e.ultimo_corte:
                self.acertou_combo()
                if self.modo == "historia" and isinstance(e, MorcegoDoGalho) and not clarao:
                    e.impacto_corte = ImpactoDoCorte(self.tempo, golpe.clip(e.rect).center,
                                                    lume.arma.face, not e.ativo)
                    if lume.arma.tipo in ("corte1", "corte2", "corte3", "avanco", "retorno", "queda"):
                        self.tutorial.add(CORTE_PRATICADO)
            if resultado:
                self.eventos.append(resultado)
                if (lume.arma.tipo == "queda" and golpe and lume.arma.serie == e.ultimo_corte
                        and resultado != "bloqueio"):
                    lume.arma.rebote = .16
                    lume.vy = -344.
                    lume.chao = False
                    self.eventos.append("rebote")
                if not e.ativo:
                    if reforcos is not None:
                        self.recuperar_abate(0, 3)
                        continue
                    if self.em_vertical:
                        self.cartografia.add("vigia_"+str(e.origem[0]))
                    else:
                        origem = ORIGEM_MORCEGO if isinstance(e, MorcegoDoGalho) else e.origem[0]
                        self.flags.add("inimigo_" + str(origem))
                    self.pontuacao += 18
                    self.recuperar_abate(10,18) if isinstance(e,raizes_bosque.Caruncho) else self.recuperar_abate()
                    if isinstance(e, nicho_taquaral.CobraDosBercos):
                        self.notificar("A Cobra dos Berços recuou. Acenda a luz sobre o cofre a oeste.", 6.)
                    elif e.guarda:
                        self.eventos.append("porta")
                        self.notificar("O vigia recua. A trança cai e a ponte das sementes está livre.", 5.)
                    continue
            if pos_pouso is not None and isinstance(e, Habitante) and e.ouvir_pouso(pos_pouso):
                self.sons_espaciais.append(("patas_perto", e.rect.centerx))
            dentro_do_clarao = any(math.dist(e.rect.center, (v.x, v.y)) <= v.raio(self.tempo)
                                   for v in self.vestigios)
            raio_isca = max(self.raio, 225) if dentro_do_clarao else self.raio
            atingiu = False
            if not reagir(self,e,dt,terrenos):
                avisos, atingiu = e.update(dt,lume,raio_isca,"no" in self.flags or dentro_do_clarao,terrenos)
                self.sons_espaciais.extend(avisos)
            vivos = []
            for p in e.projeteis:
                contato = p.avancar(dt, lume, terrenos, golpe, clarao)
                if contato == "corte":
                    self.eventos.append("acerto")
                elif contato == "dano":
                    atingiu = True
                elif not contato:
                    vivos.append(p)
            e.projeteis = vivos
            if atingiu and lume.iframes <= 0:
                vida = lume.vida
                self.ferir()
                if lume.vida < vida:
                    lume.vx += 143 if lume.rect.centerx >= e.rect.centerx else -143
