"""
Suite completa de testes para o GameManager.
"""

import pytest
from unittest.mock import MagicMock, create_autospec, patch

from application.interfaces.i_game_view import IGameView
from infrastructure.repository.repositorio_json import RepositorioJSON


def test_mascarar_perfil_mantem_DEFAULT():
    """
    Máscara Mantém DEFAULT

    O perfil 'DEFAULT' não deve ser alterado pela máscara,
    pois já possui dados disponíveis.
    """
    resultado = GameManager._GameManager__mascarar_perfil("DEFAULT")
    assert resultado == "DEFAULT"


def test_mascarar_perfil_mantem_invalido():
    """
    Máscara Mantém Perfil Inválido

    Um perfil que não existe em CURSOS_VALIDOS deve passar
    limpo pela máscara, para que a verificação de erro
    em __iniciar_dia funcione.
    """
    resultado = GameManager._GameManager__mascarar_perfil("PERFIL_INVALIDO")
    assert resultado == "PERFIL_INVALIDO"


def test_mascarar_perfil_redireciona_para_DEFAULT():
    """
    Máscara Redireciona para DEFAULT

    Perfis que existem em CURSOS_VALIDOS mas não são 'DEFAULT'
    devem ser redirecionados para 'DEFAULT', já que atualmente
    só existem cenários para o curso DEFAULT.
    """
    for curso in RepositorioJSON.CURSOS_VALIDOS:
        if curso == "DEFAULT":
            continue
        resultado = GameManager._GameManager__mascarar_perfil(curso)
        assert resultado == "DEFAULT", f"{curso} deveria ser mascarado para DEFAULT"

from application.controllers.game_manager import GameManager
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO


@pytest.fixture
def view_mock():
    """Mock da View injetada no GameManager, validado contra IGameView."""
    return create_autospec(IGameView)


@pytest.fixture
def gm(view_mock):
    """GameManager com View mockada, pronto para testes."""
    return GameManager(view_mock)


@pytest.fixture
def diagnostico_dto_fake():
    """DiagnosticoPontuacaoDTO fake com pontuacao_final=1500.0 para testes de submissao."""
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


class TestInicializacao:
    """
    Testes de Construção e Estado Inicial

    Garantir que o GameManager é instanciado corretamente com a View injetada
    e que o estado inicial reflete o menu sem campanha ativa.
    """

    def test_estado_inicial_menu(self, gm):
        """
        Estado Inicial é ESTADO_MENU

        Ao instanciar o GameManager, o estado deve ser ESTADO_MENU,
        nenhum turno ativo e nenhum perfil selecionado.
        """
        assert gm._GameManager__estado_atual == GameManager.ESTADO_MENU
        assert gm._GameManager__gerenciador_turno is None
        assert gm._GameManager__perfil_selecionado == ""
        assert gm._GameManager__dias_concluidos == 0
        assert gm._GameManager__pontuacao_global == 0.0

    def test_view_injetada(self, gm, view_mock):
        """
        View Injetada Corretamente

        A view passada no construtor deve ser armazenada internamente.
        """
        assert gm._GameManager__view is view_mock


class TestCarregarMenuPrincipal:
    """
    Testes do Método carregar_menu_principal

    Validar que o método reseta corretamente o estado da campanha
    e instrui a View a exibir o menu.
    """

    def test_reseta_estado_para_menu(self, gm):
        """
        Reseta Estado para Menu

        Configurar um estado de campanha ativa e depois chamar
        carregar_menu_principal. O estado deve voltar ao inicial.
        """
        gm._GameManager__estado_atual = GameManager.ESTADO_EXPEDIENTE
        gm._GameManager__perfil_selecionado = "T_QUIMICA"
        gm._GameManager__dias_concluidos = 2
        gm._GameManager__pontuacao_global = 5000.0

        gm.carregar_menu_principal()

        assert gm._GameManager__estado_atual == GameManager.ESTADO_MENU
        assert gm._GameManager__gerenciador_turno is None
        assert gm._GameManager__perfil_selecionado == ""
        assert gm._GameManager__dias_concluidos == 0
        assert gm._GameManager__pontuacao_global == 0.0

    def test_view_exibir_menu_chamado(self, gm, view_mock):
        """
        View.exibir_menu é Chamado

        carregar_menu_principal deve chamar o método exibir_menu da View.
        """
        gm.carregar_menu_principal()
        view_mock.exibir_menu.assert_called_once_with()


class TestIniciarAplicacao:
    """
    Testes do Método iniciar_aplicacao

    Validar que a aplicação inicializa a View e carrega o menu principal.
    """

    def test_inicializa_view_e_carrega_menu(self, gm, view_mock):
        """
        Inicializa View e Carrega Menu

        iniciar_aplicacao deve chamar view.inicializar() e depois
        carregar_menu_principal.
        """
        gm.iniciar_aplicacao()

        view_mock.inicializar.assert_called_once_with()
        view_mock.exibir_menu.assert_called_once_with()


class TestEncerrarAplicacao:
    """
    Testes do Método encerrar_aplicacao

    Validar que a aplicação instrui a View a fechar.
    """

    def test_view_fechar_chamado(self, gm, view_mock):
        """
        View.fechar é Chamado

        encerrar_aplicacao deve chamar o método fechar da View.
        """
        gm.encerrar_aplicacao()
        view_mock.fechar.assert_called_once_with()


class TestOnIniciarSolicitado:
    """
    Testes do Método on_iniciar_solicitado

    Validar que o método instrui a View a exibir a seleção de perfil
    apenas quando o estado atual é ESTADO_MENU.
    """

    def test_view_exibir_selecao_perfil_chamado(self, gm, view_mock):
        """
        View.exibir_selecao_perfil é Chamado

        on_iniciar_solicitado deve chamar exibir_selecao_perfil da View
        quando o estado actual for ESTADO_MENU.
        """
        gm.on_iniciar_solicitado()
        view_mock.exibir_selecao_perfil.assert_called_once_with()

    def test_ignorado_fora_do_menu(self, gm, view_mock):
        """
        Deve ser Ignorado Fora do Menu

        on_iniciar_solicitado não deve chamar exibir_selecao_perfil
        se o estado actual não for ESTADO_MENU.
        """
        gm._GameManager__estado_atual = gm.ESTADO_EXPEDIENTE
        gm.on_iniciar_solicitado()
        view_mock.exibir_selecao_perfil.assert_not_called()


class TestIniciarExpediente:
    """
    Testes do Método iniciar_expediente

    Validar que o perfil é validado, a campanha é iniciada e o turno
    é criado corretamente.
    """

    @patch("application.controllers.game_manager.GerenciadorDeTurno")
    def test_iniciar_expediente_com_sucesso(
        self, mock_turno_cls, gm, view_mock
    ):
        """
        Fluxo Feliz do Expediente

        Mockar o GerenciadorDeTurno para que retorne um turno válido.
        Chamar iniciar_expediente deve criar o turno, iniciá-lo,
        renderizar o primeiro relatório e instruir a View a trocar
        para a tela de inspeção.
        """
        dados_esperados = {"id_cenario": 1, "titulo": "Primeiro"}
        mock_relatorio = MagicMock()
        mock_relatorio.extrair_apresentacao_relatorio.return_value = dados_esperados

        mock_turno = MagicMock()
        mock_turno.iniciar_turno.return_value = True
        mock_turno.obter_relatorio_da_pilha.return_value = mock_relatorio
        mock_turno_cls.return_value = mock_turno

        gm.iniciar_expediente("T_MEIO_AMBIENTE")

        assert gm._GameManager__estado_atual == GameManager.ESTADO_EXPEDIENTE
        assert gm._GameManager__perfil_selecionado == "DEFAULT"
        assert gm._GameManager__dias_concluidos == 0
        assert gm._GameManager__pontuacao_global == 0.0
        assert gm._GameManager__gerenciador_turno is mock_turno

        mock_turno_cls.assert_called_once_with("DEFAULT")
        mock_turno.iniciar_turno.assert_called_once_with()
        mock_turno.obter_relatorio_da_pilha.assert_called_once()
        view_mock.trocar_para_tela_inspecao.assert_called_once_with()
        view_mock.renderizar_relatorio.assert_called_once_with(dados_esperados)

    def test_iniciar_expediente_perfil_invalido_retorna_ao_menu(self, gm, view_mock):
        """
        Expediente com Perfil Inválido Retorna ao Menu

        Se o perfil não existir nos cursos válidos do RepositorioJSON,
        o __iniciar_dia captura a exceção, exibe popup de erro e
        retorna ao menu principal.
        """
        gm.iniciar_expediente("PERFIL_INVALIDO")

        assert gm._GameManager__estado_atual == GameManager.ESTADO_MENU
        assert gm._GameManager__gerenciador_turno is None
        assert gm._GameManager__perfil_selecionado == ""
        assert gm._GameManager__dias_concluidos == 0
        assert gm._GameManager__pontuacao_global == 0.0
        view_mock.exibir_popup_erro.assert_called_once()
        args_chamada = view_mock.exibir_popup_erro.call_args[0][0]
        assert "Falha ao carregar os dados do expediente" in args_chamada
        assert "Curso" in args_chamada
        assert "PERFIL_INVALIDO" in args_chamada
        view_mock.exibir_menu.assert_called_once_with()

    def test_iniciar_expediente_fora_do_menu_lanca_erro(self, gm):
        """
        Expediente Fora do Menu Lança Erro

        Chamar iniciar_expediente com estado diferente de ESTADO_MENU
        deve lançar RuntimeError com a tag [Erro - GameManager].
        """
        gm._GameManager__estado_atual = GameManager.ESTADO_EXPEDIENTE

        with pytest.raises(RuntimeError, match="\\[Erro - GameManager\\] Expediente"):
            gm.iniciar_expediente("T_QUIMICA")

    def test_iniciar_campanha_guard_fora_do_menu_lanca_erro(self, gm):
        """
        Guarda de __iniciar_campanha Fora do Menu Lança Erro

        Chamar __iniciar_campanha diretamente com estado diferente de
        ESTADO_MENU deve lançar RuntimeError com a tag [Erro - GameManager].
        """
        gm._GameManager__estado_atual = GameManager.ESTADO_EXPEDIENTE

        with pytest.raises(RuntimeError, match="\\[Erro - GameManager\\] Campanha"):
            gm._GameManager__iniciar_campanha("T_QUIMICA")


class TestRequisitarDadosRelatorio:
    """
    Testes do Método requisitar_dados_relatorio_atual

    Validar que os dados de apresentação do relatório são extraídos
    corretamente do GerenciadorDeTurno.
    """

    @patch("application.controllers.game_manager.GerenciadorDeTurno")
    def test_retorna_dict_de_apresentacao(self, mock_turno_cls, gm):
        """
        Retorna Dict de Apresentação

        Configurar um turno mockado com um relatório fake que retorna
        um dicionário. O método deve retornar esse dicionário.
        """
        dados_esperados = {
            "id_cenario": 1,
            "titulo": "Cenário Teste",
            "atividade": "Inspeção",
            "local": "Setor X",
            "texto_descricao": "Descrição",
            "envolvidos": ["Agente"],
            "anexos": [],
        }

        mock_relatorio = MagicMock()
        mock_relatorio.extrair_apresentacao_relatorio.return_value = dados_esperados

        mock_turno = MagicMock()
        mock_turno.obter_relatorio_da_pilha.return_value = mock_relatorio
        mock_turno_cls.return_value = mock_turno

        gm._GameManager__gerenciador_turno = mock_turno

        resultado = gm._GameManager__requisitar_dados_relatorio_atual()

        assert resultado == dados_esperados
        mock_turno.obter_relatorio_da_pilha.assert_called_once_with()

    def test_sem_turno_ativo_lanca_erro(self, gm):
        """
        Sem Turno Ativo Lança Erro

        Chamar requisitar_dados_relatorio_atual sem um turno ativo
        deve lançar RuntimeError.
        """
        with pytest.raises(RuntimeError, match="\\[Erro - GameManager\\] Nenhum turno"):
            gm._GameManager__requisitar_dados_relatorio_atual()


class TestProcessarSubmissao:
    """
    Testes do Método processar_submissao

    Validar a delegação da avaliação para o GerenciadorDeTurno,
    o acúmulo da pontuação global e o tratamento de erros.
    """

    @patch("application.controllers.game_manager.GerenciadorDeTurno")
    def test_submissao_com_sucesso_acumula_pontuacao(
        self, mock_turno_cls, gm, view_mock, diagnostico_dto_fake
    ):
        """
        Submissão com Sucesso Acumula Pontuação

        Mockar o turno para retornar um DiagnosticoPontuacaoDTO com
        pontuacao_final=1500.0. O método deve acumular esse valor na
        pontuação global e chamar view.exibir_tela_diagnostico com o DTO.
        """
        mock_turno = MagicMock()
        mock_turno.avaliar_respostas_jogador.return_value = diagnostico_dto_fake
        mock_turno_cls.return_value = mock_turno

        gm._GameManager__gerenciador_turno = mock_turno
        gm._GameManager__pontuacao_global = 500.0

        gm.processar_submissao({
            "riscos": ["FISICO"],
            "fatores": ["ATO_INSEGURO"],
            "decisao": "ADVERTIR",
            "tempo_segundos": 45,
        })

        assert gm._GameManager__pontuacao_global == 2000.0

        mock_turno.avaliar_respostas_jogador.assert_called_once_with(
            riscos_marcados=["FISICO"],
            fatores_marcados=["ATO_INSEGURO"],
            decisao="ADVERTIR",
            tempo_segundos=45,
        )
        view_mock.exibir_tela_diagnostico.assert_called_once_with(diagnostico_dto_fake)

    @patch("application.controllers.game_manager.GerenciadorDeTurno")
    def test_submissao_captura_value_error_e_exibe_popup(
        self, mock_turno_cls, gm, view_mock
    ):
        """
        Submissão Captura ValueError

        Se o turno lançar ValueError (regra de negócio violada),
        o GameManager deve capturar e exibir o popup de erro na View.
        """
        mock_turno = MagicMock()
        mock_turno.avaliar_respostas_jogador.side_effect = ValueError(
            "[Erro - Turno] Decisão inválida."
        )
        mock_turno_cls.return_value = mock_turno

        gm._GameManager__gerenciador_turno = mock_turno

        gm.processar_submissao({
            "riscos": [],
            "fatores": [],
            "decisao": "",
            "tempo_segundos": 0,
        })

        view_mock.exibir_popup_erro.assert_called_once_with(
            "[Erro - Turno] Decisão inválida."
        )

    @patch("application.controllers.game_manager.GerenciadorDeTurno")
    def test_submissao_captura_exception_generico_e_exibe_popup(
        self, mock_turno_cls, gm, view_mock
    ):
        """
        Submissão Captura Exception Genérico

        Se o turno lançar uma exceção que não seja ValueError
        (ex: RuntimeError, KeyError), o GameManager deve capturar
        e exibir popup genérico "Ocorreu um erro interno".
        """
        mock_turno = MagicMock()
        mock_turno.avaliar_respostas_jogador.side_effect = RuntimeError(
            "Falha inesperada no motor."
        )
        mock_turno_cls.return_value = mock_turno

        gm._GameManager__gerenciador_turno = mock_turno

        gm.processar_submissao({
            "riscos": [],
            "fatores": [],
            "decisao": "",
            "tempo_segundos": 0,
        })

        view_mock.exibir_popup_erro.assert_called_once_with(
            "Ocorreu um erro interno ao processar o relatorio."
        )

    def test_submissao_sem_turno_lanca_erro(self, gm):
        """
        Submissão sem Turno Lança Erro

        Chamar processar_submissao sem um turno ativo deve lançar
        RuntimeError.
        """
        with pytest.raises(RuntimeError, match="\\[Erro - GameManager\\] Nenhum turno"):
            gm.processar_submissao({})


class TestAvancarFilaOuDia:
    """
    Testes do Método avancar_fila_ou_dia

    Validar a lógica de decisão entre puxar o próximo relatório,
    iniciar um novo dia ou encerrar a campanha.
    """

    @patch("application.controllers.game_manager.GerenciadorDeTurno")
    def test_avancar_com_relatorios_restantes_volta_para_inspecao(
        self, mock_turno_cls, gm, view_mock
    ):
        """
        Avançar com Relatórios Restantes

        Se ainda há relatórios na pilha, o método deve instruir a
        View a trocar para a tela de inspeção e renderizar o próximo.
        """
        dados_esperados = {"id_cenario": 2, "titulo": "Próximo"}
        mock_relatorio = MagicMock()
        mock_relatorio.extrair_apresentacao_relatorio.return_value = dados_esperados

        mock_turno = MagicMock()
        mock_turno.qnt_relatorios.return_value = 2
        mock_turno.obter_relatorio_da_pilha.return_value = mock_relatorio
        mock_turno_cls.return_value = mock_turno

        gm._GameManager__gerenciador_turno = mock_turno

        gm.avancar_fila_ou_dia()

        view_mock.trocar_para_tela_inspecao.assert_called_once_with()
        view_mock.renderizar_relatorio.assert_called_once_with(dados_esperados)

    @patch("application.controllers.game_manager.GerenciadorDeTurno")
    def test_avancar_ultimo_dia_encerra_campanha_vitoria(
        self, mock_turno_cls, gm, view_mock
    ):
        """
        Avançar no Último Dia com Vitória

        Com pilha vazia e CAMPANHA_DURACAO_DIAS=1, o GameManager deve
        delegar a verificacao de vitoria ao GerenciadorDeTurno. Quando
        verificar_vitoria_do_turno retorna True, a View recebe venceu=True.
        """
        mock_turno = MagicMock()
        mock_turno.qnt_relatorios.return_value = 0
        mock_turno.verificar_vitoria_do_turno.return_value = True
        mock_turno_cls.return_value = mock_turno

        gm._GameManager__gerenciador_turno = mock_turno
        gm._GameManager__dias_concluidos = 0
        gm._GameManager__pontuacao_global = 8500.0

        gm.avancar_fila_ou_dia()

        assert gm._GameManager__dias_concluidos == 1
        assert gm._GameManager__estado_atual == GameManager.ESTADO_RESULTADO
        mock_turno.verificar_vitoria_do_turno.assert_called_once_with()
        view_mock.exibir_resultado.assert_called_once_with(8500.0, 1, True)

    @patch("application.controllers.game_manager.GerenciadorDeTurno")
    def test_avancar_ultimo_dia_encerra_campanha_derrota(
        self, mock_turno_cls, gm, view_mock
    ):
        """
        Avançar no Último Dia com Derrota

        Quando verificar_vitoria_do_turno retorna False, a View deve
        receber venceu=False, para que o PaginaEndgame renderize o
        status de derrota no lugar de vitoria.
        """
        mock_turno = MagicMock()
        mock_turno.qnt_relatorios.return_value = 0
        mock_turno.verificar_vitoria_do_turno.return_value = False
        mock_turno_cls.return_value = mock_turno

        gm._GameManager__gerenciador_turno = mock_turno
        gm._GameManager__dias_concluidos = 0
        gm._GameManager__pontuacao_global = 3000.0

        gm.avancar_fila_ou_dia()

        assert gm._GameManager__dias_concluidos == 1
        assert gm._GameManager__estado_atual == GameManager.ESTADO_RESULTADO
        mock_turno.verificar_vitoria_do_turno.assert_called_once_with()
        view_mock.exibir_resultado.assert_called_once_with(3000.0, 1, False)

    def test_avancar_sem_turno_lanca_erro(self, gm):
        """
        Avançar sem Turno Lança Erro

        Chamar avancar_fila_ou_dia sem um turno ativo deve lançar
        RuntimeError.
        """
        with pytest.raises(RuntimeError, match="\\[Erro - GameManager\\] Nenhum turno"):
            gm.avancar_fila_ou_dia()


class TestReiniciarExpediente:
    """
    Testes do metodo reiniciar_expediente.
    """

    def test_reiniciar_expediente_chama_carregar_menu_e_iniciar(self, gm, view_mock):
        """
        Reiniciar Expediente Deve Chamar Menu e Iniciar

        reiniciar_expediente() deve guardar o perfil, chamar
        carregar_menu_principal() e depois iniciar_expediente()
        com o perfil guardado.
        """
        from unittest.mock import patch

        gm._GameManager__perfil_selecionado = "DEFAULT"
        gm._GameManager__estado_atual = GameManager.ESTADO_RESULTADO

        with patch.object(gm, "carregar_menu_principal") as mock_menu, \
             patch.object(gm, "iniciar_expediente") as mock_iniciar:
            gm.reiniciar_expediente()

            mock_menu.assert_called_once()
            mock_iniciar.assert_called_once_with("DEFAULT")
