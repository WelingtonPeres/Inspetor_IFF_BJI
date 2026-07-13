"""
Suite completa de testes para o componente DesktopShortcut.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from view.desktop.desktop_shortcut import DesktopShortcut


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def shortcut():
    """Retorna um DesktopShortcut com icone real (admin.png)."""
    from view.infrastructure.layout_loader import LayoutLoader
    l = LayoutLoader()
    l.set_screen(1920, 1080)
    return DesktopShortcut(
        legenda="Iniciar\nExpediente",
        icone_arquivo="admin.png",
        layout_loader=l,
    )


@pytest.fixture
def shortcut_sem_icone():
    """Retorna um DesktopShortcut sem icone (fallback texto)."""
    from view.infrastructure.layout_loader import LayoutLoader
    l = LayoutLoader()
    l.set_screen(1920, 1080)
    return DesktopShortcut(
        legenda="Teste",
        icone_arquivo="",
        layout_loader=l,
    )


@pytest.fixture
def shortcut_icone_inexistente():
    """Retorna um DesktopShortcut com icone_arquivo que nao existe em nenhum diretorio."""
    from view.infrastructure.layout_loader import LayoutLoader
    l = LayoutLoader()
    l.set_screen(1920, 1080)
    return DesktopShortcut(
        legenda="Teste",
        icone_arquivo="nao_existe.png",
        layout_loader=l,
    )


class TestDesktopShortcut:
    """
    Testes para o componente DesktopShortcut.

    Verifica objectName, class, tamanho fixo, emissao de signal
    e fallback de icone.
    """

    def test_object_name(self, shortcut):
        """O DesktopShortcut deve ter objectName 'desktop_shortcut'."""
        assert shortcut.objectName() == "desktop_shortcut"

    def test_cursor_padrao_mouse(self, shortcut):
        """O DesktopShortcut deve ter cursor de mão (PointingHandCursor)."""
        from PySide6.QtCore import Qt

        assert shortcut.cursor().shape() == Qt.CursorShape.PointingHandCursor

    def test_tamanho_fixo(self, shortcut):
        """O DesktopShortcut deve ter largura 100 em resolucao referencia."""
        assert shortcut.width() == 100
        assert shortcut.height() == 100

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

    def test_icone_arquivo_inexistente_deve_usar_fallback_texto(
        self, shortcut_icone_inexistente
    ):
        """
        Fallback para ficheiro inexistente: quando o icone_arquivo
        nao e encontrado em nenhum diretorio, o QLabel do icone
        deve exibir '?' em vez de um QPixmap valido.
        """
        # Arrange
        icon_label = shortcut_icone_inexistente.findChild(QLabel, "shortcut_icon")

        # Act & Assert
        assert icon_label is not None, "QLabel 'shortcut_icon' deve existir"
        assert icon_label.text() == "?", (
            "Fallback deve exibir '?'"
        )
        assert icon_label.pixmap() is None or icon_label.pixmap().isNull(), (
            "Nao deve haver QPixmap valido definido"
        )

    def test_carregar_pixmap_deve_procurar_em_desktop_icons_primeiro(
        self, shortcut
    ):
        """
        Pixmap carregado com dimensoes validas: quando o icone_arquivo
        existe em desktop_Icons/, o QPixmap carregado deve ter
        largura e altura maiores que zero.
        """
        # Arrange
        icon_label = shortcut.findChild(QLabel, "shortcut_icon")

        # Act
        pixmap = icon_label.pixmap()

        # Assert
        assert pixmap is not None, "QPixmap deve existir"
        assert not pixmap.isNull(), "QPixmap nao deve ser nulo"
        assert pixmap.width() > 0, "QPixmap deve ter largura positiva"
        assert pixmap.height() > 0, "QPixmap deve ter altura positiva"

    def test_legenda_deve_ter_word_wrap_configurado_pelo_layout(self, shortcut):
        """
        Word wrap da legenda: o QLabel com objectName 'shortcut_label'
        deve ter wordWrap=True conforme definido no layout.json
        na seccao desktop_shortcut > legenda > word_wrap.
        """
        # Arrange
        label = shortcut.findChild(QLabel, "shortcut_label")

        # Act & Assert
        assert label is not None, "QLabel 'shortcut_label' deve existir"
        assert label.wordWrap() is True, (
            "wordWrap deve estar ativo conforme layout.json"
        )
