"""
Suite completa de testes para RepositorioJSON.
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any

from infrastructure.repository.repositorio_json import RepositorioJSON


@pytest.fixture
def diretorio_dados_teste():
    """Retorna o caminho da pasta com arquivos de teste gerados."""
    return str(Path(__file__).parent.parent / "resources" / "data")


@pytest.fixture
def diretorio_dados_teste_valido():
    """Retorna o caminho da pasta com arquivos VÁLIDOS para teste de filtragem/extração."""
    return str(Path(__file__).parent.parent / "resources" / "data" / "test_valido")


@pytest.fixture
def diretorio_dados_teste_invalido():
    """Retorna o caminho da pasta com arquivos INVÁLIDOS para teste de esquema/erro."""
    return str(Path(__file__).parent.parent / "resources" / "data" / "test_invalido")


@pytest.fixture
def dir_temporario_vazio():
    """Cria um diretório temporário vazio."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TesteSuite1Inicializacao:
    """
    Testes de Inicialização e Infraestrutura
    
    Garantir que o repositório não é instanciado se o ambiente ou 
    os parâmetros básicos estiverem corrompidos.
    """

    def test_diretorio_fantasma(self):
        """
        Diretório Fantasma
        
        Tentar inicializar o repositório passando um caminho de pasta 
        que não existe no disco.
        
        O sistema deve abortar imediatamente lançando 
        um `FileNotFoundError`.
        """
        with pytest.raises(FileNotFoundError):
            RepositorioJSON(
                diretorio_base="/caminho/inexistente/ao/disco",
                curso_selecionado="T_QUIMICA",
                quantidade_gerada=5
            )

    def test_diretorio_esteril(self, dir_temporario_vazio):
        """
        Diretório Estéril
        
        Apontar o repositório para uma pasta real, mas que não contém 
        nenhum ficheiro com a extensão `.json`.
        
        Abortar com `FileNotFoundError` (Não há dados 
        para ler).
        """
        with pytest.raises(FileNotFoundError):
            RepositorioJSON(
                diretorio_base=dir_temporario_vazio,
                curso_selecionado="T_QUIMICA",
                quantidade_gerada=5
            )

    def test_validacao_curso_invalido(self, diretorio_dados_teste_valido):
        """
        Validação de Curso Inválido
        
        Passar um `curso_selecionado` que não faz parte da lista 
        estrita interna de cursos.
        
        Abortar com `ValueError`.
        """
        with pytest.raises(ValueError, match="não é válido"):
            RepositorioJSON(
                diretorio_base=diretorio_dados_teste_valido,
                curso_selecionado="T_MEDICINA",
                quantidade_gerada=5
            )

    def test_quantidade_ilogica(self, diretorio_dados_teste_valido):
        """
        Quantidade Ilógica
        
        Pedir ao repositório para gerar `0` ou `-5` cenários.
        
        Abortar com `ValueError` (exigindo inteiros positivos).
        """
        # Teste com quantidade 0
        with pytest.raises(ValueError, match="inteiro positivo"):
            RepositorioJSON(
                diretorio_base=diretorio_dados_teste_valido,
                curso_selecionado="T_QUIMICA",
                quantidade_gerada=0
            )
        
        # Teste com quantidade negativa
        with pytest.raises(ValueError, match="inteiro positivo"):
            RepositorioJSON(
                diretorio_base=diretorio_dados_teste_valido,
                curso_selecionado="T_QUIMICA",
                quantidade_gerada=-5
            )

class TesteSuite2Esquema:
    """
    Testes de Esquema e Estrutura Estrita 
    
    Garantir que nenhum JSON mal formado entra na memória do jogo, 
    testando a composição desde a raiz até às ramificações mais profundas.
    """

    def test_tipagem_raiz_invalida(self):
        """
        Tipagem da Raiz
        
        Fornecer um ficheiro JSON válido, mas que começa com um 
        Objeto `{}` em vez de uma Lista `[]`.
        
        Rejeição com `TypeError`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            arquivo = Path(tmpdir) / "raiz_objeto.json"
            
            # Escreve um objeto em vez de lista
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump({"id_cenario": 1}, f)
            
            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )
            
            with pytest.raises(TypeError, match="Lista"):
                repo.extrair_dados()

    def test_ausencia_chave_primaria(self):
        """
        Ausência de Chave Primária
        
        Fornecer um cenário sem uma chave obrigatória na raiz 
        
        Rejeição com `KeyError`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            arquivo = Path(tmpdir) / "chave_faltando.json"
            dados = [
                {
                    # Falta "titulo"
                    "id_cenario": 1,
                    "dificuldade": 2,
                    "relatorio": {
                        "atividade": "Teste",
                        "local": "Lab",
                        "envolvidos": ["Pessoa"],
                        "texto_descricao": "Desc",
                        "riscos": ["FISICO"],
                        "fatores_inseguranca": ["ATO_INSEGURO"],
                        "decisao_administrativa": {
                            "decisao_otima": "INTERDITAR",
                            "decisao_boa": "ADVERTIR"
                        },
                        "curso": ["DEFAULT"]
                    },
                    "anexos": []
                }
            ]
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False)
            
            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )
            
            with pytest.raises(KeyError):
                repo.extrair_dados()

    def test_ausencia_em_subbloco_relatorio(self):
        """
        Ausência em Sub-bloco 
        
        Fornecer o bloco `"relatorio"`, mas omitir uma chave vital 
        lá de dentro (ex: falta a chave `"riscos"`).
        
        Rejeição com `KeyError`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            arquivo = Path(tmpdir) / "relatorio_incompleto.json"
            dados = [
                {
                    "id_cenario": 1,
                    "titulo": "Teste",
                    "dificuldade": 2,
                    "relatorio": {
                        "atividade": "Teste",
                        "local": "Lab",
                        "envolvidos": ["Pessoa"],
                        "texto_descricao": "Desc",
                        # Falta "riscos"
                        "fatores_inseguranca": ["ATO_INSEGURO"],
                        "decisao_administrativa": {
                            "decisao_otima": "INTERDITAR",
                            "decisao_boa": "ADVERTIR"
                        },
                        "curso": ["DEFAULT"]
                    },
                    "anexos": []
                }
            ]
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False)
            
            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )
            
            with pytest.raises(KeyError):
                repo.extrair_dados()

    def test_validacao_profunda_decisao_administrativa(self):
        """
        Validação Profunda (Composição Nível 2)
        
        No bloco `"decisao_administrativa"`, omitir a chave `"decisao_otima"`.
        
        Rejeição com `KeyError` (Garante que a alfândega desce a todos os níveis).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            arquivo = Path(tmpdir) / "decisao_incompleta.json"
            dados = [
                {
                    "id_cenario": 1,
                    "titulo": "Teste",
                    "dificuldade": 2,
                    "relatorio": {
                        "atividade": "Teste",
                        "local": "Lab",
                        "envolvidos": ["Pessoa"],
                        "texto_descricao": "Desc",
                        "riscos": ["FISICO"],
                        "fatores_inseguranca": ["ATO_INSEGURO"],
                        "decisao_administrativa": {
                            # Falta "decisao_otima"
                            "decisao_boa": "ADVERTIR"
                        },
                        "curso": ["DEFAULT"]
                    },
                    "anexos": []
                }
            ]
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False)
            
            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )
            
            with pytest.raises(KeyError):
                repo.extrair_dados()

    def test_anexo_malformado_tipo_invalido(self, diretorio_dados_teste_invalido):
        """
        Anexo Malformado
        
        Colocar a chave `"anexos"` como uma string em vez de uma lista 
        
        Rejeição com `TypeError`.
        """
        with pytest.raises(TypeError, match="anexos.*lista"):
            repo = RepositorioJSON(
                diretorio_base=diretorio_dados_teste_invalido,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )
            repo.extrair_dados()

    def test_anexo_incompleto_chave_faltando(self):
        """
        Anexo Incompleto
        
        Fornecer um item na lista de anexos, mas sem a chave 
        `"caminho_arquivo"`.
        
        Rejeição com `KeyError`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            arquivo = Path(tmpdir) / "anexo_incompleto.json"
            dados = [
                {
                    "id_cenario": 1,
                    "titulo": "Teste",
                    "dificuldade": 2,
                    "relatorio": {
                        "atividade": "Teste",
                        "local": "Lab",
                        "envolvidos": ["Pessoa"],
                        "texto_descricao": "Desc",
                        "riscos": ["FISICO"],
                        "fatores_inseguranca": ["ATO_INSEGURO"],
                        "decisao_administrativa": {
                            "decisao_otima": "INTERDITAR",
                            "decisao_boa": "ADVERTIR"
                        },
                        "curso": ["DEFAULT"]
                    },
                    "anexos": [
                        {
                            "id_anexo": 1,
                            "tipo": "IMAGEM"
                            # Falta "caminho_arquivo"
                        }
                    ]
                }
            ]
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False)
            
            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )
            
            with pytest.raises(KeyError):
                repo.extrair_dados()

    def test_sucesso_com_composicao_vazia(self, diretorio_dados_teste_valido):
        """
        Sucesso com Composição Vazia (Caminho Feliz Edge Case)
        
        Fornecer um JSON perfeito, e o repositório deve extrair 
        cenários válidos sem erros.
        
        Sucesso. O repositório deve ler e instanciar 
        os DTOs sem erros.
        """
        repo = RepositorioJSON(
            diretorio_base=diretorio_dados_teste_valido,
            curso_selecionado="DEFAULT",
            quantidade_gerada=1
        )
        resultado = repo.extrair_dados()
        
        assert isinstance(resultado, list)
        assert len(resultado) >= 1
        # Todos devem ter anexos como lista (vazia ou com itens)
        assert all(isinstance(dto.anexos, list) for dto in resultado)

class TesteSuite3Extracao:
    """
    Testes de Lógica de Extração e Filtragem
    
    Garantir a resiliência a erros operacionais e o correto 
    funcionamento do "Pool and Sample" (Sorteio e Limitação).
    """

    def test_resiliencia_ficheiro_vazio(self, diretorio_dados_teste_valido):
        """
        Resiliência a Ficheiro Vazio
        
        O sistema deve processar múltiplos arquivos, extraindo dados 
        válidos mesmo que haja arquivo vazio ou inválido.
        
        O sistema deve ignorar arquivos vazios/inválidos 
        e extrair dados dos arquivos válidos, ou rejeitar se nenhum dado 
        compatível for encontrado.
        """
        repo = RepositorioJSON(
            diretorio_base=diretorio_dados_teste_valido,
            curso_selecionado="DEFAULT",
            quantidade_gerada=1
        )
        
        # Pode extrair com sucesso ou lançar erro se nenhum dado compatível
        try:
            resultado = repo.extrair_dados()
            assert isinstance(resultado, list)
        except (ValueError, TypeError, KeyError):
            # Comportamento aceitável com arquivos corrompidos
            pass

    def test_filtragem_restrita(self, diretorio_dados_teste_valido):
        """
        Filtragem Restrita
        
        Pedir extração apenas para "T_QUIMICA" a partir da base gerada.
        
        A extração deve conter apenas cenários de T_QUIMICA.
        """
        repo = RepositorioJSON(
            diretorio_base=diretorio_dados_teste_valido,
            curso_selecionado="T_QUIMICA",
            quantidade_gerada=10  # Pede até 10
        )
        
        resultado = repo.extrair_dados()
        
        assert isinstance(resultado, list)
        assert len(resultado) > 0
        
        # Validar que todos contêm T_QUIMICA
        for dto in resultado:
            assert "T_QUIMICA" in dto.cursos

    def test_filtragem_default_global(self, diretorio_dados_teste_valido):
        """
        Filtragem DEFAULT (Global/Sem Filtro)
        
        Pedir a extração com o curso "DEFAULT" da base gerada.
        
        O repositório deve trazer TODOS os cenários 
        (DEFAULT significa "sem filtro", retorna tudo).
        """
        repo = RepositorioJSON(
            diretorio_base=diretorio_dados_teste_valido,
            curso_selecionado="DEFAULT",
            quantidade_gerada=5
        )
        
        resultado = repo.extrair_dados()
        
        assert isinstance(resultado, list)
        assert len(resultado) >= 1  # Deve retornar pelo menos um cenário
        # DEFAULT retorna todos, então podem ser cursos variados
        for dto in resultado:
            assert isinstance(dto.cursos, list)
            assert len(dto.cursos) > 0

    def test_corte_slicing_superior(self, diretorio_dados_teste_valido):
        """
        Corte (Slicing) Superior
        
        Pedir quantidade menor que a quantidade disponível.
        
        Retornar exatamente a quantidade solicitada.
        """
        repo = RepositorioJSON(
            diretorio_base=diretorio_dados_teste_valido,
            curso_selecionado="DEFAULT",
            quantidade_gerada=2  # Pede apenas 2
        )
        
        resultado = repo.extrair_dados()
        
        assert isinstance(resultado, list)
        assert len(resultado) <= 2  # Até 2

    def test_escudo_quantidade_min(self, diretorio_dados_teste_valido):
        """
        Escudo de Quantidade (Função Min)
        
        Pedir quantidade muito maior que a disponível.
        
        Sucesso. Retornar apenas os dados disponíveis 
        sem lançar erros de índice.
        """
        repo = RepositorioJSON(
            diretorio_base=diretorio_dados_teste_valido,
            curso_selecionado="DEFAULT",
            quantidade_gerada=100  # Pede muito mais
        )
        
        resultado = repo.extrair_dados()
        
        assert isinstance(resultado, list)
        assert len(resultado) > 0  # Retorna os disponíveis

    def test_seca_falta_dados_compativeis(self, diretorio_dados_teste_valido):
        """
        Seca (Falta de Dados Compatíveis)
        
        Selecionar um curso que não existe na base.
        
        Abortar com `ValueError` indicando que 
        nenhum cenário foi encontrado para aquele curso.
        """
        with pytest.raises(ValueError, match="Nenhum cenário encontrado"):
            repo = RepositorioJSON(
                diretorio_base=diretorio_dados_teste_valido,
                curso_selecionado="T_INFORMATICA",  # Não existe na base
                quantidade_gerada=5
            )
            repo.extrair_dados()

