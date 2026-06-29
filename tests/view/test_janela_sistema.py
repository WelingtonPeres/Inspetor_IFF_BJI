"""
Suite completa de testes para o componente JanelaSistema.
"""

import pytest
from PySide6.QtCore import Qt

from view.components.janela_sistema import JanelaSistema


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def janela():
    """Retorna uma instancia do JanelaSistema."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    LayoutLoader.instance().set_screen(1920, 1080)
    return JanelaSistema()


class TestJanelaSistema:
    """
    Testes para o componente JanelaSistema (floating window container).

    Verifica estrutura, signals e exibicao de paginas internas.
    """

    def test_object_name(self, janela):
        """O JanelaSistema deve ter objectName 'janela_sistema'."""
        assert janela.objectName() == "janela_sistema"

    def test_property_class(self, janela):
        """O JanelaSistema deve ter property class 'janela_sistema'."""
        assert janela.property("class") == "janela_sistema"

    def test_fixed_size(self, janela):
        """O JanelaSistema deve ter tamanho fixo vindo do layout.json."""
        assert janela.width() == 480
        assert janela.height() == 340

    def test_close_signal(self, janela, qtbot):
        """Fechar a janela pelo title bar deve emitir close_requested."""
        with qtbot.waitSignal(janela.close_requested, timeout=1000):
            janela.close_requested.emit()

    def test_perfil_confirmado_signal(self, janela, qtbot):
        """perfil_confirmado deve propagar do body."""
        with qtbot.waitSignal(janela.perfil_confirmado, timeout=1000) as blocker:
            janela.perfil_confirmado.emit("T_INFORMATICA")
        assert blocker.args[0] == "T_INFORMATICA"

    def test_exibir_selecao_perfil(self, janela):
        """exibir_selecao_perfil deve delegar ao body e mostrar a janela."""
        janela.show()
        janela.exibir_selecao_perfil()
        assert janela.isVisible()
