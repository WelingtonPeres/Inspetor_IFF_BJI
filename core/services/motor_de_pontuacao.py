from typing import List, Dict, Any

from core.model.relatorio import Relatorio

class MotorDePontuacao:
    """
    Responsável por processar a lógica matemática determinística do jogo, avaliando a acurácia (riscos/fatores), a decisão administrativa e a eficiência temporal.
    """

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
    BONUS_CONTEXTO = 100
    
    # Variáveis de Tempo e Condição de Vitória
    TEMPO_IDEAL_SEGUNDOS = 120
    TAXA_DECAIMENTO_ALFA = 0.01
    LIMITE_MINIMO_RETENCAO = 0.20
    LIMIAR_VITORIA_TURNO = 0.60

    def __init__(self, t:float, taxa_decaimento: float = 0.05, limite_minimo_retencao: float = 0.20 ):
        """
        Injeta as variáveis de calibragem matemática do motor.
        
        Args:
            taxa_decaimento: Valor de decréscimo da nota por segundo extra (alfa).
            limite_minimo_retencao: Piso mínimo do fator de tempo (L_min), ex: 0.20 (20%).
        """
        # Encapsulamento das configurações do motor
        self.__taxa_decaimento = taxa_decaimento
        self.__limite_minimo_retencao = limite_minimo_retencao



    def calcular_meta_turno(self, lista_relatorios: List[Relatorio]) -> float:
        """
        Varre a pilha de relatórios do dia para calcular o Vmax total (A pontuação 
        máxima absoluta caso o jogador faça tudo perfeito e em tempo recorde).
        
        Args:
            lista_relatorios: Lista de entidades Relatorio do turno atual.
        Returns:
            Valor float representando 100% da nota do expediente.
        """
        return sum(self._calcular_vmax(relatorio) for relatorio in lista_relatorios or [])

    def calcular_pontuacao_relatorio(self, dados_comparacao: Dict[str, Any]) -> Dict[str, Any]:
        """
        O coração do motor. Orquestra a chamada de todos os métodos de cálculo
        individuais e consolida a nota final do relatório avaliado.

        Args:
            dados_comparacao: Dicionário contendo o gabarito do Relatório cruzado 
                                 com as escolhas e o tempo gasto pelo jogador.
        Returns:
            Dicionário detalhado com as parciais (nota_riscos, nota_fatores, nota_decisao, 
            fator_tempo e nota_final).
        """
        v_max = float(dados_comparacao.get("v_max", 0.0))
        riscos = dados_comparacao.get("riscos", {}) or {}
        fatores = dados_comparacao.get("fatores_inseguranca", {}) or {}
        decisao = dados_comparacao.get("decisao", {}) or {}

        riscos_marcados = riscos.get("marcados", []) if isinstance(riscos, dict) else []
        riscos_gabarito = riscos.get("gabarito", []) if isinstance(riscos, dict) else []
        fatores_marcados = fatores.get("marcados", []) if isinstance(fatores, dict) else []
        fatores_gabarito = fatores.get("gabarito", []) if isinstance(fatores, dict) else []

        nota_riscos = self._calcular_pontuacao_riscos(v_max, riscos_marcados, riscos_gabarito)
        nota_fatores = self._calcular_pontuacao_inseguranca(v_max, fatores_marcados, fatores_gabarito)
        nota_decisao = self._calcular_pontuacao_decisao(
            v_max,
            decisao.get("escolha_jogador", ""),
            decisao.get("gabarito_otimo", ""),
            decisao.get("gabarito_subotimo", "")
        )

        tempo_gasto = float(dados_comparacao.get("tempo_gasto_segundos", dados_comparacao.get("tempo", 0.0)))
        fator_tempo = self._calcular_fator_tempo(
            tempo_gasto,
            self.TEMPO_IDEAL_SEGUNDOS,
            self.__taxa_decaimento,
            self.__limite_minimo_retencao,
        )

        nota_final = (nota_riscos + nota_fatores + nota_decisao) * fator_tempo

        return {
            "nota_riscos": nota_riscos,
            "nota_fatores": nota_fatores,
            "nota_decisao": nota_decisao,
            "fator_tempo": fator_tempo,
            "nota_final": nota_final,
            "v_max": v_max,
        }

    def conferir_condicao_vitoria(self, pontuacao_obtida: float, pontuacao_maxima: float) -> bool:
        """
        Verifica se a pontuação atingiu o limiar de aprovação do turno (ex: >= 60%).
        """
        return pontuacao_obtida >= pontuacao_maxima * self.LIMIAR_VITORIA_TURNO

    def _calcular_vmax(self, relatorio: Relatorio) -> float:
        riscos = len(relatorio.folha_gabarito.riscos)
        fatores = len(relatorio.folha_gabarito.fatores_inseguranca)
        anexos = relatorio.obter_anexos()
        imagens = sum(1 for anexo in anexos if anexo.get_tipo_midia() == "IMAGEM")
        videos = sum(1 for anexo in anexos if anexo.get_tipo_midia() == "VIDEO")
        contexto = len(relatorio.envolvidos)

        subtotal_quant = (
            self.VALOR_BASE_PARTICIPACAO
            + riscos * self.BONUS_RISCO
            + fatores * self.BONUS_FATOR
            + imagens * self.BONUS_MIDIA_IMAGEM
            + videos * self.BONUS_MIDIA_VIDEO
            + contexto * self.BONUS_CONTEXTO
        )

        return subtotal_quant * relatorio.dificuldade


    def _calcular_pontuacao_riscos(self, v_max: float, marcados: List[str], gabarito: List[str]) -> float:
        """
        Calcula a nota de riscos com base em Taxa de Descoberta (Td) e Taxa de Precisão (Tp).

        P_risco = (Vmax * 0.60) * Td * Tp
        """
        marcados_set = {str(item).strip().upper() for item in (marcados or [])}
        gabarito_set = {str(item).strip().upper() for item in (gabarito or [])}

        total_gabarito = len(gabarito_set)
        total_marcados = len(marcados_set)

        if total_gabarito == 0:
            return v_max * self.PESO_RISCOS if total_marcados == 0 else 0.0

        acertos_reais = len(marcados_set.intersection(gabarito_set))
        taxa_descoberta = acertos_reais / total_gabarito
        taxa_precisao = acertos_reais / total_marcados if total_marcados > 0 else 0.0

        return v_max * self.PESO_RISCOS * taxa_descoberta * taxa_precisao

    def _calcular_pontuacao_inseguranca(self, v_max: float, marcados: List[str], gabarito: List[str]) -> float:
        """
        Calcula a nota de fatores de insegurança conforme o modelo:
        P_inseg = (Vmax * 0.15) * C_exatidao

        O coeficiente de exatidão é a média dos acertos binários de estado:
        S_ato e S_cond.
        """
        marcados_set = {str(item).strip().upper() for item in (marcados or [])}
        gabarito_set = {str(item).strip().upper() for item in (gabarito or [])}

        acertou_ato = int(('ATO_INSEGURO' in marcados_set) == ('ATO_INSEGURO' in gabarito_set))
        acertou_condicao = int(('CONDICAO_INSEGURA' in marcados_set) == ('CONDICAO_INSEGURA' in gabarito_set))

        coeficiente_exatidao = (acertou_ato + acertou_condicao) / 2.0

        return v_max * self.PESO_FATORES * coeficiente_exatidao

    def _calcular_pontuacao_decisao(
        self,
        v_max: float,
        decisao_jogador: str,
        decisao_otima: str,
        decisao_boa: str,
        peso_otima: float = PESO_DECISAO_OTIMA,
        peso_boa: float = PESO_DECISAO_BOA,
    ) -> float:
        """
        Calcula a pontuação da decisão administrativa com base no Vmax e no mapeamento de decisão.

        :param v_max: Valor máximo do relatório.
        :param decisao_jogador: Decisão escolhida pelo jogador.
        :param decisao_otima: Decisão ótima registrada no gabarito.
        :param decisao_boa: Decisão subótima registrada no gabarito.
        :param peso_otima: Percentual do Vmax para decisão ótima.
        :param peso_boa: Percentual do Vmax para decisão subótima.
        :return: Pontuação de decisão calculada.
        """
        decisao = (decisao_jogador or "").strip().upper()
        decisao_otima = (decisao_otima or "").strip().upper()
        decisao_boa = (decisao_boa or "").strip().upper()

        if decisao == decisao_otima:
            return v_max * peso_otima

        if decisao == decisao_boa:
            return v_max * peso_boa

        return 0.0

    def _calcular_fator_tempo(self, t: float, T_ideal: float, alpha: float, L_min: float) -> float:
        """
        Calcula o fator de tempo (multiplicador de decaimento) com base no tempo investido.

        :param t: Tempo investido na inspeção.
        :param T_ideal: Tempo ideal para completar a tarefa.
        :param alpha: Taxa de rigor para o decaimento linear.
        :param L_min: Limite mínimo de retenção.
        :return: Fator de tempo calculado.
        """
        if t <= T_ideal:
            return 1.0
        elif t <= 1.5 * T_ideal:
            return max(1.0 - alpha * (t - T_ideal), L_min)
        else:
            return L_min