"""
Suite de testes para o widget GameWin.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

from view.expediente.paginas.game_win import GameWin


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def game_win():
    """Retorna uma GameWin com pontuacao 5000.0."""
    return GameWin(pontuacao_global=5000.0)


class TestEstrutura:
    """
    Testes de estrutura basica da GameWin.

    Verifica objectName, property class e componentes principais.
    """

    def test_object_name(self, game_win):
        """A GameWin deve ter objectName 'game_win'."""
        assert game_win.objectName() == "game_win"

    def test_property_class(self, game_win):
        """A GameWin deve ter property class 'game_win'."""
        assert game_win.property("class") == "game_win"

    def test_titulo_existe(self, game_win):
        """A GameWin deve conter um QLabel 'label_endgame_titulo' com texto de vitoria."""
        titulo = game_win.findChild(QLabel, "label_endgame_titulo")
        assert titulo is not None
        assert titulo.text() == "EXPEDIENTE CONCLUÍDO"

    def test_pontuacao_existe(self, game_win):
        """A GameWin deve conter um QLabel 'label_endgame_pontuacao' com a pontuacao."""
        pont = game_win.findChild(QLabel, "label_endgame_pontuacao")
        assert pont is not None
        assert "5000.0" in pont.text()

    def test_btn_jogar_novamente_existe(self, game_win):
        """A GameWin deve conter um QPushButton 'btn_jogar_novamente'."""
        btn = game_win.findChild(QPushButton, "btn_jogar_novamente")
        assert btn is not None
        assert btn.text() == "Jogar de Novo"

    def test_btn_voltar_menu_existe(self, game_win):
        """A GameWin deve conter um QPushButton 'btn_voltar_menu'."""
        btn = game_win.findChild(QPushButton, "btn_voltar_menu")
        assert btn is not None
        assert btn.text() == "Voltar ao Menu"

    def test_btn_sair_jogo_existe(self, game_win):
        """A GameWin deve conter um QPushButton 'btn_sair_jogo'."""
        btn = game_win.findChild(QPushButton, "btn_sair_jogo")
        assert btn is not None
        assert btn.text() == "Sair do Jogo"


class TestSignals:
    """
    Testes dos sinais da GameWin.
    """

    def test_voltar_menu_signal(self, game_win, qtbot):
        """Clicar em voltar ao menu deve emitir voltar_menu_solicitado."""
        btn = game_win.findChild(QPushButton, "btn_voltar_menu")
        with qtbot.waitSignal(game_win.voltar_menu_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_jogar_novamente_signal(self, game_win, qtbot):
        """Clicar em jogar de novo deve emitir jogar_novamente_solicitado."""
        btn = game_win.findChild(QPushButton, "btn_jogar_novamente")
        with qtbot.waitSignal(game_win.jogar_novamente_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
