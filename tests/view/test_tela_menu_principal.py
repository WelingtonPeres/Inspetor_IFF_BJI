"""
Suite completa de testes para a TelaMenuPrincipal.
"""

import pytest
from PySide6.QtWidgets import QLabel

from view.desktop.menu import TelaMenuPrincipal


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def tela():
    """Retorna uma TelaMenuPrincipal com LayoutLoader configurado."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    l = LayoutLoader.instance()
    l.set_screen(1920, 1080)
    return TelaMenuPrincipal()


class TestTelaMenuPrincipal:
    """
    Testes para a tela de menu principal (desktop z=1).

    Verifica a composicao dos elementos: wallpaper, shortcuts e logo.
    """

    def test_object_name(self, tela):
        """A TelaMenuPrincipal deve ter objectName 'tela_menu_principal'."""
        assert tela.objectName() == "tela_menu_principal"

    def test_wallpaper_carregado(self, tela):
        """
        O wallpaper deve ser carregado como QLabel com pixmap.

        O QLabel com objectName 'wallpaper_label' deve existir
        e conter um QPixmap valido.
        """
        wallpaper = tela.findChild(QLabel, "wallpaper_label")
        assert wallpaper is not None
        assert wallpaper.pixmap() is not None
        assert not wallpaper.pixmap().isNull()

    def test_shortcuts_criados(self, tela):
        """
        A quantidade de shortcuts deve corresponder ao layout.json.

        O layout possui 3 atalhos na lista 'atalhos_lista'.
        """
        from view.desktop.desktop_shortcut import DesktopShortcut
        shortcuts = tela.findChildren(DesktopShortcut)
        assert len(shortcuts) >= 3

    def test_shortcut_iniciar_emite_signal(self, tela, qtbot):
        """
        O shortcut 'Iniciar\\nExpediente' deve emitir o signal
        iniciar_solicitado ao ser clicado.
        """
        from view.desktop.desktop_shortcut import DesktopShortcut
        from PySide6.QtCore import Qt

        atalho = None
        for child in tela.findChildren(DesktopShortcut):
            if "Iniciar" in child._DesktopShortcut__legenda:
                atalho = child
                break
        assert atalho is not None

        with qtbot.waitSignal(tela.iniciar_solicitado, timeout=1000) as blocker:
            qtbot.mouseClick(atalho, Qt.MouseButton.LeftButton)
        assert "Iniciar" in blocker.args[0]
