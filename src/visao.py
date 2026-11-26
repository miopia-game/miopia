"""Luz portátil de Lume e clarões que permanecem nas coordenadas do mundo."""
from dataclasses import dataclass
import math

DURACAO = 5.5
ALCANCE = 520

@dataclass(frozen=True)
class Vestigio:
    x: float
    y: float
    inicio: float
    duracao: float = DURACAO

    def raio(self, agora):
        idade = max(0., agora - self.inicio)
        if idade >= self.duracao:
            return 0
        if idade < .22:
            return round(92 + (ALCANCE - 92) * math.sin(idade / .22 * math.pi / 2))
        if idade <= 2.0:
            return ALCANCE
        u = (idade - 2.) / (self.duracao - 2.)
        return round(ALCANCE * (1. - u*u*(3.-2.*u)))


def fontes(j, *, vestigios=True):
    from .aula_sino import luzes as luz_do_sino
    from .resgates import fontes as fontes_vivas
    from .luzes_mundo import fontes as globos
    luzes=[(*j.lume.rect.center,j.raio)]
    if j.fagulha_ativa:
        f = j.fagulha_ativa
        luzes.append((*f.posicao(j.tempo),f.raio(j.tempo)))
    if vestigios:
        luzes.extend((v.x,v.y,v.raio(j.tempo)) for v in j.vestigios)
    luzes.extend(fontes_vivas(j))
    luzes.extend(globos(j))
    luzes.extend(luz_do_sino(j))
    if j.em_vertical:
        from .arquivo_casca import luzes as luzes_arquivo
        from .fauna_jardim import luzes as luzes_nectar
        from .fio_corte import luzes as luzes_fio
        luzes.extend(luzes_arquivo(j))
        luzes.extend(luzes_nectar(j))
        luzes.extend(luzes_fio(j))
    if j.boss and j.boss.estado.startswith('coro_'):
        from .ultimo_chamado import alvo
        luzes.append((*alvo(j.boss),70))
    return luzes


def ponto_visivel(j,ponto,margem=0,terrenos=None):
    """Luz atravessa o terreno; alcance e duração continuam limitando a visão.

    `terrenos` é aceito para compatibilidade com chamadas anteriores. Colisão
    física e percepção dos ataques são sistemas separados da iluminação.
    """
    from .luzes_mundo import zonas
    return any(z.collidepoint(ponto) for z in zonas(j)) or any(math.dist(ponto,(x,y))<=raio+margem and raio>0 for x,y,raio in fontes(j))
