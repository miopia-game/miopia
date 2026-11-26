"""Compromisso de mira, saídas físicas, fases e contagem de acertos das arenas."""
import unittest
import pygame
from src.chefes import Encontro, Fio
from src import casco, coruja
from src.fases import CHAO


def corpo(x, base=CHAO, altura=42):
    r=pygame.FRect(0,0,24,altura)
    r.midbottom=x,base
    return r


def ate(e, estado, jogador, segundos=12):
    eventos=[]
    for _ in range(round(segundos*120)):
        if e.estado==estado:return eventos
        eventos.extend(e.update(1/120,jogador))
    raise AssertionError((e.nome,e.estado,estado))


class GuardioesS05(unittest.TestCase):
    def test_casco_cruza_jogador_mas_nao_corrige_mira_no_aviso(self):
        e=Encontro(2,0,CHAO);l=corpo(400)
        ate(e,'aviso',l)
        self.assertEqual(e.tecnica,'carga')
        self.assertGreaterEqual(e.tempo,.6)
        plano=e.destino,e.alvo_y,e.frente
        ate(e,'investida',corpo(650))
        self.assertEqual((e.destino,e.alvo_y,e.frente),plano)
        eventos=ate(e,'freio_casco',l)
        self.assertEqual(eventos.count('dano_jogador'),1)
        self.assertLess(e.x,l.left)
        self.assertAlmostEqual(e.tempo,.76*e.ritmo.recuperacao)
        e=Encontro(2,0,CHAO)
        ate(e,'aviso',l)
        eventos=ate(e,'freio_casco',corpo(650))
        self.assertNotIn('dano_jogador',eventos)

    def test_salto_pune_apoio_alto_e_permite_sair_da_queda(self):
        for esquiva in (False,True):
            e=Encontro(2,0,CHAO)
            apoio=e.apoios()[2]
            alvo=corpo(apoio.centerx,apoio.top)
            ate(e,'aviso',alvo)
            self.assertEqual(e.tecnica,'salto')
            self.assertEqual(e.som_aviso,'casco_salto')
            destino=e.destino
            jogador=corpo(100) if esquiva else alvo
            eventos=ate(e,'freio_casco',jogador)
            self.assertEqual('dano_jogador' in eventos,not esquiva)
            self.assertAlmostEqual(e.x,destino)
            self.assertEqual(len(e.ondas),2)
            self.assertEqual([o.vx for o in e.ondas],[-255,255])

    def test_onda_tem_salto_como_saida_e_expira(self):
        for saltou in (False,True):
            e=Encontro(2,0,CHAO)
            e.tempo=10
            e.ondas=[casco.Onda(150,CHAO,255)]
            l=corpo(210,CHAO-40 if saltou else CHAO)
            eventos=[]
            for _ in range(60):eventos.extend(e.update(1/120,l))
            self.assertEqual(eventos.count('dano_jogador'),int(not saltou))
            for _ in range(120):e.update(1/120,l)
            self.assertFalse(e.ondas)

    def test_fase_dois_tem_transicao_e_dois_avisos_separados(self):
        e=Encontro(2,0,CHAO);l=corpo(300)
        e.vida=49
        eventos=e.update(1/120,l)
        self.assertIn('casco_muda',eventos)
        self.assertEqual((e.fase,e.estado),(2,'muda_casco'))
        avisos=[];pausas=[]
        anterior=e.estado
        for _ in range(800):
            eventos=e.update(1/120,l)
            if 'aviso' in eventos:avisos.append((e.tecnica,e.tempo))
            if e.estado=='freio_casco' and anterior!=e.estado:pausas.append(e.tempo)
            anterior=e.estado
            if len(avisos)>=2:break
        self.assertEqual(len(avisos),2)
        self.assertTrue(all(t>=.47 for _,t in avisos))
        self.assertIn(.30*e.ritmo.recuperacao,pausas)
        self.assertEqual(e.combo_restante,0)

    def test_coruja_tres_familias_reproduziveis_com_mira_fixa(self):
        a=Encontro(3,0,CHAO);b=Encontro(3,0,CHAO)
        escolhidas=[]
        for n in range(30):
            l=corpo(150 if n%2 else 440)
            coruja.preparar(a,l,[]);coruja.preparar(b,l,[])
            escolhidas.append(a.tecnica)
            self.assertEqual(a.tecnica,b.tecnica)
        self.assertEqual(set(escolhidas),{'garra','rasante','penas'})
        plano=a.destino,a.alvo_y,a.tecnica
        ate(a,'investida' if a.tecnica!='penas' else 'recolhe_coruja',corpo(650))
        self.assertEqual((a.destino,a.alvo_y,a.tecnica),plano)

    def test_garra_e_rasante_tem_altura_de_fuga_e_penas_expiram(self):
        for tecnica in ('garra','rasante'):
            for esquiva in (False,True):
                e=Encontro(3,0,CHAO)
                # Fixture de início da faixa física, após o aviso já conferido.
                e.tecnica=tecnica;e.estado='investida';e.tempo=2
                e.x,e.y=500,CHAO-31;e.destino,e.alvo_y=150,CHAO-31
                l=corpo(300,CHAO-90 if esquiva else CHAO)
                eventos=ate(e,'recolhe_coruja',l)
                self.assertEqual('dano_jogador' in eventos,not esquiva)
        e=Encontro(3,0,CHAO);e.tempo=10
        e.penas=[Fio(350,300,0,0)]
        for _ in range(370):e.update(1/120,corpo(150))
        self.assertFalse(e.penas)

    def test_coruja_usa_ultima_escuta_sem_ler_posicao_em_silencio(self):
        e=Encontro(3,0,CHAO)
        e.update(.01,corpo(300),ruido=.9)
        ate(e,'aviso',corpo(650))
        self.assertIn(e.destino,(208,300,392))
        self.assertIsNone(e.ouvido_corpo)
        plano=e.destino,e.alvo_y
        for _ in range(10):e.update(1/120,corpo(650),ruido=.9)
        self.assertEqual((e.destino,e.alvo_y),plano)

    def test_mesmo_arco_nao_renova_com_k_nem_vira_critico_depois(self):
        e=Encontro(2,0,CHAO,dificuldade="fácil")
        x,y=e._marca();l=corpo(x,CHAO-85)
        area=pygame.FRect(x-30,y-20,60,50)
        e.update(.01,l,golpe=area,serie=7)
        self.assertEqual(e.vida,98)
        e.update(.01,l,golpe=area,serie=7,clarao=True)
        e.estado='aberto';e.tempo=3
        e.update(.01,l,golpe=area,serie=7)
        self.assertEqual(e.progresso,0)
        self.assertEqual(e.vida,98)
        e.update(.01,l,golpe=area,serie=8)
        self.assertEqual(e.progresso,1)
        self.assertEqual(e.vida,48)

    def test_retorno_recompoe_fase_geometria_e_ameacas(self):
        from src.ensaios import ENSAIOS, preparar_ensaio
        from src.travessia import Comando, Jornada
        for nome in ('Casco Oco','A Coruja'):
            indice=next(i for i,e in enumerate(ENSAIOS) if e.nome==nome)
            j=preparar_ensaio(indice,'normal')
            for _ in range(32):j.update(1/60,Comando(mover=1))
            self.assertIsNotNone(j.boss)
            j.boss.vida=49;j.update(.02)
            self.assertEqual(j.boss.fase,2)
            j.lume.vida=0;j.update(.02)
            self.assertEqual(j.estado,'caido')
            j.reiniciar()
            for _ in range(32):j.update(1/60,Comando(mover=1))
            self.assertEqual((j.boss.fase,j.boss.vida),(1,100))
            self.assertFalse(getattr(j.boss,'ondas',[]) or getattr(j.boss,'penas',[]))
            salvo=j.salvar()
            legado=Jornada.carregar(salvo)
            self.assertIsNone(legado.boss)
            self.assertEqual(legado.checkpoint,j.checkpoint)


if __name__=='__main__':unittest.main()
