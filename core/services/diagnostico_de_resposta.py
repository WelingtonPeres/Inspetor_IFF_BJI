import logging
from typing import NamedTuple

from core.model.folha_de_gabarito import FolhaDeGabarito
from core.model.folha_de_resposta import FolhaDeResposta

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO

logger = logging.getLogger(__name__)


class _MetadadosInspecao(NamedTuple):
    """Conjuntos extraídos de gabarito e respostas, consumidos pelos
    métodos públicos de diagnóstico."""

    riscos_set_marcados: set[str]
    riscos_set_gabarito: set[str]
    fatores_set_marcados: set[str]
    fatores_set_gabarito: set[str]


class DiagnosticoDeResposta:
    """
    Responsável por confrontar o input do jogador com o gabarito oficial
    e extrair as métricas brutas de acertos e falsos alarmes para serem
    consumidas.
    """

    def __extrair_metadados(self, gabarito: FolhaDeGabarito, respostas: FolhaDeResposta) -> _MetadadosInspecao:
        """Extrai os conjuntos de riscos e factores do gabarito e das
        respostas, servindo como fonte única para ambos os métodos
        públicos de diagnóstico."""
        
        return _MetadadosInspecao(
            riscos_set_marcados=set(respostas.riscos),
            riscos_set_gabarito=set(gabarito.riscos),
            fatores_set_marcados=set(respostas.fatores_inseguranca),
            fatores_set_gabarito=set(gabarito.fatores_inseguranca),
        )

    def gerar_diagnostico_pontuacao(self, gabarito: FolhaDeGabarito, respostas: FolhaDeResposta) -> DiagnosticoPontuacaoDTO:
        """
        Gerar um diagnóstico de pontuação a partir do confronto entre o gabarito e as respostas do jogador. 
        
        Args:
            gabarito (FolhaDeGabarito): O gabarito oficial contendo as respostas corretas.
            respostas (FolhaDeResposta): As respostas fornecidas pelo jogador.
            
        Returns:
            DiagnosticoPontuacaoDTO: Um objeto contendo as métricas de acertos, falsos alarmes, e outras informações relevantes para a pontuação do jogador.
        """
        try:
            meta = self.__extrair_metadados(gabarito, respostas)

            qnt_riscos_corretos_marcados = len(
                meta.riscos_set_marcados & meta.riscos_set_gabarito
            )

            estado_ato = ("ATO_INSEGURO" in meta.fatores_set_marcados) == (
                "ATO_INSEGURO" in meta.fatores_set_gabarito
            )
            estado_condicao = ("CONDICAO_INSEGURA" in meta.fatores_set_marcados) == (
                "CONDICAO_INSEGURA" in meta.fatores_set_gabarito
            )

            if respostas.decisao_tomada == gabarito.decisao_otima:
                decisao_jogador = "OTIMA"
            elif respostas.decisao_tomada == gabarito.decisao_boa:
                decisao_jogador = "BOA"
            else:
                decisao_jogador = "INCORRETA"

            return DiagnosticoPontuacaoDTO(
                qnt_riscos_marcados=len(meta.riscos_set_marcados),
                qnt_riscos_gabarito=len(meta.riscos_set_gabarito),
                qnt_riscos_corretos_marcados=qnt_riscos_corretos_marcados,
                estado_ato=estado_ato,
                estado_condicao=estado_condicao,
                status_decisao_jogador=decisao_jogador,
                tempo_resposta_segundos=respostas.tempo_gasto_segundos,
            )

        except (AttributeError, TypeError) as e:
            raise ValueError(
                f"[Erro - DiagnosticoDeResposta] Falha ao gerar diagnóstico: {e}"
            )

    def gerar_feedback(
        self, gabarito: FolhaDeGabarito, respostas: FolhaDeResposta
    ) -> DiagnosticoFeedbackDTO:
        """
        Gera o breakdown item-a-item do confronto entre gabarito e
        respostas, categorizando cada risco e factor como acertado,
        esquecido ou inventado.

        Os campos score_por_risco e score_por_fator saem como dicts
        vazios — serão populados pelo MotorDePontuacao na etapa
        seguinte do pipeline.
        """
        try:
            meta = self.__extrair_metadados(gabarito, respostas)

            riscos_acertados = sorted(
                meta.riscos_set_marcados & meta.riscos_set_gabarito
            )
            riscos_esquecidos = sorted(
                meta.riscos_set_gabarito - meta.riscos_set_marcados
            )
            riscos_inventados = sorted(
                meta.riscos_set_marcados - meta.riscos_set_gabarito
            )

            fatores_acertados = sorted(
                meta.fatores_set_marcados & meta.fatores_set_gabarito
            )
            fatores_esquecidos = sorted(
                meta.fatores_set_gabarito - meta.fatores_set_marcados
            )
            fatores_inventados = sorted(
                meta.fatores_set_marcados - meta.fatores_set_gabarito
            )

            return DiagnosticoFeedbackDTO(
                riscos_acertados=riscos_acertados,
                riscos_esquecidos=riscos_esquecidos,
                riscos_inventados=riscos_inventados,
                fatores_acertados=fatores_acertados,
                fatores_esquecidos=fatores_esquecidos,
                fatores_inventados=fatores_inventados,
                decisao_tomada=respostas.decisao_tomada,
                decisao_esperada=gabarito.decisao_otima,
            )

        except (AttributeError, TypeError) as e:
            raise ValueError(
                f"[Erro - DiagnosticoDeResposta] Falha ao gerar feedback: {e}"
            )
