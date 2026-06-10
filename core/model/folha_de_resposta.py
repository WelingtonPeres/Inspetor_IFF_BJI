from typing import List

from .folha_de_inspecao import FolhaDeInspecao


class FolhaDeResposta(FolhaDeInspecao):
    """Representa a folha de resposta preenchida pelo jogador, contendo os riscos e fatores que ele marcou, bem como a decisão administrativa tomada."""
    
    LISTA_DECISOES_VALIDAS = ["INTERDITAR", "ADVERTIR", "IGNORAR"]
    
    def __init__(self, riscos: List[str], fatores_inseguranca: List[str], decisao_tomada: str, tempo_gasto_segundos: int):
        
        super().__init__(riscos, fatores_inseguranca)
        
        if decisao_tomada.upper() not in FolhaDeResposta.LISTA_DECISOES_VALIDAS:
            raise ValueError(f"[Erro] Decisão tomada inválida: {decisao_tomada}")
        
        if tempo_gasto_segundos < 0:
            raise ValueError(f"[Erro] Tempo gasto inválido: {tempo_gasto_segundos}. Deve ser um valor não negativo.")
        
        self.__decisao_tomada = decisao_tomada
        self.__tempo_gasto_segundos = tempo_gasto_segundos

    @property
    def decisao_tomada(self) -> str:
        return self.__decisao_tomada

    @property
    def tempo_gasto_segundos(self) -> int:
        return self.__tempo_gasto_segundos
