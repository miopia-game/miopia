"""Regras solicitadas no S08 e mapa navegável, com perfil temporário."""
import unittest
import pygame
from src.travessia import Jornada,Lume,Comando
from src.main import App
from src.ensaios import ENSAIOS
from src.fases import Terreno,CHAO
from src.visao import ponto_visivel,Vestigio
from src.paisagem import compor_luz
from src.descoberta import revelar,conhecida,chave
from src import corte_vertical,marcas_mapa
from src.mapa_visor import Visor,QUADRO,contexto
from tests.test_travessia import Percurso


class RecursosS08(unittest.TestCase):
    def test_brillo_zero_apaga_halo_mas_nao_mata_nem_drena_vida(self):
        j=Jornada();j.lume.energia=0
        for _ in range(180):j.update(1/60)
        self.assertEqual((j.estado,j.lume.energia,j.lume.vida,j.raio),('jogando',0.,100.,0.))
        self.assertFalse(ponto_visivel(j,(j.lume.rect.centerx+20,j.lume.rect.centery)))

    def test_clarao_paga_primeiro_brilho_depois_vida_sem_repetir_custo(self):
        j=Jornada();j.lume.energia=7;j.lume.vida=60
        j.update(1/60,Comando(clarao=True))
        self.assertEqual((j.lume.energia,j.lume.vida),(0,45))
        self.assertEqual(len(j.vestigios),1);self.assertEqual(j.raio,0)
        self.assertIn('sacrificio',j.eventos)
        self.assertTrue(ponto_visivel(j,(j.lume.rect.centerx+60,j.lume.rect.centery)))
        j.update(1/60,Comando(clarao=True));self.assertEqual(j.lume.vida,45)

    def test_avanco_tambem_pode_usar_vida_e_resina_reduz_custo(self):
        j=Jornada();j.lume.energia=0;j.lume.vida=90
        j.update(.02,Comando(mover=1,deslize=True,golpe=True,carregado=True))
        self.assertEqual((j.lume.arma.tipo,j.lume.vida),('avanco',78))
        j=Jornada();j.bolsa.receber('resina',1);j.aplicar_reliquias();j.lume.energia=0
        j.update(.02,Comando(clarao=True));self.assertEqual(j.lume.vida,82)

    def test_habilidade_pode_custar_a_ultima_vida_sem_abate_que_ressuscite(self):
        j=Jornada();j.lume.energia=0;j.lume.vida=22
        j.update(.02,Comando(clarao=True))
        self.assertEqual((j.estado,j.motivo_morte,j.lume.vida),('caido','sacrificio',0))
        self.assertEqual(j.lume.vidas,2)
        j.recuperar_abate();self.assertEqual(j.lume.vida,0)
        j.reiniciar();self.assertEqual((j.lume.vida,j.lume.energia),(100,100))

    def test_dano_e_queda_usam_vida_sem_tirar_brilho(self):
        j=Jornada();j.lume.energia=12;j.lume.vida=90;j.lume.iframes=0
        j.ferir();self.assertEqual(j.lume.energia,12);self.assertEqual(j.lume.vida,90-j.dano)
        hp=j.lume.vida;j.recuperar_queda()
        self.assertEqual((j.lume.vida,j.lume.energia),(hp-25,12))
        j.lume.vida=25;j.recuperar_queda();self.assertEqual(j.motivo_morte,'queda')

    def test_balsamo_cura_vida_com_brilho_cheio_e_abrigo_nao_farma(self):
        j=Jornada();j.lume.vida=30;j.usar_item()
        self.assertEqual((j.lume.vida,j.lume.energia),(65,100))
        j.recolocar((114,CHAO));j.update(.02,Comando(interagir=True))
        self.assertEqual(j.lume.vida,100)
        j.lume.vida=50;j.update(.02,Comando(interagir=True))
        self.assertEqual(j.lume.vida,50)

    def test_save_preserva_vida_zero_brilho_migracao_e_retorno(self):
        j=Jornada();j.lume.vida=47;j.lume.energia=0
        novo=Jornada.carregar(j.salvar());self.assertEqual((novo.lume.vida,novo.lume.energia),(47,0))
        antigo=j.salvar();antigo.pop('vida');antigo['energia']=31
        novo=Jornada.carregar(antigo);self.assertEqual((novo.lume.vida,novo.lume.energia),(31,31))
        j.perder_fagulha();novo=Jornada.carregar(j.salvar())
        self.assertEqual((novo.lume.vida,novo.lume.energia,novo.lume.vidas),(100,100,2))
        for invalido in (True,float('nan'),float('inf'),'50'):
            d=j.salvar();d['vida']=invalido
            with self.assertRaises(ValueError):Jornada.carregar(d)

    def test_abate_real_recupera_pouco_uma_vez_e_persiste(self):
        j=Jornada();j.lume.vida=40;j.lume.energia=20
        e=j.inimigos[0];e.vida=1;e.rect.midbottom=(j.lume.rect.centerx+35,CHAO)
        # Mesmo estado de ataque usado pela App, sem chamar a recompensa.
        j.lume.arma.pedir(False)
        for _ in range(12):j.update(1/120)
        self.assertFalse(e.ativo)
        self.assertEqual(j.lume.vida,43);self.assertAlmostEqual(j.lume.energia,28.35,delta=.1)
        for _ in range(30):j.update(1/120)
        self.assertEqual(j.lume.vida,43)
        novo=Jornada.carregar(j.salvar());self.assertEqual(novo.lume.vida,43)
        self.assertFalse(any(x.origem==e.origem for x in novo.inimigos))


class LuzS08(unittest.TestCase):
    def test_luz_portatil_e_clarao_atravessam_paredes_no_quadro_composto(self):
        class Sala(Jornada):
            @property
            def solidos(self):return (Terreno(pygame.Rect(235,0,15,540),'parede'),Terreno(pygame.Rect(0,330,960,20),'chao'))
        pygame.init();self.addCleanup(pygame.quit);pygame.display.set_mode((960,540))
        j=Sala();j.recolocar((220,410));luz=pygame.Surface((960,540))
        compor_luz(luz,j,0,0,1)
        self.assertTrue(ponto_visivel(j,(270,380)))
        self.assertGreater(luz.get_at((270,380))[0],80)
        self.assertTrue(ponto_visivel(j,(220,315)))
        j.lume.energia=0;compor_luz(luz,j,0,0,1);self.assertEqual(luz.get_at((270,380))[0],0)
        j.vestigios=[Vestigio(220,390,0)];j.tempo=1
        compor_luz(luz,j,0,0,1);self.assertGreater(luz.get_at((330,390))[0],100)
        self.assertFalse(ponto_visivel(j,(800,390)))


class MapaS08(unittest.TestCase):
    def setUp(self):
        self.a=App(temporaria=True);self.a.iniciar('historia');self.a.jogar()
    def tearDown(self):self.a.mem.db.close();pygame.quit()
    def tecla(self,k):self.a.evento(pygame.event.Event(pygame.KEYDOWN,key=k))

    def test_zoom_pan_arrasto_centro_congelam_tempo_e_nao_revelam(self):
        a=self.a;j=a.jogo;corte_vertical.entrar(j,'jardim')
        for _ in range(20):revelar(j)
        antes=j.salvar();a.abrir_diario('jogo');v=a.mapa_visor
        w=v.janela(j).w;self.tecla(pygame.K_EQUALS);self.assertLess(v.janela(j).w,w)
        centro=tuple(v.centro);self.tecla(pygame.K_w);self.assertNotEqual(tuple(v.centro),centro)
        a.evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=QUADRO.center))
        a.evento(pygame.event.Event(pygame.MOUSEMOTION,rel=(45,-20),pos=QUADRO.center,buttons=(1,0,0)))
        a.evento(pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=(0,0)))
        self.assertFalse(v.arrastando)
        for _ in range(4):a.atualizar(.1);a.desenhar()
        self.assertEqual(j.salvar(),antes)
        self.tecla(pygame.K_c);self.assertTrue(v.janela(j).collidepoint(*j.lume.rect.center))
        self.tecla(pygame.K_RIGHT);self.assertEqual(a.pagina,1)

    def test_proporcoes_e_ancora_da_roda_sao_preservadas(self):
        j=self.a.jogo;corte_vertical.entrar(j,'jardim');v=Visor();v.preparar(j)
        pos=(QUADRO.centerx+30,QUADRO.centery);antes=v.mundo(j,pos)
        v.ampliar(j,1,pos);depois=v.mundo(j,pos)
        self.assertAlmostEqual(antes[0],depois[0],delta=.01)
        self.assertAlmostEqual(antes[1],depois[1],delta=.01)
        r=v.janela(j);self.assertAlmostEqual(r.w/r.h,QUADRO.w/QUADRO.h,places=5)
        for _ in range(20):v.ampliar(j,-1)
        self.assertEqual(v.zoom,1)

    def test_marca_real_por_mouse_persiste_e_remove_sem_revelar(self):
        a=self.a;j=a.jogo
        for _ in range(15):revelar(j)
        a.abrir_diario('jogo');v=a.mapa_visor
        x,y=j.lume.rect.center;r=v.janela(j);esc=v.escala(j)
        pos=(round(QUADRO.x+(x-r.x)*esc),round(QUADRO.y+(y-r.y)*esc))
        antes=set(j.explorado)
        a.evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=3,pos=pos))
        self.assertEqual(len(j.marcas),1);self.assertEqual(j.explorado,antes)
        novo=Jornada.carregar(a.mem.ler('campanha'));self.assertEqual(novo.marcas,j.marcas)
        novo.perder_fagulha();novo.reiniciar();self.assertEqual(novo.marcas,j.marcas)
        a.evento(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=3,pos=pos))
        self.assertFalse(j.marcas)

    def test_marcas_desconhecidas_limite_e_dados_invalidos(self):
        j=self.a.jogo
        self.assertFalse(marcas_mapa.alternar(j,(4000,50),'perigo')[0])
        for n in range(marcas_mapa.LIMITE+1):j.explorado.add(chave(j,n*24,100))
        for n in range(marcas_mapa.LIMITE):self.assertTrue(marcas_mapa.alternar(j,(n*24,100),'perigo')[0])
        self.assertFalse(marcas_mapa.alternar(j,(marcas_mapa.LIMITE*24,100),'caminho')[0])
        dados=j.salvar();dados['marcas'][0]['celula']='corte/4/4'
        with self.assertRaises(ValueError):Jornada.carregar(dados)
        dados=j.salvar();dados.pop('marcas');self.assertFalse(Jornada.carregar(dados).marcas)

    def test_consulta_corte_na_superficie_nao_usa_geometria_ou_posicao_da_superficie(self):
        j=self.a.jogo;corte_vertical.entrar(j,'jardim');j.entrar(0)
        outro=contexto(j,True)
        self.assertTrue(outro.em_vertical);self.assertFalse(j.em_vertical)
        self.assertTrue(outro._mapa_sem_lume)
        self.assertTrue(any(t.rect.top==1828 for t in outro.solidos))
        self.a.abrir_diario('jogo');self.a.pagina=2;self.a.desenhar()
        self.assertEqual(self.a.mapa_visor.regiao,'corte')

    def test_cache_reusa_quadro_e_invalida_por_marca_e_exploracao(self):
        a=self.a;j=a.jogo
        for _ in range(15):revelar(j)
        a.abrir_diario('jogo');a.desenhar();v=a.mapa_visor;n=v.construcoes
        antes=pygame.image.tobytes(v.camada,'RGB')
        for _ in range(5):a.desenhar()
        self.assertEqual(v.construcoes,n)
        marcas_mapa.alternar(j,j.lume.rect.center,'perigo');a.desenhar()
        self.assertEqual(v.construcoes,n+1)
        self.assertNotEqual(antes,pygame.image.tobytes(v.camada,'RGB'))
        j.explorado.add(chave(j,700,420));a.desenhar();self.assertEqual(v.construcoes,n+2)


class PedidosS08(unittest.TestCase):
    def test_pos_jogo_tem_estado_correto_e_jardim_nao_repete_objetivo(self):
        from src.missoes import conhecidas
        from src.orientacao import objetivo_atual
        j=Jornada();j.concluida=True
        j.sobreviventes={i:{'oficio':'trilha','premio':False} for i in ('tila','bento','aru')}
        self.assertEqual(conhecidas(j)[0].estado,'Concluída')
        self.assertIn('jardim',[m.id for m in conhecidas(j)])
        j.cartografia.add('jardim_plantado')
        self.assertEqual(objetivo_atual(j).id,'colonia_reunida')


class LuzPermanenteS08(unittest.TestCase):
    def test_globo_consume_uma_carga_e_persiste_na_morte_e_save(self):
        from src import luzes_mundo
        j=Jornada();j.bolsa.receber('globo',2);j.bolsa.equipado='globo';j.lume.energia=0
        j.usar_item();self.assertEqual(len(j.globos),1);self.assertEqual(j.bolsa.estoque['globo'],1)
        j.usar_item();self.assertEqual(j.bolsa.estoque['globo'],1) # sobreposição não desperdiça.
        self.assertTrue(ponto_visivel(j,(200,400)))
        j.perder_fagulha();j.reiniciar();novo=Jornada.carregar(j.salvar());novo.lume.energia=0
        self.assertEqual(novo.globos,j.globos);self.assertTrue(ponto_visivel(novo,(200,400)))
        novo.entrar(1);self.assertFalse(luzes_mundo.fontes(novo))
        novo.entrar(0);self.assertTrue(luzes_mundo.fontes(novo))

    def test_tocha_exige_desafio_e_nucleo_unico_gera_zona_nitida(self):
        from src import encontros,luzes_mundo
        j=Jornada();c=encontros.CLAREIRAS[0]
        tocha=next(o for o in encontros.objetos(j) if o.id=='tocha_vigilia')
        encontros.interagir(j,tocha);self.assertFalse(j.tochas)
        j.flags.update('inimigo_'+str(x) for x in c.membros)
        nucleo=next(o for o in encontros.objetos(j) if o.id=='nucleo_vigilia')
        encontros.interagir(j,nucleo);encontros.interagir(j,nucleo)
        self.assertEqual((j.bolsa.estoque['globo'],j.bolsa.estoque['semente_luz']),(1,1))
        encontros.interagir(j,tocha);self.assertEqual(j.tochas,{'vigilia'})
        self.assertEqual(j.bolsa.estoque['semente_luz'],0)
        j.recolocar((1700,CHAO));j.camera=1250;j.lume.energia=0
        pygame.init();self.addCleanup(pygame.quit)
        luz=pygame.Surface((960,540));compor_luz(luz,j,j.camera,0,1)
        self.assertEqual(luz.get_at((450,300))[:3],(255,255,255))
        novo=Jornada.carregar(j.salvar());self.assertTrue(luzes_mundo.zonas(novo))
        self.assertTrue(ponto_visivel(novo,(1700,300)))
        novo.flags.difference_update('inimigo_'+str(x) for x in c.membros)
        novo.entrar(0);self.assertTrue(any(e.origem[0]==1595 and e.ativo for e in novo.inimigos))
        self.assertTrue(luzes_mundo.zonas(novo))

    def test_k_cega_no_escuro_mas_nao_na_zona_acesa(self):
        from src.taticas import Habitante
        for iluminada in (False,True):
            j=Jornada();j.recolocar((1600,CHAO));e=Habitante('aranha',1700,CHAO)
            j.inimigos=[e]
            if iluminada:j.tochas.add('vigilia')
            j.update(.02,Comando(clarao=True))
            self.assertEqual(e.cego>0,not iluminada)
            if not iluminada:
                e.plano=[0];self.assertEqual(e.preparar(j.lume,()),'')


class CombosS08(unittest.TestCase):
    def test_j_l_j_e_k_l_sao_golpes_diferentes_sem_custo_natural(self):
        l=Lume(400,CHAO);a=l.arma
        nomes=[]
        for forte in (False,True,False):
            a.pedir(False,forte=forte)
            self.assertTrue(a.avancar(.001,l));nomes.append(a.tipo)
            total=a.perfil.total
            for _ in range(round(total*120)+1):a.avancar(1/120,l)
        self.assertEqual(nomes,['corte1','quebra','retorno']);self.assertEqual(l.energia,100)
        a.cancelar();a.clarao();a.pedir(False,forte=True);a.avancar(.001,l)
        self.assertEqual(a.tipo,'aurora')

    def test_luz_dobra_dano_consumo_e_resposta_ao_controle_l(self):
        a=App(temporaria=True)
        try:
            a.iniciar('historia');a.jogar()
            from collections import defaultdict
            teclas=defaultdict(bool);teclas[pygame.K_LCTRL]=True
            a.evento(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_l));a.atualizar(.02,teclas)
            self.assertEqual(a.jogo.lume.arma.tipo,'pesado');self.assertEqual(a.jogo.lume.energia,86)
            self.assertEqual(a.jogo.lume.arma.perfil.dano,4)
            a.desenhar()
        finally:a.mem.db.close();pygame.quit()

    def test_retorno_exponencial_tem_teto_e_dano_zera(self):
        j=Jornada();l=j.lume;l.energia=0
        ganhos=[]
        for _ in range(12):
            antes=l.energia;j.acertou_combo();ganhos.append(l.energia-antes)
        self.assertGreater(ganhos[-1],ganhos[0]*2)
        l.combo_acertos=10**8;l.energia=0;j.acertou_combo();self.assertLessEqual(l.energia,2.8)
        l.iframes=0;j.ferir();self.assertEqual(l.combo_acertos,0)
        l.energia=0;j.acertou_combo();self.assertAlmostEqual(l.energia,.35)


class EncontroS08(unittest.TestCase):
    def test_grupo_tem_papeis_e_avisos_escalonados(self):
        from src import encontros, luzes_mundo
        j=Jornada();j.recolocar((1580,CHAO));luzes_mundo.colocar(j);encontros.coordenar(j)
        grupo=[e for e in j.inimigos if e.grupo=='vigilia']
        self.assertEqual(len(grupo),3);self.assertEqual({e.papel for e in grupo},{'pressao','flanco','cobertura'})
        for e in grupo:e.rect.midbottom=(1600,CHAO);e.plano=[0]
        self.assertTrue(grupo[0].preparar(j.lume,()))
        self.assertEqual(grupo[1].preparar(j.lume,()),'')
        grupo[0].t=.1;grupo[1].plano=[0]
        self.assertTrue(grupo[1].preparar(j.lume,()))
        grupo[1].t=.1;grupo[2].plano=[0]
        self.assertEqual(grupo[2].preparar(j.lume,()),'')

    def test_morte_restaura_vida_posicao_e_ameacas_dos_sobreviventes(self):
        from src.combate import Projetil,Vetor
        j=Jornada();morto=j.inimigos[0];morto.ativo=False;morto.vida=0
        for e in j.inimigos[1:]:
            e.vida=1;e.rect.x+=80;e.estado='aviso';e.projeteis=[Projetil('fio',Vetor(e.rect.center),Vetor(100,0),3)]
        j.perder_fagulha();j.reiniciar()
        self.assertFalse(morto.ativo);self.assertEqual(morto.vida,0)
        for e in j.inimigos[1:]:
            self.assertEqual(e.vida,e.max_vida);self.assertEqual(e.rect.midbottom,e.origem)
            self.assertFalse(e.projeteis);self.assertEqual(e.estado,'patrulha')

    def test_game_over_na_app_recarrega_mobs_vivos_inteiros_e_nao_revive_derrotados(self):
        a=App(temporaria=True)
        try:
            a.iniciar('historia');a.jogar();j=a.jogo
            morto=j.inimigos[0];morto.ativo=False;j.flags.add('inimigo_'+str(morto.origem[0]))
            for e in j.inimigos[1:]:e.vida=1;e.rect.x+=130
            j.lume.vidas=1;j.lume.vida=0
            a.atualizar(.02);self.assertEqual(a.estado,'morte')
            a.atualizar(.5);a.selecao=0;a.ativar()
            for e in a.jogo.inimigos:
                if e.origem==morto.origem:
                    self.assertFalse(e.ativo);continue
                self.assertEqual(e.vida,e.max_vida);self.assertEqual(e.rect.midbottom,e.origem)
        finally:a.mem.db.close();pygame.quit()

    def test_patruha_em_execucao_produz_ataques_de_varios_membros(self):
        from src import luzes_mundo
        j=Jornada();j.recolocar((1580,CHAO));j.lume.iframes=999
        luzes_mundo.colocar(j)
        ataques=set();simultaneos=0
        for _ in range(420):
            j.update(1/60)
            grupo=[e for e in j.inimigos if e.grupo=='vigilia']
            ataques.update(e.origem[0] for e in grupo if e.estado=='investida')
            simultaneos=max(simultaneos,sum(e.estado in ('aviso','investida') for e in grupo))
        self.assertGreaterEqual(len(ataques),2);self.assertEqual(simultaneos,2)


class TutorialS08(unittest.TestCase):
    def test_inicio_ensina_durante_o_movimento_sem_pausar_e_persiste(self):
        j=Jornada();origem=j.lume.rect.x
        for _ in range(30):j.update(1/60,Comando(mover=1))
        self.assertGreater(j.lume.rect.x,origem);self.assertEqual(j.estado,'jogando')
        self.assertIn('primeiros_passos',j.tutorial);self.assertTrue(j.ensino_texto)
        novo=Jornada.carregar(j.salvar());self.assertIn('primeiros_passos',novo.tutorial)

    def test_item_novo_e_mecanica_da_subida_sao_explicados_no_local(self):
        from src.tutorial import atualizar
        j=Jornada(etapa=1);j.bolsa.receber('globo',1);j.bolsa.estoque['balsamo']=0
        atualizar(j,Comando());self.assertIn('item_globo',j.tutorial)
        self.assertIn('permanentemente',j.ensino_texto)
        j=Jornada();j.recolocar((2150,CHAO));atualizar(j,Comando())
        self.assertIn('parede',j.tutorial);self.assertIn('parede oposta',j.ensino_texto)


if __name__=='__main__':unittest.main()
