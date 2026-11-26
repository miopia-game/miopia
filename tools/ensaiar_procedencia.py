"""Verifica uma pasta candidata à distribuição e, opcionalmente, exporta um ZIP de ensaio."""
import argparse
from contextlib import nullcontext
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import unicodedata
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


CANAIS = ("jogo", "loja", "github")
DECISOES = ("liberado", "excluido", "pendente")


def objeto_sem_duplicatas(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"Campo repetido no manifesto: {chave}")
        objeto[chave] = valor
    return objeto


def caminho_relativo(nome):
    if not isinstance(nome, str) or not nome:
        raise ValueError(f"Caminho vazio ou inválido: {nome!r}")
    partes = nome.split("/")
    if (any(not parte or parte.endswith((".", " ")) for parte in partes)
            or re.search(r'[\\:<>"|?*\x00-\x1f]', nome)):
        raise ValueError(f"Caminho inválido na pasta candidata: {nome!r}")
    return nome


def ler_manifesto(arquivo, canal):
    dados = json.loads(arquivo.read_text(encoding="utf-8"), object_pairs_hook=objeto_sem_duplicatas)
    if (not isinstance(dados, dict) or type(dados.get("versao")) is not int
            or dados["versao"] != 1 or not isinstance(dados.get("arquivos"), list)):
        raise ValueError("O manifesto deve declarar versao 1 e uma lista de arquivos.")
    creditos = caminho_relativo(dados.get("creditos"))
    entradas = set()
    liberados = {}
    obrigatorios = {creditos}
    chaves = set()
    for item in dados["arquivos"]:
        if not isinstance(item, dict):
            raise ValueError("Entrada de arquivo inválida no manifesto.")
        nome = caminho_relativo(item.get("caminho"))
        chave = unicodedata.normalize("NFC", nome).casefold()
        if chave in chaves:
            raise ValueError(f"Arquivo repetido ou ambíguo no manifesto: {nome}")
        chaves.add(chave)
        entradas.add(nome)
        decisoes = item.get("decisoes")
        if (not isinstance(decisoes, dict) or set(decisoes) - set(CANAIS)
                or any(d not in DECISOES for d in decisoes.values())):
            raise ValueError(f"{nome}: decisões de canal inválidas.")
        decisao = decisoes.get(canal, "pendente")
        if decisao == "excluido":
            continue
        if decisao == "pendente":
            raise ValueError(f"{nome}: decisão pendente para o canal {canal}.")
        for campo in ("origem", "prova"):
            if not isinstance(item.get(campo), str) or not item[campo].strip():
                raise ValueError(f"{nome}: falta {campo} para liberar no canal {canal}.")
        if not isinstance(item.get("sha256"), str) or not re.fullmatch(r"[a-fA-F0-9]{64}", item["sha256"]):
            raise ValueError(f"{nome}: SHA-256 inválido.")
        avisos = item.get("avisos")
        if not isinstance(avisos, list):
            raise ValueError(f"{nome}: declarar a lista de avisos, mesmo quando vazia.")
        obrigatorios.update(caminho_relativo(aviso) for aviso in avisos)
        liberados[nome] = item["sha256"].lower()
    for nome in sorted(obrigatorios - liberados.keys()):
        raise ValueError(f"{nome}: crédito ou aviso obrigatório precisa estar liberado para {canal}.")
    return entradas, liberados, obrigatorios


def conferir_inventario(pasta, esperados):
    encontrados = set()
    diretorios = [pasta]
    while diretorios:
        for caminho in diretorios.pop().iterdir():
            nome = caminho.relative_to(pasta).as_posix()
            modo = caminho.lstat().st_mode
            if stat.S_ISDIR(modo):
                diretorios.append(caminho)
            elif stat.S_ISREG(modo):
                if nome not in esperados:
                    raise ValueError(f"{nome}: arquivo sem registro de origem no manifesto.")
                encontrados.add(nome)
            else:
                raise ValueError(f"{nome}: link ou arquivo especial na pasta candidata.")
    faltam = sorted(esperados - encontrados)
    if faltam:
        raise ValueError(f"{faltam[0]}: arquivo declarado ausente na pasta candidata.")


def conferir_conteudo(pasta, liberados, obrigatorios, pacote):
    for nome, esperado in sorted(liberados.items()):
        caminho = pasta / nome
        digest = hashlib.sha256()
        with caminho.open("rb") as fonte:
            info = os.fstat(fonte.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ValueError(f"{nome}: tipo de arquivo inválido.")
            if nome in obrigatorios and not info.st_size:
                raise ValueError(f"{nome}: crédito ou aviso obrigatório está vazio.")
            membro = ZipInfo(nome)
            membro.compress_type = ZIP_DEFLATED
            membro.create_system = 3
            membro.external_attr = (stat.S_IFREG | (0o755 if info.st_mode & 0o111 else 0o644)) << 16
            membro.file_size = info.st_size
            destino = pacote.open(membro, "w") if pacote else nullcontext()
            with destino as saida:
                while bloco := fonte.read(1024 * 1024):
                    digest.update(bloco)
                    if saida is not None:
                        saida.write(bloco)
        if digest.hexdigest() != esperado:
            raise ValueError(f"{nome}: conteúdo alterado (SHA-256 diverge do manifesto).")


def ensaiar(manifesto, pasta, canal, saida=None):
    pasta = pasta.resolve(strict=True)
    manifesto = manifesto.resolve(strict=True)
    if not pasta.is_dir() or manifesto.is_relative_to(pasta):
        raise ValueError("Use uma pasta candidata e um manifesto externo a ela.")
    if saida is not None:
        if saida.is_symlink() or saida.resolve().is_relative_to(pasta) or saida.resolve() == manifesto:
            raise ValueError("O ZIP precisa ficar fora da pasta candidata, separado do manifesto e sem link.")
    esperados, liberados, obrigatorios = ler_manifesto(manifesto, canal)
    conferir_inventario(pasta, esperados)
    if saida is None:
        conferir_conteudo(pasta, liberados, obrigatorios, None)
        conferir_inventario(pasta, esperados)
    else:
        # O arquivo anterior permanece intacto se a verificação, leitura ou compressão falhar.
        with tempfile.TemporaryDirectory(dir=saida.parent) as trabalho:
            tentativa = Path(trabalho) / "ensaio.zip"
            with ZipFile(tentativa, "w", compression=ZIP_DEFLATED) as pacote:
                conferir_conteudo(pasta, liberados, obrigatorios, pacote)
            conferir_inventario(pasta, esperados)
            os.replace(tentativa, saida)
    return len(liberados), len(esperados) - len(liberados)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifesto", type=Path)
    parser.add_argument("pasta", type=Path, help="pasta preparada exclusivamente para o ensaio")
    parser.add_argument("--canal", required=True, choices=CANAIS)
    parser.add_argument("--saida", type=Path, help="gravar o ZIP após verificar os arquivos")
    args = parser.parse_args()
    try:
        liberados, excluidos = ensaiar(args.manifesto, args.pasta, args.canal, args.saida)
    except (ValueError, OSError) as erro:
        print(f"Ensaio bloqueado: {erro}", file=sys.stderr)
        return 1
    print(f"Ensaio conferido para {args.canal}: {liberados} liberado(s), {excluidos} excluído(s).")
    if args.saida is not None:
        print(f"ZIP de ensaio: {args.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
