"""Imprime as vinte sequências reais de cada espécie, incluindo as manobras."""
import json,sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT","1")
from src.taticas import RECEITAS,FAMILIAS

def catalogo():
    return {tipo:[{"id":n,"nome":combo.nome,"passos":[familias[p] if isinstance(p,int) else p for p in combo.passos]}
                  for n,combo in enumerate(RECEITAS)] for tipo,familias in FAMILIAS.items()}

if __name__=="__main__":print(json.dumps(catalogo(),ensure_ascii=False,indent=2))
