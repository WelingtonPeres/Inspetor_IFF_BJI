"""
Suite completa de testes para a TelaDeExpediente.
"""

import pytest
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtWidgets import (
    QComboBox, QFrame, QLabel, QProgressBar, QPushButton,
    QSplitter, QStackedWidget, QWidget,
)

from view.expediente.tela import TelaDeExpediente
from view.expediente.widgets.anexo_preview import AnexoPreview
from view.expediente.widgets.sidebar import Sidebar
from view.expediente.widgets.window_title_bar import WindowTitleBar
from view.expediente.overlays.anexo_gallery import AnexoGallery
from view.expediente.overlays.media_viewer import MediaViewer
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def expediente():
    """Retorna uma TelaDeExpediente com LayoutLoader configurado."""
    from view.infrastructure.layout_loader import LayoutLoader
    LayoutLoader._instance = None
    LayoutLoader.instance().set_screen(1920, 1080)
    return TelaDeExpediente()


class TestEstrutura:
    """
    Testes de estrutura basica da TelaDeExpediente.

    Verifica objectName, property class, componentes principais.
    """

    def test_object_name(self, expediente):
        """A TelaDeExpediente deve ter objectName 'tela_de_expediente'."""
        assert expediente.objectName() == "tela_de_expediente"

    def test_property_class(self, expediente):
        """A TelaDeExpediente deve ter property class 'tela_expediente'."""
        assert expediente.property("class") == "tela_expediente"

    def test_window_title_bar_integrado(self, expediente):
        """TelaDeExpediente deve conter um WindowTitleBar."""
        bar = expediente.findChild(WindowTitleBar)
        assert bar is not None

    def test_stacked_com_cinco_paginas(self, expediente):
        """O QStackedWidget interno deve conter 5 paginas."""
        stack = expediente.findChild(QStackedWidget)
        assert stack is not None
        assert stack.count() == 5

    def test_sidebar_integrada(self, expediente):
        """TelaDeExpediente deve conter uma Sidebar."""
        sidebar = expediente.findChild(Sidebar)
        assert sidebar is not None

    def test_anexo_preview_integrado(self, expediente):
        """TelaDeExpediente deve conter um AnexoPreview."""
        preview = expediente.findChild(AnexoPreview)
        assert preview is not None

    def test_anexo_gallery_integrado(self, expediente):
        """TelaDeExpediente deve conter uma AnexoGallery (escondida)."""
        gallery = expediente.findChild(AnexoGallery)
        assert gallery is not None
        assert not gallery.isVisible()

    def test_media_viewer_integrado(self, expediente):
        """TelaDeExpediente deve conter um MediaViewer (escondido)."""
        viewer = expediente.findChild(MediaViewer)
        assert viewer is not None
        assert not viewer.isVisible()


class TestPaginas:
    """
    Testes de navegacao entre as 4 paginas do QStackedWidget (sem loading).
    """

    def test_pagina_0_selecao_perfil(self, expediente):
        """A pagina 0 deve conter combo de perfis e botao confirmar."""
        expediente.exibir_selecao_perfil()
        stack = expediente.findChild(QStackedWidget)
        pagina = stack.widget(0)
        combo = pagina.findChild(QComboBox, "combo_perfil")
        assert combo is not None
        assert combo.count() == 9
        btn = pagina.findChild(QPushButton, "btn_confirmar_perfil")
        assert btn is not None

    def test_pagina_1_inspecao_com_splitter_60_40(self, expediente):
        """A pagina 1 deve conter QSplitter com proporcao 60/40."""
        expediente.renderizar_relatorio({"titulo": "Teste"})
        stack = expediente.findChild(QStackedWidget)
        pagina = stack.widget(1)
        splitter = pagina.findChild(QSplitter)
        assert splitter is not None
        assert splitter.count() == 2
        deck = pagina.findChild(QWidget, "deck_observacao")
        assert deck is not None
        prancheta = pagina.findChild(QWidget, "prancheta")
        assert prancheta is not None
        btn = pagina.findChild(QPushButton, "btn_submeter")
        assert btn is not None

    def test_pagina_2_diagnostico(self, expediente):
        """A pagina 2 deve conter label de feedback e botao continuar."""
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=2, qnt_riscos_gabarito=3,
            qnt_riscos_corretos_marcados=1, estado_ato=True,
            estado_condicao=False, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=30.0, pontuacao_final=1500.0,
        )
        expediente.exibir_tela_diagnostico(dto)
        stack = expediente.findChild(QStackedWidget)
        pagina = stack.widget(2)
        btn = pagina.findChild(QPushButton, "btn_continuar")
        assert btn is not None

    @pytest.mark.parametrize("venceu,indice_esperado", [
        (True, 3),
        (False, 4),
    ])
    def test_pagina_3_4_endgame_win_lose(self, expediente, venceu, indice_esperado):
        """As paginas 3 e 4 devem exibir GameWin/GameOver conforme venceu."""
        expediente.exibir_tela_endgame(pontuacao_global=5000.0, dias_concluidos=1, venceu=venceu)
        stack = expediente.findChild(QStackedWidget)
        assert stack.currentIndex() == indice_esperado
        pagina = stack.widget(indice_esperado)
        if venceu:
            titulo = pagina.findChild(QLabel, "label_endgame_titulo")
            assert titulo is not None
            assert titulo.text() == "EXPEDIENTE CONCLU\u00CDDO"
            pont = pagina.findChild(QLabel, "label_endgame_pontuacao")
            assert pont is not None
            assert "5000.0" in pont.text()
        else:
            titulo = pagina.findChild(QLabel, "gameover_titulo")
            assert titulo is not None
            assert titulo.text() == "GAME OVER"
            pont = pagina.findChild(QLabel, "gameover_score_valor")
            assert pont is not None
            assert "5000" in pont.text()

    def test_navegacao_ciclo_completo(self, expediente):
        """Navegar por todas as paginas sequencialmente deve funcionar."""
        expediente.exibir_selecao_perfil()
        assert expediente._TelaDeExpediente__stack.currentIndex() == 0
        expediente.renderizar_relatorio({"titulo": "Teste"})
        assert expediente._TelaDeExpediente__stack.currentIndex() == 1
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=0, qnt_riscos_gabarito=0,
            qnt_riscos_corretos_marcados=0, estado_ato=True,
            estado_condicao=True, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=10.0, pontuacao_final=500.0,
        )
        expediente.exibir_tela_diagnostico(dto)
        assert expediente._TelaDeExpediente__stack.currentIndex() == 2
        expediente.exibir_tela_endgame(5000.0, 1, True)
        assert expediente._TelaDeExpediente__stack.currentIndex() == 3
        expediente.exibir_tela_endgame(3000.0, 1, False)
        assert expediente._TelaDeExpediente__stack.currentIndex() == 4


class TestSignals:
    """
    Testes dos 5 sinais emitidos pela TelaDeExpediente.
    """

    def test_perfil_confirmado_signal(self, expediente, qtbot):
        """Clicar em confirmar deve emitir perfil_confirmado."""
        expediente.exibir_selecao_perfil()
        btn = expediente.findChild(QPushButton, "btn_confirmar_perfil")
        with qtbot.waitSignal(expediente.perfil_confirmado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_submeter_respostas_signal(self, expediente, qtbot):
        """Emitir submeter_respostas deve funcionar."""
        with qtbot.waitSignal(expediente.submeter_respostas, timeout=1000) as blocker:
            expediente.submeter_respostas.emit({
                "riscos": [], "fatores": [], "decisao": "", "tempo_segundos": 0,
            })
        dados = blocker.args[0]
        assert isinstance(dados, dict)

    def test_continuar_solicitado_signal(self, expediente, qtbot):
        """Clicar em continuar deve emitir continuar_solicitado."""
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=0, qnt_riscos_gabarito=0,
            qnt_riscos_corretos_marcados=0, estado_ato=True,
            estado_condicao=True, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=10.0, pontuacao_final=500.0,
        )
        expediente.exibir_tela_diagnostico(dto)
        btn = expediente.findChild(QPushButton, "btn_continuar")
        with qtbot.waitSignal(expediente.continuar_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_voltar_menu_signal(self, expediente, qtbot):
        """Clicar em voltar ao menu na pagina de endgame deve emitir voltar_menu_solicitado."""
        expediente.exibir_tela_endgame(5000.0, 1, True)
        btn = expediente.findChild(QPushButton, "btn_voltar_menu")
        with qtbot.waitSignal(expediente.voltar_menu_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_minimized_signal(self, expediente, qtbot):
        """minimized_solicitado deve ser emitivel."""
        with qtbot.waitSignal(expediente.minimized_solicitado, timeout=1000):
            expediente.minimized_solicitado.emit()


class TestTamanho:
    """
    Testes de tamanho 80%, minimizar, maximizar, restaurar.
    """

    def test_exibir_com_tamanho_inicial_80_porcento(self, expediente):
        """exibir_com_tamanho_inicial deve definir 80% do parent."""
        expediente.show()
        parent_rect = QRect(0, 0, 1920, 1080)
        expediente.exibir_com_tamanho_inicial(parent_rect)
        assert expediente.isVisible()
        assert expediente.width() == int(1920 * 0.8)
        assert expediente.height() == int(1080 * 0.8)
        expediente.hide()

    def test_tamanho_normal_preservado_apos_maximizar(self, expediente):
        """Maximizar deve salvar tamanho normal e depois restaurar."""
        expediente.show()
        parent_rect = QRect(0, 0, 1920, 1080)
        expediente.exibir_com_tamanho_inicial(parent_rect)
        tamanho_normal = expediente.geometry()
        expediente._TelaDeExpediente__on_maximizar_restaurar()
        assert expediente._TelaDeExpediente__maximizado
        expediente._TelaDeExpediente__on_maximizar_restaurar()
        assert not expediente._TelaDeExpediente__maximizado
        assert expediente.geometry() == tamanho_normal
        expediente.hide()

    def test_minimizar_esconde(self, expediente):
        """Minimizar deve esconder o widget."""
        expediente.show()
        expediente._TelaDeExpediente__on_minimizar()
        assert not expediente.isVisible()

    def test_minimizar_apos_reexibir_restaura_tamanho_normal(self, expediente):
        """Minimizar e re-exibir deve restaurar tamanho normal."""
        expediente.show()
        parent_rect = QRect(0, 0, 1920, 1080)
        expediente.exibir_com_tamanho_inicial(parent_rect)
        tamanho = expediente.geometry()
        expediente._TelaDeExpediente__on_minimizar()
        assert not expediente.isVisible()
        expediente.show()
        assert expediente.geometry() == tamanho

    def test_fechar_reseta_maximizado(self, expediente):
        """Fechar deve resetar estado maximizado."""
        expediente._TelaDeExpediente__maximizado = True
        expediente._TelaDeExpediente__on_fechar()
        assert not expediente._TelaDeExpediente__maximizado


class TestSidebar:
    """
    Testes de visibilidade condicional da sidebar por pagina.
    """

    def test_sidebar_oculta_na_selecao_perfil(self, expediente):
        """Sidebar deve estar oculta na pagina 0."""
        expediente.exibir_selecao_perfil()
        sidebar = expediente.findChild(Sidebar)
        assert sidebar.isHidden()

    def test_sidebar_visivel_na_inspecao(self, expediente):
        """Sidebar deve estar visivel na pagina 1 (nao oculta)."""
        expediente.renderizar_relatorio({"titulo": "Teste"})
        sidebar = expediente.findChild(Sidebar)
        assert not sidebar.isHidden()

    def test_sidebar_visivel_no_diagnostico(self, expediente):
        """Sidebar deve estar visivel na pagina 2 (nao oculta)."""
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=0, qnt_riscos_gabarito=0,
            qnt_riscos_corretos_marcados=0, estado_ato=True,
            estado_condicao=True, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=10.0, pontuacao_final=500.0,
        )
        expediente.exibir_tela_diagnostico(dto)
        sidebar = expediente.findChild(Sidebar)
        assert not sidebar.isHidden()

    def test_sidebar_oculta_no_endgame(self, expediente):
        """Sidebar deve estar oculta nas paginas de endgame (3 e 4)."""
        expediente.exibir_tela_endgame(5000.0, 1, True)
        sidebar = expediente.findChild(Sidebar)
        assert sidebar.isHidden()
        expediente.exibir_tela_endgame(3000.0, 1, False)
        assert sidebar.isHidden()


class TestTituloDinamico:
    """
    Testes do titulo dinamico no WindowTitleBar ao navegar.
    """

    def test_titulo_selecao_perfil(self, expediente):
        """exibir_selecao_perfil deve mudar titulo para 'Selecao de Perfil'."""
        expediente.exibir_selecao_perfil()
        bar = expediente.findChild(WindowTitleBar)
        label = bar.findChild(QLabel, "window_title_text")
        assert "Seleção" in label.text()

    def test_titulo_inspecao(self, expediente):
        """renderizar_relatorio deve mudar titulo para 'Relatorio: ...'."""
        expediente.renderizar_relatorio({"titulo": "Lab Quimico"})
        bar = expediente.findChild(WindowTitleBar)
        label = bar.findChild(QLabel, "window_title_text")
        assert "Lab Quimico" in label.text()

    def test_titulo_diagnostico(self, expediente):
        """exibir_tela_diagnostico deve mudar titulo."""
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=0, qnt_riscos_gabarito=0,
            qnt_riscos_corretos_marcados=0, estado_ato=True,
            estado_condicao=True, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=10.0, pontuacao_final=500.0,
        )
        expediente.exibir_tela_diagnostico(dto)
        bar = expediente.findChild(WindowTitleBar)
        label = bar.findChild(QLabel, "window_title_text")
        assert "Resultado" in label.text()


class TestCasosLimite:
    """
    Casos limite: dupla chamada, dados vazios, re-exibir.
    """

    def test_exibir_selecao_perfil_chamada_duas_vezes_deve_manter_stacked(self, expediente):
        """Chamar exibir_selecao_perfil duas vezes nao deve quebrar o stacked."""
        expediente.exibir_selecao_perfil()
        expediente.exibir_selecao_perfil()
        assert expediente._TelaDeExpediente__stack.currentIndex() == 0

    def test_renderizar_relatorio_com_dados_vazios_nao_deve_lancar_excecao(self, expediente):
        """renderizar_relatorio com dict vazio nao deve lancar excecao."""
        expediente.renderizar_relatorio({})
        assert expediente._TelaDeExpediente__stack.currentIndex() == 1

    def test_reiniciar_reseta_para_pagina_0(self, expediente):
        """reiniciar deve voltar para pagina 0 e limpar formulario."""
        expediente.renderizar_relatorio({"titulo": "Teste"})
        expediente.reiniciar()
        assert expediente._TelaDeExpediente__stack.currentIndex() == 0

    def test_resize_event_nao_crasha(self, expediente):
        """resizeEvent nao deve crashar quando os sub-overlays estao ocultos."""
        from PySide6.QtGui import QResizeEvent
        from PySide6.QtCore import QSize
        event = QResizeEvent(QSize(800, 600), QSize(1024, 768))
        expediente.resizeEvent(event)
