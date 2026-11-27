"""Apresenta um quadro Full HD e leva o ponteiro até as coordenadas da partida."""
from math import floor

import pygame
from pygame._sdl2.video import Renderer, Texture

QUADRO = (1920, 1080)
LOGICA = (960, 540)
TITULO = "Miopia · A última luz da mata"
PONTEIRO = (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL)


def area_de_jogo(tamanho):
    """Centraliza a imagem preservando a proporção e limita a ampliação em telas 4K."""
    largura, altura = tamanho
    escala = min(1., largura / QUADRO[0], altura / QUADRO[1])
    area = pygame.Rect(0, 0, max(1, round(QUADRO[0]*escala)), max(1, round(QUADRO[1]*escala)))
    area.center = (largura//2, altura//2)
    return area


class Janela:
    def __init__(self, icone):
        self.cheia = False
        self.nativa = self.renderer = self.textura = None
        self._visivel = None
        self._apresentou_sem_foco = False
        driver = pygame.display.get_driver()
        if driver == 'dummy':
            # O piloto usa a mesma superfície Full HD com o driver de software.
            self.quadro = pygame.display.set_mode(QUADRO)
            pygame.display.set_caption(TITULO)
            pygame.display.set_icon(icone)
            return
        self.nativa = pygame.Window(TITULO, size=LOGICA, hidden=True, resizable=True,
                                    allow_high_dpi=True)
        try:
            if driver == "cocoa" and self.nativa.handle:
                from .visibilidade_macos import janela_visivel
                self._visivel = janela_visivel
            self.renderer = Renderer(self.nativa, vsync=False)
            self.renderer.draw_color = (0, 0, 0, 255)
            self.textura = Texture(self.renderer, QUADRO, streaming=True, scale_quality=1)
            self.quadro = pygame.Surface(QUADRO, depth=32)
            self.nativa.set_icon(icone)
            # O SDL mede a janela em pontos e o viewport do renderer em pixels físicos.
            pixels = self.renderer.get_viewport().size
            desktop = pygame.display.get_desktop_sizes()[0]
            alvo = tuple(round(q*u/max(1,p)) for q,u,p in zip(QUADRO,self.nativa.size,pixels))
            # Em monitores menores toda a partida deve caber na área útil da janela.
            cabe_no_painel = all(v <= limite for v,limite in zip(alvo,desktop))
            usa_toda_altura = cabe_no_painel and alvo[1] > desktop[1]-54
            if cabe_no_painel:
                self.nativa.borderless = usa_toda_altura
                self.nativa.size = alvo
                self.nativa.minimum_size = alvo
            else:
                fator = min(desktop[0]/alvo[0], max(1,desktop[1]-54)/alvo[1])
                self.nativa.size = tuple(max(1,round(v*fator)) for v in alvo)
            self.nativa.position = pygame.WINDOWPOS_CENTERED, pygame.WINDOWPOS_CENTERED
            self.nativa.show()
            if usa_toda_altura:
                # A moldura consumiria pixels num monitor de exatamente 1080 linhas.
                self.tela_cheia(True)
        except BaseException:
            self.fechar()
            raise

    def apresentar(self, quadro):
        """Retorna se o quadro foi enviado à saída de vídeo."""
        if quadro.get_size() != QUADRO:
            raise ValueError(f"O quadro de apresentação deve medir {QUADRO}.")
        if self.renderer is None:
            if quadro is not self.quadro:
                self.quadro.blit(quadro,(0,0))
            pygame.display.flip()
            return True
        if self._visivel is not None:
            if not self._visivel(self.nativa.handle):
                self._apresentou_sem_foco = False
                return False
            # Ao sair da Mesa, o Cocoa perde o foco antes de notificar a oclusão.
            # Entrega a pausa uma vez e evita esperar pelo compositor na transição.
            sem_foco = not self.nativa.focused
            if sem_foco and self._apresentou_sem_foco:
                return False
            self._apresentou_sem_foco = sem_foco
        self.textura.update(quadro)
        self.renderer.clear()
        self.textura.draw(dstrect=area_de_jogo(self.renderer.get_viewport().size))
        self.renderer.present()
        return True

    def tela_cheia(self, ativa):
        self.cheia = ativa
        if self.nativa is None:
            return
        if ativa:
            self.nativa.set_fullscreen(desktop=True)
        else:
            self.nativa.set_windowed()

    def _posicao_logica(self, posicao):
        if self.nativa is None:
            tamanho_janela = tamanho_saida = QUADRO
        else:
            tamanho_janela = self.nativa.size
            tamanho_saida = self.renderer.get_viewport().size
        area = area_de_jogo(tamanho_saida)
        x = posicao[0]*tamanho_saida[0]/max(1,tamanho_janela[0])
        y = posicao[1]*tamanho_saida[1]/max(1,tamanho_janela[1])
        # Pontos nas barras ficam fora da área interativa da partida.
        return floor((x-area.x)*LOGICA[0]/area.w), floor((y-area.y)*LOGICA[1]/area.h)

    def evento_logico(self, e):
        if e.type == pygame.WINDOWCLOSE:
            return pygame.event.Event(pygame.QUIT)
        if e.type not in PONTEIRO:
            return e
        valores = e.dict.copy()
        if valores.get('pos') is not None:
            pos = valores['pos']
        elif 'mouse_x' in valores and 'mouse_y' in valores:
            pos = (valores['mouse_x'], valores['mouse_y'])
        else:
            pos = pygame.mouse.get_pos()
        x, y = valores['pos'] = self._posicao_logica(pos)
        if 'rel' in valores:
            dx, dy = valores['rel']
            anterior = self._posicao_logica((pos[0]-dx,pos[1]-dy))
            valores['rel'] = (x-anterior[0],y-anterior[1])
        return pygame.event.Event(e.type, valores)

    def fechar(self):
        # As texturas SDL devem ser liberadas antes da janela que contém o renderer.
        self.textura = self.renderer = None
        if self.nativa is not None:
            self.nativa.destroy()
            self.nativa = None
