from typing import List, Dict, Any
from pathlib import Path
import json

import random

from ..dtos.dados_cenario import DadosCenarioDTO, DadosAnexoDTO

class RepositorioJSON:
    """
    Responsável por interagir com o sistema de arquivos do SO, localizar os 
    arquivos .json correspondentes ao curso escolhido e devolvê-los como DTO's para a Fábrica de Relatórios.
    """
    
    CURSOS_VALIDOS = [
        "DEFAULT",
        "T_QUIMICA",
        "T_INFORMATICA",
        "T_AGROPECUARIA",
        "T_ALIMENTOS",
        "T_MEIO_AMBIENTE",
        "T_ZOOTECNIA",
        "CT_ALIMENTOS",
        "E_COMPUTACAO",
    ]
    

    def __init__(self, diretorio_base: str, curso_selecionado: str, quantidade_gerada: int):
        """
        Inicializa o repositório com o caminho base onde os arquivos JSON estão armazenados.

        Args:
            diretorio_base: String representando o caminho do diretório onde os arquivos JSON estão local
        """
        
        self.__diretorio_base = Path(diretorio_base) # Converte a string para um objeto Path para ajustar com o sistema operacional
        self.__verificar_diretorio_existe()
        
        self.curso_selecionado = curso_selecionado
        self.__verificar_curso_valido()
        
        self.quantidade_gerada = quantidade_gerada
        self.__verificar_quantidade_gerada_valida()
        
    def extrair_dados(self) -> List[DadosCenarioDTO]:
        """
        Itera sobre todos os arquivos JSON do diretório base, valida seus esquemas,
        e extrai apenas os cenários compatíveis com o curso selecionado.
        """
        cenarios_compativeis_dto: List[DadosCenarioDTO] = []

        # O método glob('*.json') cria um iterador leve que busca todos os arquivos da pasta
        for caminho_arquivo in self.__diretorio_base.glob('*.json'):
            
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                    dados_brutos = json.load(arquivo)
                    
                if len(dados_brutos) == 0:
                    raise ValueError(f"[Erro - Json] O arquivo {caminho_arquivo.name} foi lido, mas está vazio (sem cenários).")
                    
            except json.JSONDecodeError as erro_sintaxe:
                raise ValueError(f"[Erro - Json] O arquivo {caminho_arquivo.name} está corrompido ou mal formatado. Detalhes: {erro_sintaxe}")

            self.__validar_esquema_basico(dados_brutos)
            
            for cenario_dict in dados_brutos:
                
                relatorio_do_cenario: Dict = cenario_dict["relatorio"]
                cursos_do_cenario: List[str] = relatorio_do_cenario["curso"]
                
                if self.curso_selecionado in cursos_do_cenario or self.curso_selecionado == "DEFAULT":
                    
                    anexos_dto: List[DadosAnexoDTO] = []
                    
                    for anexo_dict in cenario_dict["anexos"]:
                        
                        anexo_dto = DadosAnexoDTO(
                            id_anexo=anexo_dict["id_anexo"],
                            tipo=anexo_dict["tipo"],
                            caminho_arquivo=anexo_dict["caminho_arquivo"]
                        )
                        
                        anexos_dto.append(anexo_dto)
                        
                    dto = DadosCenarioDTO(
                        id_cenario=cenario_dict["id_cenario"],
                        titulo=cenario_dict["titulo"],
                        dificuldade=cenario_dict["dificuldade"],
                        atividade=relatorio_do_cenario["atividade"],
                        local=relatorio_do_cenario["local"],
                        texto_descricao=relatorio_do_cenario["texto_descricao"],
                        envolvidos=relatorio_do_cenario["envolvidos"],
                        cursos=relatorio_do_cenario["curso"],
                        riscos=relatorio_do_cenario["riscos"],
                        fatores_inseguranca=relatorio_do_cenario["fatores_inseguranca"],
                        decisao_otima=relatorio_do_cenario["decisao_administrativa"]["decisao_otima"],
                        decisao_boa=relatorio_do_cenario["decisao_administrativa"]["decisao_boa"],
                        anexos=anexos_dto
                    )
                    
                    cenarios_compativeis_dto.append(dto)
                    

        if not cenarios_compativeis_dto:
            raise ValueError(f"[Aviso] Nenhum cenário encontrado para o curso '{self.curso_selecionado}' nos arquivos lidos.")
        
        random.shuffle(cenarios_compativeis_dto)

        # Usa o 'min' para evitar erro se o jogo pedir numero de cenários maior do que o disponível.
        quantidade_real = min(self.quantidade_gerada, len(cenarios_compativeis_dto))
        cenarios_finais_dto = cenarios_compativeis_dto[:quantidade_real]

        return cenarios_finais_dto
        

    def __verificar_quantidade_gerada_valida(self):
        """
        Verifica se a quantidade de relatórios a serem gerados é um número inteiro positivo.
        """
        
        if self.quantidade_gerada <= 0:
            raise ValueError("[Erro - Valor Numérico] A quantidade de relatórios a serem gerados deve ser um número inteiro positivo.")

    def __verificar_curso_valido(self):
        """
        Verifica se o curso selecionado é válido.
        """
        
        if self.curso_selecionado not in self.CURSOS_VALIDOS:
            raise ValueError(f"[Erro - Curso] O curso '{self.curso_selecionado}' não é válido. Por favor, selecione um curso válido.")

    def __verificar_diretorio_existe(self):
        """
        Verifica se o diretório base existe.
        """
        
        if not self.__diretorio_base.exists():
            raise FileNotFoundError(f"[Erro - Caminho Json] : O diretório {self.__diretorio_base} não foi encontrado.")
        
        if not self.__diretorio_base.is_dir():
            raise NotADirectoryError(f"[Erro - Caminho Json] : O caminho {self.__diretorio_base} não é um diretório.")
        
        if not any(self.__diretorio_base.glob('*.json')):
            raise FileNotFoundError(f"[Erro - Caminho Json] : Nenhum arquivo JSON encontrado no diretório {self.__diretorio_base}.")

    def __validar_esquema_basico(self, dados: Any):
        """
        Verifica se a estrutura é o que o sistema espera.
        """
        if not isinstance(dados, list):
            raise TypeError("[Erro - Estrutura JSON] O arquivo JSON deve conter uma Lista [] de cenários na raiz.")
        
        # Futuramente, podemos implementar uma validação mais robusta, usando bibliotecas como jsonschema, para garantir que a estrutura do JSON esteja de acordo com um esquema pré-definido. 
        # Por enquanto, essa validação básica já ajuda a garantir que o formato geral do arquivo seja o esperado.
        chaves_raiz = ["id_cenario", 
                       "titulo", 
                       "dificuldade", 
                       "relatorio", 
                       "anexos"]
        
        chaves_relatorio = ["atividade", 
                            "local", 
                            "envolvidos", 
                            "texto_descricao", 
                            "riscos", 
                            "fatores_inseguranca", 
                            "decisao_administrativa", 
                            "curso"]
        
        chaves_decisao_administrativa = ["decisao_otima", "decisao_boa"]
        
        chaves_anexo = ["id_anexo", 
                        "tipo", 
                        "caminho_arquivo"]
        
        
        # Loop de validação para cada cenário, verificando se as chaves esperadas estão presentes e se os tipos de dados são corretos.
        for index, cenario_dict in enumerate(dados):
            if not isinstance(cenario_dict, dict):
                raise TypeError(f"[Erro - Estrutura JSON] O item na posição {index} da lista de cenários deve ser um dicionário.")
            
            for chave in chaves_raiz:
                if chave not in cenario_dict:
                    raise KeyError(f"[Erro - Estrutura JSON] O cenário na posição {index} está sem a chave raiz '{chave}'.")

            # Validação do Sub-bloco 'relatorio'
            relatorio_dict = cenario_dict["relatorio"]
            if not isinstance(relatorio_dict, dict):
                raise TypeError(f"[Erro - Estrutura JSON] O 'relatorio' do cenário {index} deve ser um objeto/dicionário.")
                
            for chave in chaves_relatorio:
                if chave not in relatorio_dict:
                    raise KeyError(f"[Erro - Estrutura JSON] O 'relatorio' do cenário {index} está sem a chave vital '{chave}'.")
                
            # Validação do Sub-bloco 'decisao_administrativa' dentro do 'relatorio'
            decisao_administrativa_dict = relatorio_dict["decisao_administrativa"]
            if not isinstance(decisao_administrativa_dict, dict):
                raise TypeError(f"[Erro - Estrutura JSON] O 'decisao_administrativa' do cenário {index} deve ser um objeto/dicionário.")
                
            for chave in chaves_decisao_administrativa:
                if chave not in decisao_administrativa_dict:
                    raise KeyError(f"[Erro - Estrutura JSON] O 'decisao_administrativa' do cenário {index} está sem a chave vital '{chave}'.")

            # Validação da Lógica de Anexos
            anexos_list = cenario_dict["anexos"]
            if not isinstance(anexos_list, list):
                raise TypeError(f"[Erro - Estrutura JSON] A chave 'anexos' do cenário {index} deve ser uma lista, mesmo que vazia [].")

            # Só inspeciona os anexos se a lista não estiver vazia
            if len(anexos_list) > 0:
                for i_anexo, anexo_dict in enumerate(anexos_list):
                    if not isinstance(anexo_dict, dict):
                        raise TypeError(f"[Erro - Estrutura JSON] O anexo {i_anexo} do cenário {index} não é um objeto válido.")
                        
                    for chave in chaves_anexo:
                        if chave not in anexo_dict:
                            raise KeyError(f"[Erro - Estrutura JSON] O anexo {i_anexo} (cenário {index}) está sem a chave vital '{chave}'.")
            
            