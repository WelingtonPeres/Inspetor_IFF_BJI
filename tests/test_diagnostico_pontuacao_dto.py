"""
Suite de testes para os novos campos do DiagnosticoPontuacaoDTO.
"""

import pytest
from dataclasses import FrozenInstanceError, fields

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO


@pytest.fixture
def dto_original_8_campos():
    """DiagnosticoPontuacaoDTO com os 8 campos originais (sem novos sub-totais)."""
    return DiagnosticoPontuacaoDTO(
        qnt_riscos_marcados=2,
        qnt_riscos_gabarito=3,
        qnt_riscos_corretos_marcados=2,
        estado_ato=True,
        estado_condicao=False,
        status_decisao_jogador="OTIMA",
        tempo_resposta_segundos=30.0,
    )


@pytest.fixture
def dto_12_campos():
    """DiagnosticoPontuacaoDTO com todos os 12 campos preenchidos."""
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


class TestDiagnosticoPontuacaoDTONovosCampos:
    """
    Testes de backward compatibility e valores dos 4 novos campos de sub-totais.
    """

    def test_novos_campos_tem_default_zero(self, dto_original_8_campos):
        """Instanciar sem os 4 novos campos deve atribuir default 0.0 a cada um."""
        # Arrange — fixture dto_original_8_campos
        # Assert
        assert dto_original_8_campos.nota_riscos == 0.0
        assert dto_original_8_campos.nota_fatores == 0.0
        assert dto_original_8_campos.nota_decisao == 0.0
        assert dto_original_8_campos.pontos_bonus_tempo == 0.0

    def test_construcao_legada_nao_quebra(self, dto_original_8_campos):
        """Construtor com 8 campos posicionais continua a funcionar."""
        # Arrange — fixture dto_original_8_campos
        # Assert — campos originais preservados
        assert dto_original_8_campos.qnt_riscos_marcados == 2
        assert dto_original_8_campos.qnt_riscos_gabarito == 3
        assert dto_original_8_campos.qnt_riscos_corretos_marcados == 2
        assert dto_original_8_campos.estado_ato is True
        assert dto_original_8_campos.estado_condicao is False
        assert dto_original_8_campos.status_decisao_jogador == "OTIMA"
        assert dto_original_8_campos.tempo_resposta_segundos == 30.0

    def test_novos_campos_populados_explicitamente(self, dto_12_campos):
        """Passar valores explicitos para os 4 novos campos deve preserva-los."""
        # Assert
        assert dto_12_campos.nota_riscos == 600.0
        assert dto_12_campos.nota_fatores == 150.0
        assert dto_12_campos.nota_decisao == 750.0
        assert dto_12_campos.pontos_bonus_tempo == 0.0

    def test_dto_continua_frozen_com_novos_campos(self, dto_12_campos):
        """O DTO deve permanecer frozen com os novos campos."""
        # Arrange — dto_12_campos
        # Act & Assert
        with pytest.raises(FrozenInstanceError):
            dto_12_campos.nota_riscos = 999.0

    def test_quinze_campos_no_total(self):
        """O DTO completo deve ter 15 campos (8 originais + 7 novos)."""
        # Arrange & Act
        nomes = [f.name for f in fields(DiagnosticoPontuacaoDTO)]
        # Assert
        assert len(nomes) == 15

    def test_subtotais_sao_float(self, dto_12_campos):
        """Os 4 novos campos devem ser do tipo float."""
        # Assert
        assert isinstance(dto_12_campos.nota_riscos, float)
        assert isinstance(dto_12_campos.nota_fatores, float)
        assert isinstance(dto_12_campos.nota_decisao, float)
        assert isinstance(dto_12_campos.pontos_bonus_tempo, float)

    def test_pontuacao_final_com_default_zero(self):
        """pontuacao_final mantem default 0.0 (campo existente, nao novo)."""
        # Arrange & Act
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=0, qnt_riscos_gabarito=0,
            qnt_riscos_corretos_marcados=0,
            estado_ato=False, estado_condicao=False,
            status_decisao_jogador="INCORRETA",
            tempo_resposta_segundos=0.0,
        )
        # Assert
        assert dto.pontuacao_final == 0.0


class TestDecisaoAnulada:
    """
    Testes do novo campo decisao_anulada (default False, 15.º campo do DTO).
    """

    def test_decisao_anulada_default_false(self, dto_original_8_campos):
        """Instanciar sem o campo deve atribuir default False."""
        # Arrange — fixture dto_original_8_campos
        # Assert
        assert dto_original_8_campos.decisao_anulada is False

    def test_decisao_anulada_populado_explicitamente(self):
        """Passar decisao_anulada=True deve preservar o valor True no DTO."""
        # Arrange & Act
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=2,
            qnt_riscos_gabarito=3,
            qnt_riscos_corretos_marcados=2,
            estado_ato=True,
            estado_condicao=False,
            status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=45.0,
            decisao_anulada=True,
        )
        # Assert
        assert dto.decisao_anulada is True
