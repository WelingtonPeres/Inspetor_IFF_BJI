"""
Suite de testes para o DiagnosticoFeedbackDTO.
"""

import pytest
from dataclasses import FrozenInstanceError, fields

from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO


@pytest.fixture
def feedback_vazio():
    """DiagnosticoFeedbackDTO com todos os defaults."""
    return DiagnosticoFeedbackDTO()


@pytest.fixture
def feedback_preenchido():
    """DiagnosticoFeedbackDTO com todos os 10 campos populados."""
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


class TestDiagnosticoFeedbackDTO:
    """
    Testes de construcao, imutabilidade e defaults do DiagnosticoFeedbackDTO.
    """

    def test_dto_eh_dataclass_frozen(self, feedback_vazio):
        """O DTO deve ser frozen — atribuicao a campo deve lancar FrozenInstanceError."""
        # Arrange — fixture feedback_vazio
        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            feedback_vazio.riscos_acertados = ["FISICO"]

    def test_dez_campos_no_total(self):
        """O DTO deve ter exactamente 10 campos."""
        # Arrange
        # Act
        nomes = [f.name for f in fields(DiagnosticoFeedbackDTO)]
        # Assert
        assert len(nomes) == 10

    def test_todos_os_campos_tem_default(self):
        """Instanciar sem argumentos deve criar DTO com todos os defaults vazios."""
        # Arrange & Act
        dto = DiagnosticoFeedbackDTO()
        # Assert
        assert dto.riscos_acertados == []
        assert dto.riscos_esquecidos == []
        assert dto.riscos_inventados == []
        assert dto.fatores_acertados == []
        assert dto.fatores_esquecidos == []
        assert dto.fatores_inventados == []
        assert dto.decisao_tomada == ""
        assert dto.decisao_esperada == ""
        assert dto.score_por_risco == {}
        assert dto.score_por_fator == {}

    def test_riscos_acertados_populados_corretamente(self):
        """riscos_acertados deve preservar a lista exacta passada no construtor."""
        # Arrange
        riscos = ["FISICO", "QUIMICO"]
        # Act
        dto = DiagnosticoFeedbackDTO(riscos_acertados=riscos)
        # Assert
        assert dto.riscos_acertados == riscos
        assert isinstance(dto.riscos_acertados, list)

    def test_score_por_risco_mapeia_nome_para_float(self):
        """score_por_risco deve ser um dict que mapeia str -> float."""
        # Arrange
        scores = {"FISICO": 500.0, "QUIMICO": 250.0}
        # Act
        dto = DiagnosticoFeedbackDTO(score_por_risco=scores)
        # Assert
        assert dto.score_por_risco == scores
        assert isinstance(dto.score_por_risco["FISICO"], float)

    def test_score_por_fator_mapeia_nome_para_float(self):
        """score_por_fator deve ser um dict que mapeia str -> float."""
        # Arrange
        scores = {"ATO_INSEGURO": 200.0, "CONDICAO_INSEGURA": 200.0}
        # Act
        dto = DiagnosticoFeedbackDTO(score_por_fator=scores)
        # Assert
        assert dto.score_por_fator == scores
        assert isinstance(dto.score_por_fator["ATO_INSEGURO"], float)

    def test_decisao_tomada_e_decisao_esperada_strings(self):
        """decisao_tomada e decisao_esperada devem ser strings preservadas do construtor."""
        # Arrange & Act
        dto = DiagnosticoFeedbackDTO(decisao_tomada="ADVERTIR", decisao_esperada="INTERDITAR")
        # Assert
        assert dto.decisao_tomada == "ADVERTIR"
        assert dto.decisao_esperada == "INTERDITAR"

    def test_campos_lista_sao_independentes_entre_instancias(self):
        """Cada instancia deve ter a sua propria lista — nao partilhada."""
        # Arrange
        dto1 = DiagnosticoFeedbackDTO(riscos_acertados=["FISICO"])
        # Act
        dto2 = DiagnosticoFeedbackDTO()
        # Assert — dto2 nao deve herdar os riscos de dto1
        assert dto2.riscos_acertados == []

    def test_preenchido_tem_dados_corretos(self, feedback_preenchido):
        """DTO preenchido deve expor todos os campos correctamente."""
        # Assert
        assert len(feedback_preenchido.riscos_acertados) == 2
        assert len(feedback_preenchido.riscos_esquecidos) == 1
        assert len(feedback_preenchido.riscos_inventados) == 1
        assert feedback_preenchido.decisao_tomada == "INTERDITAR"
        assert feedback_preenchido.score_por_risco["FISICO"] == 500.0
