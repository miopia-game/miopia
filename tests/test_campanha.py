"""Campanha completa por teclado, sem atribuir itens, posições ou vitória ao modelo."""
import unittest
import pygame

from src.fases import ARENA, RAIZ, SAIDA, CHAO
from tests.test_travessia import Percurso


def acertar_marca(a, encontro):
    lume = a.lume
    x, y = encontro._marca()
    alvo = x - 18
    subir = encontro.indice != 1 and lume.chao and lume.rect.bottom > CHAO - 31
    if encontro.indice == 3:
        perto = lume.rect.bottom <= CHAO-32 and abs(lume.rect.centerx-x) < 100
        return alvo, {"salto": subir, "clarao": perto}

    # A entrada J só deve ocorrer com a marca ao alcance da direção atual.
    ataque = pygame.FRect(0,0,69,lume.rect.h+30)
    ataque.centery = lume.rect.centery
    if lume.face > 0:
        ataque.left = lume.rect.centerx
    else:
        ataque.right = lume.rect.centerx
    marca = pygame.FRect(x-18,y-19,36,38)
    alto = encontro.indice == 1 or lume.rect.bottom < CHAO-30
    acertar = ataque.colliderect(marca) and alto
    comandos = {"salto": subir, "golpe": acertar}
    if abs(lume.rect.centerx-alvo) < 8 and not acertar:
        comandos["mover"] = 1
    return alvo, comandos


def resolver_arena(a):
    soou = -1
    for _ in range(2400):
        e = a.jogo.boss
        l = a.lume
        if l.vida < 38 and a.jogo.bolsa.estoque["balsamo"]:
            a.tomar_balsamo()
        alvo, cmd = ARENA+80, {}
        if e and e.vencido:
            return
        if e and e.estado.startswith('coro_'):
            from src.ultimo_chamado import alvo as alvo_final
            alvo,_=alvo_final(e)
            perto=abs(l.rect.centerx-alvo)<65
            cmd={'interagir':perto and e.coro_gota,'clarao':perto and l.pulso_cd<=0}
            if e.estado=='coro_investida' and abs(e.x-l.rect.centerx)<150:
                cmd['salto']=l.chao
        elif e and e.estado == "aberto":
            alvo, cmd = acertar_marca(a,e)
        elif e and e.indice == 0:
            alvo, cmd = ARENA+75, {"baixo": True}
            if e.estado in ("aviso","investida") and e.asa_rasteira:
                # Ler a faixa e pular quando a asa estiver se aproximando. Sob
                # o voo alto o piloto segue agachado junto da raiz marcada.
                cmd={"salto": e.estado=="investida" and abs(e.x-l.rect.centerx)<160 and l.chao}
        elif e and e.indice == 1:
            alvo, cmd = e.valvula, {"interagir":bool(e.interacao(l.rect))}
        elif e and e.indice == 2:
            if e.estado == "flor":
                alvo = e.entalhe-20
            elif e.assentado:
                alvo = e.brasa
                cmd["interagir"] = bool(e.interacao(l.rect))
            elif e.engatado:
                alvo = e.entalhe+22
            else:
                alvo = e.barrel_x-15
                cmd["interagir"] = bool(e.interacao(l.rect))
            if e.estado == "investida" and abs(e.x-l.rect.centerx)<100 and not e.engatado:
                cmd["salto"] = l.chao
        elif e and e.indice == 3:
            if soou == e.progresso:
                alvo = e.dir-45
                if e.estado == "investida" and abs(e.x-l.rect.centerx)<158:
                    cmd["salto"] = l.chao
            else:
                alvo = e.valvula
                if e.interacao(l.rect):
                    cmd["interagir"] = True
                    if e.sino_movido:
                        soou = e.progresso
        if "mover" not in cmd and abs(alvo-l.rect.centerx)>4:
            cmd["mover"] = 1 if alvo>l.rect.centerx else -1
        a.tick(segurar_salto=True, **cmd)
    raise AssertionError(f"Guardiã do bioma {a.jogo.etapa} ainda guarda a saída. "
                         f"Lume {a.lume.vida:g}, estado {a.jogo.estado}, "
                         f"fase {e.estado if e else 'fora'}, aberturas {e.progresso if e else 0}.")


class CampanhaTest(unittest.TestCase):
    def test_quatro_biomas_ate_reencontrar_a_colonia(self):
        a = Percurso()
        for i, caminho in enumerate((a.bosque,a.corrego,a.taquaral,a.gruta)):
            self.assertEqual(a.jogo.etapa,i)
            caminho()
            self.assertGreaterEqual(a.jogo.orvalhos,3)
            resolver_arena(a)
            self.assertIn("chefe",a.jogo.flags)
            self.assertEqual(a.jogo.boss.progresso,a.jogo.boss.meta)
            a.ir(RAIZ)
            a.usar()
            self.assertEqual(a.jogo.restauradas,i+1)
            a.ir(SAIDA)
            a.usar()
        self.assertEqual(a.jogo.estado,"vitoria")


if __name__ == "__main__":
    unittest.main()
