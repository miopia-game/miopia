"""Ensaia decisões de distribuição com material fictício criado dentro de cada teste."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from tools.ensaiar_procedencia import ensaiar


class EnsaioProcedenciaTest(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = Path(temp.name)
        self.pasta = base / "candidata"
        self.pasta.mkdir()
        self.manifesto = base / "manifesto.json"
        self.zip = base / "ensaio.zip"
        self.dados = {"versao": 1, "creditos": "CREDITOS.txt", "arquivos": []}
        self.adicionar("CREDITOS.txt", "Material fictício do teste.")
        self.adicionar("avisos/termos.txt", "Aviso fictício.")
        self.peca = self.adicionar("arte/amostra.txt", "Forma fictícia.", ["avisos/termos.txt"])

    def adicionar(self, nome, texto, avisos=None):
        alvo = self.pasta / nome
        alvo.parent.mkdir(parents=True, exist_ok=True)
        conteudo = texto.encode("utf-8")
        alvo.write_bytes(conteudo)
        item = {"caminho": nome, "origem": "Gerado pelo próprio teste",
                "prova": "FICTICIO-01", "decisoes": {"jogo": "liberado"},
                "sha256": sha256(conteudo).hexdigest(), "avisos": avisos or []}
        self.dados["arquivos"].append(item)
        return item

    def gravar(self):
        self.manifesto.write_text(json.dumps(self.dados, ensure_ascii=False), encoding="utf-8")

    def verificar(self, canal="jogo", saida=None):
        self.gravar()
        return ensaiar(self.manifesto, self.pasta, canal, saida)

    def test_cli_exporta_copias_exatas_com_creditos_e_avisos(self):
        descartado = self.adicionar("rascunho.txt", "Uso interno.")
        descartado["decisoes"]["jogo"] = "excluido"
        self.gravar()
        comando = [sys.executable, str(Path(__file__).resolve().parents[1] / "tools/ensaiar_procedencia.py"),
                   str(self.manifesto), str(self.pasta), "--canal", "jogo", "--saida", str(self.zip)]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("3 liberado(s), 1 excluído(s)", resultado.stdout)
        # O runtime mínimo da apresentação não inclui CP437. Nomes ASCII do ZIP
        # têm a mesma representação em UTF-8; entradas não ASCII têm a flag UTF-8.
        opcoes = {"metadata_encoding": "utf-8"} if sys.version_info >= (3, 11) else {}
        with ZipFile(self.zip, **opcoes) as pacote:
            self.assertCountEqual(pacote.namelist(), ["arte/amostra.txt", "CREDITOS.txt", "avisos/termos.txt"])
            for arquivo in pacote.namelist():
                self.assertEqual(pacote.read(arquivo), (self.pasta / arquivo).read_bytes())

    def test_sem_origem_bloqueia_ate_remover_ou_regularizar(self):
        sem_origem = self.pasta / "sem_origem.txt"
        sem_origem.write_bytes(b"novo")
        with self.assertRaisesRegex(ValueError, "sem_origem.txt.*sem registro"):
            self.verificar(saida=self.zip)
        self.assertFalse(self.zip.exists())
        sem_origem.unlink()
        self.assertEqual(self.verificar(), (3, 0))
        item = self.adicionar("sem_origem.txt", "novo")
        item["origem"] = " "
        with self.assertRaisesRegex(ValueError, "sem_origem.txt.*falta origem"):
            self.verificar(saida=self.zip)
        item["origem"] = "Criado pela fixture para o ensaio"
        self.assertEqual(self.verificar(saida=self.zip), (4, 0))

    def test_alterado_ou_ausente_preserva_zip_anterior(self):
        self.verificar(saida=self.zip)
        anterior = self.zip.read_bytes()
        arquivo = self.pasta / self.peca["caminho"]
        arquivo.write_bytes(b"conteudo alterado")
        with self.assertRaisesRegex(ValueError, "amostra.txt.*SHA-256"):
            self.verificar(saida=self.zip)
        arquivo.unlink()
        with self.assertRaisesRegex(ValueError, "amostra.txt.*ausente"):
            self.verificar(saida=self.zip)
        self.assertEqual(anterior, self.zip.read_bytes())

    def test_liberacao_exige_prova_e_canal_especifico(self):
        self.peca["prova"] = ""
        with self.assertRaisesRegex(ValueError, "amostra.txt.*falta prova"):
            self.verificar()
        self.peca["prova"] = "FICTICIO-01"
        with self.assertRaisesRegex(ValueError, "pendente para o canal loja"):
            self.verificar(canal="loja")
        self.peca["decisoes"]["jogo"] = "pendente"
        with self.assertRaisesRegex(ValueError, "amostra.txt.*pendente"):
            self.verificar()

    def test_aviso_excluido_creditos_excluidos_ou_vazios_bloqueiam(self):
        aviso = self.dados["arquivos"][1]
        aviso["decisoes"]["jogo"] = "excluido"
        with self.assertRaisesRegex(ValueError, "termos.txt.*aviso obrigatório"):
            self.verificar()
        aviso["decisoes"]["jogo"] = "liberado"
        creditos = self.dados["arquivos"][0]
        creditos["decisoes"]["jogo"] = "excluido"
        with self.assertRaisesRegex(ValueError, "CREDITOS.txt.*obrigatório"):
            self.verificar()
        creditos["decisoes"]["jogo"] = "liberado"
        (self.pasta / "CREDITOS.txt").write_bytes(b"")
        creditos["sha256"] = sha256(b"").hexdigest()
        with self.assertRaisesRegex(ValueError, "CREDITOS.txt.*vazio"):
            self.verificar()

    def test_rejeita_travessias_links_e_destino_interno(self):
        for nome in ("../fora", "/raiz", "pasta\\outro", "C:/outro"):
            with self.subTest(nome=nome):
                self.peca["caminho"] = nome
                with self.assertRaisesRegex(ValueError, "Caminho inválido"):
                    self.verificar()
        self.peca["caminho"] = "arte/amostra.txt"
        with self.assertRaisesRegex(ValueError, "ZIP precisa ficar fora"):
            self.verificar(saida=self.pasta / "arte" / "saida.zip")
        (self.pasta / "ligacao").symlink_to(self.manifesto)
        with self.assertRaisesRegex(ValueError, "ligacao.*link"):
            self.verificar()

    def test_rejeita_arquivo_repetido_e_campo_duplicado(self):
        self.dados["arquivos"].append(dict(self.peca, caminho="ARTE/AMOSTRA.TXT"))
        with self.assertRaisesRegex(ValueError, "repetido ou ambíguo"):
            self.verificar()
        self.manifesto.write_text('{"versao":1,"versao":2}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Campo repetido"):
            ensaiar(self.manifesto, self.pasta, "jogo")
