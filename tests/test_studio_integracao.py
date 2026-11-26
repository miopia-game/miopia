"""Ferramentas de QA devem acompanhar o projeto nas próximas exportações."""
import tarfile,zipfile
from pathlib import Path
import pytest
from tools import preparar_equipe as equipe
from tools import empacotar_linux as linux


@pytest.fixture
def projeto_exportavel(tmp_path,monkeypatch):
    raiz=tmp_path/'fonte';raiz.mkdir()
    for pasta in equipe.PASTAS:(raiz/pasta).mkdir()
    for nome in equipe.ARQUIVOS:(raiz/nome).write_text(nome)
    (raiz/"ENTREGA.json").write_text('{"rodada":"teste"}')
    (raiz/'src/main.py').write_text('pass\n')
    (raiz/'docs/equipe').mkdir()
    for nome in ('arte-da-rodada.md','arte-do-corte.md','audio.md','continuidade.md',
                 'direcao-de-arte.md','execucao.md','guardioes.md','mapas.md',
                 'rodada-de-teste.md','s02-feedback.md','s02-aranha.md','s00-origens.md'):
        (raiz/'docs'/nome).write_text(nome)
    for nome in ('pygame-auto-qa','pygame-autonomous-studio-pro'):
        skill=raiz/'.agents/skills'/nome;skill.mkdir(parents=True)
        (skill/'SKILL.md').write_text(nome)
    pro=raiz/'.agents/skills/pygame-autonomous-studio-pro'
    (pro/'scripts').mkdir();(pro/'scripts/probe.py').write_text('print("probe pronto")\n')
    (pro/'references').mkdir();(pro/'references/protocolo.md').write_text('Procedimento de teste')
    monkeypatch.setattr(equipe,'RAIZ',raiz);monkeypatch.setattr(linux,'RAIZ',raiz)
    return raiz


def test_exportacao_equipe_leva_pro_com_scripts_e_referencias(projeto_exportavel,tmp_path):
    destino=tmp_path/'equipe';equipe.exportar(destino,None)
    with zipfile.ZipFile(destino.with_suffix('.zip')) as z:
        assert 'equipe/.agents/skills/pygame-autonomous-studio-pro/scripts/probe.py' in z.namelist()
        assert z.read('equipe/.agents/skills/pygame-autonomous-studio-pro/references/protocolo.md')==b'Procedimento de teste'
        assert z.read('equipe/.agents/skills/pygame-auto-qa/SKILL.md')==b'pygame-auto-qa'


def test_exportacao_de_desenvolvimento_mantem_atlas_e_omite_entregas_a3(projeto_exportavel,tmp_path):
    outputs=projeto_exportavel/'outputs'
    (outputs/'atlas.xlsx').write_text('atlas de teste')
    historico=outputs/'entrega-a3-s11';historico.mkdir()
    (historico/'A3_Jogo_Miopia.zip').write_text('pacote acadêmico de teste')
    destino=tmp_path/'equipe'
    equipe.exportar(destino,None,incluir_a3=False)
    with zipfile.ZipFile(destino.with_suffix('.zip')) as z:
        assert 'equipe/outputs/atlas.xlsx' in z.namelist()
        assert not any('/entrega-a3-' in nome for nome in z.namelist())
    assert (historico/'A3_Jogo_Miopia.zip').is_file()


def test_pacote_linux_leva_pro_com_scripts_e_referencias(projeto_exportavel,tmp_path):
    stage=tmp_path/'runtime';stage.mkdir();(stage/'Miopia').write_bytes(b'fixture de empacotamento')
    destino=tmp_path/'jogo.tar.gz';linux.arquivar(stage,destino)
    with tarfile.open(destino) as t:
        assert 'Miopia/.agents/skills/pygame-autonomous-studio-pro/scripts/probe.py' in t.getnames()
        assert t.extractfile('Miopia/.agents/skills/pygame-autonomous-studio-pro/references/protocolo.md').read()==b'Procedimento de teste'
        assert t.extractfile('Miopia/.agents/skills/pygame-auto-qa/SKILL.md').read()==b'pygame-auto-qa'
