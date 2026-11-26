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


def test_todas_as_folhas_renderizam_os_24_quadros_distintos(app):
    assert arte.N_QUADROS == 24
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
    assert passos.quadro_passada(20.) == 6
    intermediario = arte.deslocamento(ator,85.,.15).quadro_passada(20.)
    assert 0 < intermediario < 6
    assert passos.quadro_passada(20.) == intermediario
    assert arte.deslocamento(ator,85.,.34).quadro_passada(20.) == 0
    assert arte.deslocamento(ator,86.,.35).quadro_passada(20.) == 1


def test_patas_e_ventre_mantem_contato_com_o_piso_em_cada_quadro(app):
    for nome in ("aranha","carabideo","caruncho","sombra","casco-oco","cobra","cobra-dos-bercos"):
        w,h,margem = arte._medidas()[nome]
        folha = arte._folha(nome)
        cw,ch = w+2*margem,h+2*margem
        for i in range(arte.N_QUADROS):
            quadro = folha.subsurface((i%arte.COLUNAS*cw,i//arte.COLUNAS*ch,cw,ch))
            assert quadro.get_bounding_rect(min_alpha=80).bottom == margem+h, (nome,i)


def test_morcego_avisa_em_voo_e_tecela_continua_segurando_o_fio():
    from src.arte_inimigos import ciclo

    for ident in ("morcego", "asa-fendida", "vespa"):
        for tempo in (.07, .83, 31.23):
            antes = ciclo(ident, "neutro", "", tempo, None, 74, 0)
            aviso = ciclo(ident, "preparacao", "mergulho", tempo, None, 74, .3)
            assert antes == aviso
    assert ciclo("morcego", "repouso", "", 1., None, 74, 0.) is None
    poses = {ciclo("tecela", "recuo", "queda", i/60, None, 146, .5) for i in range(60)}
    assert len(poses) == arte.N_QUADROS


def test_coruja_conserva_uma_silhueta_do_ombro_a_ponta_da_asa(app):
    for nome in ("coruja", "coruja-impulso"):
        for indice in range(arte.N_QUADROS):
            imagem, _, _ = arte._quadro(nome, indice, (164, 128), 1, 0)
            opacidade = pygame.mask.from_surface(imagem, 90)
            areas = sorted((m.count() for m in opacidade.connected_components()), reverse=True)
            assert areas[0] > 1600
            assert sum(areas[1:]) < 12, (nome, indice, areas)


def test_extremos_das_duas_asas_sobem_e_descem_juntos_no_voo(app):
    for nome in ("coruja", "coruja-impulso", "morcego", "asa-fendida"):
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


def test_cabeca_da_coruja_tem_o_mesmo_desenho_em_cada_batida(app):
    # Coordenadas na célula sem margem. O contorno acompanha a crista,
    # a máscara e o bico. A asa distante pode passar pelo espaço ao redor.
    rostos = {
        "coruja": [(63,16),(68,10),(76,13),(79,10),(90,17),(97,24),
                   (101,32),(101,38),(99,41),(98,43),(94,43),(90,48),
                   (79,44),(65,38),(60,29)],
        "coruja-impulso": [(79,65),(122,65),(122,107),(79,107)],
    }
    for nome, contorno in rostos.items():
        w, h, margem = arte._medidas()[nome]
        largura, altura = w + margem*2, h + margem*2
        mascara = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.polygon(mascara, "white", [(x+margem,y+margem) for x,y in contorno])
        folha = arte._folha(nome)
        imagens = set()
        for indice in range(arte.N_QUADROS):
            linha, coluna = divmod(indice, arte.COLUNAS)
            celula = folha.subsurface((coluna*largura,linha*altura,largura,altura)).copy()
            celula.blit(mascara,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
            imagens.add(pygame.image.tobytes(celula, "RGBA"))
        assert len(imagens) == 1, nome


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
