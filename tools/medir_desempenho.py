"""Mede CPU de atualização/desenho em perfil temporário, sem prometer FPS real."""
import argparse,json,os,statistics,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

def medir(quadros=180):
    import pygame
    from src.main import App
    from src.travessia import Jornada,Comando
    from src.visao import Vestigio
    from src.subsolo import camera
    from src.fases import ARENA, CHAO
    from src import raizes_bosque
    app=App(temporaria=True);app.iniciar("historia");app.jogar()
    resultado={"metodo":"CPU, SDL dummy, 20 quadros de aquecimento; sem flip ou espera do monitor.","cenas":{}}
    try:
        cenas=(("bosque",0,450,442,False),("clarao",0,450,442,True),("subsolo",1,2850,1102,True),
               ('casco',2,ARENA+160,CHAO,False),('coruja',3,ARENA+160,CHAO,True),
               ('galeria',0,1850,842,True),('poco',0,2350,1282,True),('caruncho',0,1900,1282,True),
               ('jardim',1,3520,316,True),('retorno',0,450,442,False),
               ('clareira',0,1700,442,False),('globo',0,2230,442,False))
        for nome,etapa,x,y,flash in cenas:
            j=Jornada(etapa=etapa);app.jogo=j;j.recolocar((x,y));j.camera=max(0,x-450)
            if nome=='jardim':
                from src.corte_vertical import entrar,camera as camera_corte
                j.sobreviventes={i:{'oficio':'trilha','premio':False} for i in ('tila','bento','aru')}
                j.cartografia.add('jardim_aberto');entrar(j,'jardim');j.recolocar((x,y));camera_corte(j)
            if nome=='retorno':j.concluida=True
            if nome=='clareira':j.tochas.add('vigilia')
            if nome=='globo':j.globos=[{'regiao':'0:0','x':2230,'y':420}]
            if nome in ('casco','coruja'):
                j.flags.update(('meio','marco',j.fase.preparo))
            if etapa==1 and not j.em_vertical:camera(j)
            if raizes_bosque.ativo(j):raizes_bosque.camera(j)
            if nome=='caruncho':j.flags.add('porta_ninho')
            desenho=[];simulacao=[]
            for n in range(quadros+20):
                if flash:j.vestigios=[Vestigio(x,y-20,j.tempo-.5)]
                ini=time.perf_counter();j.update(1/60,Comando());tempo=(time.perf_counter()-ini)*1000
                ini=time.perf_counter();app.desenhar();draw=(time.perf_counter()-ini)*1000
                if n>=20:desenho.append(draw);simulacao.append(tempo)
            def resumo(valores):
                return {"mediana_ms":round(statistics.median(valores),3),"p95_ms":round(sorted(valores)[int(len(valores)*.95)],3),"max_ms":round(max(valores),3)}
            resultado["cenas"][nome]={"simulacao":resumo(simulacao),"desenho":resumo(desenho)}
    finally:app.mem.db.close();pygame.quit()
    return resultado

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--quadros",type=int,default=180)
    args=p.parse_args()
    if not 30<=args.quadros<=3600:p.error("Use entre 30 e 3600 quadros.")
    os.environ["SDL_VIDEODRIVER"]="dummy";os.environ["SDL_AUDIODRIVER"]="dummy"
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"]="1"
    print(json.dumps(medir(args.quadros),ensure_ascii=False,indent=2))
