"""
Suite de testes para a PaginaDiagnostico.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton

from view.expediente.paginas.diagnostico import PaginaDiagnostico
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def pagina():
    """Retorna uma PaginaDiagnostico."""
    return PaginaDiagnostico()


class TestEstrutura:
    """
    Testes de estrutura basica da PaginaDiagnostico.

    Verifica objectName, property class e componentes principais.
    """

    def test_object_name(self, pagina):
        """A PaginaDiagnostico deve ter objectName 'pagina_diagnostico'."""
        assert pagina.objectName() == "pagina_diagnostico"

    def test_property_class(self, pagina):
        """A PaginaDiagnostico deve ter property class 'pagina_diagnostico'."""
        assert pagina.property("class") == "pagina_diagnostico"

    def test_label_diagnostico_existe(self, pagina):
        """A pagina deve conter um QLabel 'label_diagnostico'."""
        label = pagina.findChild(QLabel, "label_diagnostico")
        assert label is not None

    def test_btn_continuar_existe(self, pagina):
        """A pagina deve conter um QPushButton 'btn_continuar'."""
        btn = pagina.findChild(QPushButton, "btn_continuar")
        assert btn is not None
        assert btn.text() == "Continuar"


class TestSignals:
    """
    Testes do signal continuar_solicitado.
    """

    def test_continuar_signal(self, pagina, qtbot):
        """Clicar em continuar deve emitir continuar_solicitado."""
        btn = pagina.findChild(QPushButton, "btn_continuar")
        with qtbot.waitSignal(pagina.continuar_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)


class TestComportamento:
    """
    Testes do metodo exibir_diagnostico.
    """

    def test_exibir_diagnostico_atualiza_label(self, pagina):
        """exibir_diagnostico deve atualizar o texto do label."""
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=2, qnt_riscos_gabarito=3,
            qnt_riscos_corretos_marcados=1, estado_ato=True,
            estado_condicao=False, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=30.0, pontuacao_final=1500.0,
        )
        pagina.exibir_diagnostico(dto)
        label = pagina.findChild(QLabel, "label_diagnostico")
        assert "1500.0" in label.text()
        assert "OTIMA" in label.text()
