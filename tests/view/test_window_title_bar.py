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
    return WindowTitleBar(titulo="Teste Janela", altura=32)


class TestWindowTitleBar:
    """
    Testes para o componente WindowTitleBar.

    Verifica titulo, 3 botoes (minimize, maximize, close),
    signals, titulo dinamico e funcionalidade de arrasto.
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

    def test_botao_minimizar_existe(self, title_bar):
        """O botao minimizar (—) deve existir com objectName 'window_minimize_button'."""
        btn = title_bar.findChild(QPushButton, "window_minimize_button")
        assert btn is not None
        assert btn.text() == "\u2014"

    def test_botao_maximizar_existe(self, title_bar):
        """O botao maximizar (□) deve existir com objectName 'window_maximize_button'."""
        btn = title_bar.findChild(QPushButton, "window_maximize_button")
        assert btn is not None
        assert btn.text() == "\u25a1"

    def test_close_signal(self, title_bar, qtbot):
        """
        Ao clicar no botao fechar, o signal close_requested deve ser emitido.
        """
        btn = title_bar.findChild(QPushButton, "window_close_button")
        with qtbot.waitSignal(title_bar.close_requested, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_minimizar_signal(self, title_bar, qtbot):
        """Ao clicar no botao minimizar, o signal minimized_solicitado deve ser emitido."""
        btn = title_bar.findChild(QPushButton, "window_minimize_button")
        with qtbot.waitSignal(title_bar.minimized_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_maximizar_signal(self, title_bar, qtbot):
        """Ao clicar no botao maximizar, o signal maximized_solicitado deve ser emitido."""
        btn = title_bar.findChild(QPushButton, "window_maximize_button")
        with qtbot.waitSignal(title_bar.maximized_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_alterna_maximizar_restaurar(self, title_bar):
        """set_maximizado(True) deve mudar icone para ❐; set_maximizado(False) para □."""
        btn = title_bar.findChild(QPushButton, "window_maximize_button")
        title_bar.set_maximizado(True)
        assert btn.text() == "\u2750"
        title_bar.set_maximizado(False)
        assert btn.text() == "\u25a1"

    def test_definir_titulo_dinamico(self, title_bar):
        """definir_titulo() deve alterar o texto do QLabel."""
        label = title_bar.findChild(QLabel, "window_title_text")
        title_bar.definir_titulo("Novo Titulo")
        assert label.text() == "Novo Titulo"

    def test_altura_personalizada(self):
        """WindowTitleBar deve aceitar altura personalizada no construtor."""
        bar = WindowTitleBar(titulo="Teste", altura=48)
        assert bar.height() == 48

    def test_click_close_nao_dispara_minimize(self, title_bar, qtbot):
        """Clicar no close nao deve disparar minimized_solicitado."""
        signals = []
        title_bar.minimized_solicitado.connect(lambda: signals.append("min"))
        btn = title_bar.findChild(QPushButton, "window_close_button")
        qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert len(signals) == 0
