from typing import List, Dict, Any

from core.model.relatorio import Relatorio

class AnalisadorDeDiagnostico:
    """
    Responsável por confrontar o input do jogador com o gabarito oficial (Entidade Relatorio)
    e extrair as métricas brutas de acertos e falsos alarmes para serem consumidas 
    pelo Motor de Pontuação.
    """

    @staticmethod
    def gerar_boletim_comparativo(relatorio_gabarito: Relatorio, input_jogador: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orquestra a comparação de todos os eixos da inspeção.
        
        Args:
            - relatorio_gabarito (Relatorio) : A entidade Relatorio contendo a verdade absoluta do cenário.
            - input_jogador (Dict[str, Any]) : Dicionário contendo as escolhas feitas na interface gráfica.
            
        Returns:
            - (Dict[str, Any]) : Um Dicionário (Boletim) formatado estritamente para o MotorDePontuacao.
        """
        
        # Comparação de Riscos (Físico, Químico, etc.)
        riscos_jogador = input_jogador.get("riscos_marcados", [])
        metricas_riscos = AnalisadorDeDiagnostico._comparar_riscos(
            gabarito=relatorio_gabarito.riscos, 
            marcados=riscos_jogador
        )
        
        # Comparação de Fatores de Insegurança (Ato vs Condição)
        fatores_jogador = input_jogador.get("fatores_marcados", [])
        metricas_fatores = AnalisadorDeDiagnostico._avaliar_exatidao_fatores(
            gabarito=relatorio_gabarito.fatores_inseguranca,
            marcados=fatores_jogador
        )
        
        # Consolidação do Boletim para o Motor de Pontuação
        boletim = {
            "riscos": metricas_riscos,
            "fatores_inseguranca": metricas_fatores,
            "decisao": {
                "escolha_jogador": input_jogador.get("decisao", "IGNORAR"),
                "gabarito_otimo": relatorio_gabarito.decisao_otima,
                "gabarito_subotimo": relatorio_gabarito.decisao_subotima
            }
        }
        
        return boletim

    @staticmethod
    def _comparar_riscos(gabarito: tuple, marcados: List[str]) -> Dict[str, int]:
        """
        Cruza os riscos e retorna as métricas necessárias para Td (Descoberta) e Tp (Precisão).
        """
        # TODO: Converter as listas/tuplas em Set (Conjuntos) do Python.
        # TODO: Usar a interseção de conjuntos (set.intersection) para achar os Acertos.
        # TODO: Montar e retornar um dicionário com: total_gabarito, total_marcados e acertos_reais.
        pass

    @staticmethod
    def _avaliar_exatidao_fatores(gabarito: tuple, marcados: List[str]) -> Dict[str, int]:
        """
        Avalia a natureza binária (Ato Inseguro / Condição Insegura) conforme a Seção 2.2 do documento.
        """
        # TODO: Verificar se "ATO_INSEGURO" do gabarito bate com a marcação (1 para sim, 0 para não).
        # TODO: Verificar se "CONDICAO_INSEGURA" do gabarito bate com a marcação (1 para sim, 0 para não).
        # TODO: Retornar dicionário com os valores (S_ato e S_cond).
        pass