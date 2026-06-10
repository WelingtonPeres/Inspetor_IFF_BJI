from abc import ABC
from typing import List
from unidecode import unidecode


class FolhaDeInspecao(ABC):
    """
    Classe Abstrata que representa a estrutura de dados dos itens a serem inspecionados em um cenário. Serve como base para a construção de gabaritos e respostas.
    """
    
    LISTA_RISCOS_VALIDOS = ["FISICO", "QUIMICO", "BIOLOGICO", "ERGONOMICO", "ACIDENTE"]
    FATORES_INSEGURANCA_VALIDOS = ["ATO_INSEGURO", "CONDICAO_INSEGURA"]

    def __init__(self, riscos: List[str], fatores_inseguranca: List[str]):
        
        # Cuidados de Entrada
        riscos_em_maiusculas = []
        for risco in riscos:
            risco_sem_acentos = unidecode(risco) # Remove acentos e caracteres especiais
            risco_em_maiusculas = risco_sem_acentos.upper() # Converte para maiúsculas
            riscos_em_maiusculas.append(risco_em_maiusculas)
        
        riscos_invalidos = set(riscos_em_maiusculas) - set(FolhaDeInspecao.LISTA_RISCOS_VALIDOS)
        if len(riscos_invalidos) > 0:
            raise ValueError(f"[Erro] Riscos inválidos encontrados: {riscos_invalidos}.")
                
        fatores_inseguranca_em_maiusculas = []
        for fator in fatores_inseguranca:
            fator_sem_acentos = unidecode(fator) 
            fator_em_maiusculas = fator_sem_acentos.upper() 
            fatores_inseguranca_em_maiusculas.append(fator_em_maiusculas)

        fatores_inseguranca_invalidos = set(fatores_inseguranca_em_maiusculas) - set(FolhaDeInspecao.FATORES_INSEGURANCA_VALIDOS)
        if len(fatores_inseguranca_invalidos) > 0:
            raise ValueError(f"[Erro] Fatores de insegurança inválidos encontrados: {fatores_inseguranca_invalidos}.")
        
        
        self.__riscos = riscos_em_maiusculas
        self.__fatores_inseguranca = fatores_inseguranca_em_maiusculas
        
    @property
    def riscos(self) -> List[str]:
        return self.__riscos
    
    @property
    def fatores_inseguranca(self) -> List[str]:
        return self.__fatores_inseguranca
        
        
    def contar_riscos(self) -> int:
        return len(self.__riscos)
        
    def contar_fatores(self) -> int:
        return len(self.__fatores_inseguranca)
