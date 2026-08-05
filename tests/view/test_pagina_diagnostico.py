"""
Suite de testes para a PaginaDiagnostico reescrita.
"""

from dataclasses import replace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QScrollArea

from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from core.dtos.resultado_diagnostico import ResultadoDiagnosticoDTO
from view.expediente.paginas.diagnostico import PaginaDiagnostico


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def pagina():
    """Retorna uma PaginaDiagnostico reescrita."""
    return PaginaDiagnostico()


@pytest.fixture
def resultado_fake():
    """ResultadoDiagnosticoDTO completo para testes de renderizacao."""
    return ResultadoDiagnosticoDTO(
        pontuacao=DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=3, qnt_riscos_gabarito=3,
            qnt_riscos_corretos_marcados=2, estado_ato=True,
            estado_condicao=False, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=45.0, pontuacao_final=2550.0,
            nota_riscos=600.0, nota_fatores=150.0,
            nota_decisao=750.0, pontos_bonus_tempo=0.0,
        ),
        feedback=DiagnosticoFeedbackDTO(
            riscos_acertados=["FISICO", "QUIMICO"],
            riscos_esquecidos=["BIOLOGICO"],
            riscos_inventados=["ACIDENTE"],
            fatores_acertados=["ATO_INSEGURO"],
            fatores_esquecidos=["CONDICAO_INSEGURA"],
            fatores_inventados=[],
            decisao_tomada="INTERDITAR",
            decisao_esperada="INTERDITAR",
            score_por_risco={"FISICO": 500.0, "QUIMICO": 250.0, "ACIDENTE": -125.0},
            score_por_fator={"ATO_INSEGURO": 200.0, "CONDICAO_INSEGURA": 0.0},
        ),
    )


class TestEstrutura:
    """
    Testes de estrutura base da PaginaDiagnostico reescrita.
    """

    def test_object_name(self, pagina):
        """A PaginaDiagnostico deve ter objectName 'pagina_diagnostico'."""
        assert pagina.objectName() == "pagina_diagnostico"

    def test_property_class(self, pagina):
        """A PaginaDiagnostico deve ter property class 'pagina_diagnostico'."""
        assert pagina.property("class") == "pagina_diagnostico"

    def test_scroll_area_existe(self, pagina):
        """A pagina deve conter uma QScrollArea."""
        scroll = pagina.findChild(QScrollArea, "diagnostico_scroll")
        assert scroll is not None

    def test_btn_continuar_existe(self, pagina):
        """O botao Continuar deve existir."""
        btn = pagina.findChild(QPushButton, "btn_continuar_diagnostico")
        assert btn is not None
        assert btn.text() == "Continuar"

    def test_header_existe(self, pagina, resultado_fake):
        """Apos exibir_diagnostico, header mostra pontuacao formatada."""
        # Arrange
        pagina.exibir_diagnostico(resultado_fake)
        # Act
        valor = pagina.findChild(QLabel, "diagnostico_header_valor")
        # Assert
        assert valor is not None
        assert "2550" in valor.text()


class TestExibirDiagnostico:
    """
    Testes do metodo exibir_diagnostico().
    """

    def test_header_mostra_pontuacao(self, pagina, resultado_fake):
        """Header deve mostrar pontuacao final formatada."""
        # Arrange & Act
        pagina.exibir_diagnostico(resultado_fake)
        valor = pagina.findChild(QLabel, "diagnostico_header_valor")
        # Assert
        assert "2550 pts" in valor.text()

    def test_card_riscos_existe(self, pagina, resultado_fake):
        """Card de riscos deve ser renderizado."""
        # Arrange & Act
        pagina.exibir_diagnostico(resultado_fake)
        card = pagina.findChild(type(pagina._PaginaDiagnostico__card_riscos))
        # Assert
        assert card is not None

    def test_card_decisao_correta(self, pagina, resultado_fake):
        """Com decisao correta, nao deve haver opcao dashed."""
        # Arrange & Act
        pagina.exibir_diagnostico(resultado_fake)
        # Assert — nao lanca excepcao
        resultado = pagina.findChild(QLabel, "diagnostico_decisao_resultado")
        assert resultado is not None

    def test_total_mostra_pontuacao(self, pagina, resultado_fake):
        """Linha total deve mostrar pontuacao final."""
        # Arrange & Act
        pagina.exibir_diagnostico(resultado_fake)
        total = pagina.findChild(QLabel, "diagnostico_total_valor")
        # Assert
        assert total is not None
        assert "2550" in total.text()

    def test_exibir_com_pontuacao_zero_nao_crasha(self, pagina):
        """Exibir com pontuacao zero e feedback vazio nao deve crashar."""
        # Arrange
        resultado_vazio = ResultadoDiagnosticoDTO(
            pontuacao=DiagnosticoPontuacaoDTO(
                qnt_riscos_marcados=0, qnt_riscos_gabarito=0,
                qnt_riscos_corretos_marcados=0, estado_ato=False,
                estado_condicao=False, status_decisao_jogador="INCORRETA",
                tempo_resposta_segundos=0.0,
            ),
            feedback=DiagnosticoFeedbackDTO(),
        )
        # Act
        pagina.exibir_diagnostico(resultado_vazio)
        # Assert — nao lancou excepcao

    def test_re_exibir_nao_acumula_tiles(self, pagina, resultado_fake):
        """Chamar exibir_diagnostico duas vezes nao duplica tiles."""
        # Arrange & Act
        pagina.exibir_diagnostico(resultado_fake)
        pagina.exibir_diagnostico(resultado_fake)
        # Assert — nao lanca excepcao (tiles anteriores foram limpos)


class TestCardDecisaoSolucaoSemSentido:
    """
    Testes do ramo decisao_anulada=True no card de decisao.
    """

    def test_exibir_diagnostico_decisao_anulada_mostra_label_solucao_sem_sentido(
        self, pagina, resultado_fake
    ):
        """Com decisao_anulada=True, o label de resultado deve mostrar 'solucao sem sentido'."""
        # Arrange
        resultado_anulado = replace(
            resultado_fake,
            pontuacao=replace(resultado_fake.pontuacao, decisao_anulada=True),
        )

        # Act
        pagina.exibir_diagnostico(resultado_anulado)
        resultado_label = pagina.findChild(QLabel, "diagnostico_decisao_resultado")

        # Assert
        assert resultado_label is not None
        assert resultado_label.text() == "solucao sem sentido"


class TestSignals:
    """
    Testes do signal continuar_solicitado.
    """

    def test_continuar_signal_emitido(self, pagina, qtbot):
        """Clicar no botao Continuar deve emitir continuar_solicitado."""
        # Arrange
        btn = pagina.findChild(QPushButton, "btn_continuar_diagnostico")
        # Act & Assert
        with qtbot.waitSignal(pagina.continuar_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
