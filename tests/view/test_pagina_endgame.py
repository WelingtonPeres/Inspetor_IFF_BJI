"""
Suite de testes para a PaginaEndgame.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

from view.expediente.paginas.endgame import PaginaEndgame


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def pagina():
    """Retorna uma PaginaEndgame."""
    return PaginaEndgame()


class TestEstrutura:
    """
    Testes de estrutura basica da PaginaEndgame.

    Verifica objectName, property class e componentes principais.
    """

    def test_object_name(self, pagina):
        """A PaginaEndgame deve ter objectName 'pagina_endgame'."""
        assert pagina.objectName() == "pagina_endgame"

    def test_property_class(self, pagina):
        """A PaginaEndgame deve ter property class 'pagina_endgame'."""
        assert pagina.property("class") == "pagina_endgame"

    def test_titulo_existe(self, pagina):
        """A pagina deve conter um QLabel 'label_endgame_titulo'."""
        titulo = pagina.findChild(QLabel, "label_endgame_titulo")
        assert titulo is not None

    def test_pontuacao_existe(self, pagina):
        """A pagina deve conter um QLabel 'label_endgame_pontuacao'."""
        pont = pagina.findChild(QLabel, "label_endgame_pontuacao")
        assert pont is not None

    def test_btn_voltar_existe(self, pagina):
        """A pagina deve conter um QPushButton 'btn_voltar_menu'."""
        btn = pagina.findChild(QPushButton, "btn_voltar_menu")
        assert btn is not None
        assert btn.text() == "Voltar ao Menu"


class TestSignals:
    """
    Testes do signal voltar_menu_solicitado.
    """

    def test_voltar_signal(self, pagina, qtbot):
        """Clicar em voltar ao menu deve emitir voltar_menu_solicitado."""
        btn = pagina.findChild(QPushButton, "btn_voltar_menu")
        with qtbot.waitSignal(pagina.voltar_menu_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)


class TestComportamento:
    """
    Testes do metodo exibir_resultado.
    """

    @pytest.mark.parametrize("venceu,status_texto,status_prop", [
        (True, "EXPEDIENTE CONCLUÍDO", "vitoria"),
        (False, "EXPEDIENTE INTERROMPIDO", "derrota"),
    ])
    def test_exibir_resultado(self, pagina, venceu, status_texto, status_prop):
        """exibir_resultado deve definir texto e property status corretos."""
        pagina.exibir_resultado(pontuacao_global=5000.0, dias_concluidos=1, venceu=venceu)
        titulo = pagina.findChild(QLabel, "label_endgame_titulo")
        assert titulo.text() == status_texto
        assert titulo.property("status") == status_prop
        pont = pagina.findChild(QLabel, "label_endgame_pontuacao")
        assert "5000.0" in pont.text()
        assert "1" in pont.text()
