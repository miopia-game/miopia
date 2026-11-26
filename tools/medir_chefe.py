"""Roteiro fixo de 35 s por comandos normais para comparar guardiões. Sem janela."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sys
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.fases import ARENA, CHAO, FASES
from src.travessia import Comando, Jornada


def medir(indice):
    j = Jornada(etapa=indice)
    j.flags.update(('meio', 'marco', FASES[indice].preparo))
    j.checkpoint = ARENA + 80, CHAO
    j.reiniciar()
    estados, decisoes, eventos = Counter(), [], Counter()
    anterior = None
    comandos = []
    for quadro in range(35 * 60):
        # A mesma sequência, sem consultar o alvo, a técnica ou o estado da IA.
        ciclo = quadro % 360
        mover = 1 if ciclo < 110 else -1 if ciclo < 250 else 0
        cmd = Comando(mover=mover, salto=quadro % 93 == 0,
                      segurar_salto=quadro % 93 < 42,
                      golpe=quadro % 19 == 0, interagir=quadro % 37 == 0)
        comandos.append((mover, cmd.salto, cmd.segurar_salto, cmd.golpe, cmd.interagir))
        j.update(1 / 60, cmd)
        eventos.update(j.eventos)
        e = j.boss
        if e:
            estados[e.estado] += 1
            assinatura = (e.estado, getattr(e, 'tecnica', ''), getattr(e, 'fase', 1))
            if assinatura != anterior:
                decisoes.append({'t': round(quadro / 60, 3), 'estado': e.estado,
                                 'tecnica': assinatura[1], 'fase': assinatura[2],
                                 'x': round(e.x, 1), 'destino': round(e.destino, 1)})
                anterior = assinatura
        if j.estado != 'jogando':
            break
    return {'chefe': indice, 'tempo': round((quadro + 1) / 60, 3), 'estado': j.estado,
            'vida_chefe': e.vida if e else None, 'energia_lume': round(j.lume.energia, 2),
            'eventos': dict(eventos), 'quadros_por_estado': dict(estados), 'decisoes': decisoes,
            'comandos_sha256': hashlib.sha256(json.dumps(comandos).encode()).hexdigest()}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--saida', type=Path, required=True)
    p.add_argument('--rotulo', default='atual')
    a = p.parse_args()
    raiz = Path(__file__).resolve().parents[1]
    dados = {'rotulo': a.rotulo, 'metodo': '35 s ou queda, 60 Hz, normal, mesmos comandos; não é teste humano nem piloto vencedor',
             'fontes': {str(f.relative_to(raiz)): hashlib.sha256(f.read_bytes()).hexdigest()
                        for f in sorted((raiz / 'src').glob('*.py'))},
             'ensaios': [medir(i) for i in (2, 3)]}
    a.saida.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(a.saida)
