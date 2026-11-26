"""Ida e volta por comandos, portas, cipó, mini-chefe, descoberta e recibo."""
import unittest
from src.ensaios import ENSAIOS,preparar_ensaio
from src.travessia import Comando,Jornada
from src.fases import CHAO,MEIO
from src.descoberta import conhecida
from src.missoes import conhecidas,rastreada
from src.raizes_bosque import Caruncho
from tests.test_travessia import Percurso


def percurso(nome='Raízes do Bosque'):
    p=Percurso()
    p.jogo=preparar_ensaio(next(i for i,e in enumerate(ENSAIOS) if e.nome==nome),'normal')
    p.lume=p.jogo.lume
    return p


def descer(p):
    p.ir(1640)
    for y in (542,642,742,842):
        p.tick(baixo=True,salto=True);p.esperar(60)
        if p.lume.rect.bottom!=y:raise AssertionError((p.lume.rect.bottom,y))


def buscar_pino(p):
    p.ir(1940)
    p.ir(1940,pular=True);p.ir(1940,pular=True)
    if p.jogo.proximo().id!='pino_ninho':raise AssertionError(p.jogo.proximo())
    p.usar()
    for _ in range(2):p.tick(baixo=True,salto=True);p.esperar(60)


def vencer(p):
    j,l=p.jogo,p.lume
    e=next(e for e in j.inimigos if isinstance(e,Caruncho))
    for n in range(1800):
        dx=e.rect.centerx-l.rect.centerx;lado=1 if dx>0 else -1
        fugir=e.estado in ('aviso','investida') and abs(dx)<125
        mover=-lado if fugir else lado if abs(dx)>45 or l.face!=lado else 0
        salto=fugir and e.estado=='aviso' and e.t<.20 and l.chao
        if l.vida<45 and j.bolsa.estoque['balsamo']:
            j.bolsa.equipado='balsamo';j.usar_item()  # F, mesma ação da App.
        p.tick(mover=mover,golpe=n%17==0 and not fugir,salto=salto,segurar_salto=salto)
        if not e.ativo:return e
        if j.estado!='jogando':break
    raise AssertionError((j.estado,e.vida,e.estado,l.energia))


class RaizesS06(unittest.TestCase):
    def test_tres_salas_pino_caruncho_atalho_e_entrega_por_controles(self):
        p=percurso();j=p.jogo;identidade=id(j)
        p.usar();self.assertEqual(j.dialogo[0],'A reserva do berçário');j.fechar_dialogo()
        self.assertFalse(conhecida(j,1800,1250))
        descer(p);buscar_pino(p)
        self.assertIn('pino_ninho',j.flags)
        p.ir(2200);p.ir(2390);p.ir(2148);p.usar()
        self.assertIn('porta_ninho',j.flags)
        e=vencer(p)
        self.assertGreaterEqual(e.sequencia,3)
        self.assertEqual(e.fase,2)
        self.assertIn('caruncho_vencido',j.flags)
        p.ir(1580);p.usar();p.ir(1510);p.usar()
        self.assertIn('cipo_estendido',j.flags)
        self.assertEqual(rastreada(j).estado,'Entregar')
        p.ir(2180);p.usar()
        antigo=p.lume.rect.bottom
        for _ in range(230):
            p.tick()
            self.assertLessEqual(abs(p.lume.rect.bottom-antigo),265/60+.02)
            antigo=p.lume.rect.bottom
        self.assertAlmostEqual(p.lume.rect.bottom,CHAO)
        self.assertEqual(j.checkpoint,(MEIO,CHAO))
        self.assertFalse(j.em_vertical);self.assertEqual(id(j),identidade)
        self.assertTrue(all('viu_raizes_'+s in j.flags for s in ('galeria','poco','camara')))
        # Retorno físico pela trilha; nenhuma chamada de portal ou atribuição de posição.
        if p.lume.vida<45 and j.bolsa.estoque['balsamo']:j.usar_item()
        p.ir(1520);p.ir(1320,pular=True)
        p.tick(baixo=True,salto=True);p.esperar(60)
        p.ir(1130,agachar=True);p.ir(900);p.ir(163);p.usar()
        self.assertEqual(j.dialogo[0],'Mimo');j.fechar_dialogo()
        self.assertEqual(j.bolsa.capacidade_balsamo,3)
        self.assertIn('pedido_raizes_entregue',j.flags)
        self.assertEqual(next(m for m in conhecidas(j) if m.id=='pedido_raizes').estado,'Concluída')
        novo=Jornada.carregar(j.salvar())
        mimo=next(o for o in novo.objetos if o.nome=='Mimo')
        novo.interagir(mimo)
        # Outro pedido de Mimo pode oferecer o primeiro mantimento: o frasco
        # e o recibo do Caruncho não se repetem.
        self.assertEqual(novo.bolsa.estoque['frasco'],1)
        self.assertEqual(sum(t=='A reserva do berçário · entregue' for t,_ in novo.diario),1)

    def test_retorno_sem_vencer_e_cipo_necessario(self):
        p=percurso();j=p.jogo
        descer(p);p.ir(2200);p.ir(2390);p.ir(2180)
        menor=p.lume.rect.bottom
        for n in range(150):
            p.tick(salto=n in (0,20),segurar_salto=n!=19)
            menor=min(menor,p.lume.rect.bottom)
        self.assertGreater(menor,842)
        p.esperar(80);p.usar();p.esperar(220)
        self.assertEqual(p.lume.rect.bottom,842)
        self.assertNotIn('caruncho_vencido',j.flags)
        p.ir(1640)
        for y in (742,642,542,CHAO):
            p.ir(1640,pular=True);self.assertEqual(p.lume.rect.bottom,y)
        self.assertFalse(j.em_vertical)

    def test_porta_exige_pino_e_save_nao_abre_sala_invisivel(self):
        p=percurso();j=p.jogo
        descer(p);p.ir(2200);p.ir(2390);p.ir(2148);p.usar()
        self.assertNotIn('porta_ninho',j.flags)
        self.assertIn('pino',j.aviso)
        self.assertTrue(any(t.tipo=='ninho_tranca' and t.rect.top==1054 for t in j.solidos))
        self.assertFalse(conhecida(j,1800,1250))
        energia=j.lume.energia
        novo=Jornada.carregar(j.salvar())
        self.assertFalse(novo.em_vertical)
        self.assertAlmostEqual(novo.lume.energia,energia)
        self.assertEqual(novo.lume.rect.midbottom,novo.checkpoint)
        self.assertNotIn('caruncho_vencido',novo.flags)
        self.assertFalse(conhecida(novo,1800,1250))

    def test_caruncho_retorna_inteiro_apos_morte_mas_nao_renasce_apos_vitoria(self):
        p=percurso('Caruncho do Viveiro');j=p.jogo
        e=next(e for e in j.inimigos if isinstance(e,Caruncho))
        e.vida=8;j.update(.02)
        j.perder_fagulha();j.reiniciar()
        self.assertEqual((e.vida,e.fase),(22,1))
        vencer(p)
        novo=Jornada.carregar(j.salvar())
        self.assertFalse(any(isinstance(e,Caruncho) for e in novo.inimigos))
        self.assertTrue(any(o.id=='ambar_ninho' for o in novo.objetos))


if __name__=='__main__':unittest.main()
