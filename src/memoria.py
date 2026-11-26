"""Preferências e campanha gravadas fora da instalação, com histórico local SQLite."""
import json
import os
import sqlite3
import sys
from pathlib import Path
from .controles import carregar

PADRAO = {"musica":.56,"brilho":1,"efeitos":.85,"mudo":False,"dificuldade":"normal"}
def pasta_dados():
    if os.environ.get("MIOPIA_DADOS"):
        return Path(os.environ["MIOPIA_DADOS"])
    if sys.platform=="win32":
        return Path(os.environ.get("LOCALAPPDATA",Path.home()))/"Miopia"
    if sys.platform=="darwin":
        return Path.home()/"Library"/"Application Support"/"Miopia"
    return Path(os.environ.get("XDG_DATA_HOME",Path.home()/".local"/"share"))/"miopia"


class Memoria:
    def __init__(self, temporaria=False):
        self.aviso=""
        try:
            if temporaria: self.db=sqlite3.connect(":memory:")
            else:
                pasta=pasta_dados()
                pasta.mkdir(exist_ok=True,parents=True)
                self.db=sqlite3.connect(pasta/"miopia.sqlite3")
            self.criar()
        except (OSError,sqlite3.Error):
            self.aviso="Armazenamento indisponível. Esta sessão ficará na memória."
            self.db=sqlite3.connect(":memory:")
            self.criar()
        self.prefs=dict(PADRAO)
        dados=self.ler("preferencias")
        self.prefs["teclas"] = carregar(dados.get("teclas")) if isinstance(dados, dict) else {}
        self.prefs.update(texto=100, contraste=False, claroes_suaves=False, numeros_hud=False)
        if isinstance(dados,dict):
            for k in ("musica","efeitos"):
                if isinstance(dados.get(k),(float,int)):
                    self.prefs[k]=max(0,min(1,dados[k]))
            if type(dados.get("brilho")) is int and 0 <= dados["brilho"] <= 3:
                self.prefs["brilho"] = dados["brilho"]
            if dados.get("dificuldade") in ("fácil","normal","difícil"):
                self.prefs["dificuldade"]=dados["dificuldade"]
            self.prefs["mudo"]=dados.get("mudo") is True
            if dados.get("texto") in (100, 115, 125):
                self.prefs["texto"] = int(dados["texto"])
            for ajuste in ("contraste", "claroes_suaves", "numeros_hud"):
                self.prefs[ajuste] = dados.get(ajuste) is True

    def criar(self):
        with self.db:
            self.db.execute("CREATE TABLE IF NOT EXISTS estado (chave TEXT PRIMARY KEY, valor TEXT NOT NULL)")
            self.db.execute("""CREATE TABLE IF NOT EXISTS tentativas (
                 id INTEGER PRIMARY KEY, modo TEXT NOT NULL, resultado TEXT NOT NULL,
                 etapa INTEGER NOT NULL, pontos INTEGER NOT NULL, segundos REAL NOT NULL,
                 instante TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")

    def ler(self,chave):
        try:
            row=self.db.execute("SELECT valor FROM estado WHERE chave=?",(chave,)).fetchone()
            return json.loads(row[0]) if row else None
        except (sqlite3.Error,ValueError):
            return None

    def guardar(self,chave,valor):
        try:
            with self.db:
                self._gravar(chave, valor)
        except sqlite3.Error:
            self.aviso="Não foi possível salvar neste dispositivo."
            return False
        return True

    def _gravar(self, chave, valor):
        self.db.execute("INSERT OR REPLACE INTO estado VALUES (?,?)", (chave, json.dumps(valor, ensure_ascii=False)))

    def guardar_campanha(self, dados, resultados):
        if not resultados:
            return self.guardar("campanha", dados)
        try:
            with self.db:
                self.db.executemany("INSERT INTO tentativas(modo,resultado,etapa,pontos,segundos) VALUES (?,?,?,?,?)",
                                    resultados)
                self._gravar("campanha", dados)
        except sqlite3.Error:
            self.aviso = "O resultado não pôde ser gravado. O save anterior foi preservado."
            return False
        if self.aviso.startswith("O resultado não pôde ser gravado."):
            self.aviso = ""
        return True

    def recordes(self):
        return self.db.execute("""SELECT modo, COUNT(*), MAX(pontos), MAX(etapa)
                                  FROM tentativas WHERE modo='historia' GROUP BY modo ORDER BY modo""").fetchall()
