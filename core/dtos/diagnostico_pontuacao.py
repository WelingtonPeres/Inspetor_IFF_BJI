from dataclasses import dataclass


@dataclass(frozen=True)
class DiagnosticoPontuacaoDTO:
    """
    Data Transfer Object puro que carrega apenas os operandos matematicos
    necessarios para a Pontuacao.
    """

    qnt_riscos_marcados: int
    qnt_riscos_gabarito: int
    qnt_riscos_corretos_marcados: int

    estado_ato: bool
    estado_condicao: bool

    status_decisao_jogador: str
    tempo_resposta_segundos: float
    pontuacao_final: float = 0.0

    nota_riscos: float = 0.0
    nota_fatores: float = 0.0
    nota_decisao: float = 0.0
    pontos_bonus_tempo: float = 0.0