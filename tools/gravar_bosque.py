"""Grava a rota do primeiro morcego pela App, usando teclado virtual e um save temporário."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile


def gravar(saida):
    import imageio_ffmpeg
    import pygame
    from src.abertura_bosque import pista
    from src.main import App
    from src.travessia_fagulha import CHEGADA, CORTE_PRATICADO, MorcegoDoGalho
    from tests.test_s20_raiz import tecla
    from tests.test_s22_tutorial import iniciar
    from tests.test_s31_historia import CampanhaPelaApp

    class Piloto(CampanhaPelaApp):
        quadros = 0

        def tick(self, **cmd):
            super().tick(**cmd)
            self.quadros += 1
            if self.quadros % 2 == 0:
                self.app.desenhar()
                video.stdin.write(pygame.image.tobytes(self.app.quadro_renderizado, 'RGB'))

    saida.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    app = App(temporaria=True)
    arquivo = saida / 'bosque-em-jogo.mp4'
    comando = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo',
               '-pixel_format', 'rgb24', '-video_size', f'{app.quadro_renderizado.get_width()}x{app.quadro_renderizado.get_height()}', '-framerate', '30',
               '-i', '-', '-an', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
               '-movflags', '+faststart', str(arquivo)]
    try:
        with subprocess.Popen(comando, stdin=subprocess.PIPE) as video:
            try:
                j = iniciar(app)
                p = Piloto(app)
                morcego = next(e for e in j.inimigos if isinstance(e, MorcegoDoGalho))
                p.esperar(55)
                p.ir(111)
                p.esperar(34)
                p.tick(clarao=True)
                p.esperar(22)
                app.desenhar()
                pygame.image.save(app.quadro_renderizado, saida / 'bosque-inicio.png')
                p.ir(163)
                p.esperar(38)
                p.ir(255)
                for x in (380, 558, 708):
                    p.ir(x, pular=True)
                p.esperar(31)
                p.ir(799)
                p.tick(mover=1)
                p.esperar(48)
                tecla(app, pygame.K_g)
                p.esperar(47)
                assert j.fagulha_ativa.destino == CHEGADA and j.visivel(morcego.rect.center)
                app.desenhar()
                pygame.image.save(app.quadro_renderizado, saida / 'bosque-poleiro.png')
                p.ir(1011, pular=True)
                assert j.lume.rect.bottom == 240
                for _ in range(480):
                    if not morcego.ativo:
                        break
                    dx = morcego.rect.centerx - j.lume.rect.centerx
                    lado = 1 if dx >= 0 else -1
                    mover = lado if abs(dx) > 28 or j.lume.face != lado else 0
                    if not 958 < j.lume.rect.centerx + mover * 16 < 1190:
                        mover = 0
                    janela = pista(j)
                    if janela and janela[0] == "S":
                        p.tick(baixo=True)
                    else:
                        area = j.lume.arma.area_corte_rapido(j.lume)
                        cortar = (area.colliderect(morcego.rect) and not j.lume.arma.tipo
                                  and j.lume.face == lado and morcego.estado not in ("aviso", "investida"))
                        p.tick(mover=mover, golpe=cortar)
                assert CORTE_PRATICADO in j.tutorial and "inimigo_875" in j.flags
                p.esperar(55)
            finally:
                video.stdin.close()
            if video.wait():
                raise RuntimeError("Falha ao codificar a prévia")
        subprocess.run([ffmpeg, '-v', 'error', '-i', str(arquivo), '-f', 'null', '-'], check=True)
        print(f'{arquivo} · {p.quadros // 2} quadros a 30 fps · morcego vencido')
    finally:
        app.mem.db.close()
        pygame.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saida', type=Path, default=Path('work/entrega/previa'))
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='miopia-previa-') as perfil:
        os.environ.update(MIOPIA_DADOS=perfil, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy')
        gravar(args.saida)
