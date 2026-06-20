"""
Suite completa de testes para o GerenciadorDeTurno.
"""

import pytest
from unittest.mock import patch, MagicMock

from config.constants import DIRETORIO_BASE, QUANTIDADE_GERACAO
from application.controllers.gerenciador_de_turno import GerenciadorDeTurno
from core.model.relatorio import Relatorio
from core.model.folha_de_gabarito import FolhaDeGabarito
from core.model.folha_de_resposta import FolhaDeResposta


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def relatorio_fake():
    """Relatório mínimo e válido para uso em mocks."""
    return Relatorio(
        id_cenario=1,
        titulo="Cenário Fake",
        atividade="Inspeção Simulada",
        local="Setor X",
        texto_descricao="Descrição simulada para testes.",
        envolvidos=["Agente"],
        cursos=["DEFAULT"],
        dificuldade=1,
        gabarito=FolhaDeGabarito(
            riscos=["FISICO"],
            fatores_inseguranca=["ATO_INSEGURO"],
            decisao_otima="ADVERTIR",
            decisao_boa="IGNORAR",
        ),
    )


@pytest.fixture
def relatorio_com_resposta(relatorio_fake):
    """Relatório com a resposta do jogador já anexada."""
    respostas = FolhaDeResposta(
        riscos=["FISICO"],
        fatores_inseguranca=["ATO_INSEGURO"],
        decisao_tomada="ADVERTIR",
        tempo_gasto_segundos=45,
    )
    relatorio_fake.anexar_resposta_jogador(respostas)
    return relatorio_fake


# =============================================================================
# Testes de Inicialização
# =============================================================================

class TestInicializacao:
    """
    Testes de Construção e Estado Inicial

    Garantir que o GerenciadorDeTurno é instanciado corretamente com
    perfil válido e que o estado inicial reflete um turno não iniciado.
    """

    def test_perfil_valido(self):
        """
        Perfil Válido

        Instanciar o gerenciador com um curso reconhecido não deve
        levantar nenhuma exceção e deve armazenar o perfil internamente.
        """
        g = GerenciadorDeTurno("DEFAULT")
        assert g._GerenciadorDeTurno__perfil_atual == "DEFAULT"

    def test_pilha_vazia_ao_criar(self):
        """
        Pilha Vazia na Criação

        Ao instanciar o gerenciador, a pilha de relatórios ainda não
        foi carregada — deve estar vazia.
        """
        g = GerenciadorDeTurno("DEFAULT")
        assert g.qnt_relatorios() == 0


# =============================================================================
# Testes de Inicialização do Turno (iniciar_turno)
# =============================================================================

class TestIniciarTurno:
    """
    Testes do Método iniciar_turno

    Validar o fluxo completo de preparação do turno: leitura dos dados,
    construção dos relatórios, cálculo da meta e tratamento de erros
    propagados do RepositorioJSON / FabricaDeRelatorios.
    """

    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao")
    @patch("application.controllers.gerenciador_de_turno.FabricaDeRelatorios")
    @patch("application.controllers.gerenciador_de_turno.RepositorioJSON")
    def test_iniciar_turno_com_sucesso_zera_pontuacao_e_preenche_pilha(
        self, mock_repo_cls, mock_fabrica_cls, mock_motor_cls, relatorio_fake
    ):
        """
        Fluxo Feliz Completo

        Mockar o Repositório para retornar um JSON simulado e a Fábrica
        para retornar uma lista com 3 relatórios válidos. O método deve
        retornar True, o v_max_turno preenchido, pilha com 3 e pontuação zerada.
        """
        mock_repo = MagicMock()
        mock_repo.extrair_dados.return_value = ["dto1", "dto2", "dto3"]
        mock_repo_cls.return_value = mock_repo

        mock_fabrica_cls.construir_pilha.return_value = [
            relatorio_fake, relatorio_fake, relatorio_fake
        ]

        mock_motor = MagicMock()
        mock_motor.calcular_meta_turno.return_value = 5000.0
        mock_motor_cls.return_value = mock_motor

        g = GerenciadorDeTurno("DEFAULT")
        resultado = g.iniciar_turno()

        assert resultado is True
        assert g.qnt_relatorios() == 3
        assert g._GerenciadorDeTurno__v_max_turno == 5000.0
        assert g._GerenciadorDeTurno__pontuacao_acumulada_turno == 0.0

        mock_repo_cls.assert_called_once_with(
            diretorio_base=DIRETORIO_BASE,
            curso_selecionado="DEFAULT",
            quantidade_gerada=QUANTIDADE_GERACAO,
        )
        mock_repo.extrair_dados.assert_called_once()
        mock_fabrica_cls.construir_pilha.assert_called_once_with(
            ["dto1", "dto2", "dto3"]
        )
        mock_motor.calcular_meta_turno.assert_called_once()

    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao")
    @patch("application.controllers.gerenciador_de_turno.FabricaDeRelatorios")
    @patch("application.controllers.gerenciador_de_turno.RepositorioJSON")
    def test_iniciar_turno_pilha_vazia_lanca_excecao(
        self, mock_repo_cls, mock_fabrica_cls, mock_motor_cls
    ):
        """
        Pilha Vazia Lança Exceção

        Mockar a Fábrica para retornar uma lista vazia. O sistema
        deve lançar RuntimeError com a tag [Erro - Turno].
        """
        mock_repo = MagicMock()
        mock_repo.extrair_dados.return_value = []
        mock_repo_cls.return_value = mock_repo

        mock_fabrica_cls.construir_pilha.return_value = []

        g = GerenciadorDeTurno("DEFAULT")

        with pytest.raises(RuntimeError, match="\\[Erro - Turno\\]"):
            g.iniciar_turno()

    @patch("application.controllers.gerenciador_de_turno.RepositorioJSON")
    def test_repositorio_sem_cenarios_compatíveis(self, mock_repo_cls):
        """
        Repositório sem Cenários Compatíveis

        Se o repositório não encontra cenários para o curso selecionado,
        ele levanta ValueError. O erro deve propagar para o chamador.
        """
        mock_repo = MagicMock()
        mock_repo.extrair_dados.side_effect = ValueError(
            "[Aviso] Nenhum cen\u00e1rio encontrado para o curso 'DEFAULT' nos arquivos lidos."
        )
        mock_repo_cls.return_value = mock_repo

        g = GerenciadorDeTurno("DEFAULT")

        with pytest.raises(ValueError, match="Nenhum cen\u00e1rio encontrado"):
            g.iniciar_turno()

    @patch("application.controllers.gerenciador_de_turno.RepositorioJSON")
    def test_diretorio_inexistente(self, mock_repo_cls):
        """
        Diretório Inexistente

        Se o diretório base configurado não existir em disco, o
        RepositorioJSON levanta FileNotFoundError na instanciação.
        """
        mock_repo_cls.side_effect = FileNotFoundError(
            "[Erro - Caminho Json] : O diret\u00f3rio C:\\fake\\path n\u00e3o foi encontrado."
        )

        g = GerenciadorDeTurno("DEFAULT")

        with pytest.raises(FileNotFoundError):
            g.iniciar_turno()

    @patch("application.controllers.gerenciador_de_turno.RepositorioJSON")
    def test_arquivo_json_corrompido(self, mock_repo_cls):
        """
        Arquivo JSON Corrompido

        Se um arquivo JSON está mal formatado o RepositorioJSON levanta
        ValueError. O erro deve propagar.
        """
        mock_repo = MagicMock()
        mock_repo.extrair_dados.side_effect = ValueError(
            "[Erro - Json] O arquivo dados.json est\u00e1 corrompido ou mal formatado."
        )
        mock_repo_cls.return_value = mock_repo

        g = GerenciadorDeTurno("DEFAULT")

        with pytest.raises(ValueError, match="corrompido"):
            g.iniciar_turno()


# =============================================================================
# Testes de Controle da Pilha
# =============================================================================

class TestManipulacaoDePilha:
    """
    Testes de Consulta e Consumo da Pilha de Relatórios

    Garantir que os métodos de acesso à pilha funcionam corretamente
    após o turno ser iniciado, via injeção direta no atributo privado.
    """

    def test_qnt_relatorios_retorna_tamanho_correto(self, relatorio_fake):
        """
        Quantidade de Relatórios

        Injetar manualmente 2 relatórios na pilha via atributo privado.
        qnt_relatorios() deve retornar 2.
        """
        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__pilha_relatorios = [relatorio_fake, relatorio_fake]

        assert g.qnt_relatorios() == 2

    def test_obter_relatorio_remove_elemento_da_pilha(self, relatorio_fake):
        """
        Remover Relatório da Pilha (Pop)

        Com a pilha contendo 2 relatórios, chamar obter_relatorio_da_pilha()
        deve retornar o último (LIFO) e reduzir a pilha para 1.
        """
        relatorio_b = Relatorio(
            id_cenario=2,
            titulo="Segundo Cenário",
            atividade="Inspeção Avançada",
            local="Setor Y",
            texto_descricao="Descrição do segundo cenário.",
            envolvidos=["Fake"],
            cursos=["DEFAULT"],
            dificuldade=2,
            gabarito=FolhaDeGabarito(
                riscos=["QUIMICO"],
                fatores_inseguranca=["CONDICAO_INSEGURA"],
                decisao_otima="INTERDITAR",
                decisao_boa="ADVERTIR",
            ),
        )

        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__pilha_relatorios = [relatorio_fake, relatorio_b]

        resultado = g.obter_relatorio_da_pilha()

        assert resultado.id_cenario == 2
        assert g.qnt_relatorios() == 1


# =============================================================================
# Testes de Avaliação e Pontuação
# =============================================================================

class TestAvaliacaoDeRespostas:
    """
    Testes do Método avaliar_respostas_jogador

    Validar a avaliação das respostas do jogador, incluindo a proteção
    contra relatório sem resposta anexada e o acúmulo correto da pontuação.
    """

    def test_avaliar_respostas_sem_folha_anexada_lanca_excecao(
        self, relatorio_fake
    ):
        """
        Relatório sem Resposta Lança Exceção

        Passar um Relatorio que ainda não teve a resposta anexada.
        O sistema deve lançar ValueError com a tag [Erro - Turno].
        """
        g = GerenciadorDeTurno("DEFAULT")

        with pytest.raises(
            ValueError, match="n\u00e3o possui resposta anexada"
        ):
            g.avaliar_respostas_jogador(relatorio_fake)

    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao.calcular_pontuacao_relatorio")
    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao.calcular_vmax_relatorio")
    @patch("application.controllers.gerenciador_de_turno.DiagnosticoDeResposta")
    def test_avaliar_respostas_jogador_acumula_pontuacao_com_sucesso(
        self,
        mock_diagnostico_cls,
        mock_calc_vmax,
        mock_calc_pontuacao,
        relatorio_com_resposta,
    ):
        """
        Acumula Pontuação com Sucesso

        Mockar o DiagnosticoDeResposta e o MotorDePontuacao para que a
        nota final retorne 1500.0. O método deve retornar 1500.0 e a
        pontuação acumulada deve ser incrementada com esse valor.
        """
        mock_diagnostico = MagicMock()
        mock_diagnostico.gerar_diagnostico_pontuacao.return_value = "diagnostico_fake"
        mock_diagnostico_cls.return_value = mock_diagnostico

        mock_calc_vmax.return_value = 5000.0
        mock_calc_pontuacao.return_value = 1500.0

        g = GerenciadorDeTurno("DEFAULT")
        pontuacao = g.avaliar_respostas_jogador(relatorio_com_resposta)

        assert pontuacao == 1500.0
        assert g._GerenciadorDeTurno__pontuacao_acumulada_turno == 1500.0
        mock_diagnostico.gerar_diagnostico_pontuacao.assert_called_once()


# =============================================================================
# Testes de Encerramento do Turno
# =============================================================================

class TestVerificarVitoria:
    """
    Testes do Método verificar_vitoria_do_turno

    Garantir que a vitória só pode ser verificada com a pilha vazia e
    que o resultado reflete corretamente o limiar de aprovação.
    """

    def test_verificar_vitoria_com_pilha_nao_vazia_lanca_excecao(
        self, relatorio_fake
    ):
        """
        Pilha Não Vazia Lança Exceção

        Chamar verificar_vitoria_do_turno() antes de esvaziar os
        relatórios deve lançar ValueError com a tag [Erro - Turno].
        """
        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__pilha_relatorios = [relatorio_fake]

        with pytest.raises(ValueError, match="\\[Erro - Turno\\]"):
            g.verificar_vitoria_do_turno()

    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao.conferir_condicao_vitoria")
    def test_verificar_vitoria_retorna_true_quando_atinge_meta(
        self, mock_conferir
    ):
        """
        Vitória quando Atinge a Meta

        Esvaziar a pilha, configurar pontuação acumulada alta e mockar
        o conferir_condicao_vitoria para True. Deve retornar True.
        """
        mock_conferir.return_value = True

        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__pilha_relatorios = []
        g._GerenciadorDeTurno__pontuacao_acumulada_turno = 8000.0
        g._GerenciadorDeTurno__v_max_turno = 10000.0

        assert g.verificar_vitoria_do_turno() is True
        mock_conferir.assert_called_once_with(8000.0, 10000.0)

    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao.conferir_condicao_vitoria")
    def test_verificar_vitoria_retorna_false_quando_falha_na_meta(
        self, mock_conferir
    ):
        """
        Derrota quando Falha na Meta

        Esvaziar a pilha, configurar pontuação acumulada baixa e mockar
        o conferir_condicao_vitoria para False. Deve retornar False.
        """
        mock_conferir.return_value = False

        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__pilha_relatorios = []
        g._GerenciadorDeTurno__pontuacao_acumulada_turno = 3000.0
        g._GerenciadorDeTurno__v_max_turno = 10000.0

        assert g.verificar_vitoria_do_turno() is False
        mock_conferir.assert_called_once_with(3000.0, 10000.0)
