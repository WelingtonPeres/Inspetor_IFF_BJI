import logging
from typing import List, Dict, Any

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from core.model.relatorio import Relatorio

logger = logging.getLogger(__name__)

class MotorDePontuacao:
    """
    Responsável por processar a lógica matemática determinística do jogo, avaliando a acurácia (riscos/fatores), 
    a decisão administrativa e a eficiência temporal.
    """
    
    TAXA_DECAIMENTO_ALFA = 0.01
    LIMITE_MINIMO_RETENCAO = 0.20

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
    
    TEMPO_IDEAL_SEGUNDOS = 60
    LIMIAR_VITORIA_TURNO = 0.60

    def __init__(self):
        """
        Injeta as variáveis de calibragem matemática do motor.
        """
        
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
        O coração do motor. Orquestra a chamada de todos os métodos de cálculo
        individuais e consolida a nota final do relatório avaliado.
        """

        nota_riscos = self._calcular_pontuacao_riscos(
            v_max=v_max, 
            riscos_corretos_marcados=dados_pontuacao.qnt_riscos_corretos_marcados, 
            riscos_no_gabarito=dados_pontuacao.qnt_riscos_gabarito,
            riscos_marcados=dados_pontuacao.qnt_riscos_marcados
        )
        
        nota_fatores = self._calcular_pontuacao_inseguranca(
            v_max=v_max, 
            acertou_ato=dados_pontuacao.estado_ato, 
            acertou_condicao=dados_pontuacao.estado_condicao
        )
        
        nota_decisao = self._calcular_pontuacao_decisao(
            v_max=v_max, 
            status_decisao=dados_pontuacao.status_decisao_jogador
        )

        tempo_gasto = self._calcular_fator_tempo(dados_pontuacao.tempo_resposta_segundos)
        
        nota_final = (nota_riscos + nota_fatores + nota_decisao) * tempo_gasto
        return nota_final

    def conferir_condicao_vitoria(self, pontuacao_obtida: float, pontuacao_maxima: float) -> bool:
        """
        Verifica se a pontuação atingiu o limiar de aprovação do turno (ex: >= 60%).
        """
        return pontuacao_obtida >= pontuacao_maxima * self.LIMIAR_VITORIA_TURNO

    def _calcular_pontuacao_riscos(self, 
                                   v_max: float, 
                                   riscos_corretos_marcados: int, 
                                   riscos_no_gabarito: int,
                                   riscos_marcados: int) -> float:
        """
        Calcula a nota de riscos com base em Taxa de Descoberta (Td) e Taxa de Precisão (Tp).

        P_risco = (Vmax * 0.60) * Td * Tp
        """
        
        p_riscos_base = v_max * self.PESO_RISCOS # (Vmax * 0.60)

        if riscos_no_gabarito == 0: # Cenário não há riscos no gabarito. O jogador deve marcar zero para acertar.
            
            if riscos_marcados != 0:
                return 0.0 
            
            return p_riscos_base
        
        if riscos_corretos_marcados == 0 or riscos_marcados == 0:
            return 0.0
                
        taxa_descoberta = riscos_corretos_marcados / riscos_no_gabarito
        taxa_precisao = riscos_corretos_marcados / riscos_marcados

        P_riscos = p_riscos_base * taxa_descoberta * taxa_precisao

        return P_riscos

    def _calcular_pontuacao_inseguranca(self, 
                                        v_max: float, 
                                        acertou_ato: bool, 
                                        acertou_condicao: bool) -> float:
        """
        Calcula a nota de fatores de insegurança conforme o modelo:
        P_inseg = (Vmax * 0.15) * C_exatidao

        O coeficiente de exatidão é a média dos acertos binários de estado:
        S_ato e S_cond.
        """

        acertou_ato = int(acertou_ato)
        acertou_condicao = int(acertou_condicao)

        coeficiente_exatidao = (acertou_ato + acertou_condicao) / 2.0
        
        P_inseg = v_max * self.PESO_FATORES * coeficiente_exatidao

        return P_inseg

    def _calcular_pontuacao_decisao(self, v_max: float, status_decisao: str) -> float:
        """
        Calcula a pontuação da decisão administrativa com base no Vmax e no mapeamento de decisão.
        """
        if status_decisao == "OTIMA":
            return v_max * self.PESO_DECISAO_OTIMA

        if status_decisao == "BOA":
            return v_max * self.PESO_DECISAO_BOA

        return 0.0

    def _calcular_fator_tempo(self, t: float) -> float:
        """
        Calcula o fator de tempo (multiplicador de decaimento) com base no tempo investido.
        """
        T_ideal = self.TEMPO_IDEAL_SEGUNDOS
        alpha = self.__taxa_decaimento
        L_min = self.__limite_minimo_retencao
        
        if t <= T_ideal:
            return 1.0
        elif t <= 1.5 * T_ideal:
            return 1.0 - alpha * (t - T_ideal)
        else:
            return L_min