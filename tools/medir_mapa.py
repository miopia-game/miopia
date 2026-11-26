"""Mede o mapa parado, o redesenho e o arrasto pela App em perfil temporário."""
import hashlib,json,os,statistics,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))


def resumo(amostras):
    return {'mediana_ms':round(statistics.median(amostras),3),
            'p95_ms':round(sorted(amostras)[56],3),'max_ms':round(max(amostras),3)}


def medir_arrasto(a):
    import pygame
    from src.corte_vertical import entrar
    from src.descoberta import revelar
    from src.mapa_visor import QUADRO

    a.iniciar('historia');a.jogar()
    j=a.jogo;entrar(j,'jardim')
    for _ in range(80):revelar(j)
    explorado=set(j.explorado)
    centro=QUADRO.center
    def evento(tipo,**dados):
        pygame.event.post(pygame.event.Event(tipo,**dados))
        for e in pygame.event.get():a.evento(e)

    pygame.event.clear()
    evento(pygame.KEYDOWN,key=pygame.K_m)
    evento(pygame.MOUSEWHEEL,y=-3,pos=centro)
    evento(pygame.MOUSEBUTTONDOWN,button=1,pos=centro)
    a.desenhar()
    v=a.mapa_visor;antes=v.construcoes
    amostras=[];telas=hashlib.sha256()
    for n in range(75):
        dy=-4 if n%2==0 else 4
        ini=time.perf_counter()
        evento(pygame.MOUSEMOTION,pos=(centro[0],centro[1]+dy),rel=(0,dy))
        a.atualizar(1/60);a.desenhar()
        if n>=15:amostras.append((time.perf_counter()-ini)*1000)
        telas.update(pygame.image.tobytes(a.quadro_renderizado,'RGB'))
    evento(pygame.MOUSEBUTTONUP,button=1,pos=centro)
    assert v.construcoes-antes==75 and j.explorado==explorado
    return {**resumo(amostras),'redesenhos':v.construcoes-antes,'celulas':len(explorado),
            'sha256_quadros_rgb':telas.hexdigest()}


def medir():
    import pygame
    from src.main import App
    from src.travessia import Jornada
    from src.corte_vertical import entrar,LARGURA,ALTURA
    from src.cartografia import mapa_local
    from src.mapa_visor import Visor,QUADRO
    from src.descoberta import revelar,chave
    a=App(temporaria=True);j=Jornada();entrar(j,'jardim')
    try:
        v=Visor();v.preparar(j);v.zoom=1;v.limitar(j)
        resultado={'metodo':'SDL dummy, 15 aquecimentos e 60 quadros por caso; mesmo enquadramento/proporções. Não mede FPS do monitor.',
                   'referencia_S07':{'mediana_ms':43.273,'p95_ms':68.627,'observacao':'Registro anterior: 780x153, mapa completo sem zoom e com proporções diferentes. Não usar como comparação percentual direta.'},'casos':{}}
        for completo in (False,True):
            if completo:j.explorado={chave(j,x,y) for x in range(0,LARGURA,24) for y in range(0,ALTURA,24)}
            else:
                for _ in range(80):revelar(j)
            for cache in (False,True):
                amostras=[]
                for n in range(75):
                    ini=time.perf_counter()
                    if cache:v.desenhar(a.tela,j)
                    else:mapa_local(a.tela,j,QUADRO,janela_mundo=v.janela(j))
                    if n>=15:amostras.append((time.perf_counter()-ini)*1000)
                nome=('completo' if completo else 'parcial')+('_cache' if cache else '_redesenho')
                resultado['casos'][nome]=resumo(amostras)
        resultado['casos']['parcial_arrasto_app']=medir_arrasto(a)
        return resultado
    finally:a.mem.db.close();pygame.quit()


if __name__=='__main__':
    os.environ['SDL_VIDEODRIVER']='dummy';os.environ['SDL_AUDIODRIVER']='dummy'
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1'
    print(json.dumps(medir(),ensure_ascii=False,indent=2))
