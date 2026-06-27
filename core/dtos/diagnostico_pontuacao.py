from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass(frozen=True)
class DiagnosticoPontuacaoDTO:
    """
    Data Transfer Object puro que carrega apenas os operandos matemáticos 
    necessários para o Pontuação.
    """
    
    qnt_riscos_marcados: int
    qnt_riscos_gabarito: int
    qnt_riscos_corretos_marcados: int
    
    # True se o resultado do confronto entre o ato inseguro do gabarito e o ato marcado pelo jogador indicar que o ato foi identificado, False caso contrário.
    estado_ato: bool 
    estado_condicao: bool
    
    status_decisao_jogador: str
    tempo_resposta_segundos: float
    pontuacao_final: float = 0.0 