from dataclasses import dataclass

from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO


@dataclass(frozen=True)
class ResultadoDiagnosticoDTO:
    """
    Parameter Object que agrupa o resultado matematico da pontuacao
    e o breakdown item-a-item do feedback, isolando a View de
    mudancas futuras na estrutura dos DTOs internos.

    Unica razao para mudar: a tela de diagnostico precisa de um
    novo tipo de dado alem de pontuacao e feedback.
    """

    pontuacao: DiagnosticoPontuacaoDTO
    feedback: DiagnosticoFeedbackDTO
