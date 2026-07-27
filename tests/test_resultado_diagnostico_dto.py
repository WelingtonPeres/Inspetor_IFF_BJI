"""
Suite de testes para o ResultadoDiagnosticoDTO.
"""

import pytest
from dataclasses import FrozenInstanceError, fields

from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from core.dtos.resultado_diagnostico import ResultadoDiagnosticoDTO


@pytest.fixture
def pontuacao_fake():
    """DiagnosticoPontuacaoDTO com pontuacao_final=1500.0 e sub-totais preenchidos."""
    return DiagnosticoPontuacaoDTO(
        qnt_riscos_marcados=2,
        qnt_riscos_gabarito=3,
        qnt_riscos_corretos_marcados=2,
        estado_ato=True,
        estado_condicao=False,
        status_decisao_jogador="OTIMA",
        tempo_resposta_segundos=45.0,
        pontuacao_final=1500.0,
        nota_riscos=600.0,
        nota_fatores=150.0,
        nota_decisao=750.0,
        pontos_bonus_tempo=0.0,
    )


@pytest.fixture
def feedback_fake():
    """DiagnosticoFeedbackDTO com riscos_acertados e scores populados."""
    return DiagnosticoFeedbackDTO(
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
    )


@pytest.fixture
def resultado_fake(pontuacao_fake, feedback_fake):
    """ResultadoDiagnosticoDTO construido a partir de pontuacao_fake e feedback_fake."""
    return ResultadoDiagnosticoDTO(pontuacao=pontuacao_fake, feedback=feedback_fake)


class TestResultadoDiagnosticoDTO:
    """
    Testes de construcao, imutabilidade e acesso do Parameter Object.
    """

    def test_dto_eh_dataclass_frozen(self, resultado_fake):
        """O DTO deve ser frozen — atribuicao a campo deve lancar FrozenInstanceError."""
        # Arrange — fixture resultado_fake
        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            resultado_fake.pontuacao = DiagnosticoPontuacaoDTO(
                qnt_riscos_marcados=0, qnt_riscos_gabarito=0,
                qnt_riscos_corretos_marcados=0,
                estado_ato=False, estado_condicao=False,
                status_decisao_jogador="INCORRETA",
                tempo_resposta_segundos=0.0,
            )

    def test_dois_campos_no_total(self):
        """O DTO deve ter exactamente 2 campos: pontuacao e feedback."""
        # Arrange & Act
        nomes = [f.name for f in fields(ResultadoDiagnosticoDTO)]
        # Assert
        assert nomes == ["pontuacao", "feedback"]

    def test_acesso_aninhado_pontuacao_final(self, resultado_fake):
        """resultado.pontuacao.pontuacao_final deve aceder ao DTO interno correctamente."""
        # Arrange — fixture resultado_fake com pontuacao_final=1500.0
        # Act
        valor = resultado_fake.pontuacao.pontuacao_final
        # Assert
        assert valor == 1500.0

    def test_acesso_aninhado_riscos_acertados(self, resultado_fake):
        """resultado.feedback.riscos_acertados deve aceder a lista interna correctamente."""
        # Arrange — fixture resultado_fake com riscos_acertados=["FISICO", "QUIMICO"]
        # Act
        riscos = resultado_fake.feedback.riscos_acertados
        # Assert
        assert riscos == ["FISICO", "QUIMICO"]

    def test_acesso_aninhado_subtotais(self, resultado_fake):
        """resultado.pontuacao.nota_riscos e demais sub-totais devem ser acessiveis."""
        # Assert
        assert resultado_fake.pontuacao.nota_riscos == 600.0
        assert resultado_fake.pontuacao.nota_fatores == 150.0
        assert resultado_fake.pontuacao.nota_decisao == 750.0
        assert resultado_fake.pontuacao.pontos_bonus_tempo == 0.0

    def test_construcao_com_dtos_reais(self, pontuacao_fake, feedback_fake):
        """Construir ResultadoDiagnosticoDTO com DTOs reais deve funcionar sem erro."""
        # Arrange — fixtures pontuacao_fake e feedback_fake
        # Act
        resultado = ResultadoDiagnosticoDTO(pontuacao=pontuacao_fake, feedback=feedback_fake)
        # Assert
        assert isinstance(resultado.pontuacao, DiagnosticoPontuacaoDTO)
        assert isinstance(resultado.feedback, DiagnosticoFeedbackDTO)

    def test_igualdade_entre_instancias_identicas(self, pontuacao_fake, feedback_fake):
        """Duas instancias com os mesmos DTOs internos devem ser iguais."""
        # Arrange
        r1 = ResultadoDiagnosticoDTO(pontuacao=pontuacao_fake, feedback=feedback_fake)
        r2 = ResultadoDiagnosticoDTO(pontuacao=pontuacao_fake, feedback=feedback_fake)
        # Act & Assert
        assert r1 == r2

    def test_acesso_score_por_risco_via_resultado(self, resultado_fake):
        """A View deve conseguir aceder score_por_risco via resultado.feedback."""
        # Act
        score = resultado_fake.feedback.score_por_risco.get("FISICO", 0.0)
        # Assert
        assert score == 500.0
