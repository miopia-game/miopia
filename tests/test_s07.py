"""Contratos S07: percurso físico, recibos, desfecho, descoberta e áudio real."""
import hashlib
import unittest
import wave
from pathlib import Path
import pygame
from src import resgates,corte_vertical,jardim
from src.travessia import Jornada,Comando
from src.ensaios import ENSAIOS,preparar_ensaio
from src.main import App
from src.descoberta import revelar,conhecida
from src.visao import fontes
from src.taticas import FAMILIAS,Habitante
from src.audio import Audio,PASTA
from tests.test_s06_raizes import percurso
from tests.test_campanha import resolver_arena


def tecla(a,k):a.evento(pygame.event.Event(pygame.KEYDOWN,key=k))


class NarrativaS07(unittest.TestCase):
    def test_tila_resgate_e_mantimento_nao_duplicam_apos_save_e_morte(self):
        p=percurso('Resgate no berçário');j=p.jogo
        p.usar();self.assertEqual(j.dialogo[0],'Tila')
        self.assertEqual(j.sobreviventes['tila']['oficio'],'aguardando')
        resgates.escolher(j,1);self.assertEqual(j.bolsa.estoque['pavio'],1)
        novo=Jornada.carregar(j.salvar());novo.perder_fagulha();novo.reiniciar()
        casa=next(o for o in novo.objetos if o.id=='casa_tila')
        for oficio in (0,1,0,1):
            resgates.conversar(novo,casa);resgates.escolher(novo,oficio)
        self.assertEqual(novo.bolsa.estoque['pavio'],1)
        self.assertTrue(novo.sobreviventes['tila']['premio'])

    def test_bento_e_aru_exigem_as_passagens_corretas(self):
        j=Jornada(etapa=1);b=resgates.POR_ID['bento'];a=resgates.POR_ID['aru']
        self.assertFalse(resgates.disponivel(j,b));j.flags.add('ralo')
        self.assertTrue(resgates.disponivel(j,b));j.recolocar(b.ponto)
        j.update(1/60,Comando(interagir=True));resgates.escolher(j,0)
        self.assertIn('bento',j.sobreviventes)
        corte_vertical.entrar(j,'estaleiro');self.assertFalse(resgates.disponivel(j,a))
        j.sobreviventes['tila']={'oficio':'trilha','premio':False}
        self.assertTrue(resgates.disponivel(j,a));j.recolocar(a.ponto)
        j.update(1/60,Comando(interagir=True));self.assertEqual(j.dialogo[0],'Aru')

    def test_escolha_por_teclado_paginas_e_escape_sem_escolha_implicita(self):
        a=App(temporaria=True)
        try:
            a.comecar_ensaio(next(i for i,e in enumerate(ENSAIOS) if e.nome=='Resgate no berçário'))
            a.jogo.update(1/60,Comando(interagir=True));a.nova_fala(a.jogo.dialogo[1])
            self.assertTrue(a.fala_paginas)
            self.assertEqual(' '.join(a.fala_paginas),a.jogo.dialogo[1])
            tecla(a,pygame.K_ESCAPE)
            self.assertEqual(a.jogo.sobreviventes['tila']['oficio'],'aguardando')
            o=next(o for o in a.jogo.objetos if o.id=='casa_tila')
            resgates.conversar(a.jogo,o);a.nova_fala(a.jogo.dialogo[1])
            while a.pagina_fala<len(a.fala_paginas)-1:
                a.letras=len(a.fala);tecla(a,pygame.K_RETURN)
            a.letras=len(a.fala);a.desenhar()
            tecla(a,pygame.K_DOWN);tecla(a,pygame.K_RETURN)
            self.assertIsNone(a.jogo.dialogo)
            self.assertEqual(a.jogo.bolsa.estoque['pavio'],1)
            self.assertEqual(a.jogo.sobreviventes['tila']['oficio'],'abrigo')
        finally:a.mem.db.close();pygame.quit()

    def test_luz_da_trilha_e_opcao_tem_consequencia_real(self):
        j=Jornada();j.sobreviventes={'tila':{'oficio':'trilha','premio':False}}
        j.recolocar((1640,442));j.camera=1200
        self.assertTrue(any(x==1640 and r==150 for x,y,r in resgates.fontes(j)))
        j.sobreviventes['tila']['oficio']='abrigo'
        self.assertFalse(resgates.fontes(j))

    def test_save_antigo_e_novos_estados_sao_validados(self):
        d=Jornada().salvar();d.pop('sobreviventes');d.pop('concluida')
        self.assertFalse(Jornada.carregar(d).concluida)
        d['sobreviventes']={'tila':{'oficio':'inventado','premio':False}}
        with self.assertRaises(ValueError):Jornada.carregar(d)
        d['sobreviventes']={};d['concluida']='sim'
        with self.assertRaises(ValueError):Jornada.carregar(d)

    def test_caderno_abre_por_escolha_e_permite_rever_raizes(self):
        a=App(temporaria=True)
        try:
            a.iniciar('historia');a.jogar();tecla(a,pygame.K_c)
            self.assertEqual(a.estado,'jogo')
            a.jogo.historico[(0,0)]={'raiz'};a.jogo.historico[(0,1)]={'raiz'}
            tecla(a,pygame.K_c);self.assertEqual(a.estado,'registro')
            antes=a.registro_etapa;tecla(a,pygame.K_RIGHT)
            self.assertNotEqual(antes,a.registro_etapa)
            tecla(a,pygame.K_ESCAPE);self.assertEqual(a.estado,'jogo')
        finally:a.mem.db.close();pygame.quit()

    def test_final_zero_ou_tres_aliados_continua_jogavel(self):
        for n in (0,3):
            p=percurso('Último chamado');j=p.jogo
            j.sobreviventes={k:v for k,v in list(j.sobreviventes.items())[:n]}
            j.boss.aliados=n;j.lume.energia=4
            # Recursos são recolhidos via E, sem reposição ilimitada de teste.
            resolver_arena(p)
            self.assertTrue(j.boss.vencido);self.assertEqual(j.boss.coro_sinais,3)

    def test_espada_nao_substitui_sinais_e_gota_nao_se_repete(self):
        p=percurso('Último chamado');e=p.jogo.boss
        e.x=p.lume.rect.centerx;e.y=p.lume.rect.centery
        for n in range(25):p.tick(golpe=n%8==0)
        self.assertFalse(e.vencido);self.assertEqual(e.coro_sinais,0)
        p.usar();p.jogo.lume.energia=1;p.usar()
        self.assertLess(p.jogo.lume.energia,2)

    def test_vitoria_reabre_e_persiste_sem_perder_resgates(self):
        a=App(temporaria=True)
        try:
            a.iniciar('historia');a.jogar();j=a.jogo
            j.concluida=True;j.estado='vitoria';j.sobreviventes={'tila':{'oficio':'trilha','premio':False}}
            a.atualizar(1/60);self.assertEqual(a.estado,'fim');a.desenhar()
            self.assertTrue(all(r.bottom<505 for r in a.alvos))
            a.selecao=0;a.ativar();self.assertEqual((a.estado,j.estado),('jogo','jogando'))
            novo=Jornada.carregar(a.mem.ler('campanha'))
            self.assertTrue(novo.concluida);self.assertIn('tila',novo.sobreviventes)
            self.assertTrue(resgates.fontes(novo))
        finally:a.mem.db.close();pygame.quit()


class JardimS07(unittest.TestCase):
    def test_rota_continua_dois_segredos_cipó_e_volta_sem_portal(self):
        p=percurso('Jardim do Último Sinal');j=p.jogo;identidade=id(j)
        # Invulnerabilidade isola a geometria. IA/combate têm outros regressores.
        p.lume.iframes=9999
        for x,salto in ((2680,False),(2750,True),(2910,True),(3008,False),(3125,True),(3210,True),(3330,True),(3420,False),(3520,True)):
            p.ir(x,pular=salto)
        self.assertEqual(p.lume.rect.bottom,316);p.usar()
        self.assertIn('jardim_orvalho',j.cartografia)
        p.ir(3330);p.ir(3210,pular=True);p.ir(3120);p.usar()
        self.assertEqual(j.bolsa.estoque['lente'],1)
        p.ir(3300);p.ir(3900);p.usar();self.assertIn('jardim_comporta',j.cartografia)
        p.ir(4110,pular=True);p.ir(4290)
        for n in range(1000):
            e=next((e for e in j.inimigos if e.origem[0]==4350 and e.ativo),None)
            if e is None:break
            dx=e.rect.centerx-p.lume.rect.centerx
            p.tick(mover=1 if dx>44 else -1 if dx<-44 else 0,golpe=n%12==0,clarao=n%180==0,deslize=n%240==0)
        self.assertIn('vigia_4350',j.cartografia)
        p.ir(4500);p.usar();p.ir(4170)
        for espera in (60,65,90):p.tick(baixo=True,salto=True);p.esperar(espera)
        self.assertEqual(p.lume.rect.bottom,1462)
        p.ir(3830,agachar=True);p.usar();self.assertIn('jardim_calha',j.cartografia)
        p.tick(baixo=True,salto=True);p.esperar(90);p.ir(3020);p.usar()
        self.assertIn('jardim_plantado',j.cartografia)
        p.ir(2760)
        for n in range(100):p.tick(salto=n in (0,20),segurar_salto=True)
        self.assertEqual(p.lume.rect.bottom,1710);p.usar()
        self.assertIn('jardim_memoria',j.cartografia);j.fechar_dialogo()
        p.tick(baixo=True,salto=True);p.esperar(70)
        p.ir(2300);self.assertEqual(id(j),identidade);self.assertTrue(j.em_vertical)
        p.ir(2520);p.usar();antes=p.lume.rect.bottom
        for _ in range(250):
            p.tick();self.assertLessEqual(abs(p.lume.rect.bottom-antes),265/60+.02);antes=p.lume.rect.bottom
        self.assertEqual(p.lume.rect.bottom,790)
        salvo=Jornada.carregar(j.salvar())
        self.assertEqual(salvo.checkpoint,(2510,790))
        self.assertTrue({'jardim_comporta','jardim_calha','jardim_plantado'}<=salvo.cartografia)
        self.assertEqual(salvo.bolsa.estoque['lente'],1)

    def test_porta_nao_abre_sem_resgates_nem_sementes_sem_vigia(self):
        j=Jornada();corte_vertical.entrar(j,'estaleiro')
        entrada=next(o for o in j.objetos if o.id=='jardim_entrada')
        jardim.interagir(j,entrada);self.assertNotIn('jardim_aberto',j.cartografia)
        j.sobreviventes={i:{'oficio':'aguardando','premio':False} for i in resgates.POR_ID}
        jardim.interagir(j,entrada);self.assertIn('jardim_aberto',j.cartografia)
        jardim.interagir(j,next(o for o in j.objetos if o.id=='jardim_brotos'))
        self.assertNotIn('jardim_brotos',j.cartografia)
        jardim.interagir(j,next(o for o in j.objetos if o.id=='jardim_plantar'))
        self.assertNotIn('jardim_plantado',j.cartografia)

    def test_luzes_de_pos_jogo_nao_descobrem_andares_fora_da_tela(self):
        p=percurso('Floresta reacesa');j=p.jogo
        corte_vertical.entrar(j,'jardim');j.explorado.clear()
        for _ in range(100):revelar(j)
        self.assertTrue(conhecida(j,*j.lume.rect.center))
        self.assertFalse(conhecida(j,3000,1790))


class AudioS07(unittest.TestCase):
    def test_trinta_avisos_distintos_carregaveis_e_reproduzidos(self):
        a=Audio();self.assertTrue(a.disponivel)
        hashes=set()
        try:
            for especie in FAMILIAS:
                for familia in range(5):
                    nome=f'aviso_{especie}_{familia}';p=PASTA/(nome+'.wav')
                    with wave.open(str(p)) as w:
                        self.assertEqual((w.getnchannels(),w.getsampwidth(),w.getframerate()),(1,2,22050))
                    hashes.add(hashlib.sha256(p.read_bytes()).hexdigest());self.assertIn(nome,a.fx)
                    for n in range(12,16):pygame.mixer.Channel(n).stop()
                    self.assertTrue(a.tocar_local(nome,100,0))
            self.assertEqual(len(hashes),30)
            for nome in ('jardim','retorno','chefe_final'):self.assertIn(nome,a.trilhas)
        finally:pygame.mixer.quit()

    def test_ensaio_cicla_familias_e_envia_som_espacial(self):
        p=percurso('Escuta dos ataques');j=p.jogo
        p.tick(golpe=True);p.tick(clarao=True);p.tick(interagir=True)
        self.assertEqual(j.sons_espaciais[0][0],'aviso_aranha_1')
        self.assertGreater(j.sons_espaciais[0][1],j.lume.rect.centerx)


if __name__=='__main__':unittest.main()
