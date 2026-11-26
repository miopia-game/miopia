"""Amplia a própria gravação dos encontros, seguindo as posições registradas pela App."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import imageio_ffmpeg

from tools.gravar_fauna import FPS, NOMES, QUADROS

FONTE=Path(__file__).resolve().parents[1]/"assets/fontes/Nunito-Bold.ttf"


def ampliar(pasta):
    pasta=pasta.resolve()
    with tempfile.TemporaryDirectory(dir=pasta) as tmp:
        temp=Path(tmp)
        comandos=[]
        nomes=[]
        for i,nome in enumerate(NOMES):
            trilha=json.loads((pasta/f"foco-{i+1:02}.json").read_text())
            assert len(trilha)==QUADROS
            for n,(x,y,lx,ly) in enumerate(trilha):
                alvo_x=x+max(-200,min(200,lx-x))*.28
                alvo_y=y+max(-140,min(140,ly-y))*.15
                if n==0:
                    centro_x,centro_y=alvo_x,alvo_y
                centro_x+=(alvo_x-centro_x)*.20
                centro_y+=(alvo_y-centro_y)*.20
                ox=min(960,max(0,round((centro_x-480)/2)*2))
                oy=min(540,max(0,round((centro_y-270)/2)*2))
                t=(i*QUADROS+n)/FPS
                comandos.append(f"{max(0,t-.0001):.6f} crop@seguir x {ox}, crop@seguir y {oy};")
            inicio=i*QUADROS/FPS
            nomes.append(f"drawtext=fontfile='{FONTE}':text='{nome}':fontsize=36:fontcolor=0xf6ead0:"
                         f"x=38:y=36:box=1:boxcolor=0x10131b@0.84:boxborderw=12:"
                         f"enable='gte(t,{inicio})*lt(t,{inicio+1.5})'")
        (temp/"camera.txt").write_text("\n".join(comandos))
        filtro="setpts=PTS-STARTPTS,sendcmd=f=camera.txt,crop@seguir=960:540,scale=1920:1080:flags=lanczos,"+",".join(nomes)
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),"-v","error","-y","-i",str(pasta/"fauna-1080p60.mp4"),
                        "-map","0:v:0","-map","0:a:0","-map_chapters","0","-vf",filtro,"-c:v","libx264",
                        "-threads","4","-preset","veryfast","-crf","17","-pix_fmt","yuv420p","-c:a","copy",
                        "-movflags","+faststart",str(pasta/"fauna-detalhe-1080p60.mp4")],cwd=temp,check=True)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("pasta",type=Path)
    ampliar(p.parse_args().pasta)
