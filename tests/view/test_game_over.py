"""
Suite de testes para o widget GameOver.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

from view.expediente.paginas.game_over import GameOver


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def game_over():
    """Retorna uma GameOver com pontuacao 3000.0."""
    return GameOver(pontuacao_global=3000.0)


class TestEstrutura:
    """
    Testes de estrutura basica da GameOver.

    Verifica objectName, property class e componentes principais.
    """

    def test_object_name(self, game_over):
        """A GameOver deve ter objectName 'game_over'."""
        assert game_over.objectName() == "game_over"

    def test_property_class(self, game_over):
        """A GameOver deve ter property class 'game_over'."""
        assert game_over.property("class") == "game_over"

    def test_titulo_existe(self, game_over):
        """A GameOver deve conter um QLabel 'label_endgame_titulo' com texto de derrota."""
        titulo = game_over.findChild(QLabel, "label_endgame_titulo")
        assert titulo is not None
        assert titulo.text() == "EXPEDIENTE INTERROMPIDO"

    def test_pontuacao_existe(self, game_over):
        """A GameOver deve conter um QLabel 'label_endgame_pontuacao' com a pontuacao."""
        pont = game_over.findChild(QLabel, "label_endgame_pontuacao")
        assert pont is not None
        assert "3000.0" in pont.text()

    def test_btn_jogar_novamente_existe(self, game_over):
        """A GameOver deve conter um QPushButton 'btn_jogar_novamente'."""
        btn = game_over.findChild(QPushButton, "btn_jogar_novamente")
        assert btn is not None
        assert btn.text() == "Jogar de Novo"

    def test_btn_voltar_menu_existe(self, game_over):
        """A GameOver deve conter um QPushButton 'btn_voltar_menu'."""
        btn = game_over.findChild(QPushButton, "btn_voltar_menu")
        assert btn is not None
        assert btn.text() == "Voltar ao Menu"

    def test_btn_sair_jogo_existe(self, game_over):
        """A GameOver deve conter um QPushButton 'btn_sair_jogo'."""
        btn = game_over.findChild(QPushButton, "btn_sair_jogo")
        assert btn is not None
        assert btn.text() == "Sair do Jogo"


class TestSignals:
    """
    Testes dos sinais da GameOver.
    """

    def test_voltar_menu_signal(self, game_over, qtbot):
        """Clicar em voltar ao menu deve emitir voltar_menu_solicitado."""
        btn = game_over.findChild(QPushButton, "btn_voltar_menu")
        with qtbot.waitSignal(game_over.voltar_menu_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_jogar_novamente_signal(self, game_over, qtbot):
        """Clicar em jogar de novo deve emitir jogar_novamente_solicitado."""
        btn = game_over.findChild(QPushButton, "btn_jogar_novamente")
        with qtbot.waitSignal(game_over.jogar_novamente_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
