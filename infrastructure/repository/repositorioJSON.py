from typing import List, Dict, Any

class RepositorioJSON:
    """
    Responsável por interagir com o sistema de arquivos do SO, localizar os 
    arquivos .json correspondentes ao curso escolhido e devolvê-los como 
    dicionários brutos para a aplicação.
    """

    def __init__(self, diretorio_base: str):
        """
        :param diretorio_base: Caminho raiz onde os arquivos .json estão armazenados 
                               (ex: "assets/niveis/").
        """
        # Encapsulamento do caminho base
        self.__diretorio_base: str = diretorio_base

    def buscar_dados_relatorios(self, perfil: List[str], quantidade: int) -> List[Dict]:
        """
        Vasculha a pasta do perfil selecionado, lê os arquivos .json e retorna
        os dados em formato de dicionário para serem consumidos pela Fábrica.

        :param perfil: Lista de strings com os nomes dos cursos selecionados na UI (ex: ["Mecanica"]).
        :param quantidade: Número inteiro limitando quantos relatórios carregar para o turno.
        :return: Lista contendo os dicionários extraídos dos arquivos JSON.
        """
        # TODO: Implementar lógica de abertura de arquivos (os.listdir, json.load)
        # TODO: Implementar tratamento de exceção (FileNotFoundError, JSONDecodeError)
        pass