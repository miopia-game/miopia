"""Missões e pistas exercitadas pela travessia real e pelos controles da App."""
import os
os.environ.setdefault("SDL_VIDEODRIVER","dummy")
os.environ.setdefault("SDL_AUDIODRIVER","dummy")
import unittest
from src.descoberta import conhecida
from src.orientacao import objetivo_atual
from src.travessia import Jornada
from tests.test_travessia import Percurso
from src.missoes import conhecidas,selecionar,rastreada
from src.narrativa import conversar


class PistasS04(unittest.TestCase):
    def test_proximo_mecanismo_explica_o_efeito_no_mundo(self):
        j=Jornada(etapa=1)
        for flags,ident,trecho in (((),"dreno","água"),(("dreno",),"lingueta","casulos"),
                                  (("dreno","lingueta"),"ponte","margem")):
            j.flags.clear();j.flags.update(flags)
            alvo=objetivo_atual(j)
            self.assertEqual(alvo.id,ident)
            self.assertIn(trecho,alvo.motivo)
            self.assertNotIn("x=",alvo.detalhe)

    def test_marca_antes_da_raiz_nao_revela_local_exato_no_mapa(self):
        p=Percurso(1)
        p.ir(273);p.ir(426,pular=True);p.usar()
        p.ir(798);p.usar()
        self.assertEqual(p.jogo.dialogo[0],"A peça levada pela cheia")
        self.assertIn("três dentes",p.jogo.dialogo[1])
        self.assertFalse(conhecida(p.jogo,982,422))
        p.jogo.fechar_dialogo()
        p.ir(831)
        for f in range(65):
            p.tick(mover=1,baixo=True,deslize=f==0)
            if p.jogo.interacao=="Recolher a lingueta":break
        self.assertEqual(p.jogo.interacao,"Recolher a lingueta")
        p.tick(interagir=True,baixo=True,mover=1)
        self.assertIn("lingueta",p.jogo.flags)
        self.assertIn("pista_canal",Jornada.carregar(p.jogo.salvar()).flags)

    def test_encomenda_fisica_por_controles_e_recompensa_unica(self):
        p=Percurso();p.ir(163);p.usar();p.jogo.fechar_dialogo()
        self.assertEqual([m.id for m in conhecidas(p.jogo)],["principal","entrega_mimo",'resgates'])
        p.ir(255);p.ir(374,pular=True)
        for f in range(115):p.tick(salto=f in (0,20),segurar_salto=f!=19)
        self.assertEqual(p.lume.rect.bottom,228)
        self.assertEqual(p.jogo.proximo().id,"encomenda_mimo")
        p.usar();self.assertEqual(rastreada(p.jogo).estado,"Entregar")
        p.ir(163);p.usar();p.jogo.fechar_dialogo()
        self.assertEqual(p.jogo.bolsa.estoque["tanino"],3)
        novo=Jornada.carregar(p.jogo.salvar());antes=novo.bolsa.estoque.copy()
        conversar(novo,"Mimo","")
        self.assertEqual(novo.bolsa.estoque,antes)
        self.assertFalse(any(o.id=="encomenda_mimo" for o in novo.objetos))
        self.assertEqual(next(m for m in conhecidas(novo) if m.id=="entrega_mimo").estado,"Concluída")

    def test_lista_e_selecao_por_teclado_persistem_sem_revelar_destino(self):
        import pygame
        from src.main import App
        a=App(temporaria=True)
        try:
            a.iniciar("historia");a.jogar();j=a.jogo
            self.assertFalse(selecionar(j,"pedido_3"))
            conversar(j,"Nira","");j.fechar_dialogo()
            def tecla(k):a.evento(pygame.event.Event(pygame.KEYDOWN,key=k))
            tecla(pygame.K_m);tecla(pygame.K_RIGHT);tecla(pygame.K_DOWN)
            a.desenhar();tecla(pygame.K_RETURN)
            self.assertEqual(j.missao,"pedido_0")
            self.assertEqual(a.pagina,0)
            self.assertEqual(Jornada.carregar(j.salvar()).missao,"pedido_0")
            self.assertFalse(conhecida(j,708,228))
            j.flags.add("registro")
            self.assertEqual(objetivo_atual(j).id,"vespera")
        finally:a.mem.db.close();pygame.quit()
