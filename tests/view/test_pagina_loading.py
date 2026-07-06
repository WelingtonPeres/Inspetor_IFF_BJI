"""
Suite de testes para a PaginaLoading.
"""

import pytest
from PySide6.QtWidgets import QLabel, QProgressBar

from view.expediente.paginas.loading import PaginaLoading


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def pagina():
    """Retorna uma PaginaLoading."""
    return PaginaLoading()


class TestEstrutura:
    """
    Testes de estrutura basica da PaginaLoading.

    Verifica objectName, property class e componentes principais.
    """

    def test_object_name(self, pagina):
        """A PaginaLoading deve ter objectName 'pagina_loading'."""
        assert pagina.objectName() == "pagina_loading"

    def test_property_class(self, pagina):
        """A PaginaLoading deve ter property class 'pagina_loading'."""
        assert pagina.property("class") == "pagina_loading"

    def test_label_loading_titulo_existe(self, pagina):
        """A pagina deve conter um QLabel 'label_loading_titulo'."""
        label = pagina.findChild(QLabel, "label_loading_titulo")
        assert label is not None
        assert label.text() == "IFF SISTEMA DE INSPEÇÃO"

    def test_label_loading_texto_existe(self, pagina):
        """A pagina deve conter um QLabel 'label_loading_texto'."""
        label = pagina.findChild(QLabel, "label_loading_texto")
        assert label is not None
        assert label.text() == "CARREGANDO EXPEDIENTE..."

    def test_progress_bar_range_zero(self, pagina):
        """A progress bar deve ter range 0 (modo indeterminado)."""
        progress = pagina.findChild(QProgressBar, "loading_progress_bar")
        assert progress is not None
        assert progress.minimum() == 0
        assert progress.maximum() == 0
