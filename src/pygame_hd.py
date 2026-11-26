"""Superfícies de desenho com unidades de mundo e pixels físicos independentes.

O jogo desenha dois pixels por unidade em cada eixo. Uma superfície SDL entregue
por uma ferramenta externa conserva sua própria escala. Os recortes de atlas
originais permanecem em pixels até a transformação para o tamanho de jogo.
"""
import pygame as sdl


def __getattr__(nome):
    return getattr(sdl, nome)


def _tamanho(tamanho, escala):
    return tuple(round(eixo * escala) for eixo in tamanho)


def _retangulo(r, escala):
    x, y, w, h = r
    return sdl.Rect(round(x*escala), round(y*escala),
                    round((x+w)*escala)-round(x*escala), round((y+h)*escala)-round(y*escala))


def _logico(rect, escala):
    x, y = rect.x//escala, rect.y//escala
    return sdl.Rect(x, y, (rect.right+escala-1)//escala-x, (rect.bottom+escala-1)//escala-y)


def _envolver(pixels, tamanho, escala):
    s = object.__new__(Surface)
    s.pixels, s._tamanho, s.escala = pixels, tuple(tamanho), escala
    return s


def nativa(pixels, tamanho_logico):
    """Adota um raster HD já pronto no tamanho lógico declarado."""
    if pixels.get_size() != _tamanho(tamanho_logico, 2):
        raise ValueError("A imagem nativa deve ter dois pixels por unidade de jogo.")
    return _envolver(pixels, tamanho_logico, 2)


def destino(s):
    if isinstance(s, Surface):
        return s
    return _envolver(s, s.get_size(), 1)


class Surface:
    __slots__ = ("pixels", "_tamanho", "escala")

    def __init__(self, size, flags=0, depth=0):
        self._tamanho, self.escala = tuple(size), 2
        tamanho = _tamanho(size, self.escala)
        self.pixels = sdl.Surface(tamanho, flags, depth) if depth else sdl.Surface(tamanho, flags)

    def get_size(self):
        return self._tamanho

    def get_width(self):
        return self._tamanho[0]

    def get_height(self):
        return self._tamanho[1]

    def get_rect(self, **posicao):
        rect = sdl.Rect((0, 0), self._tamanho)
        for nome, valor in posicao.items():
            setattr(rect, nome, valor)
        return rect

    def copy(self):
        return _envolver(self.pixels.copy(), self._tamanho, self.escala)

    def get_alpha(self):
        return self.pixels.get_alpha()

    def set_alpha(self, alpha, flags=0):
        self.pixels.set_alpha(alpha, flags)

    def get_at(self, xy):
        return self.pixels.get_at(_tamanho(xy, self.escala))

    def get_bounding_rect(self, min_alpha=1):
        return _logico(self.pixels.get_bounding_rect(min_alpha=min_alpha), self.escala)

    def get_clip(self):
        return _logico(self.pixels.get_clip(), self.escala)

    def set_clip(self, area=None):
        self.pixels.set_clip(None if area is None else _retangulo(area, self.escala))

    def subsurface(self, area):
        r = sdl.Rect(area)
        return _envolver(self.pixels.subsurface(_retangulo(r, self.escala)), r.size, self.escala)

    def fill(self, cor, rect=None, special_flags=0):
        area = None if rect is None else _retangulo(rect, self.escala)
        return _logico(self.pixels.fill(cor, area, special_flags), self.escala)

    def blit(self, source, dest, area=None, special_flags=0):
        fonte = destino(source)
        imagem = fonte.pixels
        recorte = None if area is None else _retangulo(area, fonte.escala)
        if fonte.escala != self.escala:
            if recorte is not None:
                recorte = recorte.clip(imagem.get_rect())
                imagem = imagem.subsurface(recorte)
                recorte = None
            dimensoes = _tamanho(imagem.get_size(), self.escala/fonte.escala)
            imagem = sdl.transform.smoothscale(imagem, dimensoes)
        ponto = _tamanho((dest[0], dest[1]), self.escala)
        return _logico(self.pixels.blit(imagem, ponto, recorte, special_flags), self.escala)


def blit(dest, src, pos, area=None, special_flags=0):
    return destino(dest).blit(src, pos, area, special_flags)


class _Desenho:
    @staticmethod
    def rect(surface, color, rect, width=0, border_radius=0, **cantos):
        s = destino(surface)
        cantos = {nome: valor*s.escala if valor > 0 else valor for nome, valor in cantos.items()}
        r = sdl.draw.rect(s.pixels, color, _retangulo(rect, s.escala), width*s.escala,
                          border_radius*s.escala, **cantos)
        return _logico(r, s.escala)

    @staticmethod
    def line(surface, color, start_pos, end_pos, width=1):
        s = destino(surface)
        r = sdl.draw.line(s.pixels, color, _tamanho(start_pos, s.escala),
                          _tamanho(end_pos, s.escala), width*s.escala)
        return _logico(r, s.escala)

    @staticmethod
    def lines(surface, color, closed, points, width=1):
        s = destino(surface)
        r = sdl.draw.lines(s.pixels, color, closed, [_tamanho(p,s.escala) for p in points], width*s.escala)
        return _logico(r,s.escala)

    @staticmethod
    def aaline(surface, color, start_pos, end_pos):
        s = destino(surface)
        # O antialiasing acompanha frações de pixel físicas.
        pontos = [tuple(x*s.escala for x in p) for p in (start_pos, end_pos)]
        return _logico(sdl.draw.aaline(s.pixels, color, *pontos), s.escala)

    @staticmethod
    def aalines(surface, color, closed, points):
        s = destino(surface)
        pontos = [tuple(x*s.escala for x in p) for p in points]
        return _logico(sdl.draw.aalines(s.pixels, color, closed, pontos), s.escala)

    @staticmethod
    def polygon(surface, color, points, width=0):
        s = destino(surface)
        r = sdl.draw.polygon(s.pixels, color, [_tamanho(p,s.escala) for p in points], width*s.escala)
        return _logico(r,s.escala)

    @staticmethod
    def ellipse(surface, color, rect, width=0):
        s = destino(surface)
        return _logico(sdl.draw.ellipse(s.pixels, color, _retangulo(rect,s.escala), width*s.escala),s.escala)

    @staticmethod
    def circle(surface, color, center, radius, width=0, **quadrantes):
        s = destino(surface)
        r = sdl.draw.circle(s.pixels,color,_tamanho(center,s.escala),round(radius*s.escala),
                            width*s.escala,**quadrantes)
        return _logico(r,s.escala)

    @staticmethod
    def arc(surface, color, rect, start_angle, stop_angle, width=1):
        s = destino(surface)
        return _logico(sdl.draw.arc(s.pixels,color,_retangulo(rect,s.escala),start_angle,
                                    stop_angle,width*s.escala),s.escala)


class _Transformacao:
    @staticmethod
    def smoothscale(surface, size, dest_surface=None):
        fonte = destino(surface)
        alvo = destino(dest_surface) if dest_surface is not None else None
        escala = alvo.escala if alvo is not None else 2
        tamanho = _tamanho(size, escala)
        if alvo is None:
            pixels = sdl.transform.smoothscale(fonte.pixels, tamanho)
        else:
            pixels = sdl.transform.smoothscale(fonte.pixels, tamanho, alvo.pixels)
        return dest_surface if alvo is not None else _envolver(pixels, size, escala)

    @staticmethod
    def flip(surface, flip_x, flip_y):
        if not isinstance(surface, Surface):
            return sdl.transform.flip(surface, flip_x, flip_y)
        return _envolver(sdl.transform.flip(surface.pixels, flip_x, flip_y), surface.get_size(), surface.escala)

    @staticmethod
    def grayscale(surface):
        if not isinstance(surface, Surface):
            return sdl.transform.grayscale(surface)
        return _envolver(sdl.transform.grayscale(surface.pixels), surface.get_size(), surface.escala)

    @staticmethod
    def rotate(surface, angle):
        if not isinstance(surface, Surface):
            return sdl.transform.rotate(surface, angle)
        pixels = sdl.transform.rotate(surface.pixels, angle)
        size = tuple((n + surface.escala - 1)//surface.escala for n in pixels.get_size())
        dims = _tamanho(size,surface.escala)
        if dims != pixels.get_size():
            ajustada = sdl.Surface(dims, sdl.SRCALPHA)
            ajustada.blit(pixels,(0,0))
            pixels = ajustada
        return _envolver(pixels,size,surface.escala)


def silhueta(surface, cor):
    """Tinge os pixels opacos do desenho usando a mesma densidade do sprite."""
    fonte = destino(surface)
    mascara = sdl.mask.from_surface(fonte.pixels)
    pixels = mascara.to_surface(setcolor=cor, unsetcolor=(0,0,0,0))
    return _envolver(pixels, fonte.get_size(), fonte.escala)


draw = _Desenho()
transform = _Transformacao()
