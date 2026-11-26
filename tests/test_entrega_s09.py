"""O runtime extraído de TAR pode conter arquivos com data Unix zero."""
from pathlib import Path
import hashlib,json,os,zipfile
import pytest
from tools import preparar_equipe as equipe


def test_exportacao_aceita_data_antiga_sem_perder_arquivos_ou_manifesto(tmp_path,monkeypatch):
    # Árvore mínima isola o empacotador; não substitui assets nos playtests.
    raiz=tmp_path/'fonte';raiz.mkdir()
    for pasta in equipe.PASTAS:
        (raiz/pasta).mkdir();(raiz/pasta/'exemplo.txt').write_text(pasta)
    for nome in equipe.ARQUIVOS:(raiz/nome).write_text(nome)
    (raiz/"ENTREGA.json").write_text('{"rodada":"teste"}')
    for nome in ('pygame-auto-qa','pygame-autonomous-studio-pro'):
        skill=raiz/'.agents/skills'/nome;skill.mkdir(parents=True)
        (skill/'SKILL.md').write_text('Rotina de QA')
    runtime=tmp_path/'instalacao';runtime.mkdir()
    for pasta in ('runtime','avisos-runtime'):
        (runtime/pasta).mkdir();(runtime/pasta/'arquivo').write_text(pasta)
    stdlib=runtime/'runtime';(stdlib/'modulo.py').write_text('valor=1')
    (stdlib/'modulo.pyc').write_bytes(b'cache dispensavel')
    (stdlib/'sem_fonte.pyc').write_bytes(b'modulo sem fonte')
    (stdlib/'__pycache__').mkdir();(stdlib/'__pycache__/cache.pyc').write_bytes(b'cache')
    (runtime/'Miopia').write_text('launcher')
    (runtime/'README.md').write_text('Leia a documentação da equipe.')
    os.utime(runtime/'README.md',(0,0))
    monkeypatch.setattr(equipe,'RAIZ',raiz)
    saida=tmp_path/'equipe';equipe.exportar(saida,runtime)
    with zipfile.ZipFile(saida.with_suffix('.zip')) as z:
        assert z.testzip() is None
        assert z.getinfo('equipe/README.md').date_time[0]==1980
        manifesto=json.loads(z.read('equipe/MANIFESTO_SHA256.json'))
        for nome,sha in manifesto.items():
            assert hashlib.sha256(z.read('equipe/'+nome)).hexdigest()==sha
        assert z.read('equipe/.agents/skills/pygame-auto-qa/SKILL.md')==b'Rotina de QA'
        assert 'qa.sh' in manifesto and 'requirements-dev.txt' in manifesto
        assert z.read('equipe/runtime/sem_fonte.pyc')==b'modulo sem fonte'
        assert 'runtime/modulo.pyc' not in manifesto
        assert not any('__pycache__' in nome for nome in manifesto)
    # A preparação do runtime deve obedecer ao mesmo contrato da exportação.
    from tools.empacotar_linux import copiar_pasta
    copia=tmp_path/'runtime-preparado';copiar_pasta(stdlib,copia)
    assert (copia/'sem_fonte.pyc').exists() and not (copia/'modulo.pyc').exists()
    antes=saida.with_suffix('.zip').read_bytes()
    with pytest.raises(SystemExit):equipe.exportar(saida,runtime)
    assert saida.with_suffix('.zip').read_bytes()==antes
