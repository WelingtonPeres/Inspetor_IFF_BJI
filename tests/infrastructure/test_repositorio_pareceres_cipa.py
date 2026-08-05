"""
Testes do RepositorioDePareceresCIPA.

Cobre carga de JSON, cache lazy, fallback para DEFAULT, geracao de numero
e tratamento de erros (ficheiro ausente, JSON corrompido, estrutura invalida).
"""

import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from core.dtos.parecer_cipa import ParecerCIPA
from infrastructure.repository.repositorio_pareceres_cipa import (
    RepositorioDePareceresCIPA,
    ParecerCIPAIndisponivelError,
)


@pytest.fixture
def json_valido(tmp_path: Path) -> Path:
    """Cria um JSON valido com 3 cursos + DEFAULT em tmp_path."""
    caminho = tmp_path / "pareceres.json"
    dados = {
        "DEFAULT": ["parecer default A", "parecer default B"],
        "T_INFORMATICA": ["parecer info A", "parecer info B"],
        "T_QUIMICA": ["parecer quim A"],
    }
    caminho.write_text(json.dumps(dados), encoding="utf-8")
    return caminho


@pytest.fixture
def json_vazio(tmp_path: Path) -> Path:
    """JSON com apenas DEFAULT disponivel."""
    caminho = tmp_path / "pareceres_vazio.json"
    caminho.write_text(json.dumps({"DEFAULT": ["unico default"]}), encoding="utf-8")
    return caminho


@pytest.fixture
def json_sem_default(tmp_path: Path) -> Path:
    """JSON sem DEFAULT (cenario problematico)."""
    caminho = tmp_path / "pareceres_sem_default.json"
    caminho.write_text(json.dumps({"T_INFORMATICA": ["x"]}), encoding="utf-8")
    return caminho


@pytest.fixture
def json_invalido(tmp_path: Path) -> Path:
    """JSON com sintaxe corrompida."""
    caminho = tmp_path / "pareceres_invalido.json"
    caminho.write_text("{ isto nao e json valido", encoding="utf-8")
    return caminho


class TestCarregamento:
    """Testes da carga inicial do JSON."""

    def test_carrega_ficheiro_existente(self, json_valido: Path):
        """Repositorio carrega o JSON do caminho injetado."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)

        # Act
        cursos = repo.cursos_disponiveis()

        # Assert
        assert "T_INFORMATICA" in cursos
        assert "DEFAULT" in cursos
        assert "T_QUIMICA" in cursos

    def test_caminho_default_aponta_para_ficheiro_real(self):
        """Sem injecao de caminho, usa o default do projecto (JSON real existe)."""
        # Arrange & Act
        repo = RepositorioDePareceresCIPA()
        cursos = repo.cursos_disponiveis()

        # Assert
        assert "DEFAULT" in cursos
        assert "T_QUIMICA" in cursos
        assert "T_INFORMATICA" in cursos

    def test_ficheiro_ausente_nao_levanta_excepcao(self, tmp_path: Path):
        """Ficheiro inexistente nao quebra o construtor; cursos ficam vazios."""
        # Arrange
        caminho_inexistente = tmp_path / "nao_existe.json"

        # Act
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=caminho_inexistente)

        # Assert
        assert repo.cursos_disponiveis() == []

    def test_json_corrompido_nao_levanta_excepcao(self, json_invalido: Path):
        """JSON com sintaxe invalida e tratado; cursos vazios."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_invalido)

        # Act
        cursos = repo.cursos_disponiveis()

        # Assert
        assert cursos == []

    def test_json_com_raiz_nao_dict_nao_levanta_excepcao(self, tmp_path: Path):
        """JSON cuja raiz e uma lista (nao dict) e tratado; cursos vazios."""
        # Arrange
        caminho = tmp_path / "raiz_lista.json"
        caminho.write_text(json.dumps(["item1", "item2"]), encoding="utf-8")

        # Act
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=caminho)

        # Assert
        assert repo.cursos_disponiveis() == []


class TestObterParecer:
    """Testes de obter_parecer_para_curso."""

    def test_devolve_parecer_para_curso_valido(self, json_valido: Path):
        """Curso existente devolve ParecerCIPA com texto desse curso."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)

        # Act
        parecer = repo.obter_parecer_para_curso("T_INFORMATICA")

        # Assert
        assert isinstance(parecer, ParecerCIPA)
        assert parecer.texto in ["parecer info A", "parecer info B"]
        assert parecer.referencia == "Conduta do Inspetor"

    def test_fallback_para_default_quando_curso_inexistente(self, json_valido: Path):
        """Curso nao existente devolve parecer do DEFAULT."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)

        # Act
        parecer = repo.obter_parecer_para_curso("CURSO_INEXISTENTE")

        # Assert
        assert parecer.texto in ["parecer default A", "parecer default B"]

    def test_fallback_quando_ficheiro_vazio(self, json_vazio: Path):
        """Curso de ficheiro sem curso proprio cai em DEFAULT."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_vazio)

        # Act
        parecer = repo.obter_parecer_para_curso("T_INFORMATICA")

        # Assert
        assert parecer.texto == "unico default"

    def test_levanta_erro_se_default_tambem_indisponivel(self, json_sem_default: Path):
        """Se nem DEFAULT existir, levanta ParecerCIPAIndisponivelError."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_sem_default)

        # Act & Assert
        with pytest.raises(ParecerCIPAIndisponivelError, match="\\[Erro -"):
            repo.obter_parecer_para_curso("CURSO_INEXISTENTE")

    def test_levanta_erro_se_default_indisponivel_e_curso_inexistente(
        self, json_sem_default: Path
    ):
        """Curso inexistente + sem DEFAULT tambem levanta erro."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_sem_default)

        # Act & Assert
        with pytest.raises(ParecerCIPAIndisponivelError, match="\\[Erro -"):
            repo.obter_parecer_para_curso("QUALQUER_CURSO")

    def test_numero_segue_formato_nnn_aaaa(self, json_valido: Path):
        """Numero gerado segue o formato NNN/AAAA com ano corrente."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)
        ano_corrente = datetime.now().year

        # Act
        parecer = repo.obter_parecer_para_curso("T_INFORMATICA")

        # Assert
        partes = parecer.numero.split("/")
        assert len(partes) == 2
        assert len(partes[0]) == 3
        assert partes[0].isdigit()
        assert partes[1] == str(ano_corrente)

    def test_curso_vazio_faz_fallback_para_default(self, json_valido: Path):
        """String vazia como curso faz fallback para DEFAULT."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)

        # Act
        parecer = repo.obter_parecer_para_curso("")

        # Assert
        assert parecer.texto in ["parecer default A", "parecer default B"]

    def test_parecer_devolvido_respeita_invariantes_dto(self, json_valido: Path):
        """Parecer devolvido passa pelas validacoes do DTO (formato, nao vazio)."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)

        # Act
        parecer = repo.obter_parecer_para_curso("T_INFORMATICA")

        # Assert
        assert parecer.referencia.strip() != ""
        assert parecer.texto.strip() != ""
        partes = parecer.numero.split("/")
        assert len(partes[0]) == 3
        assert len(partes[1]) == 4
        assert partes[0].isdigit()
        assert partes[1].isdigit()


class TestCache:
    """Testes do cache lazy de carregamento."""

    def test_segunda_chamada_nao_recarrega_ficheiro(self, json_valido: Path):
        """Cache lazy: segunda consulta nao reabre o ficheiro."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)
        # Primeira chamada para popular o cache
        repo.obter_parecer_para_curso("T_INFORMATICA")

        # Act & Assert
        with patch(
            "infrastructure.repository.repositorio_pareceres_cipa.open",
            side_effect=AssertionError("Nao devia reabrir o ficheiro"),
        ):
            # Se o open for chamado novamente, levanta AssertionError
            parecer = repo.obter_parecer_para_curso("T_QUIMICA")

        # Confirmacao adicional: o parecer e' valido
        assert parecer.texto == "parecer quim A"

    def test_dois_repositorios_instanciados_separadamente(self, json_valido: Path):
        """Cada instancia tem o seu proprio cache."""
        # Arrange
        repo1 = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)
        repo2 = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)

        # Act
        texto_repo1 = repo1.obter_parecer_para_curso("T_INFORMATICA").texto

        # Assert
        assert repo1 is not repo2
        assert texto_repo1 in ["parecer info A", "parecer info B"]
        # repo2 ainda funciona independentemente
        assert repo2.cursos_disponiveis() == ["DEFAULT", "T_INFORMATICA", "T_QUIMICA"]


class TestRandomizacao:
    """Testes da escolha aleatoria do texto."""

    def test_curso_com_multiplos_textos_retorna_um_do_conjunto(
        self, json_valido: Path
    ):
        """
        Com varios textos por curso, o retorno esta' sempre no conjunto valido.
        """
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)
        validos = {"parecer info A", "parecer info B"}

        # Act
        textos = {repo.obter_parecer_para_curso("T_INFORMATICA").texto for _ in range(20)}

        # Assert
        assert len(textos) >= 1
        assert textos.issubset(validos)

    def test_curso_com_um_unico_texto_sempre_o_mesmo(self, json_valido: Path):
        """Curso com 1 texto devolve sempre o mesmo."""
        # Arrange
        repo = RepositorioDePareceresCIPA(caminho_ficheiro=json_valido)

        # Act
        textos = {repo.obter_parecer_para_curso("T_QUIMICA").texto for _ in range(10)}

        # Assert
        assert textos == {"parecer quim A"}
