"""
Suite completa de testes para o componente WindowTitleBar.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

from view.components.window_title_bar import WindowTitleBar
from view.infrastructure.layout_loader import LayoutLoader


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def title_bar():
    """Retorna um WindowTitleBar com LayoutLoader configurado."""
    LayoutLoader._instance = None
    l = LayoutLoader.instance()
    l.set_screen(1920, 1080)
    return WindowTitleBar(titulo="Teste Janela")


class TestWindowTitleBar:
    """
    Testes para o componente WindowTitleBar.

    Verifica titulo, botoes, signals e estrutura basica.
    """

    def test_object_name(self, title_bar):
        """O WindowTitleBar deve ter objectName 'window_title_bar'."""
        assert title_bar.objectName() == "window_title_bar"

    def test_titulo_texto(self, title_bar):
        """
        O QLabel do titulo deve exibir o texto passado no construtor.
        """
        label = title_bar.findChild(QLabel, "window_title_text")
        assert label is not None
        assert label.text() == "Teste Janela"

    def test_botao_fechar_existe(self, title_bar):
        """
        O botao de fechar (✕) deve existir com objectName 'window_close_button'.
        """
        btn = title_bar.findChild(QPushButton, "window_close_button")
        assert btn is not None
        assert btn.text() == "\u2715"

    def test_close_signal(self, title_bar, qtbot):
        """
        Ao clicar no botao fechar, o signal close_requested deve ser emitido.
        """
        btn = title_bar.findChild(QPushButton, "window_close_button")
        with qtbot.waitSignal(title_bar.close_requested, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
