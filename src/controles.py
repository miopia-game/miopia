"""Vínculos do teclado e entrada SDL normalizados para as ações da partida."""
import re
from collections import Counter

import pygame as pg
from pygame._sdl2 import controller


ACOES = {
    "esquerda": ("Andar à esquerda", pg.K_a, (pg.K_LEFT,)),
    "direita": ("Andar à direita", pg.K_d, (pg.K_RIGHT,)),
    "baixo": ("Agachar / descer", pg.K_s, (pg.K_DOWN,)),
    "salto": ("Saltar / planar", pg.K_SPACE, ()),
    "deslize": ("Deslizar", pg.K_LSHIFT, ()),
    "golpe": ("Corte rápido", pg.K_j, ()),
    "forte": ("Corte pesado", pg.K_l, ()),
    "luz": ("Clarão", pg.K_k, ()),
    "interagir": ("Interagir", pg.K_e, ()),
    "carga": ("Carregar golpe de luz", pg.K_LCTRL, ()),
    "mapa": ("Abrir / fechar mapa", pg.K_m, (pg.K_TAB,)),
    "bolsa": ("Trocar item", pg.K_q, ()),
    "usar": ("Usar item", pg.K_f, ()),
    "arma": ("Trocar arma", pg.K_v, ()),
    "caderno": ("Abrir registro", pg.K_c, ()),
    "fagulha": ("Lançar fagulha", pg.K_g, ()),
}
PADRAO = {acao: info[1] for acao, info in ACOES.items()}
FIXAS = {pg.K_ESCAPE, pg.K_RETURN, pg.K_KP_ENTER, pg.K_UP, pg.K_p, pg.K_r, pg.K_F10, pg.K_F11}
ALIAS_MODIFICADORES = {"carga": pg.K_RCTRL, "deslize": pg.K_RSHIFT}


def nome_tecla(codigo):
    especiais = {pg.K_SPACE: "Espaço", pg.K_LCTRL: "Ctrl", pg.K_LSHIFT: "Shift",
                 pg.K_LEFT: "Esq.", pg.K_RIGHT: "Dir.", pg.K_DOWN: "Baixo", pg.K_TAB: "Tab"}
    return especiais.get(codigo, pg.key.name(codigo).upper())


def valida(acao, codigo):
    return type(codigo) is int and (codigo == PADRAO[acao] or
        pg.K_a <= codigo <= pg.K_z or pg.K_0 <= codigo <= pg.K_9 or pg.K_F1 <= codigo <= pg.K_F9)


def carregar(dados):
    if not isinstance(dados, dict):
        return {}
    remap = {p: k for p, k in dados.items() if p in ACOES and valida(p, k)
             and k not in FIXAS and k != PADRAO[p]}
    # G era livre na S40. Preserve a ação anterior de quem já usava essa tecla.
    if "fagulha" not in dados and list(remap.values()).count(pg.K_g) == 1:
        ocupadas = FIXAS.union(PADRAO.values(), remap.values())
        candidatas = (pg.K_h, *range(pg.K_a, pg.K_z + 1), *range(pg.K_0, pg.K_9 + 1))
        remap["fagulha"] = next(tecla for tecla in candidatas if tecla not in ocupadas)
    # Voltar ao padrão pode reocupar uma tecla usada em outro vínculo.
    while remap:
        donos = Counter(({**PADRAO, **remap}).values())
        livres = {p: k for p, k in remap.items() if donos[k] == 1}
        if len(livres) == len(remap):
            break
        remap = livres
    return remap


ROTULOS_PAD = dict(zip(ACOES, ("Esq.", "Dir.", "Baixo", "A", "B", "X", "Y", "RB",
                              "RT", "LB", "View", "L3", "LT", "R3", "Cima", "LB + RB")))
MARCAS = {"A / D": ("esquerda", "direita"), "A D": ("esquerda", "direita"),
          "M / Tab": ("mapa",), "M ou Tab": ("mapa",), "Shift": ("deslize",),
          "Ctrl": ("carga",), "Espaço": ("salto",), "G": ("fagulha",),
          **{chave: (acao,) for chave, acao in zip("SJL KEMQFVC".replace(" ", ""),
                ("baixo","golpe","forte","luz","interagir","mapa","bolsa","usar","arma","caderno"))}}
EXPRESSAO = re.compile(r"(?<!\w)(" + "|".join(re.escape(s) for s in MARCAS) + r")(?!\w)")


class Controles:
    def __init__(self, teclas):
        self.teclas = teclas
        self.ultimo_pad = False
        self.reindexar()

    def codigos(self, acao):
        _, padrao, aliases = ACOES[acao]
        principal = self.teclas.get(acao, padrao)
        if principal == padrao and acao in ALIAS_MODIFICADORES:
            aliases = (*aliases, ALIAS_MODIFICADORES[acao])
        return (principal, *aliases)

    def reindexar(self):
        self.indice = {k: p for p in ACOES for k in self.codigos(p)}

    def trocar(self, acao, codigo):
        outro = self.indice.get(codigo)
        if codigo in FIXAS:
            return "Essa tecla é reservada para os menus."
        if outro and outro != acao:
            return "Tecla ocupada por " + ACOES[outro][0].lower() + "."
        if not valida(acao, codigo):
            return "Escolha uma letra, um número ou F1 a F9."
        if codigo == PADRAO[acao]:
            self.teclas.pop(acao, None)
        else:
            self.teclas[acao] = codigo
        self.reindexar()
        return ""

    def restaurar(self):
        self.teclas.clear()
        self.reindexar()

    def dicas(self, mensagem):
        if not self.ultimo_pad and not self.teclas:
            return mensagem

        def substituir(m):
            acoes = MARCAS[m[0]]
            if self.ultimo_pad:
                return " / ".join(ROTULOS_PAD[p] for p in acoes)
            if not any(p in self.teclas for p in acoes):
                return m[0]
            return " / ".join(nome_tecla(self.codigos(p)[0]) for p in acoes)

        return EXPRESSAO.sub(substituir, mensagem)


BOTOES = {
    pg.CONTROLLER_BUTTON_A: pg.K_SPACE, pg.CONTROLLER_BUTTON_B: pg.K_LSHIFT,
    pg.CONTROLLER_BUTTON_X: pg.K_j, pg.CONTROLLER_BUTTON_Y: pg.K_l,
    pg.CONTROLLER_BUTTON_LEFTSHOULDER: pg.K_LCTRL, pg.CONTROLLER_BUTTON_RIGHTSHOULDER: pg.K_k,
    pg.CONTROLLER_BUTTON_BACK: pg.K_m, pg.CONTROLLER_BUTTON_START: pg.K_ESCAPE,
    pg.CONTROLLER_BUTTON_LEFTSTICK: pg.K_q, pg.CONTROLLER_BUTTON_RIGHTSTICK: pg.K_v,
    pg.CONTROLLER_BUTTON_DPAD_LEFT: pg.K_LEFT, pg.CONTROLLER_BUTTON_DPAD_RIGHT: pg.K_RIGHT,
    pg.CONTROLLER_BUTTON_DPAD_UP: pg.K_UP, pg.CONTROLLER_BUTTON_DPAD_DOWN: pg.K_DOWN,
}
EIXOS = {pg.CONTROLLER_AXIS_LEFTX: (pg.K_LEFT, pg.K_RIGHT),
         pg.CONTROLLER_AXIS_LEFTY: (pg.K_UP, pg.K_DOWN),
         pg.CONTROLLER_AXIS_TRIGGERLEFT: (None, pg.K_f), pg.CONTROLLER_AXIS_TRIGGERRIGHT: (None, pg.K_e)}
EVENTOS_PAD = (pg.CONTROLLERDEVICEADDED, pg.CONTROLLERDEVICEREMOVED,
               pg.CONTROLLERBUTTONDOWN, pg.CONTROLLERBUTTONUP, pg.CONTROLLERAXISMOTION)


class Gamepad:
    def __init__(self):
        self.dispositivos = {}
        self.press = {}
        try:
            controller.init()
            for numero in range(controller.get_count()):
                self.conectar(numero)
        except pg.error:
            pass

    def conectar(self, numero):
        try:
            if controller.is_controller(numero):
                dispositivo = controller.Controller(numero)
                self.dispositivos[dispositivo.id] = dispositivo
        except pg.error:
            pass

    def limpar(self):
        self.press.clear()

    @property
    def seguras(self):
        return set(self.press.values())

    def evento(self, e):
        qual = getattr(e, "instance_id", getattr(e, "which", 0))
        if e.type == pg.CONTROLLERDEVICEADDED:
            self.conectar(getattr(e, "device_index", qual))
            return None
        if e.type == pg.CONTROLLERDEVICEREMOVED:
            aparelho = self.dispositivos.pop(qual, None)
            if aparelho:
                aparelho.quit()
            self.press = {chave: v for chave, v in self.press.items() if chave[0] != qual}
            return None
        if e.type == pg.CONTROLLERAXISMOTION:
            if e.axis not in EIXOS:
                return None
            chave = (qual, "eixo", e.axis)
            # Limiar diferente ao soltar evita ativações na borda da zona morta.
            limite = 10500 if chave in self.press else 16000
            pos = -1 if e.value < -limite else 1 if e.value > limite else 0
            codigo = EIXOS[e.axis][int(pos > 0)] if pos else None
        else:
            chave = (qual, "botao", e.button)
            codigo = BOTOES.get(e.button) if e.type == pg.CONTROLLERBUTTONDOWN else None
        anterior = self.press.pop(chave, None)
        if codigo is not None:
            self.press[chave] = codigo
        return codigo if codigo != anterior else None
