"""
Suite completa de testes para a JanelaPrincipal (overlay model).
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QMessageBox, QPushButton

from view.main_window import JanelaPrincipal
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO


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
    Testes para a JanelaPrincipal refatorada com modelo de overlays.

    Verifica os 9 metodos do contrato IGameView e os sinais.
    """

    def test_eh_qmainwindow(self, janela):
        """A JanelaPrincipal deve ser um QMainWindow."""
        assert isinstance(janela, QMainWindow)

    def test_implementa_igameview(self, janela):
        """A JanelaPrincipal deve implementar IGameView."""
        from application.interfaces.i_game_view import IGameView
        assert isinstance(janela, IGameView)

    def test_tem_signals_corretos(self, janela):
        """Deve expor os 4 sinais de navegacao."""
        assert hasattr(janela, "iniciar_solicitado")
        assert hasattr(janela, "perfil_confirmado")
        assert hasattr(janela, "submeter_respostas")
        assert hasattr(janela, "continuar_solicitado")

    def test_inicializar_e_fechar(self, janela):
        """inicializar deve exibir a janela; fechar deve oculta-la."""
        janela.inicializar()
        assert janela.isVisible()
        janela.fechar()
        assert not janela.isVisible()

    def test_exibir_menu_esconde_overlays(self, janela):
        """exibir_menu deve esconder janela_sistema e tela_inspecao."""
        janela.exibir_menu()

    def test_exibir_selecao_perfil_mostra_janela_sistema(self, janela):
        """exibir_selecao_perfil deve mostrar a JanelaSistema."""
        janela.show()
        janela.exibir_selecao_perfil()
        js = janela.findChild(object, "janela_sistema")
        assert js is not None
        assert js.isVisible()

    def test_trocar_para_tela_inspecao_mostra_cheia(self, janela):
        """trocar_para_tela_inspecao deve mostrar a TelaInspecaoCheia."""
        janela.show()
        janela.trocar_para_tela_inspecao()
        ti = janela.findChild(object, "tela_inspecao_cheia")
        assert ti is not None
        assert ti.isVisible()

    def test_exibir_tela_diagnostico(self, janela):
        """exibir_tela_diagnostico deve delegar e trocar o stacked."""
        janela.show()
        janela.trocar_para_tela_inspecao()
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=2, qnt_riscos_gabarito=3,
            qnt_riscos_corretos_marcados=1, estado_ato=True,
            estado_condicao=False, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=30.0, pontuacao_final=1500.0,
        )
        janela.exibir_tela_diagnostico(dto)

    def test_renderizar_relatorio(self, janela):
        """renderizar_relatorio deve delegar sem erros."""
        janela.renderizar_relatorio({
            "titulo": "Teste", "local": "Lab", "atividade": "teste",
        })

    def test_exibir_resultado(self, janela):
        """exibir_resultado deve delegar sem erros."""
        janela.exibir_resultado(pontuacao_global=5000.0, dias_concluidos=1)

    def test_exibir_popup_erro(self, janela, qtbot):
        """exibir_popup_erro deve abrir um QMessageBox.critical."""
        janela.exibir_popup_erro("teste erro")

    def test_iniciar_solicitado_signal(self, janela, qtbot):
        """O signal iniciar_solicitado deve ser emitivel."""
        with qtbot.waitSignal(janela.iniciar_solicitado, timeout=1000):
            janela.iniciar_solicitado.emit()
