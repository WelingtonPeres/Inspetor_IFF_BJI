from abc import ABC
from typing import List, Set, Optional
from unidecode import unidecode

from ..model.anexo import Anexo

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


class FolhaDeGabarito(FolhaDeInspecao):
    """Representa a folha de gabarito com os riscos, fatores de insegurança e decisões ótimas e subótimas."""
    
    LISTA_DECISOES_VALIDAS = ["INTERDITAR", "ADVERTIR", "IGNORAR"]
    
    def __init__(self, riscos: List[str], fatores_inseguranca: List[str], decisao_otima: str, decisao_boa: str):
        
        super().__init__(riscos, fatores_inseguranca)
        
        if decisao_otima.upper() not in FolhaDeGabarito.LISTA_DECISOES_VALIDAS:
            raise ValueError(f"[Erro] Decisão ótima inválida: {decisao_otima}")
        
        if decisao_boa.upper() not in FolhaDeGabarito.LISTA_DECISOES_VALIDAS:
            raise ValueError(f"[Erro] Decisão subótima inválida: {decisao_boa}")
        
        self.__decisao_otima = decisao_otima
        self.__decisao_boa = decisao_boa
        
    @property
    def decisao_otima(self) -> str:
        return self.__decisao_otima
    
    @property
    def decisao_boa(self) -> str:
        return self.__decisao_boa


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

class Relatorio:
    """
    Guarda a apresentação visual, protege o gabarito e recebe a resposta do jogador.
    """
    
    def __init__(self, 
                 id_cenario: int, 
                 titulo: str, 
                 atividade: str,
                 local: str, 
                 texto_descricao: str,
                 lista_envolvidos: List[str], 
                 cursos: List[str],
                 dificuldade: int, 
                 gabarito: FolhaDeGabarito):
        
        self.__id_cenario = id_cenario
        self.__titulo = titulo
        self.__atividade = atividade
        self.__local = local
        self.__texto_descricao = texto_descricao
        self.__envolvidos = lista_envolvidos
        
        if dificuldade < 1 or dificuldade > 5:
            raise ValueError("[Erro] A dificuldade deve ser um inteiro entre 1 e 5.")
        
        self.__dificuldade = dificuldade
        self.__cursos = cursos
        
        self.__anexos = [] # O rlatório nasce sem anexos, mas pode ser enriquecido posteriormente por métodos específicos.
        
        self.__folha_gabarito = gabarito  # Protegido do Front-end
        self.__folha_resposta = None # Nasce por que ainda não existe resposta do jogador, mas será preenchida ao final do turno.
        
    @property
    def id_cenario(self) -> int:
        return self.__id_cenario

    @property
    def titulo(self) -> str:
        return self.__titulo

    @property
    def atividade(self) -> str:
        return self.__atividade

    @property
    def local(self) -> str:
        return self.__local

    @property
    def texto_descricao(self) -> str:
        return self.__texto_descricao

    @property
    def envolvidos(self) -> List[str]:
        return self.__envolvidos

    @property
    def dificuldade(self) -> int:
        return self.__dificuldade

    @property
    def cursos(self) -> List[str]:
        return self.__cursos
    
    @property
    def folha_gabarito(self) -> FolhaDeGabarito:
        return self.__folha_gabarito
    
    @property
    def folha_resposta_jogador(self) -> FolhaDeResposta:
        
        if self.__folha_resposta is None:
            raise ValueError("[Erro] A resposta do jogador ainda não foi anexada ao relatório.")
        
        return self.__folha_resposta
    
    def extrair_apresentacao_relatorio(self) -> dict:
        """
        Gera uma Estrutura de Dados (Dict) seguro apenas com os dados de apresentação do contexto de Relatório.
        
        Return: {
            "id_cenario": int,
            "titulo": str,
            "atividade": str,
            "local": str,
            "texto_descricao": str,
            "envolvidos": List[str],
            "anexos": List[dict] {
                "id_anexo": int,
                "tipo_midia": str,
                "caminho_arquivo": str
            } 
        }
        
        """
        lista_anexos_apresentacao = []
        for anexo in self.__anexos:
            lista_anexos_apresentacao.append(anexo.extrair_dados())            
        
        return {
            "id_cenario": self.__id_cenario,
            "titulo": self.__titulo,
            "atividade": self.__atividade,
            "local": self.__local,
            "texto_descricao": self.__texto_descricao,
            "envolvidos": self.__envolvidos,
            "anexos": lista_anexos_apresentacao,
        }
    
    # Métodos relacionados aos Anexos 
    def obter_anexos(self) -> List[Anexo]:
        """ Devolve a lista de anexos do relatório """
        return self.__anexos
    
    def adicionar_anexo(self, anexo: Anexo):
        """ Permite adicionar um anexo ao relatório """
        self.__anexos.append(anexo)
        
    def possui_anexos(self) -> bool:
        """ Verifica se o relatório tem anexos atribuídos """
        return len(self.__anexos) > 0
    
    # Métodos relacionados à resposta do jogador
    def anexar_resposta_jogador(self, resposta: FolhaDeResposta):
        """Recebe a parte do Relatório que o jogador preencheu e guarda internamente"""
        self.__folha_resposta = resposta
