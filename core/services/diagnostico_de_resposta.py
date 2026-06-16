from typing import List, Dict, Any

from core.model.folha_de_gabarito import FolhaDeGabarito
from core.model.folha_de_resposta import FolhaDeResposta

from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from core.services.diagnostico_feedback import DiagnosticoFeedback

class DiagnosticoDeResposta:
    """
    Responsável por confrontar o input do jogador com o gabarito oficial e extrair as métricas brutas de acertos 
    e falsos alarmes para serem consumidas.
    """

    def gerar_diagnostico_pontuacao(self, gabarito: FolhaDeGabarito, respostas: FolhaDeResposta) -> DiagnosticoPontuacaoDTO:
        """
        Gerar um diagnóstico de pontuação a partir do confronto entre o gabarito e as respostas do jogador. 
        
        Args:
            gabarito (FolhaDeGabarito): O gabarito oficial contendo as respostas corretas.
            respostas (FolhaDeResposta): As respostas fornecidas pelo jogador.
            
        Returns:
            DiagnosticoPontuacaoDTO: Um objeto contendo as métricas de acertos, falsos alarmes, e outras informações relevantes para a pontuação do jogador.
        """
        
        set_riscos_marcados = set(respostas.riscos)
        set_riscos_gabarito = set(gabarito.riscos)
        qnt_riscos_corretos_marcados = len(set_riscos_marcados & set_riscos_gabarito) # Interseção dos riscos marcados com os riscos do gabarito para contar os acertos
        
        estado_ato_resposta = "ATO_INSEGURO" in respostas.fatores_inseguranca
        estado_ato_gabarito = "ATO_INSEGURO" in gabarito.fatores_inseguranca        
        estado_ato = (estado_ato_resposta == estado_ato_gabarito) # True se o jogador acertou o estado do ato inseguro, False caso contrário.
        
        estado_condicao_resposta = "CONDICAO_INSEGURA" in respostas.fatores_inseguranca
        estado_condicao_gabarito = "CONDICAO_INSEGURA" in gabarito.fatores_inseguranca
        estado_condicao = (estado_condicao_resposta == estado_condicao_gabarito) 

        if respostas.decisao_tomada == gabarito.decisao_otima:
            decisao_jogador = "OTIMA"
        elif respostas.decisao_tomada == gabarito.decisao_boa:
            decisao_jogador = "BOA"
        else:
            decisao_jogador = "INCORRETA"
            
        
        diagnostico_pontuacao = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=len(set_riscos_marcados),
            qnt_riscos_gabarito=len(set_riscos_gabarito),
            qnt_riscos_corretos_marcados=qnt_riscos_corretos_marcados, 
            estado_ato=estado_ato,
            estado_condicao=estado_condicao,
            decisao_jogador=decisao_jogador,
            tempo_resposta_segundos=respostas.tempo_gasto_segundos
        )
        
        return diagnostico_pontuacao

    def __gerar_diagnostico_feedback(self, gabarito: FolhaDeGabarito, respostas: FolhaDeResposta) -> DiagnosticoFeedback:
        # Implementação futura: Gerar um diagnóstico de feedback detalhado para fornecer orientações específicas ao jogador com base em seus erros e acertos.
        pass
    
