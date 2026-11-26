"""Entrada de Miopia. A simulação só avança na tela de jogo, fora de conversas."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import sys
if __package__ in ("",None):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("SDL_RENDER_SCALE_QUALITY","1")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT","1")
import pygame
from src import telas, ambiental, mapa_visor, tutorial
from src import pygame_hd
from src.janela_hd import Janela, LOGICA
from src.audio import Audio
from src.controles import ACOES, EVENTOS_PAD, PADRAO, Controles, Gamepad
from src.ensaios import ENSAIOS, INDICE_ARANHA, SEMENTE_ARANHA, preparar_ensaio
from src.arte_lume import imagem_lume
from src.ilustracao import estilo, fonte, tinta, linhas
from src.memoria import Memoria
from src.paisagem import Paisagem, hud
from src.replay_aranha import GravacaoAranha, HistoricoCheio, gravar_tentativa, iterar_reproducao, ler_tentativa
from src.roteiro import EFEITOS_RAIZ, PROLOGO
from src.travessia import Comando, DIFICULDADES, Jornada

ACEITAR = (pygame.K_RETURN,pygame.K_KP_ENTER,pygame.K_SPACE)
CORES_AUDIO = ("bosque","corrego","taquaral","gruta")
PAUSA_NO_ACERTO=.022

class App:
    pausa_nomes=["Continuar","Diário","Ajustes","Voltar ao marco","Salvar e voltar ao menu"]
    def __init__(self, temporaria=False, pasta_ensaios=None):
        pygame.mixer.pre_init(44100,-16,2,512)
        pygame.init()
        fonte.cache_clear()
        tinta.cache_clear()
        icone = pygame_hd.destino(imagem_lume("parado",0,64,64)).pixels
        self.janela = Janela(icone)
        self.cheia = self.janela.cheia
        self.quadro_renderizado = self.janela.quadro
        self.tela = pygame_hd.nativa(self.quadro_renderizado, LOGICA)
        self.mem=Memoria(temporaria)
        self.controles = Controles(self.mem.prefs["teclas"])
        self.gamepad = Gamepad()
        self.capturando_tecla = False
        self.aviso_tecla = ""
        self.audio=Audio()
        self.ajustar_som()
        self.credito_audio=("Vento, água, taquaras e ecos sintetizados para Miopia. Seis espécies e os guardiões têm avisos próprios, posicionados em estéreo conforme a distância e o lado de Lume.")
        self.paisagem=Paisagem()
        self.paisagem.brilho_mata=self.mem.prefs["brilho"]
        self.morte_desde=0.
        self.impacto_restante=0.
        self.ensaio=None
        self.semente_aranha=SEMENTE_ARANHA
        self.gravacao=None
        self.ultimo_replay=None
        self.aviso_replay=""
        self.pasta_ensaios=pasta_ensaios
        self.gravar_em_disco=not temporaria or pasta_ensaios is not None
        self.reproducao=None
        self.espera_replay=0.
        self.replay_pausado=False
        self.rodando=True
        self.relogio=0.
        self.jogo=None
        self.selecao=0
        self.estado="menu"
        self.alvos=[]
        self.bordas=set()
        self.anterior="menu"
        self.pagina=0
        self.mapa_visor=mapa_visor.Visor()
        self.mapa_aviso=''
        self.mapa_aviso_ate=0.
        self.mapa_tipo=0
        self.pedido_cursor=0
        self.quadro=0
        self.fala=""
        self.fala_paginas=['']
        self.pagina_fala=0
        self.letras=0
        self.espera=0.
        self.passo_som=0.
        self.ultimo_save=None
        self.proximo_save=0.
        self.resultados_pendentes = []
        self.mem_camp=self.mem.ler("campanha")
        self.conf_acao=self.conf_msg=self.conf_titulo=self.confirmacao=""
        self.registro_etapa=0
        self.resposta=None
        self.musica("menu")

    def musica(self,cena):
        self.audio.tocar_musica(cena)

    def ajustar_som(self):
        self.audio.volume_musica=self.mem.prefs["musica"]
        self.audio.volume_efeitos=self.mem.prefs["efeitos"]
        self.audio.mudo=self.mem.prefs["mudo"]
        self.audio.aplicar_volumes()

    def som(self,nome):
        self.audio.tocar(nome)

    def mudar(self,nome):
        self.estado=nome
        self.mapa_visor.arrastando=False
        self.impacto_restante=0.
        self.selecao=0
        self.alvos=[]
        self.bordas.clear()
        self.gamepad.limpar()

    def menu(self):
        self.fechar_tentativa("menu")
        self.reproducao=None
        self.salvar_campanha()
        self.resultados_pendentes.clear()
        self.jogo=None
        self.ensaio=None
        self.mem_camp=self.mem.ler("campanha")
        self.mudar("menu")
        self.musica("menu")

    def menu_nomes(self):
        itens=["Continuar história","Nova história"] if self.mem_camp else ["Jogar história"]
        return itens+["Campo de testes","Como jogar","Ajustes","Recordes","Créditos","Sair"]

    def fim_nomes(self):
        if self.ensaio==INDICE_ARANHA:
            return ["Repetir a mesma semente","Voltar ao campo de testes"]
        j=self.jogo
        if j.estado=="derrota":
            return [("Retomar do marco" if j.modo=="historia" else "Tentar outra noite"),"Voltar ao menu"]
        if j.estado=='vitoria' and j.modo=='historia':return ['Explorar a floresta','Voltar ao menu']
        return ["Voltar ao menu"]

    def fechar_tentativa(self,motivo):
        if self.gravacao is None:
            return
        gravacao=self.gravacao
        self.gravacao=None
        self.ultimo_replay=gravacao.documento(self.jogo,motivo)
        self.aviso_replay="Última tentativa disponível nesta sessão."
        if self.gravar_em_disco:
            try:
                arquivo=gravar_tentativa(gravacao,self.jogo,motivo,self.pasta_ensaios)
                self.aviso_replay=f"Histórico local: {arquivo.name}"
            except HistoricoCheio as erro:
                self.aviso_replay=str(erro)
            except OSError:
                self.aviso_replay="Só nesta sessão. Confira espaço e permissão na pasta de ensaios."
        if self.ultimo_replay["fim"]["motivo"]=="limite":
            self.aviso_replay+=" Replay limitado ao trecho inicial."

    def comecar_ensaio(self,indice,dificuldade=None):
        self.fechar_tentativa("reinicio")
        self.ensaio=indice
        self.jogo=preparar_ensaio(indice,dificuldade or self.mem.prefs["dificuldade"],self.semente_aranha)
        if indice==INDICE_ARANHA:
            self.gravacao=GravacaoAranha(self.jogo)
        self.jogar()

    def voltar_aos_ensaios(self):
        selecionado=self.ensaio
        self.fechar_tentativa("saida")
        self.reproducao=None
        self.jogo=None
        self.ensaio=None
        self.mudar("ensaios")
        if selecionado is not None:
            self.selecao=selecionado
        self.musica("menu")

    def assistir_tentativa(self,dados):
        self.jogo=preparar_ensaio(INDICE_ARANHA,dados["dificuldade"],dados["semente"])
        self.ensaio=INDICE_ARANHA
        self.reproducao=iterar_reproducao(dados,self.jogo)
        self.espera_replay=0.
        self.replay_pausado=False
        self.mudar("replay")
        self.musica("bosque")

    def avancar_replay(self,dt):
        if self.reproducao is None or self.replay_pausado:
            return
        if self.impacto_restante>0:
            self.impacto_restante=max(0.,self.impacto_restante-dt)
            return
        self.espera_replay-=dt
        try:
            while self.espera_replay<=0:
                passo=next(self.reproducao)
                self.espera_replay+=passo
                if passo>0:
                    self.sons_da_jornada(self.jogo,passo)
                    self.marcar_impacto(self.jogo)
                    if self.impacto_restante>0:
                        break
        except StopIteration:
            self.reproducao=None
            self.aviso_replay="Reprodução conferida até o último comando."
        except ValueError as erro:
            self.reproducao=None
            self.aviso_replay="Reprodução interrompida: "+str(erro)

    def salvar_campanha(self,forcar=True):
        j=self.jogo
        if self.ensaio is not None or not j or j.modo!="historia" or j.estado not in ("jogando","caido","vitoria","derrota"): return
        if not forcar and self.relogio<self.proximo_save:return
        self.proximo_save=self.relogio+.65
        assinatura=(j.etapa,j.pontuacao,j.lume.vidas,round(j.lume.energia),round(j.lume.vida),j.checkpoint,len(j.diario),
                    tuple(sorted(j.flags)),j.bolsa.revisao,j.lume.arma.equipamento,j.em_vertical,j.marco_vertical,frozenset(j.cartografia),frozenset(j.explorado),j.missao,
                    j.concluida,tuple((k,v['oficio'],v['premio']) for k,v in sorted(j.sobreviventes.items())),
                    tuple((m['celula'],m['tipo']) for m in j.marcas),j.dificuldade,j.dificuldade_pendente)
        assinatura+=(tuple((g['regiao'],g['x'],g['y']) for g in j.globos),frozenset(j.tochas),frozenset(j.nucleos),frozenset(j.tutorial),
                     frozenset(j.pisadas_escuta))
        if forcar or self.resultados_pendentes or assinatura != self.ultimo_save:
            dados = j.salvar()
            if j.estado == "derrota":
                dados["vidas"] = j.fagulhas_para_nova_tentativa
            if self.mem.guardar_campanha(dados, self.resultados_pendentes):
                self.mem_camp = dados
                self.resultados_pendentes.clear()
                self.ultimo_save = assinatura

    def registrar_resultado(self):
        j = self.jogo
        self.resultados_pendentes.append((j.modo, j.estado, j.volta*4+j.etapa+1, j.pontuacao, j.tempo))
        self.salvar_campanha()

    def iniciar(self,modo,continuar=False):
        self.fechar_tentativa("menu")
        self.ensaio=None
        self.resultados_pendentes.clear()
        if continuar:
            try: self.jogo=Jornada.carregar(self.mem_camp)
            except (ValueError,KeyError,TypeError,AttributeError,OverflowError):
                self.mem.aviso="O marco salvo está ilegível. Comece uma nova história."
                self.mem_camp=None
                self.mudar("menu")
                return
        else:
            self.jogo=Jornada(modo,self.mem.prefs["dificuldade"])
            if modo=='historia':self.jogo.flags.add('ouviu_resgates')
        self.ultimo_save=None
        self.salvar_campanha()
        if modo=="historia" and not continuar:
            self.quadro=0
            self.mudar("prologo")
            self.nova_fala(PROLOGO[0][1])
            self.musica("historia")
        else:
            self.jogar()

    def jogar(self):
        self.mudar("jogo")
        self.musica(self.tema_jornada())

    def nova_fala(self,msg):
        self.pagina_fala=0
        self.alvos=[];self.selecao=0
        if self.estado=='prologo':self.fala_paginas=[msg]
        else:
            escolha=self.jogo and self.jogo.escolha_resgate is not None
            if escolha:
                oficio=self.jogo.sobreviventes[self.jogo.escolha_resgate]['oficio']
                self.selecao=int(oficio=='abrigo')
            x=179 if self.jogo and self.jogo.dialogo and self.jogo.dialogo[0] in telas.NPC_TAM else 97
            with estilo(self.mem.prefs, self.controles):
                partes=linhas(self.controles.dicas(msg),760 if escolha else 825-x,17)
            tamanho=4 if escolha else 3
            self.fala_paginas=[' '.join(partes[i:i+tamanho]) for i in range(0,len(partes),tamanho)] or ['']
        self.fala=self.fala_paginas[0]
        self.letras=0
        self.espera=.02

    @property
    def fala_visivel(self):
        return self.fala[:self.letras]

    def escrever(self,dt):
        self.espera-=dt
        while self.espera<=0 and self.letras<len(self.fala):
            ch=self.fala[self.letras]
            self.letras+=1
            self.espera+=.17 if ch in ".!?…" else (.09 if ch in ",;" else .021)

    def avancar_fala(self):
        if self.letras<len(self.fala):
            self.letras=len(self.fala)
            return
        if self.pagina_fala<len(self.fala_paginas)-1:
            self.pagina_fala+=1;self.fala=self.fala_paginas[self.pagina_fala]
            self.letras=0;self.espera=.02
            return
        if self.estado=="prologo":
            self.quadro+=1
            if self.quadro==len(PROLOGO): self.jogar()
            else: self.nova_fala(PROLOGO[self.quadro][1])
        else:
            if self.jogo.escolha_resgate is not None:
                from src.resgates import escolher
                escolher(self.jogo,self.selecao)
                self.som('resgate')
                self.salvar_campanha()
                self.alvos=[]
                return
            self.jogo.fechar_dialogo()
            self.bordas.clear()

    def confirmar(self,motivo,titulo,msg,acao):
        self.confirmacao=motivo
        self.conf_titulo,self.conf_msg,self.conf_acao=titulo,msg,acao
        self.mudar("confirmar")

    @property
    def ajustes_da_historia(self):
        return self.anterior == "pausa" and self.ensaio is None and self.jogo is not None

    @property
    def dificuldade_escolhida(self):
        if self.ajustes_da_historia:
            return self.jogo.dificuldade_pendente or self.jogo.dificuldade
        return self.mem.prefs["dificuldade"]

    def ajustar(self,delta):
        if self.selecao in (5,6,7):
            if self.selecao == 5:
                self.aviso_tecla = ""
                self.mudar("controles")
                return
            if self.selecao == 6:
                self.mudar("acessibilidade")
                return
            self.mudar(self.anterior)
            return
        p=self.mem.prefs
        if self.selecao==0:
            escolha = DIFICULDADES[(DIFICULDADES.index(self.dificuldade_escolhida)+delta) % len(DIFICULDADES)]
            if self.ajustes_da_historia:
                j = self.jogo
                j.dificuldade_pendente = escolha if escolha != j.dificuldade else None
                self.salvar_campanha()
                self.som("clique")
                return
            p["dificuldade"] = escolha
        elif self.selecao in (1,2):
            k=("musica","efeitos")[self.selecao-1]
            p[k]=max(0,min(1,round(p[k]+delta*.1,2)))
        elif self.selecao==3:
            p["brilho"]=(p["brilho"]+delta)%4
            self.paisagem.brilho_mata=p["brilho"]
        else: p["mudo"]=not p["mudo"]
        self.ajustar_som()
        self.mem.guardar("preferencias",p)
        self.som("clique")

    def ajustar_acessibilidade(self, delta):
        p = self.mem.prefs
        if self.selecao == 0:
            escalas = (100, 115, 125)
            p["texto"] = escalas[(escalas.index(p["texto"])+delta) % len(escalas)]
        elif self.selecao == 4:
            self.mudar("ajustes")
            return
        else:
            chave = ("contraste", "claroes_suaves", "numeros_hud")[self.selecao-1]
            p[chave] = not p[chave]
        self.mem.guardar("preferencias",p)
        self.som("clique")

    def ativar(self):
        estado=self.estado
        i=self.selecao
        self.som("clique")
        if estado=='jogo' and self.jogo.dialogo:
            self.avancar_fala()
        elif estado=="menu":
            nome=self.menu_nomes()[i]
            if nome=="Jogar história": self.iniciar("historia")
            elif nome=="Nova história":
                self.confirmar("nova","Começar outra história?","O novo percurso ocupará o marco salvo desta campanha.","Começar de novo")
            elif nome=="Continuar história": self.iniciar("historia",True)
            elif nome=="Sair": self.rodando=False
            elif nome=="Campo de testes":
                self.mudar("ensaios")
                self.selecao=INDICE_ARANHA
            else:
                self.anterior="menu"
                if nome=="Créditos": self.musica("creditos")
                self.mudar({"Como jogar":"ajuda","Ajustes":"ajustes","Recordes":"recordes","Créditos":"creditos"}[nome])
        elif estado=="ensaios":
            if i==len(ENSAIOS):
                self.menu()
                return
            self.comecar_ensaio(i)
        elif estado=="pausa":
            if i==0: self.jogar()
            elif i==1: self.abrir_diario("pausa")
            elif i==2:
                self.anterior="pausa"
                self.mudar("ajustes")
            elif i==3: self.perguntar_reinicio()
            elif self.ensaio is not None:
                self.voltar_aos_ensaios()
            else: self.menu()
        elif estado=="morte":
            if self.relogio-self.morte_desde < .35:
                return
            if i==0:
                if self.ensaio is not None:
                    self.comecar_ensaio(self.ensaio,self.jogo.dificuldade)
                else:
                    esgotou = self.jogo.estado == "derrota"
                    if esgotou:
                        self.jogo.estado="caido"
                    self.jogo.reiniciar()
                    if esgotou:
                        self.jogo.lume.vidas=self.jogo.vidas_iniciais
                    self.salvar_campanha()
                    self.jogar()
            elif self.ensaio is not None: self.voltar_aos_ensaios()
            else: self.menu()
        elif estado=="confirmar":
            if i==0: self.mudar("menu" if self.confirmacao=="nova" else "pausa")
            elif self.confirmacao=="nova": self.iniciar("historia")
            elif self.ensaio is not None:
                self.comecar_ensaio(self.ensaio,self.jogo.dificuldade)
            else:
                self.jogo.reiniciar(recuperar=False)
                self.salvar_campanha()
                self.jogar()
        elif estado=="ajustes": self.ajustar(1)
        elif estado=="controles":
            if i < len(ACOES):
                self.capturando_tecla = True
                self.aviso_tecla = "Pressione a nova tecla. Esc cancela."
            elif i == len(ACOES):
                self.controles.restaurar()
                self.mem.guardar("preferencias",self.mem.prefs)
                self.aviso_tecla = "Teclas padrão restauradas."
            else:
                self.mudar("ajustes")
        elif estado=="acessibilidade": self.ajustar_acessibilidade(1)
        elif estado=="fim":
            if self.ensaio==INDICE_ARANHA:
                if i==0: self.comecar_ensaio(self.ensaio,self.jogo.dificuldade)
                else: self.voltar_aos_ensaios()
            elif i==0 and self.jogo.estado=='vitoria' and self.jogo.modo=='historia':
                self.jogo.estado='jogando'
                self.salvar_campanha();self.jogar()
                if len(self.jogo.sobreviventes) < 3:
                    aviso = "A floresta está reacesa. M aponta o próximo sinal dos sobreviventes."
                elif "jardim_plantado" not in self.jogo.cartografia:
                    aviso = "Os três voltaram. M indica o caminho até o Jardim do Último Sinal."
                else:
                    aviso = "O Jardim recebeu água. As trilhas da floresta continuam abertas."
                self.jogo.notificar(aviso, 7.)
            elif i==0 and self.jogo.estado=="derrota":
                self.iniciar(self.jogo.modo,self.jogo.modo=="historia" and bool(self.mem_camp))
            else: self.menu()
        elif estado=="registro":
            if self.resposta is None: self.resposta=i
            else: self.jogar()
        elif estado=="capitulo": self.jogar()
        elif estado in ("ajuda","creditos","recordes"): self.menu()

    def perguntar_reinicio(self):
        if self.ensaio==INDICE_ARANHA:
            self.confirmar("ensaio","Repetir o duelo?","A tentativa atual fica registrada. Lume e a aranha voltam às posições desta semente.","Repetir a semente")
        elif self.ensaio is not None:
            self.confirmar("ensaio","Repetir o ensaio?","Lume, os inimigos e os itens voltam ao estado inicial deste ensaio.","Repetir o ensaio")
        else:
            self.confirmar("marco", "Voltar ao marco?",
                           "Lume mantém vida, brilho, fagulhas e itens. Os inimigos ainda vivos se recompõem.",
                           "Voltar ao marco")

    def abrir_diario(self,origem):
        tutorial.confirmar(self.jogo,'mapa')
        self.anterior=origem
        self.pagina=0
        from .missoes import conhecidas, rastreada
        ids=[m.id for m in conhecidas(self.jogo)]
        self.pedido_cursor=ids.index(rastreada(self.jogo).id)
        self.mudar("diario")
        if not hasattr(self.jogo,'sala_id'):self.mapa_visor.preparar(self.jogo,True)
        self.som("pagina")

    def abrir_caderno(self):
        conhecidos=[i for i in range(4) if 'raiz' in self.jogo.historico.get((0,i),set())]
        if not conhecidos:
            self.jogo.notificar('O caderno ganha uma página quando você restaura uma raiz.');return
        self.registro_etapa=self.jogo.etapa if self.jogo.etapa in conhecidos else conhecidos[-1]
        self.resposta=None;self.mudar('registro')

    def evento(self,e):
        if e.type == pygame.MOUSEBUTTONDOWN and not self.tela.get_rect().collidepoint(e.pos):
            return
        if e.type==pygame.QUIT:
            self.rodando=False
            return
        if e.type==pygame.WINDOWFOCUSLOST:
            self.gamepad.limpar()
            self.bordas.clear()
            if self.estado=="jogo" and not self.jogo.dialogo:
                self.mudar("pausa")
            return
        if e.type in EVENTOS_PAD:
            codigo = self.gamepad.evento(e)
            if e.type == pygame.CONTROLLERDEVICEREMOVED:
                self.bordas.clear()
                self.controles.ultimo_pad = bool(self.gamepad.dispositivos)
            if codigo is not None:
                self.controles.ultimo_pad = True
                codigo = self.tecla_do_pad(codigo, e)
                if codigo is not None:
                    self.evento(pygame.event.Event(pygame.KEYDOWN, key=codigo, do_pad=True))
            return
        if e.type == pygame.KEYDOWN and self.capturando_tecla and not getattr(e,"repeat",False):
            if e.key == pygame.K_ESCAPE:
                self.capturando_tecla = False
                self.aviso_tecla = ""
            elif not getattr(e,"do_pad",False):
                acao = tuple(ACOES)[self.selecao]
                self.aviso_tecla = self.controles.trocar(acao, e.key)
                if not self.aviso_tecla:
                    self.capturando_tecla = False
                    self.mem.guardar("preferencias",self.mem.prefs)
            return
        if self.capturando_tecla:
            return
        if e.type == pygame.KEYDOWN and not getattr(e,"repeat",False) and self.estado=="diario":
            pad = getattr(e,"do_pad",False)
            if (pad and e.key==pygame.K_m) or (not pad and e.key in self.controles.codigos("mapa")):
                self.controles.ultimo_pad = pad
                self.mudar(self.anterior)
                return
        if mapa_visor.evento(self,e):return
        if e.type in (pygame.MOUSEMOTION,pygame.MOUSEBUTTONDOWN):
            if e.type==pygame.MOUSEBUTTONDOWN and e.button!=1: return
            if e.type==pygame.MOUSEBUTTONDOWN and self.estado=="ensaios" and self.selecao==INDICE_ARANHA:
                if telas.SEMENTE_ANTERIOR.collidepoint(e.pos) or telas.SEMENTE_SEGUINTE.collidepoint(e.pos):
                    self.ajustar_semente(-1 if telas.SEMENTE_ANTERIOR.collidepoint(e.pos) else 1)
                    return
                if self.ultimo_replay is not None and telas.VER_TENTATIVA.collidepoint(e.pos):
                    self.assistir_tentativa(self.ultimo_replay)
                    return
            for i,r in enumerate(self.alvos):
                if r.collidepoint(e.pos):
                    self.selecao=i
                    if e.type==pygame.MOUSEBUTTONDOWN: self.ativar()
                    return
            if e.type==pygame.MOUSEBUTTONDOWN:
                if self.estado=="prologo" or (self.estado=="jogo" and self.jogo.dialogo): self.avancar_fala()
                elif self.estado in ("capitulo","ajuda","creditos","recordes") or self.estado=="registro" and self.resposta is not None:
                    self.ativar()
            return
        if e.type!=pygame.KEYDOWN or getattr(e,"repeat",False): return
        k=e.key
        pad = getattr(e,"do_pad",False)
        if not pad:
            self.controles.ultimo_pad = False
        if k==pygame.K_F11:
            self.cheia=not self.cheia
            self.janela.tela_cheia(self.cheia)
            return
        if k==pygame.K_F10:
            self.mem.prefs["mudo"]=not self.mem.prefs["mudo"]
            self.ajustar_som()
            self.mem.guardar("preferencias",self.mem.prefs)
            return
        est=self.estado
        if est=="replay":
            if k==pygame.K_ESCAPE: self.voltar_aos_ensaios()
            elif k==pygame.K_SPACE: self.replay_pausado=not self.replay_pausado
        elif est=="ensaios" and self.selecao==INDICE_ARANHA and k in (pygame.K_LEFT,pygame.K_RIGHT):
            self.ajustar_semente(-1 if k==pygame.K_LEFT else 1)
        elif est=="ensaios" and self.selecao==INDICE_ARANHA and k==pygame.K_v:
            if self.ultimo_replay is not None: self.assistir_tentativa(self.ultimo_replay)
        elif est=="prologo":
            if k==pygame.K_ESCAPE: self.jogar()
            elif k in ACEITAR: self.avancar_fala()
        elif est=="jogo":
            tecla = k if pad else PADRAO.get(self.controles.indice.get(k))
            if self.jogo.dialogo:
                if self.jogo.escolha_resgate is not None and k==pygame.K_ESCAPE:
                    self.jogo.fechar_dialogo();self.alvos=[]
                elif self.jogo.escolha_resgate is not None and k in (pygame.K_UP,pygame.K_DOWN):
                    self.selecao=(self.selecao+1)%2
                elif k in (*ACEITAR,pygame.K_ESCAPE) or tecla == pygame.K_e: self.avancar_fala()
            elif k in (pygame.K_ESCAPE,pygame.K_p): self.mudar("pausa")
            elif tecla==pygame.K_m: self.abrir_diario("jogo")
            elif (tecla==pygame.K_c or pad and k==pygame.K_UP) and self.jogo.modo=='historia':self.abrir_caderno()
            elif tecla==pygame.K_v and self.jogo.agulha_disponivel:
                if self.jogo.trocar_arma():
                    tutorial.confirmar(self.jogo,'agulha')
                    self.som('pagina')
                    self.salvar_campanha()
            elif tecla==pygame.K_q:
                if self.gravacao: self.gravacao.acao(self.jogo,"trocar_item")
                else: self.jogo.trocar_item()
                self.som("pagina")
            elif tecla==pygame.K_f:
                resultado=self.gravacao.acao(self.jogo,"usar_item") if self.gravacao else self.jogo.usar_item()
                if resultado:
                    tutorial.confirmar(self.jogo,'bolsa')
                self.som(resultado or "navegar")
            elif tecla is not None: self.bordas.add(tecla)
        elif est=="diario":
            if self.pagina==1:
                from .missoes import conhecidas, selecionar
                lista=conhecidas(self.jogo)
                self.pedido_cursor%=len(lista)
                if k in (pygame.K_UP,pygame.K_DOWN,pygame.K_w,pygame.K_s):
                    self.pedido_cursor=(self.pedido_cursor+(-1 if k in (pygame.K_UP,pygame.K_w) else 1))%len(lista)
                    self.som("pagina")
                    return
                if k in (pygame.K_r,pygame.K_RETURN):
                    if selecionar(self.jogo,lista[self.pedido_cursor].id):
                        self.pagina=0
                    return
            if k==pygame.K_r:
                self.jogo.missao="secundaria" if self.jogo.missao=="principal" else "principal"
                self.jogo.notificar("Rastreando missão "+self.jogo.missao)
                return
            if k==pygame.K_ESCAPE:
                self.mudar(self.anterior)
            elif k in (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_a,pygame.K_d):
                self.pagina=(self.pagina+(-1 if k in (pygame.K_LEFT,pygame.K_a) else 1))%telas.paginas_diario(self)
                self.mapa_visor.arrastando=False
                self.som("pagina")
        elif est=="pausa" and k in (pygame.K_ESCAPE,pygame.K_p): self.jogar()
        elif est=='registro' and k in (pygame.K_LEFT,pygame.K_RIGHT):
            conhecidos=[i for i in range(4) if 'raiz' in self.jogo.historico.get((0,i),set())]
            if conhecidos:
                atual=conhecidos.index(self.registro_etapa) if self.registro_etapa in conhecidos else 0
                self.registro_etapa=conhecidos[(atual+(-1 if k==pygame.K_LEFT else 1))%len(conhecidos)]
                self.resposta=None;self.selecao=0
        elif est=="pausa" and k==pygame.K_r: self.perguntar_reinicio()
        elif k==pygame.K_ESCAPE:
            if est in ("registro","capitulo"): self.jogar()
            elif est=="ajustes": self.mudar(self.anterior)
            elif est in ("controles","acessibilidade"): self.mudar("ajustes")
            elif est=="confirmar": self.mudar("menu" if self.confirmacao=="nova" else "pausa")
            elif est=="morte": return
            elif est=="menu": self.rodando=False
            else: self.menu()
        elif est=="ajustes" and k in (pygame.K_LEFT,pygame.K_RIGHT): self.ajustar(1 if k==pygame.K_RIGHT else -1)
        elif est=="acessibilidade" and k in (pygame.K_LEFT,pygame.K_RIGHT): self.ajustar_acessibilidade(1 if k==pygame.K_RIGHT else -1)
        elif k in ACEITAR: self.ativar()
        elif k in (pygame.K_UP,pygame.K_DOWN,pygame.K_w,pygame.K_s):
            quant={"menu":len(self.menu_nomes()),"pausa":5,"ajustes":8,"controles":len(ACOES)+2,"acessibilidade":5,
                   "confirmar":2,"morte":2,"ensaios":len(ENSAIOS)+1,
                   "fim":len(self.fim_nomes()) if est=="fim" else 0,"registro":3}.get(est,0)
            if quant:
                self.selecao=(self.selecao+(-1 if k in (pygame.K_UP,pygame.K_w) else 1))%quant
                self.som("navegar")

    def tecla_do_pad(self, codigo, evento):
        if self.estado == "jogo" and not self.jogo.dialogo:
            if codigo == pygame.K_UP and evento.type == pygame.CONTROLLERAXISMOTION:
                return None
            return {pygame.K_LEFT:pygame.K_a, pygame.K_RIGHT:pygame.K_d}.get(codigo,codigo)
        if self.estado == "diario":
            if evento.type == pygame.CONTROLLERAXISMOTION and self.pagina != 1:
                return {pygame.K_LEFT:pygame.K_a, pygame.K_RIGHT:pygame.K_d,
                        pygame.K_UP:pygame.K_w, pygame.K_DOWN:pygame.K_s}.get(codigo)
            especiais = {pygame.K_k:pygame.K_EQUALS, pygame.K_LCTRL:pygame.K_MINUS,
                         pygame.K_v:pygame.K_c, pygame.K_m:pygame.K_m}
            if codigo in especiais:
                return especiais[codigo]
        confirmar = pygame.K_SPACE if self.estado == "replay" else pygame.K_RETURN
        return {pygame.K_SPACE:confirmar, pygame.K_LSHIFT:pygame.K_ESCAPE,
                pygame.K_e:pygame.K_RETURN, pygame.K_LEFT:pygame.K_LEFT, pygame.K_RIGHT:pygame.K_RIGHT,
                pygame.K_UP:pygame.K_UP, pygame.K_DOWN:pygame.K_DOWN, pygame.K_ESCAPE:pygame.K_ESCAPE,
                pygame.K_j:pygame.K_r if self.estado=="pausa" else None}.get(codigo)

    def ajustar_semente(self,delta):
        self.semente_aranha=(self.semente_aranha+delta)%1000000
        self.som("navegar")

    def atualizar(self,dt,presso=None):
        self.relogio+=dt
        if self.estado=="replay":
            self.avancar_replay(dt)
            self.mix(dt)
            return
        if self.estado=="prologo" or self.estado=="jogo" and self.jogo.dialogo:
            self.escrever(dt)
        if self.estado=="jogo" and self.impacto_restante>0:
            # A fila de KEYDOWN permanece intacta durante o breve impacto.
            self.impacto_restante=max(0.,self.impacto_restante-dt)
            self.mix(dt)
            return
        if self.estado=="jogo" and not self.jogo.dialogo:
            teclas=pygame.key.get_pressed() if presso is None else presso
            controle=self.gamepad.seguras
            def segura(acao, alternativa=None):
                return (PADRAO[acao] in controle or alternativa in controle
                        or any(teclas[k] for k in self.controles.codigos(acao)))
            mover=int(segura("direita",pygame.K_RIGHT))-int(segura("esquerda",pygame.K_LEFT))
            pedir_deslize=pygame.K_LSHIFT in self.bordas or (
                segura("deslize") and bool(self.bordas.intersection((pygame.K_a,pygame.K_d))))
            from .travessia_fagulha import disponivel
            combo_fagulha = (self.controles.ultimo_pad and pygame.K_LCTRL in controle
                             and pygame.K_k in self.bordas and disponivel(self.jogo))
            cmd=Comando(mover,segura("baixo",pygame.K_DOWN),pygame.K_SPACE in self.bordas,
                        segura("salto"),pedir_deslize,
                        pygame.K_j in self.bordas,pygame.K_k in self.bordas and not combo_fagulha,pygame.K_e in self.bordas,
                        pygame.K_l in self.bordas,segura("carga") and not combo_fagulha,
                        fagulha=pygame.K_g in self.bordas or combo_fagulha)
            self.bordas.clear()
            j=self.jogo
            etapa,raizes,dificuldade=j.etapa,j.restauradas,j.dificuldade
            if self.gravacao: self.gravacao.avancar(j,dt,cmd)
            else: j.update(dt,cmd)
            self.marcar_impacto(j)
            self.sons_da_jornada(j,dt)
            if j.dialogo: self.nova_fala(j.dialogo[1])
            if j.estado in ("caido","derrota") and j.motivo_morte:
                self.fechar_tentativa("morte")
                self.morte_desde=self.relogio
                if j.estado=="derrota" and self.ensaio is None:
                    self.registrar_resultado()
                else: self.salvar_campanha()
                self.mudar("morte")
                self.musica("derrota")
            elif j.estado!="jogando":
                self.fechar_tentativa(j.estado)
                if self.ensaio is None:
                    self.registrar_resultado()
                self.mudar("fim")
                self.musica(j.estado)
            elif raizes<j.restauradas and j.modo=="historia":
                self.registro_etapa=j.etapa
                m=ambiental.MENSAGENS[j.etapa]
                j.memorizar(m["fase"],m["mensagem"])
                self.resposta=None
                j.notificar(EFEITOS_RAIZ[j.etapa] + ' C abre o registro da raiz.', 6.)
                self.salvar_campanha()
            elif j.etapa!=etapa:
                self.musica(CORES_AUDIO[j.etapa])
                if j.modo=="historia": self.mudar("capitulo")
                self.salvar_campanha()
            else: self.salvar_campanha(j.dificuldade != dificuldade)
        self.mix(dt)

    def marcar_impacto(self,j):
        if j.estado=="jogando" and any(ev in ("acerto","abatido","rebote") for ev in j.eventos):
            self.impacto_restante=PAUSA_NO_ACERTO

    def sons_da_jornada(self,j,dt):
        for ev in dict.fromkeys(j.eventos):
            if ev=="aviso" and j.boss:
                ev=j.boss.som_aviso
                if not self.audio.tocar_local(ev,j.boss.x,j.lume.rect.centerx):
                    self.audio.tocar(ev,aviso_de_chefe=True)
                continue
            self.som(ev)
        for nome,x in j.sons_espaciais:
            self.audio.tocar_local(nome,x,j.lume.rect.centerx)
        self.passo_som-=dt
        if j.lume.pose in ("andar","correr") and self.passo_som<=0:
            self.som("passo")
            self.passo_som=.34

    def tema_jornada(self):
        j=self.jogo
        if j.boss and not j.boss.vencido:
            return "chefe_final" if j.boss.coro_iniciado else f"chefe_{j.boss.indice}"
        if j.minichefe is not None:
            return "chefe_caruncho"
        if j.em_vertical and j.lume.rect.centerx>=2432:
            return "jardim"
        return "retorno" if j.concluida else CORES_AUDIO[j.etapa]

    def mix(self,dt):
        j=self.jogo
        ativo=(self.estado=="jogo" or self.estado=="replay" and self.reproducao is not None
               and not self.replay_pausado) and j and not j.dialogo
        if ativo:
            self.musica(self.tema_jornada())
        self.audio.ambiente(combate=bool(ativo and j.combate),
                           energia=j.lume.vida if ativo else 100,
                           raizes=j.restauradas if j else 0,suspenso=not ativo)
        self.audio.atualizar(dt)

    def desenhar(self):
        with estilo(self.mem.prefs, self.controles):
            self.desenhar_tela()

    def desenhar_tela(self):
        s=self.tela
        if self.estado in ("jogo","pausa","morte","replay"):
            j=self.jogo
            self.paisagem.desenhar(s,j,j.tempo)
            if self.estado=="morte":
                telas.morte(self,s)
                return
            from src.abertura_bosque import em_cena
            if self.estado!="pausa" or not em_cena(j):
                hud(s,j)
            if self.estado=="replay": telas.replay(self,s)
            if j.dialogo: telas.dialogo(self,s)
            if self.estado=="pausa": telas.pausa(self,s)
            return
        renderer={"menu":telas.menu,"prologo":telas.cena,"ajuda":telas.ajuda,"creditos":telas.creditos,
                  "ensaios":telas.ensaios,"confirmar":telas.confirmar,"ajustes":telas.opcoes_ajustes,"capitulo":telas.capitulo,
                  "registro":telas.registro,"fim":telas.fim,"recordes":telas.recordes,"diario":telas.diario,
                  "controles":telas.remapeamento,"acessibilidade":telas.acessibilidade}
        renderer[self.estado](self,s)

    def rodar(self):
        clock=pygame.time.Clock()
        try:
            while self.rodando:
                dt=min(.07,clock.tick(60)/1000)
                for e in pygame.event.get(): self.evento(self.janela.evento_logico(e))
                if not self.rodando: break
                self.atualizar(dt)
                self.desenhar()
                self.janela.apresentar(self.quadro_renderizado)
        finally:
            self.fechar_tentativa("janela")
            self.salvar_campanha()
            self.mem.db.close()
            self.janela.fechar()
            pygame.quit()

def principal():
    parser=argparse.ArgumentParser()
    modo=parser.add_mutually_exclusive_group()
    modo.add_argument("--smoke",action="store_true",help="Verifica menu, início e desenho do jogo e encerra.")
    modo.add_argument("--reproduzir",type=Path,metavar="TENTATIVA.json",help="Assistir a uma tentativa local da aranha.")
    parser.add_argument("--captura",type=Path)
    args=parser.parse_args()
    try:
        dados=ler_tentativa(args.reproduzir) if args.reproduzir is not None else None
    except (ValueError,OSError) as erro:
        parser.error(str(erro))
    app=App(temporaria=args.smoke)
    if dados is not None:
        app.ultimo_replay=dados
        app.assistir_tentativa(dados)
    if not args.smoke:
        app.rodar()
        return
    app.desenhar()
    app.iniciar("historia")
    app.jogar()
    for n in range(15):
        app.atualizar(1/60)
        app.desenhar()
        app.janela.apresentar(app.quadro_renderizado)
    if args.captura: pygame.image.save(app.quadro_renderizado,str(args.captura))
    print("Miopia OK · menu, recursos e Bosque em 1920 × 1080")
    app.mem.db.close()
    app.janela.fechar()
    pygame.quit()

if __name__=="__main__":
    principal()
