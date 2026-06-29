import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

from view.components.anexo_preview import AnexoPreview


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def preview():
    return AnexoPreview(metadados="3 anexo(s)")


class TestAnexoPreview:
    def test_object_name(self, preview):
        assert preview.objectName() == "anexo_preview"

    def test_property_class(self, preview):
        assert preview.property("class") == "anexo_preview"

    def test_metadados_exibidos(self, preview):
        meta = preview.findChild(QLabel, "anexo_metadados")
        assert meta is not None
        assert meta.text() == "3 anexo(s)"

    def test_botao_ver_anexos(self, preview):
        btn = preview.findChild(QPushButton, "btn_ver_anexos")
        assert btn is not None
        assert btn.text() == "Ver Anexos"

    def test_signal_ver_todos(self, preview, qtbot):
        btn = preview.findChild(QPushButton, "btn_ver_anexos")
        with qtbot.waitSignal(preview.ver_todos_anexos, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_thumbnail_default_vazio(self, preview):
        thumb = preview.findChild(QLabel, "anexo_thumbnail")
        assert thumb.pixmap() is None or thumb.pixmap().isNull()
