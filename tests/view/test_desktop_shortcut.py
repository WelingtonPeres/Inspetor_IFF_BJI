"""
Suite completa de testes para o componente DesktopShortcut.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from view.components.desktop_shortcut import DesktopShortcut


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def shortcut():
    """Retorna um DesktopShortcut com icone real (admin.png)."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    l = LayoutLoader.instance()
    l.set_screen(1920, 1080)
    return DesktopShortcut(legenda="Iniciar\nExpediente", icone_arquivo="admin.png")


@pytest.fixture
def shortcut_sem_icone():
    """Retorna um DesktopShortcut sem icone (fallback texto)."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    l = LayoutLoader.instance()
    l.set_screen(1920, 1080)
    return DesktopShortcut(legenda="Teste", icone_arquivo="")


class TestDesktopShortcut:
    """
    Testes para o componente DesktopShortcut.

    Verifica objectName, class, tamanho fixo, emissao de signal
    e fallback de icone.
    """

    def test_object_name(self, shortcut):
        """O DesktopShortcut deve ter objectName 'desktop_shortcut'."""
        assert shortcut.objectName() == "desktop_shortcut"

    def test_property_class(self, shortcut):
        """O DesktopShortcut deve ter property class 'desktop_shortcut'."""
        assert shortcut.property("class") == "desktop_shortcut"

    def test_tamanho_fixo(self, shortcut):
        """O DesktopShortcut deve ter largura 80 em resolucao referencia."""
        assert shortcut.width() == 80
        assert shortcut.height() == 90

    def test_emite_signal_ao_clicar(self, shortcut, qtbot):
        """
        Ao clicar no shortcut com o mouse, o signal clicked
        deve ser emitido com o texto da legenda.
        """
        with qtbot.waitSignal(shortcut.clicked, timeout=1000) as blocker:
            qtbot.mouseClick(shortcut, Qt.MouseButton.LeftButton)
        assert blocker.args[0] == "Iniciar\nExpediente"

    def test_pixmap_carregado(self, shortcut):
        """
        Quando o arquivo de icone existe, o QLabel do icone
        deve conter um QPixmap (nao texto).
        """
        icon_label = shortcut.findChild(QLabel, "shortcut_icon")
        assert icon_label is not None
        assert icon_label.pixmap() is not None
        assert not icon_label.pixmap().isNull()

    def test_fallback_texto(self, shortcut_sem_icone):
        """
        Quando nao ha arquivo de icone, o shortcut deve exibir
        texto no lugar do pixmap (fallback visual).
        """
        icon_label = shortcut_sem_icone.findChild(QLabel, "shortcut_icon")
        assert icon_label is not None
        assert icon_label.pixmap() is None or icon_label.pixmap().isNull()
        assert icon_label.text() != ""
