"""
Suite completa de testes para o GerenciadorDeTurno.
"""

import pytest
from unittest.mock import patch, MagicMock

from config.constants import DIRETORIO_BASE, QUANTIDADE_GERACAO
from application.controllers.gerenciador_de_turno import GerenciadorDeTurno
from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from core.model.relatorio import Relatorio
from core.model.folha_de_gabarito import FolhaDeGabarito


@pytest.fixture
def diagnostico_fake():
    """DiagnosticoPontuacaoDTO fake para usar como retorno do mock."""
    return DiagnosticoPontuacaoDTO(
        qnt_riscos_marcados=1,
        qnt_riscos_gabarito=1,
        qnt_riscos_corretos_marcados=1,
        estado_ato=True,
        estado_condicao=True,
        status_decisao_jogador="OTIMA",
        tempo_resposta_segundos=45.0,
        pontuacao_final=1500.0,
    )


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
        foi carregada, deve estar vazia.
        """
        g = GerenciadorDeTurno("DEFAULT")
        assert g._GerenciadorDeTurno__pilha_relatorios == []

    def test_turno_nao_iniciado_bloqueia_qnt(self):
        """
        Turno não iniciado bloqueia qnt_relatorios.

        Chamar qnt_relatorios() antes de iniciar_turno() deve lançar
        exceção.
        """
        g = GerenciadorDeTurno("DEFAULT")
        with pytest.raises(Exception, match="Turno ainda n"):
            g.qnt_relatorios()

    def test_turno_nao_iniciado_bloqueia_obter(self):
        """obter_relatorio_da_pilha() antes de iniciar_turno() lança exceção."""
        g = GerenciadorDeTurno("DEFAULT")
        with pytest.raises(Exception, match="Turno ainda n"):
            g.obter_relatorio_da_pilha()

    def test_turno_nao_iniciado_bloqueia_avaliar(self):
        """avaliar_respostas_jogador() antes de iniciar_turno() lança exceção."""
        g = GerenciadorDeTurno("DEFAULT")
        with pytest.raises(Exception, match="Turno ainda n"):
            g.avaliar_respostas_jogador(["FISICO"], ["ATO_INSEGURO"], "ADVERTIR", 45)

    def test_turno_nao_iniciado_bloqueia_vitoria(self):
        """verificar_vitoria_do_turno() antes de iniciar_turno() lança exceção."""
        g = GerenciadorDeTurno("DEFAULT")
        with pytest.raises(Exception, match="Turno ainda n"):
            g.verificar_vitoria_do_turno()


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

    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao")
    @patch("application.controllers.gerenciador_de_turno.FabricaDeRelatorios")
    @patch("application.controllers.gerenciador_de_turno.RepositorioJSON")
    def test_iniciar_turno_duas_vezes_lanca_excecao(
        self, mock_repo_cls, mock_fabrica_cls, mock_motor_cls, relatorio_fake
    ):
        """
        Iniciar turno duas vezes lança exceção.

        Chamar iniciar_turno() duas vezes deve lançar Exception.
        """
        mock_repo = MagicMock()
        mock_repo.extrair_dados.return_value = ["dto"]
        mock_repo_cls.return_value = mock_repo

        mock_fabrica_cls.construir_pilha.return_value = [relatorio_fake]

        mock_motor = MagicMock()
        mock_motor.calcular_meta_turno.return_value = 1000.0
        mock_motor_cls.return_value = mock_motor

        g = GerenciadorDeTurno("DEFAULT")
        g.iniciar_turno()

        with pytest.raises(Exception, match="não pode ser iniciado"):
            g.iniciar_turno()


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
        g._GerenciadorDeTurno__turno_iniciado = True
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
        g._GerenciadorDeTurno__turno_iniciado = True
        g._GerenciadorDeTurno__pilha_relatorios = [relatorio_fake, relatorio_b]

        resultado = g.obter_relatorio_da_pilha()

        assert resultado.id_cenario == 2
        assert g.qnt_relatorios() == 1

    def test_obter_relatorio_sem_avaliar_anterior_bloqueia(self, relatorio_fake):
        """
        Obter relatório sem avaliar o anterior bloqueia.

        Após obter um relatório, uma segunda chamada sem avaliá-lo
        deve lançar RuntimeError.
        """
        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__turno_iniciado = True
        g._GerenciadorDeTurno__pilha_relatorios = [relatorio_fake, relatorio_fake]

        g.obter_relatorio_da_pilha()

        with pytest.raises(RuntimeError, match="ainda não foi avaliado"):
            g.obter_relatorio_da_pilha()


class TestAvaliacaoDeRespostas:
    """
    Testes do Método avaliar_respostas_jogador

    Validar a avaliação das respostas do jogador, incluindo a proteção
    contra relatório sem resposta anexada e o acúmulo correto da pontuação.
    """

    def test_avaliar_respostas_sem_obter_pilha_lanca_excecao(self):
        """
        Avaliar sem obter relatório da pilha lança exceção.

        Chamar avaliar_respostas_jogador() sem antes chamar
        obter_relatorio_da_pilha() deve lançar RuntimeError.
        """
        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__turno_iniciado = True

        with pytest.raises(RuntimeError, match="Nenhum relatório foi obtido"):
            g.avaliar_respostas_jogador(["FISICO"], ["ATO_INSEGURO"], "ADVERTIR", 45)

    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao.calcular_pontuacao_detalhada")
    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao.calcular_scores_por_item")
    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao.calcular_vmax_relatorio")
    @patch("application.controllers.gerenciador_de_turno.DiagnosticoDeResposta")
    def test_avaliar_respostas_jogador_acumula_pontuacao_com_sucesso(
        self,
        mock_diagnostico_cls,
        mock_calc_vmax,
        mock_calc_scores,
        mock_calc_detalhada,
        relatorio_fake,
        diagnostico_fake,
    ):
        """
        Acumula Pontuação com Sucesso

        Mockar o DiagnosticoDeResposta para retornar um DTO fake e o
        MotorDePontuacao para que a nota final retorne 1500.0.
        O método deve retornar o ResultadoDiagnosticoDTO com
        pontuacao_final=1500.0 e a pontuação acumulada deve ser
        incrementada com esse valor.
        """
        mock_diagnostico = MagicMock()
        mock_diagnostico.gerar_diagnostico_pontuacao.return_value = diagnostico_fake
        mock_diagnostico.gerar_feedback.return_value = DiagnosticoFeedbackDTO()
        mock_diagnostico_cls.return_value = mock_diagnostico

        mock_calc_vmax.return_value = 5000.0
        mock_calc_scores.return_value = ({}, {})
        mock_calc_detalhada.return_value = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=1, qnt_riscos_gabarito=1,
            qnt_riscos_corretos_marcados=1, estado_ato=True,
            estado_condicao=True, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=45.0, pontuacao_final=1500.0,
        )

        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__turno_iniciado = True
        g._GerenciadorDeTurno__relatorio_atual = relatorio_fake

        resultado = g.avaliar_respostas_jogador(
            riscos_marcados=["FISICO"],
            fatores_marcados=["ATO_INSEGURO"],
            decisao="ADVERTIR",
            tempo_segundos=45,
        )

        assert resultado.pontuacao.pontuacao_final == 1500.0
        assert g._GerenciadorDeTurno__pontuacao_acumulada_turno == 1500.0
        assert g._GerenciadorDeTurno__relatorio_atual is None
        mock_diagnostico.gerar_diagnostico_pontuacao.assert_called_once()

    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao.calcular_pontuacao_relatorio")
    @patch("application.controllers.gerenciador_de_turno.MotorDePontuacao.calcular_vmax_relatorio")
    @patch("application.controllers.gerenciador_de_turno.DiagnosticoDeResposta")
    def test_avaliar_libera_relatorio_atual_para_proximo_pop(
        self,
        mock_diagnostico_cls,
        mock_calc_vmax,
        mock_calc_pontuacao,
        relatorio_fake,
        diagnostico_fake,
    ):
        """
        Avaliar libera relatorio_atual para o próximo pop.

        Após avaliar com sucesso, o relatorio_atual deve ser None,
        permitindo obter o próximo relatório da pilha.
        """
        mock_diagnostico = MagicMock()
        mock_diagnostico.gerar_diagnostico_pontuacao.return_value = diagnostico_fake
        mock_diagnostico_cls.return_value = mock_diagnostico
        mock_calc_vmax.return_value = 5000.0
        mock_calc_pontuacao.return_value = 1500.0

        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__turno_iniciado = True
        g._GerenciadorDeTurno__pilha_relatorios = [relatorio_fake, relatorio_fake]
        g._GerenciadorDeTurno__relatorio_atual = relatorio_fake

        g.avaliar_respostas_jogador(
            riscos_marcados=["FISICO"],
            fatores_marcados=["ATO_INSEGURO"],
            decisao="ADVERTIR",
            tempo_segundos=45,
        )

        prox = g.obter_relatorio_da_pilha()
        assert prox is relatorio_fake


class TestVerificarVitoria:
    """
    Testes do Método verificar_vitoria_do_turno

    Garantir que a vitória só pode ser verificada com a pilha vazia e
    que o resultado reflete corretamente o limiar de aprovação.
    """

    def test_verificar_vitoria_com_relatorio_pendente_lanca_excecao(
        self, relatorio_fake
    ):
        """
        Relatório pendente lança exceção.

        Chamar verificar_vitoria_do_turno() com relatorio_atual ainda
        pendente deve lançar RuntimeError.
        """
        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__turno_iniciado = True
        g._GerenciadorDeTurno__relatorio_atual = relatorio_fake

        with pytest.raises(RuntimeError, match="pendente de avaliação"):
            g.verificar_vitoria_do_turno()

    def test_verificar_vitoria_com_pilha_nao_vazia_lanca_excecao(
        self, relatorio_fake
    ):
        """
        Pilha Não Vazia Lança Exceção

        Chamar verificar_vitoria_do_turno() antes de esvaziar os
        relatórios deve lançar ValueError com a tag [Erro - Turno].
        """
        g = GerenciadorDeTurno("DEFAULT")
        g._GerenciadorDeTurno__turno_iniciado = True
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
        g._GerenciadorDeTurno__turno_iniciado = True
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
        g._GerenciadorDeTurno__turno_iniciado = True
        g._GerenciadorDeTurno__pilha_relatorios = []
        g._GerenciadorDeTurno__pontuacao_acumulada_turno = 3000.0
        g._GerenciadorDeTurno__v_max_turno = 10000.0

        assert g.verificar_vitoria_do_turno() is False
        mock_conferir.assert_called_once_with(3000.0, 10000.0)
