from typing import List, Dict, Any
from pathlib import Path
import json

from ..dtos.dados_cenario import DadosCenarioDTO, DadosAnexoDTO

class RepositorioJSON:
    """
    Responsável por interagir com o sistema de arquivos do SO, localizar os 
    arquivos .json correspondentes ao curso escolhido e devolvê-los como DTO's para a Fábrica de Relatórios.
    """

    def __init__(self, diretorio_base: str, curso_selecionado: str, quantidade_gerada: int):
        """
        Inicializa o repositório com o caminho base onde os arquivos JSON estão armazenados.

        Args:
            diretorio_base: String representando o caminho do diretório onde os arquivos JSON estão local
        """
        
        self.__diretorio_base = Path(diretorio_base) # Converte a string para um objeto Path para ajustar com o sistema operacional
        self.curso_selecionado = curso_selecionado
        self.quantidade_gerada = quantidade_gerada
        
        self.__verificar_diretorio_existe()
        
        
    def extrair_dados(self) -> List[DadosCenarioDTO]:
        """
        Abre o arquivo, valida a estrutura básica e devolve os dados limpos.
        """
        
        #Tenta abrir e decodificar o JSON
        # Aqui é usado o json.load para extrair todos dados entre o arquivo, como a pespectiva é o numero de relatorio não venha ultrapassar mais 1000,
        # esse metodo, não gerar efeitos significativos de performance, e é mais simples de implementar, do que ler linha a linha, ou usar um parser de JSON mais complexo.
        # Caso isso mude no fultutro, ou seja necessário otimizar a leitura, podemos considerar outras abordagens, como usar um parser de JSON mais eficiente, ou ler o arquivo em blocos.
        try:
            with open(self.caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                dados_brutos = json.load(arquivo)
                
        except json.JSONDecodeError as erro_sintaxe:
            raise ValueError(f"[Erro - Json] O arquivo JSON está corrompido ou mal formatado. Detalhes: {erro_sintaxe}")

        self.__validar_esquema_basico(dados_brutos)
        
        return dados_brutos # Por enquanto retorna os dicionários validados
        
    def __verificar_diretorio_existe(self):
        """
        Verifica se o diretório base existe.
        """
        
        if not self.__diretorio_base.exists():
            raise FileNotFoundError(f"[Erro - Caminho Json] : O diretório {self.__diretorio_base} não foi encontrado.")
        
        if not self.__diretorio_base.is_file():
            raise FileNotFoundError(f"[Erro - Caminho Json] : O caminho {self.__diretorio_base} não é um arquivo JSON.")
        
        if not self.__diretorio_base.is_dir():
            raise NotADirectoryError(f"[Erro - Caminho Json] : O caminho {self.__diretorio_base} não é um diretório.")
        
        if not any(self.__diretorio_base.glob('*.json')):
            raise FileNotFoundError(f"[Erro - Caminho Json] : Nenhum arquivo JSON encontrado no diretório {self.__diretorio_base}.")

    def __validar_esquema_basico(self, dados: Any):
        """
        A 'Alfândega' dos dados. Verifica se a estrutura é o que o sistema espera.
        """
        if not isinstance(dados, list):
            raise TypeError("[Erro - Estrutura JSON] O arquivo JSON deve conter uma Lista [] de cenários na raiz.")
            
        if len(dados) == 0:
            raise ValueError("[Erro - Estrutura JSON] O arquivo JSON foi lido, mas está vazio (sem cenários).")

        chaves_vitais = ["id_cenario", "titulo", "dificuldade"]
        
        for index, cenario_dict in enumerate(dados):
            if not isinstance(cenario_dict, dict):
                raise TypeError(f"[Erro - Estrutura JSON] O item na posição {index} não é um cenário válido.")
                
            for chave in chaves_vitais:
                if chave not in cenario_dict:
                    raise KeyError(f"[Erro - Estrutura JSON] O cenário na posição {index} está sem a chave obrigatória '{chave}'.")