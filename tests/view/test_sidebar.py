import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from view.expediente.widgets.sidebar import Sidebar


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def sidebar():
    return Sidebar()


class TestSidebar:
    def test_object_name(self, sidebar):
        assert sidebar.objectName() == "sidebar"

    def test_property_class(self, sidebar):
        assert sidebar.property("class") == "sidebar"

    def test_itens_criados(self, sidebar):
        botoes = sidebar.findChildren(QPushButton)
        assert len(botoes) == 4

    def test_apenas_reports_habilitado(self, sidebar):
        for btn in sidebar.findChildren(QPushButton):
            if btn.objectName() == "sidebar_reports":
                assert btn.isEnabled()
            else:
                assert not btn.isEnabled(), f"{btn.objectName()} deveria estar inativo"

    def test_signal_emitido(self, sidebar, qtbot):
        btn = sidebar.findChild(QPushButton, "sidebar_reports")
        with qtbot.waitSignal(sidebar.item_selecionado, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert blocker.args[0] == "reports"
