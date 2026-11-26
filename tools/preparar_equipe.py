"""Exporta código e jogo Linux em uma pasta nova, com manifesto de integridade."""
from argparse import ArgumentParser
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
if __package__:
    from .empacotar_linux import ignorar_cache
else:
    from empacotar_linux import ignorar_cache

RAIZ=Path(__file__).resolve().parents[1]
PASTAS=('src','assets','tests','tools','docs','outputs','capturas')
ARQUIVOS=('README.md','AGENTS.md','CLAUDE.md','requirements.txt','requirements-dev.txt',
          'pytest.ini','qa.sh','rodar.sh','rodar.bat','.gitignore','ENTREGA.json',
          'requirements-arte.txt','Jogar Miopia.command')

def exportar(saida,runtime,*,incluir_a3=True):
    if saida.exists():raise SystemExit('Escolha uma pasta nova. Exportações existentes são preservadas.')
    saida.mkdir(parents=True)
    for nome in PASTAS:
        if nome in ('outputs', 'capturas') and not (RAIZ/nome).is_dir():
            continue
        padroes=['__pycache__','*.pyc']
        if nome=='outputs' and not incluir_a3:
            padroes.append('entrega-a3*')
        shutil.copytree(RAIZ/nome,saida/nome,ignore=shutil.ignore_patterns(*padroes))
    for nome in ARQUIVOS:shutil.copy2(RAIZ/nome,saida/nome)
    registro=saida/'ENTREGA.json'
    entrega=json.loads(registro.read_text(encoding='utf-8'))
    # O ZIP não pode carregar seu próprio hash e os pacotes antigos não são copiados.
    excluir=('pacote_equipe','bytes_pacote_equipe','arquivos_verificados_equipe')
    if not incluir_a3:
        excluir+=('pacote_a3','bytes_pacote_a3')
    dados={k:v for k,v in entrega.items() if not k.startswith(excluir)}
    registro.write_text(json.dumps(dados,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for nome in ('pygame-auto-qa','pygame-autonomous-studio-pro'):
        skill=Path('.agents/skills')/nome
        shutil.copytree(RAIZ/skill,saida/skill,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    if runtime:
        for nome in ('runtime','avisos-runtime'):
            shutil.copytree(runtime/nome,saida/nome,ignore=ignorar_cache)
        shutil.copy2(runtime/'Miopia',saida/'Miopia')
        for nome in ('README.md','JOGAR.txt'):
            if (runtime/nome).is_file():
                shutil.copy2(runtime/nome,saida/nome)
    (saida/'LEIA_PRIMEIRO.txt').write_text(
        f'MIOPIA — pasta de colaboração {entrega["rodada"]}\n\n'
        'Extraia a pasta inteira antes de abrir o jogo.\n'
        'No Windows abra rodar.bat com Python 3.10 a 3.14 instalado. A primeira preparação pode usar a internet.\n'
        'No macOS e Linux abra rodar.sh. Com o runtime Linux incluído, o executável Miopia abre offline.\n\n'
        'Para trabalhar com GPT ou Claude, abra a pasta extraída e use docs/equipe/PROMPT_EQUIPE.md.\n'
        'O checklist e a fila estão em docs/equipe/CHECKLIST_EQUIPE.md e docs/equipe/PLANO.md.\n'
        'Pesquisas complementares estão em docs/equipe/PESQUISA_EQUIPE.md.\n'
        'As duas rotinas locais estão em .agents/skills/. A origem dos materiais herdados está em revisão.\n',
        encoding='utf-8')
    itens={str(p.relative_to(saida)):hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted(saida.rglob('*')) if p.is_file()}
    (saida/'MANIFESTO_SHA256.json').write_text(json.dumps(itens,ensure_ascii=False,indent=2),encoding='utf-8')
    arquivo=saida.with_suffix('.zip')
    if arquivo.exists():raise SystemExit('O ZIP de destino já existe.')
    # TarInfo gerado pode ter mtime Unix zero. ZIP começa em 1980; limitar
    # apenas sua data evita abortar a exportação de um runtime já extraído.
    with zipfile.ZipFile(arquivo,'x',zipfile.ZIP_DEFLATED,compresslevel=6,strict_timestamps=False) as z:
        for p in sorted(saida.rglob('*')):
            if p.is_file():z.write(p,str(Path(saida.name)/p.relative_to(saida)))
    print(arquivo)

if __name__=='__main__':
    p=ArgumentParser(description=__doc__)
    p.add_argument('--saida',type=Path,default=RAIZ/'colaboracao'/('Miopia-equipe-'+datetime.now().strftime('%Y%m%d-%H%M%S')))
    p.add_argument('--runtime',type=Path,default=RAIZ if (RAIZ/'runtime').is_dir() else RAIZ/'distribuicao'/'Miopia')
    p.add_argument('--sem-a3',action='store_true',help='Manter o atlas e omitir cópias das entregas acadêmicas.')
    a=p.parse_args();exportar(a.saida,a.runtime,incluir_a3=not a.sem_a3)
