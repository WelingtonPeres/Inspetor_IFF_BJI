import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from view.expediente.overlays.media_viewer import MediaViewer


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def viewer():
    return MediaViewer()


class TestMediaViewer:
    def test_object_name(self, viewer):
        assert viewer.objectName() == "media_viewer"

    def test_property_class(self, viewer):
        assert viewer.property("class") == "media_viewer"

    def test_escondido_por_padrao(self, viewer):
        assert not viewer.isVisible()

    def test_signal_fechar_emitido(self, viewer, qtbot):
        with qtbot.waitSignal(viewer.fechar_solicitado, timeout=1000):
            viewer.fechar_solicitado.emit()

    def test_exibir_imagem_inexistente(self, viewer):
        viewer.exibir_imagem({"caminho_arquivo": "nao_existe.png"})
        assert viewer.isVisible()
