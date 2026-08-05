import logging
from typing import List, NamedTuple

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
from core.model.relatorio import Relatorio

logger = logging.getLogger(__name__)


class MotorDePontuacao:
    """
    Responsável por processar a lógica matemática determinística do jogo, avaliando a acurácia (riscos/fatores),
    a decisão administrativa e a eficiência temporal.
    """

    TAXA_DECAIMENTO_ALFA = 0.007
    LIMITE_MINIMO_RETENCAO = 0.50

    PESO_RISCOS = 0.60
    PESO_FATORES = 0.15
    PESO_DECISAO_OTIMA = 0.25
    PESO_DECISAO_BOA = 0.125

    # Cálculo Quantitativo (Vmax)
    VALOR_BASE_PARTICIPACAO = 1000
    BONUS_RISCO = 250
    BONUS_FATOR = 250
    BONUS_MIDIA_IMAGEM = 100
    BONUS_MIDIA_VIDEO = 300
    BONUS_MIDIA_AUDIO = 200
    BONUS_CONTEXTO = 100

    TEMPO_IDEAL_SEGUNDOS = 45
    LIMIAR_VITORIA_TURNO = 0.60

    def __init__(self):
        """Injeta as variaveis de calibragem matematica do motor."""
        self.__taxa_decaimento = self.TAXA_DECAIMENTO_ALFA
        self.__limite_minimo_retencao = self.LIMITE_MINIMO_RETENCAO


    def calcular_vmax_relatorio(self, relatorio: Relatorio) -> float:
        """
        Calcula o Vmax individual de um relatório (base * dificuldade).

        Args:
            relatorio: Entidade Relatorio para calcular o Vmax.

        Returns:
            Valor float representando o Vmax daquele relatório específico.
        """
        if relatorio.folha_gabarito is None:
            logger.warning("Relatório %s sem gabarito. Vmax tratado como 0", relatorio.id_cenario)
            return 0.0

        v_max = self.VALOR_BASE_PARTICIPACAO

        risco = len(relatorio.folha_gabarito.riscos)
        v_max += risco * self.BONUS_RISCO

        fator = len(relatorio.folha_gabarito.fatores_inseguranca)
        v_max += fator * self.BONUS_FATOR

        for anexo in relatorio.obter_anexos():
            if anexo.get_tipo_midia() == "IMAGEM":
                v_max += self.BONUS_MIDIA_IMAGEM
            elif anexo.get_tipo_midia() == "VIDEO":
                v_max += self.BONUS_MIDIA_VIDEO
            elif anexo.get_tipo_midia() == "AUDIO":
                v_max += self.BONUS_MIDIA_AUDIO

        envolvidos = len(relatorio.envolvidos)
        v_max += envolvidos * self.BONUS_CONTEXTO

        return v_max * relatorio.dificuldade

    def calcular_meta_turno(self, lista_relatorios: List[Relatorio]) -> float:
        """
        Varre a pilha de relatórios do dia para calcular o Vmax total (A pontuação
        máxima absoluta caso o jogador faça tudo perfeito e em tempo recorde).

        Args:
            lista_relatorios: Lista de entidades Relatorio do turno atual.

        Returns:
            Valor float representando 100% da nota do expediente.
        """
        if not lista_relatorios:
            raise ValueError("[Erro - Relatorio] Lista de Relatorios Vazio")

        v_max_total = 0.0

        for relatorio in lista_relatorios:
            v_max_total += self.calcular_vmax_relatorio(relatorio)

        return v_max_total

    def calcular_pontuacao_relatorio(self, v_max: float, dados_pontuacao: DiagnosticoPontuacaoDTO) -> float:
        """
        O coracao do motor. Orquestra a chamada de todos os metodos de calculo
        individuais e consolida a nota final do relatorio avaliado.
        """
        st = self.__calcular_subtotais(v_max, dados_pontuacao)
        return (st.nota_riscos + st.nota_fatores + st.nota_decisao) * st.fator_tempo

    def calcular_pontuacao_detalhada(
        self, v_max: float, dados_pontuacao: DiagnosticoPontuacaoDTO,
        feedback: DiagnosticoFeedbackDTO,
    ) -> DiagnosticoPontuacaoDTO:
        """
        Variante de calcular_pontuacao_relatorio que expoe todos os
        sub-totais intermedios, preenchendo o DiagnosticoPontuacaoDTO
        completo com 15 campos.
        """
        st = self.__calcular_subtotais(v_max, dados_pontuacao)

        soma_subtotais = st.nota_riscos + st.nota_fatores + st.nota_decisao
        nota_final = soma_subtotais * st.fator_tempo
        pontos_bonus_tempo = soma_subtotais * (st.fator_tempo - 1.0)

        return DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=dados_pontuacao.qnt_riscos_marcados,
            qnt_riscos_gabarito=dados_pontuacao.qnt_riscos_gabarito,
            qnt_riscos_corretos_marcados=dados_pontuacao.qnt_riscos_corretos_marcados,
            estado_ato=dados_pontuacao.estado_ato,
            estado_condicao=dados_pontuacao.estado_condicao,
            status_decisao_jogador=dados_pontuacao.status_decisao_jogador,
            tempo_resposta_segundos=dados_pontuacao.tempo_resposta_segundos,
            pontuacao_final=nota_final,
            nota_riscos=st.nota_riscos,
            nota_fatores=st.nota_fatores,
            nota_decisao=st.nota_decisao,
            pontos_bonus_tempo=pontos_bonus_tempo,
            qnt_fatores_gabarito=dados_pontuacao.qnt_fatores_gabarito,
            qnt_fatores_marcados=dados_pontuacao.qnt_fatores_marcados,
            decisao_anulada=st.decisao_anulada,
        )

    class _Subtotais(NamedTuple):
        """Resultado intermedio dos tres eixos de pontuacao, do fator tempo e do flag de decisao anulada."""

        nota_riscos: float
        nota_fatores: float
        nota_decisao: float
        fator_tempo: float
        decisao_anulada: bool

    def __calcular_subtotais(self, v_max: float, dados_pontuacao: DiagnosticoPontuacaoDTO) -> _Subtotais:
        nota_riscos = self._calcular_pontuacao_riscos(
            v_max=v_max,
            riscos_corretos_marcados=dados_pontuacao.qnt_riscos_corretos_marcados,
            riscos_no_gabarito=dados_pontuacao.qnt_riscos_gabarito,
            riscos_marcados=dados_pontuacao.qnt_riscos_marcados,
        )
        nota_fatores = self._calcular_pontuacao_inseguranca(
            v_max=v_max,
            acertou_ato=dados_pontuacao.estado_ato,
            acertou_condicao=dados_pontuacao.estado_condicao,
            qnt_fatores_gabarito=dados_pontuacao.qnt_fatores_gabarito,
            qnt_fatores_marcados=dados_pontuacao.qnt_fatores_marcados,
        )
        nota_decisao = self._calcular_pontuacao_decisao(
            v_max=v_max,
            status_decisao=dados_pontuacao.status_decisao_jogador,
        )

        decisao_anulada = nota_riscos == 0.0 and nota_fatores == 0.0

        if decisao_anulada:
            nota_decisao = 0.0

        fator_tempo = self._calcular_fator_tempo(dados_pontuacao.tempo_resposta_segundos)

        return self._Subtotais(nota_riscos, nota_fatores, nota_decisao, fator_tempo, decisao_anulada)

    def calcular_scores_por_item(
        self, v_max: float, feedback: DiagnosticoFeedbackDTO,
    ) -> tuple[dict[str, float], dict[str, float]]:
        """
        Decompoe as notas de riscos e factores em scores
        individuais para os tiles da tela de diagnostico,
        respeitando a restricao de que a soma dos scores
        por eixo iguala a nota real correspondente.

        Returns:
            (score_por_risco, score_por_fator) — dicts nome → float.
        """
        score_por_risco: dict[str, float] = {}
        score_por_fator: dict[str, float] = {}

        self.__decompor_riscos(v_max, feedback, score_por_risco)
        self.__decompor_fatores(v_max, feedback, score_por_fator)

        return score_por_risco, score_por_fator

    def __decompor_riscos(
        self, v_max: float, feedback: DiagnosticoFeedbackDTO,
        score_por_risco: dict[str, float],
    ) -> None:
        total_gabarito = len(feedback.riscos_acertados) + len(feedback.riscos_esquecidos)
        total_acertos = len(feedback.riscos_acertados)
        total_marcados = total_acertos + len(feedback.riscos_inventados)
        base = v_max * self.PESO_RISCOS

        if total_gabarito == 0:
            for risco in feedback.riscos_inventados:
                score_por_risco[risco] = 0.0
            for risco in feedback.riscos_esquecidos:
                score_por_risco[risco] = 0.0
            return

        if total_acertos == 0:
            for risco in feedback.riscos_acertados:
                score_por_risco[risco] = 0.0
            for risco in feedback.riscos_inventados:
                score_por_risco[risco] = 0.0
            for risco in feedback.riscos_esquecidos:
                score_por_risco[risco] = 0.0
            return

        score_acerto = base / total_gabarito
        score_invento = -(base * total_acertos) / (total_gabarito * total_marcados)

        for risco in feedback.riscos_acertados:
            score_por_risco[risco] = score_acerto
        for risco in feedback.riscos_inventados:
            score_por_risco[risco] = score_invento
        for risco in feedback.riscos_esquecidos:
            score_por_risco[risco] = 0.0

    def __decompor_fatores(
        self, v_max: float, feedback: DiagnosticoFeedbackDTO,
        score_por_fator: dict[str, float],
    ) -> None:
        gabarito_set = set(feedback.fatores_acertados) | set(feedback.fatores_esquecidos)
        marcados_set = set(feedback.fatores_acertados) | set(feedback.fatores_inventados)

        estado_ato = ("ATO_INSEGURO" in gabarito_set) and ("ATO_INSEGURO" in marcados_set)
        estado_condicao = ("CONDICAO_INSEGURA" in gabarito_set) and ("CONDICAO_INSEGURA" in marcados_set)

        denominador = max(1, len(gabarito_set), len(marcados_set))
        score_acerto = v_max * self.PESO_FATORES / denominador

        score_por_fator["ATO_INSEGURO"] = score_acerto if estado_ato else 0.0
        score_por_fator["CONDICAO_INSEGURA"] = score_acerto if estado_condicao else 0.0

    def conferir_condicao_vitoria(self, pontuacao_obtida: float, pontuacao_maxima: float) -> bool:
        """
        Verifica se a pontuação atingiu o limiar de aprovação do turno (ex: >= 60%).

        Se o Vmax total for zero ou negativo (ex: todos os relatorios quebrados),
        retorna False independentemente da pontuacao obtida.
        """
        if pontuacao_maxima <= 0.0:
            logger.warning(
                "[MotorDePontuacao] Vmax do turno e %.2f — condicao de vitoria retorna False.",
                pontuacao_maxima,
            )
            return False

        return pontuacao_obtida >= pontuacao_maxima * self.LIMIAR_VITORIA_TURNO

    def _calcular_pontuacao_riscos(
        self, v_max: float, riscos_corretos_marcados: int,
        riscos_no_gabarito: int, riscos_marcados: int,
    ) -> float:
        """
        Calcula a nota de riscos com base em Taxa de Descoberta (Td) e Taxa de Precisão (Tp).

        P_risco = (Vmax * 0.60) * Td * Tp
        """
        p_riscos_base = v_max * self.PESO_RISCOS

        if riscos_no_gabarito == 0:
            if riscos_marcados != 0:
                return 0.0
            return p_riscos_base

        if riscos_corretos_marcados == 0 or riscos_marcados == 0:
            return 0.0

        taxa_descoberta = riscos_corretos_marcados / riscos_no_gabarito
        taxa_precisao = riscos_corretos_marcados / riscos_marcados

        P_riscos = p_riscos_base * taxa_descoberta * taxa_precisao
        return P_riscos

    def _calcular_pontuacao_inseguranca(
        self, v_max: float, acertou_ato: bool, acertou_condicao: bool,
        qnt_fatores_gabarito: int = 0, qnt_fatores_marcados: int = 0,
    ) -> float:
        """
        Calcula a nota de fatores de inseguranca conforme o modelo:
        P_inseg = (Vmax * 0.15) * C_exatidao

        O coeficiente de exatidao e a proporcao de factores do gabarito
        que o jogador correctamente identificou. Factores correctamente
        ausentes nao pontuam. O denominador usa max(g, m) para penalizar
        invencoes de factores inexistentes.
        """
        denominador = max(1, qnt_fatores_gabarito, qnt_fatores_marcados)

        acertou_ato = int(acertou_ato)
        acertou_condicao = int(acertou_condicao)

        coeficiente_exatidao = (acertou_ato + acertou_condicao) / denominador

        P_inseg = v_max * self.PESO_FATORES * coeficiente_exatidao
        return P_inseg

    def _calcular_pontuacao_decisao(self, v_max: float, status_decisao: str) -> float:
        """Calcula a pontuação da decisão administrativa com base no Vmax e no mapeamento de decisão."""
        if status_decisao == "OTIMA":
            return v_max * self.PESO_DECISAO_OTIMA
        if status_decisao == "BOA":
            return v_max * self.PESO_DECISAO_BOA
        return 0.0

    def _calcular_fator_tempo(self, t: float) -> float:
        """
        Calcula o fator de tempo (multiplicador de decaimento) com base no tempo investido.
        Decai linearmente apos T_ideal ate atingir o piso L_min.
        """
        T_ideal = self.TEMPO_IDEAL_SEGUNDOS
        alpha = self.__taxa_decaimento
        L_min = self.__limite_minimo_retencao

        if t <= T_ideal:
            return 1.0

        return max(L_min, 1.0 - alpha * (t - T_ideal))
