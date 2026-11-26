import unittest
from src.travessia import Jornada,Lume
from src.combate import Inimigo,Projetil,Vetor
from src.narrativa import Bolsa


class FerramentasS04(unittest.TestCase):
    def preparar(self,j,item):
        j.bolsa.receber(item,2);j.bolsa.equipado=item

    def test_tanino_contra_casco_e_asa_dano_distinto_e_duracao_salva(self):
        j=Jornada();self.preparar(j,"tanino")
        self.assertEqual(j.usar_item(),"seiva")
        self.assertEqual(j.bolsa.estoque["tanino"],1)
        self.assertIsNone(j.usar_item())
        for tipo,dano in (("carabideo",2.5),("morcego",1)):
            e=Inimigo(tipo,170,442);e.frente=-1
            l=j.lume;l.rect.midbottom=(135,442);l.face=1
            l.arma.pedir(False);l.arma.tipo="";l.arma.avancar(.001,l);l.arma.avancar(.06,l)
            self.assertEqual(e.acertar(l.arma,l.arma.area(l),False,l),"acerto")
            self.assertEqual(e.max_vida-e.vida,dano)
        nova=Jornada.carregar(j.salvar());self.assertTrue(nova.lume.tanino)
        nova.tempo+=19;nova.aplicar_reliquias();self.assertFalse(nova.lume.tanino)

    def test_polen_sem_alvo_nao_gasta_e_com_asa_reduz_ritmo_e_corta_projetil(self):
        j=Jornada();self.preparar(j,"polen")
        self.assertIsNone(j.usar_item());self.assertEqual(j.bolsa.quantidade,2)
        e=Inimigo("morcego",j.lume.rect.centerx+100,400)
        p=Projetil("eco",Vetor(j.lume.rect.centerx+70,410),Vetor(-90,0),1.)
        e.projeteis=[p];j.inimigos=[e]
        self.assertEqual(j.usar_item(),"abertura")
        self.assertEqual(j.bolsa.quantidade,1);self.assertEqual(e.lentidao,6)
        self.assertFalse(e.projeteis)
        antes=e.relogio;e.update(.1,j.lume,140,False,())
        self.assertAlmostEqual(e.relogio-antes,.06)

    def test_luz_fere_noturno_mas_nao_carapaca(self):
        l=Lume(100,442)
        for tipo,dano in (("morcego",3),("sombra",3),("carabideo",0)):
            e=Inimigo(tipo,180,442)
            resultado=e.acertar(l.arma,None,True,l)
            self.assertEqual(e.max_vida-e.vida,dano)
            self.assertEqual(resultado,"bloqueio" if tipo=="carabideo" else "acerto")
