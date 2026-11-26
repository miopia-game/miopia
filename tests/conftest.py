"""Headless antes de importar pygame; nunca usar o perfil pessoal no pytest."""
import os
os.environ['SDL_VIDEODRIVER']='dummy'
os.environ['SDL_AUDIODRIVER']='dummy'
import pytest


@pytest.fixture(scope='session',autouse=True)
def perfil_qa(tmp_path_factory):
    anterior=os.environ.get('MIOPIA_DADOS')
    os.environ['MIOPIA_DADOS']=str(tmp_path_factory.mktemp('miopia-perfil'))
    yield
    if anterior is None:os.environ.pop('MIOPIA_DADOS',None)
    else:os.environ['MIOPIA_DADOS']=anterior


@pytest.fixture
def app():
    from src.main import App
    import pygame
    a=App(temporaria=True)
    # Consumir somente os eventos de criação da janela dummy, antes da
    # sequência testada. Perda de foco continua sendo testável por evento.
    pygame.event.get()
    yield a
    a.mem.db.close();pygame.quit()
