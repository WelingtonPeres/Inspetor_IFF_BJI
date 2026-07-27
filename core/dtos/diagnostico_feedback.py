from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class DiagnosticoFeedbackDTO:
    """
    Data Transfer Object que carrega o breakdown item-a-item do
    confronto entre gabarito e respostas do jogador, para
    renderizacao visual da tela de diagnostico.
    """

    riscos_acertados: List[str] 
    riscos_esquecidos: List[str] 
    riscos_inventados: List[str] 

    fatores_acertados: List[str] 
    fatores_esquecidos: List[str] 
    fatores_inventados: List[str] 

    decisao_tomada: str 
    decisao_esperada: str 

    score_por_risco: Dict[str, float] 
    score_por_fator: Dict[str, float] 
