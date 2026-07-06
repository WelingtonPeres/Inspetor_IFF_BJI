"""
Suite completa de testes para o widget PaginaSelecaoPerfil.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QPushButton

from view.screens.pagina_selecao_perfil import PaginaSelecaoPerfil


@pytest.fixture(autouse=True)
def qt_app(qapp):
    """Garante que o QApplication existe para widgets Qt."""
    return qapp


@pytest.fixture
def pagina():
    """Retorna uma PaginaSelecaoPerfil com LayoutLoader configurado."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    l = LayoutLoader.instance()
    l.set_screen(1920, 1080)
    return PaginaSelecaoPerfil()


class TestEstrutura:
    """
    Testes de estrutura basica da PaginaSelecaoPerfil.

    Verifica objectName, property class e componentes principais.
    """

    def test_object_name(self, pagina):
        """
        A PaginaSelecaoPerfil deve ter objectName 'pagina_selecao_perfil'.

        Necessario para o seletor QSS #pagina_selecao_perfil.
        """
        # Arrange — fixture pagina ja instancia o widget

        # Act — obtem o objectName
        nome = pagina.objectName()

        # Assert
        assert nome == "pagina_selecao_perfil"

    def test_property_class(self, pagina):
        """
        A PaginaSelecaoPerfil deve ter property class 'pagina_selecao_perfil'.

        Necessario para o seletor QSS .pagina_selecao_perfil.
        """
        # Arrange — fixture pagina ja instancia o widget

        # Act — obtem a property "class"
        classe = pagina.property("class")

        # Assert
        assert classe == "pagina_selecao_perfil"

    def test_combo_perfil_tem_9_itens(self, pagina):
        """
        O QComboBox interno deve conter 9 itens de perfil.

        Os 9 itens correspondem aos perfis: DEFAULT, T_QUIMICA,
        T_INFORMATICA, T_AGROPECUARIA, T_ALIMENTOS, T_MEIO_AMBIENTE,
        T_ZOOTECNIA, CT_ALIMENTOS e E_COMPUTACAO.
        """
        # Arrange — localiza o combo pelo objectName
        combo = pagina.findChild(QComboBox, "combo_perfil")

        # Assert — o combo existe e tem 9 itens
        assert combo is not None
        assert combo.count() == 9

    def test_btn_confirmar_perfil_existe(self, pagina):
        """
        O QPushButton 'btn_confirmar_perfil' deve existir com texto 'Confirmar'.

        O botao e o unico meio de confirmar a selecao de perfil.
        """
        # Arrange — localiza o botao pelo objectName
        btn = pagina.findChild(QPushButton, "btn_confirmar_perfil")

        # Assert — o botao existe e tem o texto correcto
        assert btn is not None
        assert btn.text() == "Confirmar"


class TestSignals:
    """
    Testes do signal perfil_confirmado emitido pela PaginaSelecaoPerfil.
    """

    def test_perfil_confirmado_signal(self, pagina, qtbot):
        """
        Clicar no botao de confirmar deve emitir perfil_confirmado
        com o texto do perfil actualmente selecionado no combo.

        O signal carrega uma string que corresponde ao currentText
        do QComboBox no momento do clique.
        """
        # Arrange — localiza o botao e o combo
        btn = pagina.findChild(QPushButton, "btn_confirmar_perfil")
        combo = pagina.findChild(QComboBox, "combo_perfil")
        assert btn is not None
        assert combo is not None
        perfil_esperado = combo.currentText()

        # Act & Assert — clica no botao e verifica o signal emitido
        with qtbot.waitSignal(pagina.perfil_confirmado, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

        # Assert — o signal deve ter sido emitido com o texto do combo
        assert len(blocker.args) == 1
        assert blocker.args[0] == perfil_esperado
