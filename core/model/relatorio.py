from typing import List

from .anexo import Anexo
from .folha_de_gabarito import FolhaDeGabarito
from .folha_de_resposta import FolhaDeResposta

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
                 envolvidos: List[str], 
                 cursos: List[str],
                 dificuldade: int, 
                 gabarito: FolhaDeGabarito):
        
        self.__id_cenario = id_cenario
        self.__titulo = titulo
        self.__atividade = atividade
        self.__local = local
        self.__texto_descricao = texto_descricao
        self.__envolvidos = envolvidos
        
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
