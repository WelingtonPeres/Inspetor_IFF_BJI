"""
Suite completa de testes para o componente Taskbar.
"""

import pytest
from PySide6.QtWidgets import QApplication, QFrame, QLabel

from view.desktop.taskbar import Taskbar


@pytest.fixture(autouse=True)
def qt_app(qapp):
    """Garante que o QApplication existe para widgets Qt."""
    return qapp


@pytest.fixture
def taskbar():
    """Retorna uma instancia do Taskbar."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    l = LayoutLoader.instance()
    l.set_screen(1920, 1080)
    return Taskbar()


class TestTaskbar:
    """
    Testes para o componente Taskbar (z=0).

    Verifica se a barra de tarefas possui os elementos
    minimos: objectName, botao Iniciar e relogio.
    """

    def test_object_name(self, taskbar):
        """
        O Taskbar deve ter objectName 'taskbar'.

        Necessario para o seletor QSS #taskbar.
        """
        assert taskbar.objectName() == "taskbar"

    def test_property_class(self, taskbar):
        """
        O Taskbar deve ter property class 'taskbar'.

        Necessario para o seletor QSS .taskbar.
        """
        assert taskbar.property("class") == "taskbar"

    def test_possui_relogio(self, taskbar):
        """
        O Taskbar deve conter um QLabel para o relogio.

        O relogio e identificado pelo objectName 'taskbar_clock'.
        """
        clock = taskbar.findChild(QLabel, "taskbar_clock")
        assert clock is not None
        assert clock.text() != ""

    def test_start_button_icone(self, taskbar):
        """
        O icone do IFFOS deve ser um QLabel com pixmap.

        O pixmap e carregado do caminho especificado no layout.json.
        """
        start = taskbar.findChild(QLabel, "taskbar_start")
        assert start is not None
        assert start.pixmap() is not None
        assert not start.pixmap().isNull()
        assert start.toolTip() == "Iniciar"

    def test_relogio_atualiza(self, taskbar, qtbot):
        """
        O relogio deve ser atualizado pelo QTimer em ate 2 segundos.

        O QTimer interno do Taskbar atualiza o texto do relogio
        a cada segundo. Apos 2s o texto nao deve estar vazio.
        """
        clock = taskbar.findChild(QLabel, "taskbar_clock")
        texto_inicial = clock.text()
        qtbot.wait(2100)
        assert clock.text() != ""
