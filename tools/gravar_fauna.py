"""Filma a IA real em pontos preparados de encontro, com um quadro por atualização."""
import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from math import dist
import os
from pathlib import Path
import subprocess
import tempfile
import time
import wave

import imageio_ffmpeg
import pygame

from src import arte_arena
from src.arte_combate import fase_da_criatura
from src.ensaios import ENSAIOS
from src.fases import ARENA, CHAO
from src.main import App
from src.ninhada import Cria
from src.taticas import Habitante
from src.travessia import Jornada
from tools.gravar_pinturas import encerrar_mix, sincronizar_audio

FPS = 60
QUADROS = 300


@dataclass(frozen=True)
class Patrulha:
    nome: str
    tipo: str
    bioma: int
    x: int
    y: int
    familia: int
    distancia: int


PATRULHAS = (
    Patrulha("Morcego","morcego",0,840,CHAO-40,3,100),
    Patrulha("Aranha","aranha",0,1660,CHAO,3,106),
    Patrulha("Vespa","vespa",2,790,CHAO-34,2,122),
    Patrulha("Carabídeo","carabideo",0,3150,CHAO,0,112),
    Patrulha("Sombra","sombra",3,1110,CHAO,3,102),
    Patrulha("Cobra","cobra",1,672,CHAO,3,93),
)
NOMES = tuple(e.nome for e in PATRULHAS) + (
    "Caruncho do Viveiro","Cobra dos Berços","Cria da ninhada",
    "Asa Fendida","Tecelã do Vão","Casco Oco","A Coruja",
    "Morcego do Galho","Vespa da Fenda","Caçada na Ponte","Último Chamado",
)


def comecar(app,nome):
    app.comecar_ensaio(next(i for i,c in enumerate(ENSAIOS) if c.nome==nome))
    return app.jogo


def tecla(app, key):
    app.evento(pygame.event.Event(pygame.KEYDOWN,key=key))
    app.evento(pygame.event.Event(pygame.KEYUP,key=key))


def preparar(app,i):
    if i<len(PATRULHAS):
        c=PATRULHAS[i]
        j=app.jogo=Jornada(etapa=c.bioma)
        j.campo_testes=True
        app.jogar()
        ator=Habitante(c.tipo,c.x,c.y,semente=405+i)
        j.inimigos[:]=[ator]
        ator.plano[:]=[c.familia]
        ator.t=.72
        pos=(c.x-c.distancia,CHAO)
    elif i in (6,7):
        j=comecar(app,"Caruncho do Viveiro" if i==6 else "Nicho dos Berços")
        if i==7:
            tecla(app,pygame.K_e)
            app.atualizar(1/FPS,presso=defaultdict(bool))
        ator=next(e for e in j.inimigos if getattr(e,"nome","")==NOMES[i])
        ator.plano[:]=[2]
        if i==7:
            ator.vida=ator.max_vida/2
        pos=(ator.rect.centerx+106,ator.rect.bottom)
    elif i==13:
        from src.travessia_fagulha import MorcegoDoGalho
        j=comecar(app,"Combate no Bosque")
        ator=next(e for e in j.inimigos if isinstance(e,MorcegoDoGalho))
        pos=(1001,240)
    elif i==14:
        from src.galeria_taquaral import VespaDaFenda
        j=comecar(app,"Galeria das Sementes")
        ator=next(e for e in j.inimigos if isinstance(e,VespaDaFenda))
        pos=(2070,968)
    elif i==15:
        j=comecar(app,"Jardim do Último Sinal")
        ator=next(e for e in j.inimigos if e.origem==(2720,790))
        pos=(2580,790)
    elif i==16:
        j=comecar(app,"Último chamado")
        ator=j.boss
        pos=(ARENA+240,CHAO)
    else:
        j=comecar(app,"Tecelã do Vão" if i==8 else NOMES[i])
        j.recolocar((ARENA+220,CHAO))
        app.atualizar(1/FPS,presso=defaultdict(bool))
        ator=j.boss
        assert ator is not None
        pos=(ARENA+290,CHAO)
        if i==8:
            x=round(ator.inicio+ator.largura*.61)
            cria=Cria(x,ator)
            ator.ninhada.vivos[:]=[cria]
            ator.ninhada.expira=ator.relogio+14
            cria.colegas=ator.ninhada.vivos
            ator=cria
            pos=(x-78,CHAO)
    j.recolocar(pos)
    j.camera=max(0,min(j.fase.width-960,pos[0]-380))
    j.camera_y=max(0,pos[1]-410)
    j.aviso_t=0
    return j,ator


def chefe(i):
    return 9 <= i <= 12 or i == 16


def amostra(j,ator,chefe):
    if chefe:
        fase,tecnica,_=arte_arena.postura(ator)
        xy=(ator.x,ator.y)
    else:
        fase,_,tecnica=fase_da_criatura(ator)
        xy=ator.rect.center
    visivel=(j.visivel(xy,12) and 12<xy[0]-j.camera<948 and 12<xy[1]-j.camera_y<528)
    return fase,tecnica,xy,visivel


def controles(app,i,n,fase,ator):
    j=app.jogo
    teclas=defaultdict(bool)
    if chefe(i):
        if n in (8,244):
            tecla(app,pygame.K_k)
        if i==12 and n%84<29:
            teclas[pygame.K_d if n%168<84 else pygame.K_a]=True
        if fase=="preparacao" and ator.tempo<.15 and j.lume.chao:
            tecla(app,pygame.K_SPACE)
    else:
        if n==0:
            dx=ator.rect.centerx-j.lume.rect.centerx
            teclas[pygame.K_d if dx>0 else pygame.K_a]=True
        if fase=="preparacao" and ator.t<.14 and j.lume.chao:
            tecla(app,pygame.K_SPACE)
        if (i==14 and n in (2,165)) or (i in (0,3) and n==2):
            tecla(app,pygame.K_k)
        if n==4 and i in (0,3,13,14):
            tecla(app,pygame.K_g)
        if n==225 and i!=15:
            tecla(app,pygame.K_g)
    return teclas


def rotulo(q,nome):
    # Identificação editorial aplicada somente à cópia da gravação.
    from src.ilustracao import fonte
    im=fonte(29,"forte").render(nome,True,(246,234,208))
    r=im.get_rect(topright=(q.get_width()-40,34))
    painel=pygame.Surface((r.width+30,r.height+14),pygame.SRCALPHA)
    pygame.draw.rect(painel,(16,19,27,211),painel.get_rect(),border_radius=7)
    painel.blit(im,(15,7))
    q.blit(painel,(r.x-15,r.y-7))


def cena(i,pasta,sonda=False):
    from pygame._sdl2.mixer import set_post_mix
    app=App(temporaria=True)
    try:
        j,ator=preparar(app,i)
        nome=NOMES[i]
        fases=Counter()
        tecnicas=set()
        caminho=0.
        antes=None
        marcas=[]
        foco=[]
        proc=None
        mix,tempos=[],[]
        ff=imageio_ffmpeg.get_ffmpeg_exe()
        arquivo=pasta/f"{i+1:02}.mp4"
        with tempfile.TemporaryDirectory(dir=pasta) as tmp:
            imagem=Path(tmp)/"imagem.mp4"
            som=Path(tmp)/"som.wav"
            if not sonda:
                proc=subprocess.Popen([ff,"-y","-v","error","-f","rawvideo","-s","1920x1080",
                    "-r",str(FPS),"-pix_fmt","rgb24","-i","-","-an","-c:v","libx264","-threads","3",
                    "-preset","veryfast","-crf","17","-pix_fmt","yuv420p",str(imagem)],stdin=subprocess.PIPE)
                set_post_mix(lambda _,dados:mix.append((time.perf_counter(),bytes(dados))))
                time.sleep(.08)
            try:
                for n in range(QUADROS):
                    if proc:
                        if tempos:
                            time.sleep(max(0.,tempos[-1]+1/FPS-time.perf_counter()))
                        tempos.append(time.perf_counter())
                    fase=amostra(j,ator,chefe(i))[0]
                    teclas=controles(app,i,n,fase,ator)
                    app.atualizar(1/FPS,presso=teclas)
                    fase,tecnica,xy,visivel=amostra(j,ator,chefe(i))
                    assert app.estado=="jogo", (nome,app.estado,n)
                    if visivel:
                        fases[fase]+=1
                        if antes is not None:
                            caminho+=dist(antes,xy)
                        if fase=="ataque":
                            tecnicas.add(tecnica)
                        if not marcas or marcas[-1][1]!=fase:
                            marcas.append((n,fase))
                    antes=xy if visivel else None
                    foco.append([round(2*(xy[0]-j.camera)),round(2*(xy[1]-j.camera_y)),
                                 round(2*(j.lume.rect.centerx-j.camera)),round(2*(j.lume.rect.centery-j.camera_y))])
                    if proc:
                        app.desenhar()
                        quadro=app.quadro_renderizado
                        if n<90:
                            quadro=quadro.copy()
                            rotulo(quadro,nome)
                        proc.stdin.write(pygame.image.tobytes(quadro,"RGB"))
                        if visivel and fase=="ataque" and fases[fase]==5:
                            x=round(2*(xy[0]-j.camera))
                            y=round(2*(xy[1]-j.camera_y))
                            caixa=pygame.Rect(x-195,y-145,390,290).clamp(quadro.get_rect())
                            pygame.image.save(quadro.subsurface(caixa),pasta/f"inspecao-{i+1:02}.png")
                if proc:
                    tempos.append(tempos[-1]+1/FPS)
                    time.sleep(.06)
            finally:
                if proc:
                    encerrar_mix()
                    proc.stdin.close()
                    if proc.wait():
                        raise RuntimeError("Falha na gravação de "+nome)
            if proc:
                (pasta/f"foco-{i+1:02}.json").write_text(json.dumps(foco))
                sincronizar_audio(mix,tempos,som)
                subprocess.run([ff,"-y","-v","error","-i",str(imagem),"-i",str(som),"-c:v","copy",
                                "-c:a","aac","-b:a","160k","-movflags","+faststart",str(arquivo)],check=True)
        resultado=dict(nome=nome,fases=dict(fases),ataques=sorted(tecnicas),percurso=round(caminho,1),marcas=marcas)
        print(json.dumps(resultado,ensure_ascii=False),flush=True)
        if not sonda:
            assert fases["ataque"]>=5 and caminho>6,(nome,resultado)
        return resultado
    finally:
        app.mem.db.close()
        app.janela.fechar()
        pygame.quit()


def juntar(pasta):
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    with tempfile.TemporaryDirectory(dir=pasta) as tmp:
        # As faixas AAC individuais têm priming. Concatena só a imagem e monta
        # o PCM com o número exato de amostras de cada capítulo antes de codificar.
        audio=Path(tmp)/"audio.wav"
        with wave.open(str(audio),"wb") as wav:
            wav.setparams((2,2,44100,0,"NONE","PCM"))
            for i in range(len(NOMES)):
                clipe=pasta/f"{i+1:02}.mp4"
                subprocess.run([ff,"-y","-v","error","-i",str(clipe),"-map","0:v:0","-c:v","copy",
                                str(Path(tmp)/clipe.name)],check=True)
                pcm=subprocess.check_output([ff,"-v","error","-i",str(clipe),"-map","0:a:0","-f","s16le","pipe:1"])
                tamanho=QUADROS*44100//FPS*4
                assert len(pcm)>=tamanho
                wav.writeframes(pcm[:tamanho])
        lista=Path(tmp)/"lista.ffconcat"
        lista.write_text("ffconcat version 1.0\n"+"".join(f"file '{i+1:02}.mp4'\nduration {QUADROS/FPS:.6f}\n" for i in range(len(NOMES))))
        capitulos=Path(tmp)/"capitulos.txt"
        capitulos.write_text(";FFMETADATA1\n"+"".join(f"[CHAPTER]\nTIMEBASE=1/{FPS}\nSTART={i*QUADROS}\nEND={(i+1)*QUADROS}\ntitle={nome}\n" for i,nome in enumerate(NOMES)))
        subprocess.run([ff,"-y","-v","error","-f","concat","-safe","0","-i",str(lista),"-i",str(audio),"-i",str(capitulos),
                        "-map","0:v","-map","1:a","-map_chapters","2","-c:v","copy","-c:a","aac","-b:a","160k",
                        "-movflags","+faststart",str(pasta/"fauna-1080p60.mp4")],check=True)


def principal():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--saida",type=Path,required=True)
    cli.add_argument("--sondar",action="store_true")
    cli.add_argument("--somente",type=int,nargs="+")
    args=cli.parse_args()
    args.saida.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as perfil:
        os.environ.update(MIOPIA_DADOS=perfil,SDL_VIDEODRIVER="dummy",SDL_AUDIODRIVER="dummy")
        indices=[i-1 for i in args.somente] if args.somente else range(len(NOMES))
        for i in indices:
            cena(i,args.saida,args.sondar)
        if not args.sondar and all((args.saida/f"{i+1:02}.mp4").exists() for i in range(len(NOMES))):
            juntar(args.saida)


if __name__=="__main__":
    principal()
