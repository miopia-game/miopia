"""Grava e confere tentativas locais da Galeria da Seda. Uso: python -m src.replay_aranha ARQUIVO."""
import argparse
from copy import deepcopy
from dataclasses import fields
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile

from .ensaios import INDICE_ARANHA, SALA_ARANHA, preparar_ensaio
from .memoria import pasta_dados
from .travessia import Comando, NIVEIS

ESQUEMA = 1
SIMULACAO = "s09-aranha-1"
MAX_PASSOS = 18_000
MAX_ARQUIVOS = 32
MAX_BYTES = 8 * 1024 * 1024
ACOES = ("trocar_item", "usar_item")
TECLAS = tuple(campo.name for campo in fields(Comando))


class HistoricoCheio(OSError):
    """Os arquivos existentes são preservados até que o jogador libere um slot."""


@lru_cache(maxsize=1)
def assinatura():
    """A identidade das regras independe das opções de som e do desenho da sala."""
    digest = hashlib.sha256()
    for nome in ("ensaios", "sala_aranha", "travessia", "combate", "fases", "visao", "narrativa", "subsolo", "descoberta", "missoes", "taticas", "ferramentas",'recursos','raizes_bosque','resgates','jardim','ultimo_chamado','marcas_mapa','luzes_mundo','encontros','tutorial','sinalizacao','arquivo_casca','fio_corte','fauna_jardim','vento_taquaral','galeria_taquaral','aula_sino',
                 "corrego_historia", "rotas_borda", "corte_vertical", "travessia_fagulha", "desvios_fagulha", "licao_vespera", "chefes", "casco", "coruja", "ninhada", "nicho_taquaral"):
        digest.update(nome.encode("ascii"))
        digest.update(Path(__file__).with_name(nome + ".py").read_bytes())
    return digest.hexdigest()


def ponto(xy):
    return [round(float(n), 4) for n in xy]


def estado(j):
    e, l = j.inimigos[0], j.lume
    return {
        "tempo": round(j.tempo, 6), "estado": j.estado,
        "lume": ponto(l.rect.center), "velocidade": ponto((l.vx, l.vy)),
        "energia": round(l.energia, 4), 'vida':round(l.vida,4), "vidas": l.vidas, "bolsa": j.bolsa.salvar(j.tempo),
        "aranha": ponto(e.rect.center), "vida_aranha": e.vida, "fase_aranha": e.estado,
        "decisoes": e.sequencia, "tecnica": e.tecnica,
        "projeteis": [ponto(projetil.pos) for projetil in e.projeteis],
    }


def comando_curto(cmd):
    # O teclado pode entregar 0/1 em vez de bool. O arquivo usa sempre booleanos.
    return {k: int(cmd.mover) if k == "mover" else True for k in TECLAS if getattr(cmd, k)}


class GravacaoAranha:
    def __init__(self, jogo):
        if getattr(jogo, "sala_id", None) != SALA_ARANHA:
            raise ValueError("A gravação requer o ensaio da aranha.")
        self.semente = jogo.semente
        self.dificuldade = jogo.dificuldade
        self.assinatura = assinatura()
        self.inicio = estado(jogo)
        self.entradas = []
        self.eventos = []
        self.quadro = self.operacoes = 0
        self.primeiro_impacto = None
        self.fim_limite = None

    def _reservar(self, jogo):
        if self.operacoes < MAX_PASSOS:
            self.operacoes += 1
            return True
        # Guarda o último estado reproduzível e deixa o duelo real continuar.
        if self.fim_limite is None:
            self.fim_limite = estado(jogo)
        return False

    def _evento(self, jogo, tipo, **detalhes):
        ev = {"quadro": self.quadro, "tempo": round(jogo.tempo, 6), "tipo": tipo, **detalhes}
        self.eventos.append(ev)
        return ev

    def avancar(self, jogo, dt, cmd):
        if not math.isfinite(dt):
            raise ValueError("O passo de simulação requer um tempo finito.")
        dt = min(.1, dt)  # Mesmo limite de Jornada.update para chamadas fora da interface.
        if dt <= 0 or not self._reservar(jogo):
            jogo.update(dt, cmd)
            return
        teclas = comando_curto(cmd)
        ultimo = self.entradas[-1] if self.entradas else {}
        if ultimo.get("dt") == dt and ultimo.get("comando") == teclas:
            ultimo["vezes"] += 1
        else:
            self.entradas.append({"dt": dt, "comando": teclas, "vezes": 1})
        self.quadro += 1
        e = jogo.inimigos[0]
        seq, fase, vida = e.sequencia, e.estado, e.vida
        jogo.update(dt, cmd)
        if e.sequencia != seq:
            self._evento(jogo, "aviso", decisao=e.sequencia, acao=e.tecnica,
                         observado=ponto(e.observacao), origem=ponto(e.inicio),
                         alvo=ponto(e.alvo), instante_aviso=round(e.instante_aviso, 6))
        elif e.estado != fase:
            self._evento(jogo, "fase", fase=e.estado, acao=e.tecnica)
        atingiu_aranha = vida != e.vida
        for nome in jogo.eventos:
            if nome not in ("dano", "acerto", "abatido", "bloqueio", "morte"):
                continue
            if nome in ("dano", "morte"):
                atingido = "Lume"
            elif atingiu_aranha:
                atingido = "aranha"
                atingiu_aranha = False
            else:
                atingido = "projétil"
            ev = self._evento(jogo, nome, atingido=atingido, tecnica_em_curso=e.tecnica, lume=ponto(jogo.lume.rect.center),
                              aranha=ponto(e.rect.center), vida_aranha=e.vida, energia=round(jogo.lume.energia, 4),vida=round(jogo.lume.vida,4))
            if self.primeiro_impacto is None and nome in ("dano","acerto","abatido"):
                self.primeiro_impacto = ev

    def acao(self, jogo, nome):
        if nome not in ACOES:
            raise ValueError("Ação de bolsa desconhecida.")
        if self._reservar(jogo):
            self.entradas.append({"acao": nome})
        return getattr(jogo, nome)()

    def documento(self, jogo, motivo):
        fim = estado(jogo) if self.fim_limite is None else self.fim_limite
        return {
            "esquema": ESQUEMA, "simulacao": SIMULACAO, "assinatura": self.assinatura,
            "sala": SALA_ARANHA, "semente": self.semente, "dificuldade": self.dificuldade,
            "inicio": deepcopy(self.inicio), "entradas": deepcopy(self.entradas), "eventos": deepcopy(self.eventos),
            "primeiro_impacto": deepcopy(self.primeiro_impacto), "quadros": self.quadro,
            "fim": {"motivo": "limite" if self.fim_limite is not None else motivo, **fim},
        }


def gravar_tentativa(gravacao, jogo, motivo, pasta=None):
    pasta = pasta_dados() / "ensaios" / "aranha" if pasta is None else Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    dados = gravacao.documento(jogo, motivo)
    conteudo = json.dumps(dados, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    if len(conteudo) > MAX_BYTES:
        raise OSError("Tentativa excedeu o limite de tamanho do arquivo.")
    # Linkar um arquivo completo reserva o primeiro slot livre atomicamente,
    # mesmo se duas instâncias do jogo finalizarem suas tentativas juntas.
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=pasta, prefix=".aranha-", delete=False) as f:
            tmp = Path(f.name)
            f.write(conteudo)
        for slot in range(1, MAX_ARQUIVOS + 1):
            destino = pasta / f"tentativa-{slot:02d}.json"
            try:
                os.link(tmp, destino)
            except FileExistsError:
                continue
            return destino
        raise HistoricoCheio(f"Histórico cheio: {MAX_ARQUIVOS} espaços ocupados. Mova um JSON de ensaios/aranha para gravar outra tentativa.")
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


def validar(dados):
    if (not isinstance(dados, dict) or type(dados.get("esquema")) is not int
            or dados["esquema"] != ESQUEMA or dados.get("sala") != SALA_ARANHA
            or dados.get("simulacao") != SIMULACAO or dados.get("assinatura") != assinatura()):
        raise ValueError("Replay pertence a outra sala, versão ou assinatura de simulação.")
    dificuldade = dados.get("dificuldade")
    if type(dados.get("semente")) is not int or not isinstance(dificuldade, str) or dificuldade not in NIVEIS:
        raise ValueError("Semente ou dificuldade inválida.")
    if (not isinstance(dados.get("inicio"), dict) or not isinstance(dados.get("fim"), dict)
            or not isinstance(dados["fim"].get("motivo"), str) or not isinstance(dados.get("eventos"), list)
            or "primeiro_impacto" not in dados or not isinstance(dados.get("entradas"), list)):
        raise ValueError("O registro da tentativa está incompleto.")
    quadros = operacoes = 0
    for entrada in dados["entradas"]:
        if not isinstance(entrada, dict):
            raise ValueError("Entrada de replay inválida.")
        if "acao" in entrada:
            if set(entrada) != {"acao"} or entrada["acao"] not in ACOES:
                raise ValueError("Ação instantânea inválida.")
            operacoes += 1
        else:
            teclas, dt, vezes = entrada.get("comando"), entrada.get("dt"), entrada.get("vezes")
            if (set(entrada) != {"comando","dt","vezes"} or not isinstance(teclas, dict)
                    or type(dt) not in (int, float) or not 0 < dt <= .1
                    or type(vezes) is not int or vezes < 1):
                raise ValueError("Duração, repetição ou comando inválido.")
            for tecla,valor in teclas.items():
                permitido = (type(valor) is int and valor in (-1, 0, 1)) if tecla == "mover" else type(valor) is bool
                if tecla not in TECLAS or not permitido:
                    raise ValueError(f"Tecla inválida: {tecla}.")
            quadros += vezes
            operacoes += vezes
        if operacoes > MAX_PASSOS:
            raise ValueError("Tentativa excede o número máximo de entradas.")
    if type(dados.get("quadros")) is not int or dados["quadros"] != quadros:
        raise ValueError("Número de quadros não corresponde aos comandos.")


def ler_tentativa(caminho):
    with Path(caminho).open("rb") as f:
        conteudo = f.read(MAX_BYTES + 1)
    if len(conteudo) > MAX_BYTES:
        raise ValueError("Arquivo de replay excede o limite de tamanho.")
    try:
        dados = json.loads(conteudo)
    except RecursionError as erro:
        raise ValueError("Estrutura do replay excede o limite de leitura.") from erro
    validar(dados)
    return dados


def iterar_reproducao(dados, jogo):
    """Entrega um dt por atualização já executada. Divergência interrompe a reprodução."""
    validar(dados)
    gravacao = GravacaoAranha(jogo)
    if (jogo.semente != dados["semente"] or jogo.dificuldade != dados["dificuldade"]
            or gravacao.inicio != dados["inicio"]):
        raise ValueError("A sala do replay diverge já na condição inicial.")
    comparados = 0
    for entrada in dados["entradas"]:
        if "acao" in entrada:
            gravacao.acao(jogo, entrada["acao"])
            continue
        cmd = Comando(**entrada["comando"])
        for _ in range(entrada["vezes"]):
            gravacao.avancar(jogo, entrada["dt"], cmd)
            for ev in gravacao.eventos[comparados:]:
                if comparados >= len(dados["eventos"]) or ev != dados["eventos"][comparados]:
                    raise ValueError(f"Divergência no quadro {gravacao.quadro}, evento {ev['tipo']}.")
                comparados += 1
            yield entrada["dt"]
    atual = gravacao.documento(jogo, dados["fim"]["motivo"])
    if comparados != len(dados["eventos"]) or atual["primeiro_impacto"] != dados["primeiro_impacto"] or atual["fim"] != dados["fim"]:
        raise ValueError(f"Divergência ao terminar o replay no quadro {gravacao.quadro}.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", type=Path)
    args = parser.parse_args()
    try:
        dados = ler_tentativa(args.arquivo)
        jogo = preparar_ensaio(INDICE_ARANHA, dados["dificuldade"], semente=dados["semente"])
        for _ in iterar_reproducao(dados, jogo):
            pass
    except (OSError, ValueError) as erro:
        print(f"Falha na reprodução: {erro}", file=sys.stderr)
        return 1
    n = sum(ev["tipo"] == "aviso" for ev in dados["eventos"])
    print(f"Semente {jogo.semente}: {dados['quadros']} quadros, {n} decisões. Replay conferido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
