"""Gera a distribuição Fedora x86_64 a partir do Python que executa o script."""
from argparse import ArgumentParser
from importlib.metadata import distribution
from pathlib import Path
import os
from io import BytesIO
import platform
import shutil
import subprocess
import sys
import sysconfig
import tarfile
from tempfile import TemporaryDirectory

RAIZ = Path(__file__).resolve().parents[1]
PACOTE = RAIZ / "distribuicao" / "Miopia-Linux-x86_64.tar.gz"
AVISOS_FEDORA = (
    "alsa-lib", "flac-libs", "freetype", "harfbuzz", "libbrotli", "libjpeg-turbo",
    "libpng", "libsndfile", "libtiff", "libvorbis", "libwebp", "mpg123-libs",
    "opus", "opusfile", "wavpack",
)


def ignorar_cache(origem,nomes):
    # Fedora fornece parte da stdlib só como .pyc. Esses módulos não são
    # cache dispensável: removê-los elimina codecs usados por ZIP, por exemplo.
    return [n for n in nomes if n=='__pycache__' or
            n.endswith('.pyc') and (Path(origem)/n).with_suffix('.py').exists()]


def copiar_pasta(origem, destino, *ignorar):
    padroes=shutil.ignore_patterns(*ignorar)
    def excluir(p,nomes):return set(ignorar_cache(p,nomes))|set(padroes(p,nomes))
    shutil.copytree(origem, destino, ignore=excluir)


def criar_runtime(pasta):
    if platform.machine() != "x86_64" or sys.platform != "linux" or sys.platlibdir != "lib64":
        raise SystemExit("Use o ambiente de construção Fedora x86_64.")
    versao = f"python{sys.version_info.major}.{sys.version_info.minor}"
    pacote_pygame = distribution("pygame-ce")
    if pacote_pygame.version != "2.5.8":
        raise SystemExit("O ambiente de construção precisa de pygame-ce 2.5.8.")
    if pasta.exists():
        raise SystemExit(f"O destino de preparação deve ser novo: {pasta}")
    rt = pasta / "runtime"
    lib = rt / "lib64"
    lib.mkdir(parents=True)
    (rt / "bin").mkdir()
    shutil.copy2(Path(sys.executable).resolve(), rt / "bin" / versao)
    soname = sysconfig.get_config_var("INSTSONAME")
    shutil.copy2(Path(sysconfig.get_config_var("LIBDIR")) / soname, lib / soname)
    stdlib = Path(sysconfig.get_path("stdlib"))
    copiar_pasta(stdlib, lib / versao, "site-packages", "config-*", "test", "tests",
                 "ensurepip", "idlelib", "tkinter", "turtledemo")
    site_pkgs = lib / versao / "site-packages"
    site_pkgs.mkdir()
    site_origem = Path(pacote_pygame.locate_file(""))
    copiar_pasta(site_origem / "pygame", site_pkgs / "pygame", "docs", "examples", "tests", "__pyinstaller", "__briefcase")
    copiar_pasta(site_origem / "pygame_ce.libs", site_pkgs / "pygame_ce.libs")
    nome_meta = f"pygame_ce-{pacote_pygame.version}.dist-info"
    copiar_pasta(site_origem / nome_meta, site_pkgs / nome_meta)
    licencas = pasta / "avisos-runtime"
    copiar_pasta(RAIZ / "docs" / "licencas-runtime", licencas)
    shutil.copy(stdlib / "LICENSE.txt", licencas / "CPython.txt")
    for nome in AVISOS_FEDORA:
        copiar_pasta(Path("/usr/share/licenses") / nome, licencas / nome)
    shutil.copy("/usr/share/doc/libogg/COPYING", licencas / "libogg.txt")
    shutil.copy("/usr/share/licenses/alsa-lib/COPYING", licencas / "LGPL-2.1.txt")
    # Enumerar os arquivos efetivamente embarcados facilita relacionar notices
    # e SONAME e substituir as bibliotecas compartilhadas individualmente.
    libs = sorted(p.name for p in (site_pkgs / "pygame_ce.libs").iterdir() if p.is_file())
    (licencas / "bibliotecas-embarcadas.txt").write_text("\n".join(libs) + "\n", encoding="utf-8")
    inicializador = f"""#!/bin/sh
set -eu
rt=$(CDPATH= cd -- "${{0%/*}}" && pwd -P)
base=${{rt%/*}}
export PYTHONHOME="$rt" PYTHONPATH="$base:$rt/lib64/{versao}/site-packages"
export LD_LIBRARY_PATH="$rt/lib64:$rt/lib64/{versao}/site-packages/pygame_ce.libs${{LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}}"
export PYGAME_HIDE_SUPPORT_PROMPT=1
cd -- "$base"
exec "$rt/bin/{versao}" -B -s -S -P -m src.main "$@"
"""
    (rt / "iniciar").write_text(inicializador, encoding="utf-8")
    (rt / "iniciar").chmod(0o755)
    with TemporaryDirectory() as objetos:
        objeto = Path(objetos) / "inicio.o"
        subprocess.run(["as", "--64", "-o", objeto, RAIZ / "tools" / "inicio-linux.S"], check=True)
        subprocess.run(["ld", "-s", "-z", "noexecstack", "-o", pasta / "Miopia", objeto], check=True)


def arquivar(pasta, destino):
    if not (pasta / "Miopia").is_file() or not (RAIZ / "src/main.py").is_file():
        raise SystemExit("Faltam o inicializador ou src/main.py.")
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(".gz.tmp")
    # Recursos e fontes são lidos direto da árvore final. Nunca mesclar um
    # staging anterior de assets: arquivos removidos não entram na versão.
    def filtrar(membro):
        if "__pycache__" in Path(membro.name).parts:
            return None
        if membro.name.endswith('.pyc'):
            origem=pasta/Path(membro.name).relative_to('Miopia')
            if not membro.name.startswith('Miopia/runtime/') or origem.with_suffix('.py').exists():return None
        membro.uid = membro.gid = 0
        membro.uname = membro.gname = ""
        return membro
    with tarfile.open(temporario, "w:gz", compresslevel=7) as tar:
        tar.add(pasta, arcname="Miopia", filter=filtrar)
        for sub in ("assets", "src", "tools", "tests", "capturas"):
            tar.add(RAIZ / sub, arcname=f"Miopia/{sub}", filter=filtrar)
        for nome in ("arte-da-rodada.md","arte-do-corte.md","audio.md","continuidade.md",
                     "direcao-de-arte.md","execucao.md","guardioes.md","mapas.md","rodada-de-teste.md",
                     "s02-feedback.md","s02-aranha.md","s00-origens.md"):
            tar.add(RAIZ / "docs" / nome, arcname=f"Miopia/docs/{nome}", filter=filtrar)
        instrucoes = ("Extraia a pasta inteira e abra o executável Miopia.\n"
                      "S40 · Ajustes → Controles remapeia as teclas da partida. Acessibilidade ajusta texto, contraste e clarões. No controle, A confirma e B volta nos menus. Consulte docs/equipe/S40.md.\n"
                      "S39 · Campo de testes → Floresta reacesa. Véspera está junto à ponte dos casulos. Tila na forquilha abre a descida do poço, e Bento no Córrego prepara a subida das raízes. M → Missões e pedidos mostra os postos.\n"
                      "S38 · Campo de testes → Nicho dos Berços ou Patrulha em dupla. V troca a arma. Na Cobra, salte o bote e ataque quando aparecer Brecha. Ctrl + J atravessa as escamas. Use Q/F no Pólen para desfazer projéteis à frente.\n"
                      "S37 · Campo de testes → O sino soterrado. Use S + Espaço nas grades e E no sino. Suba pelos degraus da direita e use E na trava para baixar a passarela. No mapa (M), os traços âmbar indicam onde Lume pisou.\n"
                      "S36 · Esc → Ajustes permite escolher a dificuldade da História. A mudança entra em vigor no marco. Esc → Voltar ao marco conserva vida, brilho, fagulhas e itens.\n"
                      "S35 · Campo de testes → Nicho dos Berços. E ergue a tranca. A cobra protege o cofre e a lâmpada a oeste. O Campo de testes tem 30 ensaios.\n"
                      "S34 · Campo de testes → Último chamado. Saia das faixas onde caem as penas. Use E e K no ninho âmbar. Os ninhos já respondidos ficam marcados.\n"
                      "S33 · Campo de testes → Jardim do Último Sinal. Fale com Tila na ponte, Bento após soltar a calha e Aru após plantar. Na História, os pontos de luz acompanham o trabalho escolhido.\n"
                      "S32 · Córrego Fundo: compare as marcas do canal e dos berços; volte à margem quando a raiz beber. Campo de testes → Tecelã do Vão mostra as crias. A água interrompe as que estão próximas.\n"
                      "S31 · Na História, abra M e pressione Esquerda duas vezes para ver A viagem de Lume. Campo de testes → O sino soterrado demonstra a pista da Coruja. São 29 ensaios.\n"
                      "S30 · Campo de testes → Galeria das Sementes. E lê a placa de Risca. Use S + Espaço na grade e nos patamares. Depois de reparar a veneziana, a corrente leva Lume à grade leste.\n"
                      "S29 · Campo de testes → Beiral do Taquaral. Segure Espaço ao cair sob as sementes que sobem. Saia pela esquerda para pousar no beiral. Volte à direita, solte Espaço e retome sob a aba.\n"
                      "S28 · No Jardim, leia a placa da Ponte das Lanternas. K a oeste atrai a vespa enquanto Lume cruza pelos galhos. A cobra caça junto à flor.\n"
                      "S27 · No Estaleiro, converse com Fio e acompanhe O fio da cheia em M → Missões e pedidos. Compare os riscos, recupere o carretel e volte à margem para reparar a passarela.\n"
                      "S26 · E na roda do Viveiro Afundado levanta a comporta. Siga a água a oeste para voltar à cisterna. A passagem fica salva.\n"
                      "S25 · No escuro, os guardas revezam ataques e continuam cercando Lume. Sob luz suficiente, até dois ataques podem se sobrepor. O ensaio da Vigília começa em chão firme.\n"
                      "S24 · No Poço da Seiva, pule sobre o casulo e use S + J no ar. O rebote alcança o nicho com um Pavio de pólen.\n"
                      "S23: nas Raízes do Córrego, a aranha da membrana investiga onde Lume pousou. O galho de cima permite chegar ao outro lado.\n"
                      "S22: o tutorial começa durante a História. As lições indicam quando uma ação foi praticada. M → Esquerda consulta os controles no diário.\n"
                      "S21: feche a veneziana do Arquivo da Casca com E, leia os traços e reabra a janela. Converse com Véspera nos ninhos altos do Bosque.\n"
                      "S20: no Corte da Figueira, J corta o ferrolho no Poço da Seiva. E no cipó sobe ao Arquivo da Casca; S + Espaço desce pela grade.\n"
                      "S19: M destaca o ninho ativo da Coruja e a volta do Jardim. Depois de entregar o âmbar a Mimo, V alterna Espinho e Agulha na partida.\n"
                      "S14: no resgate de Tila, as opções mostram os pontos de luz na trilha e o efeito do Pavio de pólen. O reencontro destaca o trabalho salvo.\n"
                      "S13: Campo de testes → Esc → Repetir o ensaio (ou R na pausa) recomeça a cena. Na tela de morte, a saída volta à lista com a mesma cena selecionada.\n"
                      "S12: zoom e arrasto mais leves no mapa com pouca área descoberta. M abre o mapa.\n"
                      "S11: 14 faixas próprias, com música de arena para cada guardião, para o Caruncho e para o Último Chamado. Volumes em Ajustes, F10 silencia. Abra Campo de testes para comparar os encontros.\n"
                      "S10: Avisos comportam as cinco linhas das pistas atuais, sem esconder a última ação; mensagens maiores usam reticências. M identifica o ensaio e conserva sua orientação depois que o aviso desaparece. Objetivos da História seguem no alto do mapa. Dicas mudam de canto para evitar Lume; grades têm sinais de descida e câmera inferior. História e 26 ensaios, sem Infinito.\n"
                      "Vida e brilho separados. Brilho não drena sozinho; K e ataques com Ctrl custam brilho e depois vida se faltar. Zero brilho apaga o halo; zero vida mata. Abates recuperam um pouco das duas barras; acertos retornam brilho com multiplicador sem dano. Tutorial durante o começo e ao encontrar novidades. Campo de testes → Combos da colônia / Clareira da Vigília / Globos e tochas. Núcleo e E na tocha acendem regiões; Q/F fixa globos permanentes. Mobs vivos voltam inteiros ao morrer; derrotados permanecem derrotados.\n"
                      "Use A/D para andar, Espaço para pular, solte e aperte de novo para o salto duplo, segure na queda para planar, S+Espaço para descer, Shift + direção para deslizar, "
                      "E interage, J/L combina cortes rápidos/pesados, S+J no ar rebota, direção+Shift+J avança. Ctrl+J/L carrega luz (8/14 de brilho; avanço com Ctrl custa 12), K clareia 520 px (22 de brilho). M/Tab abre mapa; +/− amplia, WASD/arrasto move, C centraliza, direito marca/remove e V muda o tipo. Q/F alterna/usa item. C fora do mapa abre caderno opcional. Esc pausa; F10 silencia, F11 alterna tela cheia.\n"
                      "Áudio e arte: docs. Componentes de software: avisos-runtime.\n").encode("utf-8")
        leia = tarfile.TarInfo("Miopia/JOGAR.txt")
        leia.size = len(instrucoes)
        tar.addfile(leia, BytesIO(instrucoes))
        for nome in ("requirements.txt", "requirements-dev.txt", "pytest.ini", "qa.sh", "rodar.sh", "rodar.bat"):
            tar.add(RAIZ / nome, arcname=f"Miopia/{nome}", filter=filtrar)
        tar.add(RAIZ / "docs" / "equipe", arcname="Miopia/docs/equipe", filter=filtrar)
        for nome in ("AGENTS.md", "CLAUDE.md"):
            tar.add(RAIZ / nome, arcname=f"Miopia/{nome}", filter=filtrar)
        for nome in ('pygame-auto-qa','pygame-autonomous-studio-pro'):
            skill=Path('.agents/skills')/nome
            tar.add(RAIZ/skill,arcname=f'Miopia/{skill}',filter=filtrar)
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        blocos = [bloco for bloco in readme.split("\n\n")
                  if not bloco.startswith("**Para desenvolver por sprints**")]
        for i, bloco in enumerate(blocos):
            if bloco.startswith("**Para jogar"):
                blocos[i] = "**Para jogar no Fedora 44 x86_64, abra Miopia, o executável ao lado deste arquivo.**"
                break
        readme = "\n\n".join(blocos).replace("(docs/licencas-runtime)", "(avisos-runtime)")
        conteudo = readme.encode("utf-8")
        info = tarfile.TarInfo("Miopia/README.md")
        info.size = len(conteudo)
        tar.addfile(info, BytesIO(conteudo))
    os.replace(temporario, destino)
    print(f"{destino} · {destino.stat().st_size / 1024**2:.1f} MiB")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--preparar", type=Path, help="preparar somente runtime, em uma pasta nova")
    parser.add_argument("--usar-runtime", type=Path, help="usar runtime que já passou pela preparação")
    parser.add_argument("--saida", type=Path, default=PACOTE)
    args = parser.parse_args()
    if args.preparar:
        criar_runtime(args.preparar)
        return
    if args.usar_runtime:
        arquivar(args.usar_runtime, args.saida)
        return
    with TemporaryDirectory() as tmp:
        pasta = Path(tmp) / "Miopia"
        criar_runtime(pasta)
        arquivar(pasta, args.saida)


if __name__ == "__main__":
    main()
