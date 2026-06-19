from abc import ABC, abstractmethod
from typing import Dict, Any

class Anexo(ABC):
    """
    Representa uma evidência visual anexada a um relatório de inspeção.
    """
    
    def __init__(self, id_anexo: int, caminho_arquivo: str):
        
        if id_anexo < 0:
            raise ValueError(f"[Erro] id_anexo não pode ser negativo: {id_anexo}")
        
        if not caminho_arquivo:
            raise ValueError("[Erro] caminho_arquivo não pode ser vazio")
        
        self.__id_anexo = id_anexo
        self.__caminho_arquivo = caminho_arquivo


    @property
    def id_anexo(self) -> int:
        return self.__id_anexo

    @property
    def caminho_arquivo(self) -> str:
        return self.__caminho_arquivo


    @abstractmethod
    def get_tipo_midia(self) -> str:
        """
        Útil para a UI saber qual player de mídia abrir
        """

    def extrair_dados(self) -> dict:
        """
        Gera uma Estrutura de Dados (Dict) apenas com os dados necessários para a engine gráfica renderizar a mídia.
        """
        return {
            "id_anexo": self.__id_anexo,
            "tipo_midia": self.get_tipo_midia(),
            "caminho_arquivo": self.__caminho_arquivo,
        }


class AnexoImagem(Anexo):
    """
    Representa uma fotografia estática do ambiente inspecionado.
    """
    
    def get_tipo_midia(self) -> str:
        return "IMAGEM"

class AnexoVideo(Anexo):
    """
    Representa um clipe de vídeo da operação (ex: máquina em funcionamento).
    """
    
    def get_tipo_midia(self) -> str:
        return "VIDEO"

class AnexoAudio(Anexo):
    """
    Representa uma gravação de áudio, como um depoimento ou som ambiente.
    """
    
    def get_tipo_midia(self) -> str:
        return "AUDIO"
