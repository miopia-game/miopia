"""Os ciclos usam quadros diferentes e a passada depende do deslocamento real."""
import pygame

from src import movimento_arte as arte
from src.travessia import Lume


def test_passada_nao_avanca_com_camera_estatica_pausa_ou_retorno():
    lume = Lume(80, 442)
    trilha = arte.deslocamento(lume, 80., 0.)
    arte.deslocamento(lume, 80., .1)
    assert trilha.distancia == trilha.velocidade == 0
    arte.deslocamento(lume, 92., .2)
    assert trilha.distancia == 12 and trilha.velocidade > 0
    arte.deslocamento(lume, 92., .2)
    assert trilha.distancia == 12
    arte.deslocamento(lume, 92., .3)
    assert trilha.distancia == 12 and trilha.velocidade == 0
    arte.deslocamento(lume, 322., .32)
    assert trilha.distancia == trilha.velocidade == 0


def test_todas_as_folhas_renderizam_os_16_quadros_distintos(app):
    assert arte.N_QUADROS == 16
    superficie = pygame.Surface((255, 210), pygame.SRCALPHA)
    for nome in arte._medidas():
        imagens = set()
        for indice in range(arte.N_QUADROS):
            superficie.fill((0, 0, 0, 0))
            caixa = arte.desenhar(superficie, nome, indice, 122, 147, (125, 95), 1)
            assert caixa.width > 20 and caixa.height > 14
            imagens.add(pygame.image.tobytes(superficie, "RGBA"))
        assert len(imagens) == arte.N_QUADROS, nome


def test_passada_se_inverte_ao_recuar_e_acompanha_a_face():
    ator = Lume(80, 442)
    arte.deslocamento(ator, 80., 0., -1)
    trilha = arte.deslocamento(ator, 70., .1, -1)
    assert trilha.distancia == 10
    arte.deslocamento(ator, 75., .2, -1)
    assert trilha.distancia == 5 and trilha.velocidade > 0


def test_assenta_a_pata_na_parada_e_retoma_da_mesma_pose():
    ator = Lume(80,442)
    arte.deslocamento(ator,80.,0.)
    passos = arte.deslocamento(ator,85.,.1)
    assert passos.quadro_passada(20.) == 4
    intermediario = arte.deslocamento(ator,85.,.15).quadro_passada(20.)
    assert 0 < intermediario < 4
    assert passos.quadro_passada(20.) == intermediario
    assert arte.deslocamento(ator,85.,.34).quadro_passada(20.) == 0
    assert arte.deslocamento(ator,86.,.35).quadro_passada(20.) == 1


def test_patas_e_ventre_mantem_contato_com_o_piso_em_cada_quadro(app):
    for nome in ("aranha","carabideo","caruncho","sombra","casco-oco","cobra","cobra-dos-bercos"):
        w,h,margem = arte._medidas()[nome]
        for i in range(arte.N_QUADROS):
            quadro = arte._cel(nome,i)
            assert quadro.get_bounding_rect(min_alpha=80).bottom == margem+h, (nome,i)


def test_morcego_avisa_em_voo_e_tecela_continua_segurando_o_fio():
    from src.arte_inimigos import ciclo

    for ident in ("morcego", "asa-fendida", "vespa"):
        assert len({ciclo(ident,"neutro","",i/60,None,74,0.) for i in range(180)}) == 16
        for fase, limites in (("preparacao",(0,4)),("ataque",(5,11)),("recuo",(12,15))):
            escolhas = [ciclo(ident,fase,"mergulho",0.,None,74,i/60) for i in range(61)]
            assert all(nome == ident+("-especial" if ident=="vespa" else "-golpe") for nome,_ in escolhas)
            assert set(i for _,i in escolhas) == set(range(limites[0],limites[1]+1))
    for ident in ("morcego","asa-fendida"):
        assert {ciclo(ident,"repouso","",i/60,None,74,0.) for i in range(150)} == {
            (ident+"-repouso",n) for n in range(16)}
    poses = {ciclo("tecela", "recuo", "queda", i/60, None, 146, .5) for i in range(300)}
    assert len(poses) == arte.N_QUADROS


def test_coruja_conserva_uma_silhueta_do_ombro_a_ponta_da_asa(app):
    for nome in ("coruja", "coruja-golpe", "coruja-especial"):
        for indice in range(arte.N_QUADROS):
            imagem, _, _ = arte._quadro(nome, indice, (164, 128), 1, 0)
            opacidade = pygame.mask.from_surface(imagem, 90)
            areas = sorted((m.count() for m in opacidade.connected_components()), reverse=True)
            assert areas[0] > 1600
            assert sum(areas[1:]) < 12, (nome, indice, areas)


def test_extremos_das_duas_asas_sobem_e_descem_juntos_no_voo(app):
    for nome in ("coruja", "coruja-golpe", "morcego", "asa-fendida"):
        alturas = [[], []]
        for indice in range(arte.N_QUADROS):
            imagem, caixa, _ = arte._quadro(nome, indice, (164, 128), 1, 0)
            silhueta = pygame.mask.from_surface(imagem, 100)
            faixa = max(1, caixa.width//8)
            for curva, inicio in zip(alturas, (caixa.left, caixa.right-faixa)):
                ys = [y for x in range(inicio, inicio+faixa)
                      for y in range(caixa.top, caixa.bottom) if silhueta.get_at((x,y))]
                curva.append(sum(ys)/len(ys))
        for curva in alturas:
            assert max(curva)-min(curva) >= 12, (nome, curva)
        # Nos extremos da batida da asa próxima, a outra também deve
        # percorrer ao menos metade de sua própria excursão no mesmo sentido.
        perto, longe = alturas
        alta, baixa = perto.index(min(perto)), perto.index(max(perto))
        assert longe[baixa]-longe[alta] > (max(longe)-min(longe))*.5, nome


def test_mascara_facial_da_coruja_permanece_registrada_no_voo(app):
    # Mede o disco facial claro em relação ao tronco. As penas das asas ficam fora do recorte.
    w, h, margem = arte._medidas()["coruja"]
    area = pygame.Rect(0, 0, round(w*.46), round(h*.50))
    area.center = round(margem+w*.68), round(margem+h*.50)
    rostos = []
    for i in range(arte.N_QUADROS):
        cel = arte._cel("coruja",i).subsurface(area)
        mascara = pygame.mask.from_threshold(cel,(248,229,207,255),(30,39,51,26))
        rostos.append(max(mascara.get_bounding_rects(), key=lambda r:r.w*r.h))
    for eixo in ("centerx","centery"):
        pontos = [getattr(r,eixo) for r in rostos]
        assert max(pontos)-min(pontos) <= 6
    for eixo in ("w","h"):
        medidas = [getattr(r,eixo) for r in rostos]
        assert max(medidas) < 1.25*min(medidas)


def test_disco_facial_tem_a_mesma_escala_entre_voo_e_golpes(app):
    from statistics import median

    medidas = []
    for nome in ("coruja","coruja-golpe","coruja-especial"):
        w,h,margem = arte._medidas()[nome]
        area = pygame.Rect(0,0,round(w*.46),round(h*.65))
        area.center = round(margem+w*.68),round(margem+h*.50)
        rostos = []
        for i in range(arte.N_QUADROS):
            cel = arte._cel(nome,i).subsurface(area)
            pigmento = pygame.mask.from_threshold(cel,(248,229,207,255),(30,39,51,26))
            rostos.append(max(pigmento.get_bounding_rects(),key=lambda r:r.w*r.h))
        medidas.append((median(r.w for r in rostos),median(r.h for r in rostos)))
    for eixo in zip(*medidas):
        assert max(eixo) <= min(eixo)*1.10


def test_cobra_da_ponte_se_desloca_na_espreita_e_apos_o_bote():
    from src.arte_combate import fase_da_criatura
    from src.arte_inimigos import ciclo
    from src.fauna_jardim import MoradorDaPonte

    cobra = MoradorDaPonte("cobra",2720,790,"normal")
    for estado in ("espreita","recuo_caca"):
        cobra.estado, cobra.t = estado,.30
        fase,p,tecnica = fase_da_criatura(cobra)
        escolhas = {ciclo("cobra",fase,tecnica,0.,arte.Passos(0.,0.,distancia=d),82,p)
                    for d in range(80)}
        assert escolhas == {("cobra",i) for i in range(arte.N_QUADROS)}


def test_todo_pacote_preserva_os_desenhos_fonte(app):
    import json
    import pytest
    from pathlib import Path
    Image = pytest.importorskip("PIL.Image", reason="Ferramentas de criação de arte")
    fontes = Path(__file__).resolve().parents[1]/"docs/arte/fontes/fauna-quadros"
    registro = json.loads((fontes/"registro.json").read_text())
    assert set(registro) == set(arte._medidas())
    for nome, folha in registro.items():
        escala = folha["escala"]
        w, h, margem = folha["medida"]
        with Image.open(fontes/(nome+".png")) as pintura:
            assert len(folha["quadros"]) == len({tuple(q[:4]) for q in folha["quadros"]}) == 16
            for i,(x0,y0,x1,y1,x,y) in enumerate(folha["quadros"]):
                recorte = pintura.crop((x0,y0,x1,y1)).convert("RGBA")
                tamanho = tuple(round(v*escala) for v in recorte.size)
                esperado = Image.new("RGBA",(w+2*margem,h+2*margem))
                esperado.paste(recorte.resize(tamanho,Image.Resampling.LANCZOS),(x,y))
                assert esperado.tobytes() == pygame.image.tobytes(arte._cel(nome,i),"RGBA"), (nome,i)


def test_o_render_da_coruja_conserva_a_escala_do_sprite(monkeypatch):
    from src import arte_inimigos as fauna

    medidas = []

    def observar(s, nome, indice, x, y, medida, lado, **kwargs):
        medidas.append(medida)

    monkeypatch.setattr(arte, "desenhar", observar)
    for fase in ("neutro", "ataque", "recuo"):
        for n in range(8):
            fauna.corpo(None, "coruja", fase, 100, 100, (164, 128),
                        1, n/10, n/8, "garra", centro=True)
    assert medidas == [(164, 128)] * 24
