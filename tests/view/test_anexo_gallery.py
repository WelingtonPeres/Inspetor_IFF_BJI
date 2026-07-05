import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QStackedWidget

from view.screens.anexo_gallery import AnexoGallery


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def gallery():
    return AnexoGallery()


class TestAnexoGallery:
    def test_object_name(self, gallery):
        assert gallery.objectName() == "anexo_gallery"

    def test_property_class(self, gallery):
        assert gallery.property("class") == "anexo_gallery"

    def test_botoes_navegacao(self, gallery):
        assert gallery.findChild(QPushButton, "gallery_prev_button") is not None
        assert gallery.findChild(QPushButton, "gallery_next_button") is not None
        assert gallery.findChild(QPushButton, "gallery_close_button") is not None

    def test_indicador_inicial(self, gallery):
        indicador = gallery.findChild(QLabel, "gallery_indicador")
        assert indicador.text() == "0 / 0"

    def test_carregar_anexos_vazio(self, gallery):
        gallery.carregar_anexos([])
        indicador = gallery.findChild(QLabel, "gallery_indicador")
        assert indicador.text() == "0 / 0"

    def test_carregar_anexos_imagem(self, gallery):
        anexos = [
            {"tipo_midia": "IMAGEM", "caminho_arquivo": ""},
            {"tipo_midia": "VIDEO", "caminho_arquivo": ""},
        ]
        gallery.carregar_anexos(anexos)
        stack = gallery.findChild(QStackedWidget, "gallery_stack")
        assert stack.count() == 2
        indicador = gallery.findChild(QLabel, "gallery_indicador")
        assert indicador.text() == "1 / 2"

    def test_navegacao_proximo(self, gallery, qtbot):
        anexos = [
            {"tipo_midia": "IMAGEM", "caminho_arquivo": ""},
            {"tipo_midia": "IMAGEM", "caminho_arquivo": ""},
        ]
        gallery.carregar_anexos(anexos)
        btn = gallery.findChild(QPushButton, "gallery_next_button")
        qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        indicador = gallery.findChild(QLabel, "gallery_indicador")
        assert indicador.text() == "2 / 2"

    def test_signal_fechar(self, gallery, qtbot):
        with qtbot.waitSignal(gallery.fechar_solicitado, timeout=1000):
            gallery.fechar_solicitado.emit()
