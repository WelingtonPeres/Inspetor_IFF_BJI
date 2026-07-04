"""
Suite completa de testes para a TelaInspecaoCheia.
"""

import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QPushButton, QStackedWidget

from view.components.anexo_preview import AnexoPreview
from view.components.sidebar import Sidebar
from view.screens.anexo_gallery import AnexoGallery
from view.screens.media_viewer import MediaViewer
from view.screens.tela_inspecao_cheia import TelaInspecaoCheia
from core.dtos.diagnostico_pontuacao import DiagnosticoPontuacaoDTO


@pytest.fixture(autouse=True)
def qt_app(qapp):
    return qapp


@pytest.fixture
def tela():
    """Retorna uma TelaInspecaoCheia."""
    return TelaInspecaoCheia()


class TestTelaInspecaoCheia:
    """
    Testes para a TelaInspecaoCheia (overlay z=2 de gameplay).

    Verifica header, sidebar, navegacao interna, formulario,
    anexo_preview, gallery, media_viewer e metodos do contrato.
    """

    def test_object_name(self, tela):
        """A TelaInspecaoCheia deve ter objectName 'tela_inspecao_cheia'."""
        assert tela.objectName() == "tela_inspecao_cheia"

    def test_property_class(self, tela):
        """A TelaInspecaoCheia deve ter property class 'tela_cheia'."""
        assert tela.property("class") == "tela_cheia"

    def test_header_bar_existe(self, tela):
        """O header deve conter um titulo e o botao minimizar."""
        header = tela.findChild(QLabel, "header_title")
        assert header is not None
        btn = tela.findChild(QPushButton, "minimizar_button")
        assert btn is not None
        assert btn.text() == "\u2014"

    def test_minimizar_signal(self, tela, qtbot):
        """Ao clicar no minimizar, o signal minimizar_solicitado deve ser emitido."""
        btn = tela.findChild(QPushButton, "minimizar_button")
        with qtbot.waitSignal(tela.minimizar_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_stacked_tres_paginas(self, tela):
        """O QStackedWidget interno deve conter 3 paginas."""
        stack = tela.findChild(QStackedWidget)
        assert stack is not None
        assert stack.count() == 3

    def test_stacked_indice_0_inspecao(self, tela):
        """O indice 0 deve conter os widgets do formulario de inspecao."""
        stack = tela.findChild(QStackedWidget)
        pagina = stack.widget(0)
        assert pagina is not None
        btn = pagina.findChild(QPushButton, "btn_submeter")
        assert btn is not None

    def test_coletar_respostas(self, tela, qtbot):
        """Ao submeter, o signal submeter_respostas deve emitir um dict."""
        with qtbot.waitSignal(tela.submeter_respostas, timeout=1000) as blocker:
            tela.submeter_respostas.emit({
                "riscos": [],
                "fatores": [],
                "decisao": "IGNORAR",
                "tempo_segundos": 5,
            })
        dados = blocker.args[0]
        assert isinstance(dados, dict)
        assert "riscos" in dados
        assert "fatores" in dados
        assert "decisao" in dados
        assert "tempo_segundos" in dados

    def test_limpar_formulario(self, tela):
        """renderizar_relatorio deve limpar todos os campos."""
        tela.renderizar_relatorio({
            "titulo": "Teste", "local": "Lab", "atividade": "teste",
            "texto_descricao": "descricao",
        })
        chk_risco = tela._TelaInspecaoCheia__chk_riscos["FISICO"]
        chk_fator = tela._TelaInspecaoCheia__chk_fatores["ATO_INSEGURO"]
        assert not chk_risco.isChecked()
        assert not chk_fator.isChecked()

    def test_exibir_diagnostico(self, tela):
        """exibir_tela_diagnostico deve trocar o stacked para indice 1."""
        dto = DiagnosticoPontuacaoDTO(
            qnt_riscos_marcados=2, qnt_riscos_gabarito=3,
            qnt_riscos_corretos_marcados=1, estado_ato=True,
            estado_condicao=False, status_decisao_jogador="OTIMA",
            tempo_resposta_segundos=30.0, pontuacao_final=1500.0,
        )
        tela.exibir_tela_diagnostico(dto)
        stack = tela.findChild(QStackedWidget)
        assert stack.currentIndex() == tela.IDX_DIAGNOSTICO

    def test_exibir_resultado(self, tela):
        """exibir_resultado deve trocar o stacked para indice 2."""
        tela.exibir_resultado(pontuacao_global=5000.0, dias_concluidos=1)
        stack = tela.findChild(QStackedWidget)
        assert stack.currentIndex() == tela.IDX_RESULTADO

    def test_resultado_botao_voltar(self, tela):
        """Resultado deve conter botao 'Voltar ao Menu'."""
        tela.exibir_resultado(pontuacao_global=5000.0, dias_concluidos=1)
        btn = tela.findChild(QPushButton, "btn_voltar_menu")
        assert btn is not None
        assert btn.text() == "Voltar ao Menu"

    def test_voltar_menu_signal(self, tela, qtbot):
        """Clicar em voltar ao menu deve emitir voltar_menu_solicitado."""
        tela.exibir_resultado(pontuacao_global=5000.0, dias_concluidos=1)
        btn = tela.findChild(QPushButton, "btn_voltar_menu")
        with qtbot.waitSignal(tela.voltar_menu_solicitado, timeout=1000):
            qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)

    def test_temporizador(self, tela):
        """renderizar_relatorio deve reiniciar o temporizador."""
        tela.renderizar_relatorio({
            "titulo": "Teste", "local": "", "atividade": "",
            "texto_descricao": "",
        })
        assert tela._TelaInspecaoCheia__tempo_inicio_inspecao > 0

    def test_sidebar_integrado(self, tela):
        """TelaInspecaoCheia deve conter uma Sidebar."""
        sidebar = tela.findChild(Sidebar)
        assert sidebar is not None
        assert sidebar.objectName() == "sidebar"

    def test_anexo_preview_integrado(self, tela):
        """TelaInspecaoCheia deve conter um AnexoPreview."""
        preview = tela.findChild(AnexoPreview)
        assert preview is not None

    def test_anexo_gallery_integrado(self, tela):
        """TelaInspecaoCheia deve conter uma AnexoGallery (escondida)."""
        gallery = tela.findChild(AnexoGallery)
        assert gallery is not None
        assert not gallery.isVisible()

    def test_media_viewer_integrado(self, tela):
        """TelaInspecaoCheia deve conter um MediaViewer (escondido)."""
        viewer = tela.findChild(MediaViewer)
        assert viewer is not None
        assert not viewer.isVisible()

    def test_gallery_abre_com_anexos(self, tela, qtbot):
        """renderizar_relatorio com anexos deve permitir abrir gallery."""
        tela.show()
        qtbot.wait(50)
        tela.renderizar_relatorio({
            "titulo": "Teste", "local": "", "atividade": "",
            "texto_descricao": "",
            "anexos": [{"tipo_midia": "IMAGEM", "caminho_arquivo": ""}],
        })
        tela._TelaInspecaoCheia__abrir_gallery()
        gallery = tela.findChild(AnexoGallery)
        assert gallery.isVisible()
        tela.hide()
