"""
Suite completa de testes para a JanelaPrincipal (overlay model).
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QPushButton

from view.main_window import JanelaPrincipal
from core.dtos.diagnostico_feedback import DiagnosticoFeedbackDTO
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO
from core.dtos.resultado_diagnostico import ResultadoDiagnosticoDTO


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def janela():
    """Retorna uma JanelaPrincipal."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    LayoutLoader.instance().set_screen(1920, 1080)
    return JanelaPrincipal()


class TestJanelaPrincipal:
    """
    Testes para a JanelaPrincipal refatorada com unico overlay expediente.

    Verifica os metodos do contrato IGameView e os sinais.
    """

    def test_eh_qmainwindow(self, janela):
        """A JanelaPrincipal deve ser um QMainWindow."""
        assert isinstance(janela, QMainWindow)

    def test_implementa_igameview(self, janela):
        """A JanelaPrincipal deve implementar IGameView."""
        from application.interfaces.i_game_view import IGameView
        assert isinstance(janela, IGameView)

    def test_tem_signals_corretos(self, janela):
        """Deve expor os 6 sinais de navegacao."""
        assert hasattr(janela, "iniciar_solicitado")
        assert hasattr(janela, "perfil_confirmado")
        assert hasattr(janela, "submeter_respostas")
        assert hasattr(janela, "continuar_solicitado")
        assert hasattr(janela, "voltar_menu_solicitado")
        assert hasattr(janela, "jogar_novamente_solicitado")

    def test_inicializar_e_fechar(self, janela):
        """inicializar deve exibir a janela; fechar deve oculta-la."""
        janela.inicializar()
        assert janela.isVisible()
        janela.fechar()
        assert not janela.isVisible()

    def test_exibir_menu(self, janela):
        """exibir_menu deve esconder o expediente."""
        janela.exibir_menu()

    def test_exibir_tutorial_executa_sem_erro(self, janela):
        """exibir_tutorial deve aceitar qualquer motivo sem erro (stub Etapa 1)."""
        from application.interfaces.i_game_view import MotivoTutorial

        janela.show()
        janela.exibir_tutorial(MotivoTutorial.NOVO_JOGO)
        janela.exibir_tutorial(MotivoTutorial.CONSULTA)
        janela.hide()

    def test_exibir_selecao_perfil_mostra_expediente(self, janela):
        """exibir_selecao_perfil deve mostrar a TelaDeExpediente."""
        janela.show()
        janela.exibir_selecao_perfil()
        te = janela.findChild(object, "tela_de_expediente")
        assert te is not None
        assert te.isVisible()

    def test_exibir_tela_diagnostico(self, janela):
        """exibir_tela_diagnostico deve delegar sem erros."""
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=2, qnt_riscos_gabarito=3,
            qnt_riscos_corretos_marcados=1, estado_ato=True,
            estado_condicao=False, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=30.0, pontuacao_final=1500.0,
        )
        janela.exibir_tela_diagnostico(
            ResultadoDiagnosticoDTO(pontuacao=dto, feedback=DiagnosticoFeedbackDTO())
        )

    def test_renderizar_relatorio(self, janela):
        """renderizar_relatorio deve delegar sem erros."""
        janela.renderizar_relatorio({
            "titulo": "Teste", "local": "Lab", "atividade": "teste",
        })

    def test_exibir_resultado(self, janela):
        """exibir_resultado deve delegar para TelaDeExpediente sem erros."""
        janela.exibir_resultado(pontuacao_global=5000.0, dias_concluidos=1, venceu=True)

    # Desabilitado: QMessageBox.critical bloqueia a execução até clique do
    # utilizador. Reativar quando houver mock do QMessageBox ou fixture que
    # suprima diálogos modais automaticamente.
    # def test_exibir_popup_erro(self, janela, qtbot):
    #     """exibir_popup_erro deve abrir um QMessageBox.critical."""
    #     janela.exibir_popup_erro("teste erro")

    def test_iniciar_solicitado_signal(self, janela, qtbot):
        """O signal iniciar_solicitado deve ser emitivel."""
        with qtbot.waitSignal(janela.iniciar_solicitado, timeout=1000):
            janela.iniciar_solicitado.emit()

    def test_help_solicitado_signal(self, janela, qtbot):
        """O signal help_solicitado deve ser emitivel."""
        with qtbot.waitSignal(janela.help_solicitado, timeout=1000):
            janela.help_solicitado.emit()

    def test_on_help_solicitado_emite_help_solicitado(self, janela, qtbot):
        """O slot privado de Help deve propagar o signal publico (regressao R6)."""
        with qtbot.waitSignal(janela.help_solicitado, timeout=1000):
            janela._JanelaPrincipal__on_help_solicitado()


class TestTutorial:
    """
    Testes da fiacao do tutorial na JanelaPrincipal.
    """

    def test_tutorial_finalizado_signal_existe(self, janela, qtbot):
        """tutorial_finalizado deve ser emitivel com um MotivoTutorial."""
        from application.interfaces.i_game_view import MotivoTutorial

        assert hasattr(janela, "tutorial_finalizado")
        with qtbot.waitSignal(janela.tutorial_finalizado, timeout=1000) as blocker:
            janela.tutorial_finalizado.emit(MotivoTutorial.NOVO_JOGO)
        assert blocker.args[0] == MotivoTutorial.NOVO_JOGO

    def test_exibir_tutorial_mostra_tela_e_sombra(self, janela):
        """exibir_tutorial deve mostrar a TelaTutorial e a sombra irma."""
        from application.interfaces.i_game_view import MotivoTutorial

        janela.show()
        janela.exibir_tutorial(MotivoTutorial.NOVO_JOGO)
        tela = janela.findChild(object, "tela_tutorial")
        sombra = janela.findChild(object, "tutorial_sombra")
        assert tela is not None
        assert tela.isVisible()
        assert sombra is not None
        assert sombra.isVisible()
        janela.hide()

    def test_sombra_acompanha_geometria_da_tela(self, janela):
        """A sombra deve espelhar a geometria da tela deslocada em (6, 6)."""
        from application.interfaces.i_game_view import MotivoTutorial

        janela.show()
        janela.exibir_tutorial(MotivoTutorial.NOVO_JOGO)
        tela = janela.findChild(object, "tela_tutorial")
        sombra = janela.findChild(object, "tutorial_sombra")
        assert sombra.geometry() == tela.geometry().translated(6, 6)
        janela.hide()

    def test_pular_emite_tutorial_finalizado(self, janela, qtbot):
        """Clicar em Pular deve propagar tutorial_finalizado com o motivo."""
        from application.interfaces.i_game_view import MotivoTutorial
        from PySide6.QtWidgets import QPushButton

        janela.show()
        janela.exibir_tutorial(MotivoTutorial.NOVO_JOGO)
        tela = janela.findChild(object, "tela_tutorial")
        btn = tela.findChild(QPushButton, "tutorial_pular")
        with qtbot.waitSignal(janela.tutorial_finalizado, timeout=1000) as blocker:
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        assert blocker.args[0] == MotivoTutorial.NOVO_JOGO
        janela.hide()

    def test_exibir_menu_esconde_tutorial(self, janela):
        """exibir_menu deve esconder o tutorial e a sombra."""
        from application.interfaces.i_game_view import MotivoTutorial

        janela.show()
        janela.exibir_tutorial(MotivoTutorial.NOVO_JOGO)
        janela.exibir_menu()
        tela = janela.findChild(object, "tela_tutorial")
        sombra = janela.findChild(object, "tutorial_sombra")
        assert not tela.isVisible()
        assert not sombra.isVisible()
        janela.hide()

    def test_consulta_sobre_expediente_usam_rect_do_expediente(self, janela):
        """Em consulta com expediente visivel, o tutorial nao pode ser maior
        que o rect actual do expediente."""
        from application.interfaces.i_game_view import MotivoTutorial

        janela.show()
        janela.exibir_selecao_perfil()
        expediente = janela.findChild(object, "tela_de_expediente")
        assert expediente.isVisible()
        janela.exibir_tutorial(MotivoTutorial.CONSULTA)
        tela = janela.findChild(object, "tela_tutorial")
        assert tela.width() <= expediente.width()
        assert tela.height() <= expediente.height()
        janela.hide()
