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
    
    estado_ato: bool 
    estado_condicao: bool
    
    status_decisao_jogador: str
    tempo_resposta_segundos: float
    pontuacao_final: float = 0.0 