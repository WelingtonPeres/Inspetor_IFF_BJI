import logging
from typing import List, Dict, Any
from pathlib import Path
import json

import random
from jsonschema import ValidationError, validate

from ..dtos.dados_cenario import DadosCenarioDTO, DadosAnexoDTO

logger = logging.getLogger(__name__)

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

    JSON_SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "required": [
                "id_cenario",
                "titulo",
                "dificuldade",
                "relatorio",
                "anexos"
            ],
            "additionalProperties": False,
            "properties": {
                "id_cenario": {"type": "integer"},
                "titulo": {"type": "string"},
                "dificuldade": {"type": "integer", "minimum": 1, "maximum": 5},
                "relatorio": {
                    "type": "object",
                    "required": [
                        "atividade",
                        "local",
                        "envolvidos",
                        "texto_descricao",
                        "riscos",
                        "fatores_inseguranca",
                        "decisao_administrativa",
                        "curso"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "atividade": {"type": "string"},
                        "local": {"type": "string"},
                        "envolvidos": {
                            "type": "array",
                            "minItems": 1,
                            "items": {"type": "string"}
                        },
                        "texto_descricao": {"type": "string"},
                        "riscos": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "string",
                                "enum": ["FISICO", "QUIMICO", "BIOLOGICO", "ERGONOMICO", "ACIDENTE"]
                            }
                        },
                        "fatores_inseguranca": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "string",
                                "enum": ["ATO_INSEGURO", "CONDICAO_INSEGURA"]
                            }
                        },
                        "decisao_administrativa": {
                            "type": "object",
                            "required": ["decisao_otima", "decisao_boa"],
                            "additionalProperties": False,
                            "properties": {
                                "decisao_otima": {
                                    "type": "string",
                                    "enum": ["ADVERTIR", "INTERDITAR", "IGNORAR"]
                                },
                                "decisao_boa": {
                                    "type": "string",
                                    "enum": ["ADVERTIR", "INTERDITAR", "IGNORAR"]
                                }
                            }
                        },
                        "curso": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "string",
                                "enum": [
                                    "DEFAULT",
                                    "T_QUIMICA",
                                    "T_INFORMATICA",
                                    "T_AGROPECUARIA",
                                    "T_ALIMENTOS",
                                    "T_MEIO_AMBIENTE",
                                    "T_ZOOTECNIA",
                                    "CT_ALIMENTOS",
                                    "E_COMPUTACAO"
                                ]
                            }
                        }
                    }
                },
                "anexos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id_anexo", "tipo", "caminho_arquivo"],
                        "additionalProperties": False,
                        "properties": {
                            "id_anexo": {"type": "integer"},
                            "tipo": {"type": "string", "enum": ["IMAGEM", "VIDEO", "AUDIO"]},
                            "caminho_arquivo": {"type": "string"}
                        }
                    }
                }
            }
        }
    }

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

                self.__validar_esquema_basico(dados_brutos)

            except json.JSONDecodeError as erro_sintaxe:
                raise ValueError(f"[Erro - Json] O arquivo {caminho_arquivo.name} está corrompido ou mal formatado. Detalhes: {erro_sintaxe}")
            except ValidationError as erro_validacao:
                self.__traduzir_erro_validacao(caminho_arquivo.name, erro_validacao)
            
            for cenario_dict in dados_brutos:
                
                try:
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
                            curso=relatorio_do_cenario["curso"],
                            riscos=relatorio_do_cenario["riscos"],
                            fatores_inseguranca=relatorio_do_cenario["fatores_inseguranca"],
                            decisao_otima=relatorio_do_cenario["decisao_administrativa"]["decisao_otima"],
                            decisao_boa=relatorio_do_cenario["decisao_administrativa"]["decisao_boa"],
                            anexos=anexos_dto
                        )
                        
                        cenarios_compativeis_dto.append(dto)
                except KeyError:
                    logger.warning("Cenário com chave ausente no arquivo %s. Ignorando", caminho_arquivo.name)
                    continue
                    

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

        validate(instance=dados, schema=self.JSON_SCHEMA)
        return

    def __traduzir_erro_validacao(self, nome_arquivo: str, erro_validacao: ValidationError):
        """
        Traduz erros de schema para as exceções que o código chamador espera.
        """
        mensagem = (
            f"[Erro - Esquema JSON] O arquivo {nome_arquivo} não está conforme o esquema. "
            f"Detalhes: {erro_validacao.message}"
        )

        if erro_validacao.validator == "required":
            raise KeyError(mensagem)

        if erro_validacao.validator == "type":
            if "anexos" in list(erro_validacao.absolute_path):
                raise TypeError(
                    f"[Erro - Esquema JSON] O arquivo {nome_arquivo} não está conforme o esquema. "
                    f"Detalhes: a chave 'anexos' deve ser uma lista."
                )
            raise TypeError(mensagem)

        if erro_validacao.validator == "additionalProperties":
            raise KeyError(mensagem)

        raise ValueError(mensagem)
            
            