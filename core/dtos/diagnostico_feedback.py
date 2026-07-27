from dataclasses import dataclass, field


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

    riscos_acertados: list[str] = field(default_factory=list)
    riscos_esquecidos: list[str] = field(default_factory=list)
    riscos_inventados: list[str] = field(default_factory=list)

    fatores_acertados: list[str] = field(default_factory=list)
    fatores_esquecidos: list[str] = field(default_factory=list)
    fatores_inventados: list[str] = field(default_factory=list)

    decisao_tomada: str = ""
    decisao_esperada: str = ""

    score_por_risco: dict[str, float] = field(default_factory=dict)
    score_por_fator: dict[str, float] = field(default_factory=dict)
