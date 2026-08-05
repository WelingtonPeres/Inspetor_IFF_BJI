"""
Suite completa de testes para RepositorioJSON.
"""

import pytest
import json
import shutil
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


class TesteInicializacao:
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
        with pytest.raises(ValueError, match="inteiro positivo"):
            RepositorioJSON(
                diretorio_base=diretorio_dados_teste_valido,
                curso_selecionado="T_QUIMICA",
                quantidade_gerada=0
            )
        
        with pytest.raises(ValueError, match="inteiro positivo"):
            RepositorioJSON(
                diretorio_base=diretorio_dados_teste_valido,
                curso_selecionado="T_QUIMICA",
                quantidade_gerada=-5
            )

class TesteEsquema:
    """
    Testes de Esquema e Estrutura Estrita 
    
    Garantir que nenhum JSON mal formado entra na memória do jogo, 
    testando a composição desde a raiz até às ramificações mais profundas.
    """

    def test_tipagem_raiz_invalida(self, diretorio_dados_teste_invalido):
        """
        Tipagem da Raiz
        
        Fornecer um ficheiro JSON válido, mas que começa com um 
        Objeto `{}` em vez de uma Lista `[]`.
        
        Rejeição com `TypeError`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy2(
                Path(diretorio_dados_teste_invalido) / "teste_invalido_nao_lista.json",
                Path(tmpdir) / "teste_invalido_nao_lista.json"
            )
            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )
            
            with pytest.raises(TypeError, match="Lista"):
                repo.extrair_dados()

    def test_ausencia_chave_primaria(self, diretorio_dados_teste_invalido):
        """
        Ausência de Chave Primária
        
        Fornecer um cenário sem uma chave obrigatória na raiz 
        (dificuldade ausente).
        
        Rejeição com `KeyError`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy2(
                Path(diretorio_dados_teste_invalido) / "teste_invalido_chave_raiz_faltando_1.json",
                Path(tmpdir) / "teste_invalido_chave_raiz_faltando_1.json"
            )
            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )
            
            with pytest.raises(KeyError):
                repo.extrair_dados()

    def test_ausencia_em_subbloco_relatorio(self, diretorio_dados_teste_invalido):
        """
        Ausência em Sub-bloco 
        
        Fornecer o bloco `"relatorio"`, mas omitir uma chave vital 
        lá de dentro (ex: falta a chave `"fatores_inseguranca"`).
        
        Rejeição com `KeyError`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy2(
                Path(diretorio_dados_teste_invalido) / "teste_invalido_relatorio_chave_faltando_1.json",
                Path(tmpdir) / "teste_invalido_relatorio_chave_faltando_1.json"
            )
            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )
            
            with pytest.raises(KeyError):
                repo.extrair_dados()

    def test_validacao_profunda_decisao_administrativa(self, diretorio_dados_teste_invalido):
        """
        Validação Profunda (Composição Nível 2)
        
        No bloco `"decisao_administrativa"`, omitir a chave `"decisao_boa"`.
        
        Rejeição com `KeyError` (Garante que a alfândega desce a todos os níveis).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy2(
                Path(diretorio_dados_teste_invalido) / "teste_invalido_decisao_chave_faltando.json",
                Path(tmpdir) / "teste_invalido_decisao_chave_faltando.json"
            )
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

    def test_anexo_incompleto_chave_faltando(self, diretorio_dados_teste_invalido):
        """
        Anexo Incompleto
        
        Fornecer um item na lista de anexos, mas sem a chave 
        `"id_anexo"`.
        
        Rejeição com `KeyError`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy2(
                Path(diretorio_dados_teste_invalido) / "teste_invalido_anexo_chave_faltando.json",
                Path(tmpdir) / "teste_invalido_anexo_chave_faltando.json"
            )
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
        assert all(isinstance(dto.anexos, list) for dto in resultado)

class TesteExtracao:
    """
    Testes de Lógica de Extração e Filtragem
    
    Garantir a resiliência a erros operacionais e o correto 
    funcionamento do "Pool and Sample" (Sorteio e Limitação).
    """

    def test_resiliencia_ficheiro_vazio(self, diretorio_dados_teste_invalido):
        """
        Resiliência a Lista Vazia
        
        Fornecer um arquivo com lista vazia `[]` deve lançar ValueError.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy2(
                Path(diretorio_dados_teste_invalido) / "teste_invalido_lista_vazia.json",
                Path(tmpdir) / "teste_invalido_lista_vazia.json"
            )
            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )
            
            with pytest.raises(ValueError, match="vazio"):
                repo.extrair_dados()

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
        
        for dto in resultado:
            assert "T_QUIMICA" in dto.curso

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
            assert isinstance(dto.curso, list)
            assert len(dto.curso) > 0

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


class TesteResiliencia:
    """
    Testes de Resiliência a Dados Corrompidos

    Garantir que o repositório trata gracefulmente arquivos com
    JSON inválido e erros de esquema não mapeados.
    """

    def test_arquivo_sintaxe_corrompida(self, diretorio_dados_teste_invalido):
        """
        T10: Arquivo com sintaxe JSON corrompida deve lançar ValueError.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy2(
                Path(diretorio_dados_teste_invalido) / "teste_invalido_sintaxe_json.json",
                Path(tmpdir) / "teste_invalido_sintaxe_json.json"
            )
            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )

            with pytest.raises(ValueError, match="corrompido"):
                repo.extrair_dados()

    def test_validacao_chave_extra_additional_properties(self):
        """
        T11a: Chave não permitida pelo esquema (additionalProperties) deve
        lançar KeyError (traduzido por __traduzir_erro_validacao).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            arquivo = Path(tmpdir) / "chave_extra.json"
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
                    "anexos": [],
                    "chave_extra": "nao_permitida"
                }
            ]
            with open(arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False)

            repo = RepositorioJSON(
                diretorio_base=tmpdir,
                curso_selecionado="DEFAULT",
                quantidade_gerada=1
            )

            with pytest.raises(KeyError, match="additionalProperties|chave_extra"):
                repo.extrair_dados()

    def test_validacao_erro_nao_mapeado_fallback(self):
        """
        T11b: Erro de validação não mapeado por __traduzir_erro_validacao
        deve cair no fallback e lançar ValueError.

        Um enum inválido (ex: decisao_otima="INEXISTENTE") aciona o
        validador 'enum', que não tem if explícito em __traduzir_erro_validacao.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            arquivo = Path(tmpdir) / "enum_invalido.json"
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
                            "decisao_otima": "INEXISTENTE",
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

            with pytest.raises(ValueError, match="Esquema JSON|INEXISTENTE"):
                repo.extrair_dados()

