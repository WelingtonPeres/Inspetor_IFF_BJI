from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class DiagnosticoFeedbackDTO:
    """
    Data Transfer Object que carrega o breakdown item-a-item do
    confronto entre gabarito e respostas do jogador, para
    renderizacao visual da tela de diagnostico.

    Nao contem operandos matematicos -- esses pertencem ao
    DiagnosticoPontuacaoDTO. Os scores (pre-calculados pelo
    MotorDePontuacao) sao o unico dado numerico aqui, para
    evitar logica de dominio na View.
    """

    riscos_acertados: List[str] = field(default_factory=list)
    riscos_esquecidos: List[str] = field(default_factory=list)
    riscos_inventados: List[str] = field(default_factory=list)

    fatores_acertados: List[str] = field(default_factory=list)
    fatores_esquecidos: List[str] = field(default_factory=list)
    fatores_inventados: List[str] = field(default_factory=list)

    decisao_tomada: str = ""
    decisao_esperada: str = ""

    score_por_risco: Dict[str, float] = field(default_factory=dict)
    score_por_fator: Dict[str, float] = field(default_factory=dict)
