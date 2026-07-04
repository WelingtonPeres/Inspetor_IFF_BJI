"""
Suite completa de testes para o componente JanelaSistemaBody.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QStackedWidget

from view.components.janela_sistema_body import JanelaSistemaBody


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def body():
    """Retorna uma instancia do JanelaSistemaBody."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    LayoutLoader.instance().set_screen(1920, 1080)
    return JanelaSistemaBody()


class TestJanelaSistemaBody:
    """
    Testes para o componente JanelaSistemaBody.

    Verifica objectName, class, placeholder e pagina de selecao de perfil.
    """

    def test_object_name(self, body):
        """O JanelaSistemaBody deve ter objectName 'janela_sistema_body'."""
        assert body.objectName() == "janela_sistema_body"

    def test_stacked_com_duas_paginas(self, body):
        """O QStackedWidget interno deve conter 2 paginas (placeholder + perfil)."""
        stack = body.findChild(QStackedWidget)
        assert stack is not None
        assert stack.count() == 2

    def test_placeholder_pagina_0(self, body):
        """A pagina 0 deve conter o placeholder 'Em construcao'."""
        stack = body.findChild(QStackedWidget)
        pagina = stack.widget(0)
        placeholder = pagina.findChild(QLabel, "janela_sistema_placeholder")
        assert placeholder is not None
        assert placeholder.text() == "Em constru\u00e7\u00e3o"

    def test_perfil_pagina_1(self, body):
        """A pagina 1 deve conter combo de perfis e botao confirmar."""
        stack = body.findChild(QStackedWidget)
        pagina = stack.widget(1)
        combo = pagina.findChild(QComboBox, "combo_perfil")
        assert combo is not None
        assert combo.count() == 9
        btn = pagina.findChild(QPushButton, "btn_confirmar_perfil")
        assert btn is not None

    def test_exibir_selecao_perfil_muda_indice(self, body):
        """exibir_selecao_perfil deve trocar o stacked para pagina 1."""
        body.exibir_selecao_perfil()
        stack = body.findChild(QStackedWidget)
        assert stack.currentIndex() == body.IDX_SELECAO_PERFIL

    def test_perfil_confirmado_signal(self, body, qtbot):
        """Clicar no botao confirmar deve emitir perfil_confirmado."""
        body.exibir_selecao_perfil()
        btn = body.findChild(QPushButton, "btn_confirmar_perfil")
        with qtbot.waitSignal(body.perfil_confirmado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
