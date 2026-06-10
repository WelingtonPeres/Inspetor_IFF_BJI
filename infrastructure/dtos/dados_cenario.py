from dataclasses import dataclass
from typing import List

@dataclass
class DadosAnexoDTO:
    """DTO menor que representa um único arquivo de mídia anexado."""
    id_anexo: int
    tipo: str
    caminho_arquivo: str

@dataclass
class DadosCenarioDTO:
    """DTO principal que carrega todos os dados, incluindo os anexos."""
    id_cenario: int
    titulo: str
    dificuldade: int
    atividade: str
    local: str
    texto_descricao: str
    envolvidos: List[str]
    cursos: List[str]
    riscos: List[str]
    fatores_inseguranca: List[str]
    decisao_otima: str
    decisao_boa: str
    
    anexos: List[DadosAnexoDTO]