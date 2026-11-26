"""Cura finita, inventário legado, retorno, energia salva e autosave."""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
from src.travessia import Jornada,Comando
from src.narrativa import Bolsa
from src.fases import CHAO,MEIO


class RecursosS06(unittest.TestCase):
    def test_marco_guarda_retorno_sem_curar(self):
        j=Jornada();j.recolocar((MEIO,CHAO));j.lume.energia=30
        j.update(.02)
        self.assertEqual(j.checkpoint,(MEIO,CHAO))
        self.assertLessEqual(j.lume.energia,30)
        j.update(.02,Comando(interagir=True))
        self.assertLessEqual(j.lume.energia,30)
        self.assertIn('não cura',j.aviso)

    def test_abrigo_uma_reserva_sem_duplicar_apos_morte_ou_load(self):
        j=Jornada();j.recolocar((114,CHAO));j.lume.energia=20
        j.update(.02,Comando(interagir=True))
        self.assertGreater(j.lume.energia,99)
        self.assertEqual(j.bolsa.estoque['balsamo'],2)
        j.lume.energia=20;j.usar_item()
        self.assertEqual(j.bolsa.estoque['balsamo'],1)
        j.update(.02,Comando(interagir=True))
        self.assertAlmostEqual(j.lume.energia,55,delta=.1)
        novo=Jornada.carregar(j.salvar())
        self.assertIn('descanso_abrigo',novo.flags)
        novo.perder_fagulha();novo.reiniciar()
        self.assertEqual(novo.lume.energia,100)
        self.assertEqual(novo.bolsa.estoque['balsamo'],1)
        novo.recolocar((114,CHAO));novo.lume.energia=20
        novo.update(.02,Comando(interagir=True))
        self.assertLess(novo.lume.energia,21)

    def test_bolsa_cheia_preserva_excedentes_e_pode_retirar_sem_cura_gratis(self):
        j=Jornada();j.bolsa.receber('balsamo',6)
        self.assertEqual((j.bolsa.quantidade,j.bolsa.reserva_balsamo),(2,5))
        j.flags.add('descanso_abrigo');j.recolocar((114,CHAO))
        j.lume.energia=12;j.usar_item()
        j.update(.02,Comando(interagir=True))
        self.assertEqual((j.bolsa.quantidade,j.bolsa.reserva_balsamo),(2,4))
        self.assertAlmostEqual(j.lume.energia,47,delta=.1)
        nova=Bolsa.carregar(j.bolsa.salvar(j.tempo),j.tempo)
        self.assertEqual((nova.quantidade,nova.reserva_balsamo),(2,4))
        legado=Bolsa.carregar({'estoque':{'balsamo':7}},0)
        self.assertEqual((legado.quantidade,legado.reserva_balsamo),(2,5))
        legado.receber('frasco',1);legado.receber('balsamo',1)
        self.assertEqual((legado.quantidade,legado.reserva_balsamo),(3,5))

    def test_carregar_nao_recarrega_luz_e_save_antigo_continua(self):
        j=Jornada();j.lume.energia=27.5
        dados=j.salvar()
        self.assertEqual(Jornada.carregar(dados).lume.energia,27.5)
        dados.pop('energia');dados.pop('retorno_pendente')
        self.assertEqual(Jornada.carregar(dados).lume.energia,100)
        j.perder_fagulha()
        novo=Jornada.carregar(j.salvar())
        self.assertEqual(novo.lume.energia,100)
        self.assertEqual(novo.lume.vidas,2)
        for invalida in (float('inf'),float('nan'),'cheia'):
            dados=j.salvar();dados['energia']=invalida
            with self.assertRaises(ValueError):Jornada.carregar(dados)

    def test_mecanismo_antigo_do_corte_nao_e_fonte_infinita_de_cura(self):
        from src import corte_vertical as c
        j=Jornada();c.entrar(j,'cisterna')
        j.cartografia.update(('ralo_aberto','atalho_copa'))
        for ident in ('ralo_cisterna','selo_copa','marco_poco'):
            o=next(o for o in j.objetos if o.id==ident)
            j.lume.energia=21
            j.interagir(o);j.fechar_dialogo()
            self.assertEqual(j.lume.energia,21)

    def test_autosave_inclui_dano_mesmo_sem_mudar_posicao(self):
        from src.main import App
        import pygame
        a=App(temporaria=True)
        try:
            a.iniciar('historia');a.jogar()
            a.jogo.lume.energia=31.5
            a.relogio=a.proximo_save+1
            a.salvar_campanha(False)
            self.assertEqual(a.mem.ler('campanha')['energia'],31.5)
        finally:a.mem.db.close();pygame.quit()


if __name__=='__main__':unittest.main()
