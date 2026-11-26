"""Regressões da retirada solicitada no S09; dados antigos não são apagados."""
import unittest
from src.travessia import Jornada,Comando
from src.main import App
from src.memoria import Memoria
from src.fases import CHAO,SAIDA
import pygame

class ModoRemovidoTest(unittest.TestCase):
    def test_menu_e_api_so_oferecem_historia(self):
        a=App(temporaria=True)
        try:
            self.assertFalse(any('infinito' in nome.lower() for nome in a.menu_nomes()))
            with self.assertRaises(ValueError):Jornada('infinito')
            with self.assertRaises(ValueError):a.iniciar('infinito')
        finally:a.mem.db.close();pygame.quit()

    def test_save_antigo_ignora_relogio_sem_perder_historia(self):
        j=Jornada(etapa=1);j.flags.add('dreno');d=j.salvar()
        d['tempo_restante']=.01
        novo=Jornada.carregar(d);novo.update(.05)
        self.assertEqual(novo.estado,'jogando');self.assertIn('dreno',novo.flags)
        self.assertNotIn('tempo_restante',novo.salvar())
        # Entrada normal pela opção Continuar, com reserva única do save antigo.
        antigo=dict(d);antigo.pop('vida');antigo['energia']=31
        a=App(temporaria=True)
        try:
            a.mem_camp=antigo;a.selecao=a.menu_nomes().index('Continuar história')
            a.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
            a.desenhar()
            self.assertEqual((a.estado,a.jogo.etapa,a.jogo.lume.vida,a.jogo.lume.energia),('jogo',1,31,31))
            self.assertIn('dreno',a.jogo.flags)
        finally:a.mem.db.close();pygame.quit()
        d['modo']='infinito'
        with self.assertRaises(ValueError):Jornada.carregar(d)

    def test_recordes_legados_ficam_guardados_sem_exibir_modo_removido(self):
        m=Memoria(temporaria=True)
        try:
            with m.db:
                m.db.execute("INSERT INTO tentativas(modo,resultado,etapa,pontos,segundos) VALUES ('infinito','derrota',4,100,60)")
            self.assertEqual(m.recordes(),[])
            self.assertEqual(m.db.execute('SELECT COUNT(*) FROM tentativas').fetchone()[0],1)
        finally:m.db.close()

    def test_ultima_saida_nao_reinicia_o_mundo(self):
        j=Jornada(etapa=3);j.flags.update(('raiz','chefe'));j.recolocar((SAIDA,CHAO))
        j.update(.02,Comando(interagir=True));self.assertEqual(j.estado,'vitoria')
        j.estado='jogando';j.update(.02,Comando(interagir=True))
        self.assertEqual((j.etapa,j.volta,j.estado),(3,0,'jogando'))
