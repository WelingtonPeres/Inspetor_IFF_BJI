from typing import List

from .folha_de_inspecao import FolhaDeInspecao


class FolhaDeGabarito(FolhaDeInspecao):
    """Representa a folha de gabarito com os riscos, fatores de insegurança e decisões ótimas e subótimas."""
    
    LISTA_DECISOES_VALIDAS = ["INTERDITAR", "ADVERTIR", "IGNORAR"]
    
    def __init__(self, riscos: List[str], fatores_inseguranca: List[str], decisao_otima: str, decisao_boa: str):
        
        super().__init__(riscos, fatores_inseguranca)
        
        if decisao_otima.upper() not in FolhaDeGabarito.LISTA_DECISOES_VALIDAS:
            raise ValueError(f"[Erro] Decisão ótima inválida: {decisao_otima}")
        
        if decisao_boa.upper() not in FolhaDeGabarito.LISTA_DECISOES_VALIDAS:
            raise ValueError(f"[Erro] Decisão subótima inválida: {decisao_boa}")
        
        if decisao_otima.upper() == decisao_boa.upper():
            raise ValueError(f"[Erro] Decisão ótima e decisão boa não podem ser iguais: {decisao_otima}")
        
        self.__decisao_otima = decisao_otima
        self.__decisao_boa = decisao_boa
        
    @property
    def decisao_otima(self) -> str:
        return self.__decisao_otima
    
    @property
    def decisao_boa(self) -> str:
        return self.__decisao_boa
