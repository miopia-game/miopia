"""Recria imagens da versão lateral e um GIF do percurso físico pelo Bosque."""
import os
from pathlib import Path
import sys
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
RAIZ=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(RAIZ))
import pygame
from PIL import Image
from src.main import App
from src.fases import RAIZ as POSICAO_RAIZ, SAIDA
from tests.test_travessia import Percurso
from tests.test_campanha import resolver_arena

def capturar():
    app=App(temporaria=True)
    destino=RAIZ/"capturas"
    destino.mkdir(parents=True, exist_ok=True)
    app.desenhar()
    pygame.image.save(app.quadro_renderizado,str(destino/"menu.png"))
    piloto=Percurso()
    app.jogo=piloto.jogo
    app.jogar()
    frames=[]
    passo=piloto.tick
    def quadro(**comandos):
        passo(**comandos)
        frame=round(piloto.jogo.tempo*60)
        if frame==128:
            app.desenhar()
            pygame.image.save(app.quadro_renderizado,str(destino/"bosque.png"))
        if frame%5==0 and frame<=360:
            app.desenhar()
            menor=pygame.transform.smoothscale(app.quadro_renderizado,(576,324))
            im=Image.frombytes("RGB",menor.get_size(),pygame.image.tobytes(menor,"RGB"))
            frames.append(im.quantize(colors=112,method=Image.Quantize.MEDIANCUT))
    piloto.tick=quadro
    piloto.bosque()
    frames[0].save(destino/"travessia.gif",save_all=True,append_images=frames[1:],
                   optimize=True,loop=0,duration=83,disposal=1)
    piloto.tick=passo
    for i,caminho in enumerate((None,piloto.corrego,piloto.taquaral)):
        if caminho: caminho()
        resolver_arena(piloto)
        piloto.ir(POSICAO_RAIZ);piloto.usar()
        piloto.ir(SAIDA);piloto.usar()
    piloto.gruta()
    avisos=0
    def encontro(**comandos):
        nonlocal avisos
        passo(**comandos)
        e=piloto.jogo.boss
        if e and e.estado=="aviso" and e.impacta and not e.progresso:
            avisos+=1
            if avisos==50:
                app.desenhar()
                pygame.image.save(app.quadro_renderizado,str(destino/"coruja.png"))
    piloto.tick=encontro
    resolver_arena(piloto)
    app.mem.db.close()
    pygame.quit()

if __name__=="__main__":
    capturar()
